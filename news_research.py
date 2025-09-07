import logging

from selenium import webdriver

from constants import (
    PROCESSED_LINKS_FILENAME,
    PROCESSED_LINK_FORMAT,
    RAW_LINKS_FILENAME,
    SOURCE_TITLE_KEY,
    SOURCE_URL_KEY,
    SOURCE_INFO_KEY,
    SOURCE_RANK_KEY,
    USER_INPUT_NO,
    USER_INPUT_YES,
    VERIFIED_SOURCES_KEY,
)

from utilities import clear_file, get_datetime_one_week_ago, load_yaml_file, system_say


def process_links(
    raw_links_file: str, processed_links_file: str, source_title: str, source_rank: int
) -> None:
    # Read links from raw_links.txt and write to processed_links.txt
    with open(raw_links_file, "r") as raw_file, open(
        processed_links_file, "a"
    ) as processed_file:
        for line in raw_file:
            url = line.strip()
            processed_file.write(PROCESSED_LINK_FORMAT.format(url, source_title, source_rank))


def perform_news_research(new_sources_filename: str):
    driver = webdriver.Firefox()
    news_sources = load_yaml_file(new_sources_filename)

    for source in news_sources[VERIFIED_SOURCES_KEY]:
        logging.info(
            f"Title: {source[SOURCE_TITLE_KEY]} \nURL: {source[SOURCE_URL_KEY]} \nRANK: {source[SOURCE_RANK_KEY]}"
        )
        logging.info(f"Info: {source[SOURCE_INFO_KEY]}")
        # Log the date from one week ago to inform the user when to start retrieving articles.
        logging.info(
            f"Date one week ago: {get_datetime_one_week_ago().strftime('%d %b %y')}"
        )

        driver.get(source["url"])
        system_say(f"{source[SOURCE_TITLE_KEY]}")

        logging.info("Please add links to raw_links.txt manually.")
        user_input = input("Save and continue? [y/n] ")

        if user_input.lower() == USER_INPUT_YES:
            process_links(
                RAW_LINKS_FILENAME,
                PROCESSED_LINKS_FILENAME,
                source[SOURCE_TITLE_KEY],
                source[SOURCE_RANK_KEY],
            )
            clear_file(RAW_LINKS_FILENAME)
        elif user_input.lower() == USER_INPUT_NO:
            logging.info("Exited without saving.")
            break
        else:
            logging.info(
                f"Invalid input: '{user_input}'. Please enter {USER_INPUT_YES} or {USER_INPUT_NO}."
            )
            continue
    driver.quit()
