import logging
import os
from datetime import datetime

# --- Import Custom Modules ---
from config_manager import ConfigManager
from headline_synthesizer import HeadlineSynthesizer
from regional_summariser import RegionalSummariser

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    logging.info("--- Starting Global Event Synthesis ---")

    try:
        # ----------------------------------------
        # 1. Load Configuration & Initialize Modules
        # ----------------------------------------
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.data

        youtube_api_key = config.get("api_keys", {}).get("youtube_api")
        sources = config.get("sources", [])
        output_dir = config.get("output_directory", "outputs")

        if not youtube_api_key:
            logging.error("YouTube API key not found in config.yaml. Exiting.")
            return
        if not sources:
            logging.warning("No sources found in config.yaml.")
            return

        # Initialize both synthesizers at the start
        headline_synthesizer = HeadlineSynthesizer(api_key=youtube_api_key)
        regional_summariser = RegionalSummariser()

        # ----------------------------------------
        # 2. Filter Sources
        # ----------------------------------------
        datapoint_sources = [
            source for source in sources if source.get("type") == "datapoint"
        ]

        if not datapoint_sources:
            logging.info("No sources of type 'datapoint' found. Nothing to process.")
            return

        logging.info(f"Found {len(datapoint_sources)} 'datapoint' sources to process.")

        # ----------------------------------------
        # 3. Process Sources for Initial Summary
        # ----------------------------------------
        markdown_results = []
        for source in datapoint_sources:
            channel_name = source.get("name")
            logging.info(f"\n--- Processing Channel: {channel_name} ---")
            summary = headline_synthesizer.synthesize_channel_activity(source)
            result_block = f"## {channel_name} ({source.get('url')})\n{summary}"
            markdown_results.append(result_block)
            logging.info(f"Finished processing '{channel_name}'.")

        # ----------------------------------------
        # 4. Write Initial Summary File
        # ----------------------------------------
        if not markdown_results:
            logging.info("No summaries were generated. Halting process.")
            return

        initial_summary_content = "\n\n".join(markdown_results)
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{date_str}-global-events-summary.md"
        output_path = os.path.join(output_dir, output_filename)
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(initial_summary_content)

        logging.info("--- Global Event Synthesis Complete ---")
        logging.info(f"Successfully wrote summary to '{output_path}'")

        # -----------------------------------------------------------------
        # 5. Read the initial summary and create the regional summary
        # -----------------------------------------------------------------
        logging.info("\n--- Starting Regional Summarization Step ---")

        # The initial summary content is already in the 'initial_summary_content' variable
        regional_summary_content = regional_summariser.summarise(
            initial_summary_content
        )

        if regional_summary_content and "Error:" not in regional_summary_content:
            regional_filename = f"{date_str}-regional-briefing.md"
            regional_output_path = os.path.join(output_dir, regional_filename)

            with open(regional_output_path, "w", encoding="utf-8") as f:
                f.write(regional_summary_content)

            logging.info("--- Regional Summarization Complete ---")
            logging.info(
                f"Successfully wrote regional briefing to '{regional_output_path}'"
            )
        else:
            logging.error(
                "Skipping regional summary file generation due to an error or empty content."
            )

    except FileNotFoundError as e:
        logging.error(f"A required file was not found. {e}")
    except Exception as e:
        logging.critical(f"An unexpected critical error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
