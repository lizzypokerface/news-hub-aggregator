# content_summarizer.py

import logging
import time
import re
from urllib.parse import urlparse, parse_qs

import openai
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

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---
MINIMUM_CONTENT_LENGTH = (
    150  # Minimum characters for any content to be considered valid for summarization
)
SUMMARY_PROMPT_TEMPLATE = """
**Role:** You are an intelligence analyst and news reporter.

**Task:** Your task is to create a detailed, journalistic summary of the provided document. The summary should be written as a news report or an intelligence briefing, designed to inform a reader about the current situation, key claims, and important figures involved.

**Audience:** The summary is for a well-informed reader who needs a quick but thorough understanding of the key events, claims, and dynamics discussed in the text.

**Key Requirements for Your Summary:**

1.  **Journalistic Style:** Begin the summary with a dateline (e.g., "**City, Country --**") and write in a clear, objective, and professional news style.
2.  **Strict Attribution:** Attribute all claims, opinions, and predictions directly to the speaker(s) mentioned in the text. Use phrases like "According to [Speaker's Name]," "[Speaker] stated that," or "[Speaker] claims." Never present an opinion from the text as an established fact.
3.  **Extract Key Facts:** Identify and include all critical factual information:
    -   **People:** Full names and their titles/roles (e.g., "Seyed Mohammad Marandi, a professor at Tehran University").
    -   **Organizations:** Names of government bodies, agencies, or groups (e.g., "IAEA," "Supreme National Security Council").
    -   **Locations:** Important cities, countries, or regions mentioned (e.g., "Gaza," "Tehran," "Beijing").
    -   **Specific Events:** Mention key events discussed, such as "US and Israeli strikes," "a military parade in Beijing," or "sanctions."
4.  **Summarize the Core Thesis:** Clearly state the central argument of the speaker. What is the main point they are trying to convey?
5.  **Include Supporting Evidence:** Mention the key pieces of evidence or examples the speaker uses to support their main points.
6.  **Capture Critical Statements:** Incorporate direct quotes or precise paraphrases of the most important statements, especially any warnings, policy shifts, or significant declarations.
7.  **Logical Structure:**
    -   Start with the most important information (the lead).
    -   Follow with supporting details, context, and evidence.
    -   Conclude with any forward-looking statements or final assessments made by the speaker.
8.  **Word Count:** Aim for a detailed summary of approximately 250-350 words. Omit timestamps.

---

### **Examples to Guide You:**

Let's use the provided transcript about Professor Marandi as our source text.

**Bad Example (What to AVOID):**

> "Professor Marandi talked about the situation in the Middle East. He said Iran wasn't really hurt by the attacks and that they are being ambiguous about their nuclear program now. He thinks Iran is stronger and has better friends, so they are more prepared for a war."
> -   **Why it's bad:** This summary is too generic. It lacks names, titles, specific evidence, attribution, and the professional tone of a news report.

**Good Example (What to AIM FOR):**

> "Tehran, Iran -- According to Seyed Mohammad Marandi, a professor at Tehran University, recent US and Israeli strikes failed to damage Iran's nuclear program, prompting Tehran to adopt a policy of 'strategic ambiguity.' Marandi claims key facilities are deep underground and that Iran retains a strong industrial base for producing advanced centrifuges. A major consequence, he stated, is Iran's decision to cease most cooperation with the IAEA. He highlighted a warning from Dr. Jani, head of Iran's Supreme National Security Council, that Iran's 'nuclear posture will change' if its existence is threatened. Marandi concluded that Iran's geopolitical position is strengthening through deeper ties with China and Russia, making it more prepared for any future conflict."
> -   **Why it's good:** It uses a dateline, attributes every claim, includes names and titles (Marandi, Dr. Jani), mentions key organizations (IAEA), quotes a critical warning, and follows a logical news structure.

---

**Now, using the rules and examples above, process the following document:**

`{content}`
"""

# ---  HELPER FUNCTIONS  ---


def _get_firefox_driver():
    """Initializes and returns a headless Firefox WebDriver."""
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    )
    try:
        driver = webdriver.Firefox(options=options)
        return driver
    except WebDriverException as e:
        logger.error(
            f"Failed to initialize Firefox WebDriver. Ensure geckodriver is in your PATH. Error: {e}"
        )
        raise


def _clean_html_content(html_content: str) -> str:
    """Cleans HTML content by extracting visible text and removing extra whitespace."""
    soup = BeautifulSoup(html_content, "html.parser")
    for script_or_style in soup(
        ["script", "style", "noscript", "header", "footer", "nav", "aside"]
    ):
        script_or_style.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\n", " ")
    text = text.replace("\r", "")
    return text.strip()


def extract_transcript_youtube_api(youtube_url: str) -> str:
    """Extracts the transcript of a YouTube video using the youtube-transcript-api library."""
    logger.info(
        f"Attempting to extract YouTube transcript via youtube-transcript-api for: {youtube_url}"
    )
    try:
        parsed_url = urlparse(youtube_url)
        video_id = None
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            if parsed_url.path == "/watch":
                video_id_qs = parse_qs(parsed_url.query).get("v")
                if video_id_qs:
                    video_id = video_id_qs[0]
            elif parsed_url.path.startswith("/shorts/"):
                video_id = parsed_url.path.split("/")[-1]
        elif parsed_url.hostname == "youtu.be":
            video_id = parsed_url.path.split("/")[-1]

        if not video_id:
            raise ValueError(f"Could not determine video ID from URL: {youtube_url}")

        ytt_api = YouTubeTranscriptApi()
        transcript_data = ytt_api.get_transcript(video_id)
        transcript_text = " ".join([snippet["text"] for snippet in transcript_data])
        logger.info(
            f"Successfully extracted transcript for video ID: {video_id} using youtube-transcript-api."
        )
        return transcript_text
    except (NoTranscriptFound, TranscriptsDisabled):
        logger.warning(
            f"No transcript found or transcripts are disabled for video: {youtube_url}."
        )
        return ""
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while fetching YouTube transcript via youtube-transcript-api for {youtube_url}: {e}"
        )
        return ""


def extract_transcript_youtube_tactiq(youtube_url: str) -> str:
    """Extracts the transcript of a YouTube video using Tactiq.io via Selenium."""
    logger.info(
        f"Attempting to extract YouTube transcript via Tactiq.io for: {youtube_url}"
    )
    tactiq_base_url = "https://tactiq.io/tools/youtube-transcript"
    driver = None
    try:
        driver = _get_firefox_driver()
        driver.get(tactiq_base_url)
        logger.info(f"Navigated to Tactiq.io: {tactiq_base_url}")
        url_input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "yt-2"))
        )
        url_input_field.send_keys(youtube_url)
        get_transcript_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@value='Get Video Transcript']")
            )
        )
        get_transcript_button.click()
        logger.info("Clicked 'Get Video Transcript' button.")
        WebDriverWait(driver, 20).until(EC.url_contains("run/youtube_transcript"))
        transcript_container = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "transcript"))
        )
        WebDriverWait(driver, 10).until(
            lambda d: transcript_container.text.strip() != ""
        )
        raw_transcript_text = transcript_container.text
        timestamp_pattern = r"\d{2}:\d{2}:\d{2}\.\d{3}\s*"
        cleaned_transcript_text = re.sub(timestamp_pattern, "", raw_transcript_text)
        logger.info("Timestamps removed from Tactiq.io transcript.")
        return cleaned_transcript_text.strip()
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during Tactiq.io transcript extraction for {youtube_url}: {e}"
        )
        return ""
    finally:
        if driver:
            driver.quit()


def extract_content_webpage_selenium_bs4(webpage_url: str) -> str:
    """Extracts cleaned text content from a dynamic webpage using Selenium (Firefox)."""
    logger.info(
        f"Attempting to extract content from dynamic webpage via Selenium/BeautifulSoup for: {webpage_url}"
    )
    driver = None
    try:
        driver = _get_firefox_driver()
        driver.get(webpage_url)
        WebDriverWait(driver, 20).until(
            lambda d: d.find_element(By.TAG_NAME, "body").text.strip() != ""
        )
        html_content = driver.page_source
        cleaned_text = _clean_html_content(html_content)
        logger.info(f"Cleaned HTML content for {webpage_url}.")
        return cleaned_text
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during dynamic webpage extraction for {webpage_url}: {e}"
        )
        return ""
    finally:
        if driver:
            driver.quit()


# --- MAIN CLASS ---


class ContentSummarizer:
    """
    Fetches, parses, and summarizes content from YouTube or webpages using a hybrid approach.
    """

    def __init__(self, poe_api_key: str, model: str = "Gemini-2.5-Flash"):
        self.model = model
        try:
            self.client = openai.OpenAI(
                api_key=poe_api_key, base_url="https://api.poe.com/v1"
            )
            logger.info(
                f"ContentSummarizer initialized successfully for Poe API with model '{model}'."
            )
        except Exception as e:
            logger.error(f"Failed to initialize Poe API client. Error: {e}")
            raise

    def _clean_llm_output(self, llm_response_text: str) -> str:
        """
        Removes meta-commentary and 'thinking' lines (blockquotes) from the LLM output.
        """
        if not llm_response_text:
            return ""

        lines = llm_response_text.splitlines()
        # Keep lines that do not start with the markdown blockquote character '>'
        cleaned_lines = [line for line in lines if not line.strip().startswith(">")]

        # Join the remaining lines and remove any leading/trailing whitespace
        result = "\n".join(cleaned_lines).strip()
        return result

    def _summarize_text(self, content: str) -> str:
        """Sends content to the Poe API for summarization and cleans the output."""
        if not content or len(content) < MINIMUM_CONTENT_LENGTH:
            return "Error: Not enough content to generate a meaningful summary."

        logger.info(
            f"Sending {len(content)} characters to Poe API for summarization..."
        )
        prompt = SUMMARY_PROMPT_TEMPLATE.format(content=content)
        try:
            start_time = time.monotonic()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            raw_summary = response.choices[0].message.content

            # Clean the raw output from the LLM
            cleaned_summary = self._clean_llm_output(raw_summary)

            duration = time.monotonic() - start_time
            logger.info(
                f"Poe API summarization and cleaning successful. Time taken: {duration:.2f} seconds."
            )
            return cleaned_summary
        except Exception as e:
            logger.error(f"Poe API call failed: {e}")
            return f"Error: Failed to generate summary due to an API error: {e}"

    def summarize(self, source_name: str, url: str) -> str:
        """
        Public method to orchestrate content fetching and summarization.
        """
        logger.info(f"--- Starting summarization for '{source_name}': {url} ---")
        parsed_url = urlparse(url)
        is_youtube = (
            "youtube.com" in parsed_url.hostname or "youtu.be" in parsed_url.hostname
        )

        content = ""

        if is_youtube:
            content = extract_transcript_youtube_api(url)
            if not content or len(content) < MINIMUM_CONTENT_LENGTH:
                logger.info(
                    "API method failed or returned insufficient content. Trying Tactiq fallback."
                )
                content = extract_transcript_youtube_tactiq(url)
        else:
            content = extract_content_webpage_selenium_bs4(url)

        if not content or len(content) < MINIMUM_CONTENT_LENGTH:
            error_message = (
                f"Failed to extract any usable content from {url} after all attempts."
            )
            logger.error(error_message)
            return f"Error: {error_message}"

        return self._summarize_text(content)
