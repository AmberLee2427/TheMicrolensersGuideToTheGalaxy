import copy
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exercise_blocks import (  # noqa: E402
    ExerciseBlockError,
    find_exercise_blocks,
    index_unique_blocks,
)
from replacement import collect_notebook_blocks, replace_solutions  # noqa: E402
from solutions import save_references  # noqa: E402


ALLOWED_MISSING_SOLUTIONS = {"PlanetsEX.txt"}


def cell_source(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def mask_exercises(source, cell_type):
    """Remove exercise contents while retaining their names and positions."""

    blocks = find_exercise_blocks(source, cell_type)
    masked = source
    for block in sorted(blocks, key=lambda item: item.start, reverse=True):
        token = (
            f"<EXERCISE {block.key.filename} {block.key.block_type} "
            f"{block.key.part or '-'}>"
        )
        masked = masked[: block.start] + token + masked[block.end :]
    return masked


def reference_block(reference_dir, key):
    path = reference_dir / key.filename
    indexed = index_unique_blocks(
        find_exercise_blocks(path.read_text(encoding="utf-8")), str(path)
    )
    return indexed[key]


def assert_only_exercises_changed(before, after):
    before_without_cells = copy.deepcopy(before)
    after_without_cells = copy.deepcopy(after)
    before_without_cells.pop("cells", None)
    after_without_cells.pop("cells", None)
    assert after_without_cells == before_without_cells

    assert len(after["cells"]) == len(before["cells"])
    for original, updated in zip(before["cells"], after["cells"]):
        original_without_source = copy.deepcopy(original)
        updated_without_source = copy.deepcopy(updated)
        original_without_source.pop("source", None)
        updated_without_source.pop("source", None)
        assert updated_without_source == original_without_source

        cell_type = original.get("cell_type")
        if cell_type in {"code", "markdown"}:
            assert mask_exercises(
                cell_source(updated), cell_type
            ) == mask_exercises(cell_source(original), cell_type)
        else:
            assert cell_source(updated) == cell_source(original)


def test_replacement_is_cell_local_and_preserves_notebook_structure(tmp_path):
    marker = (
        "######################\n"
        "# EXERCISE: Demo.txt\n"
        "#---------------------\n"
        "learner_answer = None\n"
        "######################"
    )
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "id": "unrelated",
                "metadata": {"tags": ["keep"]},
                "outputs": [{"name": "stdout", "output_type": "stream", "text": "ok\n"}],
                "source": [
                    "######################\n",
                    "ordinary_code = 'this is not an exercise'\n",
                ],
            },
            {
                "cell_type": "markdown",
                "id": "middle",
                "metadata": {"important": True},
                "source": ["This entire neighboring cell must survive.\n"],
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "id": "exercise",
                "metadata": {"collapsed": False},
                "outputs": [],
                "source": ["prefix = 1\n", f"{marker}\n", "suffix = 2\n"],
            },
        ],
        "metadata": {"kernelspec": {"name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    reference = (
        "```python\n"
        "######################\n"
        "# EXERCISE: Demo.txt\n"
        "#---------------------\n"
        "learner_answer = 42\n"
        "######################\n"
        "```\n"
    )
    source_path = tmp_path / "source.ipynb"
    output_path = tmp_path / "output.ipynb"
    reference_dir = tmp_path / "answers"
    reference_dir.mkdir()
    source_path.write_text(json.dumps(notebook), encoding="utf-8")
    (reference_dir / "Demo.txt").write_text(reference, encoding="utf-8")

    replace_solutions(source_path, output_path, reference_dir)
    updated = json.loads(output_path.read_text(encoding="utf-8"))

    assert_only_exercises_changed(notebook, updated)
    assert "learner_answer = 42" in cell_source(updated["cells"][2])
    assert "prefix = 1" in cell_source(updated["cells"][2])
    assert "suffix = 2" in cell_source(updated["cells"][2])


def test_duplicate_named_blocks_are_rejected(tmp_path):
    marked = (
        "######################\n"
        "# EXERCISE: Duplicate.txt\n"
        "#---------------------\n"
        "pass\n"
        "######################"
    )
    notebook = {
        "cells": [
            {"cell_type": "code", "metadata": {}, "outputs": [], "source": marked},
            {"cell_type": "code", "metadata": {}, "outputs": [], "source": marked},
        ]
    }

    with pytest.raises(ExerciseBlockError, match="Duplicate exercise marker"):
        collect_notebook_blocks(notebook, str(tmp_path / "duplicate.ipynb"))


def test_incomplete_marker_is_rejected_instead_of_silently_ignored():
    incomplete = (
        "######################\n"
        "# EXERCISE: Broken.txt\n"
        "#---------------------\n"
        "answer = None\n"
    )

    with pytest.raises(ExerciseBlockError, match="without one complete"):
        find_exercise_blocks(incomplete, "code")


def test_saving_references_requires_explicit_overwrite(tmp_path):
    marked = (
        "######################\n"
        "# EXERCISE: Saved.txt PART: 1a\n"
        "#---------------------\n"
        "answer = 42\n"
        "######################"
    )
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": marked,
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    notebook_path = tmp_path / "solved.ipynb"
    output_dir = tmp_path / "references"
    output_dir.mkdir()
    notebook_path.write_text(json.dumps(notebook), encoding="utf-8")
    (output_dir / "Saved.txt").write_text("do not overwrite", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        save_references(notebook_path, output_dir)

    written = save_references(notebook_path, output_dir, force=True)
    assert written == [output_dir / "Saved.txt"]
    saved = find_exercise_blocks(
        (output_dir / "Saved.txt").read_text(encoding="utf-8")
    )
    assert len(saved) == 1
    assert saved[0].key.part == "1a"
    assert saved[0].content == "answer = 42"


def test_repository_reset_references_match_canonical_notebooks():
    reset_dir = ROOT / "Notebooks" / "Reset"
    answer_dir = ROOT / "Notebooks" / "Exercises"
    count = 0

    for notebook_path in sorted((ROOT / "Notebooks").glob("*.ipynb")):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for located in collect_notebook_blocks(notebook, str(notebook_path)):
            block = located.block
            count += 1
            assert (reset_dir / block.key.filename).exists()
            assert reference_block(reset_dir, block.key).content == block.content

            answer_path = answer_dir / block.key.filename
            if block.key.filename in ALLOWED_MISSING_SOLUTIONS:
                assert not answer_path.exists()
            else:
                assert answer_path.exists()
                reference_block(answer_dir, block.key)

    assert count > 0


@pytest.mark.parametrize("reference_name", ["Reset", "Exercises"])
def test_real_notebooks_round_trip_without_touching_other_content(
    tmp_path, reference_name
):
    reference_dir = ROOT / "Notebooks" / reference_name
    total = 0

    for notebook_path in sorted((ROOT / "Notebooks").glob("*.ipynb")):
        before = json.loads(notebook_path.read_text(encoding="utf-8"))
        before_blocks = collect_notebook_blocks(before, str(notebook_path))
        if not before_blocks:
            continue

        output_path = tmp_path / reference_name / notebook_path.name
        replace_solutions(
            notebook_path,
            output_path,
            reference_dir,
            allowed_missing=(
                ALLOWED_MISSING_SOLUTIONS if reference_name == "Exercises" else ()
            ),
        )
        after = json.loads(output_path.read_text(encoding="utf-8"))
        assert_only_exercises_changed(before, after)

        after_by_key = {
            item.block.key: item.block
            for item in collect_notebook_blocks(after, str(output_path))
        }
        for located in before_blocks:
            key = located.block.key
            total += 1
            if reference_name == "Exercises" and key.filename in ALLOWED_MISSING_SOLUTIONS:
                assert after_by_key[key].content == located.block.content
            else:
                assert after_by_key[key].content == reference_block(
                    reference_dir, key
                ).content

    assert total > 0
