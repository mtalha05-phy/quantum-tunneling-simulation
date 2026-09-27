"""
qtunnel
=======

A small, dependency-light package implementing a split-step Fourier
solver for the 1D time-dependent Schrodinger equation, used to study
quantum tunneling of a Gaussian wave packet through a rectangular
potential barrier.

Public API re-exported here for convenience:

    from qtunnel import SimulationParams, run_simulation, analytic_transmission

See qtunnel/core.py for full documentation of every function.
"""

from .core import (
    HBAR,
    MASS,
    SimulationParams,
    suggested_n_steps,
    build_grid,
    gaussian_wave_packet,
    rectangular_barrier,
    absorbing_boundary,
    SplitStepPropagator,
    probability_density,
    total_norm,
    transmission_reflection,
    probability_current,
    mean_energy,
    analytic_transmission,
    run_simulation,
)

__all__ = [
    "HBAR",
    "MASS",
    "SimulationParams",
    "suggested_n_steps",
    "build_grid",
    "gaussian_wave_packet",
    "rectangular_barrier",
    "absorbing_boundary",
    "SplitStepPropagator",
    "probability_density",
    "total_norm",
    "transmission_reflection",
    "probability_current",
    "mean_energy",
    "analytic_transmission",
    "run_simulation",
]

__version__ = "0.1.0"
