import logging
import sys
import os

from legacy_modules.config_manager import ConfigManager
from services.global_news_aggregator import GlobalNewsAggregator
from services.historical_materialist_researcher import HistoricalMaterialistResearcher
from services.news_summariser import NewsSummariser


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)

    try:
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.data

        # ----------------------------------------
        # 3. User Selection Interface
        # ----------------------------------------
        print("\n" + "=" * 50)
        print(" NEWSHUB: GLOBAL INTELLIGENCE")
        print("=" * 50)
        print("1. Generate Regional Briefing (YouTube/Poe Synthesis)")
        print("2. Generate Weekly News Post (ETL + Markdown)")
        print("3. Batch Summarization (By Region or Source)")
        print("4. Targeted Research (Deep Dive Analysis)")
        print("=" * 50)

        choice = input("Select Mode (1-4): ").strip()

        # ----------------------------------------
        # 4. Execute Selected Workflow
        # ----------------------------------------

        if choice == "1":
            logger.info("Mode Selected: Regional Briefing Generation")
            aggregator = GlobalNewsAggregator(config)
            aggregator.generate_regional_briefing()

        elif choice == "2":
            logger.info("Mode Selected: Weekly News Post Generation")
            aggregator = GlobalNewsAggregator(config)
            aggregator.run_news_etl()
            aggregator.construct_news_post()

        elif choice == "3":
            logger.info("Mode Selected: Batch Summarization")

            # 1. Ask for Mode
            print("\nSummarize by:")
            print("1. Region (e.g., compile all 'China' articles)")
            print("2. Source (e.g., compile all 'The New Atlas' articles)")
            sub_choice = input("Select (1 or 2): ").strip()

            mode = "region" if sub_choice == "1" else "source"

            # 2. Ask for Filter
            print(f"\nEnter specific {mode} name to filter (e.g., 'China').")
            print("Or press Enter to summarize ALL.")
            filter_key = input("Filter: ").strip()
            if filter_key == "":
                filter_key = None  # None implies "All"

            # 3. Define Input Path
            input_csv = os.path.join(
                config.get("output_directory", "outputs"),
                "p3_articles_with_regions.csv",
            )

            # 4. Run
            summariser = NewsSummariser(config)
            summariser.batch_summarize(input_csv, mode, filter_key)

        elif choice == "4":
            input_dir = config.get("input_directory", "inputs")
            links_file = os.path.join(input_dir, "research_links.txt")

            if not os.path.exists(links_file):
                pass

            researcher = HistoricalMaterialistResearcher(config)
            researcher.conduct_research(manual_review=True)

        else:
            logger.warning(f"Invalid selection: '{choice}'. Exiting.")
            sys.exit(0)

    except Exception as e:
        logger.critical(f"Critical Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
