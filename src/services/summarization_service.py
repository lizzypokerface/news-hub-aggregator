import logging
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import asdict

from legacy_modules.csv_handler import CSVHandler
from legacy_modules.content_extractor import ContentExtractor
from reporters.markdown_report_builder import MarkdownReportBuilder
from interfaces.models import Article, ReportArtifact

# Generators
from generators.intel_brief_generator import IntelBriefGenerator

CHECKPOINT_FILENAME = "stage_04_enriched_articles_summarized.jsonl"

logger = logging.getLogger(__name__)


class SummarizationService:
    """
    Orchestrates Batch Summarization (Phase 3).
    Implements JSONL-based persistence to allow resuming after failures.
    """

    def __init__(self, config: Dict[str, Any], llm_client: Any):
        self.config = config
        self.llm_client = llm_client
        self.extractor = ContentExtractor(self.config)
        self.builder = MarkdownReportBuilder()

    def run_batch_summarization(
        self,
        csv_path: str,
        mode: str = "region",
        filter_key: str = None,
        style: str = "intel_brief",
    ) -> List[ReportArtifact]:
        logger.info(f"Starting Batch Summarization (Mode: {mode}, Style: {style})...")

        # 1. Setup Checkpoint File
        # We create a checkpoint file in the same directory as the input CSV
        base_dir = os.path.dirname(csv_path)
        checkpoint_path = os.path.join(base_dir, CHECKPOINT_FILENAME)

        # Load existing progress
        processed_cache = self._load_checkpoint(checkpoint_path)
        logger.info(f"Loaded {len(processed_cache)} articles from checkpoint.")

        # 2. Select Generator
        generator = self._get_generator(style)
        if not generator:
            logger.error(f"Unknown style: {style}")
            return []

        # 3. Load Input Metadata
        df = CSVHandler.load_as_dataframe(csv_path)
        if df.empty:
            return []

        # 4. Filter & Group
        if filter_key:
            df = df[df[mode].astype(str).str.contains(filter_key, case=False, na=False)]

        grouped = df.groupby(mode)
        generated_artifacts = []

        # 5. Processing Loop
        for group_name, group_df in grouped:
            group_name_str = str(group_name)
            logger.info(
                f"Processing Group: {group_name_str} ({len(group_df)} articles)"
            )

            group_articles: List[Article] = []

            for _, row in group_df.iterrows():
                url = row.get("url")
                if not url:
                    continue

                # Checkpoint Lookup
                if url in processed_cache:
                    # HIT: Load from cache, skip API calls
                    logger.info(f"Skipping (Cached): {url}")
                    article = processed_cache[url]
                    group_articles.append(article)
                    continue

                # MISS: Perform work
                title = row.get("title", "Unknown")
                source = row.get("source", "Unknown")

                # A. Extraction
                raw_text = self.extractor.get_text(url)

                article = Article(
                    title=title,
                    source_name=source,
                    url=url,
                    raw_content=raw_text,
                    date_collected=datetime.now(),
                )

                # B. Generation
                enriched_article = generator.generate(article)

                # Persistence Logic
                self._append_to_checkpoint(checkpoint_path, enriched_article)
                # Update local cache so we don't process duplicates in same run
                processed_cache[url] = enriched_article

                group_articles.append(enriched_article)

            # 6. Build Report for this Group
            # We build the report using ALL articles (both cached and new)
            report_title = f"{style.replace('_', ' ').title()} - {group_name_str}"

            artifact = self.builder.build_intel_brief_report(
                report_title=report_title,
                articles=group_articles,
                run_date=datetime.now(),
            )
            generated_artifacts.append(artifact)

        return generated_artifacts

    def _get_generator(self, style: str):
        if style == "intel_brief":
            return IntelBriefGenerator(self.llm_client)
        return None

    # ==========================================
    # Persistence Helpers
    # ==========================================

    def _load_checkpoint(self, path: str) -> Dict[str, Article]:
        """
        Reads the JSONL file and reconstructs Article objects.
        Returns a dict mapping URL -> Article object.
        """
        cache = {}
        if not os.path.exists(path):
            return cache

        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        # Reconstruct Article object
                        # We need to handle datetime deserialization manually
                        if "date_collected" in data and data["date_collected"]:
                            try:
                                data["date_collected"] = datetime.fromisoformat(
                                    data["date_collected"]
                                )
                            except ValueError:
                                data["date_collected"] = datetime.now()

                        article = Article(**data)
                        cache[article.url] = article
                    except json.JSONDecodeError:
                        logger.warning("Skipping corrupt line in checkpoint file.")
                        continue
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")

        return cache

    def _append_to_checkpoint(self, path: str, article: Article):
        """
        Appends a single Article object to the JSONL file.
        """
        try:
            # Convert to dict
            data = asdict(article)

            # Serialize datetime objects to string
            if isinstance(data.get("date_collected"), datetime):
                data["date_collected"] = data["date_collected"].isoformat()

            # Write line
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

        except Exception as e:
            logger.error(f"Failed to append to checkpoint: {e}")
