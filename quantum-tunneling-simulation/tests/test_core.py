"""
tests/test_core.py

Basic sanity/regression tests for qtunnel.core. Run with:

    pytest

These are NOT a substitute for careful physical validation (see
docs/theory.md and the discussion in the project README), but they
catch obvious regressions: broken normalization, broken grid shapes,
and wrong analytic-formula edge cases.
"""

import numpy as np
import pytest

from qtunnel.core import (
    SimulationParams,
    build_grid,
    gaussian_wave_packet,
    rectangular_barrier,
    absorbing_boundary,
    total_norm,
    analytic_transmission,
    run_simulation,
    suggested_n_steps,
)


def test_grid_shapes():
    p = SimulationParams()
    x, dx, k = build_grid(p)
    assert x.shape == (p.N,)
    assert k.shape == (p.N,)
    assert dx > 0


def test_initial_wave_packet_is_normalizable():
    p = SimulationParams()
    x, dx, k = build_grid(p)
    psi = gaussian_wave_packet(x, p.x0, p.k0, p.sigma)
    norm = total_norm(psi, dx)
    # Should be close to 1 already (small deviation from finite domain
    # truncation of the Gaussian tails), and exactly correctable by
    # dividing by sqrt(norm) as run_simulation() does internally.
    assert 0.95 < norm < 1.05


def test_rectangular_barrier_shape():
    x = np.linspace(-10, 10, 2001)
    V = rectangular_barrier(x, V0=2.0, width=4.0, center=0.0)
    assert V.max() == pytest.approx(2.0)
    assert V.min() == 0.0
    # Barrier should be "on" only within +/- width/2 of the center
    inside = np.abs(x) <= 2.0
    assert np.all(V[inside] == 2.0)
    assert np.all(V[~inside] == 0.0)


def test_absorbing_boundary_is_zero_in_the_middle():
    p = SimulationParams()
    x, dx, k = build_grid(p)
    eta = absorbing_boundary(x, p)
    middle = np.abs(x) < (p.x_max - p.absorb_width) / 2
    assert np.allclose(eta[middle], 0.0)
    # It should be nonzero near the edges
    assert eta[0] > 0
    assert eta[-1] > 0


def test_analytic_transmission_zero_barrier_is_unity():
    # With no barrier at all (V0=0), transmission must be 1 for any E>0.
    T = analytic_transmission(E=1.0, V0=0.0, a=3.0)
    assert T == pytest.approx(1.0, abs=1e-9)


def test_analytic_transmission_is_bounded():
    for E in [0.1, 0.5, 1.0, 2.0, 5.0]:
        T = analytic_transmission(E=E, V0=1.5, a=3.0)
        assert 0.0 <= T <= 1.0 + 1e-9


def test_analytic_transmission_increases_with_energy_below_barrier():
    # In the deep-tunneling regime, higher energy should mean higher T.
    V0, a = 1.5, 3.0
    T_low = analytic_transmission(E=0.2, V0=V0, a=a)
    T_high = analytic_transmission(E=0.8, V0=V0, a=a)
    assert T_high > T_low


def test_full_simulation_conserves_probability_reasonably():
    """
    Runs a short simulation and checks that T_sim + R_sim + under_barrier
    is close to 1 (probability is conserved up to small numerical error
    from the absorbing-boundary bookkeeping).
    """
    p = SimulationParams()
    p.N = 512          # smaller grid for a fast test
    p.n_steps = suggested_n_steps(p)
    p.n_frames = 2
    results = run_simulation(p, verbose=False)

    total = results["T_sim"] + results["R_sim"] + results["under_sim"]
    assert total == pytest.approx(1.0, abs=1e-2)


def test_full_simulation_below_barrier_gives_small_transmission():
    """Sanity check: deep sub-barrier energy should give small T_sim."""
    p = SimulationParams()
    p.N = 512
    p.k0 = 0.7   # E well below V0 = 1.5
    p.n_steps = suggested_n_steps(p)
    p.n_frames = 2
    results = run_simulation(p, verbose=False)
    assert results["T_sim"] < 0.1
