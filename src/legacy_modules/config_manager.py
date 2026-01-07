# Legacy module: retained for compatibility and slated for migration or deprecation.

import yaml
import os
import logging


class ConfigManager:
    """
    A modular class to manage reading and accessing configuration from a YAML file.
    Includes basic logging for operations.
    """

    def __init__(self, config_path: str):
        logging.info(f"Initializing configuration from '{config_path}'...")

        if not os.path.exists(config_path):
            # Log the error before raising the exception
            logging.error(f"Configuration file not found at '{config_path}'")
            raise FileNotFoundError(
                f"Error: The configuration file was not found at '{config_path}'"
            )

        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self) -> dict:
        try:
            with open(self.config_path) as file:
                config_data = yaml.safe_load(file)
                logging.info(
                    f"Successfully loaded and parsed configuration from '{self.config_path}'"
                )
                return config_data
        except yaml.YAMLError as e:
            # Handle potential errors during YAML parsing
            logging.error(f"Error parsing YAML file '{self.config_path}': {e}")
            return {}  # Return an empty dict on error
