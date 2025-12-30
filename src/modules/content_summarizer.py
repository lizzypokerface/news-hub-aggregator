import logging
import time
from modules.content_extractor import ContentExtractor
from modules.llm_client import LLMClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MINIMUM_CONTENT_LENGTH = 150

SUMMARY_PROMPT_TEMPLATE = """
**Role:** You are an elite Intelligence Analyst processing raw source documents for a high-level decision-maker.

**Objective:** Create a "Triage Card" that allows the user to instantly assess the document's value, tone, and critical intel without reading the full text.

**Constraints:**
1.  **Input:** You will process ONE document at a time.
2.  **Brevity:** The final output must be readable in under 60 seconds.
3.  **Structure:** Follow the exact "Output Format" below. Do not deviate.
4.  **Implications:** Every point must include a *forward-looking* implication (what happens next?), not just a summary of the past.

**Output Format:**

**Triage Tags**
* **Type:** [Choose one: Strategic Analysis / Battlefield Report / Economic Forecast / Historical Context / Opinion / News Report]
* **Region:** [Primary region discussed]
* **Sentiment:** [Choose one: Optimistic / Cautiously Optimistic / Neutral / Critical / Alarmist]
* **Key Entities:** [List top 3-4 specific people, organizations, or places mentioned]

**5-Point Intel Brief**
* **[HEADLINE 1 in Bold]:** [The core fact or claim].
    * *Implication:* [One sentence prediction: What happens next because of this? What is the consequence?]

(Repeat for max 5 points. If the document is short or low-signal, use fewer than 5 points. Never invent points.)

**Document Content:**
{content}
"""


class ContentSummarizer:
    """
    Summarizes content using an LLM via the unified LLMClient.
    Delegates text extraction to ContentExtractor with robust retry logic.
    """

    def __init__(self, config: dict, model: str = "Gemini-2.5-Flash"):
        """
        Args:
            config (dict): Global configuration containing api_keys.
            model (str): The default model to use for summarization.
        """
        self.config = config
        self.model = model

        # Initialize Extraction Delegate
        self.extractor = ContentExtractor(headless=True)

        # Initialize Unified LLM Client
        self.llm_client = LLMClient(config)

    def _clean_llm_output(self, llm_response_text: str) -> str:
        """Removes meta-commentary and 'thinking' lines from the LLM output."""
        if not llm_response_text:
            return ""

        lines = llm_response_text.splitlines()
        # Filter out blockquotes often used for "Chain of Thought"
        cleaned_lines = [line for line in lines if not line.strip().startswith(">")]
        return "\n".join(cleaned_lines).strip()

    def _summarize_text(self, content: str) -> str:
        """Sends content to the LLMClient for summarization."""
        if not content or len(content) < MINIMUM_CONTENT_LENGTH:
            return "Error: Not enough content to generate a meaningful summary."

        logger.info(f"Sending {len(content)} characters to LLM for summarization...")
        prompt = SUMMARY_PROMPT_TEMPLATE.format(content=content)

        try:
            start_time = time.monotonic()

            # Delegate to LLMClient
            raw_summary = self.llm_client.query(
                prompt=prompt,
                provider="poe",  # Defaulting to Poe
                model=self.model,
            )

            cleaned_summary = self._clean_llm_output(raw_summary)

            duration = time.monotonic() - start_time
            logger.info(f"Summarization successful. Time: {duration:.2f}s.")
            return cleaned_summary
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return f"Error: Failed to generate summary: {e}"

    def summarize(self, source_name: str, url: str) -> str:
        """
        Public method to orchestrate content fetching and summarization.
        """
        logger.info(f"--- Processing: '{source_name}': {url} ---")

        try:
            # 1. Fetch Content (Extractor handles retries internally)
            content = self.extractor.get_text(url)

            # 2. Validate
            if (
                not content
                or len(content) < MINIMUM_CONTENT_LENGTH
                or content.startswith("[Error")
            ):
                error_msg = f"Failed to extract usable content from {url}."
                logger.error(error_msg)
                return f"Error: {error_msg}"

            # 3. Summarize
            return self._summarize_text(content)

        except Exception as e:
            logger.error(f"Critical error in summarize workflow for {url}: {e}")
            return f"Error: {e}"
