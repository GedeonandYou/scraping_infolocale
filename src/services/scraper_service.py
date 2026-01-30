"""Service for scraping events from Infolocale.fr with Selenium - REAL IMPLEMENTATION."""

import time
import hashlib
import os
import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from loguru import logger

from src.config.settings import get_settings
from src.services.geocoding_service import GeocodingService
from src.services.storage_service import StorageService

settings = get_settings()


class ScraperService:
    """Service to scrape events from Infolocale.fr with Selenium + real selectors."""

    BASE_URL = "https://www.infolocale.fr"

    def __init__(self):
        """Initialize scraper service with Selenium."""
        self.geocoding_service = GeocodingService()
        self.storage_service = StorageService()
        self.driver = None
        self.existing_uids = set()

    def _init_driver(self):
        """Initialize Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Mode sans interface
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'user-agent={settings.SCRAPING_USER_AGENT}')

        # Chemin vers le ChromeDriver local
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')

        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome WebDriver initialized")

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

    def _fetch_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch and parse a page with Selenium.

        Args:
            url: URL to scrape

        Returns:
            List of parsed events
        """
        logger.info(f"Fetching: {url}")

        try:
            self.driver.get(url)

            # Attendre que le JavaScript charge le contenu
            time.sleep(5)

            # Scroll pour charger plus de contenu
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Récupérer le HTML
            html = self.driver.page_source

            # Parser
            soup = BeautifulSoup(html, 'lxml')

            # Extraire les cartes d'événements
            cards = soup.select('.memo-card')
            logger.info(f"Found {len(cards)} event cards")

            # Si aucune carte HTML, la page est vide
            if len(cards) == 0:
                logger.warning(f"No event cards found (page might be empty)")
                return None  # Signal qu'il faut arrêter

            events = []
            for card in cards:
                try:
                    event_data = self._parse_event_card(str(card))
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    logger.error(f"Error processing card: {e}")
                    continue

            # Log : Nouveaux vs déjà existants
            logger.info(f"Parsed {len(events)} new events (out of {len(cards)} cards)")

            # Respecter le rate limiting
            time.sleep(settings.SCRAPING_DELAY)

            return events

        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            return []

    def scrape_events(
        self,
        region: Optional[str] = None,
        max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape events with pagination.

        Args:
            region: Region to filter (not implemented yet)
            max_pages: Maximum number of pages to scrape

        Returns:
            List of event dictionaries
        """
        logger.info(f"Starting scraping process (max_pages={max_pages})")

        # Initialiser Selenium
        self._init_driver()

        # Charger UIDs existants
        self.existing_uids = self.storage_service.get_all_uids()
        logger.info(f"Loaded {len(self.existing_uids)} existing event UIDs")

        all_events = []

        try:
            # URL de base
            base_url = f"{self.BASE_URL}/evenements"

            for page in range(1, max_pages + 1):
                # Pagination (à adapter selon le site)
                url = base_url if page == 1 else f"{base_url}?page={page}"

                events = self._fetch_page(url)

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
            region: Region to filter
            max_pages: Maximum number of pages
            with_geocoding: Enable geocoding

        Returns:
            Number of events saved
        """
        events = self.scrape_events(region=region, max_pages=max_pages)

        if not events:
            logger.warning("No events to store")
            return 0

        # Geocodage (optionnel)
        if with_geocoding and self.geocoding_service.api_key:
            logger.info("Starting geocoding process...")
            for i, event in enumerate(events, 1):
                try:
                    self.geocoding_service.geocode_event(event)
                    # Pause pour respecter le rate limit (40 req/min = 1.5 sec entre chaque)
                    if i < len(events):  # Pas de pause après le dernier
                        time.sleep(2)  # 2 secondes = 30 req/min (sécurité)
                        logger.debug(f"Geocoded {i}/{len(events)} events")
                except Exception as e:
                    logger.error(f"Error geocoding event {event.get('uid')}: {e}")

        # Stocker en batch
        saved_count = self.storage_service.save_events_batch(events)
        logger.info(f"Scraping session completed: {saved_count} events saved to database")

        return saved_count

    def close(self):
        """Close WebDriver."""
        if self.driver:
            self.driver.quit()
