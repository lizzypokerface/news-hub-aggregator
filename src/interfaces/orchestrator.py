from abc import ABC, abstractmethod


class BaseOrchestrator(ABC):
    """
    Responsible for managing the workflow: configuring the pipeline
    and passing data between Consolidators, Generators, and Synthesizers.
    """

    @abstractmethod
    def run(self) -> None:
        """
        Executes the full pipeline.
        """
        pass
