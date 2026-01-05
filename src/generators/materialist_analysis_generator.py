import os
import logging
from typing import List

from interfaces import BaseGenerator
from interfaces.models import MaterialistAnalyses, MaterialistAnalysisEntry

logger = logging.getLogger(__name__)

# --- Configuration Constants ---
MODEL_NAME = "Gemini-2.5-Flash"

PROMPT_TEMPLATE = """
You are **The Materialist Analyst**. Your goal is to analyze the provided text (news reports, transcripts, intelligence briefs) and strip away the "Breaking News" sensation, diplomatic rhetoric, and moral posturing.

You must isolate the underlying economic, physical, and geopolitical mechanics of the events. You view the world through a lens of **Historical Materialism** and **Realpolitik**.

**Your Core Directives:**
1.  **Ignore Ideology:** Do not analyze based on "democracy vs. autocracy" or "good vs. evil." Analyze based on interests, capital flows, and strategic depth.
2.  **Focus on the Material Base:** Look for the physical basis of the conflict (Oil, Lithium, Semiconductors, Shipping Lanes, Land, Food).
3.  **Analyze Power Dynamics:** Treat international law and diplomacy as tools used by powerful states to enforce their will, not as objective standards.

**Output Structure:**
Organize your analysis into the following four specific sections. For each section, identify 2-3 key conflicts or trends found in the text and provide a "Materialist Analysis" for each.

### 1. Resource Sovereignty & Supply Chains
* **Focus:** Control over raw materials (oil, rare earths, chips), strategic geography (straits, islands), and the physical means of production.
* **Question to answer:** Who is trying to seize or protect the physical resources necessary for their economy?

### 2. Hegemony & Military Industrial Complex
* **Focus:** The use of kinetic force, "policing," proxy wars, arms sales, and the maintenance of imperial hierarchies.
* **Question to answer:** How is the dominant power (or aspiring power) using violence or the threat of violence to discipline others?

### 3. Multipolarity & De-dollarization
* **Focus:** Resistance blocks, South-South cooperation, alternative financial systems (BRICS, CIPS), and the challenge to Unipolarity.
* **Question to answer:** How are nations forming alliances to bypass the dominant financial or political order?

### 4. The Rentier Economy & Financialization
* **Focus:** Extraction of value via debt, sanctions, asset seizure, colonial administration, and the weaponization of currency.
* **Question to answer:** How is value being extracted from a region without the production of goods (e.g., through sanctions or financial warfare)?

### Synthesis
* **System Status:** Provide a 2-sentence summary of the global state of affairs based *only* on the provided text (e.g., "Critical," "Stabilizing," "Bifurcating").

**Input Data:**
{content}
"""


class MaterialistAnalysisGenerator(BaseGenerator):
    """
    Phase 4: Materialist Analysis.
    Iterates through summary files, extracting the region name from the header (# Region),
    and generating a Historical Materialist analysis using an LLM.
    """

    def generate(self, input_dir: str) -> MaterialistAnalyses:
        """
        Args:
            input_dir: Path to the directory containing summary markdown files.

        Returns:
            MaterialistAnalyses object containing entries for all processed regions.
        """
        if not os.path.exists(input_dir):
            logger.error(f"Summary directory not found: {input_dir}")
            return MaterialistAnalyses(entries=[])

        entries: List[MaterialistAnalysisEntry] = []

        # Get all markdown files in the directory
        files = [f for f in os.listdir(input_dir) if f.endswith(".md")]

        if not files:
            logger.warning(f"No summary files found in {input_dir}")
            return MaterialistAnalyses(entries=[])

        logger.info(f"Starting Materialist Analysis for {len(files)} regions...")

        for filename in files:
            file_path = os.path.join(input_dir, filename)

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # 1. Extract Region Name (First line starting with #)
                region_name = self._extract_region_name(content)
                if not region_name:
                    logger.warning(
                        f"Could not extract region name from {filename}. Skipping."
                    )
                    continue

                # 2. Generate Analysis
                logger.info(f"Analyzing Region: {region_name} using {MODEL_NAME}")
                analysis_text = self._query_llm(content)

                # 3. Store Result
                entries.append(
                    MaterialistAnalysisEntry(region=region_name, analysis=analysis_text)
                )

            except Exception as e:
                logger.error(f"Failed to analyze file {filename}: {e}")
                continue

        return MaterialistAnalyses(entries=entries)

    def _extract_region_name(self, content: str) -> str:
        """
        Parses the markdown content to find the first H1 header.
        Example Input: "# Southeast Asia\n..." -> Returns: "Southeast Asia"
        """
        for line in content.splitlines():
            if line.startswith("# "):
                return line.replace("# ", "").strip()
        return "Unknown Region"

    def _query_llm(self, summary_content: str) -> str:
        """
        Constructs the prompt and calls the LLM client.
        """
        # Inject the content into the template
        prompt = PROMPT_TEMPLATE.format(content=summary_content)

        # Use the injected LLM client with the specific provider and model
        #
        return self.llm_client.query(prompt, provider="poe", model=MODEL_NAME)
