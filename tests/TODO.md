# Notebook Build TODO

[ ] BinarySource (unsolved & solved) – execution errors and timeouts; depends on MulensModel datasets and long MCMC sampling. Review the err log (docs/_build/html/reports/Notebooks/BinarySource.err.log) and confirm data paths / install steps, or mark heavy cells to skip.
[ ] Eras (unsolved & solved) – cells fail while referencing other notebooks and shared assets; check that referenced files are copied into docs/ and adjust cross-link anchors (what-is-microlensing, Planets..., etc.).
[ ] MulensModelFSPLError (unsolved & solved) – header-level warnings fixed, but execution still trips if MulensModel is missing; verify import succeeds in CI.
[ ] PlanetsAndBrownDwarfs (unsolved & solved) – execution errors due to data paths (Data/Events/BD/*.csv) and expensive runs; ensure CSVs exist in the copied tree and consider skipping long cells.
[ ] RemnantsAndDarkMatter / SingleLens / ProgressChecklist (unsolved & solved) – similar dataset or dependency issues; inspect respective .err.log files for missing assets or library imports.
[ ] Solved notebooks overall – watch for image warnings (Assets/... not readable). Confirm build.py copies Assets/ into both docs/Notebooks/ and docs/Solved/.
[ ] General cross-reference warnings – many :doc: links point to notebooks that don’t exist yet (e.g., BinaryLens.ipynb); either add stubs or ignore until content arrives.

Use the specific logs in docs/_build/html/reports/ to prioritize fixes; once the missing assets and imports are handled, rerun python build.py or trigger the CI workflow to verify the warnings clear.