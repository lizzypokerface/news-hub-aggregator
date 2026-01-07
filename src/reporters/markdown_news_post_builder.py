import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from src.interfaces.models import (
    GlobalBriefing,
    MultiLensAnalysis,
    ReportArtifact,
)

from src.reporters.markdown_formatter import MarkdownFormatter

logger = logging.getLogger(__name__)

# Strict Region Order
REGION_HEADINGS = {
    "Global": "Global",
    "China": "China",
    "East Asia": "East Asia",
    "Singapore": "Singapore",
    "Southeast Asia": "Southeast Asia",
    "South Asia": "South Asia",
    "Central Asia": "Central Asia",
    "Russia": "Russia",
    "West Asia (Middle East)": "West Asia (Middle East)",
    "Africa": "Africa",
    "Europe": "Europe",
    "Latin America & Caribbean": "Latin America & Caribbean",
    "North America": "North America",
    "Oceania": "Oceania",
}


class NewsPostBuilder:
    """
    Phase 7 Reporter.
    Assembles the final Weekly Intelligence Post by fusing data streams.
    Uses MarkdownFormatter for standard output generation.
    """

    def assemble_weekly_post(
        self,
        briefing: GlobalBriefing,
        lenses: MultiLensAnalysis,
        articles_df: pd.DataFrame,
        config: Dict[str, Any],
        run_date: datetime,
    ) -> ReportArtifact:
        logger.info("Assembling Final Weekly News Post...")

        date_str = run_date.strftime("%Y-%m-%d")
        display_date = run_date.strftime("%d %B %Y")

        # 1. YAML Front Matter
        content = [
            "---",
            "layout: post",
            f"title:  🌏 Global Briefing | {display_date}",
            f"date:   {date_str} 08:00:00 +0800",
            "categories: weekly news",
            "---",
            "",
        ]

        # 2. Navigation Bar
        content.append(self._build_navigation())
        content.append("\n---\n")

        # 3. Process Regions
        briefing_map = {e.region: e for e in briefing.entries}
        lens_map = {e.region: e for e in lenses.entries}

        if "region" not in articles_df.columns:
            articles_df["region"] = "Unknown"
        articles_df["region"] = articles_df["region"].fillna("Unknown")

        for region_key, region_display in REGION_HEADINGS.items():
            briefing_entry = briefing_map.get(region_key)
            lens_entry = lens_map.get(region_key)
            region_articles = articles_df[articles_df["region"] == region_key].copy()

            if not briefing_entry and not lens_entry and region_articles.empty:
                continue

            # B. Header with ID
            slug = MarkdownFormatter.slugify(region_key)
            content.append(f"# {region_display} <a id='{slug}'></a>\n")

            # C. Mainstream Narrative
            if briefing_entry and briefing_entry.mainstream_narrative:
                clean_text = MarkdownFormatter.clean_text(
                    briefing_entry.mainstream_narrative
                )
                content.append(f"{clean_text}\n")

            # D. Multi-Lens Dropdowns
            if lens_entry and lens_entry.lenses:
                for lens in lens_entry.lenses:
                    clean_lens = MarkdownFormatter.clean_text(lens.analysis_text)
                    dropdown = MarkdownFormatter.create_dropdown(
                        title=f"Lens: {lens.lens_name}", content=clean_lens
                    )
                    content.append(dropdown)
                content.append("<br>\n")

            # E. Article Links (Ranked)
            if not region_articles.empty:
                region_articles["rank"] = pd.to_numeric(
                    region_articles["rank"], errors="coerce"
                ).fillna(999)
                region_articles = region_articles.sort_values(
                    by=["rank", "source"], ascending=[True, True]
                )

                for _, row in region_articles.iterrows():
                    content.append(self._format_article_line(row))
                content.append("")

        # 4. In-Depth Analysis
        unknown_articles = articles_df[articles_df["region"] == "Unknown"].copy()
        if not unknown_articles.empty:
            content.append("# In-Depth Analysis <a id='in-depth-analysis'></a>\n")

            unknown_articles["rank"] = pd.to_numeric(
                unknown_articles["rank"], errors="coerce"
            ).fillna(999)
            unknown_articles = unknown_articles.sort_values(
                by=["rank", "source"], ascending=[True, True]
            )

            for _, row in unknown_articles.iterrows():
                content.append(self._format_article_line(row))
            content.append("")

        # 5. Sources Footer
        content.append("---")
        content.append(self._build_sources_footer(config))

        final_markdown = "\n".join(content)
        filename = f"{date_str}-weekly-news.md"

        return ReportArtifact(content=final_markdown, filename=filename)

    def _build_navigation(self) -> str:
        links = []
        for region in REGION_HEADINGS.keys():
            slug = MarkdownFormatter.slugify(region)
            links.append(f"[{region}](#{slug})")

        links.append("[In-Depth Analysis](#in-depth-analysis)")

        lines = []
        chunk_size = 7
        for i in range(0, len(links), chunk_size):
            chunk = links[i : i + chunk_size]
            lines.append(" | ".join(chunk))

        return "**Navigate:** \n" + "  \n".join(lines)

    def _build_sources_footer(self, config: Dict[str, Any]) -> str:
        sources = config.get("sources", [])
        datapoints = [s for s in sources if s.get("type") == "datapoint"]
        analysis = [s for s in sources if s.get("type") == "analysis"]

        def fmt_source(s):
            return MarkdownFormatter.link(s.get("name", "Link"), s.get("url", "#"))

        footer = [MarkdownFormatter.h3("Sources"), "<small>"]

        if datapoints:
            links = ", ".join([fmt_source(s) for s in datapoints])
            footer.append(f"**Datapoints:** {links}  ")

        if analysis:
            links = ", ".join([fmt_source(s) for s in analysis])
            footer.append(f"**Analysis:** {links}")

        footer.append("</small>")
        return "\n".join(footer)

    def _format_article_line(self, row: pd.Series) -> str:
        """Formats: * [`Source` Title](URL)"""
        title = str(row.get("title", "No Title"))
        title = title.replace("|", "-").replace("[", "(").replace("]", ")")
        source = str(row.get("source", "Unknown Source"))
        url = str(row.get("url", "#"))

        return f"* [`{source}` {title}]({url})"
