"""Service for geocoding addresses using Google Places API."""

from typing import Optional, Dict, Any
import googlemaps
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings

settings = get_settings()


class GeocodingService:
    """Service to geocode addresses and enrich location data with Google Places API."""

    def __init__(self):
        """Initialize Google Maps client."""
        self.client = None
        if settings.GOOGLE_PLACES_API_KEY:
            try:
                self.client = googlemaps.Client(key=settings.GOOGLE_PLACES_API_KEY)
                logger.info("Google Maps client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def geocode_address(
        self,
        address: Optional[str] = None,
        city: Optional[str] = None,
        zipcode: Optional[str] = None,
        country: str = "France"
    ) -> Optional[Dict[str, Any]]:
        """
        Geocode an address and return enriched location data.

        Args:
            address: Street address
            city: City name
            zipcode: Postal code
            country: Country name (default: France)

        Returns:
            Dictionary with geocoding results or None if geocoding fails
            {
                'latitude': float,
                'longitude': float,
                'display_name': str,
                'place_id': str,
                'place_name': str,
                'place_types': list[str],
                'rating': float
            }
        """
        if not self.client:
            logger.warning("Google Maps client not initialized (missing API key)")
            return None

        # Construct full address
        address_parts = [p for p in [address, zipcode, city, country] if p]
        if not address_parts:
            logger.warning("No address components provided for geocoding")
            return None

        full_address = ", ".join(address_parts)

        try:
            # Geocode the address
            geocode_result = self.client.geocode(full_address)

            if not geocode_result:
                logger.warning(f"No geocoding results for address: {full_address}")
                return None

            result = geocode_result[0]
            location = result['geometry']['location']

            geocoded_data = {
                'latitude': location['lat'],
                'longitude': location['lng'],
                'display_name': result['formatted_address'],
                'place_id': result.get('place_id'),
            }

            # Try to get place details if we have a place_id
            if geocoded_data['place_id']:
                try:
                    place_details = self.client.place(
                        place_id=geocoded_data['place_id'],
                        fields=['name', 'types', 'rating']
                    )

                    if place_details and 'result' in place_details:
                        details = place_details['result']
                        geocoded_data.update({
                            'place_name': details.get('name'),
                            'place_types': details.get('types', []),
                            'rating': details.get('rating'),
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch place details: {e}")

            logger.info(f"Successfully geocoded: {full_address}")
            return geocoded_data

        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Maps API error for '{full_address}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during geocoding '{full_address}': {e}")
            return None

    def geocode_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Geocode an event's location and enrich the event data.

        Args:
            event_data: Event dictionary with location fields

        Returns:
            Updated event_data with geocoding results
        """
        geocoded = self.geocode_address(
            address=event_data.get('address'),
            city=event_data.get('city'),
            zipcode=event_data.get('zipcode'),
            country=event_data.get('country', 'France')
        )

        if geocoded:
            event_data.update({
                'latitude': geocoded.get('latitude'),
                'longitude': geocoded.get('longitude'),
                'display_name': geocoded.get('display_name'),
                'place_id': geocoded.get('place_id'),
                'place_name': geocoded.get('place_name'),
                'place_types': geocoded.get('place_types'),
                'rating': geocoded.get('rating'),
            })

        return event_data
