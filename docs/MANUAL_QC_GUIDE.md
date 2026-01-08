Here is your refined **Manual Quality Control (QC) Guide**.

This checklist is designed to be executed top-to-bottom. It verifies file integrity, data flow, and visual formatting without altering the existing filenames.

---

# 🛡️ Weekly Intel Orchestrator: Manual QC Checklist

**Tester:** __________________
**Run Date:** __________________
**Workspace:** `outputs/W{Week}-{Date}`

---

### **Phase 0: Initialization**

* [ ] **Config Load:** Confirm `config.yaml` was read without errors.
* [ ] **Workspace Creation:** Verify the directory `outputs/W{Week}-{Date}` exists.
* [ ] **Manager Init:** Logs show `Intel Pipeline Initialized`.

---

### **Phase 1: Global Overview (Baselines)**

* [ ] **1.1 Headlines (Mainstream):**
* File Exists: `p1_mainstream_headlines.json`
* Report Exists: `...-mainstream_headlines.md`


* [ ] **1.2 Narrative (Mainstream):**
* File Exists: `p1_mainstream_narrative.json`
* Report Exists: `...-mainstream_narrative.md`
* *QC Check:* Open report. Does it contain distinct paragraphs for regions like "China" or "Global"?


* [ ] **1.3 Geopolitical Ledger:**
* File Exists: `p1_geopolitical_ledger.json`
* Report Exists: `...-global_economic_snapshot.md`



---

### **Phase 2: News ETL (Raw Data)**

* [ ] **2.1 Data Ingestion:**
* **CRITICAL CSV:** Verify `stage_o3_enriched_articles_regions.csv` exists.
* *Data Check:* Open CSV. Verify columns `title`, `url`, `source`, and `region` are not empty.


* [ ] **2.2 Consolidation:**
* Report Exists: `...-analysis_headlines.md`



---

### **Phase 3: Summarization (Enrichment)**

* [ ] **3.1 Batch Processing:**
* Internal Checkpoint: `stage_04_enriched_articles_summarized.jsonl` exists in the workspace (or alongside input CSV).


* [ ] **3.2 Output Generation:**
* Folder: `outputs/.../summaries/` exists.
* Content: Folder is populated with `.md` files (e.g., `Intel-Brief-China.md`, `Intel-Brief-Global.md`).



---

### **Phase 4: Materialist Analysis (Deep Dive)**

* [ ] **4.1 Analysis Generation:**
* File Exists: `p4_materialist_analysis.json`
* Report Exists: `...-materialist_analysis.md`
* *QC Check:* Open report. Verify header structure matches regional summaries (e.g., `## China` followed by analysis).



---

### **Phase 5: Global Briefing (Synthesis)**

* [ ] **5.1 Synthesis:**
* File Exists: `p5_global_briefing.json`
* Report Exists: `...-global_briefing.md`


* [ ] **5.2 Structure QC:**
* Open the report.
* Verify each region has **two** distinct subsections:
* `**Mainstream Narrative:**`
* `**Strategic Analysis:**`





---

### **Phase 6: Multi-Lens Analysis (Refraction)**

* [ ] **6.1 Synthesis:**
* File Exists: `p6_multi_lens_analysis.json`
* Report Exists: `...-multi_lens_analysis.md`


* [ ] **6.2 Content QC:**
* Open the report.
* Verify regions contain HTML `<details>` tags (collapsible dropdowns).
* Verify all 9 lenses (e.g., "The Realist", "The GPE Perspective") are present inside the dropdowns.



---

### **Phase 7: Final Assembly (The Product)**

* [ ] **7.1 Artifact Creation:**
* Final File: `...-weekly-news.md` exists.



#### **7.2 Visual Verification (Open Final File)**

* [ ] **Navigation Bar:**
* Is it centered?
* Do the buttons look like grey/light blocks (Inline CSS check)?
* Does the "In-Depth Analysis" button exist at the end?


* [ ] **Region Headers:**
* Are regions sorted correctly (Global -> China -> East Asia ...)?


* [ ] **Narrative Flow:**
* Does each region start with `**Mainstream Narrative:**` followed by `**Strategic Analysis:**`?


* [ ] **Lenses:**
* Are the `<details>` dropdowns rendering correctly (clickable to expand)?


* [ ] **Article Sorting:**
* Check the article list at the bottom of a region.
* Are **Rank 1** articles listed before Rank 2 or 3?


* [ ] **Footer:**
* Is the "Sources" section present at the very bottom?



---

### **Test: Idempotency (The "Crash" Test)**

* [ ] **Re-run Logic:** Run the Orchestrator a second time immediately after a successful run.
* [ ] **Log Verification:**
* Phase 1: Shows `[SKIP] ... found in checkpoint`.
* Phase 2: Shows `[SKIP] ... found in checkpoint`.
* Phase 4: Shows `[SKIP] ... found in checkpoint`.
* Phase 5: Shows `[SKIP] ... found in checkpoint`.
* Phase 6: Shows `[SKIP] ... found in checkpoint`.
