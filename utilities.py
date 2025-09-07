import logging
from datetime import datetime, timedelta
import os

import yaml


def load_yaml_file(filename: str):
    with open(filename) as file:
        return yaml.safe_load(file)


def clear_file(filename: str) -> None:
    open(filename, "w").close()


def get_datetime_one_week_ago() -> None:
    return datetime.now() - timedelta(days=7)


def create_new_file(filename: str, content: str) -> None:
    try:
        with open(filename, "w") as file:
            file.write(content)
        logging.info(f"File {filename} created successfully in the current directory.")
    except Exception as e:
        logging.error(f"Failed to create file {filename}. Error: {e}")
        raise


def system_say(text: str) -> None:
    os.system(f"say '{text}'")
