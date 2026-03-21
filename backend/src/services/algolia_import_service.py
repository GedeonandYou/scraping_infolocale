"""Service pour importer les événements depuis l'API Algolia d'Infolocale."""

import re
import time
from base64 import b64decode
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

import httpx
from loguru import logger
from playwright.sync_api import sync_playwright

from src.config.settings import get_settings
from src.services.storage_service import StorageService

settings = get_settings()


def _key_valid_until(api_key: str) -> Optional[int]:
    """Extrait le timestamp validUntil d'une Secured API Key Algolia."""
    try:
        decoded = b64decode(api_key + "==").decode("utf-8", errors="ignore")
        m = re.search(r"validUntil=(\d+)", decoded)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def fetch_algolia_key_from_site() -> Optional[str]:
    """
    Charge infolocale.fr avec Playwright headless et intercepte la clé Algolia
    depuis les headers des requêtes réseau (X-Algolia-API-Key).
    """
    captured_key: list = []

    try:
        print("INFO: Chargement de infolocale.fr pour intercepter la clé Algolia...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def on_request(request):
                if "algolia" in request.url:
                    key = request.headers.get("x-algolia-api-key", "")
                    if key and len(key) > 40:
                        captured_key.append(key)

            page.on("request", on_request)
            page.goto("https://www.infolocale.fr", wait_until="networkidle", timeout=30000)
            browser.close()

        if captured_key:
            key = captured_key[0]
            print(f"INFO: Clé Algolia interceptée (validUntil={_key_valid_until(key)})")
            return key

        print("WARNING: Aucune clé Algolia trouvée dans les requêtes interceptées")

    except Exception as e:
        print(f"WARNING: Impossible de récupérer la clé Algolia via Playwright : {e}")

    return None


class AlgoliaImportService:
    """
    Importe massivement les événements depuis l'index Algolia d'Infolocale
    (index memo_events) via l'endpoint /query avec pagination par pages.

    La clé publique (search-only) ne permet pas l'endpoint /browse.
    Algolia limite la pagination à offset < 1000 par défaut ; pour contourner
    cette limite on passe des filtres par département (101 départements FR)
    afin que chaque requête retourne < 1000 résultats.

    La clé est rotative (~30 jours) : la renouveler depuis les DevTools du
    navigateur sur infolocale.fr (onglet Network → requête *.algolia.net →
    header X-Algolia-API-Key).
    """

    QUERY_URL = "https://{app_id}-dsn.algolia.net/1/indexes/{index}/query"
    INFOLOCALE_BASE = "https://www.infolocale.fr"

    # 101 slugs de départements français (métropole + DOM)
    DEPARTEMENTS = [
        "ain", "aisne", "allier", "alpes-de-haute-provence", "hautes-alpes",
        "alpes-maritimes", "ardeche", "ardennes", "ariege", "aube", "aude",
        "aveyron", "bouches-du-rhone", "calvados", "cantal", "charente",
        "charente-maritime", "cher", "correze", "cote-d-or", "cotes-d-armor",
        "creuse", "dordogne", "doubs", "drome", "eure", "eure-et-loir",
        "finistere", "gard", "haute-garonne", "gers", "gironde", "herault",
        "ille-et-vilaine", "indre", "indre-et-loire", "isere", "jura",
        "landes", "loir-et-cher", "loire", "haute-loire", "loire-atlantique",
        "loiret", "lot", "lot-et-garonne", "lozere", "maine-et-loire",
        "manche", "marne", "haute-marne", "mayenne", "meurthe-et-moselle",
        "meuse", "morbihan", "moselle", "nievre", "nord", "oise", "orne",
        "pas-de-calais", "puy-de-dome", "pyrenees-atlantiques",
        "hautes-pyrenees", "pyrenees-orientales", "bas-rhin", "haut-rhin",
        "rhone", "haute-saone", "saone-et-loire", "sarthe", "savoie",
        "haute-savoie", "paris", "seine-maritime", "seine-et-marne",
        "yvelines", "deux-sevres", "somme", "tarn", "tarn-et-garonne", "var",
        "vaucluse", "vendee", "vienne", "haute-vienne", "vosges", "yonne",
        "territoire-de-belfort", "essonne", "hauts-de-seine",
        "seine-saint-denis", "val-de-marne", "val-d-oise",
        "guadeloupe", "martinique", "guyane", "la-reunion", "mayotte",
        "corse-du-sud", "haute-corse",
    ]

    def __init__(self):
        self.storage_service = StorageService()
        self.client = httpx.Client(timeout=30, follow_redirects=True)

        api_key = self._resolve_api_key()

        self._headers = {
            "X-Algolia-Application-Id": settings.ALGOLIA_APP_ID,
            "X-Algolia-API-Key": api_key,
            "Content-Type": "application/json",
        }
        self._query_url = self.QUERY_URL.format(
            app_id=settings.ALGOLIA_APP_ID,
            index=settings.ALGOLIA_INDEX_NAME,
        )

    @staticmethod
    def _resolve_api_key() -> str:
        """
        Retourne la clé Algolia à utiliser :
        1. Clé du .env si encore valide (validUntil > maintenant + 5 min)
        2. Sinon, tente de l'extraire automatiquement depuis infolocale.fr
        3. Sinon, utilise quand même la clé du .env (l'erreur sera explicite)
        """
        env_key = settings.ALGOLIA_API_KEY
        valid_until = _key_valid_until(env_key) if env_key else None
        now = int(time.time())

        if env_key and valid_until and valid_until > now + 300:
            remaining = (valid_until - now) // 3600
            logger.info(f"Clé Algolia (.env) valide encore ~{remaining}h")
            return env_key

        if env_key and valid_until and valid_until <= now:
            logger.warning("Clé Algolia (.env) expirée — tentative d'extraction automatique...")
        elif not env_key:
            logger.info("ALGOLIA_API_KEY non définie — tentative d'extraction automatique...")

        auto_key = fetch_algolia_key_from_site()
        if auto_key:
            return auto_key

        logger.warning("Extraction automatique échouée — utilisation de la clé .env")
        return env_key or ""

    # ------------------------------------------------------------------
    # Search avec pagination par pages
    # ------------------------------------------------------------------

    def _search_page(self, page: int, dept_slug: str = "") -> Dict[str, Any]:
        """Appelle l'endpoint /query pour une page donnée."""
        body: Dict[str, Any] = {
            "hitsPerPage": settings.ALGOLIA_HITS_PER_PAGE,
            "page": page,
        }
        if dept_slug:
            body["facetFilters"] = [[f"lieu.departement.slug:{dept_slug}"]]

        response = self.client.post(self._query_url, json=body, headers=self._headers)
        if not response.is_success:
            logger.error(f"Algolia {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()

    def search_all(self, dept_slug: str = "") -> Iterator[Dict[str, Any]]:
        """Itère sur toutes les pages pour un département donné."""
        page = 0
        total_fetched = 0

        while True:
            data = self._search_page(page=page, dept_slug=dept_slug)
            hits: List[Dict[str, Any]] = data.get("hits", [])
            nb_pages: int = data.get("nbPages", 1)

            if not hits:
                break

            total_fetched += len(hits)
            logger.info(
                f"Algolia [{dept_slug or 'global'}]: "
                f"page {page + 1}/{nb_pages} ({total_fetched} hits)"
            )

            yield from hits

            page += 1
            if page >= nb_pages:
                break

    def browse_all(self, dept_slug: str = "") -> Iterator[Dict[str, Any]]:
        """
        Récupère les événements en itérant par département.
        - Si dept_slug est fourni : un seul département.
        - Sinon : tous les 101 départements (contourne la limite de 1000 résultats).
        """
        seen_ids: set = set()
        total = 0

        depts = [dept_slug] if dept_slug else self.DEPARTEMENTS

        for slug in depts:
            for hit in self.search_all(dept_slug=slug):
                oid = hit.get("objectID")
                if oid in seen_ids:
                    continue
                seen_ids.add(oid)
                total += 1
                yield hit

        logger.info(f"Browse total : {total} hits uniques récupérés")

    # ------------------------------------------------------------------
    # Mapping hit → ScannedEvent
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_literal_date(literal: Optional[str]) -> tuple[Optional[datetime.date], Optional[str]]:
        """Parse '20/03/2026 09:00:00' → (date, 'HH:MM')."""
        if not literal:
            return None, None
        try:
            dt = datetime.strptime(literal, "%d/%m/%Y %H:%M:%S")
            time_str = dt.strftime("%H:%M") if (dt.hour or dt.minute) else None
            return dt.date(), time_str
        except ValueError:
            return None, None

    def map_hit(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        """Mappe un hit Algolia vers un dictionnaire compatible ScannedEvent."""
        lieu: Dict[str, Any] = hit.get("lieu") or {}
        commune: Dict[str, Any] = lieu.get("commune") or {}
        departement: Dict[str, Any] = lieu.get("departement") or {}
        photo: Dict[str, Any] = hit.get("photo") or {}

        begin_date, start_time = self._parse_literal_date(hit.get("_date-first-literal"))
        end_date, end_time = self._parse_literal_date(hit.get("_date-last-literal"))

        # Coordonnées GPS : lieu est plus précis que _geoloc
        geoloc: Dict[str, Any] = hit.get("_geoloc") or {}
        latitude: Optional[float] = lieu.get("latitude") or geoloc.get("lat")
        longitude: Optional[float] = lieu.get("longitude") or geoloc.get("lng")

        # Tarifs
        tarifs = hit.get("tarifs") or []
        pricing: Optional[str] = ", ".join(str(t) for t in tarifs) if tarifs else None

        # URL de la page événement
        chemin = hit.get("chemin")
        website = f"{self.INFOLOCALE_BASE}{chemin}" if chemin else None

        # Accessibilités et âges (tableaux Algolia, peuvent être vides)
        accessibilites: Optional[list] = hit.get("accessibilites") or None
        ages: Optional[list] = hit.get("ages") or None

        # Organisateur : Algolia renvoie un dict {"id": ..., "nom": ..., ...}
        organisme = hit.get("organisme")
        organizer: Optional[str] = (
            organisme.get("nom") if isinstance(organisme, dict) else organisme
        )

        return {
            "uid": f"algolia_{hit['objectID']}",
            "user_id": settings.DEFAULT_USER_ID,
            "title": hit.get("titre") or "Sans titre",
            "description": hit.get("texte"),
            "category": hit.get("categorie"),
            "genre": hit.get("genre"),
            "begin_date": begin_date,
            "end_date": end_date,
            "start_time": start_time,
            "end_time": end_time,
            "organizer": organizer,
            "pricing": pricing,
            "website": website,
            "location_name": lieu.get("nom"),
            "address": lieu.get("adresse"),
            "zipcode": commune.get("codePostal"),
            "city": commune.get("libelle"),
            "state": departement.get("libelle"),
            "country": "France",
            "latitude": latitude,
            "longitude": longitude,
            "image_path": photo.get("url"),
            "annule": bool(hit.get("annule", False)),
            "complet": bool(hit.get("complet", False)),
            "permanent": bool(hit.get("permanent", False)),
            "accessibilites": accessibilites,
            "ages": ages,
            "raw_json": hit,
        }

    # ------------------------------------------------------------------
    # Import pipeline
    # ------------------------------------------------------------------

    def import_all(
        self,
        dept_slug: str = "",
        limit: int = 0,
        batch_size: int = 500,
    ) -> int:
        """
        Récupère tous les événements Algolia et les stocke en base.

        Args:
            dept_slug: Slug de département à filtrer (ex: "vaucluse"), vide = tous
            limit: Nombre max d'événements à importer (0 = illimité)
            batch_size: Taille des batches pour l'insertion en base

        Returns:
            Nombre d'événements sauvegardés
        """
        logger.info(
            f"Démarrage import Algolia (index={settings.ALGOLIA_INDEX_NAME}"
            + (f", dept={dept_slug!r}" if dept_slug else "")
            + (f", limit={limit}" if limit else "")
            + ")"
        )

        batch: List[Dict[str, Any]] = []
        total_saved = 0
        total_processed = 0

        for hit in self.browse_all(dept_slug=dept_slug):
            total_processed += 1

            try:
                event = self.map_hit(hit)
                batch.append(event)
            except Exception as e:
                logger.warning(f"Erreur mapping hit {hit.get('objectID')}: {e}")
                continue

            if len(batch) >= batch_size:
                saved = self.storage_service.save_events_batch(batch)
                total_saved += saved
                logger.info(f"Batch sauvegardé : {saved}/{len(batch)} | total={total_saved}")
                batch = []

            if limit and total_processed >= limit:
                logger.info(f"Limite atteinte ({limit} événements)")
                break

        # Dernier batch
        if batch:
            saved = self.storage_service.save_events_batch(batch)
            total_saved += saved

        logger.info(
            f"Import Algolia terminé : {total_saved} événements sauvegardés "
            f"(sur {total_processed} traités)"
        )
        return total_saved

    def close(self):
        """Ferme le client HTTP."""
        self.client.close()
