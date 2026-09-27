"""
=====================================================================
 sim2_animation.py
 SIMULATION 2: Animated GIF of the Wave Packet Crossing the Barrier
=====================================================================

WHAT THIS PRODUCES
-------------------
An animated GIF showing |Psi(x,t)|^2 evolving in real time as the wave
packet approaches, partially reflects off, and partially tunnels
through the potential barrier. Great for a presentation slide or a
project demo (as opposed to a single static figure).

HOW TO USE
----------
Just run this script:  python3 sim2_animation.py

Tune `n_frames` for a smoother (more frames, bigger file) or lighter
(fewer frames, smaller file) GIF. `fps` controls playback speed.

Output file: tunneling_animation.gif
=====================================================================
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ^ lets this script run straight from a clone without `pip install -e .`

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from qtunnel.core import SimulationParams, run_simulation, suggested_n_steps


def make_animation(results, filename="tunneling_animation.gif", fps=20):
    x = results["x"]
    snaps = results["snapshots"]
    times = results["times"]
    V = results["V_barrier"]
    p = results["params"]

    fig, ax = plt.subplots(figsize=(9, 5))
    y_max = max(s.max() for s in snaps) * 1.15
    V_scaled = V / (V.max() if V.max() > 0 else 1) * y_max * 0.9

    ax.fill_between(x, V_scaled, color="grey", alpha=0.3, label="Potential barrier")
    line, = ax.plot([], [], color="crimson", lw=2, label=r"$|\Psi(x,t)|^2$")
    time_text = ax.text(0.02, 0.92, "", transform=ax.transAxes)

    ax.set_xlim(p.x_min, p.x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("Position x")
    ax.set_ylabel("Probability density")
    ax.set_title("Quantum Tunneling Through a Potential Barrier")
    ax.legend(loc="upper right")

    def init():
        line.set_data([], [])
        time_text.set_text("")
        return line, time_text

    def update(frame):
        line.set_data(x, snaps[frame])
        time_text.set_text(f"t = {times[frame]:.2f}")
        return line, time_text

    anim = animation.FuncAnimation(
        fig, update, frames=len(snaps), init_func=init, blit=True, interval=1000 / fps
    )
    anim.save(filename, writer=animation.PillowWriter(fps=fps))
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
    p.n_frames = 150   # more frames = smoother animation, larger file

    results = run_simulation(p, verbose=True)
    make_animation(results, "tunneling_animation.gif", fps=20)
