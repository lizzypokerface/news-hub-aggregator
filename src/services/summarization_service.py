import logging
from typing import List, Dict, Any
from datetime import datetime

from legacy_modules.csv_handler import CSVHandler
from legacy_modules.content_extractor import ContentExtractor
from reporters.markdown_report_builder import MarkdownReportBuilder
from interfaces.models import Article, ReportArtifact

# Generators
from generators.intel_brief_generator import IntelBriefGenerator

logger = logging.getLogger(__name__)


class SummarizationService:
    """
    Orchestrates Batch Summarization (Phase 3).
    Supports multiple summarization styles via the 'style' flag.
    """

    def __init__(self, config: Dict[str, Any], llm_client: Any):
        """
        Args:
            config: The full configuration dictionary.
            llm_client: The shared LLM client instance.
        """
        self.config = config
        self.llm_client = llm_client

        # Initialize helper components
        self.extractor = ContentExtractor(self.config)
        self.builder = MarkdownReportBuilder()

    def run_batch_summarization(
        self,
        csv_path: str,
        mode: str = "region",
        filter_key: str = None,
        style: str = "intel_brief",
    ) -> List[ReportArtifact]:
        """
        Args:
            csv_path: Path to article metadata CSV.
            mode: Grouping mode ('region' or 'source').
            filter_key: Optional filter string.
            style: Generator style ('intel_brief', etc.).
        """
        logger.info(f"Starting Batch Summarization (Mode: {mode}, Style: {style})...")

        # 1. Select Generator Strategy
        generator = self._get_generator(style)
        if not generator:
            logger.error(f"Unknown summarization style: '{style}'")
            return []

        # 2. Load Data
        df = CSVHandler.load_as_dataframe(csv_path)
        if df.empty:
            logger.error("Input CSV is empty.")
            return []

        # 3. Filter & Group
        if filter_key:
            df = df[df[mode].astype(str).str.contains(filter_key, case=False, na=False)]

        grouped = df.groupby(mode)
        generated_artifacts = []

        # 4. Processing Loop
        for group_name, group_df in grouped:
            group_name_str = str(group_name)
            logger.info(
                f"Processing Group: {group_name_str} ({len(group_df)} articles)"
            )

            processed_articles: List[Article] = []

            for _, row in group_df.iterrows():
                url = row.get("url")
                if not url:
                    continue

                # Extraction
                raw_text = self.extractor.get_text(url)

                article = Article(
                    title=row.get("title", "Unknown"),
                    source=row.get("source", "Unknown"),
                    url=url,
                    raw_content=raw_text,
                    date_collected=datetime.now(),
                )

                # Generation (Delegated to selected generator)
                enriched_article = generator.generate(article)
                processed_articles.append(enriched_article)

            # Build Report
            report_title = f"{style.replace('_', '-').title()}-{group_name_str}"

            # build_summary_report is the generic method for all summary styles.
            artifact = self.builder.build_summary_report(
                report_title=report_title,
                articles=processed_articles,
                run_date=datetime.now(),
            )
            generated_artifacts.append(artifact)

        return generated_artifacts

    def _get_generator(self, style: str):
        """Factory method to select the generator."""
        if style == "intel_brief":
            return IntelBriefGenerator(self.llm_client)
        # Future styles:
        # elif style == "detailed_summary":
        #     return DetailedSummaryGenerator(self.llm_client)
        else:
            return None
