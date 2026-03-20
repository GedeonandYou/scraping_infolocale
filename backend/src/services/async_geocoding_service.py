"""Asynchronous geocoding service using httpx for better performance."""

import asyncio
from typing import Optional, Dict, Any, List
import httpx
from loguru import logger

from src.config.settings import get_settings
from src.services.geocoding_cache import GeocodingCache

settings = get_settings()


class AsyncGeocodingService:
    """Async service to geocode addresses in batches with OpenRouteService API."""

    def __init__(self):
        """Initialize async OpenRouteService client."""
        self.api_key = settings.OPENROUTESERVICE_API_KEY
        self.base_url = "https://api.openrouteservice.org/geocode"
        self.rate_limit_delay = 1.5  # 40 req/min = 1.5 sec between requests
        self.cache = GeocodingCache()

        if not self.api_key:
            logger.warning("OpenRouteService API key not configured")

    async def geocode_address(
        self,
        client: httpx.AsyncClient,
        address: Optional[str] = None,
        city: Optional[str] = None,
        zipcode: Optional[str] = None,
        country: str = "France"
    ) -> Optional[Dict[str, Any]]:
        """
        Geocode an address asynchronously.

        Args:
            client: httpx AsyncClient
            address: Street address
            city: City name
            zipcode: Postal code
            country: Country name (default: France)

        Returns:
            Dictionary with geocoding results or None
        """
        if not self.api_key:
            return None

        # Construct full address
        address_parts = [p for p in [address, zipcode, city, country] if p]
        if not address_parts:
            logger.warning("No address components provided for geocoding")
            return None

        full_address = ", ".join(address_parts)

        # Check cache first
        cached = await self.cache.get(address, city, zipcode, country)
        if cached:
            logger.debug(f"Cache hit for: {city or full_address}")
            return cached

        try:
            url = f"{self.base_url}/search"
            params = {
                'text': full_address,
                'boundary.country': 'FR',
                'size': 1
            }

            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()

            data = response.json()

            if not data.get('features'):
                logger.warning(f"No geocoding results for: {full_address}")
                await self.cache.set_not_found(address, city, zipcode, country)
                return None

            feature = data['features'][0]
            geometry = feature['geometry']
            properties = feature['properties']

            geocoded_data = {
                'latitude': geometry['coordinates'][1],
                'longitude': geometry['coordinates'][0],
                'display_name': properties.get('label'),
                'place_id': properties.get('id'),
                'confidence': properties.get('confidence'),
                'locality': properties.get('locality'),
                'region': properties.get('region'),
                'country': properties.get('country'),
            }

            await self.cache.set(address, city, zipcode, country, geocoded_data)
            logger.debug(f"✓ Geocoded: {city or full_address}")
            return geocoded_data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for '{full_address}': {e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Network error for '{full_address}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for '{full_address}': {e}")
            return None

    async def geocode_events_batch(
        self,
        events: List[Dict[str, Any]],
        batch_size: int = 10,
        delay_between_batches: float = 15.0
    ) -> List[Dict[str, Any]]:
        """
        Geocode multiple events in parallel batches.

        Args:
            events: List of event dictionaries
            batch_size: Number of concurrent requests (default: 10)
            delay_between_batches: Seconds to wait between batches (default: 15s)

        Returns:
            List of events with geocoding data
        """
        if not self.api_key:
            logger.warning("OpenRouteService API key not configured, skipping geocoding")
            await self.cache.close()
            return events

        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }

        total_events = len(events)
        logger.info(f"Starting async geocoding for {total_events} events (batch_size={batch_size})")

        async with httpx.AsyncClient(headers=headers, limits=httpx.Limits(max_connections=batch_size)) as client:
            # Process events in batches to respect rate limit (40 req/min)
            for i in range(0, total_events, batch_size):
                batch = events[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_events + batch_size - 1) // batch_size

                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} events)")

                # Create tasks for this batch
                tasks = []
                for event in batch:
                    task = self.geocode_address(
                        client=client,
                        address=event.get('address'),
                        city=event.get('city'),
                        zipcode=event.get('zipcode'),
                        country=event.get('country', 'France')
                    )
                    tasks.append(task)

                # Execute batch in parallel
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Update events with geocoding results
                for event, geocoded in zip(batch, results):
                    if isinstance(geocoded, dict) and geocoded:
                        event.update({
                            'latitude': geocoded.get('latitude'),
                            'longitude': geocoded.get('longitude'),
                            'display_name': geocoded.get('display_name'),
                            'place_id': geocoded.get('place_id'),
                        })

                # Wait between batches to respect rate limit (40 req/min)
                if i + batch_size < total_events:
                    logger.debug(f"Waiting {delay_between_batches}s before next batch...")
                    await asyncio.sleep(delay_between_batches)

        geocoded_count = sum(1 for e in events if e.get('latitude'))
        logger.info(f"Async geocoding completed: {geocoded_count}/{total_events} events geocoded")

        await self.cache.close()
        return events

    def geocode_events_sync(
        self,
        events: List[Dict[str, Any]],
        batch_size: int = 10,
        delay_between_batches: float = 15.0
    ) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for async geocoding.

        Args:
            events: List of event dictionaries
            batch_size: Number of concurrent requests
            delay_between_batches: Seconds to wait between batches

        Returns:
            List of events with geocoding data
        """
        return asyncio.run(self.geocode_events_batch(events, batch_size, delay_between_batches))
