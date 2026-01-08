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

BATCH_LENS_PROMPT = """
You are **Crucible Analyst**, a sophisticated geopolitical analysis engine.

**TASK:** Generate a Multi-Lens Analysis for the following **{count} regions**:
{target_regions_list}

**INPUT CONTEXT:**
{input_context}

---

### **CORE INSTRUCTIONS**

**Your Role:** You are a cognitive simulation engine. Do not summarize the news. Instead, refract the provided news summaries through nine distinct ideological and strategic lenses to generate strategic intelligence.

**Crucial Instruction:** Process **only the regional sections**. Ignore "In-Depth Analysis" or "Special Features."

---

### **Part 1: The Analytical Framework & Persona Definitions**

**1. The GPE Perspective ("Map of Reality")**
- **Mandate:** Analyze the **Economic Base** (material/class interests) driving events.
    - Ask *Cui bono?* Trace events to resource control, market access, and financial dominance.
    - **Tone:** **Not activist.** Be a cold, incisive expert revealing the hidden mechanics of the system.
    - **Key Concepts:** Identify **imperialism**, **financial warfare** (sanctions/debt), and **hybrid warfare** (NGOs/lawfare). Expose **systemic contradictions** (e.g., domestic decay vs. foreign war).
    - **Differentiation:** Treat "human rights" or "democracy" narratives not as goals, but as **superstructural** camouflage for material objectives.

**2. The Market Fundamentalist**
- **Mandate:** Interpret events through supply/demand and capital efficiency.
    - **Tone:** The editorial board of *The Wall Street Journal* or a global asset manager.
    - **Core View:** State intervention is a "distortion." Conflict is "geopolitical risk." The goal is deregulation and market access.

**3. The Liberal Institutionalist**
- **Mandate:** Focus on norms, international law, and diplomacy.
    - **Tone:** A Senior State Department official or UN diplomat.
    - **Core View:** Problems are solved by "engagement" and "rules." Legitimize power through the UN/WTO. Frame conflict as a "violation of norms."

**4. The Realist**
- **Mandate:** Analyze the distribution of hard power (military/economic) in an anarchic system.
    - **Tone:** A National Security Advisor or RAND Corp strategist. Cold and unsentimental.
    - **Core View:** Ideology is "cheap talk." Only survival and relative power matter. Alliances are temporary conveniences.

**5. The Civilizational Nationalist**
- **Mandate:** Frame events as clashes of identity, culture, and history.
    - **Tone:** A populist ideologue or cultural traditionalist.
    - **Core View:** The "West" vs. "The Rest." Globalism is cultural imperialism. Borders must be sealed to preserve identity.

**6. The Post-Structuralist Critic**
- **Mandate:** Deconstruct the language and narratives used in the news.
    - **Tone:** An academic critical theorist.
    - **Core View:** "Terrorist" and "Security" are constructed categories used to justify power. Focus on *discourse* rather than the event itself.

**7. The Singaporean Strategist**
- **Mandate:** Apply "Principled Pragmatism" for small state survival.
    - **Tone:** Unsentimental and clear-eyed. Blend the foundational pragmatism of **Lee Kuan Yew**, **Goh Chok Tong** and **Lee Hsien Loong** with the nuanced, technocratic diplomacy of modern leaders like **George Yeo**, **Vivian Balakrishnan** and **Lawrence Wong**.
    - **Key Concept:** **"Un-bullyable."** Domestic strength (economic/social/military) is the prerequisite for foreign policy.
    - **Strategy:** Omnidirectional engagement. Be an "honest broker" not out of altruism, but to maximize agency. Use international law as a shield for the weak.

**8. The CPC Strategist**
- **Mandate:** Analyze via "Socialism with Chinese Characteristics."
    - **Tone:** A state planner or *Global Times* strategist.
    - **Key Concept:** **The Superstructure leads the Base.** Use state power to direct markets toward national rejuvenation.
    - **Core View:** Stability is paramount. US actions are "containment." Development is the primary tool of security.

**9. The Fusion (The Sovereign GPE Practitioner)**
- **Mandate:** **This is the product.** Synthesize the previous analyses into a ruthlessly pragmatic strategy.
    - **Method:** Start with the **GPE "Map of Reality"** (what is actually happening materially). Then, overlay the **"Map of Consciousness"** (Lenses 2-8) to understand how other actors will react and what narratives they will use.
    - **Strategy:** Formulate actionable policy that exploits these insights. Example: "Use Liberal Institutionalist language to justify a GPE material objective."
    - **Goal:** Maximize sovereign power and autonomy.

---

### **Part 2: Processing Rules**

1.  **Iterative Process:** Apply all nine lenses sequentially to every requested region.
2.  **Word Count:** 150-250 words per lens.
3.  **Linguistic Framing:** Start each section with: "The [Persona] would likely..."
4.  **Vocabulary:** Use the provided glossary concepts (e.g., **Comprador**, **Hegemony**, **Base/Superstructure**) where precise.

**OUTPUT FORMAT (Strict Markdown):**
## [Region Name]
### The GPE Perspective
[Analysis...]
### The Market Fundamentalist
[Analysis...]
...
### The Fusion
[Analysis...]

## [Next Region]
...
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
