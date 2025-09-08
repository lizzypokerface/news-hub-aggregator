import os
import logging
from config_manager import ConfigManager
from link_collector import LinkCollector


if __name__ == "__main__":
    try:
        # 1. Load configuration from the YAML file.
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.data

        if not config:
            raise ValueError(
                "Configuration could not be loaded. Please check config.yaml."
            )

        # 2. Initialize the LinkCollector with sources and the input directory path.
        collector = LinkCollector(
            sources=config.get("sources", []),
            input_directory=config.get(
                "input_directory", config.get("input_directory", "../outputs/")
            ),
        )

        # 3. Run the link collection process. This will open the browser and wait for you.
        links_df = collector.collect_analysis_links()

        # 4. Display the results and save them to a file.
        if not links_df.empty:
            print("\n--- Collected Links DataFrame ---")
            print(links_df.to_string())

            # Save the DataFrame to a CSV file in the specified output directory.
            output_dir = config.get("output_directory", "../outputs/")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "collected_analysis_links.csv")
            links_df.to_csv(output_path, index=False)
            logging.info(f"DataFrame successfully saved to '{output_path}'")
        else:
            print("\nProcess complete. No new links were collected.")

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred during execution: {e}")
