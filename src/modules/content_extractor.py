import logging
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
)
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    A dedicated class for extracting raw text content from various sources (YouTube, Webpages).
    This replaces the extraction logic previously embedded in ContentSummarizer.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initializes and returns a Firefox WebDriver."""
        options = FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")

        # Stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        )

        try:
            driver = webdriver.Firefox(options=options)
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to initialize Firefox WebDriver: {e}")
            raise

    def _clean_html_content(self, html_content: str) -> str:
        """Cleans HTML content by extracting visible text."""
        soup = BeautifulSoup(html_content, "html.parser")
        for script_or_style in soup(
            ["script", "style", "noscript", "header", "footer", "nav", "aside"]
        ):
            script_or_style.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_transcript_youtube_tactiq(self, youtube_url: str) -> str:
        """Extracts YouTube transcript using Tactiq via Selenium."""
        logger.info(f"Extracting YouTube transcript via Tactiq for: {youtube_url}")
        tactiq_base_url = "https://tactiq.io/tools/youtube-transcript"
        driver = None

        try:
            driver = self._init_driver()
            driver.get(tactiq_base_url)

            # Interact with Tactiq input
            url_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "yt-2"))
            )
            url_input.send_keys(youtube_url)

            btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@value='Get Video Transcript']")
                )
            )
            btn.click()

            # Wait for transcript container
            WebDriverWait(driver, 20).until(EC.url_contains("run/youtube_transcript"))
            container = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "transcript"))
            )

            # Wait for text to appear
            WebDriverWait(driver, 20).until(lambda d: container.text.strip() != "")

            # Cleanup text (remove timestamps)
            raw_text = container.text
            cleaned_text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3}\s*", "", raw_text)

            return cleaned_text.strip()

        except Exception as e:
            logger.error(f"Tactiq extraction failed for {youtube_url}: {e}")
            return f"[Error extracting YouTube transcript: {e}]"
        finally:
            if driver:
                driver.quit()

    def _extract_webpage_content(self, url: str) -> str:
        """Extracts text from a generic webpage using Selenium + BS4."""
        logger.info(f"Extracting webpage content for: {url}")
        driver = None

        try:
            driver = self._init_driver()
            driver.get(url)

            # Wait for body text
            WebDriverWait(driver, 30).until(
                lambda d: d.find_element(By.TAG_NAME, "body").text.strip() != ""
            )

            html = driver.page_source
            return self._clean_html_content(html)

        except Exception as e:
            logger.error(f"Webpage extraction failed for {url}: {e}")
            return f"[Error extracting webpage content: {e}]"
        finally:
            if driver:
                driver.quit()

    def get_text(self, url: str) -> str:
        """
        Public method to route the URL to the correct extraction strategy.
        """
        parsed = urlparse(url)
        # Simple heuristic to detect YouTube
        if "youtube.com" in parsed.hostname or "youtu.be" in parsed.hostname:
            return self._extract_transcript_youtube_tactiq(url)
        else:
            return self._extract_webpage_content(url)
