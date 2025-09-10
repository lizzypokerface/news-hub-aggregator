import logging
import os
from typing import Any, Dict, List
from datetime import datetime, timedelta

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# Configure logging for clear and informative output
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LinkCollector:
    """
    Manages the semi-automated process of collecting links for analysis sources.

    This class iterates through a list of sources from a configuration file,
    filters for those marked as 'analysis', and opens their URLs in a browser.
    It then waits for the user to manually find and save relevant links to a
    text file. Finally, it processes these links into a structured pandas DataFrame.
    """

    def __init__(
        self,
        sources: List[Dict[str, Any]],
        input_directory: str,
        input_file: str = "raw_links.txt",
    ):
        if not sources:
            logging.warning(
                "The provided source list is empty. No links will be collected."
            )
        self.sources = sources
        self.input_directory = input_directory
        self.raw_links_path = os.path.join(self.input_directory, input_file)
        self.driver = self._init_driver()
        self._ensure_input_dir_exists()

    def _init_driver(self) -> webdriver.Chrome:
        logging.info("Initializing Selenium WebDriver...")
        try:
            driver = webdriver.Firefox()
            logging.info("WebDriver initialized successfully.")
            return driver
        except WebDriverException as e:
            logging.error(f"Failed to initialize WebDriver. Error: {e}")
            raise

    def _ensure_input_dir_exists(self) -> None:
        logging.info(f"Ensuring input directory exists at '{self.input_directory}'")
        os.makedirs(self.input_directory, exist_ok=True)
        if not os.path.exists(self.raw_links_path):
            logging.info(f"Creating empty raw links file at '{self.raw_links_path}'")
            # Create the file so the user can easily find and edit it.
            open(self.raw_links_path, "w").close()

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
                logging.warning(
                    f"No links found in '{self.raw_links_path}' for source: {source_metadata['name']}."
                )
                return []

            for url in urls:
                record = {
                    "source": source_metadata["name"],
                    "url": url,
                    "type": source_metadata["type"],
                    "format": source_metadata["format"],
                    "rank": source_metadata["rank"],
                }
                processed_records.append(record)
            logging.info(
                f"Collected {len(processed_records)} links for source: {source_metadata['name']}."
            )

            # IMPORTANT: Clear the file's content after processing to prepare for the next source.
            with open(self.raw_links_path, "w") as f:
                f.write("")
            logging.info(f"Cleared '{self.raw_links_path}' for the next source.")

        except FileNotFoundError:
            logging.error(
                f"Raw links file not found at '{self.raw_links_path}'. This should not happen."
            )
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while processing the raw links file: {e}"
            )

        return processed_records

    def collect_analysis_links(self) -> pd.DataFrame:
        one_week_ago = datetime.now() - timedelta(days=7)
        all_collected_records = []
        analysis_sources = [s for s in self.sources if s.get("type") == "analysis"]

        if not analysis_sources:
            logging.warning(
                "No sources of type 'analysis' were found in the configuration."
            )
            if self.driver:
                self.driver.quit()
            return pd.DataFrame()

        logging.info(
            f"Found {len(analysis_sources)} sources of type 'analysis' to process."
        )

        for source in analysis_sources:
            # Print clear instructions to the console for the user.
            print("\n" + "=" * 80)
            print(f"ACTION REQUIRED: Processing source '{source['name']}'")
            print(f"Opening URL: {source['url']}")
            print("\n1. A browser window will open with the source's page.")
            print(
                "2. Find the articles/videos you want to include and copy their links."
            )
            print("3. Paste the links into the following file (one link per line):")
            print(f"   ==> {os.path.abspath(self.raw_links_path)}")
            print(f"Date One Week Ago: {one_week_ago.strftime('%d/%m/%y')}")
            print("=" * 80)

            self.driver.get(source["url"])

            # Wait for the user to confirm they have saved the links.
            while True:
                user_input = (
                    input("Have you saved the links and are ready to continue? [y/n]: ")
                    .lower()
                    .strip()
                )
                if user_input == "y":
                    break
                elif user_input == "n":
                    input(
                        "Okay, I will wait. Press Enter when you are ready to proceed..."
                    )
                    break
                else:
                    print("Invalid input. Please enter 'y' to continue or 'n' to wait.")

            records = self._process_raw_links_file(source)
            all_collected_records.extend(records)

        logging.info("Finished collecting links from all analysis sources.")
        self.driver.quit()
        logging.info("WebDriver has been closed.")

        if not all_collected_records:
            logging.warning(
                "Process finished, but no records were collected in total. Returning an empty DataFrame."
            )
            return pd.DataFrame()

        # Convert the list of dictionaries to a DataFrame.
        df = pd.DataFrame(all_collected_records)

        # Ensure the DataFrame columns are in the desired order.
        df = df[["source", "url", "type", "format", "rank"]]
        return df
