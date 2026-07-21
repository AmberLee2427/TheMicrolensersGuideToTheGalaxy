"""Shared parsing helpers for marked exercise blocks.

The markers are deliberately located inside individual notebook cells.  Callers
must therefore parse one cell at a time; this prevents a malformed expression
from consuming cell boundaries or unrelated notebook content.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Literal


BlockType = Literal["code", "markdown"]


class ExerciseBlockError(ValueError):
    """Raised when exercise markers or reference files are ambiguous."""


@dataclass(frozen=True, order=True)
class ExerciseKey:
    """The unique identity of one exercise block."""

    filename: str
    block_type: BlockType
    part: str | None = None

    def describe(self) -> str:
        part = f" part {self.part}" if self.part else ""
        return f"{self.filename}{part} ({self.block_type})"


@dataclass(frozen=True)
class ExerciseBlock:
    """One complete marked block and its position within a cell or text file."""

    key: ExerciseKey
    text: str
    content: str
    start: int
    end: int
    indent: str


# Code markers must be adjacent lines with identical indentation.  In
# particular, the opening rule does not contain a leading ``.*?``: that was the
# source of the old cross-cell corruption bug.
CODE_PATTERN = re.compile(
    r"^(?P<indent>[ \t]*)#{22}[ \t]*\r?\n"
    r"(?P=indent)# EXERCISE: (?P<label>[^\r\n]+?)[ \t]*\r?\n"
    r"(?P=indent)(?P<separator>#-+[^\r\n]*)\r?\n"
    r"(?P<content>.*?)"
    r"^(?P=indent)#{22}[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


MD_PATTERN = re.compile(
    r"^(?P<indent>[ \t]*)<!-- EXERCISE: (?P<label>[^\r\n]+?) -->[ \t]*\r?\n"
    r"(?P<content>.*?)"
    r"^(?P=indent)<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->[ \t]*$",
    re.MULTILINE | re.DOTALL,
)

CODE_MARKER_LINE = re.compile(r"^[ \t]*# EXERCISE:[^\r\n]*$", re.MULTILINE)
MD_MARKER_LINE = re.compile(r"^[ \t]*<!-- EXERCISE:[^\r\n]*-->[ \t]*$", re.MULTILINE)


def parse_exercise_label(label: str) -> tuple[str, str | None]:
    """Split ``filename [PART: label]`` from an exercise marker."""

    filename, separator, part = label.strip().partition(" PART: ")
    filename = filename.strip()
    part = part.strip() if separator else None

    if not filename:
        raise ExerciseBlockError("Exercise marker has an empty filename.")
    if Path(filename).name != filename or filename in {".", ".."}:
        raise ExerciseBlockError(
            f"Exercise reference must be a plain filename, not {filename!r}."
        )
    if separator and not part:
        raise ExerciseBlockError(
            f"Exercise marker for {filename!r} has an empty part label."
        )

    return filename, part


def _blocks_from_matches(
    text: str, pattern: re.Pattern[str], block_type: BlockType
) -> list[ExerciseBlock]:
    blocks: list[ExerciseBlock] = []
    for match in pattern.finditer(text):
        filename, part = parse_exercise_label(match.group("label"))
        blocks.append(
            ExerciseBlock(
                key=ExerciseKey(filename, block_type, part),
                text=match.group(0),
                content=match.group("content").rstrip("\r\n"),
                start=match.start(),
                end=match.end(),
                indent=match.group("indent"),
            )
        )
    return blocks


def find_exercise_blocks(
    text: str, cell_type: BlockType | None = None
) -> list[ExerciseBlock]:
    """Find marked blocks in one cell or a fenced reference text file.

    ``cell_type`` should be supplied for notebook cells so code markers cannot
    be interpreted inside Markdown and vice versa.  Reference files may contain
    either type and are parsed with ``cell_type=None``.
    """

    blocks: list[ExerciseBlock] = []
    if cell_type in (None, "code"):
        blocks.extend(_blocks_from_matches(text, CODE_PATTERN, "code"))
    if cell_type in (None, "markdown"):
        blocks.extend(_blocks_from_matches(text, MD_PATTERN, "markdown"))
    blocks.sort(key=lambda block: block.start)

    marker_lines: list[re.Match[str]] = []
    if cell_type in (None, "code"):
        marker_lines.extend(CODE_MARKER_LINE.finditer(text))
    if cell_type in (None, "markdown"):
        marker_lines.extend(MD_MARKER_LINE.finditer(text))
    if len(marker_lines) != len(blocks):
        unparsed = []
        for marker in sorted(marker_lines, key=lambda item: item.start()):
            if not any(block.start <= marker.start() < block.end for block in blocks):
                line_number = text.count("\n", 0, marker.start()) + 1
                unparsed.append(f"line {line_number}: {marker.group(0).strip()}")
        detail = "; ".join(unparsed) if unparsed else "nested or overlapping markers"
        raise ExerciseBlockError(
            "Found an EXERCISE marker without one complete, cell-local marker "
            f"block ({detail})."
        )

    for previous, current in zip(blocks, blocks[1:]):
        if current.start < previous.end:
            raise ExerciseBlockError(
                f"Overlapping exercise markers: {previous.key.describe()} and "
                f"{current.key.describe()}."
            )

    return blocks


def index_unique_blocks(
    blocks: Iterable[ExerciseBlock], source: str
) -> dict[ExerciseKey, ExerciseBlock]:
    """Index blocks by key, rejecting duplicate filename/type/part markers."""

    indexed: dict[ExerciseKey, ExerciseBlock] = {}
    for block in blocks:
        if block.key in indexed:
            raise ExerciseBlockError(
                f"Duplicate exercise marker {block.key.describe()} in {source}."
            )
        indexed[block.key] = block
    return indexed


def replace_marked_blocks(
    text: str,
    blocks: Iterable[ExerciseBlock],
    replacements: dict[ExerciseKey, ExerciseBlock],
) -> str:
    """Replace known blocks in one cell, working backwards by character offset."""

    updated = text
    for target in sorted(blocks, key=lambda block: block.start, reverse=True):
        replacement = replacements.get(target.key)
        if replacement is None:
            continue
        if replacement.indent != target.indent:
            raise ExerciseBlockError(
                f"Indentation mismatch for {target.key.describe()}: notebook uses "
                f"{target.indent!r}, reference uses {replacement.indent!r}. "
                "Refresh both solution and reset references after moving a marker."
            )
        updated = updated[: target.start] + replacement.text + updated[target.end :]
    return updated


def render_reference_file(blocks: Iterable[ExerciseBlock]) -> str:
    """Render marked blocks as fenced text suitable for a reference file."""

    rendered: list[str] = []
    for block in blocks:
        language = "python" if block.key.block_type == "code" else "markdown"
        rendered.append(f"```{language}\n{block.text.rstrip()}\n```")
    return "\n\n".join(rendered) + "\n"
