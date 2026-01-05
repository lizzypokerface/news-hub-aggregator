import os
import logging
from datetime import datetime
from typing import Optional

# Interfaces & Modules
from src.interfaces import BaseOrchestrator
from src.modules.config_manager import ConfigManager
# from src.modules.csv_handler import CSVHandler

# Consolidators (Phase 1 & 2)
# from src.consolidators.analysis_headline_consolidator import AnalysisHeadlineConsolidator
# from src.consolidators.mainstream_headline_consolidator import MainstreamHeadlineConsolidator

# Reporters (Presentation Layer)
# from src.reporters.markdown_report_builder import MarkdownReportBuilder

logger = logging.getLogger(__name__)


class Orchestrator(BaseOrchestrator):
    """
    The Director of the Production Line.
    Manages the 7-Phase manufacturing process of the Weekly News Post.
    """

    def __init__(
        self, config_path: str = "config.yaml", run_date: Optional[datetime] = None
    ):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.data

        # Workspace Context
        self.run_date = run_date or datetime.now()
        self.week_number = self.run_date.strftime("%Y-W%U")
        self.workspace_dir = os.path.join(
            self.config.get("output_directory", "outputs"), self.week_number
        )
        os.makedirs(self.workspace_dir, exist_ok=True)

        logger.info(f"Production Line Initialized: {self.workspace_dir}")

    def run(self) -> None:
        """Executes the full assembly line from Phase 1 to 7."""
        self.run_phase_1_global_overview()
        self.run_phase_2_news_etl()
        self.run_phase_3_summarization()
        self.run_phase_4_materialist_analysis()
        self.run_phase_5_global_briefing()
        self.run_phase_6_multi_lens_analysis()
        self.run_phase_7_construct_news_post()

    # ==========================================
    # Phase 1: Global Overview (Auto)
    # ==========================================
    def run_phase_1_global_overview(self):
        """
        Ingests 'Raw Material': Mainstream Headlines & Economic Data.
        Output: Mainstream Report & Economic Snapshot Report.
        """
        logger.info(">>> Phase 1: Global Overview (Mainstream + Econ) Started")

        # 1. Mainstream Headlines
        # consolidator = MainstreamHeadlineConsolidator(self.config_manager)
        # data = consolidator.consolidate()
        # builder.build_mainstream_report(data)

        # 2. Economic Snapshot
        # generator = EconomicSnapshotGenerator(self.config)
        # snapshot = generator.generate()

        logger.info("<<< Phase 1 Complete")

    # ==========================================
    # Phase 2: News ETL (Semi-Auto)
    # ==========================================
    def run_phase_2_news_etl(self):
        """
        Ingests 'Raw Material': Analysis Articles.
        Action: Scrapes articles (ETL) and consolidates headlines.
        Output: p3_articles.csv & Analysis Headlines Report.
        """
        logger.info(">>> Phase 2: News ETL (Analysis Ingestion) Started")

        # 1. Run ETL (Link Collection -> Scrape)
        # etl_service = NewsETLService(self.config, self.workspace_dir)
        # etl_service.run_collection()

        # 2. Consolidate Results
        # csv_path = os.path.join(self.workspace_dir, "p3_articles_with_regions.csv")
        # consolidator = AnalysisHeadlineConsolidator(csv_path)
        # data = consolidator.consolidate()
        # builder.build_analysis_report(data)

        logger.info("<<< Phase 2 Complete")

    # ==========================================
    # Phase 3: Summarization (Auto)
    # ==========================================
    def run_phase_3_summarization(self):
        """
        Refines 'Raw Material' into 'Intermediate Product'.
        Action: Generates summaries for all collected analysis articles.
        Output: /Summaries/ folder populated.
        """
        logger.info(">>> Phase 3: Batch Summarization Started")

        # summariser = NewsSummariser(self.config, self.workspace_dir)
        # summariser.summarize_all_regions()

        logger.info("<<< Phase 3 Complete")

    # ==========================================
    # Phase 4: Materialist Analysis (Auto)
    # ==========================================
    def run_phase_4_materialist_analysis(self):
        """
        Refines 'Summaries' into 'Materialist Analysis'.
        Action: Applies Historical Materialist lens to regional summaries.
        Output: Materialist Analysis Report.
        """
        logger.info(">>> Phase 4: Materialist Analysis Started")

        # analyst = MaterialistAnalyst(self.config, self.workspace_dir)
        # analysis = analyst.analyze_regions()
        # builder.build_materialist_report(analysis)

        logger.info("<<< Phase 4 Complete")

    # ==========================================
    # Phase 5: Global Briefing (Auto)
    # ==========================================
    def run_phase_5_global_briefing(self):
        """
        Synthesizes 'Intermediate Products' (P1, P2, P4) into a Narrative.
        Action: Combines Mainstream, Econ, and Materialist analysis into a briefing.
        Output: Global Briefing Report.
        """
        logger.info(">>> Phase 5: Global Briefing Synthesis Started")

        # synthesizer = GlobalBriefingSynthesizer(self.workspace_dir)
        # briefing = synthesizer.create_briefing()
        # builder.build_briefing_report(briefing)

        logger.info("<<< Phase 5 Complete")

    # ==========================================
    # Phase 6: Multi-Lens Analysis (Auto)
    # ==========================================
    def run_phase_6_multi_lens_analysis(self):
        """
        Synthesizes 'Intermediate Products' into a Comparative Analysis.
        Action: Identifies contradictions between Mainstream (P1) and Analysis (P2).
        Output: Multi-Lens Analysis Report.
        """
        logger.info(">>> Phase 6: Multi-Lens Analysis Started")

        # lens_analyst = MultiLensSynthesizer(self.workspace_dir)
        # report = lens_analyst.compare_narratives()
        # builder.build_multilens_report(report)

        logger.info("<<< Phase 6 Complete")

    # ==========================================
    # Phase 7: Final Assembly (Auto)
    # ==========================================
    def run_phase_7_construct_news_post(self):
        """
        Assembles 'Final Product'.
        Action: Compiles P2, P5, and P6 artifacts into the final Markdown post.
        Output: Weekly_News_Post_YYYY-MM-DD.md
        """
        logger.info(">>> Phase 7: Final News Post Construction Started")

        # publisher = PublicationService(self.workspace_dir)
        # publisher.assemble_post()

        logger.info("<<< Phase 7 Complete. Production Line Finished.")

    # ==========================================
    # Helpers
    # ==========================================

    def _save_report(self, content: str, filename: str):
        """
        Writes a file to the active Weekly Workspace.
        """
        output_path = os.path.join(self.workspace_dir, filename)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Report saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save report {filename}: {e}")
