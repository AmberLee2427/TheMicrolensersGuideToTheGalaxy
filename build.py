import json
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

import replacement


NOTEBOOK_ORDER: list[str] = [
    "Introduction.ipynb",
    "SingleLens.ipynb",
    "BinarySource.ipynb",
    "PlanetsAndBrownDwarfs.ipynb",
    "RemnantsAndDarkMatter.ipynb",
    "Eras.ipynb",
    "Modelling.ipynb",
    "MulensModelFSPLError.ipynb",
]

NOTEBOOK_ROOT = Path("Notebooks")
REFERENCE_DIR = NOTEBOOK_ROOT / "Exercises"
BUILD_ROOT = Path("build")
SOLVED_BUILD_DIR = BUILD_ROOT / "Complete"
DOCS_ROOT = Path("docs")
DOCS_UNSOLVED_DIR = DOCS_ROOT / "Notebooks"
DOCS_SOLVED_DIR = DOCS_ROOT / "Solved"

# PlanetsEX is a deliberately unfinished, developer-only placeholder in the
# source notebook.  Keep this exception narrow and visible; any other missing
# answer reference should fail solved-notebook generation loudly.
ALLOWED_MISSING_SOLUTIONS = {"PlanetsEX.txt"}


def clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_notebook_tree(target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(NOTEBOOK_ROOT, target)


def iter_course_notebooks() -> Iterable[Path]:
    for name in NOTEBOOK_ORDER:
        notebook_path = NOTEBOOK_ROOT / name
        if notebook_path.exists():
            yield notebook_path
        else:
            print(f"Warning: expected notebook {notebook_path} not found; skipping.")


def generate_solved_notebooks() -> None:
    clean_directory(SOLVED_BUILD_DIR)

    # Ensure docs/Solved mirrors the notebook tree (assets, data, etc.)
    copy_notebook_tree(DOCS_SOLVED_DIR)

    for src in iter_course_notebooks():
        dest = SOLVED_BUILD_DIR / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)

        notebook = json.loads(src.read_text(encoding="utf-8"))
        if replacement.collect_notebook_blocks(notebook, str(src)):
            replacement.replace_solutions(
                str(src),
                str(dest),
                str(REFERENCE_DIR),
                allowed_missing=ALLOWED_MISSING_SOLUTIONS,
            )
            print(f"Solved notebook created for {src.name}.")
        else:
            print(f"No marked exercises in {src.name}; copying it unchanged.")
            shutil.copy2(src, dest)

        shutil.copy2(dest, DOCS_SOLVED_DIR / src.name)


def build_sphinx_docs() -> None:
    html_dir = DOCS_ROOT / "_build" / "html"
    if html_dir.exists():
        shutil.rmtree(html_dir)

    subprocess.run(
        ["sphinx-build", "-b", "html", str(DOCS_ROOT), str(html_dir)],
        check=True,
    )


def main() -> None:
    clean_directory(BUILD_ROOT)
    copy_notebook_tree(DOCS_UNSOLVED_DIR)
    generate_solved_notebooks()
    build_sphinx_docs()


if __name__ == "__main__":
    main()
