from abc import ABC, abstractmethod
from typing import List, Any


class BaseSynthesizer(ABC):
    """
    Responsible for combining multiple inputs into a higher-level insight
    (fusion/reasoning).
    """

    def __init__(self, llm_client: Any):
        self.llm_client = llm_client

    @abstractmethod
    def synthesize(self, inputs: List[Any], context: str = "") -> Any:
        """
        Synthesizes a collection of inputs into a single report or briefing.
        """
        pass
