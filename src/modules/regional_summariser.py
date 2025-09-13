# regional_summarizer.py

import logging
import time
import openai  # Use the openai library for Poe API calls

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- LLM Prompt Template (as a standard f-string) ---
REGIONAL_PROMPT_STRING = """
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
    - 'West Asia (Middle East)': For countries like Lebanon, Iran, Saudi Arabia, Palestine, etc.
    - 'Africa': For countries on the African continent.
    - 'Europe': For European countries, including the UK and the European Union as an entity.
    - 'Latin America & Caribbean': For countries in Central and South America, and the Caribbean.
    - 'North America': For the United States and Canada.
    - 'Oceania': For Australia, New Zealand, Pacific Islands.
    - 'Unknown': Use ONLY if you cannot determine the region with confidence.

**Region Order:** You MUST follow this strict order for the regions. Include a section for every region on this list, even if information is sparse.
---
**METHODOLOGY:**
1.  **Read and Categorize:** Go through all the event summaries provided in the input text below. For each distinct event or piece of information, assign it to one of the predefined regions listed above.
2.  **Synthesize by Region:** After categorizing all information, group the points for each region.
3.  **Summarize and Format:** For each region that has events, write a single, coherent paragraph that synthesizes all the relevant information.
4.  **Omit Empty Regions:** If no events are found for a particular region, do not include its header in the final output.
5.  **Present in English.**
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


class RegionalSummariser:
    """
    Summarizes a text block of event summaries by geographic region using the Poe API.
    """

    def __init__(self, poe_api_key: str, model: str = "Gemini-2.5-Pro"):
        """
        Initializes the regional summarizer with a Poe API client.

        Args:
            poe_api_key (str): Your key for the Poe API.
            model (str): The Poe model to use (e.g., "Gemini-1.5-Pro", "Claude-3-Opus").
        """
        self.model = model
        try:
            # Initialize the OpenAI client pointed at the Poe API endpoint
            self.client = openai.OpenAI(
                api_key=poe_api_key,
                base_url="https://api.poe.com/v1",
            )
            logging.info(
                f"RegionalSummariser initialized successfully for Poe API with model '{model}'."
            )
        except Exception as e:
            logging.error(
                f"Failed to initialize Poe API client. Check API key or library installation. Error: {e}"
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

        logging.info(
            "Starting regional synthesis of the event summaries via Poe API..."
        )

        # Format the prompt with the input content
        final_prompt = REGIONAL_PROMPT_STRING.format(input_text=markdown_content)

        try:
            start_time = time.monotonic()

            # Make the API call using the initialized client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.0,  # For deterministic output
            )

            regional_summary = response.choices[0].message.content

            end_time = time.monotonic()
            duration = end_time - start_time

            logging.info(
                f"Regional synthesis successful. Time taken: {duration:.2f} seconds."
            )
            return regional_summary.strip()
        except Exception as e:
            logging.error(
                f"Regional synthesis failed. Error communicating with Poe API: {e}"
            )
            return (
                "Error: Regional synthesis failed due to a Poe API communication error."
            )
