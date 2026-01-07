import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd

# Core Interfaces & Config
from interfaces import BaseOrchestrator
from modules.llm_client import LLMClient
from src.modules.csv_handler import CSVHandler

# Services
from services.analysis_etl_service import AnalysisETLService
from services.summarization_service import SummarizationService

# Consolidators
from consolidators.mainstream_headline_consolidator import (
    MainstreamHeadlineConsolidator,
)
from consolidators.analysis_headline_consolidator import (
    AnalysisHeadlineConsolidator,
)

# Generators
from generators.geopolitical_ledger_generator import GeopoliticalLedgerGenerator
from generators.materialist_analysis_generator import MaterialistAnalysisGenerator

# Synthesizers
from synthesizers.mainstream_news_synthesizer import MainstreamNewsSynthesizer
from synthesizers.global_briefing_synthesizer import GlobalBriefingSynthesizer
from synthesizers.multi_lens_synthesizer import MultiLensSynthesizer

# Reporters
from reporters.markdown_report_builder import MarkdownReportBuilder
# from src.reporters.news_post_builder import NewsPostBuilder (Upcoming)

# Data Models
from interfaces.models import (
    GlobalBriefing,
    MultiLensAnalysis,
    ReportArtifact,
)

logger = logging.getLogger(__name__)


class WeeklyIntelOrchestrator(BaseOrchestrator):
    """
    The Manufacturing Plant.
    Coordinates the end-to-end production of the Weekly Intelligence Briefing.

    Phases:
    0. Setup & Workspace
    1. Global Overview (Mainstream + Econ)
    2. News ETL (Analysis Ingestion)
    3. Summarization (Batch Processing)
    4. Materialist Analysis (Deep Dive)
    5. Global Briefing (Synthesis)
    6. Multi-Lens Analysis (Refraction)
    7. Final Assembly (News Post)
    """

    def __init__(
        self,
        config: Dict[str, Any],
        llm_client: LLMClient,
        run_date: Optional[datetime] = None,
    ):
        # Setup
        self.config = config
        self.llm_client = llm_client
        self.run_date = run_date or datetime.now()

        # Workspace: outputs/W{Week}-{YYYY-MM-DD}
        week_str = self.run_date.strftime("W%U-%Y-%m-%d")
        base_output = self.config.get("output_directory", "outputs")
        self.workspace_dir = os.path.join(base_output, week_str)
        os.makedirs(self.workspace_dir, exist_ok=True)

        # Pipeline State
        self.global_briefing: Optional[GlobalBriefing] = None
        self.multi_lens_analysis: Optional[MultiLensAnalysis] = None
        self.analysis_articles_df: pd.DataFrame = None

        logger.info(f"Intel Pipeline Initialized. Workspace: {self.workspace_dir}")

    def run(self) -> None:
        """Executes the full manufacturing sequence."""
        try:
            self.run_phase_1_global_overview()
            self.run_phase_2_news_etl()
            self.run_phase_3_summarization()
            self.run_phase_4_materialist_analysis()
            self.run_phase_5_global_briefing()
            self.run_phase_6_multi_lens_analysis()
            self.run_phase_7_final_assembly()
            logger.info(">>> Pipeline Execution Successful.")
        except Exception as e:
            logger.critical(f"Pipeline Halted: {e}", exc_info=True)
            raise

    # ==========================================
    # Phase 1: Global Overview (The Baseline)
    # ==========================================
    def run_phase_1_global_overview(self):
        logger.info(">>> Phase 1: Global Overview Started")
        builder = MarkdownReportBuilder()

        # 1.1 Mainstream Headlines (Raw)
        consolidator = MainstreamHeadlineConsolidator(self.config)
        ms_data = consolidator.consolidate()
        artifact = builder.build_consolidated_mainstream_headlines_report(
            ms_data, self.run_date
        )
        self._save_report(artifact)

        # 1.2 Mainstream Narrative (Synthesis)
        # We read the report we just saved to ensure consistency
        ms_content = self._read_file(artifact.filename)
        synthesizer = MainstreamNewsSynthesizer(self.llm_client)
        narrative = synthesizer.synthesize(mainstream_content=ms_content)
        artifact = builder.build_mainstream_narrative_report(narrative)
        self._save_report(artifact)

        # 1.3 Geopolitical Ledger (Econ Snapshot)
        ledger_gen = GeopoliticalLedgerGenerator(self.llm_client)
        ledger_data = ledger_gen.generate(self.run_date)
        artifact = builder.build_geopolitical_ledger_report(ledger_data)
        self._save_report(artifact)

    # ==========================================
    # Phase 2: News ETL (The Raw Material)
    # ==========================================
    def run_phase_2_news_etl(self):
        logger.info(">>> Phase 2: News ETL Started")

        # 2.1 Run Analysis ETL Service
        # We pass the specific workspace_dir so CSVs land in the correct week folder
        etl_service = AnalysisETLService(self.config, self.workspace_dir)
        final_csv_path = etl_service.run_etl()

        if not final_csv_path or not os.path.exists(final_csv_path):
            logger.warning(
                "ETL Phase failed or produced no data. Skipping report generation."
            )
            return

        # 2.2 Consolidate Analysis Headlines (Report Generation)
        # We use the path returned by the service
        consolidator = AnalysisHeadlineConsolidator(final_csv_path)
        data = consolidator.consolidate()
        builder = MarkdownReportBuilder()
        artifact = builder.build_consolidated_analysis_headlines_report(
            data, self.run_date
        )
        self._save_report(artifact)

        # 2.3 Load Data into Memory for downstream phases
        try:
            self.analysis_articles_df = CSVHandler.load_as_dataframe(final_csv_path)
            logger.info(
                f"Loaded {len(self.analysis_articles_df)} articles into memory."
            )
        except Exception as e:
            logger.error(f"Failed to load articles DataFrame: {e}")

        logger.info("<<< Phase 2 Complete")

    # ==========================================
    # Phase 3: Summarization (The Intermediate)
    # ==========================================
    def run_phase_3_summarization(self):
        logger.info(">>> Phase 3: Batch Summarization Started")

        csv_path = os.path.join(
            self.config.get("output_directory", "outputs"),
            "p3_articles_with_regions.csv",
        )

        service = SummarizationService(self.config, self.llm_client)

        # Run Batch Processing (Region Mode)
        artifacts = service.run_batch_summarization(
            csv_path=csv_path, mode="region", style="intel_brief"
        )

        # Save summaries to 'Summaries' subfolder
        summaries_dir = os.path.join(self.workspace_dir, "Summaries")
        os.makedirs(summaries_dir, exist_ok=True)

        for art in artifacts:
            # We treat these as reports too, but save to subfolder
            path = os.path.join(summaries_dir, art.filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(art.content)
            logger.info(f"Summary Saved: {art.filename}")

    # ==========================================
    # Phase 4: Materialist Analysis (The Deep Dive)
    # ==========================================
    def run_phase_4_materialist_analysis(self):
        logger.info(">>> Phase 4: Materialist Analysis Started")

        summaries_dir = os.path.join(self.workspace_dir, "Summaries")
        if not os.path.exists(summaries_dir):
            logger.warning("No summaries folder found. Skipping Phase 4.")
            return

        generator = MaterialistAnalysisGenerator(self.llm_client)
        data = generator.generate(input_dir=summaries_dir)

        builder = MarkdownReportBuilder()
        artifact = builder.build_materialist_analysis_report(data, self.run_date)
        self._save_report(artifact)

    # ==========================================
    # Phase 5: Global Briefing (The Synthesis)
    # ==========================================
    def run_phase_5_global_briefing(self):
        logger.info(">>> Phase 5: Global Briefing Synthesis Started")

        # 5.1 Load Inputs using naming conventions
        date_str = self.run_date.strftime("%Y-%m-%d")

        ms_content = self._read_file(f"{date_str}-mainstream_headlines.md")
        an_content = self._read_file(f"{date_str}-analysis_headlines.md")
        ec_content = self._read_file(f"{date_str}-global_economic_snapshot.md")
        mat_content = self._read_file(f"{date_str}-materialist_analysis.md")

        # 5.2 Synthesize
        synthesizer = GlobalBriefingSynthesizer(self.llm_client)
        self.global_briefing = synthesizer.synthesize(
            mainstream_text=ms_content,
            analysis_text=an_content,
            materialist_text=mat_content,
            econ_text=ec_content,
        )

        # 5.3 Report
        builder = MarkdownReportBuilder()
        artifact = builder.build_global_briefing_report(self.global_briefing)
        self._save_report(artifact)

    # ==========================================
    # Phase 6: Multi-Lens Analysis (The Refraction)
    # ==========================================
    def run_phase_6_multi_lens_analysis(self):
        logger.info(">>> Phase 6: Multi-Lens Analysis Started")

        date_str = self.run_date.strftime("%Y-%m-%d")

        # Inputs (Same as Phase 5)
        ms_content = self._read_file(f"{date_str}-mainstream_headlines.md")
        an_content = self._read_file(f"{date_str}-analysis_headlines.md")
        ec_content = self._read_file(f"{date_str}-global_economic_snapshot.md")
        mat_content = self._read_file(f"{date_str}-materialist_analysis.md")

        synthesizer = MultiLensSynthesizer(self.llm_client)
        self.multi_lens_analysis = synthesizer.synthesize(
            mainstream_text=ms_content,
            analysis_text=an_content,
            materialist_text=mat_content,
            econ_text=ec_content,
        )

        builder = MarkdownReportBuilder()
        artifact = builder.build_multi_lens_report(self.multi_lens_analysis)
        self._save_report(artifact)

    # ==========================================
    # Phase 7: Final Assembly (The Product)
    # ==========================================
    def run_phase_7_final_assembly(self):
        logger.info(">>> Phase 7: Final Assembly Started")

        if not self.global_briefing or not self.multi_lens_analysis:
            logger.warning(
                "Missing Briefing or Lens objects. Cannot assemble final post."
            )
            return

        # WIP: NewsPostBuilder logic
        # builder = NewsPostBuilder()
        # post_artifact = builder.assemble_weekly_post(
        #     briefing=self.global_briefing,
        #     lenses=self.multi_lens_analysis,
        #     run_date=self.run_date
        # )
        # self._save_report(post_artifact)

        logger.info("Final Assembly Logic is WIP. Check artifacts in workspace.")

    # ==========================================
    # Helpers
    # ==========================================
    def _save_report(self, artifact: ReportArtifact):
        """Saves a ReportArtifact to the workspace."""
        path = os.path.join(self.workspace_dir, artifact.filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(artifact.content)
            logger.info(f"Saved: {artifact.filename}")
        except Exception as e:
            logger.error(f"Failed to save {artifact.filename}: {e}")

    def _read_file(self, filename: str) -> str:
        """Reads a file from the workspace."""
        path = os.path.join(self.workspace_dir, filename)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
        logger.warning(f"File not found: {filename}")
        return ""
