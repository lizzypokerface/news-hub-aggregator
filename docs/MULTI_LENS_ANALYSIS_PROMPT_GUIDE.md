# Multi-Lens Analysis Prompt Guide

## 1. Overview

This document details the logic, theoretical derivation, and structural design of the **Batch Lens Prompt** used in the Crucible Framework.

The purpose of this prompt is to act as an ideological prism. Instead of asking the AI for a single "objective" summary (which often defaults to a liberal institutionalist bias inherent in training data), this prompt forces the model to roleplay 9 distinct, conflicting worldviews. This "Cubist" approach ensures that the final analysis captures the full spectrum of geopolitical reality—from the material economic base to the superstructural narratives of culture and law.

---

## 2. The Prompt Artifact

**Prompt Name:** `BATCH_LENS_PROMPT`
**Target Model:** `Gemini-3-Pro` (High reasoning capability required)

```text
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
```

## 3. Derivation of the Lenses (Theoretical Framework)

The 9 lenses in the prompt are not random; they are rigorously derived from the **Analytical Models** document. Each lens corresponds to a specific way of viewing the relationship between the **Economic Base** (material reality) and the **Superstructure** (ideology/politics).

### Lens 1: The GPE Perspective (The Base)
*   **Source Model:** The Geopolitical Economist (GPE) Analyst.
*   **Theoretical Role:** The "Diagnostic Engine." It analyzes the **Economic Base**.
*   **Prompt Instruction:** "Historical Materialism. Class interests, imperialism, contradictions."
*   **Why this matters:** This lens strips away rhetoric to reveal *Cui Bono?* (Who benefits?). It focuses on financial warfare, resource extraction, and the "real economy" rather than diplomatic niceties.

### Lens 2: The Market Fundamentalist (The Capitalist Superstructure)
*   **Source Model:** The Market Fundamentalist.
*   **Theoretical Role:** The "Investor's Eye." It represents the ideology of the transnational capitalist class.
*   **Prompt Instruction:** "Efficiency, incentives, 'market corrections'."
*   **Why this matters:** This lens predicts how global capital will react. It views state intervention as "inefficient" and interprets crises merely as "market corrections," providing insight into the incentive structures of the enemy.

### Lens 3: The Liberal Institutionalist (The Official Narrative)
*   **Source Model:** The Liberal Institutionalist.
*   **Theoretical Role:** The "Diplomat." It represents the official **Superstructure** of the US-led order.
*   **Prompt Instruction:** "International law, norms, human rights, 'rules-based order'."
*   **Why this matters:** This lens maps the moral and legal justifications the hegemon will use. It identifies the specific "rules" or "norms" that will be weaponized against sovereign states.

### Lens 4: The Realist (The Security State)
*   **Source Model:** The Realist.
*   **Theoretical Role:** The "General." It analyzes the **Political Superstructure** (the state system) detached from economics.
*   **Prompt Instruction:** "Power distribution, security, national interest."
*   **Why this matters:** It provides a hard-power filter, ignoring moral arguments to focus on balance of power, alliances, and security dilemmas. It is the antidote to wishful thinking.

### Lens 5: The Civilizational Nationalist (The Identity Lens)
*   **Source Model:** The Civilizational Nationalist.
*   **Theoretical Role:** The "Demagogue." It obscures class conflict (Base) with cultural conflict (Superstructure).
*   **Prompt Instruction:** "Identity, culture, 'clash of civilizations'."
*   **Why this matters:** It captures the visceral, emotional forces that drive populations—forces that purely economic analysis often misses. It highlights how identity is weaponized for "divide and conquer."

### Lens 6: The Post-Structuralist Critic (The Deconstructor)
*   **Source Model:** The Post-Structuralist Critic.
*   **Theoretical Role:** The "Academic." It critiques the **Superstructure** itself.
*   **Prompt Instruction:** "Deconstruct language, narratives, power of discourse."
*   **Why this matters:** It dissects propaganda. Instead of analyzing the event, it analyzes the *language* used to describe the event, revealing how terms like "terrorist" or "freedom" are used to manufacture consent.

### Lens 7: The Singaporean Strategist (The Small State Survivor)
*   **Source Model:** The Singaporean Strategist.
*   **Theoretical Role:** The "Pragmatist." A model of a state managing its Base-Superstructure relation for survival.
*   **Prompt Instruction:** "Principled Pragmatism. Survival, foundations, omnidirectional engagement."
*   **Why this matters:** It offers a specific strategic playbook for non-great powers: build internal resilience (Base) to maximize external agency (Superstructure).

### Lens 8: The CPC Strategist (The Long-Term Planner)
*   **Source Model:** The CPC Strategist.
*   **Theoretical Role:** The "Developer." A model where the Superstructure (Party) actively shapes the Base.
*   **Prompt Instruction:** "Dialectical Materialism w/ Chinese Characteristics. Development, stability."
*   **Why this matters:** It provides the perspective of the primary challenger to the current order. It focuses on long-term planning, stability maintenance, and development as the primary form of security.

### Lens 9: The Fusion (The Sovereign Practitioner)
*   **Source Model:** The Fusion (The Sovereign GPE Practitioner).
*   **Theoretical Role:** The "Synthesizer."
*   **Prompt Instruction:** "The 'Sovereign Practitioner'. Concrete, ruthless, actionable strategy."
*   **Why this matters:** This is the goal of the entire system. It combines the diagnostic map of GPE with the actionable ruthlessness of Realism to produce concrete strategy.

---

## 4. Structural Design of the Prompt

The prompt is engineered to handle **Batch Processing**, analyzing multiple regions in a single inference pass.

### The "Cubist" Approach
The prompt explicitly uses the metaphor of "Multi-Lens (Cubist) Analysis." In art, Cubism depicts subjects from a multitude of viewpoints simultaneously to represent the subject in a greater context.
*   **Traditional AI:** Gives one "averaged" view (usually Liberal Institutionalist).
*   **Crucible AI:** Gives 9 distinct views, allowing the user to see the contradictions between them.

### Input Context Integration
The `{input_context}` variable is a massive concatenation of four distinct data streams:
1.  **Economics:** Raw data on trade, debt, and markets.
2.  **Mainstream:** Official news and Western media narratives.
3.  **Analysis:** Existing geopolitical commentary.
4.  **Materialist:** Specialized anti-imperialist analysis.

The prompt forces the AI to look at this *same* dataset but interpret it differently for each lens. For example, when looking at a trade deal in the context:
*   **Lens 1 (GPE)** sees neo-colonial extraction.
*   **Lens 2 (Market)** sees efficiency and growth.
*   **Lens 3 (Liberal)** sees a triumph of international cooperation.

### Output Formatting
The prompt enforces a **Strict Markdown** structure (`## Region`, `### Lens`). This is not for aesthetics, but for programmatic parsing. It allows the system to mechanically separate the "Fusion" strategy from the "Civilizational" rhetoric, ensuring that the final report is structured and navigable.
