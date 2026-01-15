import pandas as pd
import logging
from typing import List
from interfaces import BaseConsolidator
from legacy_modules.csv_handler import CSVHandler
from interfaces.models import AnalysisHeadlines, SourceHeadlines

logger = logging.getLogger(__name__)


class AnalysisHeadlineConsolidator(BaseConsolidator):
    """
    Consolidates analysis headlines from a local CSV file.
    Returns a single AnalysisHeadlines object containing all sources.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def consolidate(self) -> AnalysisHeadlines:
        """
        Reads the CSV, sorts by rank, and structures the output.
        """
        try:
            logger.info(f"Starting consolidation for file: {self.file_path}")

            # 1. Read Data
            df = CSVHandler.load_as_dataframe(self.file_path)
            logger.debug(f"Loaded dataframe with shape: {df.shape}")

            if df.empty:
                logger.warning(f"No data found in {self.file_path}")
                return AnalysisHeadlines(source_groups=[])

            # Validation
            required_cols = {"rank", "source", "title"}
            if not required_cols.issubset(df.columns):
                logger.error(
                    f"CSV missing columns. Required: {required_cols}, Found: {set(df.columns)}"
                )
                return AnalysisHeadlines(source_groups=[])

            # 2. Pre-processing
            df["rank"] = pd.to_numeric(df["rank"], errors="coerce").fillna(999)
            logger.debug("Converted 'rank' column to numeric and filled NaNs with 999.")

            # Sort: Rank 1 first, then alphabetical by source
            df = df.sort_values(by=["rank", "source"], ascending=[True, True])
            logger.info("Sorted dataframe by 'rank' and 'source'.")

            source_groups: List[SourceHeadlines] = []

            # 3. Grouping Logic (Flat by Source)
            # Use dictionary to group titles while preserving sort order
            source_map = {}

            for _, row in df.iterrows():
                source = row["source"]
                title = row["title"]

                if source not in source_map:
                    source_map[source] = []
                    logger.debug(f"Creating new group for source: {source}")

                source_map[source].append(title)
                logger.debug(f"Added title to source '{source}': {title}")

            # Convert to Data Class objects
            for source_name, titles in source_map.items():
                logger.info(f"Source '{source_name}' has {len(titles)} titles.")
                group = SourceHeadlines(source_name=source_name, titles=titles)
                source_groups.append(group)

            logger.info(f"Consolidation complete. Total sources: {len(source_groups)}")
            # Return the single object container
            return AnalysisHeadlines(source_groups=source_groups)

        except Exception as e:
            logger.exception(f"Error consolidating headlines: {e}")
            return AnalysisHeadlines(source_groups=[])
