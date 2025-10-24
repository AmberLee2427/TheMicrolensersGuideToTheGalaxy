"""
Create or refresh solution reference files from a fully solved notebook.

The script walks through the exercise markers in a notebook (either the
`.ipynb` source or an intermediate `.txt` export), captures each solution
block, and writes the corresponding fenced content into the files under
`Notebooks/Exercises`. It honours both code and markdown exercises, and
supports multipart exercises with alphanumeric part labels (e.g. `PART: 1a`).
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path
import re
import sys
from typing import Dict, List, Tuple

import nb4llm

# Matches code exercise blocks, preserving leading indentation and the separator line.
CODE_PATTERN = re.compile(
    r"(?P<indent>[ \t]*)######################\n"
    r"(?P=indent)# EXERCISE: (?P<filename>.*?)(?: PART: (?P<part>[^\n]+))?\n"
    r"(?P=indent)(?P<separator>#-+[^\n]*)\n"
    r"(?P<content>.*?)(?:\r?\n)?(?P=indent)######################",
    re.DOTALL,
)

# Matches markdown exercise blocks.
MD_PATTERN = re.compile(
    r"<!-- EXERCISE: (?P<filename>.*?)(?: PART: (?P<part>[^\n]+))? -->\n"
    r"(?P<content>.*?)"
    r"<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->",
    re.DOTALL,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract solved exercises from a notebook into reference files."
    )
    parser.add_argument("notebook", help="Path to the solved notebook (.ipynb or .txt).")
    parser.add_argument("output_dir", help="Directory where solution files are written.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the temporary txt export if it already exists.",
    )
    return parser.parse_args()


def get_text_notebook_path(notebook_path: Path, force: bool) -> Tuple[Path, bool]:
    """
    Return a path to a txt representation of the notebook.

    For `.ipynb` inputs we emit a sibling file named `<stem>.__solutions_tmp__.txt`.
    When the file already exists the caller can opt into overwriting it with
    `--force`.
    """
    if notebook_path.suffix.lower() == ".ipynb":
        temp_txt = notebook_path.with_name(f"{notebook_path.stem}.__solutions_tmp__.txt")
        if temp_txt.exists():
            if force:
                temp_txt.unlink()
            else:
                raise FileExistsError(
                    f"Temporary txt notebook {temp_txt} already exists. "
                    "Re-run with --force to overwrite it."
                )
        nb4llm.convert_ipynb_to_txt(str(notebook_path), str(temp_txt))
        return temp_txt, True

    if notebook_path.suffix.lower() == ".txt":
        return notebook_path, False

    raise ValueError("Notebook must be a .ipynb or .txt file.")


def extract_solution_blocks(notebook_text: str) -> "OrderedDict[str, List[Dict[str, str]]]":
    """
    Scan the notebook text for exercise blocks and group them by filename.
    """
    matches: List[Tuple[int, str, re.Match[str]]] = []
    matches.extend((m.start(), "code", m) for m in CODE_PATTERN.finditer(notebook_text))
    matches.extend((m.start(), "markdown", m) for m in MD_PATTERN.finditer(notebook_text))
    matches.sort(key=lambda item: item[0])

    solutions: "OrderedDict[str, List[Dict[str, str]]]" = OrderedDict()
    for _, block_type, match in matches:
        filename = match.group("filename").strip()
        part = match.group("part")
        part = part.strip() if part else None

        if filename not in solutions:
            solutions[filename] = []

        if block_type == "code":
            solutions[filename].append(
                {
                    "type": "code",
                    "part": part,
                    "indent": match.group("indent"),
                    "separator": match.group("separator"),
                    "content": match.group("content").rstrip("\r\n"),
                }
            )
        else:
            solutions[filename].append(
                {
                    "type": "markdown",
                    "part": part,
                    "content": match.group("content").rstrip("\r\n"),
                }
            )

    return solutions


def render_solution_file(filename: str, blocks: List[Dict[str, str]]) -> str:
    """
    Render the list of blocks for a solution file back to fenced markdown.
    """
    rendered_blocks: List[str] = []

    for block in blocks:
        part_suffix = f" PART: {block['part']}" if block.get("part") else ""

        if block["type"] == "code":
            indent = block["indent"]
            separator = block["separator"]
            content = block["content"]

            code_lines = [
                "```python",
                f"{indent}######################",
                f"{indent}# EXERCISE: {filename}{part_suffix}",
                f"{indent}{separator}",
            ]

            if content:
                code_lines.append(content)
            else:
                code_lines.append("")

            code_lines.append(f"{indent}######################")
            code_lines.append("```")
            rendered_blocks.append("\n".join(code_lines))
        else:
            content = block["content"]
            md_lines = [
                "```markdown",
                f"<!-- EXERCISE: {filename}{part_suffix} -->",
            ]
            if content:
                md_lines.append(content)
            else:
                md_lines.append("")
            md_lines.append("<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->")
            md_lines.append("```")
            rendered_blocks.append("\n".join(md_lines))

    return "\n\n".join(rendered_blocks) + "\n"


def write_solution_files(
    output_dir: Path, solutions: "OrderedDict[str, List[Dict[str, str]]]"
) -> None:
    for name, blocks in solutions.items():
        target = output_dir / name
        target.write_text(render_solution_file(name, blocks), encoding="utf-8")


def main() -> None:
    args = parse_args()
    notebook_path = Path(args.notebook).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook {notebook_path} does not exist.")

    output_dir.mkdir(parents=True, exist_ok=True)

    txt_path, cleanup = get_text_notebook_path(notebook_path, args.force)

    try:
        notebook_text = txt_path.read_text(encoding="utf-8")
        solutions = extract_solution_blocks(notebook_text)

        if not solutions:
            print("No exercise markers found; no files were written.", file=sys.stderr)
            return

        write_solution_files(output_dir, solutions)
        print(f"Wrote {len(solutions)} solution file(s) to {output_dir}.")
    finally:
        if cleanup and txt_path.exists():
            txt_path.unlink()


if __name__ == "__main__":
    main()
