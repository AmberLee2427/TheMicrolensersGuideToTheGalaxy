"""Fill or reset notebook exercises without relying on notebook cell numbers.

Each notebook cell is scanned independently for named exercise markers.  Only
the text between a matched marker pair is replaced; cells can be freely added,
removed, or reordered without affecting the workflow.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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
    replace_marked_blocks,
)


@dataclass(frozen=True)
class LocatedBlock:
    """An exercise block and the notebook cell containing it."""

    cell_index: int
    block: ExerciseBlock


def _cell_source(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def _set_cell_source(cell: dict, source: str) -> None:
    """Update a cell while preserving whether its source used a list or string."""

    if isinstance(cell.get("source", ""), list):
        cell["source"] = source.splitlines(keepends=True)
    else:
        cell["source"] = source


def collect_notebook_blocks(notebook: dict, source: str) -> list[LocatedBlock]:
    """Collect unique exercise blocks from all code and Markdown cells."""

    located: list[LocatedBlock] = []
    seen: dict[ExerciseKey, int] = {}

    for index, cell in enumerate(notebook.get("cells", [])):
        cell_type = cell.get("cell_type")
        if cell_type not in {"code", "markdown"}:
            continue
        blocks = find_exercise_blocks(_cell_source(cell), cell_type)
        for block in blocks:
            if block.key in seen:
                raise ExerciseBlockError(
                    f"Duplicate exercise marker {block.key.describe()} in {source}: "
                    f"cells {seen[block.key]} and {index}."
                )
            seen[block.key] = index
            located.append(LocatedBlock(index, block))

    return located


def _load_reference_blocks(
    reference_dir: Path,
    keys: Iterable[ExerciseKey],
    skip_missing: bool,
    allowed_missing: set[str],
) -> dict[ExerciseKey, ExerciseBlock]:
    """Resolve every notebook key to one unambiguous reference block."""

    replacements: dict[ExerciseKey, ExerciseBlock] = {}
    files: dict[str, dict[ExerciseKey, ExerciseBlock]] = {}
    problems: list[str] = []

    for key in keys:
        reference_path = reference_dir / key.filename
        if not reference_path.exists():
            if skip_missing or key.filename in allowed_missing:
                print(
                    f"[replacement] No reference file for {key.describe()}; "
                    "leaving the notebook block unchanged."
                )
                continue
            problems.append(f"missing reference file {reference_path}")
            continue

        if key.filename not in files:
            text = reference_path.read_text(encoding="utf-8")
            try:
                files[key.filename] = index_unique_blocks(
                    find_exercise_blocks(text), str(reference_path)
                )
            except ExerciseBlockError as exc:
                problems.append(str(exc))
                files[key.filename] = {}

        replacement = files[key.filename].get(key)
        if replacement is None:
            if skip_missing or key.filename in allowed_missing:
                print(
                    f"[replacement] No matching block for {key.describe()} in "
                    f"{reference_path}; leaving it unchanged."
                )
                continue
            problems.append(
                f"no matching block for {key.describe()} in {reference_path}"
            )
            continue

        replacements[key] = replacement

    if problems:
        details = "\n  - ".join(problems)
        raise ExerciseBlockError(f"Cannot replace exercises:\n  - {details}")

    return replacements


def _write_json_atomic(path: Path, notebook: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(notebook, handle, ensure_ascii=False, indent=1)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def replace_solutions(
    old_notebook: str,
    new_notebook: str,
    reference_dir: str = "Notebooks/Exercises/",
    destructive: bool = True,
    skip_missing: bool = False,
    allowed_missing: Iterable[str] | None = None,
) -> None:
    """Replace marked exercise blocks using references and save a new file.

    ``destructive`` is retained for API compatibility with the former
    text-conversion implementation.  There is no intermediate text file in the
    cell-aware implementation, so its value has no effect.

    Args:
        old_notebook: Input ``.ipynb`` notebook or legacy ``.txt`` export.
        new_notebook: Output path with the same suffix as the input.
        reference_dir: Directory containing one reference file per exercise.
        destructive: Deprecated compatibility argument; ignored.
        skip_missing: Leave all missing references unchanged when true.
        allowed_missing: Specific reference filenames that may be absent.
    """

    del destructive
    input_path = Path(old_notebook)
    output_path = Path(new_notebook)
    references = Path(reference_dir)
    allowed = set(allowed_missing or ())

    if not input_path.exists():
        raise FileNotFoundError(f"Input notebook {input_path} does not exist.")
    if not references.is_dir():
        raise NotADirectoryError(f"Reference directory {references} does not exist.")
    if input_path.suffix.lower() not in {".ipynb", ".txt"}:
        raise ValueError("Input must be a .ipynb notebook or .txt export.")
    if output_path.suffix.lower() != input_path.suffix.lower():
        raise ValueError("Input and output must use the same .ipynb or .txt suffix.")

    if input_path.suffix.lower() == ".ipynb":
        notebook = json.loads(input_path.read_text(encoding="utf-8"))
        located = collect_notebook_blocks(notebook, str(input_path))
        if not located:
            raise ExerciseBlockError(f"No exercises found in {input_path}.")

        replacements = _load_reference_blocks(
            references,
            (item.block.key for item in located),
            skip_missing,
            allowed,
        )

        by_cell: dict[int, list[ExerciseBlock]] = {}
        for item in located:
            by_cell.setdefault(item.cell_index, []).append(item.block)

        for cell_index, blocks in by_cell.items():
            cell = notebook["cells"][cell_index]
            updated = replace_marked_blocks(_cell_source(cell), blocks, replacements)
            _set_cell_source(cell, updated)

        _write_json_atomic(output_path, notebook)
    else:
        text = input_path.read_text(encoding="utf-8")
        blocks = find_exercise_blocks(text)
        if not blocks:
            raise ExerciseBlockError(f"No exercises found in {input_path}.")
        index_unique_blocks(blocks, str(input_path))
        replacements = _load_reference_blocks(
            references,
            (block.key for block in blocks),
            skip_missing,
            allowed,
        )
        _write_text_atomic(output_path, replace_marked_blocks(text, blocks, replacements))

    print(
        f"Replaced {len(replacements)} exercise block(s) in {input_path}; "
        f"wrote {output_path}."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill or reset marked exercises in a notebook."
    )
    parser.add_argument("input_notebook")
    parser.add_argument("output_notebook")
    parser.add_argument(
        "reference_dir",
        nargs="?",
        default="Notebooks/Exercises/",
        help="Answer or reset reference directory (default: Notebooks/Exercises/).",
    )
    parser.add_argument(
        "--allow-missing",
        action="append",
        default=[],
        metavar="FILENAME",
        help="Leave this specifically named missing reference unchanged; repeatable.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.keep:
        print("[replacement] --keep is no longer needed; no temporary file is created.")
    if args.force:
        print(
            "[replacement] --force is a deprecated alias for allowing all missing "
            "references. Prefer --allow-missing FILENAME."
        )
    replace_solutions(
        args.input_notebook,
        args.output_notebook,
        args.reference_dir,
        skip_missing=args.force,
        allowed_missing=args.allow_missing,
    )


if __name__ == "__main__":
    main()
