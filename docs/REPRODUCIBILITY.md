# Reproducibility

Conflux targets Python 3.12 or newer. Create an isolated environment, install
the package with development dependencies, and run tests before experiments:

```text
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
```

Experiments should record the scenario, attack, defence, model configuration,
provider configuration, random seed, and produced trace/metrics. Generated
experiment data belongs outside version control unless it is an intentional
paper artefact.

The paper source is in `paper/`. Build it with the repository's LaTeX source
and required `.sty`/`.bst` files. Commit the source, diagrams, bibliography,
and final PDF; LaTeX intermediates are ignored by `.gitignore`.
