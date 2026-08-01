"""Discrete bistable-diaphragm chain simulator (dimensional form).

This is a verbatim extraction of `run_sim` from diaphragm_metafluid.ipynb
(the D3/D4 sweep cell), so scripts can import the exact simulator the
notebook results were produced with. The notebook remains the source of the
validation story (convergence, energy audit); this module exists so the UQ
ensemble and the reproducible-result protocol call one shared implementation.

Physics: N bistable diaphragms coupled by sealed isothermal gas pockets
(Boyle's law), velocity-Verlet integration with semi-implicit damping,
absorbing sponge layers at both ends, sustained trigger on the left.
"""

import numpy as np


def run_sim(A, delta, alpha, N=120, T=150, dt=1e-4,
            n_sponge=10, damp_max=4.0, n_trigger=5):
    """
    Run one simulation and return (v_measured, v_predicted, ratio).

    This is a self-contained copy of the main simulation that accepts
    A, delta, and alpha as arguments, so the parameter sweep can call it cleanly
    without clobbering the notebook-level variables.

    v_predicted uses the Arrieta formula with ∫(du/dξ)² computed from a mid-run
    snapshot — cleaner than the last-frame snapshot (which sits near the sponge), because the
    mid-run kink is in the bulk of the lattice, not near the sponge boundary.

    Returns (nan, nan, nan) if the wave fails to propagate (e.g. volume collapse).
    """
    a2 = 0.09
    m = 1.0; p0 = 1.0; v0 = 1.0

    # ── Well positions ────────────────────────────────────────────────────────
    roots = np.roots([1, 0, -a2, delta])
    real_roots = sorted(roots[np.abs(roots.imag) < 1e-10].real)
    if len(real_roots) < 3:
        return np.nan, np.nan, np.nan     # delta too large means no bistability
    u_lo, _, u_hi = real_roots

    def psi(u):
        return u**4/4 - a2*u**2/2 + delta*u

    # ── Damping array with sponge layers ─────────────────────────────────────
    damp = np.ones(N) * alpha
    for i in range(n_sponge):
        strength = damp_max * ((n_sponge - i) / n_sponge)**2
        damp[i]         += strength
        damp[N - 1 - i] += strength

    # ── Force functions (same physics as notebook top) ────────────────────────
    def f_bistable(u):
        return u**3 - a2*u + delta

    def pressure_force(u):
        F = np.zeros_like(u)
        sv        = v0 + A * (u[1:] - u[:-1])
        pressures = p0 * v0 / sv
        F[1:-1]   = A * (pressures[:-1] - pressures[1:])
        return F

    def net_force(u):
        return pressure_force(u) - f_bistable(u)

    def accel(u, v):
        return (net_force(u) - damp * v) / m

    # ── Initial conditions ────────────────────────────────────────────────────
    u = np.ones(N) * u_hi
    u[:n_trigger] = u_lo
    v = np.zeros(N)

    steps      = int(T / dt)
    save_every = 500
    history    = []
    a_arr      = accel(u, v)

    # ── Time loop (semi-implicit Verlet) ────────────────────────────────────────
    for step in range(steps):
        u     += v * dt + 0.5 * a_arr * dt**2
        u[:n_trigger] = u_lo;  u[-1] = u_hi
        v[:n_trigger] = 0.0;   v[-1] = 0.0
        # Volume collapse check — only after warm-up (initial step smooths out)
        if step > steps // 10:
            sv_check = v0 + A * (u[1:] - u[:-1])
            if np.any(sv_check <= 0):
                return np.nan, np.nan, np.nan
        F_new  = net_force(u)
        v      = (v + 0.5 * dt * (a_arr + F_new / m)) / (1.0 + 0.5 * damp * dt / m)
        v[:n_trigger] = 0.0;   v[-1] = 0.0
        a_arr  = (F_new - damp * v) / m
        if step % save_every == 0:
            history.append(u.copy())

    history = np.array(history)

    # ── Wave speed: linear fit to front position vs time ─────────────────────
    mid = 0.5 * (u_lo + u_hi)
    front_pos = []
    for snap in history:
        front = np.where(snap < mid)[0]
        front_pos.append(front[-1] if len(front) else 0)
    front_pos = np.array(front_pos, dtype=float)
    times     = np.arange(len(history)) * save_every * dt

    # Skip first 20% as transient; check the wave actually moved (std > 0)
    steady = times > 0.2 * T
    if steady.sum() < 5 or front_pos[steady].std() < 1e-6:
        return np.nan, np.nan, np.nan
    v_measured, _ = np.polyfit(times[steady], front_pos[steady], 1)
    if v_measured < 1e-6:
        return np.nan, np.nan, np.nan    # wave stalled (volume collapse or no driving)

    # ── Arrieta formula: gradient integral from mid-run snapshot ─────────────
    # Use the middle frame to get the kink in the bulk, away from sponge distortion.
    snap_mid        = history[len(history) // 2]
    du_dn           = np.gradient(snap_mid)
    integral_direct = np.sum(du_dn**2)
    energy_diff     = psi(u_hi) - psi(u_lo)

    if integral_direct < 1e-12:
        return v_measured, np.nan, np.nan

    v_predicted = energy_diff / (alpha * integral_direct)
    ratio       = v_predicted / v_measured

    return v_measured, v_predicted, ratio
