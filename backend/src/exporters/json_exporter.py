"""JSON Exporter for events data."""

import json
from typing import List
from pathlib import Path
from datetime import date, datetime
from loguru import logger

from src.models.scanned_event import ScannedEvent
from src.config.settings import get_settings

settings = get_settings()


class JSONExporter:
    """Export events to JSON format."""

    def __init__(self, output_path: str = None):
        """
        Initialize JSON exporter.

        Args:
            output_path: Path to output JSON file
        """
        self.output_path = output_path or settings.EXPORT_JSON_PATH
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)

    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def export(self, events: List[ScannedEvent], pretty: bool = True) -> str:
        """
        Export events to JSON file.

        Args:
            events: List of ScannedEvent objects
            pretty: Whether to format JSON with indentation

        Returns:
            Path to exported file
        """
        if not events:
            logger.warning("No events to export")
            return None

        try:
            events_data = []

            for event in events:
                event_dict = {
                    'id': event.id,
                    'uid': event.uid,
                    'user_id': event.user_id,
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
                    'tags': event.tags,
                    'artists': event.artists,
                    'sponsors': event.sponsors,
                    'location': {
                        'name': event.location_name,
                        'address': event.address,
                        'zipcode': event.zipcode,
                        'city': event.city,
                        'state': event.state,
                        'country': event.country,
                        'coordinates': {
                            'latitude': event.latitude,
                            'longitude': event.longitude,
                        } if event.latitude and event.longitude else None,
                        'display_name': event.display_name,
                    },
                    'google_places': {
                        'place_id': event.place_id,
                        'place_name': event.place_name,
                        'place_types': event.place_types,
                        'rating': event.rating,
                    } if event.place_id else None,
                    'technical': {
                        'image_path': event.image_path,
                        'qr_code': event.qr_code,
                        'schema_org_types': event.schema_org_types,
                        'raw_json': event.raw_json,
                    },
                    'is_private': event.is_private,
                    'created_at': event.created_at,
                }

                events_data.append(event_dict)

            # Export to JSON
            with open(self.output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(
                    {
                        'total_events': len(events_data),
                        'exported_at': datetime.utcnow(),
                        'events': events_data
                    },
                    jsonfile,
                    indent=2 if pretty else None,
                    ensure_ascii=False,
                    default=self._json_serializer
                )

            logger.info(f"Successfully exported {len(events)} events to {self.output_path}")
            return self.output_path

        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
