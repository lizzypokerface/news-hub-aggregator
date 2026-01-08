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
    GlobalBriefing,
    MultiLensAnalysis,
    MainstreamNarrative,
)
from reporters.markdown_formatter import MarkdownFormatter

logger = logging.getLogger(__name__)


class MarkdownReportBuilder:
    """
    Presentation Layer.
    Converts internal Data Models into formatted Markdown strings.
    Uses MarkdownFormatter for styling.
    """

    def build_consolidated_analysis_headlines_report(
        self, data: AnalysisHeadlines, run_date: datetime
    ) -> ReportArtifact:
        logger.info("Building analysis headlines report for: %s", run_date)
        date_str = run_date.strftime("%Y-%m-%d")
        title = f"Consolidated Analysis Headlines ({date_str})"
        filename = f"{date_str}-analysis_headlines.md"

        md_buffer = []
        md_buffer.append(MarkdownFormatter.h1(title))
        md_buffer.append(f"*Generated on {run_date.isoformat()}*")
        md_buffer.append("---")

        if not data.source_groups:
            md_buffer.append("> No analysis data found.")
            return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

        for source in data.source_groups:
            content_block = MarkdownFormatter.bullet_list(source.titles)
            dropdown = MarkdownFormatter.create_dropdown(
                title=f"{source.source_name} ({len(source.titles)})",
                content=content_block,
            )
            md_buffer.append(dropdown)

        return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

    def build_consolidated_mainstream_headlines_report(
        self, data: MainstreamHeadlines, run_date: datetime
    ) -> ReportArtifact:
        logger.info("Building mainstream headlines report for: %s", run_date)
        date_str = run_date.strftime("%Y-%m-%d")
        title = f"Consolidated Mainstream Headlines ({date_str})"
        filename = f"{date_str}-mainstream_headlines.md"

        md_buffer = []
        md_buffer.append(MarkdownFormatter.h1(title))
        md_buffer.append(f"*Generated on {run_date.isoformat()}*")
        md_buffer.append("---")

        if not data.entries:
            md_buffer.append("> No mainstream data found.")
            return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

        for entry in data.entries:
            display_title = f"{entry.source_name} [{entry.source_type.upper()}]"
            # Logic: Use raw content list or string
            if entry.source_type == "youtube":
                inner_content = entry.content
            else:
                inner_content = entry.content[0] if entry.content else "No content."

            dropdown = MarkdownFormatter.create_dropdown(
                title=display_title, content=inner_content
            )
            md_buffer.append(dropdown)

        return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

    def build_materialist_analysis_report(
        self, data: MaterialistAnalyses, run_date: datetime
    ) -> ReportArtifact:
        date_str = run_date.strftime("%Y-%m-%d")
        title = f"Materialist Analysis Report ({date_str})"
        filename = f"{date_str}-materialist_analysis.md"

        md_buffer = []
        md_buffer.append(MarkdownFormatter.h1(title))
        md_buffer.append(f"*Generated on {run_date.isoformat()}*")
        md_buffer.append("---")

        if not data.entries:
            md_buffer.append("> No materialist analyses generated.")
            return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

        for entry in data.entries:
            md_buffer.append(MarkdownFormatter.h1(entry.region))
            md_buffer.append(entry.analysis)
            md_buffer.append("---")

        return ReportArtifact(content="\n\n".join(md_buffer), filename=filename)

    def build_geopolitical_ledger_report(
        self, data: GeopoliticalLedger
    ) -> ReportArtifact:
        date_str = data.date.strftime("%Y-%m-%d")
        filename = f"{date_str}-global_economic_snapshot.md"

        md_buffer = []
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
        date_str = run_date.strftime("%Y-%m-%d")
        filename = f"{date_str}-{report_title}.md"

        md_buffer = []
        md_buffer.append(MarkdownFormatter.h1(report_title))

        for article in articles:
            md_buffer.append(MarkdownFormatter.h2(article.title))
            md_buffer.append(f"**Collected at:** {article.date_collected}")
            md_buffer.append("")
            md_buffer.append(f"**Source:** {article.source}")
            md_buffer.append("")
            md_buffer.append(f"**URL:** {article.url}")
            md_buffer.append("")

            content = article.summary if article.summary else "_No summary generated_"
            md_buffer.append(content)

            md_buffer.append("---")
            md_buffer.append("")

        return ReportArtifact(content="\n".join(md_buffer), filename=filename)

    def build_global_briefing_report(self, briefing: GlobalBriefing) -> ReportArtifact:
        date_str = briefing.date.strftime("%Y-%m-%d")
        filename = f"{date_str}-global_briefing.md"

        md_buffer = []
        md_buffer.append(
            MarkdownFormatter.h1(f"Global Strategic Briefing ({date_str})")
        )
        md_buffer.append(
            "> **Synthesis of:** Mainstream, Analysis, Economic, and Materialist Intelligence."
        )
        md_buffer.append("---")
        md_buffer.append("")

        if not briefing.entries:
            md_buffer.append("> No briefing generated.")
            return ReportArtifact(content="\n".join(md_buffer), filename=filename)

        for entry in briefing.entries:
            md_buffer.append(MarkdownFormatter.h2(entry.region))

            md_buffer.append("**Mainstream Narrative:**")
            # Use Formatter to handle blockquote formatting safely
            md_buffer.append(MarkdownFormatter.blockquote(entry.mainstream_narrative))
            md_buffer.append("")

            md_buffer.append("**Strategic Analysis:**")
            md_buffer.append(entry.strategic_analysis)

            md_buffer.append("")
            md_buffer.append("---")
            md_buffer.append("")

        return ReportArtifact(content="\n".join(md_buffer), filename=filename)

    def build_multi_lens_report(self, data: MultiLensAnalysis) -> ReportArtifact:
        date_str = data.date.strftime("%Y-%m-%d")
        filename = f"{date_str}-multi_lens_analysis.md"

        md_buffer = []
        md_buffer.append(
            MarkdownFormatter.h1(f"Multi-Lens Strategic Analysis ({date_str})")
        )
        md_buffer.append(
            "> **Methodology:** Refracting global events through 9 distinct ideological lenses."
        )
        md_buffer.append("---")
        md_buffer.append("")

        if not data.entries:
            md_buffer.append("> No analysis generated.")
            return ReportArtifact(content="\n".join(md_buffer), filename=filename)

        for entry in data.entries:
            md_buffer.append(MarkdownFormatter.h2(entry.region))

            for lens in entry.lenses:
                dropdown = MarkdownFormatter.create_dropdown(
                    title=f"Lens: {lens.lens_name}", content=lens.analysis_text
                )
                md_buffer.append(dropdown)

            md_buffer.append("")
            md_buffer.append("---")
            md_buffer.append("")

        return ReportArtifact(content="\n".join(md_buffer), filename=filename)

    def build_mainstream_narrative_report(
        self, narrative: MainstreamNarrative
    ) -> ReportArtifact:
        date_str = narrative.date.strftime("%Y-%m-%d")
        filename = f"{date_str}-mainstream_narrative.md"

        md_buffer = []
        md_buffer.append(
            MarkdownFormatter.h1(f"Mainstream Global Narrative ({date_str})")
        )
        md_buffer.append(
            "> **Context:** A synthesis of major global headlines and official reporting."
        )
        md_buffer.append("---")
        md_buffer.append("")

        if not narrative.entries:
            md_buffer.append("> No mainstream narrative generated.")
            return ReportArtifact(content="\n".join(md_buffer), filename=filename)

        for entry in narrative.entries:
            md_buffer.append(MarkdownFormatter.h2(entry.region))
            md_buffer.append(entry.summary_text)
            md_buffer.append("")
            md_buffer.append("---")
            md_buffer.append("")

        return ReportArtifact(content="\n".join(md_buffer), filename=filename)
