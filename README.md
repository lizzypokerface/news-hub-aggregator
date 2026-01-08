# news-hub-aggregator

The Comprehensive News Aggregator. A sophisticated intelligence pipeline that aggregates, synthesizes, and reports on global news using a 7-phase manufacturing process.

## Getting Started

### Requirements

- **Python 3.13+**
- **API Keys:**
  - **Poe API Key** (for LLM inference via Gemini/Claude)
  - **YouTube Data API Key** (for headline aggregation)

### Setup

1. **Create a Virtual Environment:**

    In the root directory, run:

    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows use: venv\Scripts\activate
    ```

2. **Install Poetry:**

    Install [Poetry](https://python-poetry.org/docs/cli/) for dependency management:

    ```bash
    pip install -U pip setuptools
    pip install poetry
    ```

3. **Install Dependencies:**

    Use Poetry to install project dependencies:

    ```bash
    poetry install --no-root
    ```

    *(Note: This installs pandas, selenium, pyyaml, openai, and other core libraries).*

4. **Set Up Pre-Commit Hooks:**

    Install [pre-commit](https://pre-commit.ci/) hooks for static tests:

    ```bash
    pre-commit install
    ```

---

### Configuration

The system relies on a `config.yaml` file to define API keys and target sources.

1.  Create a file named `config.yaml` in the root directory.
2.  Add your API keys and source lists (YouTube channels, websites, RSS feeds).

**Example `config.yaml` structure:**

```yaml
api_keys:
  poe_api: "YOUR_POE_KEY_HERE"
  youtube_api: "YOUR_YOUTUBE_KEY_HERE"

output_directory: "outputs"

sources:
  - name: "Global News Network"
    url: "[https://www.youtube.com/@ExampleNewsChannel](https://www.youtube.com/@ExampleNewsChannel)"
    type: "datapoint"
    format: "video"
  - name: "Economic Analysis Blog"
    url: "[https://example-economic-blog.com/](https://example-economic-blog.com/)"
    type: "analysis"
    format: "article"

```

---

### Running the Main Program

Execute `main.py` to start the intelligence manufacturing pipeline.

**Standard Run (Default Config & Date):**

```bash
python main.py

```

**Run with Custom Configuration:**
Useful for testing different source lists or API keys.

```bash
python main.py --config my_custom_config.yaml

```

**Run for a Specific Date (Backfill):**
Useful if you want to regenerate a report for a past week.

```bash
python main.py --date 2025-06-01

```

**Debug Mode:**
Enables verbose logging to troubleshoot ETL or API issues.

```bash
python main.py --debug

```

---

### Artifacts & Outputs

All intelligence products are saved in the `outputs/` folder, organized by week.

* **Weekly Workspace:** `outputs/W{Week}-{Date}/`
* **Final Report:** `outputs/W{Week}-{Date}/{Date}-weekly-news.md`

### Pipeline Architecture

The Orchestrator runs a 7-phase process to manufacture the final report:

1. **Global Overview:** Generates mainstream & economic baselines.
2. **News ETL:** Scrapes analysis articles (Manual intervention may be required for captchas).
3. **Summarization:** Summarizes articles in batches using the LLM.
4. **Materialist Analysis:** Applies a historical materialist lens to the summaries.
5. **Global Briefing:** Synthesizes mainstream narratives vs. strategic reality.
6. **Multi-Lens Analysis:** Refracts global events through 9 distinct ideological lenses.
7. **Final Assembly:** Compiles all artifacts into the final Markdown post.
