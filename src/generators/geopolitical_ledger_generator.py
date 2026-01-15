import logging
from datetime import datetime

from interfaces import BaseGenerator
from interfaces.models import GeopoliticalLedger

logger = logging.getLogger(__name__)

# --- Configuration Constants ---
MODEL_NAME = "Claude-Opus-4.5"  # web-search capable model on Poe
PROMPT_TEMPLATE = """
You are an expert political economist and data analyst, in the vein of thinkers like Michael Hudson and Radhika Desai. Your task is to compile a snapshot of the global economy that reveals underlying power structures, dependency dynamics, and a nation's policy space.

**Reference Date:** {month_year}

The entire response must be titled: **Global Economic and Geopolitical Snapshot (as of {month_year})**

**Instructions:**

1. **Analytical Lens:**
    Your analysis must be framed through the lens of geopolitical economy. The goal is not just to present data, but to use data to highlight creditor/debtor relationships, fiscal pressures (austerity), national priorities (military vs. social spending), and economic sovereignty. The notes in each cell are the most important part of this task.

2. **Economies to Analyze:**
    You must analyze the following countries, presenting them in the specified order and under their respective subheadings in the final table.

    **Part A: Global North Economies**
    - **G7 Members:** United States, Japan, Germany, United Kingdom, France, Canada
    - **Other Key Developed Economies:** Australia, South Korea

    **Part B: Global South Economies**
    - **BRICS Members:** China, India, Brazil, South Africa, Russia
    - **Key ASEAN Economies:** Indonesia, Vietnam, Singapore
    - **Key Gulf Economies (GCC):** Saudi Arabia, United Arab Emirates (UAE), Qatar, Kuwait

    > Note on Key Trends for GCC (if applicable): These creditor nations are executing a high-stakes transition, using immense hydrocarbon wealth to pivot from being security-dependent, resource-based economies into diversified, multi-aligned global investment hubs.

3. **Required Indicators and In-Cell Notes:**
    For each country, find the most recent data available as of the **Reference Date**. The key is to provide a concise, interpretive note within the same cell as the data point.

    - **GDP Growth (%) & Stance:** Provide the latest YoY growth rate. In the note, characterize the government's fiscal stance (e.g., "Stimulus," "Fiscal Consolidation," "Austerity Measures").
    - **Inflation & Unemployment (%):** Combine the latest CPI and Unemployment rates. The note should interpret the social impact (e.g., "High inflation eroding wages," "Stable but high structural unemployment").
    - **Current Account (% of GDP):** This is a critical indicator. State the balance as a % of GDP. The note must classify the nation as a **"Creditor Nation"** (surplus) or **"Debtor Nation"** (deficit) and what this implies (e.g., "reliant on foreign capital," "exporting capital").
    - **Govt. Debt (% of GDP):** Provide the Debt-to-GDP ratio. The note should contextualize this level (e.g., "High, creating austerity pressure," "Manageable due to sovereign currency," "Risk of external leverage").
    - **Military Spend (% of GDP):** Use the latest SIPRI data available. The note should compare this to global averages or national priorities (e.g., "Exceptionally high, reflects global projection," "Low, prioritizes domestic development").
    - **Sovereignty Indicators:** Provide the central bank's **Policy Rate** and the total value of **Foreign Exchange Reserves**. The note must assess the country's monetary sovereignty (e.g., "High reserves provide buffer," "Rate policy constrained by Fed," "Dependent on USD swaps").

4. **Output Format:**
    - Present the final output as a single, well-formatted Markdown table.
    - The table columns must be exactly: `Country`, `GDP Growth (%) & Stance`, `Inflation & Unemployment (%)`, `Current Account (% of GDP)`, `Govt. Debt (% of GDP)`, `Military Spend (% of GDP)`, and `Sovereignty Indicators`.
    - Use bold subheadings within the table for "Part A: Global North Economies" and "Part B: Global South Economies" to structure the output clearly.
    - The interpretive notes are mandatory and should be concise.

    **Example of a cell's content:**
    - For Current Account: `3.1% (Debtor Nation, reliant on foreign capital to fund deficits)`
    - For Govt. Debt: `125% (High, but manageable as debt is issued in its own sovereign currency)`

5. **Data Sourcing and Constraints:**
    - **Sources:** Prioritize IMF, World Bank, OECD, and national statistics offices. For military spending, **SIPRI** is the primary source.
    - **Conciseness:** Do not add any introductory text or concluding summaries. The output should be only the title and the single table.
    - **Missing Data:** If a specific data point cannot be reliably found, use "N/A" but still attempt to provide an analytical note if possible.
"""


class GeopoliticalLedgerGenerator(BaseGenerator):
    """
    Generates a high-density table of global economic data using a Critical Geopolitical Economy framework.
    """

    def generate(self, run_date: datetime) -> GeopoliticalLedger:
        """
        Args:
            run_date: The date for which to generate the snapshot (usually datetime.now()).

        Returns:
            GeopoliticalLedger object containing the Markdown table.
        """
        month_year = run_date.strftime("%B %Y")

        logger.info(f"Generating Geopolitical Ledger for {month_year}...")

        try:
            prompt = PROMPT_TEMPLATE.format(month_year=month_year)

            # Use the injected LLM client
            # We assume 'poe' provider with web search capabilities is ideal here.
            ledger_content = self.llm_client.query(
                prompt, provider="poe", model=MODEL_NAME
            )

            return GeopoliticalLedger(date=run_date, ledger_content=ledger_content)

        except Exception as e:
            logger.error(f"Failed to generate Geopolitical Ledger: {e}")
            return GeopoliticalLedger(
                date=run_date, ledger_content="Error generating ledger."
            )
