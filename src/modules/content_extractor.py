import logging
import re
import time
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
)
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

# Configure logging
logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    A dedicated class for extracting raw text content from various sources.
    Replicates the robust retry logic of the legacy ContentSummarizer.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.max_retries = 1
        self.retry_delays = [2]  # Wait 2s between retries

    def _init_driver(self):
        """Initializes and returns a fresh Firefox WebDriver."""
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
        """Standardizes cleaning logic."""
        soup = BeautifulSoup(html_content, "html.parser")
        for script_or_style in soup(
            ["script", "style", "noscript", "header", "footer", "nav", "aside"]
        ):
            script_or_style.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Replicate the exact cleaning from the old reliable file
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\n", " ").replace("\r", "")
        return text.strip()

    def _get_video_id(self, url: str) -> str:
        """robust video ID parsing matching the legacy logic."""
        parsed = urlparse(url)
        if parsed.hostname in ["www.youtube.com", "youtube.com"]:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]
            elif parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[-1]
        elif parsed.hostname == "youtu.be":
            return parsed.path.split("/")[-1]
        return None

    def _extract_transcript_youtube_api(self, youtube_url: str) -> str:
        """
        Primary Method: Extracts transcript using youtube-transcript-api.
        """
        video_id = self._get_video_id(youtube_url)
        if not video_id:
            logger.warning(
                f"Could not determine Video ID for API extraction: {youtube_url}"
            )
            return ""

        logger.info(f"Attempting API extraction for Video ID: {video_id}")
        try:
            ytt_api = YouTubeTranscriptApi()
            transcripts_snippets_list = ytt_api.fetch(video_id=video_id)
            # Combine all text snippets into one string
            full_text = " ".join([t.text for t in transcripts_snippets_list])
            logger.info("API extraction successful.")
            return full_text
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.warning(
                f"API Transcript unavailable/disabled for {video_id}. Fallback required."
            )
            return ""
        except Exception as e:
            logger.error(f"API extraction error for {video_id}: {e}")
            return ""

    def _extract_transcript_youtube_api(self, youtube_url: str) -> str:
        """
        Primary Method: Extracts transcript using youtube-transcript-api.
        Includes retry logic for network glitches, but fails fast for disabled transcripts.
        """
        video_id = self._get_video_id(youtube_url)
        if not video_id:
            logger.warning(
                f"Could not determine Video ID for API extraction: {youtube_url}"
            )
            return ""

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"API Retry {attempt + 1}/{self.max_retries + 1} for {video_id}..."
                    )

                # Fetch Transcript
                ytt_api = YouTubeTranscriptApi()
                transcripts_snippets_list = ytt_api.fetch(video_id=video_id)
                # Combine all text snippets into one string
                full_text = " ".join([t.text for t in transcripts_snippets_list])

                logger.info("API extraction successful.")
                return full_text

            except (TranscriptsDisabled, NoTranscriptFound):
                # Deterministic error: Retrying will not help. Fail fast.
                logger.warning(
                    f"API Transcript unavailable/disabled for {video_id}. Switching to fallback."
                )
                return ""

            except Exception as e:
                # Transient error (Network, etc): Retry allowed.
                logger.error(
                    f"API extraction error for {video_id} (Attempt {attempt + 1}): {e}"
                )

                if attempt < self.max_retries:
                    time.sleep(self.retry_delays[attempt])

    def _extract_transcript_youtube_tactiq(self, youtube_url: str) -> str:
        """
        Fallback Method: Extracts YouTube transcript using Tactiq via Selenium.
        Uses a fresh driver per attempt and waits for content load.
        """
        logger.info(f"Starting Selenium/Tactiq fallback for: {youtube_url}")
        tactiq_base_url = "https://tactiq.io/tools/youtube-transcript"

        for attempt in range(self.max_retries + 1):
            driver = None
            try:
                if attempt > 0:
                    logger.info(f"Tactiq Retry {attempt + 1}/{self.max_retries + 1}...")

                # 1. Fresh Driver per Attempt
                driver = self._init_driver()
                driver.get(tactiq_base_url)
                logger.info(f"Navigated to Tactiq.io: {tactiq_base_url}")

                # 2. Interactions
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
                logger.info("Clicked 'Get Video Transcript' button.")

                # 3. Wait for URL Change
                WebDriverWait(driver, 20).until(
                    EC.url_contains("run/youtube_transcript")
                )

                # 4. Wait for Container Presence
                container = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "transcript"))
                )

                # 5. CRITICAL: Wait for Text Content
                WebDriverWait(driver, 30).until(lambda d: container.text.strip() != "")

                # 6. Clean and Return
                raw_text = container.text
                cleaned_text = re.sub(
                    r"\d{2}:\d{2}:\d{2}\.\d{3}\s*", "", raw_text
                ).strip()
                logger.info("Timestamps removed from Tactiq.io transcript.")

                if cleaned_text:
                    logger.info(f"Tactiq extraction successful on attempt {attempt+1}")
                    return cleaned_text

            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                logger.warning(
                    f"Tactiq attempt {attempt + 1} failed (Selenium Error): {e}"
                )
            except Exception as e:
                logger.error(f"Tactiq attempt {attempt + 1} failed (Unexpected): {e}")
            finally:
                if driver:
                    driver.quit()

            # Backoff
            if attempt < self.max_retries:
                time.sleep(self.retry_delays[attempt])

        return ""

    def _extract_webpage_content(self, url: str) -> str:
        """
        Extracts webpage content using Selenium + BS4 with internal retries.
        """
        for attempt in range(self.max_retries + 1):
            driver = None
            try:
                if attempt > 0:
                    logger.info(
                        f"Webpage Retry {attempt + 1}/{self.max_retries + 1}..."
                    )

                driver = self._init_driver()
                driver.get(url)

                # Wait for body text to be non-empty
                WebDriverWait(driver, 20).until(
                    lambda d: d.find_element(By.TAG_NAME, "body").text.strip() != ""
                )

                html = driver.page_source
                cleaned_text = self._clean_html_content(html)

                if cleaned_text:
                    logger.info(f"Webpage extraction successful on attempt {attempt+1}")
                    return cleaned_text

            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                logger.warning(
                    f"Webpage attempt {attempt + 1} failed (Selenium Error): {e}"
                )
            except Exception as e:
                logger.warning(
                    f"Webpage attempt {attempt + 1} failed (Unexpected): {e}"
                )
            finally:
                if driver:
                    driver.quit()

            if attempt < self.max_retries:
                time.sleep(self.retry_delays[attempt])

    def get_text(self, url: str) -> str:
        """
        Public Router.
        """
        parsed = urlparse(url)
        is_youtube = "youtube.com" in parsed.hostname or "youtu.be" in parsed.hostname

        if is_youtube:
            # Strategy A: API (Fast, low resource)
            content = self._extract_transcript_youtube_api(url)

            # Strategy B: Fallback to Selenium/Tactiq
            if not content:
                logger.info(
                    "API extraction yielded no result. Switching to Tactiq fallback..."
                )
                content = self._extract_transcript_youtube_tactiq(url)

            return content
        else:
            return self._extract_webpage_content(url)
