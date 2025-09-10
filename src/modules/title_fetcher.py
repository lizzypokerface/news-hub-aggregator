import logging
from typing import Optional, List, Dict, Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TitleFetcher:
    """
    Fetches titles for a given DataFrame of URLs in a two-phase process.

    First, it attempts to fetch all titles automatically. URLs that fail are
    queued. After the automatic phase, it processes the queue, prompting the
    user for manual input for each failed URL.
    """

    def __init__(self, input_df: pd.DataFrame):
        """
        Initializes the TitleFetcher.

        Args:
            input_df (pd.DataFrame): DataFrame containing at least 'url' and 'format' columns.
        """
        if not isinstance(input_df, pd.DataFrame) or input_df.empty:
            raise ValueError("A non-empty pandas DataFrame must be provided.")
        self.df = input_df.copy()
        self.driver: Optional[webdriver.Firefox] = None  # Lazy initialization

    def _init_driver(self) -> None:
        """Initializes the Selenium WebDriver if it hasn't been already."""
        if self.driver is None:
            logging.info("Initializing Selenium WebDriver for Firefox...")
            try:
                self.driver = webdriver.Firefox()
                logging.info("WebDriver initialized successfully.")
            except WebDriverException as e:
                logging.error(
                    f"Failed to initialize WebDriver. Please ensure Firefox is installed. Error: {e}"
                )
                raise

    def _get_youtube_title(self, url: str) -> Optional[str]:
        """Fetches a YouTube video title using Selenium."""
        self._init_driver()  # Ensure driver is running
        logging.info(f"Fetching YouTube title for: {url}")
        try:
            self.driver.get(url)
            title_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//yt-formatted-string[@class='style-scope ytd-watch-metadata']",
                    )
                )
            )
            title = title_element.text.strip()
            logging.info(f"Successfully fetched title: '{title}'")
            return title
        except (TimeoutException, Exception) as e:
            logging.warning(
                f"Could not fetch YouTube title for {url}. Error: {e.__class__.__name__}"
            )
            return None

    def _get_webpage_title(self, url: str) -> Optional[str]:
        """Fetches a webpage title using requests and BeautifulSoup."""
        logging.info(f"Fetching webpage title for: {url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else None

            if title:
                cleaned_title = title.strip()
                logging.info(f"Successfully fetched title: '{cleaned_title}'")
                return cleaned_title
            else:
                logging.warning(f"No <title> tag found for {url}.")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Could not fetch title for {url}. Request error: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred for {url}: {e}")
            return None

    def _get_title_manually(self, url: str) -> str:
        """Opens a URL and prompts the user to enter the title manually."""
        self._init_driver()  # Ensure driver is running
        self.driver.get(url)

        print("\n" + "=" * 80)
        print("ACTION REQUIRED: Please provide the title for the article.")
        print(f"URL (opened in browser): {url}")

        while True:
            title = input("Enter the title here and press Enter: ").strip()
            if title:
                return title
            else:
                print("Title cannot be empty. Please try again.")

    def fetch_all_titles(self) -> pd.DataFrame:
        """
        Iterates through the DataFrame, fetches titles, and returns the
        DataFrame with an added 'title' column.
        """
        titles: List[Optional[str]] = []
        manual_queue: List[Dict[str, Any]] = []

        try:
            # --- Phase 1: Automatic Fetching ---
            logging.info("--- Starting Automatic Title Fetching Phase ---")
            for index, row in self.df.iterrows():
                url = row["url"]
                source_format = row.get("format", "webpage")
                title = None

                print(f"\nProcessing URL {index + 1}/{len(self.df)}: {url}")

                if source_format == "youtube":
                    title = self._get_youtube_title(url)
                elif source_format == "webpage":
                    title = self._get_webpage_title(url)
                else:
                    logging.warning(
                        f"Unknown format '{source_format}'. Queuing for manual input."
                    )

                titles.append(title)
                if not title:
                    # Add to the manual queue if fetching failed
                    manual_queue.append({"index": index, "url": url})

            logging.info("--- Automatic Fetching Phase Complete ---")

            # --- Phase 2: Manual Input ---
            if manual_queue:
                logging.info(
                    f"\n--- Starting Manual Input Phase for {len(manual_queue)} items ---"
                )
                for i, item in enumerate(manual_queue):
                    print(f"\nProcessing manual item {i + 1}/{len(manual_queue)}...")
                    manual_title = self._get_title_manually(item["url"])
                    # Place the manually entered title in the correct position in the list
                    titles[item["index"]] = manual_title
                logging.info("--- Manual Input Phase Complete ---")
            else:
                logging.info(
                    "All titles were fetched automatically. No manual input needed."
                )

            self.df["title"] = titles
            return self.df

        finally:
            # Ensure the driver is closed if it was initialized
            if self.driver:
                self.driver.quit()
                logging.info("WebDriver has been closed.")
