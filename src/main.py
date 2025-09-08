import os
import logging
from config_manager import ConfigManager
from link_collector import LinkCollector
from title_fetcher import TitleFetcher

if __name__ == "__main__":
    try:
        # Set up logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )

        # ----------------------------------------
        # Phase 1: Link Collection
        # ----------------------------------------

        # Load configuration from YAML file
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.data

        if not config:
            raise ValueError(
                "Configuration could not be loaded. Please check config.yaml."
            )

        # Initialize LinkCollector with configuration parameters
        collector = LinkCollector(
            sources=config.get("sources", []),
            input_directory=config.get("input_directory", "../inputs/"),
            input_file="raw_links.txt",
        )

        # Collect links from configured sources
        links_df = collector.collect_analysis_links()

        # Process and save collected links
        if not links_df.empty:
            print("\n--- Collected Links DataFrame ---")
            print(links_df.to_string())

            # Save links to CSV in the output directory
            output_dir = config.get("output_directory", "../outputs/")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(
                output_dir, "p1_collected_analysis_links.csv"
            )  # Fixed backtick typo
            links_df.to_csv(output_path, index=False)
            logging.info(f"Links successfully saved to '{output_path}'")

            # ----------------------------------------
            # Phase 2: Title Fetching
            # ----------------------------------------

            logging.info(
                "\n--- Link Collection Complete. Starting Phase 2: Title Fetching ---"
            )

            # Initialize TitleFetcher with collected links
            fetcher = TitleFetcher(input_df=links_df)

            # Fetch titles for all collected links
            df_with_titles = fetcher.fetch_all_titles()

            # Process and save results with titles
            if not df_with_titles.empty:
                print("\n--- Final DataFrame with Titles ---")
                print(df_with_titles.to_string())

                # Save final data to CSV
                output_dir = config.get("output_directory", "../outputs/")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "p2_articles_with_titles.csv")

                df_with_titles.to_csv(output_path, index=False)
                logging.info(f"Process complete. Final data saved to '{output_path}'")
            else:
                logging.warning("Title fetching did not produce any results.")
        else:
            print("\nProcess complete. No new links were collected.")

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred during execution: {e}")
