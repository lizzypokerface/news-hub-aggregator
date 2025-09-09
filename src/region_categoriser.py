import logging
import pandas as pd
from typing import List
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Module-level Constants (as requested) ---

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

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are an expert news editor with deep geopolitical knowledge. Your task is to categorize a news article based ONLY on its title and source.

        You MUST choose exactly one category from the following list:
        {', '.join(CATEGORIES)}

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

        Analyze the geographic entities (countries, cities, regions) mentioned in the title. The source can also be a strong clue.

        Your response MUST BE ONLY the category name and nothing else. Do not add explanations or any extra text.
        """,
        ),
        ("user", 'Title: "{title}"\nSource: "{source}"\n\nCategory:'),
    ]
)


class RegionCategorizer:
    """
    Categorizes articles into geographic regions using an Ollama LLM.
    """

    def __init__(self, input_df: pd.DataFrame, model: str = "llama3.1"):
        """
        Initializes the categorizer and sets up the LangChain connection.

        Args:
            input_df (pd.DataFrame): DataFrame with 'title' and 'source' columns.
            model (str): The Ollama model to use.
        """
        if not isinstance(input_df, pd.DataFrame) or input_df.empty:
            raise ValueError("A non-empty pandas DataFrame must be provided.")
        self.df = input_df.copy()

        try:
            logging.info(f"Initializing connection to Ollama with model '{model}'...")
            llm = Ollama(model=model, temperature=0.0)
            self.chain = PROMPT_TEMPLATE | llm | StrOutputParser()
            logging.info("Ollama connection successful.")
        except Exception as e:
            logging.error(
                f"Failed to initialize Ollama. Is the application running and the model '{model}' pulled?"
            )
            raise RuntimeError(f"Ollama initialization failed: {e}")

    def _get_region_for_row(self, title: str, source: str) -> str:
        """
        Invokes the LLM for a single row and handles errors.

        Returns:
            The category string or 'Unknown' if any error occurs.
        """
        try:
            input_data = {"title": title, "source": source}
            category = self.chain.invoke(input_data)

            cleaned_category = category.strip()
            if cleaned_category not in CATEGORIES:
                logging.warning(
                    f"LLM returned an invalid category: '{cleaned_category}'. Defaulting to 'Unknown'."
                )
                return "Unknown"

            logging.info(f"Categorized '{title}' as '{cleaned_category}'")
            return cleaned_category

        except Exception as e:
            logging.error(
                f"LLM invocation failed for title '{title}'. Error: {e}. Defaulting to 'Unknown'."
            )
            return "Unknown"

    def categorize_regions(self) -> pd.DataFrame:
        """
        Processes the entire DataFrame to add a 'region' column.
        """
        regions: List[str] = []

        logging.info("--- Starting Region Categorization ---")
        total_rows = len(self.df)
        for index, row in self.df.iterrows():
            logging.info(f"Processing row {index + 1}/{total_rows}...")

            title = row.get("title", "")
            source = row.get("source", "")

            region = self._get_region_for_row(title, source)
            regions.append(region)

        self.df["region"] = regions
        logging.info("--- Region Categorization Complete ---")
        return self.df
