import logging
from typing import List, Dict
from modules.llm_client import LLMClient

# --- Module-level Constants ---
CATEGORIES: List[str] = [
    "Global",
    "China",
    "East Asia",
    "Singapore",
    "Southeast Asia",
    "South Asia",
    "Central Asia",
    "Russia",
    "Oceania",
    "West Asia (Middle East)",
    "Africa",
    "Europe",
    "Latin America & Caribbean",
    "North America",
    "Unknown",
]

# Map common LLM shorthands to official categories
CATEGORY_ALIASES: Dict[str, str] = {
    # --- North America ---
    "us": "North America",
    "usa": "North America",
    "united states": "North America",
    "america": "North America",
    "canada": "North America",
    "white house": "North America",  # Metonymy often returned by smaller models
    "washington": "North America",
    # --- Europe ---
    "uk": "Europe",
    "britain": "Europe",
    "eu": "Europe",
    "european union": "Europe",
    "eurozone": "Europe",
    "ukraine": "Europe",  # Major news topic, often misclassified if separate
    "brussels": "Europe",
    # --- Latin America & Caribbean ---
    "latin america": "Latin America & Caribbean",
    "latam": "Latin America & Caribbean",
    "south america": "Latin America & Caribbean",
    "central america": "Latin America & Caribbean",
    "caribbean": "Latin America & Caribbean",
    "mexico": "Latin America & Caribbean",  # Often grouped here culturally/geopolitically
    "brazil": "Latin America & Caribbean",
    "venezuela": "Latin America & Caribbean",
    # --- West Asia (Middle East) ---
    "middle east": "West Asia (Middle East)",
    "mideast": "West Asia (Middle East)",
    "west asia": "West Asia (Middle East)",
    "gulf": "West Asia (Middle East)",
    "gcc": "West Asia (Middle East)",
    "iran": "West Asia (Middle East)",
    "israel": "West Asia (Middle East)",
    "palestine": "West Asia (Middle East)",
    "gaza": "West Asia (Middle East)",
    # --- Southeast Asia ---
    # Note: Singapore is its own category, so we don't map it here.
    "asean": "Southeast Asia",
    "indochina": "Southeast Asia",
    "indonesia": "Southeast Asia",
    "malaysia": "Southeast Asia",
    "philippines": "Southeast Asia",
    "thailand": "Southeast Asia",
    "vietnam": "Southeast Asia",
    # --- East Asia ---
    "northeast asia": "East Asia",
    "japan": "East Asia",
    "korea": "East Asia",
    "south korea": "East Asia",
    "north korea": "East Asia",
    "dprk": "East Asia",
    "taiwan": "East Asia",
    # --- South Asia ---
    "india": "South Asia",
    "pakistan": "South Asia",
    "indian subcontinent": "South Asia",
    # --- Oceania ---
    "australia": "Oceania",
    "new zealand": "Oceania",
    "nz": "Oceania",
    "pacific islands": "Oceania",
    # --- China ---
    # Since 'China' is its own category, catch variations
    "prc": "China",
    "mainland china": "China",
    "beijing": "China",  # Metonymy
    # --- Russia ---
    "russian federation": "Russia",
    "moscow": "Russia",  # Metonymy
    # --- Global ---
    "world": "Global",
    "international": "Global",
    "un": "Global",
    "united nations": "Global",
}

PROMPT_TEMPLATE = """
You are an expert news editor. Categorize the following text into exactly one of these regions:
{categories_list}

Text to Analyze:
"{text}"

Instructions:
1. Analyze the geographic entities (countries, cities) and the source context.
2. Return ONLY the category name from the list above.
3. Do not add punctuation, explanations, or 'Category:'.
"""


class RegionCategoriser:
    """
    Categorizes text into geographic regions using a lightweight LLM via LLMClient.
    """

    def __init__(self, config: dict, model: str = "qwen2.5:14b"):
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.llm_client = LLMClient(config)

    def get_region(self, text: str) -> str:
        """
        Determines the geographic region for a given text string.
        """
        if not text:
            return "Unknown"

        # Format prompt
        prompt = PROMPT_TEMPLATE.format(
            categories_list=", ".join(CATEGORIES), text=text
        )

        try:
            # We use 'ollama' provider for local small models
            response = self.llm_client.query(
                prompt, provider="ollama", model=self.model
            )

            # 1. Clean response
            cleaned_category = response.strip().strip('"').strip("'")

            # 2. Check Aliases (Normalization)
            if cleaned_category.lower() in CATEGORY_ALIASES:
                normalized_cat = CATEGORY_ALIASES[cleaned_category.lower()]
                self.logger.info(f"{text[:50]}... category assigned <{normalized_cat}>")
                return normalized_cat

            # 3. Exact Match Check
            if cleaned_category in CATEGORIES:
                self.logger.info(
                    f"{text[:50]}... category assigned <{cleaned_category}>"
                )
                return cleaned_category

            # 4. Fallback: Case-insensitive check against valid categories
            for cat in CATEGORIES:
                if cat.lower() == cleaned_category.lower():
                    self.logger.info(f"{text[:50]}... category assigned <{cat}>")
                    return cat

            self.logger.warning(
                f"Invalid category returned: '{cleaned_category}'. Defaulting to 'Unknown'."
            )
            return "Unknown"

        except Exception as e:
            self.logger.error(
                f"Categorization failed for text: '{text[:30]}...'. Error: {e}"
            )
            return "Unknown"
