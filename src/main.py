import logging
import sys
import os

from modules.config_manager import ConfigManager
from global_news_aggregator import GlobalNewsAggregator
from historical_materialist_researcher import HistoricalMaterialistResearcher


def main():
    """
    Main entry point for the Global Intelligence System.
    """
    # ----------------------------------------
    # 1. Setup Global Logging
    # ----------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)

    try:
        logger.info("=== Starting Global Intelligence System ===")

        # ----------------------------------------
        # 2. Load Configuration
        # ----------------------------------------
        # Check current and parent directory for config
        config_path = "config.yaml"
        if not os.path.exists(config_path):
            if os.path.exists("../config.yaml"):
                config_path = "../config.yaml"
            else:
                raise FileNotFoundError(
                    "Could not find config.yaml in current or parent directory."
                )

        logger.info(f"Loading configuration from {config_path}...")
        config_manager = ConfigManager(config_path)
        config = config_manager.data

        if not config:
            raise ValueError("Configuration is empty or could not be loaded.")

        # ----------------------------------------
        # 3. User Selection Interface
        # ----------------------------------------
        print("\n" + "=" * 50)
        print(" NEWSHUB: GLOBAL INTELLIGENCE")
        print("=" * 50)
        print("1. Generate Regional Briefing")
        print("2. Generate Weekly News Post")
        print("3. Perform Targeted Research (Deep Dive Analysis)")
        print("=" * 50)

        choice = input("Select Mode (1-3): ").strip()

        # ----------------------------------------
        # 4. Execute Selected Workflow
        # ----------------------------------------

        if choice == "1":
            logger.info("Mode Selected: Regional Briefing Generation")
            aggregator = GlobalNewsAggregator(config)

            # Stage A: Regional Briefing only
            aggregator.generate_regional_briefing()

            logger.info("Regional Briefing Workflow Completed.")

        elif choice == "2":
            logger.info("Mode Selected: Weekly News Post Generation")
            aggregator = GlobalNewsAggregator(config)

            # Stage B: News ETL (Link Collection -> Titles -> Regions)
            aggregator.run_news_etl()

            # Stage C: News Post Construction (Final Markdown generation)
            aggregator.construct_news_post()

            logger.info("Weekly News Workflow Completed Successfully.")

        elif choice == "3":
            logger.info("Mode Selected: Targeted Research")

            # Check for input file existence before starting
            input_dir = config.get("input_directory", "../inputs")
            links_file = os.path.join(input_dir, "research_links.txt")

            if not os.path.exists(links_file):
                logger.warning(f"Research links file not found at: {links_file}")
                create_new = (
                    input("Create a new empty links file? (y/n): ").lower().strip()
                )
                if create_new == "y":
                    os.makedirs(input_dir, exist_ok=True)
                    with open(links_file, "w") as f:
                        f.write("")  # Create empty file
                    print(f"\nCreated {links_file}.")
                    print(
                        "Please paste your links into that file and restart the script."
                    )
                    return
                else:
                    logger.error("Cannot proceed without links file.")
                    return

            researcher = HistoricalMaterialistResearcher(config)

            # Run the interactive research workflow
            # manual_review=True allows you to edit the raw transcript file before analysis
            researcher.conduct_research(manual_review=True)

            logger.info("Targeted Research Workflow Completed Successfully.")

        else:
            logger.warning(f"Invalid selection: '{choice}'. Exiting.")
            sys.exit(0)

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
