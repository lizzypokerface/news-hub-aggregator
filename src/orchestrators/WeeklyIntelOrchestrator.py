import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from interfaces import BaseOrchestrator

from legacy_modules.llm_client import LLMClient
from legacy_modules.csv_handler import CSVHandler

from services.analysis_etl_service import AnalysisETLService
from services.summarization_service import SummarizationService

from consolidators.mainstream_headline_consolidator import (
    MainstreamHeadlineConsolidator,
)
from consolidators.analysis_headline_consolidator import (
    AnalysisHeadlineConsolidator,
)

from generators.geopolitical_ledger_generator import GeopoliticalLedgerGenerator
from generators.materialist_analysis_generator import MaterialistAnalysisGenerator

from synthesizers.mainstream_news_synthesizer import MainstreamNewsSynthesizer
from synthesizers.global_briefing_synthesizer import GlobalBriefingSynthesizer
from synthesizers.multi_lens_synthesizer import MultiLensSynthesizer

from reporters.markdown_report_builder import MarkdownReportBuilder
from reporters.news_post_builder import NewsPostBuilder

from managers.workspace_manager import WorkspaceManager

from interfaces.models import (
    GlobalBriefing,
    MultiLensAnalysis,
    RegionalBriefingEntry,
    MultiLensRegionEntry,
    LensAnalysis,
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
        self.config = config
        self.llm_client = llm_client
        self.run_date = run_date or datetime.now()

        # Workspace: outputs/W{Week}-{YYYY-MM-DD}
        week_str = self.run_date.strftime("W%U-%Y-%m-%d")
        base_output = self.config.get("output_directory", "outputs")
        self.workspace_path = os.path.join(base_output, week_str)

        # The Manager handles all State and IO
        self.workspace = WorkspaceManager(self.workspace_path)

        logger.info(f"Intel Pipeline Initialized. Workspace: {self.workspace_path}")

    def run(self) -> None:
        """Executes the full manufacturing sequence."""
        try:
            self.run_phase_1_global_overview()
            # self.run_phase_2_news_etl()
            # self.run_phase_3_summarization()
            # self.run_phase_4_materialist_analysis()
            # self.run_phase_5_global_briefing()
            # self.run_phase_6_multi_lens_analysis()
            # self.run_phase_7_final_assembly()
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

        # --- 1.1 Mainstream Headlines (Raw) ---
        KEY_MS_HEADLINES = "p1_mainstream_headlines"

        if self.workspace.has_checkpoint("p1_mainstream"):
            logger.info("   [SKIP] 1.1 Mainstream Headlines found in checkpoint.")

        else:
            # Do Work
            consolidator = MainstreamHeadlineConsolidator(self.config)
            ms_data = consolidator.consolidate()
            # Save Checkpoint
            self.workspace.save_checkpoint(KEY_MS_HEADLINES, ms_data)
            # Save Report
            artifact = builder.build_consolidated_mainstream_headlines_report(
                ms_data, self.run_date
            )
            self.workspace.save_report(artifact.filename, artifact.content)
            ms_report_filename = artifact.filename  # Update var if needed

        # --- 1.2 Mainstream Narrative (Synthesis) ---
        KEY_MS_NARRATIVE = "p1_mainstream_narrative"

        if self.workspace.has_checkpoint(KEY_MS_NARRATIVE):
            logger.info("   [SKIP] 1.2 Mainstream Narrative found in checkpoint.")
        else:
            # Load Input (The text report from 1.1)
            ms_content = self.workspace.load_report(ms_report_filename)

            if ms_content:
                # Do Work
                synthesizer = MainstreamNewsSynthesizer(self.llm_client)
                narrative = synthesizer.synthesize(mainstream_content=ms_content)
                # Save Checkpoint
                self.workspace.save_checkpoint(KEY_MS_NARRATIVE, narrative)
                # Save Report
                artifact = builder.build_mainstream_narrative_report(narrative)
                self.workspace.save_report(artifact.filename, artifact.content)
            else:
                logger.warning(
                    "   [FAIL] Prerequisite Mainstream Headlines report not found. Skipping 1.2."
                )

        # --- 1.3 Geopolitical Ledger (Econ Snapshot) ---
        KEY_GEO_LEDGER = "p1_geopolitical_ledger"

        if self.workspace.has_checkpoint(KEY_GEO_LEDGER):
            logger.info("   [SKIP] 1.3 Geopolitical Ledger found in checkpoint.")
        else:
            # Do Work
            ledger_gen = GeopoliticalLedgerGenerator(self.llm_client)
            ledger_data = ledger_gen.generate(self.run_date)
            # Save Checkpoint
            self.workspace.save_checkpoint(KEY_GEO_LEDGER, ledger_data)
            # Save Report
            artifact = builder.build_geopolitical_ledger_report(ledger_data)
            self.workspace.save_report(artifact.filename, artifact.content)

        logger.info("<<< Phase 1 Complete")

    # ==========================================
    # Phase 2: News ETL (The Raw Material)
    # ==========================================
    def run_phase_2_news_etl(self):
        logger.info(">>> Phase 2: News ETL Started")

        # FUTURE WORK: Refactor to use WorkspaceManager for checkpointing.
        # Currently, AnalysisETLService handles its own file persistence and backups internally.

        # 2.1 Run Analysis ETL Service
        etl_service = AnalysisETLService(self.config, self.workspace_path)
        final_csv_path = etl_service.run_etl()

        if not final_csv_path or not os.path.exists(final_csv_path):
            logger.warning(
                "ETL Phase failed or produced no data. Skipping report generation."
            )
            return

        # 2.2 Consolidate Analysis Headlines (Report Generation)
        consolidator = AnalysisHeadlineConsolidator(final_csv_path)
        data = consolidator.consolidate()
        builder = MarkdownReportBuilder()
        artifact = builder.build_consolidated_analysis_headlines_report(
            data, self.run_date
        )
        self.workspace.save_report(artifact.filename, artifact.content)

        logger.info("<<< Phase 2 Complete")

    # ==========================================
    # Phase 3: Summarization (The Intermediate)
    # ==========================================
    def run_phase_3_summarization(self):
        logger.info(">>> Phase 3: Batch Summarization Started")

        # FUTURE WORK: Refactor to use WorkspaceManager for consistency.
        # Currently, SummarizationService manages its own granular JSONL checkpointing logic
        # (stage_04_enriched_articles_summarized.jsonl) instead of using the central manager.

        # Resolve Input Path
        csv_filename = "stage_03_enriched_articles_regions.csv"
        csv_path = self.workspace.get_file_path(csv_filename)

        if not os.path.exists(csv_path):
            logger.warning(
                f"   [FAIL] Input CSV not found at {csv_path}. Skipping Phase 3."
            )
            return

        # 3.1 Run Summarization Service
        # The service manages its own granular checkpointing (JSONL) internally
        service = SummarizationService(self.config, self.llm_client)

        artifacts = service.run_batch_summarization(
            csv_path=csv_path, mode="region", style="intel_brief"
        )

        if not artifacts:
            logger.info("   [INFO] No summaries generated.")
            return

        # Save Outputs
        for art in artifacts:
            relative_path = os.path.join("summaries", art.filename)
            self.workspace.save_report(relative_path, art.content)

        logger.info("<<< Phase 3 Complete")

    # ==========================================
    # Phase 4: Materialist Analysis (The Deep Dive)
    # ==========================================
    def run_phase_4_materialist_analysis(self):
        logger.info(">>> Phase 4: Materialist Analysis Started")

        KEY_MAT_ANALYSIS = "p4_materialist_analysis"

        if self.workspace.has_checkpoint(KEY_MAT_ANALYSIS):
            logger.info("   [SKIP] 4.1 Materialist Analysis found in checkpoint.")
            return
        # Check Inputs
        summaries_dir = os.path.join(self.workspace.workspace_dir, "summaries")
        if not os.path.exists(summaries_dir):
            logger.warning("   [FAIL] No 'summaries' folder found. Cannot run Phase 4.")
            return
        # Do Work
        generator = MaterialistAnalysisGenerator(self.llm_client)
        data = generator.generate(input_dir=summaries_dir)
        # Save Checkpoint
        self.workspace.save_checkpoint(KEY_MAT_ANALYSIS, data)
        # Save Report
        builder = MarkdownReportBuilder()
        artifact = builder.build_materialist_analysis_report(data, self.run_date)
        self.workspace.save_report(artifact.filename, artifact.content)

    # ==========================================
    # Phase 5: Global Briefing (The Synthesis)
    # ==========================================
    def run_phase_5_global_briefing(self):
        logger.info(">>> Phase 5: Global Briefing Synthesis Started")

        KEY_GLOBAL_BRIEFING = "p5_global_briefing"

        # Check for Checkpoint
        if self.workspace.has_checkpoint(KEY_GLOBAL_BRIEFING):
            logger.info("   [SKIP] 5.1 Global Briefing found in checkpoint. Loading...")
            data = self.workspace.load_checkpoint_json(KEY_GLOBAL_BRIEFING)
            if data:
                self.global_briefing = self._reconstruct_global_briefing(data)
            return

        # Load Inputs
        date_str = self.run_date.strftime("%Y-%m-%d")

        # Load reports from disk using the Workspace Manager
        ms_content = self.workspace.load_report(f"{date_str}-mainstream_narrative.md")
        an_content = self.workspace.load_report(f"{date_str}-analysis_headlines.md")
        ec_content = self.workspace.load_report(
            f"{date_str}-global_economic_snapshot.md"
        )
        mat_content = self.workspace.load_report(f"{date_str}-materialist_analysis.md")

        # Validate inputs (Optional but recommended)
        if not ms_content or not an_content or not ec_content or not mat_content:
            logger.warning(
                "   [FAIL] Critical inputs (Mainstream, Analysis, Economic, or Materialist reports) missing. Phase 5 may fail."
            )
        # Do Work
        synthesizer = GlobalBriefingSynthesizer(self.llm_client)
        self.global_briefing = synthesizer.synthesize(
            mainstream_text=ms_content,
            analysis_text=an_content,
            materialist_text=mat_content,
            econ_text=ec_content,
        )
        # Save Checkpoint
        self.workspace.save_checkpoint(KEY_GLOBAL_BRIEFING, self.global_briefing)
        # Save Report
        builder = MarkdownReportBuilder()
        artifact = builder.build_global_briefing_report(self.global_briefing)
        self.workspace.save_report(artifact.filename, artifact.content)

        logger.info("<<< Phase 5 Complete")

    # ==========================================
    # Phase 6: Multi-Lens Analysis (The Refraction)
    # ==========================================
    def run_phase_6_multi_lens_analysis(self):
        logger.info(">>> Phase 6: Multi-Lens Analysis Started")

        KEY_MULTI_LENS = "p6_multi_lens_analysis"

        # Check for Checkpoint
        if self.workspace.has_checkpoint(KEY_MULTI_LENS):
            logger.info(
                "   [SKIP] 6.1 Multi-Lens Analysis found in checkpoint. Loading..."
            )
            data = self.workspace.load_checkpoint_json(KEY_MULTI_LENS)
            if data:
                self.multi_lens_analysis = self._reconstruct_multi_lens_analysis(data)
            return

        # Load Inputs (Same as Phase 5)
        date_str = self.run_date.strftime("%Y-%m-%d")

        ms_content = self.workspace.load_report(f"{date_str}-mainstream_narrative.md")
        an_content = self.workspace.load_report(f"{date_str}-analysis_headlines.md")
        ec_content = self.workspace.load_report(
            f"{date_str}-global_economic_snapshot.md"
        )
        mat_content = self.workspace.load_report(f"{date_str}-materialist_analysis.md")

        # Do Work
        synthesizer = MultiLensSynthesizer(self.llm_client)
        self.multi_lens_analysis = synthesizer.synthesize(
            mainstream_text=ms_content,
            analysis_text=an_content,
            materialist_text=mat_content,
            econ_text=ec_content,
        )

        # Save Checkpoint
        self.workspace.save_checkpoint(KEY_MULTI_LENS, self.multi_lens_analysis)
        # Save Report
        builder = MarkdownReportBuilder()
        artifact = builder.build_multi_lens_report(self.multi_lens_analysis)
        self.workspace.save_report(artifact.filename, artifact.content)

        logger.info("<<< Phase 6 Complete")

    # ==========================================
    # Phase 7: Final Assembly (The Product)
    # ==========================================
    def run_phase_7_final_assembly(self):
        logger.info(">>> Phase 7: Final Assembly Started")

        # ----------------------------------------------
        # 1. Load Global Briefing (From Phase 5 JSON)
        # ----------------------------------------------
        gb_data = self.workspace.load_checkpoint_json("p5_global_briefing")
        if not gb_data:
            raise ValueError(
                "CRITICAL: Global Briefing checkpoint not found. Run Phase 5."
            )

        global_briefing = self._reconstruct_global_briefing(gb_data)
        logger.info("   [LOAD] Global Briefing re-hydrated from disk.")

        # ----------------------------------------------
        # 2. Load Multi-Lens Analysis (From Phase 6 JSON)
        # ----------------------------------------------
        mla_data = self.workspace.load_checkpoint_json("p6_multi_lens_analysis")
        if not mla_data:
            raise ValueError(
                "CRITICAL: Multi-Lens Analysis checkpoint not found. Run Phase 6."
            )

        multi_lens_analysis = self._reconstruct_multi_lens_analysis(mla_data)
        logger.info("   [LOAD] Multi-Lens Analysis re-hydrated from disk.")

        # ----------------------------------------------
        # 3. Load Analysis Articles
        # ----------------------------------------------
        stage_03_path = os.path.join(
            self.workspace.workspace_dir, "stage_03_enriched_articles_regions.csv"
        )

        if not os.path.exists(stage_03_path):
            raise ValueError(f"CRITICAL: Analysis CSV not found at {stage_03_path}.")

        analysis_articles_df = CSVHandler.load_as_dataframe(stage_03_path)
        logger.info(
            f"   [LOAD] Articles DataFrame loaded ({len(analysis_articles_df)} rows)."
        )

        # ----------------------------------------------
        # 4. Assemble Final Post
        # ----------------------------------------------
        logger.info("   [BUILD] Assembling final Markdown post...")

        builder = NewsPostBuilder()

        final_artifact = builder.assemble_weekly_post(
            briefing=global_briefing,
            lenses=multi_lens_analysis,
            articles_df=analysis_articles_df,
            config=self.config,
            run_date=self.run_date,
        )

        # Save the Final Product
        self.workspace.save_report(final_artifact.filename, final_artifact.content)

        logger.info(f"<<< Phase 7 Complete. Final Product: {final_artifact.filename}")

    # ==========================================
    # Reconstruction Helpers (Re-hydration)
    # ==========================================
    def _reconstruct_global_briefing(self, data: Dict[str, Any]) -> GlobalBriefing:
        """Helper to reconstruct GlobalBriefing object from JSON dictionary."""
        entries = [RegionalBriefingEntry(**e) for e in data.get("entries", [])]

        # Handle date parsing safely
        date_val = data.get("date")
        obj_date = datetime.fromisoformat(date_val) if date_val else self.run_date

        return GlobalBriefing(entries=entries, date=obj_date)

    def _reconstruct_multi_lens_analysis(
        self, data: Dict[str, Any]
    ) -> MultiLensAnalysis:
        """Helper to reconstruct MultiLensAnalysis object from JSON dictionary."""
        reconstructed_entries = []

        for entry_data in data.get("entries", []):
            # Nested list comprehension for lenses
            lenses = [LensAnalysis(**lens) for lens in entry_data.get("lenses", [])]
            reconstructed_entries.append(
                MultiLensRegionEntry(region=entry_data["region"], lenses=lenses)
            )

        # Handle date parsing safely
        date_val = data.get("date")
        obj_date = datetime.fromisoformat(date_val) if date_val else self.run_date

        return MultiLensAnalysis(entries=reconstructed_entries, date=obj_date)
