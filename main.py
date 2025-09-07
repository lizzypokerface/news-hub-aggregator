import logging
from datetime import datetime

from utilities import clear_file, system_say
from news_research import perform_news_research
from news_links_markdown import process_markdown_links
from news_post import create_weekly_news_post_template
from constants import (
    NEWS_SOURCES_FILENAME,
    RAW_LINKS_FILENAME,
    PROCESSED_LINKS_FILENAME,
    NEWS_LINKS_MD_FILENAME,
)


logging.basicConfig(level=logging.INFO)


def clear_caches():
    logging.info("Clearing caches.")
    system_say("Clearing caches.")
    clear_file(RAW_LINKS_FILENAME)
    clear_file(PROCESSED_LINKS_FILENAME)
    clear_file(NEWS_LINKS_MD_FILENAME)
    logging.info("Caches cleared.")
    system_say("Caches cleared.")


def step_1_perform_news_research():
    logging.info("Starting news research.")
    system_say("Starting news research.")
    perform_news_research(NEWS_SOURCES_FILENAME)
    logging.info("News research completed.")
    system_say("News research completed.")


def step_2_process_markdown_links():
    logging.info("Processing markdown links.")
    system_say("Processing markdown links.")
    process_markdown_links(PROCESSED_LINKS_FILENAME, NEWS_LINKS_MD_FILENAME)
    logging.info("Markdown link processing completed.")
    system_say("Markdown link processing completed.")


def step_3_create_weekly_post_template():
    logging.info("Creating weekly news post template.")
    system_say("Creating weekly news post template.")
    create_weekly_news_post_template(current_date=datetime.now())
    logging.info("Weekly news post template created.")
    system_say("Weekly news post template created.")
    system_say("Please transfer articles in news_links.md to weekly news post")


def run():
    clear_caches()
    step_1_perform_news_research()
    step_2_process_markdown_links()
    step_3_create_weekly_post_template()


if __name__ == "__main__":
    run()
