# Intel Brief Prompt Guide

## 1. Overview

This document details the logic and structural design of the **Intel Brief Prompt** used in the Crucible Framework.

This prompt functions as a **Transformation Engine** (Phase 3). While earlier phases aggregate broad narratives, this prompt operates at the *atomic level*, processing individual source documents one by one. Its purpose is to convert raw, unstructured text (articles, reports, transcripts) into a standardized "Triage Card."

It is designed to solve the problem of information overload by forcing every document into a strict, scannable format that emphasizes *implications* over mere summarization.

---

## 2. The Prompt Artifact

**Prompt Name:** `SUMMARY_PROMPT_TEMPLATE`
**Target Model:** `Gemini-3-Flash` (Chosen for speed and cost-efficiency)
**Python Controller:** `IntelBriefGenerator`

```text
**Role:** You are an elite Intelligence Analyst processing raw source documents for a high-level decision-maker.

**Objective:** Create a "Triage Card" that allows the user to instantly assess the document's value, tone, and critical intel without reading the full text.

**Constraints:**
1.  **Input:** You will process ONE document at a time.
2.  **Brevity:** The final output must be readable in under 60 seconds.
3.  **Structure:** Follow the exact "Output Format" below. Do not deviate.
4.  **Implications:** Every point must include a *forward-looking* implication (what happens next?), not just a summary of the past.

**Output Format:**

**Triage Tags**
* **Type:** [Choose one: Strategic Analysis / Battlefield Report / Economic Forecast / Historical Context / Opinion / News Report]
* **Region:** [Primary region discussed]
* **Sentiment:** [Choose one: Optimistic / Cautiously Optimistic / Neutral / Critical / Alarmist]
* **Key Entities:** [List top 3-4 specific people, organizations, or places mentioned]

**5-Point Intel Brief**
* **[HEADLINE 1 in Bold]:** [The core fact or claim].
    * *Implication:* [One sentence prediction: What happens next because of this? What is the consequence?]

(Repeat for max 5 points. If the document is short or low-signal, use fewer than 5 points. Never invent points.)

**Document Content:**
{content}
```

---

## 3. The Narrative Logic (Theoretical Framework)

The core logic of this prompt is **Predictive Triage**.

### The "So What?" Constraint
Standard summaries often fail because they only repeat *what happened*. This prompt enforces a "So What?" logic via the `Implication` constraint:
*   *Constraint:* "Every point must include a forward-looking implication."
*   *Goal:* To shift the user's focus from passive consumption of news to active anticipation of consequences.

### The Triage Card Metaphor
The prompt treats information like emergency medicine triage. Before the user commits time to reading a 2,000-word article, the AI provides metadata tags:
*   **Type:** Helps the user filter (e.g., "I only want to read Economic Forecasts").
*   **Sentiment:** Provides immediate emotional context (e.g., "Is this article Alarmist?").
*   **Entities:** Identifies key players immediately.

---

## 4. Input Data Architecture

This prompt operates on a 1:1 basis (One Prompt : One Article).

| Variable Name | Content Description | Limit |
| :--- | :--- | :--- |
| `content` | The raw text body of a single `Article` object. | **Variable**. The Python controller checks for a minimum length (`MINIMUM_CONTENT_LENGTH = 150`) to avoid hallucinating summaries for empty inputs. |

---

## 5. Structural Design & Parsing Constraints

Unlike the Mainstream News prompt which requires strict Regex parsing, this prompt is designed for **Human Readability**. The output is stored directly as a string (`article.summary`) rather than parsed into a data object.

### Formatting Rules
1.  **Bold Headlines:** Used to make the text scannable.
2.  **Nested Bullets:** The structure (Fact -> Implication) is visually enforced by indentation.
3.  **Tagging System:** The "Triage Tags" section acts as a structured header block.

### Post-Processing (`_clean_llm_output`)
The Python controller performs a light cleaning pass on the output:
*   **Quote Removal:** It strips lines starting with `>` to ensure the AI isn't just quoting the prompt back to the user.
*   **Whitespace:** It trims excess whitespace to ensure the card fits neatly in the UI.

### Error Handling
*   **Short Content:** If content is < 150 characters, the generator aborts early (`Content too short`) to save API costs.
*   **Generation Failure:** If the API call fails, the summary is replaced with a visible error marker (`**GENERATION FAILED**`) so the user knows the data is missing, rather than seeing a blank space.
