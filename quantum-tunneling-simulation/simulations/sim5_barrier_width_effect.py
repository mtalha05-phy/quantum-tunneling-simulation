"""
=====================================================================
 sim5_barrier_width_effect.py
 SIMULATION 5: Effect of Barrier Width on Tunneling
=====================================================================

WHAT THIS PRODUCES
-------------------
Two panels in one figure:

  Left panel:  Transmission coefficient T vs barrier width `a`,
               for a FIXED incoming energy E < V0 (genuine tunneling
               regime). Shows the expected exponential-like drop in
               tunneling probability as the barrier gets wider.

  Right panel: The final (post-collision) probability density curves
               for a few representative barrier widths, overlaid, so
               you can visually compare how much probability leaks
               through a thin barrier vs a thick one.

This is a great complementary figure to sim4 (which fixes the barrier
and scans energy) — here we fix the energy and scan the barrier
geometry instead.

HOW TO USE
----------
Just run this script:  python3 sim5_barrier_width_effect.py

Output file: barrier_width_effect.png
=====================================================================
"""

import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ^ lets this script run straight from a clone without `pip install -e .`

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qtunnel.core import SimulationParams, run_simulation, suggested_n_steps


def barrier_width_scan(base_params: SimulationParams, widths,
                        filename="barrier_width_effect.png",
                        widths_to_overlay=None):
    T_sim_list, T_theory_list = [], []
    overlay_results = {}

    if widths_to_overlay is None:
        # By default overlay the thinnest, a middle, and the thickest barrier
        widths_to_overlay = {widths[0], widths[len(widths) // 2], widths[-1]}

    for a in widths:
        p = SimulationParams()
        p.__dict__.update(base_params.__dict__)
        p.barrier_width = a
        p.n_steps = suggested_n_steps(p)
        p.n_frames = 60 if a in widths_to_overlay else 2

        res = run_simulation(p, verbose=False)
        T_sim_list.append(res["T_sim"])
        T_theory_list.append(res["T_theory"])
        print(f"width={a:.2f}  T_sim={res['T_sim']:.4f}  T_theory={res['T_theory']:.4f}")

        if a in widths_to_overlay:
            overlay_results[a] = res

    # --- Figure with two panels ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Panel 1: T vs width
    widths_fine = np.linspace(widths[0], widths[-1], 300)
    from qtunnel.core import analytic_transmission, mean_energy
    E_fixed = mean_energy(base_params)
    T_fine = [analytic_transmission(E_fixed, base_params.V0, a) for a in widths_fine]

    ax1.plot(widths_fine, T_fine, "-", color="black", lw=2, label="Analytic (plane wave)")
    ax1.plot(widths, T_sim_list, "o", color="crimson", ms=6, label="Simulated (wave packet)")
    ax1.set_yscale("log")   # tunneling probability drops roughly exponentially
    ax1.set_xlabel("Barrier width a")
    ax1.set_ylabel("Transmission coefficient T (log scale)")
    ax1.set_title(f"Tunneling Probability vs Barrier Width\n(E = {E_fixed:.2f}, V0 = {base_params.V0:.2f})")
    ax1.legend()
    # NOTE ON ACCURACY: for wide/opaque barriers the true transmission
    # becomes extremely small (see the analytic curve), but the
    # SIMULATED value will floor out around ~1e-3 to 1e-4. This is a
    # genuine numerical limitation of grid-based wave-packet propagation
    # (finite floating-point precision plus the small residual leakage
    # of the absorbing boundary), not new physics -- trust the analytic
    # curve, not the simulated dots, once T drops below roughly 1e-3.

    # Panel 2: overlay of final density profiles for selected widths
    colors = plt.cm.viridis(np.linspace(0, 0.85, len(overlay_results)))
    for color, (a, res) in zip(colors, sorted(overlay_results.items())):
        x = res["x"]
        final_density = res["snapshots"][-1]
        ax2.plot(x, final_density, color=color, lw=1.8, label=f"a = {a:.1f}")

    p_ref = base_params
    ax2.axvspan(p_ref.barrier_center - max(overlay_results) / 2,
                p_ref.barrier_center + max(overlay_results) / 2,
                color="grey", alpha=0.15, label="Widest barrier region")
    ax2.set_xlabel("Position x")
    ax2.set_ylabel(r"Final $|\Psi(x)|^2$")
    ax2.set_title("Final Wave Packet for Different Barrier Widths")
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved -> {filename}")
    return filename


if __name__ == "__main__":
    base_params = SimulationParams()
    base_params.V0 = 1.5
    base_params.k0 = 1.0   # chosen so E < V0 -> genuine tunneling regime

    widths = np.linspace(1.0, 6.0, 10)
    barrier_width_scan(base_params, widths, "barrier_width_effect.png")
