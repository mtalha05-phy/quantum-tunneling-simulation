# Theory & Numerical Method

## 1. The physical problem

A particle of mass `m`, represented by a wave function `Psi(x,t)`, is
incident on a rectangular potential barrier:

```
V(x) = V0   for |x - x_center| <= a/2
V(x) = 0    otherwise
```

Classically: if the particle's kinetic energy `E` is less than `V0`, it
is reflected with 100% probability. Quantum mechanically, the wave
function does not vanish inside the barrier — it decays exponentially
but remains nonzero — so there is a finite probability `T` that the
particle is found on the far side. This is **quantum tunneling**.

The system evolves under the time-dependent Schrodinger equation (TDSE):

```
i * hbar * dPsi/dt = -(hbar^2 / 2m) * d^2Psi/dx^2 + V(x) * Psi
```

This project uses natural units `hbar = 1`, `m = 1`, which is the
standard convention for this kind of teaching/research simulation —
all lengths, times and energies are then dimensionless multiples of
whatever physical units you choose to interpret them as.

## 2. Initial state: a Gaussian wave packet

A localized particle with a well-defined mean momentum is represented
by a **minimum-uncertainty Gaussian wave packet**:

```
Psi(x,0) = (2*pi*sigma^2)^(-1/4) * exp(-(x-x0)^2 / (4*sigma^2)) * exp(i*k0*x)
```

- `x0`  — initial mean position
- `k0`  — mean momentum (sets the mean energy `E ~ hbar^2 k0^2 / 2m`)
- `sigma` — spatial width (position uncertainty)

Because of the uncertainty principle, this packet also has a *spread*
of momenta (and therefore energies) of width `~ 1/(2*sigma)`. This
matters later: a wave packet's measured transmission will differ
slightly from the single-energy analytic formula because it is really
a superposition of many energies, not one.

## 3. Numerical method: Split-Step Fourier (Split-Operator)

Exponentiating the full Hamiltonian directly is expensive. Instead we
use **Strang splitting** to approximate the time-evolution operator
for one small time step `dt`:

```
exp(-i*H*dt/hbar) ~= exp(-i*V*dt/2hbar) * exp(-i*T*dt/hbar) * exp(-i*V*dt/2hbar)
```

where `T` is the kinetic energy operator and `V` is the potential
energy operator. This is accurate to `O(dt^3)` per step.

- The **potential** half-steps are diagonal in *position* space, so
  they are just a pointwise multiplication by `exp(-i*V(x)*dt/2hbar)`.
- The **kinetic** step is diagonal in *momentum* space. We move to
  momentum space with an FFT, multiply by `exp(-i*hbar*k^2*dt/2m)`,
  and transform back with an inverse FFT.

Each full time step therefore costs `O(N log N)` (dominated by the
FFT), rather than `O(N^2)` or worse for a naive matrix exponential —
and the method is unconditionally stable and exactly unitary (norm
is conserved) when `V` is real.

## 4. Absorbing boundaries

The FFT grid is implicitly **periodic**: a wave that reaches the right
edge of the simulation box would wrap around and reappear on the left,
which is unphysical for a scattering problem. To prevent this, a small
**complex absorbing potential (CAP)**, `-i*eta(x)`, is added near each
edge of the domain. Its imaginary part causes controlled probability
loss only in that thin edge layer, mimicking an open (infinite)
domain.

This project tracks *where* probability is absorbed (left edge vs.
right edge) and folds it back into the reflection/transmission
statistics, so `T + R + (probability still under the barrier) ~= 1`
even though some probability physically left through the CAP.

## 5. Diagnostics computed

- **Transmission coefficient `T`**: total probability found to the
  right of the barrier once the collision is over.
- **Reflection coefficient `R`**: total probability found to the left.
- **Probability current** `J(x) = (hbar/m) * Im(Psi* dPsi/dx)`: the
  local flow of probability, useful for visualizing flux through the
  barrier rather than just density.

## 6. Analytic benchmark

For a **single-energy plane wave** (not a wave packet), the exact
stationary-state transmission coefficient through a rectangular
barrier is known in closed form:

- `E < V0` (tunneling regime):

  ```
  kappa = sqrt(2m(V0-E)) / hbar
  T = [1 + V0^2 * sinh^2(kappa*a) / (4*E*(V0-E))]^-1
  ```

- `E > V0` (above-barrier scattering, with resonances):

  ```
  k2 = sqrt(2m(E-V0)) / hbar
  T = [1 + V0^2 * sin^2(k2*a) / (4*E*(E-V0))]^-1
  ```

This project uses that formula (`qtunnel.core.analytic_transmission`)
as a sanity check against the simulated wave-packet result.

## 7. Known numerical limitation

For very opaque barriers (large `V0*a^2`), the *true* transmission
coefficient becomes extremely small (e.g. `1e-6` or smaller). The
wave-packet simulation's measured transmission floors out around
`1e-3`–`1e-4` in that regime due to finite floating-point precision
and small residual leakage through the absorbing boundary — not new
physics. Trust the analytic formula, not the simulated value, once `T`
drops below roughly `1e-3`. See `simulations/sim5_barrier_width_effect.py`
for a demonstration and further discussion.

## 8. Suggested extensions

- 2D or 3D tunneling (e.g. tunneling through a finite-width wall with
  transverse spreading)
- Time-dependent or oscillating barriers
- Double-barrier resonant tunneling (quantum well between two
  barriers) — a classic demonstration of transmission resonances
- WKB approximation comparison for smoothly varying (non-rectangular)
  potentials
- Crank-Nicolson solver as an alternative to split-step Fourier, useful
  when a strictly non-periodic (Dirichlet) boundary is required
