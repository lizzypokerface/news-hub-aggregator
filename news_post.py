import logging
from datetime import datetime

from constants import (
    NEWS_POST_FILENAME_FORMAT,
    NEWS_POST_TEMPLATE,
    NEWS_POST_COMMIT_MSG,
)
from utilities import create_new_file


def create_weekly_news_post_template(current_date: datetime):
    date_str = current_date.strftime("%Y-%m-%d")
    date_display = current_date.strftime("%d %B %Y")
    filename = NEWS_POST_FILENAME_FORMAT.format(date_str)
    template = NEWS_POST_TEMPLATE.format(date_display, date_str)
    logging.info(
        f"Creating weekly news post template. Filename: {filename}, Display Date: {date_display}"
    )
    create_new_file(filename, template)
    logging.info(f"Git commit with message: {NEWS_POST_COMMIT_MSG.format(date_display)}")
