import logging
import os
from typing import Dict, Any

from legacy_modules.link_collector import LinkCollector
from legacy_modules.title_fetcher import TitleFetcher
from legacy_modules.region_categoriser import RegionCategoriser

logger = logging.getLogger(__name__)


class AnalysisETLService:
    """
    Responsible for the 'Semi-Automated' gathering of Analysis articles.

    Pipeline:
    1. Link Collection -> p1_csv
    2. Title Fetching -> p2_csv
    3. Region Categorization -> p3_csv
    """

    def __init__(self, config: Dict[str, Any], workspace_dir: str):
        """
        Args:
            config: Global config dict.
            workspace_dir: The 'Weekly Workspace' path where CSVs will be saved.
        """
        self.config = config
        self.workspace_dir = workspace_dir

        # Input dir for raw_links.txt (usually static 'inputs/')
        self.input_dir = self.config.get("input_directory", "inputs")

    def run_etl(self) -> str:
        """
        Executes the 3-step ETL process.
        Returns the path to the final P3 CSV.
        """
        logger.info(">>> Starting Analysis ETL Pipeline...")

        # --- Step 1: Link Collection ---
        p1_path = os.path.join(self.workspace_dir, "etl_p1_articles_with_links.csv")

        collector = LinkCollector(
            sources=self.config.get("sources", []),
            input_directory=self.input_dir,
            input_file="raw_links.txt",
            persistence_path=p1_path,
        )

        # Returns dataframe of collected links
        links_df = collector.collect_analysis_links()

        if links_df.empty:
            logger.warning("No links collected. ETL stopping.")
            return ""

        logger.info(f"Phase 1 Complete. Saved to: {p1_path}")

        # --- Step 2: Title Fetching ---
        logger.info("Starting Phase 2: Title Fetching...")
        fetcher = TitleFetcher(input_df=links_df)
        df_with_titles = fetcher.fetch_all_titles()

        if df_with_titles.empty:
            logger.warning("Title fetching produced no results.")
            return ""

        p2_path = os.path.join(
            self.workspace_dir, "etl_p2_articles_with_links_titles.csv"
        )
        df_with_titles.to_csv(p2_path, index=False)
        logger.info(f"Phase 2 Complete. Saved to: {p2_path}")

        # --- Step 3: Region Categorization ---
        logger.info("Starting Phase 3: Region Categorization...")
        categorizer = RegionCategoriser(self.config)

        regions = []
        total_rows = len(df_with_titles)

        for index, row in df_with_titles.iterrows():
            if index % 5 == 0:
                logger.info(f"Categorizing {index + 1}/{total_rows}...")

            title = row.get("title", "")
            source_name = row.get("source", "")
            # Heuristic check using combined text
            combined_text = f"Title: {title}\nSource: {source_name}"
            region = categorizer.get_region(combined_text)
            regions.append(region)

        df_with_titles["region"] = regions

        p3_path = os.path.join(
            self.workspace_dir, "etl_p3_articles_with_links_titles_regions.csv"
        )
        df_with_titles.to_csv(p3_path, index=False)
        logger.info(f"Phase 3 Complete. Final Dataset: {p3_path}")

        return p3_path
