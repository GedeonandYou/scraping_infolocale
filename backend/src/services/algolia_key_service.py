"""Service pour recuperer automatiquement la cle API Algolia depuis infolocale.fr.

Utilise Selenium + Chrome DevTools Protocol (CDP) pour intercepter les requetes
reseau vers algolia.net et capturer le header X-Algolia-API-Key.
"""

import base64
import json
import re
import time
from typing import Optional
from urllib.parse import parse_qs, urlparse

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class AlgoliaKeyService:
    """Recupere la cle API Algolia en interceptant les requetes du frontend infolocale.fr."""

    INFOLOCALE_URL = "https://www.infolocale.fr/activites"

    MAX_RETRIES = 3

    @staticmethod
    def fetch_key() -> Optional[str]:
        """
        Lance Chrome headless, charge infolocale.fr/activites, et intercepte
        le header X-Algolia-API-Key dans les requetes vers algolia.net.

        Gere le WAF Ouest-France avec attente du challenge et retries.
        Fallback: extrait la cle depuis le code source JS de la page.

        Returns:
            La cle API Algolia (base64 raw) ou None si echec.
        """
        driver = None
        try:
            driver = AlgoliaKeyService._create_driver()

            for attempt in range(1, AlgoliaKeyService.MAX_RETRIES + 1):
                logger.info(f"Tentative {attempt}/{AlgoliaKeyService.MAX_RETRIES}...")

                # Charger la page et attendre le passage du WAF
                page_ok = AlgoliaKeyService._load_page_past_waf(driver)

                if page_ok:
                    # Methode 1 : intercepter les requetes reseau via CDP
                    api_key = AlgoliaKeyService._find_key_in_logs(driver)

                    # Methode 2 (fallback) : extraire la cle depuis le source JS
                    if not api_key:
                        logger.info("Fallback: extraction de la cle depuis le source de la page...")
                        api_key = AlgoliaKeyService._extract_key_from_source(driver)

                    if api_key:
                        valid_until = AlgoliaKeyService._get_valid_until(api_key)
                        if valid_until:
                            logger.info(f"Cle Algolia recuperee (validUntil={valid_until})")
                        else:
                            logger.info("Cle Algolia recuperee (validUntil non lisible)")
                        return api_key
                else:
                    logger.warning("Page bloquee par le WAF")

                if attempt < AlgoliaKeyService.MAX_RETRIES:
                    wait = attempt * 5
                    logger.info(f"Attente de {wait}s avant nouvelle tentative...")
                    time.sleep(wait)
                    # Vider les logs avant de reessayer
                    driver.get_log("performance")

            logger.error("Aucune cle Algolia trouvee apres toutes les tentatives")
            return None

        except Exception as e:
            logger.error(f"Erreur lors de la recuperation de la cle Algolia: {e}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    @staticmethod
    def _create_driver() -> webdriver.Chrome:
        """Cree un Chrome headless avec le logging performance CDP active."""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

        # Masquer les signaux d'automatisation
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Activer le logging performance pour capturer les requetes reseau
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Supprimer navigator.webdriver
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )

        logger.debug("Chrome WebDriver initialise pour capture de cle Algolia")
        return driver

    @staticmethod
    def _load_page_past_waf(driver: webdriver.Chrome, timeout: int = 30) -> bool:
        """
        Charge la page infolocale et attend que le WAF challenge se resolve.

        Le WAF Ouest-France sert une page challenge (~15k chars) qui doit
        s'executer en JS avant de rediriger vers la vraie page (~100k+ chars).

        Returns:
            True si la vraie page a charge, False si WAF toujours bloquant.
        """
        logger.info(f"Chargement de {AlgoliaKeyService.INFOLOCALE_URL} ...")
        driver.get(AlgoliaKeyService.INFOLOCALE_URL)

        # Attendre que le WAF challenge se resolve
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(3)
            page_len = len(driver.page_source)
            title = driver.title
            current_url = driver.current_url
            logger.debug(
                f"Page: taille={page_len}, titre='{title[:50]}...', url={current_url[:80]}"
            )

            # La vraie page fait >100k chars et contient "infolocale" dans le titre
            if page_len > 50000:
                logger.info(f"Page chargee avec succes ({page_len} chars)")
                # Attendre encore un peu pour que les requetes Algolia soient envoyees
                time.sleep(3)
                return True

        page_len = len(driver.page_source)
        logger.warning(f"Timeout WAF: page toujours a {page_len} chars apres {timeout}s")
        return False

    @staticmethod
    def _find_key_in_logs(driver: webdriver.Chrome) -> Optional[str]:
        """
        Parcourt les logs performance CDP pour trouver x-algolia-api-key
        dans les headers OU les query parameters de l'URL.

        Le client Algolia JS v4 envoie la cle comme parametre d'URL.
        """
        logs = driver.get_log("performance")
        logger.debug(f"{len(logs)} entrees de log performance")

        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                method = msg.get("method", "")

                if method == "Network.requestWillBeSent":
                    request = msg["params"]["request"]
                    url = request.get("url", "")

                    if "algolia.net" not in url:
                        continue

                    # Chercher dans les query parameters de l'URL
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    if "x-algolia-api-key" in params:
                        key = params["x-algolia-api-key"][0]
                        logger.debug("Cle trouvee dans les query parameters de l'URL")
                        return key

                    # Chercher dans les headers
                    headers = request.get("headers", {})
                    for header_name, header_value in headers.items():
                        if header_name.lower() == "x-algolia-api-key":
                            logger.debug("Cle trouvee dans les headers")
                            return header_value

            except (KeyError, json.JSONDecodeError):
                continue

        return None

    @staticmethod
    def _extract_key_from_source(driver: webdriver.Chrome) -> Optional[str]:
        """
        Extrait la cle API Algolia depuis le code source de la page.

        Cherche dans le HTML/JS les patterns typiques:
        - apiKey dans __NEXT_DATA__ ou config JS
        - x-algolia-api-key dans des headers JS
        """
        source = driver.page_source

        # Pattern 1: "apiKey":"..." dans le JS (Next.js / config Algolia)
        patterns = [
            r'"apiKey"\s*:\s*"([A-Za-z0-9+/=]{40,})"',
            r"'apiKey'\s*:\s*'([A-Za-z0-9+/=]{40,})'",
            r'"x-algolia-api-key"\s*:\s*"([A-Za-z0-9+/=]{40,})"',
            r'algolia[_-]?(?:api[_-]?)?key["\']?\s*[:=]\s*["\']([A-Za-z0-9+/=]{40,})["\']',
        ]

        for pattern in patterns:
            match = re.search(pattern, source, re.IGNORECASE)
            if match:
                candidate = match.group(1)
                # Verifier que ca ressemble a une secured key Algolia (base64 long)
                if len(candidate) > 50:
                    logger.debug(f"Cle candidate trouvee dans le source (pattern: {pattern[:30]}...)")
                    return candidate

        # Pattern 2: Essayer d'executer du JS pour recuperer la config Algolia
        try:
            key = driver.execute_script(
                "try { "
                "  var scripts = document.querySelectorAll('script'); "
                "  for (var s of scripts) { "
                "    var m = s.textContent.match(/[\"']apiKey[\"']\\s*:\\s*[\"']([A-Za-z0-9+\\/=]{40,})[\"']/); "
                "    if (m) return m[1]; "
                "  } "
                "} catch(e) {} "
                "return null;"
            )
            if key and len(key) > 50:
                logger.debug("Cle trouvee via execution JS")
                return key
        except Exception:
            pass

        return None

    @staticmethod
    def _get_valid_until(api_key: str) -> Optional[int]:
        """
        Decode la cle base64 pour extraire le timestamp validUntil.

        Returns:
            Le timestamp validUntil ou None si non decodable.
        """
        try:
            # Ajouter le padding base64 si necessaire
            padded = api_key + "=" * (-len(api_key) % 4)
            decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")

            # Format: {hex_key}validUntil={timestamp}
            if "validUntil=" in decoded:
                ts_str = decoded.split("validUntil=")[1].split("&")[0]
                return int(ts_str)
        except Exception:
            pass
        return None

    @staticmethod
    def is_key_expired(api_key: str) -> bool:
        """Verifie si la cle Algolia est expiree en lisant le validUntil."""
        valid_until = AlgoliaKeyService._get_valid_until(api_key)
        if valid_until is None:
            return False  # Impossible de determiner, on suppose valide
        return int(time.time()) >= valid_until
