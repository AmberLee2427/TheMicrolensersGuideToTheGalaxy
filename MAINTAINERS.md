# Maintainer guide

This document describes how exercise answers are saved, inserted, reset, and
published. The short version is that **marker names are identities; cell
numbers are not**. Cells can be inserted, deleted, split, merged, or reordered.
The scripts inspect every code and Markdown cell independently and replace only
complete marked blocks inside that cell.

## Where each version lives

- `Notebooks/*.ipynb` contains the canonical learner-facing notebooks. Commit
  these with blank or learner-form exercise contents.
- `Notebooks/Exercises/*.txt` contains the solved blocks used to generate
  complete notebooks and the solved documentation pages.
- `Notebooks/Reset/*.txt` contains the learner-form blocks. These should match
  the corresponding blocks in the canonical notebooks.
- `replacement.py` inserts either set of references into a notebook.
- `solutions.py` saves marked blocks from a notebook into reference files.
- `build.py` creates both documentation trees and then runs Sphinx.

Reference `.txt` files are fenced for readability, but the fences are not part
of the notebook content. A reference file may hold several `PART` blocks that
share one filename.

## Marker format

A code exercise uses exactly this shape (including 22 `#` characters on the
opening and closing lines):

````text
```python
######################
# EXERCISE: SingleLensE5.txt PART: 1
#---------------------
# learner prompt or solved code
######################
```
````

A Markdown exercise uses:

````text
```markdown
<!-- EXERCISE: SingleLensE7.txt PART: 1b -->
Learner prompt or solved prose.
<!-- ~~~~~~~~~~~~~~~~~~~~~~~ -->
```
````

The opening marker, separator, contents, and closing marker of a code block
must use the same indentation. Within one notebook, the combination of
filename, block type, and optional `PART` label must be unique. Part labels may
be numbers or text such as `1a`.

Do not reuse a reference filename for unrelated exercises. Do not put markers
across two cells. The parser rejects duplicate identities and indentation
mismatches rather than guessing.

## Edit an existing solved answer

Generate a disposable solved copy from the canonical learner notebook:

```bash
python replacement.py \
  Notebooks/SingleLens.ipynb \
  build/SingleLens_solved.ipynb
```

Open `build/SingleLens_solved.ipynb`, edit the answer *inside its markers*, and
save the notebook. Then save all marked blocks from that solved copy:

```bash
python solutions.py \
  build/SingleLens_solved.ipynb \
  Notebooks/Exercises \
  --force
git diff -- Notebooks/Exercises
```

`solutions.py` validates every marker before writing anything. It refuses to
overwrite existing files unless `--force` is given. Here, overwriting is the
intended operation—but always inspect the diff immediately. Some older
references contain surrounding whole-cell code; the first refresh may compact
those files to the marked blocks only. That is expected.

Do not edit the canonical notebook into a solved version. Keeping the solved
work in `build/` makes it much harder to publish spoilers accidentally.

## Edit a learner prompt or blank

Edit the marked learner content directly in the canonical notebook, then
refresh its reset references:

```bash
python solutions.py \
  Notebooks/SingleLens.ipynb \
  Notebooks/Reset \
  --force
git diff -- Notebooks/SingleLens.ipynb Notebooks/Reset
```

This saves every marked block in that notebook, not only the block you edited.
The resulting diff should contain the intended prompt change plus, possibly,
the expected removal of legacy surrounding cell content.

To reset any working notebook explicitly:

```bash
python replacement.py \
  build/SingleLens_solved.ipynb \
  build/SingleLens_reset.ipynb \
  Notebooks/Reset
```

## Add a new exercise

1. Add a uniquely named marker block containing the learner form to the
   canonical notebook.
2. Save the learner references with `solutions.py ... Notebooks/Reset --force`
   and inspect the diff.
3. Generate a solved working copy. Because its answer does not exist yet,
   permit only that exact missing filename:

   ```bash
   python replacement.py \
     Notebooks/SingleLens.ipynb \
     build/SingleLens_solved.ipynb \
     Notebooks/Exercises \
     --allow-missing SingleLensE8.txt
   ```

4. Fill the new answer inside its marker in the solved working copy.
5. Save solved references with `solutions.py ... Notebooks/Exercises --force`
   and inspect the diff. Existing exercises in that copy have already been
   filled, so their saved references remain solved.
6. Run the checks below.

Use the same filename plus distinct `PART` labels for a multipart exercise.
The explicit `--allow-missing` option is intentionally narrow; a typo or a
second missing answer will still stop the operation.

## Known exception

`PlanetsEX.txt` is present in the learner/reset material but has no solved
reference. Its notebook comment identifies it as a developer-only exercise.
`build.py` allows exactly this missing filename and leaves that one block in
learner form. Any other missing answer is an error. Either supply its solved
reference when the exercise becomes public or remove the marker and its reset
file if it is retired.

## Validate before committing

Run:

```bash
pytest
python build.py
git diff --check
git status --short
```

The exercise workflow tests verify all current markers and references, generate
both reset and solved forms, and assert that cell count, cell order, metadata,
outputs, and all non-exercise text remain unchanged. `build.py` also executes
the documentation build, so review its warnings and open the affected pages if
the exercise contains rendered mathematics, plots, or interactive output.

Generated solved notebooks belong under `build/` or `docs/Solved/`; do not use
them as canonical source files. Commit the canonical learner notebook (if it
changed), the appropriate reference files, the tests or documentation needed
for the change, and nothing generated by the build.
