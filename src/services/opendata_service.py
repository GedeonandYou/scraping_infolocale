"""Service pour récupérer les données depuis l'API OpenDataSoft d'Infolocale."""

import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

from src.config.settings import get_settings

settings = get_settings()


class OpenDataService:
    """
    Service pour accéder aux données ouvertes Infolocale via OpenDataSoft API.

    Plus fiable et légal que le scraping HTML !
    Documentation: https://data.opendatasoft.com/api/explore/v2.1
    """

    BASE_URL = "https://datainfolocale.opendatasoft.com/api/explore/v2.1"
    DATASET_ID = "agenda_culturel"

    def __init__(self):
        """Initialize OpenData service."""
        self.client = httpx.Client(timeout=30)

    def get_events(
        self,
        limit: int = 100,
        offset: int = 0,
        where: Optional[str] = None,
        refine: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Récupérer les événements depuis l'API OpenDataSoft.

        Args:
            limit: Nombre d'événements à récupérer (max 100 par requête)
            offset: Offset pour la pagination
            where: Clause WHERE pour filtrer (ex: "departement='35'")
            refine: Filtres par facette (ex: {"departement": "35"})

        Returns:
            Dictionary avec 'total_count' et 'results'
        """
        url = f"{self.BASE_URL}/catalog/datasets/{self.DATASET_ID}/records"

        params = {
            "limit": min(limit, 100),  # Max 100 par requête
            "offset": offset,
        }

        if where:
            params["where"] = where

        if refine:
            for key, value in refine.items():
                params[f"refine.{key}"] = value

        try:
            logger.info(f"Fetching events from OpenDataSoft API (limit={limit}, offset={offset})")
            response = self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            logger.info(f"Successfully fetched {len(data.get('results', []))} events")

            return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching events: {e}")
            return {"total_count": 0, "results": []}
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return {"total_count": 0, "results": []}

    def get_all_events(
        self,
        max_records: int = 1000,
        where: Optional[str] = None,
        refine: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupérer tous les événements avec pagination automatique.

        Args:
            max_records: Nombre maximum d'enregistrements à récupérer
            where: Clause WHERE pour filtrer
            refine: Filtres par facette

        Returns:
            Liste de tous les événements
        """
        all_events = []
        offset = 0
        limit = 100

        while len(all_events) < max_records:
            data = self.get_events(
                limit=limit,
                offset=offset,
                where=where,
                refine=refine
            )

            results = data.get("results", [])
            if not results:
                break

            all_events.extend(results)
            offset += limit

            # Vérifier si on a tout récupéré
            total_count = data.get("total_count", 0)
            if offset >= total_count:
                break

        logger.info(f"Retrieved total of {len(all_events)} events")
        return all_events[:max_records]

    def transform_to_event_data(self, opendata_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transformer un enregistrement OpenDataSoft en format ScannedEvent.

        Args:
            opendata_record: Enregistrement depuis l'API

        Returns:
            Dictionary compatible avec ScannedEvent
        """
        fields = opendata_record.get("record", {}).get("fields", {})
        record_id = opendata_record.get("record", {}).get("id", "")

        # Générer un UID unique
        uid = f"opendata_{record_id}"

        # Extraire les coordonnées géographiques
        geo = fields.get("geolocalisation", {})
        latitude = None
        longitude = None

        if geo and isinstance(geo, dict):
            latitude = geo.get("lat")
            longitude = geo.get("lon")

        event_data = {
            "uid": uid,
            "user_id": settings.DEFAULT_USER_ID,
            "title": fields.get("titre", ""),
            "category": fields.get("rubrique", None),
            "begin_date": fields.get("date_debut"),
            "end_date": fields.get("date_fin"),
            "start_time": fields.get("horaire_debut"),
            "end_time": fields.get("horaire_fin"),
            "description": fields.get("description", None),
            "organizer": fields.get("organisateur", None),
            "pricing": fields.get("tarif", None),
            "website": fields.get("lien", None),
            "tags": fields.get("mots_cles", "").split(",") if fields.get("mots_cles") else None,
            "location_name": fields.get("lieu", None),
            "address": fields.get("adresse", None),
            "zipcode": fields.get("code_postal", None),
            "city": fields.get("commune", None),
            "state": fields.get("departement", None),
            "country": "France",
            "latitude": latitude,
            "longitude": longitude,
            "image_path": fields.get("image", None),
            "raw_json": fields,  # Stocker les données brutes
        }

        return event_data

    def close(self):
        """Close HTTP client."""
        self.client.close()


# Exemple d'utilisation
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    service = OpenDataService()

    console.print("[bold blue]Test OpenDataService[/bold blue]\n")

    # Récupérer quelques événements
    events = service.get_all_events(max_records=10)

    console.print(f"[green]✓ {len(events)} événements récupérés[/green]\n")

    # Afficher dans un tableau
    table = Table(title="Événements Infolocale")
    table.add_column("Titre", style="cyan", no_wrap=False)
    table.add_column("Ville", style="green")
    table.add_column("Date", style="yellow")

    for event in events[:5]:
        fields = event.get("record", {}).get("fields", {})
        table.add_row(
            fields.get("titre", "")[:50],
            fields.get("commune", ""),
            fields.get("date_debut", "")
        )

    console.print(table)

    # Transformer un événement
    if events:
        console.print("\n[bold blue]Transformation en format ScannedEvent:[/bold blue]")
        transformed = service.transform_to_event_data(events[0])
        console.print(transformed)

    service.close()
