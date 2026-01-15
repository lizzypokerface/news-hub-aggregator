from abc import ABC, abstractmethod
from typing import Any


class BaseConsolidator(ABC):
    """
    Responsible for fetching raw data from external sources (web, APIs, files).
    """

    @abstractmethod
    def consolidate(self) -> Any:
        """
        Fetches and cleans data, returning a standardized data object.
        """
        pass
