"""Save marked exercise blocks from a notebook into reference files.

Exercise identity comes from the marker filename, block type, and optional part
label.  Notebook cell positions are deliberately irrelevant: every code or
Markdown cell is inspected independently, so cells may be added, removed, or
reordered without changing this workflow.
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
import json
import os
from pathlib import Path
import tempfile
from typing import Iterable

from exercise_blocks import (
    ExerciseBlock,
    ExerciseBlockError,
    ExerciseKey,
    find_exercise_blocks,
    index_unique_blocks,
    render_reference_file,
)
from replacement import collect_notebook_blocks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Save marked exercises from a notebook into reference files."
    )
    parser.add_argument("notebook", help="Solved or learner notebook (.ipynb or .txt).")
    parser.add_argument("output_dir", help="Directory where reference files are written.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing reference files after all markers are validated.",
    )
    return parser.parse_args()


def collect_blocks(path: Path) -> list[ExerciseBlock]:
    """Read and validate every marked block in a notebook or text export."""

    if path.suffix.lower() == ".ipynb":
        notebook = json.loads(path.read_text(encoding="utf-8"))
        return [item.block for item in collect_notebook_blocks(notebook, str(path))]

    if path.suffix.lower() == ".txt":
        blocks = find_exercise_blocks(path.read_text(encoding="utf-8"))
        index_unique_blocks(blocks, str(path))
        return blocks

    raise ValueError("Notebook must be a .ipynb notebook or .txt export.")


def group_blocks_by_filename(
    blocks: Iterable[ExerciseBlock],
) -> "OrderedDict[str, list[ExerciseBlock]]":
    """Group blocks in notebook order while retaining their exact markers."""

    grouped: "OrderedDict[str, list[ExerciseBlock]]" = OrderedDict()
    seen: set[ExerciseKey] = set()
    for block in blocks:
        if block.key in seen:
            raise ExerciseBlockError(
                f"Duplicate exercise marker {block.key.describe()} while saving."
            )
        seen.add(block.key)
        grouped.setdefault(block.key.filename, []).append(block)
    return grouped


def _write_text_atomic(path: Path, text: str) -> None:
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise


def write_reference_files(
    output_dir: Path,
    grouped: "OrderedDict[str, list[ExerciseBlock]]",
    *,
    force: bool = False,
) -> list[Path]:
    """Write validated references, refusing accidental overwrites by default."""

    output_dir.mkdir(parents=True, exist_ok=True)
    targets = [output_dir / filename for filename in grouped]
    existing = [target for target in targets if target.exists()]
    if existing and not force:
        names = "\n  - ".join(str(path) for path in existing)
        raise FileExistsError(
            "Refusing to overwrite existing exercise references:\n"
            f"  - {names}\n"
            "Review the source notebook, then re-run with --force and inspect the diff."
        )

    for target, blocks in zip(targets, grouped.values()):
        _write_text_atomic(target, render_reference_file(blocks))
    return targets


def save_references(
    notebook: str | Path,
    output_dir: str | Path,
    *,
    force: bool = False,
) -> list[Path]:
    """Public API for validating and saving notebook exercise references."""

    notebook_path = Path(notebook)
    destination = Path(output_dir)
    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook {notebook_path} does not exist.")

    grouped = group_blocks_by_filename(collect_blocks(notebook_path))
    if not grouped:
        raise ExerciseBlockError(f"No exercise markers found in {notebook_path}.")
    return write_reference_files(destination, grouped, force=force)


def main() -> None:
    args = parse_args()
    written = save_references(args.notebook, args.output_dir, force=args.force)
    print(f"Wrote {len(written)} reference file(s) to {Path(args.output_dir)}.")


if __name__ == "__main__":
    main()
