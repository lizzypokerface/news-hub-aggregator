import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from interfaces.models import (
    GlobalBriefing,
    MultiLensAnalysis,
    ReportArtifact,
)

from reporters.markdown_formatter import MarkdownFormatter

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

        # 1. YAML Front Matter & Top Anchor
        content = [
            "---",
            "layout: post",
            f"title:  🌏 Global Briefing | {display_date}",
            f"date:   {date_str} 08:00:00 +0800",
            "categories: weekly news",
            "---",
            "",
            "<a id='top'></a>",  # Anchor for 'Back to Top' buttons
            "",
        ]

        # 2. Navigation Bar
        content.append(self._build_navigation())
        content.append("")

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

            # C. Briefing Narratives (Mainstream + Strategic)
            if briefing_entry:
                # Mainstream
                if briefing_entry.mainstream_narrative:
                    clean_ms = MarkdownFormatter.clean_text(
                        briefing_entry.mainstream_narrative
                    )
                    content.append(f"**Mainstream Narrative:** {clean_ms}\n")

                content.append("")

                # Strategic
                if briefing_entry.strategic_analysis:
                    clean_strat = MarkdownFormatter.clean_text(
                        briefing_entry.strategic_analysis
                    )
                    content.append(f"**Strategic Analysis:** {clean_strat}\n")

            # D. Multi-Lens Dropdowns
            if lens_entry and lens_entry.lenses:
                for lens in lens_entry.lenses:
                    clean_lens = MarkdownFormatter.clean_text(lens.analysis_text)
                    dropdown = MarkdownFormatter.create_dropdown(
                        title=f"Lens: {lens.lens_name}", content=clean_lens
                    )
                    content.append(dropdown)
                content.append("<br>\n")

            # Add Back to Top Button
            if briefing_entry or (lens_entry and lens_entry.lenses):
                content.append(self._build_back_to_top())
                content.append("")

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

            # Add Back to Top Button for In-Depth section too
            content.append(self._build_back_to_top())
            content.append("")

        # 5. Sources Footer
        content.append("---")
        content.append(self._build_sources_footer(config))

        final_markdown = "\n".join(content)
        filename = f"{date_str}-weekly-news.md"

        return ReportArtifact(content=final_markdown, filename=filename)

    def _build_navigation(self) -> str:
        """
        Constructs a horizontal navigation bar using HTML with inline CSS.
        """
        links = []

        # Button Style
        btn_style = (
            "display: inline-block; "
            "padding: 6px 12px; "
            "margin: 4px; "
            "background-color: #f8f9fa; "
            "border: 1px solid #ddd; "
            "border-radius: 5px; "
            "text-decoration: none; "
            "color: #333; "
            "font-weight: 500; "
            "font-size: 0.9em;"
        )

        # 1. Generate Region Buttons
        for region in REGION_HEADINGS.keys():
            slug = MarkdownFormatter.slugify(region)
            # No indentation in the f-string to prevent markdown code blocks
            links.append(f'<a href="#{slug}" style="{btn_style}">{region}</a>')

        # 2. Add In-Depth Analysis Button
        links.append(
            f'<a href="#in-depth-analysis" style="{btn_style}">In-Depth Analysis</a>'
        )

        nav_html = "\n".join(links)

        # No indentation for the return string
        return f'<div style="text-align: left; margin: 20px 0;">\n{nav_html}\n</div>'

    def _build_back_to_top(self) -> str:
        """
        Constructs a 'Back to Top' button aligned to the right.
        """
        style = (
            "display: inline-block; "
            "padding: 4px 10px; "
            "font-size: 0.8em; "
            "color: #6c757d; "
            "border: 1px solid #dee2e6; "
            "border-radius: 4px; "
            "text-decoration: none; "
            "background-color: #fff;"
        )
        return f'<div style="text-align: left; margin-bottom: 10px;"><a href="#top" style="{style}">↑ Back to Top</a></div>'

    def _build_sources_footer(self, config: Dict[str, Any]) -> str:
        sources = config.get("sources", [])
        datapoints = [s for s in sources if s.get("type") == "datapoint"]
        analysis = [s for s in sources if s.get("type") == "analysis"]

        def fmt_source(s):
            return MarkdownFormatter.link(s.get("name", "Link"), s.get("url", "#"))

        footer = [MarkdownFormatter.h3("Sources")]

        if datapoints:
            links = ", ".join([fmt_source(s) for s in datapoints])
            footer.append(f"**Mainstream Narratives:** {links}")
        footer.append("")
        if analysis:
            links = ", ".join([fmt_source(s) for s in analysis])
            footer.append(f"**Strategic Analyses:** {links}")

        return "\n".join(footer)

    def _format_article_line(self, row: pd.Series) -> str:
        """Formats: * [`Source` Title](URL)"""
        title = str(row.get("title", "No Title"))
        title = title.replace("|", "-").replace("[", "(").replace("]", ")")
        source = str(row.get("source", "Unknown Source"))
        url = str(row.get("url", "#"))

        return f"* [`{source}` {title}]({url})"
