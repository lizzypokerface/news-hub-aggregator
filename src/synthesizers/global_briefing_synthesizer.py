import logging
import re
from typing import List

from interfaces import BaseSynthesizer
from interfaces.models import GlobalBriefing, RegionalBriefingEntry

logger = logging.getLogger(__name__)

MODEL_NAME = "Gemini-3-Pro"

BRIEFING_PROMPT_TEMPLATE = """
You are a Geopolitical Strategy Chief. Your task is to synthesize disparate intelligence streams into a coherent **Global Situation Briefing**.

**Objective:**
For each predefined region, you must produce TWO distinct sections:
1.  **Mainstream Narrative:** Summarize what the mainstream news (Layer 2) is reporting. Capture the tone, the headlines, and the "official story."
2.  **Strategic Analysis:** Provide the deep materialist/strategic reality (synthesizing Layers 1, 3, and 4). Contrast this with the mainstream narrative. Explain *why* events are happening based on economics and class dynamics.

---
**PREDEFINED REGIONS (Use strictly):**
Global, China, East Asia, Singapore, Southeast Asia, South Asia, Central Asia, Russia, West Asia (Middle East), Africa, Europe, Latin America & Caribbean, North America, Oceania.

**INPUT INTELLIGENCE:**
=== LAYER 1: GLOBAL ECONOMIC SNAPSHOT ===
{econ_text}

=== LAYER 2: MAINSTREAM HEADLINES ===
{mainstream_text}

=== LAYER 3: ANALYSIS HEADLINES ===
{analysis_text}

=== LAYER 4: MATERIALIST ANALYSIS ===
{materialist_text}

---
**OUTPUT FORMAT:**
- The final output must be a single block of text in Markdown format.
- Structure each region EXACTLY as follows:

## Region Name
### Mainstream Narrative
[Summary of what the news is saying...]

### Strategic Analysis
[Deep dive into the strategic/material reality...]

- Separate regions with newlines.
"""


class GlobalBriefingSynthesizer(BaseSynthesizer):
    """
    Fuses intelligence into a two-part regional briefing (Mainstream vs. Reality).
    """

    def synthesize(
        self,
        mainstream_text: str,
        analysis_text: str,
        materialist_text: str,
        econ_text: str,
    ) -> GlobalBriefing:
        logger.info("Synthesizing Global Briefing (Dual-Section Mode)...")

        # Large context window usage (Gemini-3-Pro style)
        prompt = BRIEFING_PROMPT_TEMPLATE.format(
            mainstream_text=mainstream_text[:1000000],
            analysis_text=analysis_text[:1000000],
            materialist_text=materialist_text[:1000000],
            econ_text=econ_text[:500000],
        )

        try:
            response_text = self.llm_client.query(
                prompt, provider="poe", model=MODEL_NAME
            )
            entries = self._parse_llm_output(response_text)
            return GlobalBriefing(entries=entries)

        except Exception as e:
            logger.error(f"Global Briefing Synthesis failed: {e}")
            return GlobalBriefing(entries=[])

    def _parse_llm_output(self, text: str) -> List[RegionalBriefingEntry]:
        """
        Parses the structured Markdown response.
        Expected format:
        ## China
        ### Mainstream Narrative
        ...
        ### Strategic Analysis
        ...
        """
        entries = []
        # Split by Level 2 headers (Regions)
        region_sections = re.split(r"(?m)^##\s+(.+)$", text)

        # Skip preamble (index 0)
        for i in range(1, len(region_sections), 2):
            region_name = region_sections[i].strip()
            content_block = region_sections[i + 1].strip()

            # Now extract the two subsections from the content block
            mainstream_match = re.search(
                r"### Mainstream Narrative\s*(.*?)(?=### Strategic Analysis|$)",
                content_block,
                re.DOTALL,
            )
            strategic_match = re.search(
                r"### Strategic Analysis\s*(.*)", content_block, re.DOTALL
            )

            mainstream = (
                mainstream_match.group(1).strip()
                if mainstream_match
                else "_No narrative extracted._"
            )
            strategic = (
                strategic_match.group(1).strip()
                if strategic_match
                else "_No analysis extracted._"
            )

            entries.append(
                RegionalBriefingEntry(
                    region=region_name,
                    mainstream_narrative=mainstream,
                    strategic_analysis=strategic,
                )
            )

        return entries
