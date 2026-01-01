# Testing Guide & Configuration

This document outlines how to run the unit test suite for this project, including the necessary environment setup and the configuration required to resolve Python import paths between the `src` and `test` directories.

## 1. Setup Requirements

Before running tests, ensure your environment is set up with the necessary dependencies.

```bash
pip install pytest requests

```

This setup verifies that the logic works correctly with mock data before attempting real API calls.

## 2. Project Structure & Import Logic

This project uses a sibling directory structure (source code in `src/` and tests in `test/`).

### The Import Problem

If you attempt to run tests without specific configuration, you may encounter the following error:
`ModuleNotFoundError: No module named 'modules'`

**Why this happens:**
Source files (e.g., `RegionCategorizer`) import generic modules using `from modules.llm_client import ...`. When running `pytest` from the project root, Python does not automatically see inside the `src/` folder, causing imports to fail.

### The Solution: `test/conftest.py`

To fix this, we use a `conftest.py` file to inject the `src` directory into the Python path.

**Action Required:**
Ensure a file named `conftest.py` exists in the `test/` folder with the following content:

```python
# test/conftest.py
import sys
import os

# Calculate the absolute path to the 'src' folder
# (Goes up one level from 'test' directory, then down into 'src')
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))

# Add 'src' to the system path if it's not already there
if src_path not in sys.path:
    sys.path.insert(0, src_path)

```

**How it Works:**

1. **Automatic Execution:** `pytest` automatically detects and runs `conftest.py` before executing tests.
2. **Path Injection:** It adds `../src` to `sys.path`, making the source folder "visible" to Python.
3. **Enables Imports:** This allows test files to successfully import from `src` (e.g., `from modules.region_categoriser import ...`) even though they are located in the sibling `test/` directory.

## 3. How to Run the Tests

Tests should be executed from the **project root directory** (the parent of both `src` and `test`).

### Option A: Using `python -m pytest` (Recommended)

This method is preferred as it automatically adds the current directory to your Python path, which helps resolve basic import issues.

```bash
python -m pytest test/

```

### Option B: Using `pytest` directly

If you have `pytest` installed globally or in your active virtual environment path:

```bash
pytest test/

```


## 4. Known Issues & Learnings

### The "Double Import Trap" (Namespace Mismatch)

**Symptom:**
You apply a `@patch` to a class, but your test still executes the real code (e.g., calling the real LLM instead of the mock).

**Cause:**
This happens when you import a module using a different path than the one you patch. Python treats `src.modules.my_module` and `modules.my_module` as two completely separate objects in memory.

* **Your Test Import:** `from src.modules.region_categoriser import RegionCategoriser`
* **Your Patch:** `@patch("modules.region_categoriser.LLMClient")`

In this scenario, you successfully patched the `modules...` copy, but your test is running the `src.modules...` copy, which remains unpatched.

**Solution:**
Always align your test imports with your patch paths. Since `conftest.py` adds `src` to the system path, you should drop the `src.` prefix in your test imports:

```python
# INCORRECT (Causes mismatch with patch "modules.region_categoriser...")
from src.modules.region_categoriser import RegionCategoriser

# CORRECT (Matches the patch path)
from modules.region_categoriser import RegionCategoriser

```
