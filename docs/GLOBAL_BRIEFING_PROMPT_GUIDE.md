# Global Briefing Prompt Guide

## 1. Overview

This document details the logic and structural design of the **Global Briefing Prompt** used in the Crucible Framework.

Unlike the "Multi-Lens" prompt which explores ideological diversity, this prompt is a **Synthesis Engine**. Its purpose is to ingest massive amounts of raw intelligence (up to 3.5 million characters of text) and distill it into a high-level situation report. It enforces a strict separation between the "Official Story" (Mainstream Narrative) and the "Material Reality" (Strategic Analysis), ensuring the user can clearly see the gap between propaganda and ground truth.

---

## 2. The Prompt Artifact

**Prompt Name:** `BRIEFING_PROMPT_TEMPLATE`
**Target Model:** `Gemini-3-Pro` (Selected for massive context window capacity)
**Python Controller:** `GlobalBriefingSynthesizer`

```text
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
```

## 3. The Dual-Layer Logic (Theoretical Framework)

The core logic of this prompt is the dialectical contrast between the **Superstructure** and the **Base**. The prompt explicitly instructs the AI to separate these two realities rather than blending them.

### Section 1: Mainstream Narrative (The Superstructure)
*   **Source Data:** Primarily `Layer 2` (Mainstream Headlines).
*   **Goal:** To capture the "Official Story." This is what the world *says* is happening. It captures the justifications, the diplomatic rhetoric, and the emotional framing used by dominant media outlets.
*   **Why this matters:** A strategist must know what the public believes and what cover stories are being employed by state actors.

### Section 2: Strategic Analysis (The Base)
*   **Source Data:** Synthesizes `Layer 1` (Economics), `Layer 3` (Geopolitical Analysis), and `Layer 4` (Materialist Analysis).
*   **Goal:** To describe what is *actually* happening. This focuses on trade flows, resource control, military movements, and class dynamics.
*   **Why this matters:** This provides the "ground truth" that often contradicts the mainstream narrative. The value of the briefing lies in the **delta** between Section 1 and Section 2.

---

## 4. Input Data Architecture

The prompt is designed to handle a massive context window, ingesting four distinct "Layers" of intelligence simultaneously.

| Layer | Variable Name | Content Description | Theoretical Role |
| :--- | :--- | :--- | :--- |
| **1** | `econ_text` | Raw economic data, commodities, stock markets, trade stats. | **The Economic Base.** The raw numbers that drive conflict. |
| **2** | `mainstream_text` | Reuters, AP, CNN, BBC, State Media headlines. | **The Superstructure.** The narrative veil. |
| **3** | `analysis_text` | Think tank reports, specialized geopolitical newsletters. | **The Strategic Layer.** Conventional interpretation of state actions. |
| **4** | `materialist_text` | Critical theory, anti-imperialist analysis, Marxist critique. | **The Critical Layer.** Analysis of contradictions and imperialism. |

---

## 5. Structural Design & Parsing Constraints

The prompt is rigorously engineered to support programmatic parsing by the Python backend (`_parse_llm_output`). The AI is not free to choose its formatting; it must adhere to a strict Markdown schema.

### The 14-Region Standard
The prompt enforces a specific list of 14 regions (`REQUIRED_REGIONS`).
*   **Constraint:** The AI must generate a section for every region in the list, even if data is sparse.
*   **Fallback:** The Python controller (`_validate_and_fill_regions`) includes a safety mechanism. If the AI skips a region (e.g., "Oceania"), the code detects the missing key and inserts a placeholder entry to prevent the frontend from crashing.

### Regex-Ready Headers
The output format is designed to be sliced by Regular Expressions:
1.  **Region Splitting:** The code splits text by `^##\s+(.+)$`. This requires the AI to use Level 2 Headers for Region names.
2.  **Section Extraction:** The code searches for `### Mainstream Narrative` and `### Strategic Analysis`.
    *   *Critical Note:* If the AI varies the header (e.g., writes "### Strategic Overview" instead of "Analysis"), the Regex will fail, and the content will be lost. The prompt emphasizes "EXACTLY as follows" to mitigate this risk.

### Context Window Management
The Python script truncates inputs to ensure they fit within the model's limits:
*   Mainstream/Analysis/Materialist text: Capped at 1,000,000 characters each.
*   Economic text: Capped at 500,000 characters.
*   **Total Capacity:** The prompt is designed for "Long Context" models (Gemini-1.5/3 Pro classes) capable of processing millions of tokens, allowing for a truly comprehensive global synthesis that was previously impossible.
