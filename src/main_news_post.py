import os
import logging
from datetime import datetime
from modules.config_manager import ConfigManager
from modules.link_collector import LinkCollector
from modules.title_fetcher import TitleFetcher
from modules.region_categoriser import RegionCategorizer
from modules.markdown_generator import MarkdownGenerator


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
            output_path = os.path.join(output_dir, "p1_collected_analysis_links.csv")
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

            # ----------------------------------------
            # Phase 3: Region Categorization
            # ----------------------------------------
            logging.info("\n--- Starting Phase 3: Region Categorization ---")

            # Initialize and run the categorizer
            categorizer = RegionCategorizer(input_df=df_with_titles)
            df_with_regions = categorizer.categorize_regions()

            print("\n--- Final DataFrame with Regions ---")
            print(df_with_regions.to_string())

            # Save final data to CSV
            output_dir = config.get("output_directory", "../outputs/")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "p3_articles_with_regions.csv")

            df_with_regions.to_csv(output_path, index=False)
            logging.info(f"Process complete. Final data saved to '{output_path}'")

            # ----------------------------------------
            # Phase 4: Markdown Post Generation
            # ----------------------------------------
            logging.info("\n--- Starting Phase 4: Markdown Post Generation ---")
            generator = MarkdownGenerator(
                input_df=df_with_regions,
                output_directory=output_dir,
                current_date=datetime.now(),
            )
            generator.generate_markdown_post()
            logging.info(
                "\nAll phases complete. The weekly news post has been generated."
            )

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred during execution: {e}")
