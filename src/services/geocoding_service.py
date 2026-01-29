"""Service for geocoding addresses using OpenRouteService API."""

from typing import Optional, Dict, Any
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings

settings = get_settings()


class GeocodingService:
    """Service to geocode addresses and enrich location data with OpenRouteService API."""

    def __init__(self):
        """Initialize OpenRouteService client."""
        self.api_key = settings.OPENROUTESERVICE_API_KEY
        self.base_url = "https://api.openrouteservice.org/geocode"
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({
                'Authorization': self.api_key,
                'Content-Type': 'application/json'
            })
            logger.info("OpenRouteService client initialized successfully")
        else:
            logger.warning("OpenRouteService API key not configured")

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
                'confidence': float,
                'locality': str,
                'region': str
            }
        """
        if not self.api_key:
            logger.warning("OpenRouteService API key not configured")
            return None

        # Construct full address
        address_parts = [p for p in [address, zipcode, city, country] if p]
        if not address_parts:
            logger.warning("No address components provided for geocoding")
            return None

        full_address = ", ".join(address_parts)

        try:
            # Call OpenRouteService Geocoding API
            url = f"{self.base_url}/search"
            params = {
                'text': full_address,
                'boundary.country': 'FR',  # Limit to France
                'size': 1  # Get only the best result
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data.get('features'):
                logger.warning(f"No geocoding results for address: {full_address}")
                return None

            feature = data['features'][0]
            geometry = feature['geometry']
            properties = feature['properties']

            geocoded_data = {
                'latitude': geometry['coordinates'][1],  # ORS returns [lon, lat]
                'longitude': geometry['coordinates'][0],
                'display_name': properties.get('label'),
                'place_id': properties.get('id'),
                'confidence': properties.get('confidence'),
                'locality': properties.get('locality'),
                'region': properties.get('region'),
                'country': properties.get('country'),
            }

            logger.info(f"Successfully geocoded: {full_address}")
            return geocoded_data

        except requests.exceptions.HTTPError as e:
            logger.error(f"OpenRouteService HTTP error for '{full_address}': {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during geocoding '{full_address}': {e}")
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
            })

        return event_data

    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()
