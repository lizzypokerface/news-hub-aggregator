"""
CONFIG VALIDATOR SCRIPT
-----------------------
Purpose:
    This script reads a `config.yaml` file and validates the 'sources' section.
    It ensures that every source entry meets strict type, format, and value requirements
    to prevent the main application from crashing during execution.

    Specific Logic Checks:
    1. Schema: Ensures all required keys (name, url, type, format, rank) exist.
    2. Data Types: Validates ranks are integers (1-5) and enums match allowed values.
    3. URL Integrity: Checks for valid URL structure (scheme + domain).
    4. Business Logic: Enforces that sources with format 'youtube' must use YouTube URLs,
       and non-YouTube URLs cannot use the 'youtube' format.

How to Run:
    Open your terminal/command prompt and run:

    python scripts/validate_config.py --config ./config.yaml

Requirements:
    - Python 3.x
    - PyYAML library (pip install PyYAML)
"""

import argparse
import sys
import yaml  # Requires: pip install PyYAML
from urllib.parse import urlparse


def is_valid_url(url):
    """
    Checks if the URL has a valid structure.
    Enforces that a Scheme (http/s) and Netloc (Domain) exist.
    """
    if not url or not isinstance(url, str):
        return False
    result = urlparse(url)
    # result.scheme ensures 'https' or 'http' exists
    # result.netloc ensures 'www.youtube.com' (the domain) exists
    if result.scheme and result.netloc:
        return True
    return False


def validate_source(source):
    """
    Validates a single source dictionary against strict schema rules.
    Returns (True, None) if valid, or (False, Error Message) if invalid.
    """

    # 1. Check if source is a dictionary
    if not isinstance(source, dict):
        return False, "Item is not a valid dictionary."

    # 2. Check for missing keys
    required_keys = ["name", "url", "type", "format", "rank"]
    for key in required_keys:
        if key not in source:
            return False, f"Missing required key: '{key}'"

    # 3. Validate 'name' (Must be string)
    if not isinstance(source["name"], str) or not source["name"].strip():
        return False, "Field 'name' must be a valid string."

    # 4. Validate 'url' (Must be valid URL with domain)
    if not is_valid_url(source["url"]):
        return (
            False,
            f"Field 'url' is invalid (missing http/s or domain): {source.get('url')}",
        )

    # 5. Validate 'type' (Strict Enum)
    valid_types = ["analysis", "datapoint"]
    if source["type"] not in valid_types:
        return (
            False,
            f"Field 'type' must be 'analysis' or 'datapoint'. Found: '{source['type']}'",
        )

    # 6. Validate 'format' (Strict Enum)
    valid_formats = ["youtube", "webpage"]
    if source["format"] not in valid_formats:
        return (
            False,
            f"Field 'format' must be 'youtube' or 'webpage'. Found: '{source['format']}'",
        )

    # 7. Enforce YouTube URL Rules
    # Check if the URL is a YouTube link
    is_yt_link = "youtube.com" in source["url"] or "youtu.be" in source["url"]

    if source["format"] == "youtube" and not is_yt_link:
        return (
            False,
            f"Format is 'youtube', but URL is not a YouTube link: {source['url']}",
        )

    if is_yt_link and source["format"] != "youtube":
        return (
            False,
            f"URL is a YouTube link, but format is '{source['format']}' (must be 'youtube').",
        )

    # 8. Validate 'rank' (1-5 Integer)
    try:
        rank = int(source["rank"])
        if not (1 <= rank <= 5):
            raise ValueError
    except (ValueError, TypeError):
        return (
            False,
            f"Field 'rank' must be an integer between 1 and 5. Found: '{source['rank']}'",
        )

    return True, None


def main():
    parser = argparse.ArgumentParser(
        description="Validate config.yaml sources structure and logic."
    )
    parser.add_argument("--config", required=True, help="Path to the config.yaml file")
    args = parser.parse_args()

    # Load YAML
    try:
        with open(args.config, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {args.config}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file.\n{e}")
        sys.exit(1)

    # Basic Structure Check
    if "sources" not in data:
        print("Error: 'sources' section missing in config file.")
        sys.exit(1)

    sources = data["sources"]
    if not sources or not isinstance(sources, list):
        print("Error: 'sources' must be a list.")
        sys.exit(1)

    has_errors = False

    # Validate Sources
    print(f"Validating {len(sources)} sources from '{args.config}'...")
    print("-" * 30)

    for i, source in enumerate(sources):
        is_valid, error_msg = validate_source(source)

        if not is_valid:
            has_errors = True
            # Try to get the name for identification, fallback to index
            name = source.get("name", f"Item #{i+1}")
            print(f"Mistake on source '{name}': {error_msg}")

    print("-" * 30)
    if not has_errors:
        print("Success! Everything checks out.")
    else:
        print("Validation Failed. Please fix the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
