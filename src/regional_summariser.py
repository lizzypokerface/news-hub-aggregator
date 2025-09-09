# regional_summarizer.py

import logging
import time

from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- LLM Prompt Template for Regional Summarization ---
REGIONAL_PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
You are a geopolitical analyst and expert summarizer. Your task is to read a collection of event summaries from different news sources and reorganize them by geographic region into a final, clean intelligence briefing.

---
**PREDEFINED REGIONS (Use these categories ONLY):**
    - 'Global': Use for articles involving multiple distinct regions (e.g., a US-China summit, a UN resolution).
    - 'China': For articles primarily about China.
    - 'East Asia': For Japan, South Korea, North Korea.
    - 'Singapore': Use ONLY for articles specifically about Singapore.
    - 'Southeast Asia': For countries like Vietnam, Thailand, Indonesia, Malaysia, Philippines.
    - 'South Asia': For India, Pakistan, Bangladesh, Sri Lanka.
    - 'Central Asia': For Kazakhstan, Uzbekistan, etc.
    - 'Russia': For articles primarily about Russia.
    - 'Oceania': For Australia, New Zealand, Pacific Islands.
    - 'West Asia (Middle East)': For countries like Lebanon, Iran, Saudi Arabia, Palestine, etc.
    - 'Africa': For countries on the African continent.
    - 'Europe': For European countries, including the UK and the European Union as an entity.
    - 'Latin America & Caribbean': For countries in Central and South America, and the Caribbean.
    - 'North America': For the United States and Canada.
    - 'Unknown': Use ONLY if you cannot determine the region with confidence.

---
**METHODOLOGY:**
1.  **Read and Categorize:** Go through all the event summaries provided in the input text below. For each distinct event or piece of information, assign it to one of the predefined regions listed above.
2.  **Synthesize by Region:** After categorizing all information, group the points for each region.
3.  **Summarize and Format:** For each region that has events, write a single, coherent paragraph that synthesizes all the relevant information.
4.  **Omit Empty Regions:** If no events are found for a particular region, do not include its header in the final output.

---
**OUTPUT FORMAT (Follow Strictly):**
- The final output must be a single block of text in Markdown format.
- Each region with events must have a Level 2 Markdown header (e.g., `## Global`).
- Following the header, provide the synthesized summary paragraph for that region.
- Separate each region's section with two newlines.
- **DO NOT** include any introductory text, concluding remarks, explanations, or any text other than the regional summaries and their headers.

---
**INPUT TEXT TO PROCESS:**
{input_text}

**REGIONAL SUMMARY:**
"""
)


class RegionalSummariser:
    """
    Summarizes a text block of event summaries by geographic region using an LLM.
    """

    def __init__(self, model: str = "llama3.1"):
        """
        Initializes the regional summarizer.

        Args:
            model (str): The Ollama model to use for synthesis.
        """
        try:
            llm = Ollama(model=model, temperature=0.0)
            self.llm_chain = REGIONAL_PROMPT_TEMPLATE | llm | StrOutputParser()
            logging.info(
                f"RegionalSummarizer initialized successfully with model '{model}'."
            )
        except Exception as e:
            logging.error(
                f"Failed to initialize Ollama for RegionalSummarizer. Is the service running? Error: {e}"
            )
            raise

    def summarise(self, markdown_content: str) -> str:
        """
        Takes a string of markdown content and returns a new summary organized by region.

        Args:
            markdown_content (str): The string content from the initial summary file.

        Returns:
            A new markdown string with content summarized by region.
        """
        if not markdown_content.strip():
            logging.warning(
                "Input content for regional summarization is empty. Returning empty string."
            )
            return ""

        logging.info("Starting regional synthesis of the event summaries...")

        try:
            start_time = time.monotonic()
            regional_summary = self.llm_chain.invoke({"input_text": markdown_content})
            end_time = time.monotonic()
            duration = end_time - start_time

            logging.info(
                f"Regional synthesis successful. Time taken: {duration:.2f} seconds."
            )
            return regional_summary.strip()
        except Exception as e:
            logging.error(
                f"Regional synthesis failed. Could not connect to Ollama: {e}"
            )
            return "Error: Regional synthesis failed due to an LLM communication error."
