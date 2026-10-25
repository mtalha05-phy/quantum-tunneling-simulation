import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ^ lets this script run straight from a clone without `pip install -e .`

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qtunnel.core import SimulationParams, run_simulation, suggested_n_steps


def plot_snapshots(results, filename="tunneling_snapshots.png"):
    x = results["x"]
    snaps = results["snapshots"]
    V = results["V_barrier"]
    p = results["params"]

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    stage_indices = [0, len(snaps) // 2, -1]
    stage_titles = ["Initial (t = 0)", "Mid-collision", "Final (transmitted + reflected)"]

    # Scale the barrier outline so it's visible next to the probability
    # density curves, regardless of their absolute height.
    peak_density = max(snaps[0].max(), snaps[-1].max())
    V_scaled = V / (V.max() if V.max() > 0 else 1) * peak_density

    for ax, idx, title in zip(axes, stage_indices, stage_titles):
        ax.plot(x, snaps[idx], color="steelblue", lw=1.6, label=r"$|\Psi(x)|^2$")
        ax.fill_between(x, V_scaled, color="grey", alpha=0.3, label="Barrier (scaled)")
        ax.set_title(title)
        ax.set_xlabel("Position x")
        ax.set_ylabel(r"$|\Psi(x)|^2$")
        ax.set_xlim(p.x_min, p.x_max)
        ax.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        f"Quantum Tunneling — E/V0 = {results['E_mean']/p.V0:.2f}   "
        f"T_sim = {results['T_sim']:.3f}   T_theory = {results['T_theory']:.3f}"
    )
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved -> {filename}")
    return filename


if __name__ == "__main__":
    p = SimulationParams()

    # ---- Feel free to edit these for your own report ----
    p.V0 = 1.5
    p.barrier_width = 3.0
    p.k0 = 2.0                       # try 1.0 for E < V0 (deep tunneling)
    p.n_steps = suggested_n_steps(p)  # auto-picks a safe run length

    results = run_simulation(p, verbose=True)
    plot_snapshots(results, "tunneling_snapshots.png")
