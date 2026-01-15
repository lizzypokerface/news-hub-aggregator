# Mainstream News Analysis Prompt Guide

## 1. Overview

This document details the logic and structural design of the **Mainstream News Analysis Prompt** used in the Crucible Framework.

This prompt functions as a **Sanitization and Aggregation Engine** (Phase 1b). Unlike the Global Briefing prompt which synthesizes multiple layers of reality, this prompt focuses exclusively on **Layer 2 (Mainstream Media)**. Its purpose is to ingest raw, noisy headlines and article snippets and convert them into clean, readable summaries of the "Official Narrative" organized by region.

It serves as the "Control Group" for the system—establishing exactly what the establishment media is reporting before deeper analysis is applied.

---

## 2. The Prompt Artifact

**Prompt Name:** `MAINSTREAM_PROMPT_TEMPLATE`
**Target Model:** `Gemini-3-Pro`
**Python Controller:** `MainstreamNewsSynthesizer`

```text
You are a Mainstream News Analyst. Your task is to synthesize a collection of headlines and summaries from major global news outlets into a clean, objective situational report.

**Constraint:** Report ONLY what the mainstream sources are saying. Do not add critical analysis, debunking, or alternative theories. Your goal is to capture the "Official Narrative" or "Chatter" exactly as it is being presented to the public.

---
**PREDEFINED REGIONS (Use these categories ONLY):**
    - 'Global': Use for articles involving multiple distinct regions.
    - 'China': For articles primarily about China.
    - 'East Asia': For Japan, South Korea, North Korea.
    - 'Singapore': Use ONLY for articles specifically about Singapore.
    - 'Southeast Asia': For countries like Vietnam, Thailand, Indonesia, Malaysia, Philippines.
    - 'South Asia': For India, Pakistan, Bangladesh, Sri Lanka.
    - 'Central Asia': For Kazakhstan, Uzbekistan, etc.
    - 'Russia': For articles primarily about Russia.
    - 'West Asia (Middle East)': For countries like Lebanon, Iran, Saudi Arabia, Palestine, etc.
    - 'Africa': For countries on the African continent.
    - 'Europe': For European countries, including the UK and the EU.
    - 'Latin America & Caribbean': For countries in Central and South America, and the Caribbean.
    - 'North America': For the United States and Canada.
    - 'Oceania': For Australia, New Zealand, Pacific Islands.
    - 'Unknown': Use ONLY if you cannot determine the region with confidence.

**Region Order:** You MUST follow this strict order for the regions.
---
**METHODOLOGY:**
1.  **Read and Categorize:** Assign each input event to a predefined region.
2.  **Synthesize by Region:** Group the points for each region.
3.  **Summarize:** Write a single, coherent paragraph (approx 150-200 words) synthesizing the mainstream reporting.
4.  **Tone:** Neutral, journalistic, summary style.

**OUTPUT FORMAT (Strict Markdown):**
- Use Level 2 Markdown headers for regions (e.g., `## Global`).
- Follow with the summary paragraph.
- Separate regions with newlines.

---
**INPUT MAINSTREAM HEADLINES:**
{input_text}

**REGIONAL SUMMARY:**
```

---

## 3. The Narrative Logic (Theoretical Framework)

The core logic of this prompt is **Narrative Isolation**.

### The "Mirror" Function
The prompt is explicitly instructed: *"Report ONLY what the mainstream sources are saying. Do not add critical analysis."*
*   **Goal:** To create a high-fidelity mirror of the current media landscape.
*   **Why this matters:** To perform effective materialist analysis (in later stages), the system must first clearly define the "Superstructure" (the ideology/narrative). If the AI begins debunking the news at this stage, we lose the ability to see the propaganda clearly. This prompt ensures the "Official Story" is preserved in its purest form.

### Regional Categorization
The prompt forces the AI to act as a classifier. Raw news feeds are often chaotic and unorganized. This prompt imposes a geopolitical structure (China, Global, West Asia, etc.) onto unstructured text, preparing it for downstream processing.

---

## 4. Input Data Architecture

This prompt handles a single, high-volume stream of text.

| Variable Name | Content Description | Limit |
| :--- | :--- | :--- |
| `input_text` | Aggregated headlines and snippets from Reuters, AP, BBC, CNN, etc. | **500,000 characters**. (Truncated by Python controller to ensure safety, though the model can handle more). |

---

## 5. Structural Design & Parsing Constraints

The prompt is engineered for reliability in parsing, ensuring the Python backend (`_parse_llm_output`) can extract structured data objects (`MainstreamEventEntry`).

### The Region Schema
The prompt provides a strict list of 15 categories (14 geographic + 1 "Unknown").
*   **Specific Definitions:** The prompt clarifies potentially ambiguous regions (e.g., defining "East Asia" vs "Southeast Asia" and isolating "Singapore").
*   **"Unknown" Fallback:** A safety valve is included for inputs that cannot be geographically placed, preventing hallucination or misclassification.

### Regex-Ready Headers
The output format is strictly controlled to allow for regex splitting:
1.  **Header Requirement:** `Use Level 2 Markdown headers for regions (e.g., ## Global)`.
2.  **Parsing Logic:** The Python script splits the text using `re.split(r"(?m)^##\s+(.+)$", text)`.
    *   This captures the Region Name as group 1.
    *   The subsequent text block is captured as the content.
3.  **Content Block:** The prompt requests a "single, coherent paragraph (approx 150-200 words)." This standardization ensures the UI looks consistent regardless of how many articles were processed.

### Error Handling
*   **Empty Input Check:** The controller checks if `mainstream_content` is `< 50` characters to prevent wasting tokens on empty prompts.
*   **Exception Handling:** If the LLM fails or produces unparseable text, the system returns an empty list rather than crashing.
