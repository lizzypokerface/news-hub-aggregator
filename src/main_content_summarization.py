import logging
import os
import re
from datetime import datetime
import pandas as pd

# --- Import Custom Modules ---
from modules.config_manager import ConfigManager
from modules.content_summarizer import ContentSummarizer


def sanitize_filename(name: str) -> str:
    """Removes spaces and special characters to create a valid filename."""
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[-\s]+", "_", name)
    return name


def main():
    """
    Main function to orchestrate the content summarization process.
    """
    logger = logging.getLogger(__name__)
    logger.info("--- Starting Content Summarization Workflow ---")

    try:
        # ----------------------------------------
        # 1. Load Configuration
        # ----------------------------------------
        logger.info("Loading configuration from ../config.yaml...")
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.data

        if not config:
            raise ValueError(
                "Configuration could not be loaded or is empty. Please check config.yaml."
            )

        # Extract API key, sources, and output path from config
        poe_api_key = config.get("api_keys", {}).get("poe_api")
        sources_to_summarize = config.get("summarise", [])
        output_dir_base = config.get(
            "output_directory", "../outputs"
        )  # Use path from config

        # --- Configuration Validation ---
        if not poe_api_key:
            logger.error("Poe API key ('poe_api') not found in config.yaml. Exiting.")
            return
        if not sources_to_summarize:
            logger.warning(
                "No sources listed under 'summarise' in config.yaml. Nothing to do."
            )
            return

        logger.info(
            f"Found {len(sources_to_summarize)} sources to process: {', '.join(sources_to_summarize)}"
        )
        logger.info(f"Base output directory set to: {output_dir_base}")

        # ----------------------------------------
        # 2. Create Dated Output Directory
        # ----------------------------------------
        date_str = datetime.now().strftime("%Y-%m-%d")
        final_output_dir = os.path.join(output_dir_base, f"summaries_{date_str}")

        logger.info(
            f"Creating output directory for today's summaries: {final_output_dir}"
        )
        os.makedirs(final_output_dir, exist_ok=True)

        # ----------------------------------------
        # 3. Load and Filter Articles
        # ----------------------------------------
        input_csv_path = "../outputs/p3_articles_with_regions.csv"
        logger.info(f"Reading articles from {input_csv_path}...")

        if not os.path.exists(input_csv_path):
            logger.error(f"Input file not found: {input_csv_path}. Exiting.")
            return

        df = pd.read_csv(input_csv_path)
        filtered_df = df[df["source"].isin(sources_to_summarize)].copy()

        if filtered_df.empty:
            logger.warning(
                "No articles found matching the sources specified in config.yaml. Exiting."
            )
            return

        filtered_df.sort_values(by="source", ascending=True, inplace=True)
        logger.info(f"Found {len(filtered_df)} articles to summarize.")

        # ----------------------------------------
        # 4. Initialize Summarizer
        # ----------------------------------------
        summarizer = ContentSummarizer(poe_api_key=poe_api_key)

        # ----------------------------------------
        # 5. Process Articles by Source
        # ----------------------------------------
        for source_name, group in filtered_df.groupby("source"):
            logger.info(f"\n--- Processing Source: {source_name} ---")

            markdown_blocks = [f"# {source_name}\n"]

            for index, row in group.iterrows():
                title, url, region, format = (
                    row["title"],
                    row["url"],
                    row["region"],
                    row["format"],
                )
                logger.info(f"Summarizing article: '{title}' from {url}")

                summary_text = summarizer.summarize(source_name=source_name, url=url)

                # --- Graceful Failure Handling ---
                if summary_text.strip().startswith("Error:"):
                    logger.warning(
                        f"Failed to summarize '{title}'. Using fallback text. Reason: {summary_text}"
                    )
                    summary_text = (
                        "Could not retrieve summary. Please visit the link directly."
                    )

                article_block = (
                    f"## {title} | {region}\n"
                    f"{format}: {url}\n\n"
                    f"{summary_text}\n"
                )
                markdown_blocks.append(article_block)

            # --- Write the final Markdown file for the source ---
            final_content = "\n---\n".join(
                markdown_blocks
            )  # Use --- for a horizontal rule between articles

            sanitized_source_name = sanitize_filename(source_name)
            output_filename = f"{sanitized_source_name}-{date_str}.md"
            # Use the new dated directory path
            output_path = os.path.join(final_output_dir, output_filename)

            logger.info(f"Writing final summary for '{source_name}' to {output_path}")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_content)

        logger.info("\n--- Content Summarization Workflow Complete ---")

    except FileNotFoundError as e:
        logger.error(f"A required file was not found. Please check paths. Error: {e}")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    main()
