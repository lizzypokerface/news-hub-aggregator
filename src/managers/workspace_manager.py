import os
import json
import logging
import dataclasses
from typing import Any, TypeVar, Optional

logger = logging.getLogger(__name__)

T = TypeVar("T")


class WorkspaceManager:
    """
    Manages the physical storage of the Weekly Intelligence run.
    Handles Checkpointing (JSON) and Reporting (Markdown).
    """

    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        os.makedirs(self.workspace_dir, exist_ok=True)
        # Cache existing files to minimize IO calls (though OS caching is fast)
        self._refresh_file_cache()

    def _refresh_file_cache(self):
        self.existing_files = set(os.listdir(self.workspace_dir))

    def has_checkpoint(self, key: str) -> bool:
        """Checks if a machine-readable checkpoint exists (e.g., 'p1_mainstream.json')."""
        filename = f"{key}.json"
        return filename in self.existing_files

    def save_checkpoint(self, key: str, data_object: Any):
        """
        Saves a Data Class to JSON.
        Automatically converts datetime objects to ISO strings.
        """
        filename = f"{key}.json"
        path = os.path.join(self.workspace_dir, filename)

        try:
            # Convert Dataclass to Dict
            if dataclasses.is_dataclass(data_object):
                data_dict = dataclasses.asdict(data_object)
            else:
                data_dict = data_object

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=2, default=str, ensure_ascii=False)

            self.existing_files.add(filename)
            logger.info(f"Checkpoint Saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint {filename}: {e}")

    def load_checkpoint_json(self, key: str) -> Optional[dict]:
        """Loads raw JSON data from a checkpoint."""
        filename = f"{key}.json"
        path = os.path.join(self.workspace_dir, filename)

        if not os.path.exists(path):
            return None

        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load checkpoint {filename}: {e}")
            return None

    def save_report(self, filename: str, content: str):
        """Saves a human-readable Markdown report."""
        path = os.path.join(self.workspace_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.existing_files.add(filename)
            logger.info(f"Report Saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save report {filename}: {e}")

    def load_report(self, filename: str) -> str:
        path = os.path.join(self.workspace_dir, filename)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
        return ""
