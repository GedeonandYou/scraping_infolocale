"""Service for scraping events from Infolocale.fr."""

import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.services.geocoding_service import GeocodingService
from src.services.storage_service import StorageService

settings = get_settings()


class ScraperService:
    """Service to scrape events from Infolocale.fr."""

    BASE_URL = "https://www.infolocale.fr"

    def __init__(self):
        """Initialize scraper service."""
        self.geocoding_service = GeocodingService()
        self.storage_service = StorageService()
        self.session = httpx.Client(
            headers={
                'User-Agent': settings.SCRAPING_USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            },
            timeout=settings.SCRAPING_TIMEOUT,
            follow_redirects=True,
        )
        self.existing_uids = set()

    def _generate_uid(self, title: str, location: str, date: str) -> str:
        """
        Generate a unique identifier for an event.

        Args:
            title: Event title
            location: Event location
            date: Event date

        Returns:
            Unique identifier (hash)
        """
        unique_string = f"{title}_{location}_{date}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    @retry(
        stop=stop_after_attempt(settings.SCRAPING_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page with retry logic.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()

            # Respect rate limiting
            time.sleep(settings.SCRAPING_DELAY)

            return response.text

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_event_listing(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse event listing page and extract event data.

        Args:
            html: HTML content

        Returns:
            List of event dictionaries
        """
        events = []
        soup = BeautifulSoup(html, 'lxml')

        # TODO: Implement actual parsing logic based on Infolocale HTML structure
        # This is a placeholder - you need to inspect the actual HTML structure

        # Example structure (to be adapted):
        event_cards = soup.find_all('div', class_='event-card')  # Adjust selector

        for card in event_cards:
            try:
                event_data = self._parse_event_card(card)
                if event_data:
                    events.append(event_data)
            except Exception as e:
                logger.error(f"Error parsing event card: {e}")
                continue

        logger.info(f"Parsed {len(events)} events from listing page")
        return events

    def _parse_event_card(self, card) -> Optional[Dict[str, Any]]:
        """
        Parse a single event card from listing page.

        Args:
            card: BeautifulSoup element

        Returns:
            Event data dictionary or None
        """
        # TODO: Implement actual parsing based on HTML structure
        # This is a placeholder implementation

        try:
            # Example parsing (adjust selectors):
            title = card.find('h3', class_='event-title')
            title = title.text.strip() if title else "Unknown Event"

            # Extract location
            location = card.find('span', class_='event-location')
            location_name = location.text.strip() if location else None

            # Extract date
            date_elem = card.find('time', class_='event-date')
            begin_date = date_elem.get('datetime') if date_elem else None

            # Generate UID
            uid = self._generate_uid(
                title=title,
                location=location_name or "",
                date=begin_date or ""
            )

            # Check if already exists
            if uid in self.existing_uids:
                logger.debug(f"Event {uid} already scraped, skipping")
                return None

            event_data = {
                'uid': uid,
                'user_id': settings.DEFAULT_USER_ID,
                'title': title,
                'location_name': location_name,
                'begin_date': begin_date,
                # Add more fields as you parse them
            }

            return event_data

        except Exception as e:
            logger.error(f"Error parsing event card: {e}")
            return None

    def scrape_events(
        self,
        region: Optional[str] = None,
        max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape events from Infolocale.

        Args:
            region: Region to scrape (None for all)
            max_pages: Maximum number of pages to scrape

        Returns:
            List of scraped event dictionaries
        """
        logger.info(f"Starting scraping process (max_pages={max_pages})")

        # Load existing UIDs for deduplication
        self.existing_uids = self.storage_service.get_all_uids()
        logger.info(f"Loaded {len(self.existing_uids)} existing event UIDs")

        all_events = []

        # TODO: Implement actual URL construction based on Infolocale structure
        # This is a placeholder
        base_search_url = f"{self.BASE_URL}/evenements"

        for page in range(1, max_pages + 1):
            url = f"{base_search_url}?page={page}"

            html = self._fetch_page(url)
            if not html:
                logger.warning(f"Failed to fetch page {page}, stopping")
                break

            events = self.parse_event_listing(html)
            if not events:
                logger.info(f"No more events found on page {page}, stopping")
                break

            all_events.extend(events)

        logger.info(f"Scraping completed: {len(all_events)} events collected")
        return all_events

    def scrape_and_store(
        self,
        region: Optional[str] = None,
        max_pages: int = 5,
        with_geocoding: bool = True
    ) -> int:
        """
        Scrape events and store them in database.

        Args:
            region: Region to scrape
            max_pages: Maximum number of pages
            with_geocoding: Whether to geocode addresses

        Returns:
            Number of events saved
        """
        events = self.scrape_events(region=region, max_pages=max_pages)

        if not events:
            logger.warning("No events to store")
            return 0

        # Geocode events if requested
        if with_geocoding and self.geocoding_service.client:
            logger.info("Starting geocoding process...")
            for event in events:
                try:
                    self.geocoding_service.geocode_event(event)
                except Exception as e:
                    logger.error(f"Error geocoding event {event.get('uid')}: {e}")

        # Store events in batch
        saved_count = self.storage_service.save_events_batch(events)
        logger.info(f"Scraping session completed: {saved_count} events saved to database")

        return saved_count

    def close(self):
        """Close HTTP session."""
        self.session.close()
