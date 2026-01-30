"""Service pour importer les données Open Data d'Infolocale depuis data.gouv.fr."""

import csv
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import httpx
from loguru import logger
from datetime import datetime

from src.config.settings import get_settings
from src.services.storage_service import StorageService

settings = get_settings()


class OpenDataImportService:
    """
    Service pour télécharger et importer les données Open Data Infolocale.

    Source : https://www.data.gouv.fr/fr/datasets/donnees-evenementielles-infolocale/
    Licence : ODbL (Open Database License)
    """

    # URLs des ressources Open Data (à mettre à jour)
    DATASET_PAGE = "https://www.data.gouv.fr/fr/datasets/donnees-evenementielles-infolocale/"

    # URL directe du CSV (à récupérer depuis la page du dataset)
    # Vous devrez mettre à jour cette URL avec l'URL réelle du CSV
    CSV_URL = None  # À définir après inspection du dataset

    def __init__(self):
        """Initialize import service."""
        self.storage_service = StorageService()
        self.client = httpx.Client(timeout=120, follow_redirects=True)

    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Récupérer les informations du dataset depuis l'API data.gouv.fr.

        Returns:
            Dictionary avec les métadonnées du dataset
        """
        api_url = "https://www.data.gouv.fr/api/1/datasets/donnees-evenementielles-infolocale/"

        try:
            logger.info("Fetching dataset info from data.gouv.fr API...")
            response = self.client.get(api_url)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Dataset: {data.get('title')}")
            logger.info(f"Resources available: {len(data.get('resources', []))}")

            return data

        except Exception as e:
            logger.error(f"Error fetching dataset info: {e}")
            return {}

    def find_csv_resource(self, dataset_info: Dict[str, Any]) -> Optional[str]:
        """
        Trouver l'URL de la ressource CSV.

        Args:
            dataset_info: Informations du dataset

        Returns:
            URL du fichier CSV ou None
        """
        resources = dataset_info.get('resources', [])

        # Chercher une ressource CSV
        for resource in resources:
            format_type = resource.get('format', '').lower()
            if format_type in ['csv', 'text/csv']:
                url = resource.get('url')
                logger.info(f"Found CSV resource: {resource.get('title')}")
                logger.info(f"URL: {url}")
                return url

        # Si pas de CSV direct, chercher un lien vers une plateforme open data
        for resource in resources:
            url = resource.get('url', '')
            if 'csv' in url.lower() or 'export' in url.lower():
                logger.info(f"Found potential CSV link: {url}")
                return url

        return None

    def download_csv(self, url: str, output_path: str = "data/opendata_events.csv") -> Optional[str]:
        """
        Télécharger le fichier CSV.

        Args:
            url: URL du fichier CSV
            output_path: Chemin de sauvegarde

        Returns:
            Path to downloaded file or None
        """
        try:
            logger.info(f"Downloading CSV from {url}...")

            # Créer le dossier si nécessaire
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            response = self.client.get(url)
            response.raise_for_status()

            # Sauvegarder
            with open(output_path, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content) / 1024 / 1024  # MB
            logger.info(f"✓ CSV downloaded: {output_path} ({file_size:.2f} MB)")

            return output_path

        except Exception as e:
            logger.error(f"Error downloading CSV: {e}")
            return None

    def _generate_uid(self, row: Dict[str, str]) -> str:
        """
        Générer un UID unique pour un événement.

        Args:
            row: Ligne CSV

        Returns:
            UID unique
        """
        # Utiliser plusieurs champs pour créer un identifiant unique
        unique_string = f"{row.get('titre', '')}_{row.get('commune', '')}_{row.get('date_debut', '')}_{row.get('organisateur', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def parse_csv_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Transformer une ligne CSV en format ScannedEvent.

        Args:
            row: Dictionary représentant une ligne du CSV

        Returns:
            Dictionary compatible avec ScannedEvent
        """
        # Générer UID
        uid = self._generate_uid(row)

        # Parser les coordonnées géographiques
        latitude = None
        longitude = None

        geo_point = row.get('geolocalisation', '') or row.get('geo_point_2d', '')
        if geo_point:
            try:
                parts = geo_point.split(',')
                if len(parts) == 2:
                    latitude = float(parts[0].strip())
                    longitude = float(parts[1].strip())
            except (ValueError, AttributeError):
                pass

        # Parser les tags
        tags = None
        mots_cles = row.get('mots_cles', '') or row.get('tags', '')
        if mots_cles:
            tags = [tag.strip() for tag in mots_cles.split(',') if tag.strip()]

        # Construire l'événement
        event_data = {
            'uid': uid,
            'user_id': settings.DEFAULT_USER_ID,
            'title': row.get('titre', '') or row.get('title', ''),
            'category': row.get('rubrique', None) or row.get('category', None),
            'begin_date': row.get('date_debut', None) or row.get('start_date', None),
            'end_date': row.get('date_fin', None) or row.get('end_date', None),
            'start_time': row.get('horaire_debut', None) or row.get('start_time', None),
            'end_time': row.get('horaire_fin', None) or row.get('end_time', None),
            'description': row.get('description', None),
            'organizer': row.get('organisateur', None) or row.get('organizer', None),
            'pricing': row.get('tarif', None) or row.get('price', None),
            'website': row.get('lien', None) or row.get('url', None) or row.get('website', None),
            'tags': tags,
            'location_name': row.get('lieu', None) or row.get('location', None),
            'address': row.get('adresse', None) or row.get('address', None),
            'zipcode': row.get('code_postal', None) or row.get('zipcode', None),
            'city': row.get('commune', None) or row.get('city', None),
            'state': row.get('departement', None) or row.get('department', None),
            'country': 'France',
            'latitude': latitude,
            'longitude': longitude,
            'image_path': row.get('image', None),
            'raw_json': row,  # Conserver les données brutes
        }

        return event_data

    def import_csv(self, csv_path: str, batch_size: int = 100, max_records: Optional[int] = None) -> int:
        """
        Importer les événements depuis un fichier CSV.

        Args:
            csv_path: Chemin du fichier CSV
            batch_size: Taille des batchs pour l'insertion
            max_records: Nombre maximum d'enregistrements à importer (None = tous)

        Returns:
            Nombre d'événements importés
        """
        logger.info(f"Starting CSV import from {csv_path}...")

        try:
            events_batch = []
            total_imported = 0
            total_processed = 0

            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                # Détecter le délimiteur
                sample = csvfile.read(4096)
                csvfile.seek(0)

                delimiter = ','
                if ';' in sample:
                    delimiter = ';'

                reader = csv.DictReader(csvfile, delimiter=delimiter)

                for row in reader:
                    total_processed += 1

                    # Vérifier max_records
                    if max_records and total_processed > max_records:
                        break

                    try:
                        event_data = self.parse_csv_row(row)
                        events_batch.append(event_data)

                        # Insérer par batch
                        if len(events_batch) >= batch_size:
                            saved = self.storage_service.save_events_batch(events_batch)
                            total_imported += saved
                            logger.info(f"Progress: {total_processed} processed, {total_imported} imported")
                            events_batch = []

                    except Exception as e:
                        logger.error(f"Error parsing row {total_processed}: {e}")
                        continue

                # Insérer le dernier batch
                if events_batch:
                    saved = self.storage_service.save_events_batch(events_batch)
                    total_imported += saved

            logger.info(f"✓ Import completed: {total_imported}/{total_processed} events imported")
            return total_imported

        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            raise

    def download_and_import(self, max_records: Optional[int] = None) -> int:
        """
        Pipeline complet : télécharger et importer les données.

        Args:
            max_records: Nombre maximum d'enregistrements (None = tous)

        Returns:
            Nombre d'événements importés
        """
        logger.info("Starting Open Data import pipeline...")

        # 1. Récupérer les infos du dataset
        dataset_info = self.get_dataset_info()
        if not dataset_info:
            logger.error("Failed to fetch dataset info")
            return 0

        # 2. Trouver l'URL du CSV
        csv_url = self.find_csv_resource(dataset_info)
        if not csv_url:
            logger.error("No CSV resource found")
            logger.info(f"Visit {self.DATASET_PAGE} to find the CSV URL manually")
            return 0

        # 3. Télécharger le CSV
        csv_path = self.download_csv(csv_url)
        if not csv_path:
            logger.error("Failed to download CSV")
            return 0

        # 4. Importer dans la DB
        total_imported = self.import_csv(csv_path, max_records=max_records)

        logger.info(f"✓ Pipeline completed: {total_imported} events imported")
        return total_imported

    def close(self):
        """Close HTTP client."""
        self.client.close()
