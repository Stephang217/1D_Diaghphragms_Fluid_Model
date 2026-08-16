"""Dimensionless diaphragm chain: the (eta, theta, Pi, Omega) simulator.

This is the extraction of the simulator cell of dimensionless_model.ipynb, in the
same relationship to that notebook as src/model.py is to diaphragm_metafluid.ipynb.
The notebook keeps its own inline copy so it reads top to bottom without imports;
the two must be kept in step. scripts/closed_form_check.py calls check_canonical()
before every sweep, which fails loudly if they have drifted apart.

The only addition beyond the notebook cell is the u_init argument to run(), which
replaces the default sharp-step start with a supplied displacement field. It
defaults to None, so every existing call behaves exactly as before.
"""
import numpy as np

# The canonical point of dimensionless_model.ipynb cell 1, and the speed it gives.
# Used by check_canonical() as a guard against this file drifting from the notebook.
CANONICAL = dict(eta=80.0, theta=0.1, Pi=0.115, Omega=10.0)
CANONICAL_SPEED = 0.0687139990  # run(**CANONICAL, N=200, T=150)


def wells(Pi):
    """The three rest states: roots of  u^3 - u + Pi = 0,  sorted low < mid < high."""
    r = np.sort(np.roots([1, 0, -1, Pi]).real)
    return r[0], r[1], r[2]


def gas_force(u, eta, theta):
    """Boyle-law pressure force on each diaphragm."""
    p = 1.0 / (1.0 + theta * (u[1:] - u[:-1]))     # 1 / volume of each gas pocket
    F = np.zeros_like(u)
    F[1:-1] = eta * (p[:-1] - p[1:])
    return F


def energy(u, v, eta, theta, Pi):
    """Total energy: motion + the double-well + the gas."""
    gaps = 1.0 + theta * (u[1:] - u[:-1])
    well = u**4/4 - u**2/2 + Pi*u
    return 0.5*np.sum(v**2) + np.sum(well) - (eta/theta)*np.sum(np.log(gaps))


def front_speed(frames, times, u_lo, u_hi, flip=False):
    """Track where the wave front is in each frame and fit its speed."""
    N = frames.shape[1]
    mid = 0.5*(u_lo + u_hi)
    pos = []
    for f in frames:
        sel = np.where(f < mid)[0] if not flip else np.where(f > mid)[0]
        if len(sel) == 0:
            pos.append(0.0)
        elif sel[-1] + 1 >= N:
            pos.append(float(sel[-1]))
        else:
            i = sel[-1]
            pos.append(i + (f[i] - mid) / (f[i] - f[i+1]))   # sub-diaphragm crossing
    pos = np.array(pos)
    half = times > 0.5*times[-1]                             # steady half only
    return (np.polyfit(times[half], pos[half], 1)[0] if half.sum() > 2 else np.nan), pos


def grad4(u):
    """du/dn by a 4th-order central difference, unit spacing.

    np.gradient is 2nd order; on a front a few sites wide its truncation error is a
    percent or more and always biases the gradient integral low. See the simulator
    cell of dimensionless_model.ipynb for the measured size of the effect.
    """
    g = np.zeros_like(u)
    g[2:-2] = (-u[4:] + 8*u[3:-1] - 8*u[1:-3] + u[:-4]) / 12.0
    g[1], g[-2] = (u[2]-u[0])/2, (u[-1]-u[-3])/2      # 2nd order at the edges
    return g


def gradient_integral(u):
    """I = int (dU/dxi)^2 dxi, estimated from a lattice snapshot."""
    return float(np.sum(grad4(u)**2))


def run(eta, theta, Pi, Omega, N=120, T=150.0, dt=None,
        n_sponge=10, sponge=4.0, n_trigger=5, save_every=200,
        track_energy=False, flip=False, u_init=None):
    """
    Integrate the chain and return the wave.

    Normally the left end is held low and the rest starts high; the boundary travels
    right as a wave. With flip=True the roles swap (left end high, rest low), which
    runs the mirrored wave. u_init replaces the default sharp-step start with a given
    displacement field (the boundary sites are re-imposed on top of it). Returns a
    dict with frames, times, wave position and speed, or {'error': ...} if a gas
    pocket collapses.
    """
    if dt is None:
        dt = 0.05 / max(np.sqrt(2 + 4*abs(eta*theta)), Omega)
    u_lo, _, u_hi = wells(Pi)
    bg, trig = (u_hi, u_lo) if not flip else (u_lo, u_hi)

    # a little extra damping near the walls so the wave is absorbed, not reflected
    damp = np.full(N, float(Omega))
    if n_sponge > 0:
        ramp = sponge * ((n_sponge - np.arange(n_sponge)) / n_sponge)**2
        damp[:n_sponge]  += ramp
        damp[-n_sponge:] += ramp[::-1]

    if u_init is None:
        u = np.full(N, bg)
    else:
        u = np.asarray(u_init, dtype=float).copy()
    u[:n_trigger] = trig; u[-1] = bg
    v = np.zeros(N)
    force = lambda uu: gas_force(uu, eta, theta) - (uu**3 - uu + Pi)

    steps = int(T / dt)
    frames, E = [], []
    a = force(u) - damp*v
    for step in range(steps):
        u += v*dt + 0.5*a*dt**2
        u[:n_trigger] = trig; u[-1] = bg
        v[:n_trigger] = 0.0;  v[-1] = 0.0
        if step > steps//10 and np.min(1 + theta*(u[1:]-u[:-1])) <= 0:
            return {'error': 'a gas pocket collapsed to zero volume'}
        f = force(u)
        v = (v + 0.5*dt*(a + f)) / (1 + 0.5*damp*dt)   # semi-implicit, handles damping
        v[:n_trigger] = 0.0; v[-1] = 0.0
        a = f - damp*v
        if step % save_every == 0:
            frames.append(u.copy())
            if track_energy: E.append(energy(u, v, eta, theta, Pi))

    frames = np.array(frames)
    times  = np.arange(len(frames)) * save_every * dt
    speed, pos = front_speed(frames, times, u_lo, u_hi, flip=flip)

    out = {'frames': frames, 'times': times, 'pos': pos, 'speed': speed,
           'u_lo': u_lo, 'u_hi': u_hi, 'dt': dt}
    if track_energy: out['energy'] = np.array(E)
    return out


def check_canonical(tol=1e-9):
    """Fail loudly if this file has drifted from the notebook's simulator cell."""
    v = run(N=200, T=150.0, **CANONICAL)['speed']
    if abs(v - CANONICAL_SPEED) > tol:
        raise AssertionError(
            f"src/dimless.py has drifted from dimensionless_model.ipynb: canonical "
            f"speed is {v:.10f}, expected {CANONICAL_SPEED:.10f}")
    return v

