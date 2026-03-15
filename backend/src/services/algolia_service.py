"""Service pour scraper les evenements Infolocale via l'API Algolia."""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import httpx
from loguru import logger

from src.config.settings import get_settings
from src.services.algolia_key_service import AlgoliaKeyService

settings = get_settings()


class AlgoliaService:
    """
    Scrape les evenements Infolocale via l'API Algolia (index memo_events).

    L'API key est une secured key base64 recuperee depuis le frontend infolocale.fr.
    Elle doit etre envoyee RAW (PAS decodee) dans le header X-Algolia-API-Key.
    Si la cle est absente ou expiree, elle est recuperee automatiquement.
    """

    def __init__(self):
        self.app_id = settings.ALGOLIA_APP_ID
        self.api_key = settings.ALGOLIA_API_KEY
        self.index = settings.ALGOLIA_INDEX
        self.search_url = f"https://{self.app_id}-dsn.algolia.net/1/indexes/{self.index}/query"
        self.browse_url = f"https://{self.app_id}-dsn.algolia.net/1/indexes/{self.index}/browse"
        self.client = httpx.Client(timeout=30)
        self._key_refreshed = False

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-Algolia-Application-Id": self.app_id,
            "X-Algolia-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _refresh_key(self) -> bool:
        """
        Recupere une nouvelle cle API Algolia via Selenium CDP.

        Returns:
            True si la cle a ete renouvelee, False sinon.
        """
        logger.info("Tentative de recuperation automatique de la cle Algolia...")
        new_key = AlgoliaKeyService.fetch_key()
        if new_key:
            self.api_key = new_key
            self._key_refreshed = True
            logger.info("Cle Algolia renouvelee avec succes")
            return True
        logger.error("Impossible de recuperer une nouvelle cle Algolia")
        return False

    def _is_expired_key_error(self, response: httpx.Response) -> bool:
        """Detecte si l'erreur HTTP est due a une cle expiree."""
        if response.status_code not in (400, 403):
            return False
        try:
            body = response.json()
            message = body.get("message", "")
            return "validUntil" in message or "expired" in message.lower()
        except Exception:
            return False

    def _search(self, params: str) -> Dict[str, Any]:
        """
        Effectue une requete de recherche Algolia (endpoint query).
        Auto-refresh la cle si elle est expiree.

        Args:
            params: Parametres de recherche URL-encoded

        Returns:
            Reponse JSON Algolia
        """
        body = {"params": params}
        response = self.client.post(self.search_url, json=body, headers=self._get_headers())

        if self._is_expired_key_error(response) and not self._key_refreshed:
            if self._refresh_key():
                response = self.client.post(self.search_url, json=body, headers=self._get_headers())

        response.raise_for_status()
        return response.json()

    def _browse(self, params: Optional[str] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Effectue une requete browse Algolia (sans limite de 1000 hits).
        Auto-refresh la cle si elle est expiree.

        Args:
            params: Parametres de recherche URL-encoded (premiere requete)
            cursor: Cursor de pagination (requetes suivantes)

        Returns:
            Reponse JSON Algolia avec cursor pour la page suivante
        """
        body: Dict[str, Any] = {}
        if cursor:
            body["cursor"] = cursor
        elif params:
            body["params"] = params

        response = self.client.post(self.browse_url, json=body, headers=self._get_headers())

        if self._is_expired_key_error(response) and not self._key_refreshed:
            if self._refresh_key():
                response = self.client.post(self.browse_url, json=body, headers=self._get_headers())

        response.raise_for_status()
        return response.json()

    def fetch_events(
        self,
        limit: Optional[int] = None,
        date_from: Optional[int] = None,
        date_to: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Recupere les evenements depuis Algolia via l'endpoint browse (sans limite de 1000).

        Utilise le cursor Algolia pour paginer au-dela de 1000 resultats.

        Args:
            limit: Nombre max d'evenements a recuperer (None = tous)
            date_from: Timestamp unix minimum (filtre sur date-first)
            date_to: Timestamp unix maximum (filtre sur date-first)

        Returns:
            Liste de tous les hits (evenements)
        """
        if not self.api_key:
            logger.warning("ALGOLIA_API_KEY non configuree, recuperation automatique...")
            if not self._refresh_key():
                logger.error("Impossible de recuperer la cle Algolia")
                return []

        # Construire les parametres initiaux
        params_parts = ["hitsPerPage=1000"]
        numeric_filters = []
        if date_from is not None:
            numeric_filters.append(f"date-first>={date_from}")
        if date_to is not None:
            numeric_filters.append(f"date-first<={date_to}")
        if numeric_filters:
            params_parts.append(f"numericFilters={','.join(numeric_filters)}")

        params = "&".join(params_parts)

        all_hits = []
        cursor = None
        page = 0

        while True:
            logger.info(f"Algolia browse page={page} ...")
            try:
                if page == 0:
                    data = self._browse(params=params)
                else:
                    data = self._browse(cursor=cursor)
            except httpx.HTTPStatusError as e:
                logger.error(f"Algolia HTTP error: {e.response.status_code} - {e.response.text[:200]}")
                break
            except Exception as e:
                logger.error(f"Algolia request error: {e}")
                break

            hits = data.get("hits", [])
            cursor = data.get("cursor")

            all_hits.extend(hits)
            logger.info(f"Page {page}: {len(hits)} hits (total: {len(all_hits)})")

            page += 1

            # Arreter si on a atteint la limite demandee
            if limit and len(all_hits) >= limit:
                all_hits = all_hits[:limit]
                break

            # Arreter si plus de cursor (fin des resultats)
            if not cursor:
                break

            time.sleep(0.3)

        logger.info(f"Total recupere: {len(all_hits)} evenements")
        return all_hits

    def _flatten_hit(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplatit un hit Algolia en colonnes CSV lisibles.

        Extrait les champs imbriques : _geoloc, lieu, rubrique, photo.
        """
        lieu = hit.get("lieu") or {}
        rubrique = hit.get("rubrique") or {}
        photo = hit.get("photo") or {}
        geoloc = hit.get("_geoloc") or {}

        return {
            "objectID": hit.get("objectID"),
            "titre": hit.get("titre"),
            "texte": hit.get("texte"),
            "categorie": hit.get("categorie"),
            "genre": hit.get("genre"),
            "rubrique_lvl0": rubrique.get("lvl0"),
            "rubrique_lvl1": rubrique.get("lvl1"),
            "date_debut": hit.get("_date-first-literal"),
            "date_fin": hit.get("_date-last-literal"),
            "lieu_nom": lieu.get("nom"),
            "lieu_adresse": lieu.get("adresse"),
            "latitude": geoloc.get("lat") or lieu.get("latitude"),
            "longitude": geoloc.get("lng") or lieu.get("longitude"),
            "photo_url": photo.get("url"),
            "url": f"https://www.infolocale.fr{hit.get('chemin', '')}",
            "annule": hit.get("annule"),
            "complet": hit.get("complet"),
            "permanent": hit.get("permanent"),
            "source": hit.get("source"),
            "provider": hit.get("provider"),
            "tarifs": "|".join(str(t) for t in hit.get("tarifs", [])) if hit.get("tarifs") else "",
            "ages": "|".join(str(a) for a in hit.get("ages", [])) if hit.get("ages") else "",
            "accessibilites": "|".join(str(a) for a in hit.get("accessibilites", [])) if hit.get("accessibilites") else "",
        }

    def export_to_json(
        self,
        hits: List[Dict[str, Any]],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Exporte les hits Algolia en fichier JSON.

        Args:
            hits: Liste des evenements Algolia
            output_path: Chemin du fichier JSON (defaut: settings.EXPORT_JSON_PATH)

        Returns:
            Chemin du fichier JSON cree
        """
        if not hits:
            logger.warning("Aucun evenement a exporter")
            return ""

        output_path = output_path or settings.EXPORT_JSON_PATH
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        rows = [self._flatten_hit(hit) for hit in hits]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON exporte: {output_path} ({len(rows)} evenements)")
        return output_path

    def export_to_csv(
        self,
        hits: List[Dict[str, Any]],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Exporte les hits Algolia en fichier CSV.

        Les champs imbriques (lieu, rubrique, photo, _geoloc) sont aplatis
        en colonnes lisibles.

        Args:
            hits: Liste des evenements Algolia
            output_path: Chemin du fichier CSV (defaut: settings.EXPORT_CSV_PATH)

        Returns:
            Chemin du fichier CSV cree
        """
        if not hits:
            logger.warning("Aucun evenement a exporter")
            return ""

        output_path = output_path or settings.EXPORT_CSV_PATH
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        rows = [self._flatten_hit(hit) for hit in hits]
        fieldnames = list(rows[0].keys())

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"CSV exporte: {output_path} ({len(rows)} evenements)")
        return output_path

    def scrape_and_export(
        self,
        output_path: Optional[str] = None,
        limit: Optional[int] = None,
        date_from: Optional[int] = None,
        date_to: Optional[int] = None,
    ) -> str:
        """
        Pipeline complet : fetch Algolia + export CSV.

        Args:
            output_path: Chemin du fichier CSV
            limit: Nombre max d'evenements
            date_from: Timestamp unix minimum
            date_to: Timestamp unix maximum

        Returns:
            Chemin du fichier CSV cree
        """
        logger.info("Demarrage du scraping Algolia Infolocale...")

        hits = self.fetch_events(
            limit=limit,
            date_from=date_from,
            date_to=date_to,
        )

        if not hits:
            logger.warning("Aucun evenement recupere")
            return ""

        csv_path = self.export_to_csv(hits, output_path=output_path)

        logger.info(f"Scraping termine: {len(hits)} evenements -> {csv_path}")
        return csv_path

    def close(self):
        """Ferme le client HTTP."""
        self.client.close()


if __name__ == "__main__":
    service = AlgoliaService()

    try:
        # Scraper et exporter (1000 events pour test)
        csv_path = service.scrape_and_export(limit=1000)
        if csv_path:
            print(f"Export CSV: {csv_path}")
    finally:
        service.close()
