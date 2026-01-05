"""
This module serves as the interface aggregator for the news-hub-aggregator project.
It imports and exposes the base classes for consolidators, generators, synthesizers, and orchestrators,
making them available for external use. The `__all__` variable defines the public API of this package,
ensuring that only the specified base classes are accessible when importing from the interfaces package.
"""

from .consolidator import BaseConsolidator
# from .generator import BaseGenerator
# from .synthesizer import BaseSynthesizer
# from .orchestrator import BaseOrchestrator

__all__ = [
    "BaseConsolidator",
    # "BaseGenerator",
    # "BaseSynthesizer",
    # "BaseOrchestrator"
]
