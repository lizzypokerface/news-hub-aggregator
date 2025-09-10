import os
import logging
from datetime import datetime

# Import your custom modules
from modules.config_manager import ConfigManager
from modules.gpe_analyser import generate_gpe_regional_briefing

# --- Helper Functions (No changes needed here) ---


def _find_input_file(directory: str, suffix: str) -> str:
    """Finds a unique file in a directory with a specific suffix."""
    logging.info(f"Searching for file ending with '{suffix}' in '{directory}'...")
    try:
        files = [f for f in os.listdir(directory) if f.endswith(suffix)]
        if len(files) == 0:
            raise FileNotFoundError(
                f"No file ending with '{suffix}' found in '{directory}'."
            )
        if len(files) > 1:
            logging.warning(
                f"Multiple files ending with '{suffix}' found. Using the first one: {files[0]}"
            )

        file_path = os.path.join(directory, files[0])
        logging.info(f"Found input file: '{file_path}'")
        return file_path
    except Exception as e:
        logging.error(f"An error occurred while searching for input files: {e}")
        raise


def _read_file_content(file_path: str) -> str:
    """Reads the entire content of a file into a string."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to read content from '{file_path}': {e}")
        raise


def _clean_llm_output(llm_response_text: str) -> str:
    """Removes meta-commentary and 'thinking' lines (blockquotes) from the LLM output."""
    if not llm_response_text:
        return ""

    logging.info("Cleaning LLM response: removing blockquote 'thinking' lines...")
    lines = llm_response_text.splitlines()
    cleaned_lines = [line for line in lines if not line.strip().startswith(">")]
    result = "\n".join(cleaned_lines).strip()
    return result


# --- Main Execution Block ---

if __name__ == "__main__":
    # Set up logging first to capture messages from all parts of the script
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    try:
        logging.info("Starting GPE analysis workflow...")

        # 1. Load configuration using your ConfigManager
        config_manager = ConfigManager("../config.yaml")

        # Check if the data was loaded successfully
        if not config_manager.data:
            raise ValueError(
                "Configuration data is empty. Check config.yaml for errors."
            )

        # Access the data dictionary from the config_manager instance
        config_data = config_manager.data

        # 2. Retrieve settings from the configuration data
        input_directory = config_data.get("input_directory")
        output_directory = config_data.get("output_directory")
        api_keys = config_data.get("api_keys", {})
        poe_api_key = api_keys.get("poe_api")

        # Validate configuration values
        if not input_directory or not output_directory:
            raise ValueError(
                "Input and output directories must be specified in config.yaml."
            )
        if not poe_api_key or poe_api_key == "your_poe_api_key_goes_here":
            raise ValueError("Poe API key is missing or not set in config.yaml.")

        # 3. Find and read input files
        mainstream_file_path = _find_input_file(
            output_directory, "regional-briefing.md"
        )
        analysis_file_path = _find_input_file(output_directory, "weekly-news.md")

        mainstream_content = _read_file_content(mainstream_file_path)
        analysis_content = _read_file_content(analysis_file_path)

        # 4. Call the GPE analysis function
        raw_briefing = generate_gpe_regional_briefing(
            mainstream_analysis=mainstream_content,
            expert_analysis=analysis_content,
            poe_api_key=poe_api_key,
        )

        # 5. Clean the LLM's output
        cleaned_briefing = _clean_llm_output(raw_briefing)

        # 6. Write the final output file
        today_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{today_str}-gpe-regional-briefing.md"
        output_path = os.path.join(output_directory, output_filename)

        os.makedirs(output_directory, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_briefing)

        logging.info(f"Workflow complete. GPE briefing saved to '{output_path}'.")

    except Exception as e:
        logging.critical(f"A critical error stopped the workflow: {e}")
