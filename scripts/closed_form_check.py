#!/usr/bin/env python3
"""Validation of the closed-form speed  v* = 3 Pi sqrt(2 kappa) / (2 Omega).

The energy-balance speed of Section 2.6 is v* = dpsi / (Omega * I) with
I = \\int U'^2 dxi, which is not a closed form: I depends on the profile, which
depends on v.  Substituting the continuum kink U = tanh(xi / w) with w = sqrt(2 kappa)
closes it.  For a kink of amplitude +/-1, I = 4 / (3w), and with dpsi = 2 Pi
(Appendix D) this gives

    v* = 2 Pi / (Omega * 4 / (3w)) = 3 Pi w / (2 Omega),    w = sqrt(2 kappa).

Two approximations went into that and they fail for different reasons, so this
script measures them separately rather than reporting one combined error:

    v_EB / v_meas      the energy-balance formula itself, using the *measured*
                       gradient integral.  Known from Section 3.2 to degrade as
                       Omega falls, where the front's inertia and the lattice
                       waves it radiates stop being negligible.

    v_closed / v_EB    the tanh substitution and the leading-order dpsi = 2 Pi.
                       Expected to degrade as Pi grows, where the O(Pi^2) terms
                       in both the well depth and the well separation bite.

Reporting only v_closed / v_meas would blend the two and make "where does it
degrade" unattributable.

The sweep is restricted to wide fronts (w >= 3 sites) and moderate-to-high damping,
which is where the energy-balance formula is known to hold in the first place --
this validates the closed form, not the formula it closes.

Usage
-----
    python3 scripts/closed_form_check.py                 # full grid, ~5 min on 8 workers
    python3 scripts/closed_form_check.py --quick         # coarse grid, ~30 s

Writes results/closed_form_validation.csv with '#' metadata lines -- load with
pandas.read_csv(path, comment='#').  Deterministic: no randomness, no seed.
"""

import argparse
import os
import platform
import sys
import time
from datetime import datetime, timezone
from multiprocessing import Pool, cpu_count

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from dimless import run, check_canonical, gradient_integral  # noqa: E402

THETA = 0.1                      # held fixed; kappa is dialled through eta
KAPPAS = [4.5, 8.0, 12.5, 18.0, 32.0]                    # w = 3, 4, 5, 6, 8 sites
PIS = [0.02, 0.05, 0.08, 0.115, 0.15, 0.20, 0.25, 0.30]
OMEGAS = [1.0, 3.0, 10.0, 30.0]

T_CAP = 8000.0                   # ceiling on run time for the slowest corners
MIN_MOVE = 15.0                  # below this the speed fit is not trustworthy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'results', 'closed_form_validation.csv')


def one_run(task):
    """One (kappa, Pi, Omega) point.  Returns a dict, or None if it did not resolve."""
    kappa, Pi, Omega = task
    w = np.sqrt(2*kappa)
    v_closed = 3*Pi*w / (2*Omega)

    # Long enough for the front to travel several times its OWN WIDTH -- the speed
    # settles long before the profile does, and I is a property of the profile.
    # Sizing on a fixed number of sites left wide fronts still relaxing, which read
    # as a spurious 1% drift in v_EB. Floor at ten ring-down times (tau = 2/Omega).
    T = float(min(max(25.0*w/v_closed, 20.0/Omega), T_CAP))
    dt = 0.05 / max(np.sqrt(2 + 4*kappa), Omega)
    save_every = max(1, int(T/dt/400))          # ~400 frames whatever the point

    # The lattice has to hold the whole journey plus a front and both sponges,
    # otherwise the longer runs above simply drive the front into the sponge.
    travel = v_closed*T
    N = int(np.clip(40 + travel + 8*w + 40, 150, 900))
    r = run(kappa/THETA, THETA, Pi, Omega, N=N, T=T, save_every=save_every)
    if 'error' in r or not np.isfinite(r.get('speed', np.nan)) or r['speed'] <= 0:
        return None

    moved = r['pos'][-1] - r['pos'][0]
    # A front that has reached the sponge is decelerating, not travelling.
    fits = bool(r['pos'].max() < N - 10 - 10) and moved >= MIN_MOVE

    # Energy balance with the MEASURED gradient integral (as in the notebook's
    # arrieta_ratio): this is v* before the tanh substitution is made. The integral
    # uses a 4th-order stencil -- np.gradient's truncation error is 2.8% at w = 3
    # and would be mistaken for the formula failing on narrow fronts.
    snap = r['frames'][int(0.75*(len(r['frames']) - 1))]
    I_meas = gradient_integral(snap)
    psi = lambda u: u**4/4 - u**2/2 + Pi*u
    dpsi = psi(r['u_hi']) - psi(r['u_lo'])
    v_EB = dpsi / (Omega * I_meas)

    return dict(kappa=kappa, Pi=Pi, Omega=Omega, w=w, T=T, dt=dt, N=N,
                v_meas=r['speed'], v_EB=v_EB, v_closed=v_closed,
                I_meas=I_meas, I_tanh=4.0/(3*w), dpsi=dpsi, dpsi_lead=2*Pi,
                moved=moved, fits=int(fits))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true', help='coarse grid for a smoke test')
    ap.add_argument('--workers', type=int, default=max(1, cpu_count() - 1))
    args = ap.parse_args()

    kappas, pis, omegas = KAPPAS, PIS, OMEGAS
    if args.quick:
        kappas, pis, omegas = [4.5, 8.0, 32.0], [0.05, 0.115, 0.30], [3.0, 10.0]

    print(f"checking src/dimless.py against the notebook... ", end='', flush=True)
    print(f"canonical v = {check_canonical():.8f}  OK")

    tasks = [(k, p, o) for k in kappas for p in pis for o in omegas]
    print(f"{len(tasks)} points: kappa={kappas}, Pi={pis}, Omega={omegas}")

    t0 = time.time()
    with Pool(args.workers) as pool:
        rows = [r for r in pool.map(one_run, tasks) if r]
    wall = time.time() - t0

    cols = ['kappa', 'Pi', 'Omega', 'w', 'T', 'dt', 'N', 'v_meas', 'v_EB', 'v_closed',
            'I_meas', 'I_tanh', 'dpsi', 'dpsi_lead', 'moved', 'fits']
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(f"# closed-form speed validation, written {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"# v_closed = 3*Pi*sqrt(2*kappa)/(2*Omega);  theta={THETA} fixed, eta=kappa/theta\n")
        f.write(f"# kappa={kappas} Pi={pis} Omega={omegas}\n")
        f.write(f"# N sized per point (travel + front + sponges), T_cap={T_CAP} min_move={MIN_MOVE}\n")
        f.write(f"# n={len(rows)} wall={wall:.0f}s workers={args.workers}\n")
        f.write(f"# python={platform.python_version()}  numpy={np.__version__}  {platform.platform()}\n")
        f.write(','.join(cols) + "\n")
        for r in rows:
            f.write(','.join(f"{r[c]:.10g}" for c in cols) + "\n")
    print(f"wrote {OUT}  ({len(rows)} rows, {wall:.0f}s)")

    summarise(rows)


def summarise(rows):
    ok = [r for r in rows if r['fits']]
    if not ok:
        print("no points resolved")
        return
    closed = np.array([r['v_closed']/r['v_meas'] for r in ok])
    print(f"\nresolved {len(ok)}/{len(rows)} points  (w >= 3 sites, Omega >= 1)")
    print(f"v_closed / v_meas:  median {np.median(closed):.3f}   "
          f"range {closed.min():.3f} to {closed.max():.3f}")

    def table(key, label):
        print(f"\n  {label:>7} |  v_closed/v_meas   v_closed/v_EB   v_EB/v_meas   n")
        print(f"  {'-'*7}-+-{'-'*54}")
        for val in sorted({r[key] for r in ok}):
            g = [r for r in ok if r[key] == val]
            a = np.mean([r['v_closed']/r['v_meas'] for r in g])
            b = np.mean([r['v_closed']/r['v_EB'] for r in g])
            c = np.mean([r['v_EB']/r['v_meas'] for r in g])
            print(f"  {val:7.3f} |      {a:6.3f}           {b:6.3f}         {c:6.3f}    {len(g):2d}")

    table('Pi', 'Pi')
    table('Omega', 'Omega')
    table('w', 'w')


if __name__ == '__main__':
    main()
