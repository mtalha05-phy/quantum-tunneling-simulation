# ⚛️ Quantum Tunneling Simulation

**Numerical solution of the 1D time-dependent Schrödinger equation**,
simulating a Gaussian wave packet tunneling through a rectangular
potential barrier via the split-step Fourier (split-operator) method.

[![CI](https://github.com/YOUR-USERNAME/quantum-tunneling-simulation/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-USERNAME/quantum-tunneling-simulation/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

<p align="center">
  <img src="assets/tunneling_animation.gif" width="600" alt="Wave packet tunneling through a potential barrier">
</p>

## 🔭 Overview

A particle's wave function hitting an energy barrier it classically
shouldn't be able to cross — and quantum mechanics saying part of it
gets through anyway. This project solves the Schrödinger equation
numerically (no approximations beyond standard discretization) to show
exactly how much of the wave packet tunnels through, reflects back,
and how that compares to the textbook analytic formula.

## ✨ Features

- **⚡	Split-step Fourier solver** — `O(N log N)` per time step,
  unconditionally stable, exactly unitary for a real potential
- **🧱 Absorbing boundaries** (complex absorbing potential) so wave
  packets don't unphysically wrap around the periodic FFT grid
- **📐 Exact analytic benchmark** — every simulated result is checked
  against the closed-form stationary-state transmission coefficient
- **🎨 Five ready-to-run scripts**, each producing one publication-quality
  figure or animation

## 🚀 Installation

```bash
git clone https://github.com/YOUR-USERNAME/quantum-tunneling-simulation.git
cd quantum-tunneling-simulation
pip install -e .
```

This installs the `qtunnel` package (numpy, scipy, and matplotlib are
pulled in automatically). Python 3.9+ required.

## ⚡ Quickstart

```bash
cd simulations
python sim1_snapshots.py
```

Every script in `simulations/` also runs directly from a fresh clone
without the `pip install` step (each has a small `sys.path` bootstrap),
so `python simulations/sim1_snapshots.py` works too.

## 🎬 The five simulations

| Script | Output | Shows |
|---|---|---|
| `sim1_snapshots.py` | `tunneling_snapshots.png` | Before / during / after panels of the collision |
| `sim2_animation.py` | `tunneling_animation.gif` | Live animation of the wave packet crossing the barrier |
| `sim3_spacetime_map.py` | `tunneling_spacetime_map.png` | Position-vs-time heatmap of the entire collision |
| `sim4_transmission_vs_energy.py` | `transmission_vs_energy.png` | Transmission coefficient vs energy, sim vs exact formula |
| `sim5_barrier_width_effect.py` | `barrier_width_effect.png` | Transmission vs barrier width (log scale) |

### 1. Snapshots

<p align="center"><img src="assets/tunneling_snapshots.png" width="800"></p>

### 2. Space-time map

<p align="center"><img src="assets/tunneling_spacetime_map.png" width="500"></p>

### 3. Transmission vs energy

<p align="center"><img src="assets/transmission_vs_energy.png" width="500"></p>

### 4. Transmission vs barrier width

<p align="center"><img src="assets/barrier_width_effect.png" width="700"></p>

Each script has an editable parameter block at the bottom (barrier
height/width, incoming momentum, grid resolution, etc.) — see the
docstring at the top of each file for details.

## Project structure

```
quantum-tunneling-simulation/
├── qtunnel/                    # Installable package: the physics engine
│   ├── __init__.py
│   └── core.py                 # Grid, wave packet, barrier, propagator, diagnostics
├── simulations/                # Standalone scripts, one per figure/animation
│   ├── sim1_snapshots.py
│   ├── sim2_animation.py
│   ├── sim3_spacetime_map.py
│   ├── sim4_transmission_vs_energy.py
│   └── sim5_barrier_width_effect.py
├── tests/
│   └── test_core.py            # pytest suite for qtunnel/core.py
├── docs/
│   └── theory.md                # Full physics derivation and method write-up
├── assets/                      # Sample output images used in this README
├── .github/workflows/ci.yml    # Runs the test suite + a smoke test on push
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── CONTRIBUTING.md
```

## The physics, briefly

The time-dependent Schrödinger equation

```
i·ħ ∂Ψ/∂t = -(ħ²/2m) ∂²Ψ/∂x² + V(x)Ψ
```

is solved with the **split-step Fourier method**: the time-evolution
operator is split into a potential half-step (applied in position
space) and a kinetic full-step (applied in momentum space via FFT),
which is accurate, fast, and unconditionally stable. Full derivation,
the exact analytic transmission formula used for validation, and a
documented numerical limitation are in **[docs/theory.md](docs/theory.md)**.

## Validation

Every result here is checked, not assumed:

- Below-barrier (E/V₀ ≈ 0.34): simulated T ≈ 0.002 vs analytic T ≈ 0.0008 — correctly tiny.
- Above-barrier (E/V₀ ≈ 1.34): simulated T ≈ 0.75 vs analytic T ≈ 0.99 — high transmission, gap explained by the wave packet's energy spread.
- The transmission-vs-energy scan (`sim4`) tracks the analytic curve closely, including resonance oscillations above V₀.
- A known limitation — the simulated transmission floors out around 10⁻³ for very opaque barriers due to floating-point precision, not physics — is documented in `docs/theory.md` and in `sim5`'s output.

## Running the tests

```bash
pip install -e ".[dev]"
pytest -v
```

## Roadmap / possible extensions

- [ ] 2D or 3D tunneling
- [ ] Time-dependent or oscillating barriers
- [ ] Double-barrier resonant tunneling (quantum well)
- [ ] WKB approximation comparison for smooth (non-rectangular) potentials
- [ ] Crank-Nicolson solver as an alternative for non-periodic boundaries

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) — free to use, modify, and share.
