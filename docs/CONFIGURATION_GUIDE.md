# Configuration Guide (`config.yaml`)

This document explains how to configure the inputs, API keys, and intelligence sources for the analysis engine.

## 1. Core Settings

* **`api_keys`**: Stores authentication tokens for external services (YouTube Data API, Poe, etc.).
* **`input_directory`**: The folder containing raw context files (e.g., transcripts, news).
* **`output_directory`**: Where the final reports and logs will be saved.

## 2. Intelligence Sources

The `sources` section is the heart of the engine. Each entry represents a feed of information to be ingested.

**Required Fields:**
* **`name`**: The display name of the source.
* **`url`**: A valid URL (YouTube channel or website).
* **`type`**: `analysis` (opinion/breakdown) or `datapoint` (raw reporting).
* **`format`**: `youtube` or `webpage`.
* **`rank`**: An integer (1-5) defining the source's analytical weight.

### The Ranking System (Weighted Trust)

The `rank` field determines how the engine weighs the information provided by a source.

* **Rank 1: The Signal.** These sources cut through the noise to reveal the actual mechanics of what’s happening. When they speak, I listen because they provide the "why" that others miss.
* **Rank 2: High-Level Intel.** Deeply insightful, but I cross-reference their claims against Rank 1 to see where the narrative might still be influencing the analysis.
* **Rank 3: Informed Reporting.** Provides solid information and context, but begins to lean into the general consensus. Good for detail, but requires a critical eye.
* **Rank 4: The Official Record.** Mostly data and facts that follow the mainstream storyline. It tells you what is being said, but rarely what is actually happening behind the scenes.
* **Rank 5: The Echo Chamber.** Pure mainstream narrative and raw chatter. This is the "public version" of events—useful only to see what the masses are being told.

---

## 3. Validation

To ensure your configuration is valid before running the main application, use the validation script:

```bash
python scripts/validate_config.py --config config.yaml
