# Legacy module: retained for compatibility and slated for migration or deprecation.

import logging
import os
import re
import pandas as pd
from datetime import datetime
from legacy_modules.content_summarizer import ContentSummarizer

logger = logging.getLogger(__name__)


class NewsSummariser:
    """
    Orchestrates batch summarization of news articles from a CSV file.
    Supports grouping by 'Region' or 'Source'.
    """

    def __init__(self, config: dict):
        self.config = config
        self.output_dir = self.config.get("output_directory", "../outputs/")

        if not self.config.get("api_keys", {}).get("poe_api"):
            raise ValueError("Poe API key not found in config.")

        self.summarizer = ContentSummarizer(config=self.config)

    def _sanitize_filename(self, name: str) -> str:
        name = re.sub(r"[^\w\s-]", "", str(name))
        name = re.sub(r"[-\s]+", "_", name)
        return name

    def _save_file(self, content: str, name: str, directory: str, date_str: str):
        """Helper to write the markdown file to disk."""
        sanitized_name = self._sanitize_filename(name)
        filename = f"{sanitized_name}-{date_str}.md"
        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Saved summary to: {filepath}")
        except OSError as e:
            logger.error(f"Failed to write file {filepath}: {e}")

    def _summarize_by_region(
        self, df: pd.DataFrame, output_dir: str, date_str: str, filter_key: str
    ):
        """
        Handles grouping by Region.
        Format: # Region Name -> ## Title | Source | Date
        """
        if "region" not in df.columns:
            logger.error("Column 'region' not found in CSV.")
            return

        grouped = df.groupby("region")

        for region_name, group in grouped:
            # Apply Filter
            if (
                filter_key
                and str(region_name).lower() != filter_key.lower()
                and filter_key.lower() != "all"
            ):
                continue

            logger.info(f"Processing Region: {region_name} ({len(group)} articles)")

            markdown_content = f"# {region_name}\n\n"

            for _, row in group.iterrows():
                title = row.get("title", "No Title")
                url = row.get("url", "#")
                collected_at = row.get("collected_at", "Unknown Date")
                source_name = row.get("source", "Unknown Source")

                logger.info(f"Summarizing: {title}")
                summary = self.summarizer.summarize(str(region_name), url)

                # Context is Source
                markdown_content += f"## {title}\n"
                markdown_content += f"collected at: {collected_at}\n\n"
                markdown_content += f"source name: {source_name}\n\n"
                markdown_content += f"source: {url}\n\n"
                markdown_content += f"{summary}\n\n"
                markdown_content += "---\n\n"

            self._save_file(markdown_content, region_name, output_dir, date_str)

    def _summarize_by_source(
        self, df: pd.DataFrame, output_dir: str, date_str: str, filter_key: str
    ):
        """
        Handles grouping by Source.
        Format: # Source Name -> ## Title | Region | Date
        """
        if "source" not in df.columns:
            logger.error("Column 'source' not found in CSV.")
            return

        grouped = df.groupby("source")

        for source_name, group in grouped:
            # Apply Filter
            if (
                filter_key
                and str(source_name).lower() != filter_key.lower()
                and filter_key.lower() != "all"
            ):
                continue

            logger.info(f"Processing Source: {source_name} ({len(group)} articles)")

            markdown_content = f"# {source_name}\n\n"

            for _, row in group.iterrows():
                title = row.get("title", "No Title")
                url = row.get("url", "#")
                collected_at = row.get("collected_at", "Unknown Date")
                source_name = row.get("source", "Unknown Source")

                logger.info(f"Summarizing: {title}")
                summary = self.summarizer.summarize(str(source_name), url)

                # Context is Region
                markdown_content += f"## {title}\n"
                markdown_content += f"collected at: {collected_at}\n\n"
                markdown_content += f"source name: {source_name}\n\n"
                markdown_content += f"source: {url}\n\n"
                markdown_content += f"{summary}\n\n"
                markdown_content += "---\n\n"

            self._save_file(markdown_content, source_name, output_dir, date_str)

    def batch_summarize(self, csv_path: str, mode: str, filter_key: str = None):
        """
        Main entry point for batch processing.
        """
        logger.info(f"Starting Batch Summarization. Mode: {mode}, Filter: {filter_key}")

        # 1. Validation & Setup
        if not os.path.exists(csv_path):
            logger.error(f"Input CSV not found: {csv_path}")
            return

        df = pd.read_csv(csv_path)
        if df.empty:
            logger.warning("Input CSV is empty.")
            return

        # Prepare Output Directory
        date_str = datetime.now().strftime("%Y-%m-%d")
        summaries_dir = os.path.join(self.output_dir, "summaries", date_str)
        os.makedirs(summaries_dir, exist_ok=True)

        # 2. Dispatch to specific logic
        if mode == "region":
            self._summarize_by_region(df, summaries_dir, date_str, filter_key)
        elif mode == "source":
            self._summarize_by_source(df, summaries_dir, date_str, filter_key)
        else:
            logger.error(f"Invalid mode selected: {mode}")

        logger.info("Batch Summarization Complete.")
