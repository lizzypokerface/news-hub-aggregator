import logging
import re
import pandas as pd
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from constants import NEWS_LINK_MD_FORMAT
from utilities import system_say

from categorize_headlines import categorize_headline_region


def fetch_links(file_path: str) -> list[str]:
    logging.info(f"Reading links from {file_path}")
    with open(file_path, "r") as file:
        links = file.readlines()
    # Remove empty lines and strip whitespace
    links = [link.strip() for link in links if link.strip()]
    logging.info(f"Found {len(links)} links in {file_path}")
    return links


def is_valid_youtube_link(link: str) -> bool:
    return link.startswith("https://youtu.be/") or link.startswith(
        "https://www.youtube.com/"
    )


def tidy_title(title: str) -> str:
    # Remove characters that can break markdown
    tidy = re.sub(r"[\|\[\]]", " ", title)
    return tidy


def get_embedded_link(link: str) -> str:
    return re.sub(r"\[.*?\]$", "", link)

def get_source(line):
    # Match text between the square brackets after the URL
    match = re.search(r"\[([^\]]+)\]\[", line)
    if match:
        return match.group(1).strip()
    return "Unknown Source"

def get_rank(line):
    # Match the number inside the square brackets at the end of the line
    match = re.search(r"\[(\d+)\]$", line)
    if match:
        return int(match.group(1))
    return -1


def get_youtube_video_title(driver: WebDriver, url: str) -> Optional[str]:
    logging.info(f"Fetching title for {url}")
    driver.get(url)
    try:
        # Wait for the title element to be present
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@id='above-the-fold']/div[@id='title']//yt-formatted-string[@class='style-scope ytd-watch-metadata']",
                )
            )
        )
        return title_element.text
    except Exception as e:
        logging.error(f"Error fetching title for {url}: {e}")
        return None


def sort_dataframe_by_rank_and_source(df: pd.DataFrame) -> pd.DataFrame:
    sorted_df = df.sort_values(by=["rank", "source"], ascending=[True, False])
    #sorted_df.to_csv("output.csv")
    return sorted_df


def write_article_dataframe_to_markdown(
    df: pd.DataFrame,
    news_links_md_filename: str,
) -> None:

    sorted_df = sort_dataframe_by_rank_and_source(df)

    with open(news_links_md_filename, "w") as f:
        previous_source = None
        for _, row in sorted_df.iterrows():
            title = row["title"]
            source = row["source"]
            url = row["url"]

            if previous_source is None:
                f.write("\n")
                f.write(f"## {source}")
                f.write("\n")

            elif previous_source is not None and source != previous_source:
                f.write("\n")
                f.write(f"## {source}")
                f.write("\n")

            f.write(NEWS_LINK_MD_FORMAT.format(source, title, url) + "\n")

            previous_source = source


def process_markdown_links(
    processed_links_filename: str, news_links_md_filename: str
) -> pd.DataFrame:

    processed_links = fetch_links(processed_links_filename)
    youtube_links = []
    other_links = []
    article_df = []

    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    for link in processed_links:
        if is_valid_youtube_link(link):
            youtube_links.append(link)
        else:
            other_links.append(link)

    for link in youtube_links:
        # Initialize and quit the driver during each loop to prevent memory issues.
        # Refer to: https://stackoverflow.com/questions/55072731/selenium-using-too-much-ram-with-firefox
        driver = webdriver.Firefox(options=options)

        yt_link = get_embedded_link(link)
        source = get_source(link)
        rank = get_rank(link)
        title = get_youtube_video_title(driver, yt_link)
        if title:
            cleaned_title_text = tidy_title(title)
            logging.info(f"Successfully retrieved title: {cleaned_title_text}")
            article_df.append(
                {
                    "title": cleaned_title_text,
                    "rank": rank,
                    "source": source,
                    "url": yt_link,
                }
            )
            driver.quit()
        else:
            logging.error(f"Failed to retrieve title for {yt_link}")
            driver.quit()

    logging.info("Please add other link titles manually.")
    system_say("Please add other link titles manually.")

    for link in other_links:
        try:
            other_link = get_embedded_link(link)
            source = get_source(link)
            rank = get_rank(link)
            title = input(f"Enter the title for the link {other_link}: ").strip()
            if title:
                cleaned_title_text = tidy_title(title)
                logging.info(f"Successfully retrieved title: {cleaned_title_text}")
                article_df.append(
                    {
                        "title": cleaned_title_text,
                        "rank": rank,
                        "source": source,
                        "url": other_link,
                    }
                )
            else:
                logging.warning(f"No title provided for link: {link}")
        except Exception as e:
            logging.error(f"Error processing link {link}: {e}")

    df = pd.DataFrame(article_df, columns=["title", "rank", "source", "url"])
    write_article_dataframe_to_markdown(df, news_links_md_filename)

    logging.info("Finished processing all links")
