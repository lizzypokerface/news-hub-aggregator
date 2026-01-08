import logging
import re
from typing import List

from interfaces import BaseSynthesizer
from interfaces.models import MainstreamNarrative, MainstreamEventEntry

logger = logging.getLogger(__name__)

MODEL_NAME = "Gemini-2.5-Pro"

# Standard Region Order (14 Core + Unknown)
REQUIRED_REGIONS = [
    "Global",
    "China",
    "East Asia",
    "Singapore",
    "Southeast Asia",
    "South Asia",
    "Central Asia",
    "Russia",
    "West Asia (Middle East)",
    "Africa",
    "Europe",
    "Latin America & Caribbean",
    "North America",
    "Oceania",
    "Unknown",
]

# Adapted from regional_summarizer.py to focus strictly on mainstream reporting
MAINSTREAM_PROMPT_TEMPLATE = """
You are a Mainstream News Analyst. Your task is to synthesize a collection of headlines and summaries from major global news outlets into a clean, objective situational report.

**Constraint:** Report ONLY what the mainstream sources are saying. Do not add critical analysis, debunking, or alternative theories. Your goal is to capture the "Official Narrative" or "Chatter" exactly as it is being presented to the public.

---
**PREDEFINED REGIONS (Use these categories ONLY):**
    - 'Global': Use for articles involving multiple distinct regions.
    - 'China': For articles primarily about China.
    - 'East Asia': For Japan, South Korea, North Korea.
    - 'Singapore': Use ONLY for articles specifically about Singapore.
    - 'Southeast Asia': For countries like Vietnam, Thailand, Indonesia, Malaysia, Philippines.
    - 'South Asia': For India, Pakistan, Bangladesh, Sri Lanka.
    - 'Central Asia': For Kazakhstan, Uzbekistan, etc.
    - 'Russia': For articles primarily about Russia.
    - 'West Asia (Middle East)': For countries like Lebanon, Iran, Saudi Arabia, Palestine, etc.
    - 'Africa': For countries on the African continent.
    - 'Europe': For European countries, including the UK and the EU.
    - 'Latin America & Caribbean': For countries in Central and South America, and the Caribbean.
    - 'North America': For the United States and Canada.
    - 'Oceania': For Australia, New Zealand, Pacific Islands.
    - 'Unknown': Use ONLY if you cannot determine the region with confidence.

**Region Order:** You MUST follow this strict order for the regions.
---
**METHODOLOGY:**
1.  **Read and Categorize:** Assign each input event to a predefined region.
2.  **Synthesize by Region:** Group the points for each region.
3.  **Summarize:** Write a single, coherent paragraph (approx 150-200 words) synthesizing the mainstream reporting.
4.  **Tone:** Neutral, journalistic, summary style.

**OUTPUT FORMAT (Strict Markdown):**
- Use Level 2 Markdown headers for regions (e.g., `## Global`).
- Follow with the summary paragraph.
- Separate regions with newlines.

---
**INPUT MAINSTREAM HEADLINES:**
{input_text}

**REGIONAL SUMMARY:**
"""


class MainstreamNewsSynthesizer(BaseSynthesizer):
    """
    Phase 1b: Mainstream Narrative Synthesis.
    Takes consolidated mainstream headlines and creates a coherent 'What the world is saying' report.
    """

    def synthesize(self, mainstream_content: str) -> MainstreamNarrative:
        """
        Synthesizes raw mainstream headlines into a regional narrative.
        """
        logger.info("Synthesizing Mainstream Narrative...")

        # Sanity check for empty content
        if not mainstream_content or len(mainstream_content) < 50:
            logger.warning("Mainstream content too short or empty.")
            return MainstreamNarrative(entries=self._create_empty_entries())

        # Truncate to safety limit if necessary
        prompt = MAINSTREAM_PROMPT_TEMPLATE.format(
            input_text=mainstream_content[:500000]
        )

        try:
            # Query LLM via unified client
            response_text = self.llm_client.query(
                prompt, provider="poe", model=MODEL_NAME
            )

            # Parse Response
            entries = self._parse_llm_output(response_text)

            # Validation Step: Ensure all regions are present
            final_entries = self._validate_and_fill_regions(entries)

            return MainstreamNarrative(entries=final_entries)

        except Exception as e:
            logger.error(f"Mainstream Synthesis failed: {e}")
            return MainstreamNarrative(entries=self._create_empty_entries())

    def _parse_llm_output(self, text: str) -> List[MainstreamEventEntry]:
        """
        Parses Markdown structure: ## Region \n Content
        """
        entries = []
        # Split by Level 2 headers (## Region)
        region_sections = re.split(r"(?m)^##\s+(.+)$", text)

        # Iterate through captured groups (skipping preamble at index 0)
        for i in range(1, len(region_sections), 2):
            region_name = region_sections[i].strip()
            content = region_sections[i + 1].strip()

            if region_name and content:
                entries.append(
                    MainstreamEventEntry(region=region_name, summary_text=content)
                )

        return entries

    def _validate_and_fill_regions(
        self, entries: List[MainstreamEventEntry]
    ) -> List[MainstreamEventEntry]:
        """
        Ensures all 15 required regions are present.
        Logs warnings for missing regions and fills them with placeholders.
        Returns a sorted list of entries matching the REQUIRED_REGIONS order.
        """
        # Map existing entries by region name for quick lookup
        existing_map = {e.region: e for e in entries}
        final_list = []
        missing_regions = []

        for region in REQUIRED_REGIONS:
            if region in existing_map:
                final_list.append(existing_map[region])
            else:
                # Region missing: Log it and create placeholder
                missing_regions.append(region)
                final_list.append(
                    MainstreamEventEntry(
                        region=region,
                        summary_text="*No mainstream reporting found for this region.*",
                    )
                )

        if missing_regions:
            logger.info(
                f"Mainstream Narrative Missing Regions (Auto-filled): {len(missing_regions)} regions"
            )

        return final_list

    def _create_empty_entries(self) -> List[MainstreamEventEntry]:
        """Helper to create a fully empty dataset if generation fails."""
        return [
            MainstreamEventEntry(
                region=r, summary_text="*No data available due to processing error.*"
            )
            for r in REQUIRED_REGIONS
        ]
