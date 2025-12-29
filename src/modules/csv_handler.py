import os
import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class CSVHandler:
    """
    Handles reading and writing to CSV files with a focus on incremental appending.
    """

    @staticmethod
    def append_records(records: List[Dict[str, Any]], filepath: str) -> None:
        """
        Appends a list of dictionaries to a CSV file.
        Handles creating the file and writing headers if it doesn't exist.
        """
        if not records:
            return

        df = pd.DataFrame(records)

        # Check if file exists to determine if we need to write the header
        file_exists = os.path.isfile(filepath)

        try:
            # mode='a' is append. header=not file_exists means write header only if new file.
            df.to_csv(filepath, mode="a", header=not file_exists, index=False)
            logger.info(f"Appended {len(records)} records to {filepath}")
        except Exception as e:
            logger.error(f"Failed to append records to CSV: {e}")
            raise

    @staticmethod
    def load_as_dataframe(filepath: str) -> pd.DataFrame:
        """
        Reads the CSV into a Pandas DataFrame. Returns empty DF if file doesn't exist.
        """
        if not os.path.exists(filepath):
            return pd.DataFrame()

        try:
            return pd.read_csv(filepath)
        except Exception as e:
            logger.error(f"Failed to read CSV from {filepath}: {e}")
            return pd.DataFrame()
