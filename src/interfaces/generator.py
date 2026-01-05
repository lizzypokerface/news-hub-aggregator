from abc import ABC, abstractmethod
from typing import Any


class BaseGenerator(ABC):
    """
    Responsible for transforming a single unit of input using an LLM
    (e.g., summarization, categorization).
    """

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    @abstractmethod
    def generate(self, input_data: Any) -> Any:
        """
        Transforms input data into a new format via an LLM call.
        """
        pass
