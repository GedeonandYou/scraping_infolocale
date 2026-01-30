"""Service for scraping events from Infolocale.fr with Selenium - REAL IMPLEMENTATION."""

import hashlib
import time
import os
import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from loguru import logger

from src.config.settings import get_settings
from src.services.async_geocoding_service import AsyncGeocodingService
from src.services.storage_service import StorageService

settings = get_settings()


class ScraperService:
    """Service to scrape events from Infolocale.fr with Selenium + real selectors."""

    BASE_URL = "https://www.infolocale.fr"

    def __init__(self):
        """Initialize scraper service with Selenium."""
        self.geocoding_service = AsyncGeocodingService()
        self.storage_service = StorageService()
        self.driver = None
        self.existing_uids = set()

    def _build_driver(self):
        """Build a Chrome WebDriver with performance optimizations."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Mode sans interface
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'user-agent={settings.SCRAPING_USER_AGENT}')

        # Performance optimizations
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.page_load_strategy = 'eager'  # Don't wait for full page load

        # Additional performance
        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'profile.default_content_setting_values.notifications': 2,
            'profile.managed_default_content_settings.stylesheets': 2,
            'profile.managed_default_content_settings.cookies': 1,
            'profile.managed_default_content_settings.javascript': 1,
            'profile.managed_default_content_settings.plugins': 2,
            'profile.managed_default_content_settings.popups': 2,
            'profile.managed_default_content_settings.geolocation': 2,
            'profile.managed_default_content_settings.media_stream': 2,
        }
        chrome_options.add_experimental_option('prefs', prefs)

        # Chemin vers le ChromeDriver local
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')

        service = Service(executable_path=chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)

    def _init_driver(self):
        """Initialize Chrome WebDriver with performance optimizations."""
        self.driver = self._build_driver()
        logger.info("Chrome WebDriver initialized with performance optimizations")

    def _generate_uid(self, data_id: str) -> str:
        """
        Generate UID from data-id attribute.

        Args:
            data_id: data-id from HTML card

        Returns:
            UID for database
        """
        return f"infolocale_{data_id}"

    def _parse_french_date(self, date_str: Optional[str]) -> Optional[date]:
        """
        Parse French date format to Python date.

        Args:
            date_str: Date string like "28 Janv.", "15 Févr.", etc.

        Returns:
            Python date object or None
        """
        if not date_str:
            return None

        # Mapping des mois français abrégés
        french_months = {
            'janv': 1, 'févr': 2, 'mars': 3, 'avr': 4, 'mai': 5, 'juin': 6,
            'juil': 7, 'août': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'déc': 12
        }

        try:
            # Normaliser et nettoyer
            date_str = unicodedata.normalize('NFKD', date_str.lower())
            date_str = date_str.replace('.', '').strip()

            # Pattern: "28 janv"
            match = re.match(r'(\d{1,2})\s+(\w+)', date_str)
            if match:
                day = int(match.group(1))
                month_str = match.group(2)[:4]  # Prendre les 4 premières lettres

                # Trouver le mois
                month = None
                for key, val in french_months.items():
                    if month_str.startswith(key):
                        month = val
                        break

                if month:
                    # Déterminer l'année (si la date est passée cette année, c'est l'année prochaine)
                    today = datetime.now()
                    year = today.year
                    try:
                        parsed_date = date(year, month, day)
                        # Si la date est dans le passé (plus de 30 jours), c'est probablement l'année prochaine
                        if (today.date() - parsed_date).days > 30:
                            parsed_date = date(year + 1, month, day)
                        return parsed_date
                    except ValueError:
                        logger.warning(f"Invalid date: day={day}, month={month}, year={year}")
                        return None

            logger.warning(f"Could not parse French date: {date_str}")
            return None

        except Exception as e:
            logger.error(f"Error parsing French date '{date_str}': {e}")
            return None

    def _parse_french_time_range(self, time_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse French time format to start and end times.

        Args:
            time_str: Time string like "à 21h00", "de 14h30 à 18h00", etc.

        Returns:
            Tuple of (start_time, end_time) as strings or (None, None)
        """
        if not time_str:
            return None, None

        try:
            # Nettoyer
            time_str = time_str.strip()

            # Pattern 1: "à 21h00"
            match = re.search(r'à\s+(\d{1,2})h(\d{2})', time_str)
            if match:
                start_time = f"{match.group(1).zfill(2)}:{match.group(2)}"
                return start_time, None

            # Pattern 2: "de 14h30 à 18h00"
            match = re.search(r'de\s+(\d{1,2})h(\d{2})\s+à\s+(\d{1,2})h(\d{2})', time_str)
            if match:
                start_time = f"{match.group(1).zfill(2)}:{match.group(2)}"
                end_time = f"{match.group(3).zfill(2)}:{match.group(4)}"
                return start_time, end_time

            # Pattern 3: "21h00" (sans "à")
            match = re.search(r'(\d{1,2})h(\d{2})', time_str)
            if match:
                start_time = f"{match.group(1).zfill(2)}:{match.group(2)}"
                return start_time, None

            logger.warning(f"Could not parse French time: {time_str}")
            return None, None

        except Exception as e:
            logger.error(f"Error parsing French time '{time_str}': {e}")
            return None, None

    def _parse_event_card(self, card_html: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single .memo-card event card with REAL selectors.

        Args:
            card_html: HTML of the card

        Returns:
            Event data dictionary or None
        """
        soup = BeautifulSoup(card_html, 'lxml')

        try:
            # Data-ID (identifiant unique Infolocale)
            card = soup.select_one('.memo-card')
            if not card:
                return None

            data_id = card.get('data-id')
            if not data_id:
                logger.warning("No data-id found")
                return None

            # UID
            uid = self._generate_uid(data_id)

            # Vérifier déduplication
            if uid in self.existing_uids:
                logger.debug(f"Event {uid} already exists, skipping")
                return None

            # Titre (dans l'alt de l'image)
            title_elem = soup.select_one('img.thumbnail')
            title = title_elem.get('alt', 'Sans titre') if title_elem else 'Sans titre'

            # Catégorie
            category_elem = soup.select_one('.gender')
            category = category_elem.text.strip() if category_elem else None

            # Dates
            dates = soup.select('.day')
            begin_date_raw = dates[0].text.strip() if dates else None

            # Heure (généralement dans le 2e .day)
            start_time_raw = dates[1].text.strip() if len(dates) > 1 else None

            begin_date = self._parse_french_date(begin_date_raw)
            start_time, end_time = self._parse_french_time_range(start_time_raw)

            # Ville (contient code postal)
            location_elem = soup.select_one('.location')
            city_full = location_elem.text.strip() if location_elem else None

            # Parser ville et code postal (ex: "La Roche-sur-Yon (85000)")
            city = None
            zipcode = None
            if city_full:
                match = re.match(r'(.+)\s+\((\d{5})\)', city_full)
                if match:
                    city = match.group(1).strip()
                    zipcode = match.group(2)
                else:
                    city = city_full

            # Organisateur
            organizer_elem = soup.select_one('.card-header .name')
            organizer = organizer_elem.text.strip() if organizer_elem else None

            # Image
            image_elem = soup.select_one('img.thumbnail')
            image_url = None
            if image_elem:
                image_url = image_elem.get('data-path') or image_elem.get('src')

            # Lieu (nom de l'équipement)
            location_name = organizer  # Souvent le même que l'organisateur

            event_data = {
                'uid': uid,
                'user_id': settings.DEFAULT_USER_ID,
                'title': title,
                'category': category,
                'begin_date': begin_date,
                'start_time': start_time,
                'end_time': end_time,
                'city': city,
                'zipcode': zipcode,
                'organizer': organizer,
                'location_name': location_name,
                'image_path': image_url,
                'country': 'France',
                'raw_json': {
                    'data_id': data_id,
                    'city_full': city_full,
                    'begin_date_raw': begin_date_raw,
                    'start_time_raw': start_time_raw,
                },
            }

            logger.debug(f"Parsed event: {title}")
            return event_data

        except Exception as e:
            logger.error(f"Error parsing event card: {e}")
            return None

    @staticmethod
    def _normalize_text(value: str) -> str:
        """Normalize a French text token to ASCII-friendly lowercase."""
        value = value.strip().lower().replace('.', ' ')
        value = unicodedata.normalize("NFKD", value)
        value = "".join(ch for ch in value if not unicodedata.combining(ch))
        value = re.sub(r"[^0-9a-z :]+", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value

    def _parse_french_date(self, date_text: Optional[str]) -> Optional[date]:
        """Parse French date strings like '28 Janv.' into a date object."""
        if not date_text:
            return None

        normalized = self._normalize_text(date_text)
        if not normalized:
            return None

        normalized = re.sub(r"(\d{1,2})er\b", r"\1", normalized)

        today = datetime.utcnow().date()

        if "aujourdhui" in normalized:
            return today
        if "demain" in normalized:
            return today + timedelta(days=1)

        month_map = {
            "janv": 1,
            "janvier": 1,
            "fevr": 2,
            "fevrier": 2,
            "mars": 3,
            "avr": 4,
            "avril": 4,
            "mai": 5,
            "juin": 6,
            "juil": 7,
            "juillet": 7,
            "aout": 8,
            "sept": 9,
            "septembre": 9,
            "oct": 10,
            "octobre": 10,
            "nov": 11,
            "novembre": 11,
            "dec": 12,
            "decembre": 12,
        }

        match = re.search(r"(\d{1,2})\s+([a-z]+)\s*(\d{4})?", normalized)
        if not match:
            logger.debug(f"Unable to parse date: {date_text}")
            return None

        day = int(match.group(1))
        month_token = match.group(2)
        year_token = match.group(3)

        month = month_map.get(month_token)
        if not month:
            logger.debug(f"Unknown month token '{month_token}' in date: {date_text}")
            return None

        year = int(year_token) if year_token else today.year

        try:
            return date(year, month, day)
        except ValueError:
            logger.debug(f"Invalid date components from '{date_text}'")
            return None

    def _parse_french_time_range(self, time_text: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Parse French time strings like 'à 21h00' or '21h-23h'."""
        if not time_text:
            return None, None

        normalized = self._normalize_text(time_text)
        if not normalized:
            return None, None

        matches = re.findall(r"(\d{1,2})\s*(?:h|:)\s*(\d{2})?", normalized)
        if not matches:
            logger.debug(f"Unable to parse time: {time_text}")
            return None, None

        def format_time(parts: Tuple[str, str]) -> Optional[str]:
            hour = int(parts[0])
            minute = int(parts[1]) if parts[1] else 0
            if hour > 23 or minute > 59:
                return None
            return f"{hour:02d}:{minute:02d}"

        start_time = format_time(matches[0])
        end_time = format_time(matches[1]) if len(matches) > 1 else None

        return start_time, end_time

    @staticmethod
    def _append_page_param(url: str, page: int) -> str:
        """Append or replace the page query parameter."""
        if page <= 1:
            return url
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query))
        query["page"] = str(page)
        new_query = urlencode(query)
        return urlunparse(parsed._replace(query=new_query))

    @staticmethod
    def _split_regions(region: Optional[str]) -> List[str]:
        if not region:
            return []
        return [token.strip() for token in region.split(",") if token.strip()]

    def _build_region_base_url(self, region: Optional[str]) -> str:
        """Build the base URL for a region (slug, path, or full URL)."""
        if not region:
            return f"{self.BASE_URL}/evenements"
        region = region.strip()
        if region.startswith("http://") or region.startswith("https://"):
            return region.rstrip("/")
        if region.startswith("/"):
            return f"{self.BASE_URL}{region}"
        template = settings.SCRAPING_REGION_URL_TEMPLATE
        return template.format(base_url=self.BASE_URL, region=quote_plus(region))

    @staticmethod
    def _dedupe_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events by uid while preserving first occurrence."""
        unique: Dict[str, Dict[str, Any]] = {}
        for event in events:
            uid = event.get("uid")
            if not uid:
                continue
            if uid not in unique:
                unique[uid] = event
        return list(unique.values())

    def _scrape_url_chunk(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape a list of URLs using a dedicated WebDriver instance."""
        if not urls:
            return []
        driver = self._build_driver()
        try:
            events: List[Dict[str, Any]] = []
            for url in urls:
                page_events = self._fetch_page(url, driver)
                if page_events is None:
                    break
                if page_events:
                    events.extend(page_events)
            return events
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    def _scrape_urls_parallel(self, urls: List[str], max_workers: int) -> List[Dict[str, Any]]:
        """Scrape multiple pages in parallel using multiple drivers."""
        if not urls:
            return []
        max_workers = max(1, max_workers)
        chunks = [urls[i::max_workers] for i in range(max_workers)]
        events: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._scrape_url_chunk, chunk) for chunk in chunks if chunk]
            for future in as_completed(futures):
                try:
                    events.extend(future.result() or [])
                except Exception as e:
                    logger.error(f"Error in parallel scrape worker: {e}")
        return events

    def _fetch_page(self, url: str, driver: Optional[webdriver.Chrome] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch and parse a page with Selenium using smart waits.

        Args:
            url: URL to scrape

        Returns:
            List of parsed events
        """
        logger.info(f"Fetching: {url}")

        try:
            driver = driver or self.driver
            if not driver:
                raise RuntimeError("WebDriver not initialized")

            driver.get(url)

            # Wait for event cards to load (smart wait instead of sleep)
            wait = WebDriverWait(driver, 15)
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.memo-card')))
                logger.debug("Event cards loaded")
            except:
                logger.warning("No event cards found after 15s wait")
                return None

            # Scroll to load lazy content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for any lazy-loaded cards (shorter wait)
            time.sleep(1)

            # Get HTML
            html = driver.page_source

            # Parse
            soup = BeautifulSoup(html, 'lxml')

            # Extract event cards
            cards = soup.select('.memo-card')
            logger.info(f"Found {len(cards)} event cards")

            # If no HTML cards, page is empty
            if len(cards) == 0:
                logger.warning(f"No event cards found (page might be empty)")
                return None  # Signal to stop

            events = []
            for card in cards:
                try:
                    event_data = self._parse_event_card(str(card))
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    logger.error(f"Error processing card: {e}")
                    continue

            # Log: New vs already existing
            logger.info(f"Parsed {len(events)} new events (out of {len(cards)} cards)")

            return events

        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            return []

    def scrape_events(
        self,
        region: Optional[str] = None,
        max_pages: int = 5,
        parallel_pages: Optional[bool] = None,
        max_workers: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scrape events with pagination.

        Args:
            region: Region slug/path/URL (comma-separated for multiple)
            max_pages: Maximum number of pages to scrape
            parallel_pages: Enable parallel page scraping
            max_workers: Max parallel drivers

        Returns:
            List of event dictionaries
        """
        parallel_pages = settings.SCRAPING_PARALLEL_PAGES if parallel_pages is None else parallel_pages
        max_workers = max_workers or settings.SCRAPING_MAX_WORKERS

        logger.info(
            f"Starting scraping process (max_pages={max_pages}, parallel_pages={parallel_pages})"
        )

        # Charger UIDs existants
        self.existing_uids = self.storage_service.get_all_uids()
        logger.info(f"Loaded {len(self.existing_uids)} existing event UIDs")

        all_events = []

        region_tokens = self._split_regions(region) or [None]

        if parallel_pages and max_pages > 1:
            urls: List[str] = []
            for token in region_tokens:
                base_url = self._build_region_base_url(token)
                for page in range(1, max_pages + 1):
                    urls.append(self._append_page_param(base_url, page))
            all_events = self._scrape_urls_parallel(urls, max_workers)
        else:
            # Initialiser Selenium (single driver)
            self._init_driver()
            try:
                for token in region_tokens:
                    base_url = self._build_region_base_url(token)
                    for page in range(1, max_pages + 1):
                        url = self._append_page_param(base_url, page)
                        events = self._fetch_page(url, self.driver)

                        # Si None, la page est vide (aucune carte HTML) → arrêter
                        if events is None:
                            logger.info(f"No event cards on page {page}, stopping")
                            break

                        # Si liste vide, tous les événements existent déjà → continuer
                        if len(events) == 0:
                            logger.info(f"Page {page}: 0 new events (all duplicates), continuing...")
                            continue

                        all_events.extend(events)
                        logger.info(f"Page {page}: {len(events)} new events collected")
            finally:
                if self.driver:
                    self.driver.quit()
                    logger.info("WebDriver closed")

        all_events = self._dedupe_events(all_events)
        logger.info(f"Scraping completed: {len(all_events)} events collected")
        return all_events

    def scrape_and_store(
        self,
        region: Optional[str] = None,
        max_pages: int = 5,
        with_geocoding: bool = True,
        parallel_pages: Optional[bool] = None,
        max_workers: Optional[int] = None,
    ) -> int:
        """
        Scrape events and store them in database.

        Args:
            region: Region slug/path/URL (comma-separated for multiple)
            max_pages: Maximum number of pages
            with_geocoding: Enable geocoding
            parallel_pages: Enable parallel page scraping
            max_workers: Max parallel drivers

        Returns:
            Number of events saved
        """
        events = self.scrape_events(
            region=region,
            max_pages=max_pages,
            parallel_pages=parallel_pages,
            max_workers=max_workers,
        )

        if not events:
            logger.warning("No events to store")
            return 0

        # Geocodage (optionnel)
        if with_geocoding and self.geocoding_service.api_key:
            logger.info("Starting async geocoding process...")
            try:
                events = self.geocoding_service.geocode_events_sync(
                    events,
                    batch_size=settings.GEOCODING_BATCH_SIZE,
                    delay_between_batches=settings.GEOCODING_BATCH_DELAY,
                )
            except Exception as e:
                logger.error(f"Error during async geocoding: {e}")

        # Stocker en batch
        saved_count = self.storage_service.save_events_batch(events)
        logger.info(f"Scraping session completed: {saved_count} events saved to database")

        return saved_count

    def close(self):
        """Close WebDriver."""
        if self.driver:
            self.driver.quit()
