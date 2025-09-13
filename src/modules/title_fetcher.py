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

    def __init__(self, input_df: pd.DataFrame, driver_reset_threshold: int = 25):
        """
        Initializes the TitleFetcher.

        Args:
            input_df (pd.DataFrame): DataFrame containing at least 'url' and 'format' columns.
            driver_reset_threshold (int): The number of times the driver can be "used"
                                          (i.e., _init_driver is called) before it's quit
                                          and a new instance is launched to clean up RAM.
        """
        if not isinstance(input_df, pd.DataFrame) or input_df.empty:
            raise ValueError("A non-empty pandas DataFrame must be provided.")
        self.df = input_df.copy()
        self.driver: Optional[
            webdriver.Firefox
        ] = None  # Stores the current WebDriver instance
        self._driver_use_count = (
            0  # Counter for how many times the current driver has been requested
        )
        self._driver_reset_threshold = (
            driver_reset_threshold  # The limit for the use count
        )
        self._current_headless_mode: Optional[
            bool
        ] = None  # To track the headless mode of the currently active driver

    def _launch_new_driver(self, headless: bool) -> None:
        """
        Quits any existing driver and launches a new Firefox WebDriver instance
        with the specified headless mode. Resets the driver use count.

        Args:
            headless (bool): If True, runs Firefox in headless mode.
        """
        logging.info("Launching a new WebDriver instance...")
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Existing WebDriver instance quit successfully.")
            except Exception as e:
                logging.warning(f"Error while quitting existing WebDriver: {e}")
            finally:
                self.driver = (
                    None  # Ensure driver is set to None regardless of quit success
                )

        try:
            firefox_options = webdriver.FirefoxOptions()
            if headless:
                firefox_options.add_argument("--headless")
                logging.info("New Firefox instance will run in headless mode.")
            else:
                logging.info("New Firefox instance will run in visible mode.")

            # Recommended options for stability, especially in headless environments
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")

            self.driver = webdriver.Firefox(options=firefox_options)
            self._driver_use_count = 0  # Reset counter for the new driver
            self._current_headless_mode = (
                headless  # Store the mode of the newly created driver
            )
            logging.info("New WebDriver initialized successfully.")
        except WebDriverException as e:
            logging.error(
                f"Failed to initialize WebDriver. Please ensure Firefox is installed and geckodriver is in your system's PATH. Error: {e}"
            )
            self.driver = None  # Ensure driver is None on failure
            self._current_headless_mode = None
            raise  # Re-raise the exception to propagate the error
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during WebDriver initialization: {e}"
            )
            self.driver = None
            self._current_headless_mode = None
            raise

    def _init_driver(self, headless: bool = False) -> webdriver.Firefox:
        """
        Ensures a Selenium WebDriver instance is available.
        It initializes a new driver if:
        1. No driver currently exists.
        2. The current driver's use count has reached the predefined threshold.
           This is done to periodically clean up RAM and prevent resource exhaustion.
        3. The requested 'headless' mode is different from the currently active driver's mode.
           We cannot change headless mode on an already running browser.

        Args:
            headless (bool): If True, configures the *new* Firefox instance to run in headless mode.
                             If False, configures it to run with a visible UI. Defaults to False.

        Returns:
            webdriver.Firefox: The active Firefox WebDriver instance.
        """
        self._driver_use_count += 1
        logging.info(
            f"Driver use count: {self._driver_use_count}/{self._driver_reset_threshold}"
        )

        # Determine if a new driver instance is needed based on:
        # 1. No driver currently exists.
        # 2. The current driver's use count has reached the predefined threshold.
        #    This is crucial for RAM management and preventing resource exhaustion.
        # 3. The requested 'headless' mode is different from the currently active driver's mode.
        #    We cannot change headless mode on an already running browser.
        needs_new_driver = (
            self.driver is None
            or self._driver_use_count >= self._driver_reset_threshold
            or (self.driver is not None and headless != self._current_headless_mode)
        )

        if needs_new_driver:
            logging.info("Conditions met for initializing a new WebDriver instance.")
            self._launch_new_driver(headless)
        else:
            logging.info("Reusing existing WebDriver instance.")

        # If driver is still None after attempting to launch (due to an error), raise an exception
        if self.driver is None:
            raise RuntimeError(
                "WebDriver could not be initialized or is not available."
            )

        return self.driver

    def close_driver(self):
        """
        Closes the Selenium WebDriver if it's active and resets all associated state.
        This should be called when you are completely done with the driver.
        """
        if self.driver:
            try:
                self.driver.quit()
                logging.info("WebDriver closed successfully.")
            except Exception as e:
                logging.warning(f"Error closing WebDriver: {e}")
            finally:
                # Always ensure the driver reference and state are cleared
                self.driver = None
                self._driver_use_count = 0
                self._current_headless_mode = None
        else:
            logging.info("No active WebDriver to close.")

    def _get_youtube_title(self, url: str) -> Optional[str]:
        """Fetches a YouTube video title using Selenium."""
        # Ensure the driver is ready and assigned to self.driver
        self.driver = self._init_driver()
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
        # Ensure the driver is ready and assigned to self.driver, typically visible for manual input
        self.driver = self._init_driver(headless=False)
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
                    # _get_youtube_title will call _init_driver internally
                    title = self._get_youtube_title(url)
                elif source_format == "webpage":
                    # _get_webpage_title uses requests, no driver needed here
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
                    # _get_title_manually will call _init_driver internally
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
            # Ensure the driver is closed and state is reset when the process is complete
            self.close_driver()
