# Contributing

Contributions are welcome — bug fixes, new visualizations, alternative
numerical methods (e.g. Crank-Nicolson), or extensions like 2D
tunneling or double-barrier resonance.

## Development setup

```bash
git clone https://github.com/YOUR-USERNAME/quantum-tunneling-simulation.git
cd quantum-tunneling-simulation
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running the tests

```bash
pytest -v
```

Please add or update a test in `tests/test_core.py` for any change to
`qtunnel/core.py`.

## Adding a new simulation script

1. Add `simulations/simN_your_name.py`.
2. Import shared physics from the package: `from qtunnel.core import ...`.
3. Follow the existing pattern: a module docstring explaining what the
   script produces and how to use it, a plotting function, and an
   `if __name__ == "__main__":` block with an editable parameter
   section at the bottom.
4. Regenerate the corresponding image and, if it's a good example,
   add it to `assets/` and reference it in the README.

## Code style

- Keep `qtunnel/core.py` free of any plotting code — it should stay a
  pure physics/numerics module usable from any script.
- Prefer clear, heavily-commented code over cleverness; this is meant
  to be readable by someone learning the physics, not just by
  experienced numerical programmers.
- Run `pytest` before opening a pull request.

## Reporting issues

Please open a GitHub issue with:
- what you ran (which script, which parameters),
- what you expected,
- what actually happened (include the console output/error, and the
  image if relevant).
