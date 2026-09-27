"""
=====================================================================
 qtunnel_core.py
 SHARED PHYSICS ENGINE for the Quantum Tunneling simulation series
=====================================================================

This module contains ONLY the reusable physics/numerics: grid setup,
the initial wave packet, the potential barrier, the absorbing boundary,
the split-step Fourier propagator, and the diagnostic/analytic
formulas. It does NOT run a simulation or make plots by itself.

Each "simN_....py" script in this project IMPORTS this module and
uses it to build one specific figure or animation. This way:
  - the physics is written and tested in exactly one place,
  - every simulation script stays short and focused on ONE picture,
  - you can safely tweak parameters in one sim script without
    breaking the others.

Keep this file in the same folder as the simN_*.py scripts.

Units convention: hbar = 1, m = 1 (natural units).
=====================================================================
"""

import numpy as np
from scipy.fft import fft, ifft, fftfreq

HBAR = 1.0
MASS = 1.0


# =====================================================================
# SIMULATION PARAMETERS CONTAINER
# =====================================================================
class SimulationParams:
    """
    All tunable knobs for a single tunneling run. Each sim script
    creates one of these, tweaks whatever it needs, and passes it to
    run_simulation().
    """

    def __init__(self):
        # --- Spatial grid ---
        self.x_min = -60.0
        self.x_max = 60.0
        self.N = 2048              # grid points (power of 2 -> fast FFT)

        # --- Time grid ---
        # Chosen so the packet fully separates from the barrier before
        # reaching the absorbing layers near the domain edges. If you
        # change k0, m, or the domain size, re-check this (see the
        # `suggested_n_steps()` helper below).
        self.dt = 0.05
        self.n_steps = 500

        # --- Initial Gaussian wave packet ---
        self.x0 = -20.0            # starting position (left of barrier)
        self.k0 = 2.0              # mean momentum (positive => moves right)
        self.sigma = 3.0           # initial spatial spread (width)

        # --- Rectangular potential barrier ---
        self.V0 = 1.5              # barrier height
        self.barrier_width = 3.0
        self.barrier_center = 0.0

        # --- Complex Absorbing Potential (CAP) at domain edges ---
        # Prevents spurious wraparound on the periodic FFT grid.
        self.absorb_width = 15.0
        self.absorb_strength = 0.2

        # --- Output control ---
        self.n_frames = 150        # snapshots to keep (for animations/heatmaps)


def suggested_n_steps(p: SimulationParams, safety=0.75):
    """
    Rough estimate of how many time steps let the packet travel from
    x0 to just inside the absorbing layer, so you don't cut the
    simulation short OR run it so long that probability is lost before
    you can measure it. `safety` < 1 stops a bit earlier to be safe.
    """
    v_group = HBAR * p.k0 / MASS
    if v_group <= 0:
        return p.n_steps
    travel_distance = (p.x_max - p.absorb_width) - p.x0
    t_needed = safety * travel_distance / v_group
    return max(50, int(t_needed / p.dt))


# =====================================================================
# GRID CONSTRUCTION
# =====================================================================
def build_grid(p: SimulationParams):
    """Position grid x, spacing dx, and conjugate momentum grid k."""
    x = np.linspace(p.x_min, p.x_max, p.N, endpoint=False)
    dx = x[1] - x[0]
    k = 2 * np.pi * fftfreq(p.N, d=dx)
    return x, dx, k


# =====================================================================
# INITIAL WAVE PACKET
# =====================================================================
def gaussian_wave_packet(x, x0, k0, sigma):
    """
    Normalized initial Gaussian wave packet (minimum uncertainty state):

        Psi(x,0) = (2*pi*sigma^2)^(-1/4) * exp(-(x-x0)^2/(4 sigma^2)) * exp(i k0 x)
    """
    norm = (2 * np.pi * sigma ** 2) ** (-0.25)
    envelope = np.exp(-(x - x0) ** 2 / (4 * sigma ** 2))
    plane_wave = np.exp(1j * k0 * x)
    return norm * envelope * plane_wave


# =====================================================================
# POTENTIAL: BARRIER + ABSORBING BOUNDARY
# =====================================================================
def rectangular_barrier(x, V0, width, center):
    """A simple rectangular (square) potential barrier."""
    V = np.zeros_like(x)
    half = width / 2.0
    V[np.abs(x - center) <= half] = V0
    return V


def absorbing_boundary(x, p: SimulationParams):
    """
    Smooth complex absorbing potential (CAP), nonzero only within
    `absorb_width` of each domain edge, ramping smoothly to zero so it
    does not itself scatter the wave.
    """
    eta = np.zeros_like(x)

    left_edge = x - p.x_min
    right_edge = p.x_max - x

    left_mask = left_edge < p.absorb_width
    right_mask = right_edge < p.absorb_width

    eta[left_mask] = p.absorb_strength * (
        (p.absorb_width - left_edge[left_mask]) / p.absorb_width
    ) ** 2
    eta[right_mask] = p.absorb_strength * (
        (p.absorb_width - right_edge[right_mask]) / p.absorb_width
    ) ** 2
    return eta


# =====================================================================
# SPLIT-STEP FOURIER PROPAGATOR
# =====================================================================
class SplitStepPropagator:
    """
    One symmetric (Strang) split-operator time step:

        psi <- exp(-i V dt / 2hbar) psi                  (half potential step)
        psi <- IFFT{ exp(-i hbar k^2 dt / 2m) FFT{psi} }  (full kinetic step)
        psi <- exp(-i V dt / 2hbar) psi                  (half potential step)

    V = V_real(x) - i*eta(x); the imaginary part causes controlled norm
    loss only near the domain edges (the absorbing boundary).
    """

    def __init__(self, k, V_real, eta, dt, hbar=HBAR, mass=MASS):
        self.dt = dt
        V_complex = V_real - 1j * eta
        self.half_potential_phase = np.exp(-1j * V_complex * dt / (2 * hbar))
        self.kinetic_phase = np.exp(-1j * hbar * k ** 2 * dt / (2 * mass))

    def step(self, psi):
        psi = self.half_potential_phase * psi
        psi_k = fft(psi)
        psi_k = self.kinetic_phase * psi_k
        psi = ifft(psi_k)
        psi = self.half_potential_phase * psi
        return psi


# =====================================================================
# DIAGNOSTICS
# =====================================================================
def probability_density(psi, dx):
    """Per-cell probability (sums to total norm)."""
    return np.abs(psi) ** 2 * dx


def total_norm(psi, dx):
    return np.sum(probability_density(psi, dx))


def transmission_reflection(psi, x, dx, barrier_center, barrier_width):
    """Fraction of probability to the right (transmitted) / left (reflected)."""
    right_edge = barrier_center + barrier_width / 2
    left_edge = barrier_center - barrier_width / 2
    prob = probability_density(psi, dx)
    transmitted = np.sum(prob[x > right_edge])
    reflected = np.sum(prob[x < left_edge])
    under_barrier = np.sum(prob) - transmitted - reflected
    return transmitted, reflected, under_barrier


def probability_current(psi, dx, hbar=HBAR, mass=MASS):
    """
    Probability current density J(x) = (hbar/m) * Im(psi* dpsi/dx).
    Useful to visualize the net flow of probability (e.g. through the
    barrier) rather than just the density.
    """
    dpsi_dx = np.gradient(psi, dx)
    J = (hbar / mass) * np.imag(np.conj(psi) * dpsi_dx)
    return J


def mean_energy(p: SimulationParams, hbar=HBAR, mass=MASS):
    """
    Mean kinetic energy of the initial Gaussian packet:
        <E> = hbar^2 k0^2 / 2m  +  hbar^2 / (8 m sigma^2)
    (the second term is the extra energy from the packet's momentum
    spread, via the uncertainty principle).
    """
    return (hbar ** 2 * p.k0 ** 2) / (2 * mass) + (hbar ** 2) / (8 * mass * p.sigma ** 2)


# =====================================================================
# ANALYTIC (EXACT) TRANSMISSION COEFFICIENT, RECTANGULAR BARRIER
# =====================================================================
def analytic_transmission(E, V0, a, hbar=HBAR, m=MASS):
    """
    Exact 1D stationary-state transmission coefficient (textbook result):

      E < V0 (tunneling regime):
          kappa = sqrt(2m(V0-E))/hbar
          T = [1 + V0^2 sinh^2(kappa a) / (4E(V0-E))]^-1
      E > V0 (above barrier):
          k2 = sqrt(2m(E-V0))/hbar
          T = [1 + V0^2 sin^2(k2 a) / (4E(E-V0))]^-1
      E == V0:
          T = [1 + m V0 a^2 / (2 hbar^2)]^-1
    """
    if np.isclose(E, V0):
        return 1.0 / (1.0 + m * V0 * a ** 2 / (2 * hbar ** 2))
    elif E < V0:
        kappa = np.sqrt(2 * m * (V0 - E)) / hbar
        return 1.0 / (1.0 + (V0 ** 2 * np.sinh(kappa * a) ** 2) / (4 * E * (V0 - E)))
    else:
        k2 = np.sqrt(2 * m * (E - V0)) / hbar
        return 1.0 / (1.0 + (V0 ** 2 * np.sin(k2 * a) ** 2) / (4 * E * (E - V0)))


# =====================================================================
# FULL SIMULATION RUN (used by every sim script)
# =====================================================================
def run_simulation(p: SimulationParams, record_every=None, verbose=False):
    """
    Runs the full time evolution and returns a results dictionary:

        x, dx, k              : grids
        V_barrier              : barrier potential array
        snapshots, times       : list of |psi|^2 arrays and their times
        psi_snapshots          : list of complex psi arrays (for current/phase plots)
        E_mean                 : mean energy of the packet
        T_sim, R_sim, under_sim: final transmission/reflection/under-barrier probabilities
        T_theory                : analytic single-energy transmission coefficient
    """
    x, dx, k = build_grid(p)

    psi = gaussian_wave_packet(x, p.x0, p.k0, p.sigma)
    psi /= np.sqrt(total_norm(psi, dx))

    V_barrier = rectangular_barrier(x, p.V0, p.barrier_width, p.barrier_center)
    eta = absorbing_boundary(x, p)
    propagator = SplitStepPropagator(k, V_barrier, eta, p.dt)

    E_mean = mean_energy(p)

    if record_every is None:
        record_every = max(1, p.n_steps // p.n_frames)

    snapshots, psi_snapshots, times = [], [], []

    left_absorb_mask = (x - p.x_min) < p.absorb_width
    right_absorb_mask = (p.x_max - x) < p.absorb_width
    transmitted_accum = 0.0
    reflected_accum = 0.0

    for step in range(p.n_steps + 1):
        if step % record_every == 0:
            snapshots.append(np.abs(psi) ** 2)
            psi_snapshots.append(psi.copy())
            times.append(step * p.dt)

        if step < p.n_steps:
            dens_before = probability_density(psi, dx)
            norm_before = np.sum(dens_before)

            psi = propagator.step(psi)

            norm_after = total_norm(psi, dx)
            loss = norm_before - norm_after
            if loss > 1e-14:
                w_left = np.sum(dens_before[left_absorb_mask])
                w_right = np.sum(dens_before[right_absorb_mask])
                w_total = w_left + w_right
                if w_total > 0:
                    reflected_accum += loss * w_left / w_total
                    transmitted_accum += loss * w_right / w_total

    T_raw, R_raw, under_sim = transmission_reflection(
        psi, x, dx, p.barrier_center, p.barrier_width
    )
    T_sim = T_raw + transmitted_accum
    R_sim = R_raw + reflected_accum

    T_theory = analytic_transmission(E_mean, p.V0, p.barrier_width)

    if verbose:
        print(f"E_mean={E_mean:.4f}  V0={p.V0:.4f}  T_sim={T_sim:.4f}  "
              f"R_sim={R_sim:.4f}  T_theory={T_theory:.4f}")

    return dict(
        x=x, dx=dx, k=k, V_barrier=V_barrier, params=p,
        snapshots=snapshots, psi_snapshots=psi_snapshots, times=times,
        E_mean=E_mean, T_sim=T_sim, R_sim=R_sim, under_sim=under_sim,
        T_theory=T_theory,
    )
