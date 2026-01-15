import logging
from typing import Any
from interfaces import BaseGenerator
from interfaces.models import Article

logger = logging.getLogger(__name__)

# Constants
MINIMUM_CONTENT_LENGTH = 150
MODEL_NAME = "Gemini-3-Flash"  # Fast, efficient model for summarization

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


class IntelBriefGenerator(BaseGenerator):
    """
    Phase 3: Transformation.
    Takes a RawArticle and generates a structured 'Triage Card' summary.
    """

    def __init__(self, llm_client: Any):
        """
        Args:
            llm_client: An initialized LLMClient instance.
        """
        self.llm_client = llm_client

    def generate(self, article: Article) -> Article:
        """
        Takes an Article, generates the summary, and returns the enriched Article.
        """
        logger.info(f"Generating Intel Brief for: '{article.title}'...")

        if not article.raw_content or len(article.raw_content) < MINIMUM_CONTENT_LENGTH:
            return self._mark_as_failed(article, "Content too short.")

        try:
            prompt = SUMMARY_PROMPT_TEMPLATE.format(content=article.raw_content)

            raw_summary = self.llm_client.query(
                prompt=prompt, provider="poe", model=MODEL_NAME
            )

            article.summary = self._clean_llm_output(raw_summary)
            return article

        except Exception as e:
            logger.error(f"Generation error for {article.title}: {e}")
            return self._mark_as_failed(article, f"Generation Error: {e}")

    def _clean_llm_output(self, text: str) -> str:
        if not text:
            return ""
        lines = text.splitlines()
        cleaned_lines = [line for line in lines if not line.strip().startswith(">")]
        return "\n".join(cleaned_lines).strip()

    def _mark_as_failed(self, article: Article, error_msg: str) -> Article:
        article.summary = f"**GENERATION FAILED**\n{error_msg}"
        return article
