# The Geopolitical Ledger Prompt Guide

**Version:** 1.0  
**Framework:** Critical Geopolitical Economy  
**Last Updated:** 2026-01-05

---

## Table of Contents
- [The Geopolitical Ledger Prompt Guide](#the-geopolitical-ledger-prompt-guide)
  - [Table of Contents](#table-of-contents)
  - [1. Overview](#1-overview)
  - [2. Usage Instructions](#2-usage-instructions)
    - [Prerequisites](#prerequisites)
    - [Input Variable](#input-variable)
  - [3. The Prompt](#3-the-prompt)
  - [4. Output Schema Definition](#4-output-schema-definition)
  - [5. Integration Guide](#5-integration-guide)
  - [Appendix A: The Analyst's Handbook (Interpretive Guide)](#appendix-a-the-analysts-handbook-interpretive-guide)
    - [Part 1: The Three Core Lenses](#part-1-the-three-core-lenses)
      - [Lens 1: Sovereignty — The Freedom to Act](#lens-1-sovereignty--the-freedom-to-act)
      - [Lens 2: The Creditor/Debtor Axis](#lens-2-the-creditordebtor-axis)
      - [Lens 3: The Core/Periphery Structure](#lens-3-the-coreperiphery-structure)
    - [Part 2: The Three-Step Analytical Method](#part-2-the-three-step-analytical-method)
    - [Part 3: Example Interpretations](#part-3-example-interpretations)

---

## 1. Overview

**The Geopolitical Ledger** is a specialized prompt designed to instruct an LLM (with web browsing capabilities) to generate a high-density table of global economic data.

Unlike standard financial reports, this prompt forces the AI to adopt a **Critical Geopolitical Economy** framework. It rejects neutral observation in favor of analyzing power dynamics. It interprets raw data to reveal:
*   **Sovereignty:** The capacity of a nation to act independently.
*   **Hierarchy:** The distinction between the "Core" (Global North) and the "Periphery" (Global South).
*   **Dependency:** The flow of capital and influence between Creditor and Debtor nations.

**Primary Use Case:** This prompt generates a structured **Context Layer**. The output is intended to be fed into downstream LLM agents (e.g., a Strategy Bot, Policy Analyst, or RAG system) to provide a materialist grounding for complex queries.

---

## 2. Usage Instructions

### Prerequisites
*   **AI Model:** Must have active web browsing/search capabilities (e.g., ChatGPT-4o, Claude 3.5 Sonnet, Perplexity).
*   **Context Window:** Standard context window is sufficient.

### Input Variable
The prompt requires a single variable to be defined by the user before execution:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `[Month Year]` | The reference date for the data search. | `January 2026` |

---

## 3. The Prompt

> **Copy the code block below into your AI agent.** Ensure you replace `[INSERT MONTH YEAR HERE]` with your desired date.

```text
You are an expert political economist and data analyst, in the vein of thinkers like Michael Hudson and Radhika Desai. Your task is to compile a snapshot of the global economy that reveals underlying power structures, dependency dynamics, and a nation's policy space.

**Reference Date:** [INSERT MONTH YEAR HERE]

The entire response must be titled: **Global Economic and Geopolitical Snapshot (as of [INSERT MONTH YEAR HERE])**

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

    > Note on Key Trends for GCC: These creditor nations are executing a high-stakes transition, using immense hydrocarbon wealth to pivot from being security-dependent, resource-based economies into diversified, multi-aligned global investment hubs.

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
```

## 4. Output Schema Definition

The output is a Markdown table designed for machine readability and high information density.

| Column | Data Point | Geopolitical Significance |
| :--- | :--- | :--- |
| **Country** | Nation Name | The subject of analysis. |
| **GDP Growth & Stance** | YoY Growth % | Reveals the *trajectory* (growing/shrinking) and the *method* (spending/cutting). |
| **Inflation & Unemployment** | CPI & Jobless Rate | Reveals *internal social pressure* and stability risks. |
| **Current Account** | % of GDP | **The Pivot Point.** <br>• *Surplus:* Creditor (Power/Influence). <br>• *Deficit:* Debtor (Dependency/Vulnerability). |
| **Govt. Debt** | % of GDP | Analyzed via the **Sovereignty Lens**. <br>• High debt in foreign currency = Vulnerability. <br>• High debt in own currency = Policy Tool. |
| **Military Spend** | % of GDP | Reveals the *true* priority of the state (Guns vs. Butter). |
| **Sovereignty Indicators** | Policy Rate & FX Reserves | • *Policy Rate:* Rule-Maker vs. Rule-Taker. <br>• *FX Reserves:* The "financial shield" against sanctions. |

---

## 5. Integration Guide

Once the LLM generates the table, this data becomes the "World State" for downstream tasks.

**Example System Prompt for a Downstream Bot:**

> "You are a geopolitical strategist. I will provide you with a 'Global Economic Snapshot' table. Use the data in this table as your ground truth.
>
> When answering questions about a specific country, check their **Current Account** and **Sovereignty Indicators** first. If a country has low FX reserves and a current account deficit, assume they are vulnerable to external pressure. If a country is a Creditor with high military spending, assume they are projecting power."

---

## Appendix A: The Analyst's Handbook (Interpretive Guide)

*The following guide explains the theoretical framework used to interpret the data generated by this prompt. It is derived from the "Veritas Data" methodology.*

### Part 1: The Three Core Lenses
Before analyzing any data, you must wear the right analytical glasses.

#### Lens 1: Sovereignty — The Freedom to Act
Sovereignty is the measure of a nation's agency in the international system.
*   **Monetary Sovereignty:** Does the nation's debt exist in a currency it controls? (e.g., USA, Japan). If yes, they cannot be forced into bankruptcy. If they borrow in foreign currency, they are less sovereign.
*   **Financial Shield (FX Reserves):** A nation's war chest. Massive reserves (e.g., China) allow a country to defend its currency and survive sanctions. Small reserves signal vulnerability.
*   **Policy Independence:** Is the central bank a "rule-maker" or a "rule-taker"? The US Fed is the rule-maker. Others often must raise rates to protect against capital flight, even if it hurts their domestic economy.

#### Lens 2: The Creditor/Debtor Axis
The global economy is divided between those who sell more than they buy (Creditors) and those who buy more than they sell (Debtors).
*   **Creditor Nations (Surplus):** The world's lenders (e.g., China, Germany, Gulf States). Their power lies in funding projects and exerting influence over debtors.
*   **Debtor Nations (Deficit):** The world's borrowers (e.g., Brazil, India). They are structurally dependent on foreign capital.
*   **The US Exception:** The US is a Debtor, but because it issues the global reserve currency, its deficit is a source of power ("Exorbitant Privilege"), not weakness.

#### Lens 3: The Core/Periphery Structure
*   **The Core (Global North):** The historical centers of capital and rule-making.
*   **The Periphery (Global South):** Nations historically integrated as suppliers. The primary 21st-century story is the challenge to this structure by rising powers (BRICS+).

### Part 2: The Three-Step Analytical Method
When reading the generated table, apply these steps:

1.  **The Sovereignty Check (Who holds the power?)**
    *   *Rule-Maker or Rule-Taker?* Check the currency and central bank status.
    *   *How Big is the Shield?* Check FX Reserves.

2.  **The Economic Engine (How does it make a living?)**
    *   *Creditor or Debtor?* Check the Current Account.
    *   *What Powers Growth?* Is it export-led, commodity-dependent, or consumption-driven?

3.  **The Stress Test & Priorities (Vulnerabilities and Goals)**
    *   *Internal Pressure:* Check Unemployment and Inflation.
    *   *External Pressure:* Check Debt-to-GDP (through the sovereignty lens).
    *   *True Priority:* Check Military Spending. This reveals where the state's focus truly lies.

### Part 3: Example Interpretations

*   **United States:** A **Privileged Debtor**. High debt is manageable due to sovereignty. High military spending underwrites the global system.
*   **Brazil:** A **Constrained Peripheral**. High interest rates are required to attract foreign capital, strangling domestic growth. Policy is constrained by external dependency.
*   **China:** A **Rising Challenger**. Massive Creditor status and FX reserves provide a shield. High military spending and industrial policy reflect an ambition to restructure the global hierarchy.
