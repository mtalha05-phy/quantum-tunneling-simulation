import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ^ lets this script run straight from a clone without `pip install -e .`

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qtunnel.core import SimulationParams, run_simulation, suggested_n_steps


def transmission_vs_energy_scan(base_params: SimulationParams, k_values,
                                 filename="transmission_vs_energy.png"):
    E_list, T_sim_list, T_theory_list = [], [], []

    for k0 in k_values:
        p = SimulationParams()
        p.__dict__.update(base_params.__dict__)  # copy all base settings
        p.k0 = k0
        p.n_steps = suggested_n_steps(p)          # re-time for this speed
        p.n_frames = 2                            # don't need many snapshots here

        res = run_simulation(p, verbose=False)
        E_list.append(res["E_mean"])
        T_sim_list.append(res["T_sim"])
        T_theory_list.append(res["T_theory"])
        print(f"k0={k0:.2f}  E={res['E_mean']:.3f}  "
              f"T_sim={res['T_sim']:.3f}  T_theory={res['T_theory']:.3f}")

    # Smooth analytic curve over a finer energy grid, for a clean line.
    E_fine = np.linspace(min(E_list) * 0.9, max(E_list) * 1.05, 400)
    from qtunnel.core import analytic_transmission
    T_fine = [analytic_transmission(E, base_params.V0, base_params.barrier_width)
              for E in E_fine]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(E_fine, T_fine, "-", color="black", lw=2, label="Analytic (plane wave)")
    ax.plot(E_list, T_sim_list, "o", color="crimson", ms=6, label="Simulated (wave packet)")
    ax.axvline(base_params.V0, color="grey", ls="--", label="Barrier height V0")
    ax.set_xlabel("Mean energy E")
    ax.set_ylabel("Transmission coefficient T")
    ax.set_title("Transmission Coefficient vs Energy")
    ax.set_ylim(-0.02, 1.05)
    ax.legend()
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved -> {filename}")
    return filename


if __name__ == "__main__":
    base_params = SimulationParams()
    base_params.V0 = 1.5
    base_params.barrier_width = 3.0

    n_energy_points = 14
    k_scan = np.linspace(1.0, 3.2, n_energy_points)  # spans below & above V0

    transmission_vs_energy_scan(base_params, k_scan, "transmission_vs_energy.png")
