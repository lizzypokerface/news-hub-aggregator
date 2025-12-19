import os
import logging
from datetime import datetime
from modules.content_extractor import ContentExtractor
from modules.llm_client import LLMClient

logger = logging.getLogger(__name__)

# The detailed prompt template for Historical Materialist Analysis

HISTORICAL_MATERIALIST_ANALYSIS_PROMPT = """
### OVERVIEW
You are a critical political economy and geopolitical analyst, inspired by the frameworks of Michael Hudson, Radhika Desai, and Ben Norton.

### INSTRUCTIONS
Analyze the provided "Raw Research Transcripts" below and produce a comprehensive, structured report following the format below.

### REPORT STRUCTURE

1. Executive Summary
    - Synthesize key historical, class, power, and geopolitical dynamics
    - Highlight important contradictions, conflict drivers, and material conditions
    - Focus on how history, class structure, imperialism, and external influences shape the present
    - Keep concise (maximum 200 words)
2. Basic Data
    - Capital, population, languages, region, etc.
3. Pre-capitalist Foundations
    - Ancient societies, modes of production, and early power structures
4. Colonialism, Imperialism, and State Formation
    - Colonial experience, borders, independence, and state-building
5. Class Structure and Social Forces
    - Main social classes, elites, popular movements, and their evolution
6. Economic Development and Structural Change
    - Key phases (agrarian, industrial, financial), dependencies, and transformations
7. Imperialism, Neocolonialism, and External Relations
    - Historical and current external domination, alliances, and dependencies
8. Political Power Structure
    - Main forms of rule, institutions, and factional struggles
9. Material Conditions and Social Indicators
    - Inequality, labor, infrastructure, poverty, living standards
10. Current Contradictions and Structural Issues
    - Ongoing crises, class conflict, external shocks, or contradictions
11. Recent Developments and Trends
    - Major events, shifts in alliances, social/political changes
12. Analytical Notes (Marxist/Geopolitical Perspective)
    - Critical assessment of world-system position, historical legacies, class dynamics, and alternative paths

### ANALYSIS GUIDELINES

- Foreground history, class, imperialism, power, and material conditions—not just political or cultural surface events
- Draw explicit connections between past and present
- Highlight contradictions and whose interests are being served
- Where relevant, comment on the roles of major powers (US, China, Russia) and regional blocs (BRICS, ASEAN, etc.)
- Analyze neoliberal or multipolar trends affecting the country
- If analyzing two countries, compare and contrast throughout, especially in summary and analytical sections
- Keep sections clear and focused for database entry suitability

### EXAMPLE OUTPUT FORMAT

## Thailand & Cambodia: Executive Summary (2025)

**Thailand and Cambodia are locked in a renewed border conflict rooted not only in colonial-era boundaries but also in the internal power struggles and class dynamics of each country. The Preah Vihear dispute, reignited in 2025, is both a legacy of imperialist cartography and a tool for elites on both sides to shore up legitimacy amid domestic crises. In Thailand, the military-monarchy alliance leverages nationalism and conflict to weaken civilian, populist forces, while in Cambodia, the ruling family uses the crisis to consolidate succession. Externally, the crisis exposes the region's vulnerability to great power maneuvering.**

---

## Structured Historical-Structural Summary

### 1. Basic Data

| | Thailand | Cambodia |
| --- | --- | --- |
| Capital | Bangkok | Phnom Penh |
| Population | ~70 million | ~17 million |
| Languages | Thai | Khmer |
| Region | Southeast Asia | Southeast Asia |

---

### 2. Pre-capitalist Foundations
- **Thailand:** Feudal monarchy, successor to Tai and Siamese kingdoms, never colonized, tributary relationships.
- **Cambodia:** Center of the ancient Khmer Empire, Hindu-Buddhist civilization, agrarian village structure.

---

### 3. Colonialism, Imperialism, and State Formation
- **Thailand:** Maintained independence but ceded territory under British and French pressure; borders shaped by colonial negotiation.
- **Cambodia:** French colony; borders defined by colonial authorities, setting stage for later disputes; independence in 1953.

---

### 4. Class Structure and Social Forces
- **Thailand:** Power triangle—monarchy, military, and weak civilian government; populist bourgeois force; persistent rural-urban divisions.
- **Cambodia:** One-party rule, dynastic family control, party-military alliance; legacy of peasantry and trauma from Khmer Rouge era.

---

### 5. Economic Development and Structural Change
- **Thailand:** East Asian industrialization path, large manufacturing sector, significant inequality, growing financialization.
- **Cambodia:** Dependent on garment exports, agriculture, foreign investment (China, Vietnam); high informality and poverty.

---

### 6. Imperialism, Neocolonialism, and External Relations
- **Thailand:** US military ally, now leaning toward BRICS and China for geoeconomic alternatives; balancing major powers.
- **Cambodia:** Dependency on Chinese capital and Vietnamese political influence; history as Cold War proxy.

---

### 7. Political Power Structure
- **Thailand:** Military-monarchy dominance, frequent coups, populist parties marginalized; civilian government fragile.
- **Cambodia:** Party and family control, dynastic succession, weak but symbolic monarchy, centralized authority.

---

### 8. Material Conditions and Social Indicators
- **Thailand:** Urban-rural inequality, advanced infrastructure in cities, large informal and migrant labor sector.
- **Cambodia:** Rural poverty, poor infrastructure, dependence on remittances, rapid urbanization.

---

### 9. Current Contradictions and Structural Issues
- **Thailand:** Elite infighting, class polarization, instability in civilian rule, growing external vulnerabilities.
- **Cambodia:** Dynastic transition, elite capture, economic dependency, vulnerability to regional shocks.

---

### 10. Recent Developments and Trends
- **Shared:**
    - 2025 border conflict escalation.
    - Dynastic drama and nationalist mobilization.
    - Humanitarian displacement.
    - BRICS expansion and regional realignment.

---

### 11. Analytical Notes (Marxist/Geopolitical Perspective)
- **Colonial Borders as Trigger:** The dispute is a classic example of imperialist legacy shaping present antagonisms.
- **Elite Strategy:** Both sides use the crisis to mobilize nationalist sentiment, diverting attention from internal contradictions.
- **Material Contradictions:** Conflict disrupts deep economic ties; working classes suffer, while elites maneuver for advantage.
- **Multipolarity:** Thailand's BRICS move and Cambodia's reliance on China reflect broader shifts away from Western dominance.

### END OF EXAMPLE

### RAW RESEARCH TRANSCRIPTS
{transcripts}
"""


class HistoricalMaterialistResearcher:
    """
    Orchestrates the targeted research workflow:
    1. Compiling raw transcripts from links.
    2. (Optional) Pausing for manual user review.
    3. Generating a Historical Materialist analysis via LLM.
    """

    def __init__(
        self,
        config: dict,
        input_directory: str = "../inputs",
        output_directory: str = "../outputs/research",
    ):
        self.input_file = os.path.join(input_directory, "research_links.txt")
        self.output_directory = output_directory

        # State variable to hold the path of the current work in progress
        self.current_transcripts_path = None

        # Initialize helpers
        self.extractor = ContentExtractor()
        self.llm = LLMClient(config)

    def conduct_research(
        self,
        manual_review: bool = True,
        provider: str = "poe",
        model: str = "Gemini-2.5-Pro",
    ) -> None:
        """
        Public Orchestrator: Runs the full research pipeline.

        Args:
            manual_review (bool): If True, pauses execution after compilation to allow
                                  the user to edit the markdown file before analysis.
            provider (str): The LLM provider to use.
            model (str): The model name to use.
        """
        logger.info("=== Starting Historical Materialist Research Workflow ===")

        # Step 1: Compile Materials
        self._compile_research_material()

        if not self.current_transcripts_path:
            logger.error("Workflow halted: No transcripts were compiled.")
            return

        # Step 2: Manual Review Pause (Optional)
        if manual_review:
            print("\n" + "=" * 60)
            print("ACTION REQUIRED: Review the raw transcripts.")
            print(f"File location: {os.path.abspath(self.current_transcripts_path)}")
            print("You may edit this file now to remove noise or add notes.")
            print("=" * 60 + "\n")
            input("Press Enter when you are ready to proceed to Analysis... ")
            logger.info("Resuming workflow after manual review.")

        # Step 3: Generate Analysis
        self._generate_analysis(provider=provider, model=model)

        logger.info("=== Research Workflow Complete ===")

    def _compile_research_material(self) -> str:
        """
        Internal: Reads links, fetches content, and compiles to Markdown.
        Updates self.current_transcripts_path.
        """
        logger.info("--- Phase 1: Compiling Research Material ---")

        if not os.path.exists(self.input_file):
            logger.error(f"Input file not found: {self.input_file}")
            return ""

        with open(self.input_file) as f:
            links = [line.strip() for line in f if line.strip()]

        if not links:
            logger.warning("No links found in research_links.txt.")
            return ""

        compiled_content = (
            f"# Raw Research Transcripts | {datetime.now().strftime('%Y-%m-%d')}\n\n"
        )

        for index, url in enumerate(links):
            logger.info(f"Processing ({index+1}/{len(links)}): {url}")
            try:
                text_content = self.extractor.get_text(url)
                compiled_content += f"## Source {index+1}: {url}\n{'-'*40}\n{text_content}\n{'-'*40}\n\n"
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                compiled_content += (
                    f"## Source {index+1}: {url}\n[FAILED TO RETRIEVE CONTENT]\n\n"
                )

        date_str = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(self.output_directory, exist_ok=True)
        output_filename = f"{date_str}_raw_transcripts.md"
        output_path = os.path.join(self.output_directory, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(compiled_content)

        logger.info(f"Transcripts saved to: {output_path}")

        # Update State
        self.current_transcripts_path = output_path
        return output_path

    def _generate_analysis(self, provider: str, model: str) -> str:
        """
        Internal: Reads the file at self.current_transcripts_path and generates analysis.
        """
        logger.info("--- Phase 2: Generating Analysis ---")

        if not self.current_transcripts_path or not os.path.exists(
            self.current_transcripts_path
        ):
            logger.error("No transcript file found to analyze.")
            return ""

        with open(self.current_transcripts_path, encoding="utf-8") as f:
            raw_content = f.read()

        full_prompt = HISTORICAL_MATERIALIST_ANALYSIS_PROMPT.format(
            transcripts=raw_content
        )

        try:
            analysis_text = self.llm.query(
                prompt=full_prompt, provider=provider, model=model
            )
        except Exception as e:
            logger.error(f"Analysis generation failed: {e}")
            return ""

        date_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{date_str}_historical_materialist_analysis.md"
        output_path = os.path.join(self.output_directory, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(analysis_text)

        logger.info(f"Analysis saved to: {output_path}")
        return output_path
