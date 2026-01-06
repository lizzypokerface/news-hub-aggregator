import logging
from datetime import datetime
from typing import List
from interfaces.models import (
    AnalysisHeadlines,
    MainstreamHeadlines,
    MaterialistAnalyses,
    GeopoliticalLedger,
    ReportArtifact,
    Article,
)

logger = logging.getLogger(__name__)


class MarkdownReportBuilder:
    """
    Presentation Layer.
    Converts internal Data Models into formatted Markdown strings.
    Returns a ReportArtifact containing content and filename.
    """

    def build_consolidated_analysis_headlines_report(
        self, data: AnalysisHeadlines, run_date: datetime
    ) -> ReportArtifact:
        """
        Builds the report for Analysis Headlines.
        """
        logger.info(
            "Building consolidated analysis headlines report for date: %s", run_date
        )
        date_str = run_date.strftime("%Y-%m-%d")
        title = f"Consolidated Analysis Headlines ({date_str})"
        filename = f"{date_str}-consolidated_analysis_headlines_report.md"

        md_buffer = []
        md_buffer.append(self._h1(title))
        md_buffer.append(f"*Generated on {run_date.isoformat()}*")
        md_buffer.append("---")

        if not data.source_groups:
            logger.warning("No analysis data found for date: %s", run_date)
            md_buffer.append("> No analysis data found.")
            return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

        for source in data.source_groups:
            logger.debug(
                "Processing source: %s with %d titles",
                source.source_name,
                len(source.titles),
            )
            content_block = self._format_list(source.titles)
            dropdown = self._create_dropdown(
                title=f"{source.source_name} ({len(source.titles)})",
                content=content_block,
            )
            md_buffer.append(dropdown)

        logger.info("Finished building analysis headlines report: %s", filename)
        return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

    def build_consolidated_mainstream_headlines_report(
        self, data: MainstreamHeadlines, run_date: datetime
    ) -> ReportArtifact:
        """
        Builds the report for Mainstream Headlines.
        Signature matches the new Consolidator return type.
        """
        logger.info(
            "Building consolidated mainstream headlines report for date: %s", run_date
        )
        date_str = run_date.strftime("%Y-%m-%d")
        title = f"Consolidated Mainstream Headlines ({date_str})"
        filename = f"{date_str}-consolidated_mainstream_headlines_report.md"

        md_buffer = []
        md_buffer.append(self._h1(title))
        md_buffer.append(f"*Generated on {run_date.isoformat()}*")
        md_buffer.append("---")

        if not data.entries:
            logger.warning("No mainstream data found for date: %s", run_date)
            md_buffer.append("> No mainstream data found.")
            return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

        for entry in data.entries:
            display_title = f"{entry.source_name} [{entry.source_type.upper()}]"
            logger.debug(
                "Processing mainstream entry: %s of type %s",
                entry.source_name,
                entry.source_type,
            )
            if entry.source_type == "youtube":
                inner_content = entry.content
            else:
                text = entry.content[0] if entry.content else "No content."
                inner_content = text

            dropdown = self._create_dropdown(title=display_title, content=inner_content)
            md_buffer.append(dropdown)

        logger.info("Finished building mainstream headlines report: %s", filename)
        return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

    def build_materialist_analysis_report(
        self, data: MaterialistAnalyses, run_date: datetime
    ) -> ReportArtifact:
        """
        Builds the Materialist Analysis Report.
        Format:
        # Materialist Analysis Report
        ## Region
        Text
        """
        date_str = run_date.strftime("%Y-%m-%d")
        title = f"Materialist Analysis Report ({date_str})"
        filename = f"{date_str}-materialist_analysis_report.md"

        md_buffer = []
        md_buffer.append(self._h1(title))
        md_buffer.append(f"*Generated on {run_date.isoformat()}*")
        md_buffer.append("---")

        if not data.entries:
            md_buffer.append("> No materialist analyses generated.")
            return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

        # Iterate through the entries
        for entry in data.entries:
            md_buffer.append(self._h1(entry.region))
            md_buffer.append(entry.analysis)
            md_buffer.append("---")

        return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

    def build_geopolitical_ledger_report(
        self, data: GeopoliticalLedger
    ) -> ReportArtifact:
        """
        Builds the Global Economic Snapshot Report.
        Since the generator outputs a formatted table with a title, we mostly pass it through.
        """
        date_str = data.date.strftime("%Y-%m-%d")
        filename = f"{date_str}-global_economic_snapshot.md"

        md_buffer = []

        # The content from the generator already includes a title and the table.
        # We just add a generation timestamp metadata block at the top.
        md_buffer.append("> **Generated Artifact:** Geopolitical Ledger")
        md_buffer.append(f"> **Date:** {data.date.isoformat()}")
        md_buffer.append("---")
        md_buffer.append("")

        if not data.ledger_content or "Error" in data.ledger_content:
            md_buffer.append("> **Error:** No data generated.")
        else:
            md_buffer.append(data.ledger_content)

        return ReportArtifact(content="\n".join(md_buffer), filename=filename)

    def build_summary_report(
        self, report_title: str, articles: List[Article], run_date: datetime
    ) -> ReportArtifact:
        """
        Builds a stacked report of summaries.
        """
        date_str = run_date.strftime("%Y-%m-%d")
        filename = f"{date_str}-{report_title}.md"

        md_buffer = []

        md_buffer.append(self._h1(report_title))

        for article in articles:
            md_buffer.append(self._h2(article.title))
            md_buffer.append(f"**Source:** {article.source}")
            md_buffer.append(f"**URL:** {article.url}")
            md_buffer.append(f"**Collected:** {article.date_collected}")
            md_buffer.append("")

            # Use the new summary field, providing a fallback if None
            content = article.summary if article.summary else "_No summary generated_"
            md_buffer.append(content)

            md_buffer.append("---")
            md_buffer.append("")

        return ReportArtifact(content="\n".join(md_buffer), filename=filename)

    # ==========================================
    # Private Helpers
    # ==========================================

    def _h1(self, text: str) -> str:
        return f"# {text}"

    def _h2(self, text: str) -> str:
        return f"## {text}"

    def _blockquote(self, text: str) -> str:
        return f"> {text}"

    def _format_list(self, items: List[str]) -> str:
        if not items:
            return "_No items_"
        return "\n".join([f"- {item}" for item in items])

    def _create_dropdown(self, title: str, content: str) -> str:
        return f"""
<details>
<summary><b>{title}</b></summary>

{content}

</details>
"""
