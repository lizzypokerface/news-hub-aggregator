import logging
import os
from typing import Any, Dict, List
from datetime import datetime, timedelta

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from modules.csv_handler import CSVHandler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LinkCollector:
    def __init__(
        self,
        sources: List[Dict[str, Any]],
        input_directory: str,
        persistence_path: str,  # The file to save/check progress
        input_file: str = "raw_links.txt",
    ):
        if not sources:
            logging.warning("The provided source list is empty.")

        self.sources = sources
        self.input_directory = input_directory
        self.raw_links_path = os.path.join(self.input_directory, input_file)
        self.persistence_path = persistence_path

        # We don't init driver immediately, only when needed
        self.driver = None
        self._ensure_input_dir_exists()

    def _init_driver(self) -> webdriver.Firefox:
        if self.driver:
            return self.driver

        logging.info("Initializing Selenium WebDriver...")
        try:
            driver = webdriver.Firefox()
            logging.info("WebDriver initialized successfully.")
            return driver
        except WebDriverException as e:
            logging.error(f"Failed to initialize WebDriver. Error: {e}")
            raise

    def _ensure_input_dir_exists(self) -> None:
        os.makedirs(self.input_directory, exist_ok=True)
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        if not os.path.exists(self.raw_links_path):
            open(self.raw_links_path, "w").close()

    def _get_processed_sources(self) -> List[str]:
        """Reads the persistence CSV to find which sources are already done."""
        df = CSVHandler.load_as_dataframe(self.persistence_path)
        if df.empty or "source" not in df.columns:
            return []
        return df["source"].unique().tolist()

    def _process_raw_links_file(
        self, source_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        processed_records = []
        logging.info(f"Processing links from '{self.raw_links_path}'...")

        try:
            with open(self.raw_links_path) as f:
                # Read all lines, stripping whitespace, and ignore any empty lines.
                urls = [line.strip() for line in f if line.strip()]

            if not urls:
                # Return empty list if no URLs found.
                return []

            # Capture precise system time
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for url in urls:
                record = {
                    "source": source_metadata["name"],
                    "url": url,
                    "type": source_metadata["type"],
                    "format": source_metadata["format"],
                    "rank": source_metadata["rank"],
                    "collected_at": current_timestamp,
                }
                processed_records.append(record)

            logging.info(
                f"Collected {len(processed_records)} links for source: {source_metadata['name']}."
            )

            # Clear the file's content after processing
            with open(self.raw_links_path, "w") as f:
                f.write("")
            logging.info(f"Cleared '{self.raw_links_path}' for the next source.")

        except FileNotFoundError:
            logging.error(f"Raw links file not found at '{self.raw_links_path}'.")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while processing the raw links file: {e}"
            )

        return processed_records

    def collect_analysis_links(self) -> pd.DataFrame:
        one_week_ago = datetime.now() - timedelta(days=7)
        analysis_sources = [s for s in self.sources if s.get("type") == "analysis"]

        # 1. Load Checkpoint
        processed_sources = self._get_processed_sources()
        if processed_sources:
            logger.info(
                f"Resuming... Found {len(processed_sources)} sources already processed."
            )

        if not analysis_sources:
            return pd.DataFrame()

        try:
            self.driver = self._init_driver()

            for source in analysis_sources:
                source_name = source["name"]

                # 2. Checkpoint Logic
                if source_name in processed_sources:
                    logger.info(f"Skipping '{source_name}' (found in backup).")
                    continue

                # ... (User Interaction Prints) ...
                print("\n" + "=" * 80)
                print(f"ACTION REQUIRED: Processing source '{source_name}'")
                print(f"Opening URL: {source['url']}")
                print(f"One week ago was: {one_week_ago.strftime('%d %B %Y').lower()}")

                self.driver.get(source["url"])

                # Wait for user
                while True:
                    user_input = input("Links saved? [y/n]: ").lower().strip()
                    if user_input == "y":
                        break
                    elif user_input == "n":
                        input("Waiting...")
                        break

                # 3. Process & PERSIST IMMEDIATELY
                records = self._process_raw_links_file(source)
                if records:
                    CSVHandler.append_records(records, self.persistence_path)
                    # Add to local list so we don't process it again in this specific run loop
                    processed_sources.append(source_name)

        finally:
            if self.driver:
                self.driver.quit()

        # 4. Return the full dataset from disk
        return CSVHandler.load_as_dataframe(self.persistence_path)
