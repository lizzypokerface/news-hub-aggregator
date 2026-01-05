from dataclasses import dataclass
from typing import List


@dataclass
class ReportArtifact:
    """
    Represents a generated file ready to be saved to disk.
    Contains the raw content and the suggested filename.
    """

    content: str
    filename: str


@dataclass
class MainstreamSourceEntry:
    """
    Represents a chunk of data from a Mainstream 'datapoint' source.
    """

    source_name: str
    content: List[str]  # Flexible: ["Title 1", "Title 2"] OR ["Full scraped text..."]
    source_type: str  # 'youtube' or 'webpage'


@dataclass
class MainstreamHeadlines:
    """
    Container for all mainstream source entries.
    """

    entries: List[MainstreamSourceEntry]


@dataclass
class SourceHeadlines:
    """
    Helper class: Contains all titles from a single source, maintaining rank order.
    Example: Tricontinental -> ["Title 1", "Title 2"]
    """

    source_name: str
    titles: List[str]


@dataclass
class AnalysisHeadlines:
    """
    Consolidated view of analysis articles.
    Now represents a flat list of sources without a top-level region grouping.
    """

    source_groups: List[SourceHeadlines]
