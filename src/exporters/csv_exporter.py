"""CSV Exporter for events data."""

import csv
from typing import List
from pathlib import Path
from loguru import logger

from src.models.scanned_event import ScannedEvent
from src.config.settings import get_settings

settings = get_settings()


class CSVExporter:
    """Export events to CSV format."""

    def __init__(self, output_path: str = None):
        """
        Initialize CSV exporter.

        Args:
            output_path: Path to output CSV file
        """
        self.output_path = output_path or settings.EXPORT_CSV_PATH
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)

    def export(self, events: List[ScannedEvent]) -> str:
        """
        Export events to CSV file.

        Args:
            events: List of ScannedEvent objects

        Returns:
            Path to exported file
        """
        if not events:
            logger.warning("No events to export")
            return None

        try:
            with open(self.output_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV columns
                fieldnames = [
                    'id', 'uid', 'title', 'category',
                    'begin_date', 'end_date', 'start_time', 'end_time',
                    'description', 'organizer', 'pricing', 'website',
                    'location_name', 'address', 'zipcode', 'city', 'state', 'country',
                    'latitude', 'longitude', 'display_name',
                    'place_id', 'place_name', 'rating',
                    'tags', 'artists', 'sponsors',
                    'is_private', 'created_at'
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for event in events:
                    # Convert event to dict
                    event_dict = {
                        'id': event.id,
                        'uid': event.uid,
                        'title': event.title,
                        'category': event.category,
                        'begin_date': event.begin_date,
                        'end_date': event.end_date,
                        'start_time': event.start_time,
                        'end_time': event.end_time,
                        'description': event.description,
                        'organizer': event.organizer,
                        'pricing': event.pricing,
                        'website': event.website,
                        'location_name': event.location_name,
                        'address': event.address,
                        'zipcode': event.zipcode,
                        'city': event.city,
                        'state': event.state,
                        'country': event.country,
                        'latitude': event.latitude,
                        'longitude': event.longitude,
                        'display_name': event.display_name,
                        'place_id': event.place_id,
                        'place_name': event.place_name,
                        'rating': event.rating,
                        'tags': '|'.join(event.tags) if event.tags else '',
                        'artists': '|'.join(event.artists) if event.artists else '',
                        'sponsors': '|'.join(event.sponsors) if event.sponsors else '',
                        'is_private': event.is_private,
                        'created_at': event.created_at,
                    }

                    writer.writerow(event_dict)

            logger.info(f"Successfully exported {len(events)} events to {self.output_path}")
            return self.output_path

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
