import logging
import os
import re
from datetime import datetime
import pandas as pd

# --- Import Custom Modules ---
from modules.content_summarizer import ContentSummarizer
from modules.headline_synthesizer import HeadlineSynthesizer
from modules.regional_summariser import RegionalSummariser
from modules.link_collector import LinkCollector
from modules.title_fetcher import TitleFetcher
from modules.region_categoriser import RegionCategorizer
from modules.markdown_generator import MarkdownGenerator


class GlobalNewsAggregator:
    def __init__(self, config: dict):
        """
        Initializes the aggregator with a configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Default Output Directory from config or fallback
        self.output_dir = self.config.get("output_directory", "../outputs/")

    def _sanitize_filename(self, name: str) -> str:
        """Removes spaces and special characters to create a valid filename."""
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[-\s]+", "_", name)
        return name

    def generate_regional_briefing(self):
        """
        Orchestrates the headline synthesis and regional summarization process.
        Refactored from main_regional_briefing.py
        """
        self.logger.info("--- Starting Regional Briefing Generation ---")

        try:
            # Extract Keys
            api_keys = self.config.get("api_keys", {})
            youtube_api_key = api_keys.get("youtube_api")
            poe_api_key = api_keys.get("poe_api")
            sources = self.config.get("sources", [])

            # Validation
            if not youtube_api_key:
                self.logger.error("YouTube API key not found in config.")
                return
            if not poe_api_key:
                self.logger.error("Poe API key ('poe_api') not found in config.")
                return
            if not sources:
                self.logger.warning("No sources found in config.")
                return

            # Initialize Modules
            headline_synthesizer = HeadlineSynthesizer(api_key=youtube_api_key)
            regional_summariser = RegionalSummariser(poe_api_key=poe_api_key)

            # Filter Sources
            datapoint_sources = [s for s in sources if s.get("type") == "datapoint"]
            if not datapoint_sources:
                self.logger.info("No 'datapoint' sources found. Skipping.")
                return

            self.logger.info(
                f"Processing {len(datapoint_sources)} 'datapoint' sources."
            )

            # Process Sources
            markdown_results = []
            for source in datapoint_sources:
                channel_name = source.get("name")
                self.logger.info(f"Processing Channel: {channel_name}")
                summary = headline_synthesizer.synthesize_channel_activity(source)
                result_block = f"## {channel_name} ({source.get('url')})\n{summary}"
                markdown_results.append(result_block)

            if not markdown_results:
                self.logger.info("No summaries generated.")
                return

            # Write Initial Global Summary
            initial_summary_content = "\n\n".join(markdown_results)
            date_str = datetime.now().strftime("%Y-%m-%d")

            os.makedirs(self.output_dir, exist_ok=True)
            output_filename = f"{date_str}-global-events-summary.md"
            output_path = os.path.join(self.output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(initial_summary_content)
            self.logger.info(f"Global summary written to '{output_path}'")

            # Generate Regional Summary
            self.logger.info("Starting Regional Summarization...")
            regional_summary_content = regional_summariser.summarise(
                initial_summary_content
            )

            if regional_summary_content and "Error:" not in regional_summary_content:
                regional_filename = f"{date_str}-regional-briefing.md"
                regional_output_path = os.path.join(self.output_dir, regional_filename)
                with open(regional_output_path, "w", encoding="utf-8") as f:
                    f.write(regional_summary_content)
                self.logger.info(
                    f"Regional briefing written to '{regional_output_path}'"
                )
            else:
                self.logger.error(
                    "Skipping regional summary generation due to error or empty content."
                )

            self.logger.info("--- Regional Briefing Workflow Complete ---")

        except Exception as e:
            self.logger.critical(
                f"Critical error in generate_regional_briefing: {e}", exc_info=True
            )

    def run_news_etl(self):
        """
        Runs Phases 1, 2, and 3 of the news post workflow: Link Collection, Title Fetching, Region Categorization.
        Refactored from main_news_post.py
        """
        self.logger.info("--- Starting News ETL (Phases 1-3) ---")

        try:
            # Phase 1: Link Collection
            collector = LinkCollector(
                sources=self.config.get("sources", []),
                input_directory=self.config.get("input_directory", "../inputs/"),
                input_file="raw_links.txt",
            )
            links_df = collector.collect_analysis_links()

            if links_df.empty:
                self.logger.warning("No links collected. ETL stopping.")
                return

            os.makedirs(self.output_dir, exist_ok=True)
            p1_path = os.path.join(self.output_dir, "p1_collected_analysis_links.csv")
            links_df.to_csv(p1_path, index=False)
            self.logger.info(f"Phase 1 Complete. Links saved to '{p1_path}'")

            # Phase 2: Title Fetching
            self.logger.info("Starting Phase 2: Title Fetching")
            fetcher = TitleFetcher(input_df=links_df)
            df_with_titles = fetcher.fetch_all_titles()

            if df_with_titles.empty:
                self.logger.warning("Title fetching produced no results.")
                return

            p2_path = os.path.join(self.output_dir, "p2_articles_with_titles.csv")
            df_with_titles.to_csv(p2_path, index=False)
            self.logger.info(f"Phase 2 Complete. Titles saved to '{p2_path}'")

            # Phase 3: Region Categorization
            self.logger.info("Starting Phase 3: Region Categorization")
            categorizer = RegionCategorizer(input_df=df_with_titles)
            df_with_regions = categorizer.categorize_regions()

            p3_path = os.path.join(self.output_dir, "p3_articles_with_regions.csv")
            df_with_regions.to_csv(p3_path, index=False)
            self.logger.info(f"Phase 3 Complete. Regions saved to '{p3_path}'")

            self.logger.info("--- News ETL Workflow Complete ---")

        except Exception as e:
            self.logger.error(f"Error in run_news_etl: {e}", exc_info=True)

    def construct_news_post(self):
        """
        Runs Phase 4 of the news post workflow: Generating the Markdown Post.
        Refactored from main_news_post.py
        """
        self.logger.info("--- Starting News Post Construction (Phase 4) ---")

        try:
            # Load the output from Phase 3
            input_csv_path = os.path.join(
                self.output_dir, "p3_articles_with_regions.csv"
            )

            if not os.path.exists(input_csv_path):
                self.logger.error(
                    f"Input file not found: {input_csv_path}. Run ETL first."
                )
                return

            df_with_regions = pd.read_csv(input_csv_path)

            generator = MarkdownGenerator(
                input_df=df_with_regions,
                output_directory=self.output_dir,
                current_date=datetime.now(),
            )
            generator.generate_markdown_post()
            self.logger.info("News Post Construction Complete.")

        except Exception as e:
            self.logger.error(f"Error in construct_news_post: {e}", exc_info=True)

    def generate_content_summarization(self):
        """
        Summarizes specific articles based on configuration.
        Refactored from main_content_summarization.py
        """
        self.logger.info("--- Starting Content Summarization Workflow ---")

        try:
            poe_api_key = self.config.get("api_keys", {}).get("poe_api")
            sources_to_summarize = self.config.get("summarise", [])

            # Validation
            if not poe_api_key:
                self.logger.error("Poe API key ('poe_api') not found in config.")
                return
            if not sources_to_summarize:
                self.logger.warning("No sources listed under 'summarise' in config.")
                return

            # Setup Output Directory for Summaries
            date_str = datetime.now().strftime("%Y-%m-%d")
            final_output_dir = os.path.join(self.output_dir, f"summaries_{date_str}")
            os.makedirs(final_output_dir, exist_ok=True)
            self.logger.info(f"Summaries will be saved to: {final_output_dir}")

            # Load Data (Hand-off from ETL)
            input_csv_path = os.path.join(
                self.output_dir, "p3_articles_with_regions.csv"
            )
            if not os.path.exists(input_csv_path):
                self.logger.error(
                    f"Input file not found: {input_csv_path}. Run ETL first."
                )
                return

            df = pd.read_csv(input_csv_path)
            filtered_df = df[df["source"].isin(sources_to_summarize)].copy()

            if filtered_df.empty:
                self.logger.warning("No articles found matching sources to summarize.")
                return

            filtered_df.sort_values(by="source", ascending=True, inplace=True)
            self.logger.info(f"Found {len(filtered_df)} articles to summarize.")

            # Initialize Summarizer
            summarizer = ContentSummarizer(poe_api_key=poe_api_key)

            # Process by Source
            for source_name, group in filtered_df.groupby("source"):
                self.logger.info(f"Processing Source for Summaries: {source_name}")
                markdown_blocks = [f"# {source_name}\n"]

                for _, row in group.iterrows():
                    title, url, region, fmt = (
                        row["title"],
                        row["url"],
                        row["region"],
                        row["format"],
                    )
                    self.logger.info(f"Summarizing: '{title}'")

                    summary_text = summarizer.summarize(
                        source_name=source_name, url=url
                    )

                    # Graceful Failure
                    if summary_text.strip().startswith("Error:"):
                        self.logger.warning(
                            f"Failed to summarize '{title}'. Using fallback."
                        )
                        summary_text = "Could not retrieve summary. Please visit the link directly."

                    article_block = (
                        f"## {title} | {region}\n{fmt}: {url}\n\n{summary_text}\n"
                    )
                    markdown_blocks.append(article_block)

                # Write Source File
                final_content = "\n---\n".join(markdown_blocks)
                sanitized_name = self._sanitize_filename(source_name)
                output_filename = f"{sanitized_name}-{date_str}.md"
                output_path = os.path.join(final_output_dir, output_filename)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(final_content)
                self.logger.info(f"Summary written to {output_path}")

            self.logger.info("--- Content Summarization Workflow Complete ---")

        except Exception as e:
            self.logger.critical(
                f"Critical error in generate_content_summarization: {e}", exc_info=True
            )
