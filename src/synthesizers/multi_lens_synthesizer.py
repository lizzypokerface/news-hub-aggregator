import logging
import re
from typing import List

from interfaces import BaseSynthesizer
from interfaces.models import MultiLensAnalysis, MultiLensRegionEntry, LensAnalysis

logger = logging.getLogger(__name__)

MODEL_NAME = "Gemini-2.5-Flash"

# Standard Region Order
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
]

# Updated Prompt: Focused on ONE region at a time
SINGLE_REGION_LENS_PROMPT = """
You are **Crucible Analyst**, a sophisticated geopolitical analysis engine.

**TASK:** Generate a Multi-Lens (Cubist) Analysis specifically for the region: **{target_region}**.

**INPUT CONTEXT:**
{input_context}

---
### **THE 9 ANALYTICAL LENSES**

**1. The GPE Perspective ("map of reality")**
- Mandate: Ground analysis in Historical Materialism. Ask "Cui bono?". Focus on class interests, imperialism, and system contradictions.

**2. The Market Fundamentalist**
- Mandate: Focus on efficiency, incentives, and "market corrections". View government intervention as distortion.

**3. The Liberal Institutionalist**
- Mandate: Focus on international law, norms, human rights, and diplomacy. The "rules-based order" is paramount.

**4. The Realist**
- Mandate: Focus on power distribution, security, and national interest. Ideology is noise; hard power is real.

**5. The Civilizational Nationalist**
- Mandate: Focus on identity, culture, and "clash of civilizations".

**6. The Post-Structuralist Critic**
- Mandate: Deconstruct language and narratives. How is power using discourse ("security", "terrorist") to legitimize itself?

**7. The Singaporean Strategist**
- Mandate: Principled Pragmatism. Focus on survival, economic reliance, and omnidirectional engagement.

**8. The CPC Strategist**
- Mandate: Dialectical Materialism with Chinese Characteristics. Focus on development, stability, and long-term national rejuvenation.

**9. The Fusion (Actionable Strategy)**
- Mandate: The "Sovereign Practitioner". Synthesize the above views into a ruthless, concrete, actionable strategy for a sovereign state in this region.

---
### **PROCESSING INSTRUCTIONS**

1.  Analyze the input context for events relevant to **{target_region}**.
2.  If NO relevant events are found for this region, output: "NO_DATA_FOUND".
3.  Otherwise, generate all 9 perspectives. Each analysis should be **150 words**.

**OUTPUT FORMAT (Strict Markdown):**
Use Level 3 headers for Lenses (`### Lens Name`). Do not include the Region header (we handle that externally).

### The GPE Perspective
[Analysis...]

### The Market Fundamentalist
[Analysis...]

(Continue for all 9 lenses...)
"""


class MultiLensSynthesizer(BaseSynthesizer):
    """
    Refracts regional intelligence through 9 distinct ideological frameworks.
    Iterates Region-by-Region to avoid output token limits.
    """

    def synthesize(
        self,
        mainstream_text: str,
        analysis_text: str,
        materialist_text: str,
        econ_text: str,
    ) -> MultiLensAnalysis:
        logger.info("Synthesizing Multi-Lens Analysis (Iterative Phase 6)...")

        # 1. Prepare Global Context
        # We pass the full context to every call so the LLM can see cross-regional connections
        # (e.g., a decision in DC affects Oceania).
        combined_context = (
            f"=== ECONOMICS ===\n{econ_text[:500000]}\n\n"
            f"=== MAINSTREAM ===\n{mainstream_text[:1000000]}\n\n"
            f"=== ANALYSIS ===\n{analysis_text[:1000000]}\n\n"
            f"=== MATERIALIST ===\n{materialist_text[:1000000]}"
        )

        final_entries: List[MultiLensRegionEntry] = []

        # 2. Iterate Through Each Region
        for region in REQUIRED_REGIONS:
            logger.info(f"   > Processing Lenses for: {region}...")

            try:
                # Format prompt for THIS region only
                prompt = SINGLE_REGION_LENS_PROMPT.format(
                    target_region=region, input_context=combined_context
                )

                # Query LLM
                response_text = self.llm_client.query(
                    prompt, provider="poe", model=MODEL_NAME
                )

                # Check for "No Data" signal
                if "NO_DATA_FOUND" in response_text:
                    logger.warning(
                        f"     [!] No data found for {region}. Creating placeholder."
                    )
                    final_entries.append(self._create_placeholder_entry(region))
                    continue

                # Parse lenses
                lenses = self._parse_lenses(response_text)

                # If parsing failed or returned empty (hallucination), use placeholder
                if not lenses:
                    logger.warning(
                        f"     [!] Parsing failed for {region}. Creating placeholder."
                    )
                    final_entries.append(self._create_placeholder_entry(region))
                else:
                    final_entries.append(
                        MultiLensRegionEntry(region=region, lenses=lenses)
                    )

            except Exception as e:
                logger.error(f"Failed to process region {region}: {e}")
                final_entries.append(self._create_placeholder_entry(region))

        return MultiLensAnalysis(entries=final_entries)

    def _parse_lenses(self, text: str) -> List[LensAnalysis]:
        """
        Parses the list of ### Headers from a single region's output.
        """
        lenses = []
        # Split by Lens Header (### Lens Name)
        # Regex looks for line starting with ###, captures the title, then content
        lens_sections = re.split(r"(?m)^###\s+(.+)$", text)

        # Section 0 is preamble, skip it.
        for i in range(1, len(lens_sections), 2):
            lens_name = lens_sections[i].strip()
            lens_content = lens_sections[i + 1].strip()
            lenses.append(LensAnalysis(lens_name=lens_name, analysis_text=lens_content))

        return lenses

    def _create_placeholder_entry(self, region: str) -> MultiLensRegionEntry:
        """Helper to ensure the report structure remains intact even on failure."""
        return MultiLensRegionEntry(
            region=region,
            lenses=[
                LensAnalysis(
                    lens_name="System Status",
                    analysis_text="*No multi-lens analysis generated for this region.*",
                )
            ],
        )
