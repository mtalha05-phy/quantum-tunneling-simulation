import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ^ lets this script run straight from a clone without `pip install -e .`

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qtunnel.core import SimulationParams, run_simulation, suggested_n_steps


def plot_spacetime_map(results, filename="tunneling_spacetime_map.png"):
    x = results["x"]
    snaps = results["snapshots"]      # list of |psi|^2 arrays, one per recorded time
    times = results["times"]
    p = results["params"]

    # Stack all the recorded density snapshots into a 2D array:
    # rows = time, columns = position.
    density_grid = np.array(snaps)  # shape: (n_times, n_x)

    fig, ax = plt.subplots(figsize=(9, 6))

    # pcolormesh needs the x/time EDGES (or centers with shading="auto");
    # we just use the centers here with shading="auto" for simplicity.
    mesh = ax.pcolormesh(
        x, times, density_grid,
        shading="auto", cmap="inferno"
    )
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label(r"$|\Psi(x,t)|^2$")

    # Mark the barrier location with two vertical dashed lines.
    barrier_left = p.barrier_center - p.barrier_width / 2
    barrier_right = p.barrier_center + p.barrier_width / 2
    ax.axvline(barrier_left, color="cyan", ls="--", lw=1, alpha=0.8)
    ax.axvline(barrier_right, color="cyan", ls="--", lw=1, alpha=0.8,
               label="Barrier edges")

    ax.set_xlabel("Position x")
    ax.set_ylabel("Time t")
    ax.set_title(
        f"Space-Time Evolution of the Wave Packet   "
        f"(E/V0 = {results['E_mean']/p.V0:.2f})"
    )
    ax.legend(loc="upper right", fontsize=8)

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
    p.k0 = 2.0
    p.n_steps = suggested_n_steps(p)
    p.n_frames = 300   # more time-rows -> smoother-looking heatmap

    results = run_simulation(p, verbose=True)
    plot_spacetime_map(results, "tunneling_spacetime_map.png")
