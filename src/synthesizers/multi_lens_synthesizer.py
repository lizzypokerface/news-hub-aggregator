import logging
import re
from typing import List

from interfaces import BaseSynthesizer
from interfaces.models import MultiLensAnalysis, MultiLensRegionEntry, LensAnalysis

logger = logging.getLogger(__name__)

MODEL_NAME = "Gemini-2.5-Pro"

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

# Prompt: Handles a LIST of regions
BATCH_LENS_PROMPT = """
You are **Crucible Analyst**, a sophisticated geopolitical analysis engine.

**TASK:** Generate a Multi-Lens (Cubist) Analysis for the following **{count} regions**:
{target_regions_list}

**INPUT CONTEXT:**
{input_context}

---
### **THE 9 ANALYTICAL LENSES**
**1. The GPE Perspective ("map of reality")**
- Mandate: Historical Materialism. Class interests, imperialism, contradictions.
**2. The Market Fundamentalist**
- Mandate: Efficiency, incentives, "market corrections".
**3. The Liberal Institutionalist**
- Mandate: International law, norms, human rights, "rules-based order".
**4. The Realist**
- Mandate: Power distribution, security, national interest.
**5. The Civilizational Nationalist**
- Mandate: Identity, culture, "clash of civilizations".
**6. The Post-Structuralist Critic**
- Mandate: Deconstruct language, narratives, power of discourse.
**7. The Singaporean Strategist**
- Mandate: Principled Pragmatism. Survival, foundations, omnidirectional engagement.
**8. The CPC Strategist**
- Mandate: Dialectical Materialism w/ Chinese Characteristics. Development, stability.
**9. The Fusion (Actionable Strategy)**
- Mandate: The "Sovereign Practitioner". Concrete, ruthless, actionable strategy.

---
### **PROCESSING INSTRUCTIONS**

1.  Iterate through the **Target Regions** listed above.
2.  For each region, analyze the Input Context.
3.  Generate all 9 perspectives (approx 100-150 words each).

**OUTPUT FORMAT (Strict Markdown):**
Use Level 2 headers for Regions (`## Region`) and Level 3 headers for Lenses (`### Lens Name`).

## [First Region Name]
### The GPE Perspective
[Analysis...]
...
### The Fusion
[Analysis...]

## [Second Region Name]
...
(Repeat for all requested regions)
"""


class MultiLensSynthesizer(BaseSynthesizer):
    """
    Phase 6: Multi-Lens Analysis.
    Refracts regional intelligence through 9 distinct ideological frameworks.
    Uses Batch Processing (5-5-4) to optimize API calls.
    """

    def synthesize(
        self,
        mainstream_text: str,
        analysis_text: str,
        materialist_text: str,
        econ_text: str,
    ) -> MultiLensAnalysis:
        logger.info("Synthesizing Multi-Lens Analysis (Batch Mode 5-5-4)...")

        # 1. Prepare Global Context
        combined_context = (
            f"=== ECONOMICS ===\n{econ_text[:500000]}\n\n"
            f"=== MAINSTREAM ===\n{mainstream_text[:1000000]}\n\n"
            f"=== ANALYSIS ===\n{analysis_text[:1000000]}\n\n"
            f"=== MATERIALIST ===\n{materialist_text[:1000000]}"
        )

        final_entries: List[MultiLensRegionEntry] = []

        # 2. Define Batches (5, 5, 4)
        # You can adjust 'chunk_size' to tune performance vs. token limits
        batches = self._chunk_list(REQUIRED_REGIONS, 5)

        # 3. Process Batches
        for batch_index, batch_regions in enumerate(batches):
            region_list_str = ", ".join(batch_regions)
            logger.info(f"   > Processing Batch {batch_index + 1}: [{region_list_str}]")

            try:
                prompt = BATCH_LENS_PROMPT.format(
                    count=len(batch_regions),
                    target_regions_list=self._format_list_for_prompt(batch_regions),
                    input_context=combined_context,
                )

                # Query LLM
                response_text = self.llm_client.query(
                    prompt, provider="poe", model=MODEL_NAME
                )

                # Parse Batch Output
                batch_entries = self._parse_batch_output(response_text)

                # Append to master list
                final_entries.extend(batch_entries)

            except Exception as e:
                logger.error(f"Failed to process batch {batch_regions}: {e}")
                # We don't fill placeholders here immediately;
                # validation step below will handle any missing regions.

        # 4. Validation & Placeholder Filling
        # This ensures that if a batch failed, we still have 14 entries (some empty)
        validated_entries = self._validate_and_fill_regions(final_entries)

        return MultiLensAnalysis(entries=validated_entries)

    def _chunk_list(self, data: List[str], size: int) -> List[List[str]]:
        """Splits a list into chunks of size 'n'."""
        return [data[i : i + size] for i in range(0, len(data), size)]

    def _format_list_for_prompt(self, regions: List[str]) -> str:
        """Formatted bullet list for the prompt."""
        return "\n".join([f"- {r}" for r in regions])

    def _parse_batch_output(self, text: str) -> List[MultiLensRegionEntry]:
        """
        Parses a response containing MULTIPLE regions.
        Format:
        ## China
        ...
        ## East Asia
        ...
        """
        entries = []
        # Split by Region Header (## Region)
        region_sections = re.split(r"(?m)^##\s+(.+)$", text)

        # Iterate (skip preamble index 0)
        for i in range(1, len(region_sections), 2):
            region_name = region_sections[i].strip()
            content_block = region_sections[i + 1].strip()

            # Now parse the lenses within this region block
            lenses = self._parse_lenses(content_block)

            if lenses:
                entries.append(MultiLensRegionEntry(region=region_name, lenses=lenses))

        return entries

    def _parse_lenses(self, text: str) -> List[LensAnalysis]:
        """Parses the ### Lens Headers within a region block."""
        lenses = []
        lens_sections = re.split(r"(?m)^###\s+(.+)$", text)

        for i in range(1, len(lens_sections), 2):
            lens_name = lens_sections[i].strip()
            lens_content = lens_sections[i + 1].strip()
            lenses.append(LensAnalysis(lens_name=lens_name, analysis_text=lens_content))

        return lenses

    def _validate_and_fill_regions(
        self, entries: List[MultiLensRegionEntry]
    ) -> List[MultiLensRegionEntry]:
        """
        Ensures all 14 required regions are present.
        """
        existing_map = {e.region: e for e in entries}
        final_list = []
        missing_regions = []

        for region in REQUIRED_REGIONS:
            if region in existing_map:
                final_list.append(existing_map[region])
            else:
                missing_regions.append(region)
                # Create Placeholder
                placeholder_lens = LensAnalysis(
                    lens_name="System Error",
                    analysis_text="*Analysis failed or was skipped for this region.*",
                )
                final_list.append(
                    MultiLensRegionEntry(region=region, lenses=[placeholder_lens])
                )

        if missing_regions:
            logger.warning(
                f"Multi-Lens Missing Regions (Auto-filled): {missing_regions}"
            )

        return final_list
