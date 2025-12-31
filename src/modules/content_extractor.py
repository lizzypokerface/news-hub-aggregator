import logging
import re
import time
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

from modules.youtube_transcript_api_handler import YoutubeTranscriptApiHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    A dedicated class for extracting raw text content from various sources.
    Implements a 'Tiered' extraction strategy: Paid API -> Free API -> Selenium.
    """

    def __init__(self, config: dict = None, headless: bool = True):
        self.config = config or {}
        self.headless = headless
        self.max_retries = 2
        self.retry_delays = [2, 2]

        # Load Paid API Key
        self.paid_api_key = self.config.get("api_keys", {}).get(
            "youtube_transcript_api"
        )

    def _init_driver(self):
        """Initializes and returns a fresh Firefox WebDriver."""
        options = FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        )
        try:
            logger.info("Initializing Firefox WebDriver...")  # Logging
            driver = webdriver.Firefox(options=options)
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to initialize Firefox WebDriver: {e}")
            raise

    def _clean_html_content(self, html_content: str) -> str:
        logger.info("Cleaning HTML content...")  # Logging
        soup = BeautifulSoup(html_content, "html.parser")
        for script_or_style in soup(
            ["script", "style", "noscript", "header", "footer", "nav", "aside"]
        ):
            script_or_style.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _get_video_id(self, url: str) -> str:
        logger.info(f"Extracting video ID from URL: {url}")
        parsed = urlparse(url)
        if parsed.hostname in ["www.youtube.com", "youtube.com"]:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]
            elif parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[-1]
        elif parsed.hostname == "youtu.be":
            return parsed.path.split("/")[-1]
        return None

    def _extract_transcript_paid_youtube_api(self, youtube_url: str) -> str:
        """
        Tier 0 Method: Extracts transcript using the Paid youtube-transcript.io API.
        Uses YoutubeTranscriptApiHandler to fetch Title, Date, and Text.
        Includes retry logic for network stability.
        """
        if not self.paid_api_key:
            logger.info("No paid API key found.")
            return ""

        video_id = self._get_video_id(youtube_url)
        if not video_id:
            logger.warning(f"Could not determine Video ID for Paid API: {youtube_url}")
            return ""

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"Paid API Retry {attempt + 1}/{self.max_retries + 1} for {video_id}..."
                    )
                else:
                    logger.info(
                        f"Attempting Paid API extraction for Video ID: {video_id}"
                    )

                # Instantiate the Handler (Request happens here)
                handler = YoutubeTranscriptApiHandler(
                    video_id, api_token=self.paid_api_key
                )

                # Fetch Data
                transcript_text = handler.get_transcript_text()
                title = handler.get_video_title()
                date = handler.get_publish_date()

                logger.info("Paid API extraction successful.")

                # Format: Title + Date + Transcript
                return f"Title: {title}\nDate: {date}\n\n{transcript_text}"

            except Exception as e:
                logger.warning(
                    f"Paid API attempt {attempt + 1} failed for {video_id}: {e}"
                )

                if attempt < self.max_retries:
                    time.sleep(self.retry_delays[attempt])

        logger.error(f"All Paid API attempts failed for {video_id}.")
        return ""

    def _extract_transcript_free_youtube_api(self, youtube_url: str) -> str:
        """Tier 1 Method: Extracts transcript using the free youtube-transcript-api."""
        video_id = self._get_video_id(youtube_url)
        if not video_id:
            logger.info("No video ID found for Free API.")  # Logging
            return ""

        logger.info(f"Attempting Free API extraction for Video ID: {video_id}")
        try:
            ytt_api = YouTubeTranscriptApi()
            transcripts_snippets_list = ytt_api.fetch(video_id=video_id)
            full_text = " ".join([t.text for t in transcripts_snippets_list])
            logger.info("Free API extraction successful.")
            return full_text
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.warning(f"Free API Transcript unavailable for {video_id}.")
            return ""
        except Exception as e:
            logger.error(f"Free API extraction error for {video_id}: {e}")
            return ""

    def _extract_transcript_youtube_tactiq(self, youtube_url: str) -> str:
        """Tier 2 Method: Extracts YouTube transcript using Tactiq via Selenium."""
        logger.info(f"Starting Selenium/Tactiq fallback for: {youtube_url}")
        tactiq_base_url = "https://tactiq.io/tools/youtube-transcript"

        for attempt in range(self.max_retries + 1):
            driver = None
            try:
                if attempt > 0:
                    logger.info(f"Tactiq Retry {attempt + 1}/{self.max_retries + 1}...")

                driver = self._init_driver()
                driver.get(tactiq_base_url)

                url_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "yt-2"))
                )
                url_input.send_keys(youtube_url)

                btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//input[@value='Get Video Transcript']")
                    )
                )
                btn.click()

                WebDriverWait(driver, 20).until(
                    EC.url_contains("run/youtube_transcript")
                )
                container = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "transcript"))
                )
                WebDriverWait(driver, 30).until(lambda d: container.text.strip() != "")

                raw_text = container.text
                cleaned_text = re.sub(
                    r"\d{2}:\d{2}:\d{2}\.\d{3}\s*", "", raw_text
                ).strip()

                if cleaned_text:
                    logger.info(f"Tactiq extraction successful on attempt {attempt+1}")
                    return cleaned_text

            except Exception as e:
                logger.warning(f"Tactiq attempt {attempt + 1} failed: {e}")
            finally:
                if driver:
                    driver.quit()

            if attempt < self.max_retries:
                time.sleep(self.retry_delays[attempt])

        logger.error("All Tactiq attempts failed.")
        return ""

    def _extract_webpage_content(self, url: str) -> str:
        """Extracts webpage content using Selenium + BS4."""
        for attempt in range(self.max_retries + 1):
            driver = None
            try:
                if attempt > 0:
                    logger.info(
                        f"Webpage Retry {attempt + 1}/{self.max_retries + 1}..."
                    )

                driver = self._init_driver()
                driver.get(url)

                WebDriverWait(driver, 20).until(
                    lambda d: d.find_element(By.TAG_NAME, "body").text.strip() != ""
                )

                html = driver.page_source
                cleaned_text = self._clean_html_content(html)

                if cleaned_text:
                    logger.info(f"Webpage extraction successful on attempt {attempt+1}")
                    return cleaned_text

            except Exception as e:
                logger.warning(f"Webpage attempt {attempt + 1} failed: {e}")
            finally:
                if driver:
                    driver.quit()

            if attempt < self.max_retries:
                time.sleep(self.retry_delays[attempt])
        logger.error("All webpage extraction attempts failed.")
        return ""

    def get_text(self, url: str) -> str:
        """
        Public Router. Order: Paid API -> Free API -> Selenium.
        """
        logger.info(f"Starting content extraction for URL: {url}")
        parsed = urlparse(url)
        is_youtube = "youtube.com" in parsed.hostname or "youtu.be" in parsed.hostname

        if is_youtube:
            # 1. Tier 0: Paid API
            content = self._extract_transcript_paid_youtube_api(url)
            if content:
                return content

            # 2. Tier 1: Free API
            logger.info("Paid API yielded no result. Trying Free API...")
            content = self._extract_transcript_free_youtube_api(url)
            if content:
                return content

            # 3. Tier 2: Selenium Fallback
            logger.info("Free API yielded no result. Switching to Tactiq fallback...")
            return self._extract_transcript_youtube_tactiq(url)
        else:
            return self._extract_webpage_content(url)
