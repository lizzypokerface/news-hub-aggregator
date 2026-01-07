"""
CONTEXT GENERATOR SCRIPT
------------------------
Purpose:
    This script looks inside a specific folder (like ./src), reads all relevant
    code files, and combines them into a single Markdown (.md) file.

    It generates:
    1. A visual directory tree of your project.
    2. The contents of every file, wrapped in code blocks.

    This output is optimized for pasting into Large Language Models (LLMs)
    like Gemini or GPT to give them full context of your codebase.

How to Run:
    Open your terminal/command prompt and run:

    python scripts/generate_context.py ./src

    Optional: Specify an output filename
    python scripts/generate_context.py ./src --output my_project_context.md

Requirements:
    - Python 3.13+
    - No external libraries required (uses standard library only).
"""

import os
import argparse
from pathlib import Path

# --- Configuration ---
# Folders to explicitly ignore
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "migrations",
}

# File extensions to include (add more if needed)
INCLUDE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".sql",
    ".toml",
    ".txt",
}


def generate_tree(start_path):
    """Generates a string directory tree structure."""
    tree_str = f"Directory Tree for: {start_path}\n\n"
    start_path = Path(start_path)

    for root, dirs, files in os.walk(start_path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        level = root.replace(str(start_path), "").count(os.sep)
        indent = " " * 4 * (level)
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        subindent = " " * 4 * (level + 1)
        for f in files:
            if Path(f).suffix in INCLUDE_EXTENSIONS:
                tree_str += f"{subindent}{f}\n"

    return tree_str


def collect_files(start_path):
    """Yields file paths and contents."""
    start_path = Path(start_path)

    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in INCLUDE_EXTENSIONS:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        # Calculate path relative to the input folder for cleaner headers
                        rel_path = file_path.relative_to(start_path.parent)
                        yield rel_path, content
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate code files into a single Markdown file for LLM context."
    )
    parser.add_argument("target_dir", help="The directory to scan (e.g., ./src)")
    parser.add_argument(
        "--output", "-o", default="codebase_context.md", help="Output file name"
    )

    args = parser.parse_args()

    target_path = Path(args.target_dir)

    if not target_path.exists():
        print(f"Error: Directory '{target_path}' not found.")
        return

    print(f"Scanning {target_path}...")

    with open(args.output, "w", encoding="utf-8") as outfile:
        # 1. Write the preamble and directory tree
        outfile.write(f"# Codebase Context: {target_path.name}\n\n")
        outfile.write("## 1. Directory Structure\n```text\n")
        outfile.write(generate_tree(target_path))
        outfile.write("```\n\n")
        outfile.write("---\n\n## 2. File Contents\n\n")

        # 2. Write file contents
        file_count = 0
        for rel_path, content in collect_files(target_path):
            extension = rel_path.suffix.lstrip(".")
            # Format: File path header followed by code block
            outfile.write(f"### `{rel_path}`\n\n")
            outfile.write(f"```{extension}\n")
            outfile.write(content)
            outfile.write("\n```\n\n")
            file_count += 1

    print(f"Success! Combined {file_count} files into '{args.output}'.")


if __name__ == "__main__":
    main()
