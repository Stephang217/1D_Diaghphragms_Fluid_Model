#!/usr/bin/env python3
"""Per-diaphragm disorder ensemble (report Section 3.5).

This answers a different question from scripts/uq_sweep.py, and the two should not
be conflated. uq_sweep.py varies a *single* delta for the whole chain, which asks
"if this batch of diaphragms came out 5% off spec, how wrong is the speed?".  Here
every diaphragm gets its own delta,

    delta_n = delta_0 * (1 + sigma * eps_n),    eps_n ~ N(0, 1),

which asks "if the diaphragms differ from *each other*, how wrong is the speed?".

The physical expectation is that the second effect is much the smaller of the two.
A front spanning w lattice sites is driven by roughly w independent values of
delta at any instant, so it responds to their average rather than to any one of
them, and the spread in wave speed should fall roughly as 1/sqrt(w) relative to
the spread in delta itself.  The ensemble below measures whether it does.

Usage
-----
    python3 scripts/disorder_sweep.py                    # 4 sigmas x 8 seeds
    python3 scripts/disorder_sweep.py --n-seeds 2        # quick smoke test

Writes results/disorder.csv with '#' metadata lines -- load with
pandas.read_csv(path, comment='#').
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
from model import run_sim  # noqa: E402  (path set above)

# Protocol point, identical to uq_sweep.py so the two ensembles are comparable.
DELTA0, A0, ALPHA0 = 0.001, 1.0, 0.10
N_SITES, DT, T_RUN = 200, 1e-4, 400.0
SIGMAS = [0.0, 0.05, 0.10, 0.20]             # relative spread of delta site to site
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'disorder.csv')


def one_run(task):
    """Run a single disordered chain. Returns a dict, or None if it failed."""
    sigma, seed = task
    rng = np.random.default_rng(seed)
    if sigma == 0.0:
        field = np.full(N_SITES, DELTA0)     # exact homogeneous control
    else:
        field = DELTA0 * (1.0 + sigma * rng.standard_normal(N_SITES))
    # A negative delta flips which well is lower and would change the problem
    # rather than perturb it; at these sigmas it never occurs, but guard anyway.
    if np.any(field <= 0):
        return None
    v, v_pred, ratio = run_sim(A=A0, delta=DELTA0, alpha=ALPHA0,
                               N=N_SITES, T=T_RUN, dt=DT, delta_field=field)
    if not np.isfinite(v):
        return None
    return dict(sigma=sigma, seed=seed, v_sim=v, v_pred=v_pred, ratio=ratio,
                delta_realised_mean=field.mean(), delta_realised_std=field.std())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-seeds', type=int, default=8)
    ap.add_argument('--workers', type=int, default=max(1, cpu_count() - 1))
    args = ap.parse_args()

    tasks = [(s, 1000 + i) for s in SIGMAS for i in range(args.n_seeds)]
    # sigma=0 is deterministic, so one run of it is enough; drop the duplicates.
    tasks = [t for t in tasks if not (t[0] == 0.0 and t[1] != 1000)]

    print(f"{len(tasks)} runs over sigma in {SIGMAS}, {args.n_seeds} seeds each")
    t_one = time.time()
    first = one_run(tasks[0])
    dt_one = time.time() - t_one
    print(f"one run took {dt_one:.0f}s -> projected "
          f"{dt_one*len(tasks)/args.workers/60:.1f} min on {args.workers} workers")

    t0 = time.time()
    with Pool(args.workers) as pool:
        rows = [r for r in pool.map(one_run, tasks) if r]
    wall = time.time() - t0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(f"# per-diaphragm disorder ensemble, written {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"# delta0={DELTA0} A={A0} alpha={ALPHA0} N={N_SITES} T={T_RUN} dt={DT}\n")
        f.write(f"# sigmas={SIGMAS} n_seeds={args.n_seeds} seeds from 1000\n")
        f.write(f"# n={len(rows)} wall={wall:.0f}s workers={args.workers}\n")
        f.write(f"# python={platform.python_version()}  numpy={np.__version__}  {platform.platform()}\n")
        f.write("sigma,seed,v_sim,v_pred,ratio,delta_realised_mean,delta_realised_std\n")
        for r in rows:
            f.write(f"{r['sigma']},{r['seed']},{r['v_sim']:.8f},{r['v_pred']:.8f},"
                    f"{r['ratio']:.8f},{r['delta_realised_mean']:.10f},"
                    f"{r['delta_realised_std']:.10f}\n")
    print(f"wrote {OUT}  ({len(rows)} rows, {wall:.0f}s)")

    v0 = [r['v_sim'] for r in rows if r['sigma'] == 0.0]
    print(f"\n  sigma   n   mean v      spread (%)   shift vs homogeneous (%)")
    for s in SIGMAS:
        vs = np.array([r['v_sim'] for r in rows if r['sigma'] == s])
        if not len(vs):
            continue
        spread = 100*vs.std()/vs.mean() if len(vs) > 1 else 0.0
        shift = 100*(vs.mean() - v0[0])/v0[0] if v0 else float('nan')
        print(f"  {s:5.2f}  {len(vs):2d}   {vs.mean():.5f}    {spread:6.2f}      {shift:+7.2f}")


if __name__ == '__main__':
    main()
