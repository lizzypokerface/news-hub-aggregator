import os
import logging
import re
from datetime import datetime
from typing import List
from modules.content_extractor import ContentExtractor
from modules.llm_client import LLMClient

logger = logging.getLogger(__name__)

# --- PROMPT TEMPLATES ---

TITLE_GENERATION_PROMPT = """
You are an editor. Read the following analysis and generate a short, descriptive title (maximum 8 words).
The title must be concise and specific to the content (e.g., "Thailand-Cambodia Border Conflict 2025").
Do not use colons, slashes, or special characters. Do not use Markdown. Just return the plain text title.

ANALYSIS TEXT:
{analysis_text}
"""

HMA_PROMPT = """
### OVERVIEW
You are a critical political economy and geopolitical analyst, inspired by the frameworks of Michael Hudson, Radhika Desai, and Ben Norton.

### INSTRUCTIONS
Analyze the provided "Raw Research Transcripts" below and produce a comprehensive, structured report following the format below.

**CRITICAL CONSTRAINTS:**
1. The "EXAMPLE OUTPUT FORMAT" provided below is for **structural reference ONLY**.
2. Do **NOT** use the content (e.g., specific country names or events) from the example in your final output unless they appear in your transcripts.
3. Your analysis must be based **STRICTLY** on the "RAW RESEARCH TRANSCRIPTS" provided at the end.
4. If the transcripts cover only one country, adapt the structure to focus solely on that country. If they cover two, use the comparative format.

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

### EXAMPLE OUTPUT FORMAT (TEMPLATE)

## [Country/Topic Name]: Executive Summary (Year)

**[Synthesize key historical, class, power, and geopolitical dynamics here. Highlight important contradictions, conflict drivers, and material conditions. Focus on how history, class structure, imperialism, and external influences shape the present. Keep concise (maximum 200 words).]**

---

## Structured Historical-Structural Summary

### 1. Basic Data

| | [Country A] | [Country B (if applicable)] |
| --- | --- | --- |
| Capital | [City Name] | [City Name] |
| Population | [Number] | [Number] |
| Languages | [Languages] | [Languages] |
| Region | [Region] | [Region] |

---

### 2. Pre-capitalist Foundations
- **[Country A]:** [Analyze ancient societies, modes of production, and early power structures.]
- **[Country B]:** [Analyze ancient societies, modes of production, and early power structures.]

---

### 3. Colonialism, Imperialism, and State Formation
- **[Country A]:** [Analyze colonial experience, borders, independence, and state-building.]
- **[Country B]:** [Analyze colonial experience, borders, independence, and state-building.]

---

### 4. Class Structure and Social Forces
- **[Country A]:** [Analyze main social classes, elites, popular movements, and their evolution.]
- **[Country B]:** [Analyze main social classes, elites, popular movements, and their evolution.]

---

### 5. Economic Development and Structural Change
- **[Country A]:** [Analyze key phases (agrarian, industrial, financial), dependencies, and transformations.]
- **[Country B]:** [Analyze key phases (agrarian, industrial, financial), dependencies, and transformations.]

---

### 6. Imperialism, Neocolonialism, and External Relations
- **[Country A]:** [Analyze historical and current external domination, alliances, and dependencies.]
- **[Country B]:** [Analyze historical and current external domination, alliances, and dependencies.]

---

### 7. Political Power Structure
- **[Country A]:** [Analyze main forms of rule, institutions, and factional struggles.]
- **[Country B]:** [Analyze main forms of rule, institutions, and factional struggles.]

---

### 8. Material Conditions and Social Indicators
- **[Country A]:** [Analyze inequality, labor, infrastructure, poverty, living standards.]
- **[Country B]:** [Analyze inequality, labor, infrastructure, poverty, living standards.]

---

### 9. Current Contradictions and Structural Issues
- **[Country A]:** [Analyze ongoing crises, class conflict, external shocks, or contradictions.]
- **[Country B]:** [Analyze ongoing crises, class conflict, external shocks, or contradictions.]

---

### 10. Recent Developments and Trends
- **Shared/Individual:**
    - [Event 1]
    - [Event 2]
    - [Trend 1]

---

### 11. Analytical Notes (Marxist/Geopolitical Perspective)
- **[Key Concept 1]:** [Critical assessment of world-system position.]
- **[Key Concept 2]:** [Historical legacies and class dynamics.]
- **[Key Concept 3]:** [Alternative paths or future outlook.]

### END OF EXAMPLE

### RAW RESEARCH TRANSCRIPTS
{transcripts}
"""


class HistoricalMaterialistResearcher:
    """
    Orchestrates the targeted research workflow.
    """

    def __init__(
        self,
        config: dict,
        input_directory: str = "../inputs",
        output_directory: str = "../outputs/research",
    ):
        self.input_file = os.path.join(input_directory, "research_links.txt")
        self.output_directory = output_directory

        # --- State Variables ---
        self.current_transcripts_path = None
        self.research_links: List[
            str
        ] = []  # Stores links in memory to avoid re-reading files

        # --- Helpers ---
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
        """
        logger.info("=== Starting Historical Materialist Research Workflow ===")

        # Step 1: Compile Materials (Populates self.research_links)
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

        # Step 3: Generate Analysis (Uses self.research_links for citations)
        self._generate_analysis(provider=provider, model=model)

        logger.info("=== Research Workflow Complete ===")

    def _compile_research_material(self) -> str:
        """
        Internal: Reads links into memory, fetches content, and compiles to Markdown.
        """
        logger.info("--- Phase 1: Compiling Research Material ---")

        if not os.path.exists(self.input_file):
            logger.error(f"Input file not found: {self.input_file}")
            return ""

        # 1. Read links into Class Variable
        with open(self.input_file) as f:
            # Store cleaned links in self.research_links
            self.research_links = [line.strip() for line in f if line.strip()]

        if not self.research_links:
            logger.warning("No links found in research_links.txt.")
            return ""

        logger.info(f"Loaded {len(self.research_links)} links into memory.")

        # 2. Extract Content
        compiled_content = (
            f"# Raw Research Transcripts | {datetime.now().strftime('%Y-%m-%d')}\n\n"
        )

        for index, url in enumerate(self.research_links):
            logger.info(f"Processing ({index+1}/{len(self.research_links)}): {url}")
            try:
                text_content = self.extractor.get_text(url)
                compiled_content += f"## Source {index+1}: {url}\n{'-'*40}\n{text_content}\n{'-'*40}\n\n"
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                compiled_content += (
                    f"## Source {index+1}: {url}\n[FAILED TO RETRIEVE CONTENT]\n\n"
                )

        # 3. Save Output
        date_str = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(self.output_directory, exist_ok=True)
        output_filename = f"{date_str}_raw_transcripts.md"
        output_path = os.path.join(self.output_directory, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(compiled_content)

        logger.info(f"Transcripts saved to: {output_path}")
        self.current_transcripts_path = output_path
        return output_path

    def _sanitize_filename(self, name: str) -> str:
        """Removes illegal characters for filenames."""
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[-\s]+", "_", name)
        return name.strip()

    def _generate_analysis(self, provider: str, model: str) -> str:
        """
        Internal: Uses in-memory links and transcript file to generate final analysis.
        """
        logger.info("--- Phase 2: Generating Analysis ---")

        if not self.current_transcripts_path or not os.path.exists(
            self.current_transcripts_path
        ):
            logger.error("No transcript file found to analyze.")
            return ""

        # Read the (potentially edited) transcript file
        with open(self.current_transcripts_path, encoding="utf-8") as f:
            raw_content = f.read()

        # --- A. Generate Main Analysis ---
        full_prompt = HMA_PROMPT.format(transcripts=raw_content)

        try:
            logger.info(f"Querying {provider} ({model}) for analysis...")
            analysis_text = self.llm.query(
                prompt=full_prompt, provider=provider, model=model
            )
        except Exception as e:
            logger.error(f"Analysis generation failed: {e}")
            return ""

        # --- B. Generate Title ---
        logger.info("Generating title for the analysis...")
        title_prompt = TITLE_GENERATION_PROMPT.format(
            analysis_text=analysis_text[:5000]
        )

        try:
            raw_title = self.llm.query(
                prompt=title_prompt, provider=provider, model="GPT-4o"
            )
            sanitized_title = self._sanitize_filename(raw_title)
        except Exception as e:
            logger.warning(f"Title generation failed: {e}. Using default.")
            raw_title = "Historical Materialist Analysis"
            sanitized_title = "analysis"

        # --- C. Append Sources (From Class Variable) ---
        sources_section = ""
        if self.research_links:
            sources_section = "\n\n---\n### Sources\n"
            for link in self.research_links:
                sources_section += f"- {link}\n"

        # --- D. Final Assembly & Save ---
        final_content = f"# {raw_title}\n\n{analysis_text}{sources_section}"

        date_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{date_str}-hma-{sanitized_title}.md"
        output_path = os.path.join(self.output_directory, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        logger.info(f"Analysis saved to: {output_path}")
        return output_path
