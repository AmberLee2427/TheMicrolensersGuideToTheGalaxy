import os
import shutil
import subprocess
from contextlib import redirect_stdout
from io import StringIO
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


def clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_unsolved_notebooks() -> None:
    if DOCS_UNSOLVED_DIR.exists():
        shutil.rmtree(DOCS_UNSOLVED_DIR)
    shutil.copytree(NOTEBOOK_ROOT, DOCS_UNSOLVED_DIR)


def iter_course_notebooks() -> Iterable[Path]:
    for name in NOTEBOOK_ORDER:
        notebook_path = NOTEBOOK_ROOT / name
        if notebook_path.exists():
            yield notebook_path
        else:
            print(f"Warning: expected notebook {notebook_path} not found; skipping.")


def generate_solved_notebooks() -> None:
    clean_directory(SOLVED_BUILD_DIR)
    clean_directory(DOCS_SOLVED_DIR)

    for src in iter_course_notebooks():
        dest = SOLVED_BUILD_DIR / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            buffer = StringIO()
            with redirect_stdout(buffer):
                replacement.replace_solutions(
                    str(src),
                    str(dest),
                    str(REFERENCE_DIR),
                    destructive=True,
                )
            print(f"Solved notebook created for {src.name}.")
        except Exception as exc:
            print(
                f"Warning: could not generate solved notebook for {src.name}: {exc}"
            )
            print("Copying the unsolved version instead.")
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
    copy_unsolved_notebooks()
    generate_solved_notebooks()
    build_sphinx_docs()


if __name__ == "__main__":
    main()
