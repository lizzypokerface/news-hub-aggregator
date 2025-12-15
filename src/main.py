import logging
import sys
import os

# --- Import Custom Modules ---
from modules.config_manager import ConfigManager
from global_news_aggregator import GlobalNewsAggregator


def main():
    """
    Main entry point for the Global News Aggregation Workflow.
    """
    # ----------------------------------------
    # 1. Setup Global Logging
    # ----------------------------------------
    # This configuration will be used by all modules using logging.getLogger()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)

    try:
        logger.info("=== Starting Global News Aggregation Workflow ===")

        # ----------------------------------------
        # 2. Load Configuration
        # ----------------------------------------

        config_path = "../config.yaml"

        if not os.path.exists("../config.yaml"):
            raise FileNotFoundError(
                "Could not find config.yaml in current or parent directory."
            )

        logger.info(f"Loading configuration from {config_path}...")
        config_manager = ConfigManager(config_path)
        config = config_manager.data

        if not config:
            raise ValueError("Configuration is empty or could not be loaded.")

        # ----------------------------------------
        # 3. Initialize Aggregator
        # ----------------------------------------
        aggregator = GlobalNewsAggregator(config)

        # ----------------------------------------
        # 4. Execute Workflow Stages
        # ----------------------------------------

        # Stage A: Regional Briefing (YouTube/Poe Synthesis)
        aggregator.generate_regional_briefing()

        # Stage B: News ETL (Link Collection -> Titles -> Regions)
        aggregator.run_news_etl()

        # Stage C: Content Summarization (Detailed summaries of specific sources)
        aggregator.generate_content_summarization()

        # Stage D: News Post Construction (Final Markdown generation)
        aggregator.construct_news_post()

        logger.info("=== Global News Aggregation Workflow Completed Successfully ===")

    except FileNotFoundError as e:
        logger.error(f"File Error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(
            f"An unexpected error occurred in the main workflow: {e}", exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
