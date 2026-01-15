
# Architecture Reference: The Manufacturing Pipeline

## 1. Architecture Philosophy
The system is designed as a **Unidirectional Data Pipeline**, modeled after a manufacturing assembly line. Data flows strictly from the external world (**Raw Material**) through a series of transformations (**Refinement**) until it is assembled into a final report (**Commodity**).

This architecture enforces strict **Separation of Concerns**:  `Review Required`
*   **Ingestion** is strictly separated from **Analysis**.
*   **Transformation** (1-to-1 mapping) is strictly separated from **Synthesis** (Many-to-1 reduction).
*   **Control Flow** is managed centrally by an Orchestrator.

### The Materialist Framework
*   **Phases 1-2 (Extraction):** Extract raw capital (data) from the external world.
*   **Phases 3-4 (Refinement):** Process that capital into intermediate goods (summaries, analysis).
*   **Phases 5-7 (Assembly):** Combine intermediate goods into the final commodity (The News Post) for distribution.

---

## 2. Core Components (The 5 Layers)

The system relies on five distinct component types. Each has a specific role, constraint, and testability profile.

### 1. Consolidators (The "Ingestion" Layer)
*   **Role:** The **Adapter**. Bridges the messy external world (APIs, HTML, RSS) and the clean internal application.
*   **Key Constraint:** **"No merging."** These are dumb pipes. They fetch data and return a standardized Data Class (e.g., `RawArticle`).
*   **Analogy:** The **Gatherer** who brings raw ingredients to the kitchen but doesn't cook them.

### 2. Generators (The "Transformation" Layer)
*   **Role:** The **Mapper**. Takes *one* unit of input and maps it to *one* unit of output using an LLM.
*   **Key Constraint:** **"Single LLM Call."** Critical for cost control and debugging. If a Generator fails, the specific prompt responsible is immediately identifiable.
*   **Analogy:** The **Prep Cook** who chops vegetables (Summarizer) or seasons meat (SnapshotGenerator) in isolation.

### 3. Synthesizers (The "Fusion" Layer)
*   **Role:** The **Reducer**. Takes outputs from multiple sources (Ingredients + Prep work) and fuses them into a new, higher-order product.
*   **Key Constraint:** **"Combining Information."** This is where the context window is utilized heavily and where the actual *business value* (insight) is generated.
*   **Analogy:** The **Head Chef** who combines ingredients to plate the final dish.

### 4. Orchestrator (The "Management" Layer)
*   **Role:** The **Director**. Configures the pipeline and manages hand-offs. It instantiates specific components and executes the workflow.
*   **Key Constraint:** **"Flow Control Only."** Contains no business logic or data manipulation. It simply moves data objects from A to B.
*   **Analogy:** The **Expediter** who coordinates timing between stations to ensure the meal comes together seamlessly.

### 5. Reporters (The "Presentation" Layer)
*   **Role:** The **Formatter**. Takes internal Data Models and converts them into human-readable strings (Markdown, HTML).
*   **Key Constraint:** **"Read-Only."** Never modifies data; only visualizes it. Returns a `ReportArtifact`.
*   **Analogy:** The **Waiter** who presents the finished dish to the customer.

---

## 3. The Workflow Map (7 Phases)

The pipeline executes in a specific dependency order. Phase 7 cannot exist without Phase 5, and Phase 5 cannot exist without Phases 1 and 2.

### Detailed Phase Logic

#### Phase 1: Global Overview (Automated)
*   **Goal:** Establish the baseline. What is the world saying (Mainstream) vs. what is the economic reality (Snapshot)?
*   **Operations:** Consolidate Mainstream Headlines; Generate Global Economic Snapshot.

#### Phase 2: News ETL (Semi-Automated)
*   **Goal:** Ingest the "Variable Input." This requires human curation to select high-value analysis articles.
*   **Operations:** Scrape selected URLs; Consolidate Analysis Headlines.

#### Phase 3: Summarization (Automated)
*   **Goal:** Compression. Transform high-volume text (articles) into high-value tokens (summaries) to reduce downstream synthesis costs.
*   **Operations:** Batch summarize articles by region.

#### Phase 4: Materialist Analysis (Automated)
*   **Goal:** Ideological Refinement. Interpret summaries through a historical materialist lens *before* the final briefing.
*   **Operations:** Generate Materialist Analysis by region.

#### Phase 5: Global Briefing (Automated)
*   **Goal:** Narrative Synthesis.
*   **Operations:** Combine Mainstream Headlines, Economic Snapshots, and Materialist Analysis into a cohesive regional briefing.

#### Phase 6: Multi-Lens Analysis (Automated)  `Review Required`
*   **Goal:** Comparative Analysis.
*   **Operations:** Identify contradictions between the Mainstream Narrative (P1) and the Analyst Perspective (P2). This generates the "Conflict Analysis."

#### Phase 7: Final Assembly (Automated)
*   **Goal:** Packaging.
*   **Operations:** Compile the Global Briefing, Multi-Lens Analysis, and Analysis Headlines into the final Markdown artifact.

---

## 4. Data Organization Strategy

The system organizes data into three distinct lifecycle stages `Review Required`:

1.  **Primary Source Data (Raw Material):**
    *   Raw HTML, JSON responses, and CSVs containing URLs.
    *   *Input for: Consolidators.*
2.  **LLM Generated Data (Intermediate Product):**
    *   Individual summaries, economic snapshots, and regional analysis blocks.
    *   *Input for: Synthesizers.*
3.  **Finished Products (Commodities):**
    *   Final Markdown reports and consolidated briefings ready for publication.
    *   *Output of: Reporters.*

---

## 5. Technical Interfaces

To maintain the Separation of Concerns, components adhere to strict interfaces `Review Required`:

*   **`ConsolidatorInterface`**
    *   **Method:** `consolidate()`
    *   **Behavior:** Fetches external data points and standardizes them into a list or object.
*   **`GeneratorInterface`**
    *   **Method:** `generate(input_data)`
    *   **Behavior:** Accepts a single data unit, calls the LLM, and returns a transformed unit.
*   **`SynthesizerInterface`**
    *   **Method:** `synthesize(list_of_inputs)`
    *   **Behavior:** Accepts multiple data objects and reduces them into a single narrative or analysis object.
*   **`ReporterInterface`**
    *   **Method:** `build_report(data_model)`
    *   **Behavior:** Formats the data model into a string (Markdown/HTML) and saves the artifact.
*   **`OrchestratorInterface`**
