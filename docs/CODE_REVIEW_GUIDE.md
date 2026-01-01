# Code Review Guide: Engineering Excellence & Capital Stewardship

This dual-lens approach helps engineers understand *what* to do, while simultaneously understanding *why* it matters for the business's long-term production capacity.

- **Standard Engineering Terminology** (for clarity and industry alignment)
- **Materialist/Economic Framing** (to highlight business value and capital stewardship).

## 1. Philosophy: The Dual Purpose

Code review is not merely a quality gate; it is the primary mechanism for maintaining the health of our software.

* **The Engineering Lens:** We review to share knowledge, catch bugs, and maintain code quality.
* **The Economic Lens:** We review to act as **stewards of our Fixed Capital**. The codebase is the machinery of our production. If we allow it to rust (technical debt), the cost of future labor increases, and our ability to produce value degrades.

**Goal:** To merge high-quality engineering with ruthless protection of the business's means of production.

---

## 2. The Pre-Review Checklist (Context & Conditions)

Before reviewing the code (the diff), you must understand the conditions of its production.

| Item | Engineering Context | Economic Context |
| --- | --- | --- |
| **Ticket / Issue** | Does this solve the user's problem? | Does this create **Use-Value**? If the output has no utility, the labor is wasted. |
| **CI / CD** | Are tests passing? | Is the **Assembly Line** functional? Do not inspect goods from a broken machine. |
| **Description** | Does it explain the "How"? | Does it justify the modification to the means of production? |
| **Scope / Size** | Is it under ~400 lines? | Is the change **Atomic**? Large batches hide defects and increase the cognitive cost of review labor. |

---

## 3. The Review Hierarchy (The Material Audit)

Review in passes. Prioritize structural integrity over aesthetic preferences.

### Pass 1: Architecture & Value (The Structural Audit)

* **Correctness (Use-Value):** Does the code do what the business needs? If the ticket asks for a hammer and the PR builds a drill, the **Use-Value** is zero, regardless of code quality.
* **Security (Risk Management):** Does this expose the firm to liability? (e.g., SQL injection, exposed keys).
* **Efficiency (Constant Capital):** Does this code consume unnecessary resources (CPU, RAM)? Inefficient code increases the "overhead" cost of every unit produced.
* **Flexibility (Future Production):** Does this introduce rigid dependencies? Brittle code **fetters future production**, making it harder to pivot or scale.

### Pass 2: Implementation & Logic (Maintenance of Machinery)

* **Edge Cases:** Has the author accounted for variance? (e.g., API failures, null states). Robust machinery does not jam when fed irregular raw materials.
* **Complexity:** Is the code overly clever? **Simplicity is an asset.** Complex code depreciates faster because it requires highly specialized labor to repair.
* **Testing:** Are there tests? Do they verify the commodity’s function, or are they mere theater?

### Pass 3: Style & Polish (Standardization)

* **Consistency:** Adhere to the Style Guide. Standardization reduces **socially necessary labor time**—when every file looks the same, any worker can pick up the tool and start working immediately without "context switching" costs.

---

## 4. The Art of the Comment (Dialectics)

Critique is a dialectical process—thesis (code), antithesis (review), synthesis (better solution).

### Rule 1: Critique the Code, Not the Worker

* **Standard:** "You broke the login service."
* **Synthesized:** "This change appears to destabilize the login service, which would halt our production line."

### Rule 2: Interrogate the Logic

Frame feedback as questions to encourage the author to analyze their own labor.

* **Standard:** "Change this List to a Set."
* **Synthesized:** "Since we check for existence often here, would a `Set` improve our computational efficiency compared to a `List`?"

### Rule 3: Distinguish Impact (Blockers vs. Nitpicks)

* **[BLOCKER]:** "Security vulnerability detected. This endangers our capital assets. Cannot merge."
* **[NIT]:** "Minor typo. Fix if you have time, but do not delay the deployment cycle."

---

## 5. Case Studies: Applying the Dual Lens

### Scenario A: The "Resource Hog"

**The Code:** `return db.query("SELECT * FROM users")` (Returns 100k rows)

* **The Comment:** "I noticed this queries the entire table. While this works in development, I am concerned this consumes too much memory (**Constant Capital**) in production. Can we implement pagination to optimize resource usage?"

### Scenario B: The "Ghost Variable"

**The Code:** `x = 5 # Set retry limit`

* **The Comment:** "[NIT] Could we rename `x` to `MAX_RETRIES`? Clear naming reduces the **labor time** required for the next developer to understand this logic."

### Scenario C: The "Magic Number"

**The Code:** `if user.type == 2: ...`

* **The Comment:** "It's not clear what `type == 2` represents. Should we use an Enum (e.g., `UserType.ADMIN`)? Explicit code reduces **maintenance overhead**."

---

## 6. Final Sanity Check

Before you click **Approve**, ask the ultimate question:

> **"If I am on call and this machinery breaks at 3 AM, will I be able to repair it efficiently?"**

* **Yes:** The addition to our capital is sound. Authorize the merge.
* **No:** The change introduces liability. Request changes.

### 7. Glossary of Terms

| Term | Domain | Definition | Application in Code Review |
| --- | --- | --- | --- |
| **Fixed Capital** | Economic | Assets used in the production process (machinery, tools) that are not consumed in a single cycle. | **The Codebase.** We maintain it so it continues to produce value over time. |
| **Means of Production** | Economic | The physical and non-physical inputs used to produce economic value. | The combination of our **Servers, Code, and Dev Tools**. |
| **Use-Value** | Economic | The utility of consuming a good; the ability of a good to satisfy a want or need. | **Correctness.** Does the software actually solve the user's problem? |
| **Exchange Value** | Economic | The quantitative aspect of value; what a commodity is worth in trade. | **Business Value / Profit.** The revenue generated by the feature. |
| **Constant Capital** | Economic | Value invested in means of production (machines, raw materials) that does not create new value but is preserved in the product. | **System Resources (CPU/RAM).** Inefficient code consumes more constant capital per unit of output. |
| **Socially Necessary Labor Time** | Economic | The average time required to produce a commodity under normal conditions. | **Standardization.** Consistent code style reduces the time any average developer needs to understand and modify a file. |
| **Technical Debt** | Engineering | The implied cost of additional rework caused by choosing an easy/limited solution now instead of a better approach. | **Rust/Depreciation.** Allowing the means of production to degrade, increasing the "friction" of future labor. |
| **Atomic Commit** | Engineering | A change that is irreducible; it does one thing completely and nothing else. | **Batch Size.** Small, focused PRs reduce cognitive load and hide fewer defects. |
| **Fettering** | Economic | When production relations (social organization) restrict the development of productive forces (technology). | **Rigid Dependencies.** Bad architecture that blocks ("fetters") our ability to scale or pivot in the future. |
| **CI/CD** | Engineering | Continuous Integration / Continuous Deployment. | **The Assembly Line.** The automated system that verifies quality and delivers the commodity. |
