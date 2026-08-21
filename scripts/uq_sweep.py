#!/usr/bin/env python3
"""UQ ensemble for the reproducible-result protocol (report Section 3.4).

Samples (delta, A, alpha) from independent uniform +/-10% boxes around the
protocol point, runs the lattice simulation at each sample, and writes the
results to CSV. The CSVs feed the tolerance band and the delta*A/alpha collapse
in uq_reproducible_result.ipynb.

Centred on the protocol point (A=1.0, delta=0.001, alpha=0.10), T=400.

Usage
-----
    python3 scripts/uq_sweep.py                          # 256 train + 32 test
    python3 scripts/uq_sweep.py --n-train 8 --n-test 2   # quick smoke test

Each CSV starts with '#' metadata lines (seed, versions, wall time) --
load with pandas.read_csv(path, comment='#').
"""

import argparse
import os
import platform
import sys
import time
from datetime import datetime, timezone
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from model import run_sim  # noqa: E402  (path set above)

REL = 0.10                                   # +/-10% manufacturing tolerance
N_SITES, DT = 200, 1e-4                      # protocol lattice and timestep

#        centre (delta, A, alpha)     T      n_train  n_test  seeds (train, test)
CONFIG = {'centre': (0.001, 1.0, 0.10), 'T': 400.0, 'n_train': 256, 'n_test': 32,
          'seeds': (42, 1234)}


def lhs(n, d, rng):
    """Latin hypercube in [0,1]^d: one point per stratum in every dimension."""
    out = np.empty((n, d))
    for j in range(d):
        out[:, j] = (rng.permutation(n) + rng.random(n)) / n
    return out


def make_samples(n, centre, rng):
    """LHS sample of (delta, A, alpha) in the +/-REL box around `centre`."""
    c = np.asarray(centre)
    lo, hi = c * (1 - REL), c * (1 + REL)
    return lo + lhs(n, 3, rng) * (hi - lo)


def one_run(args):
    delta, A, alpha, T = args
    t0 = time.perf_counter()
    v_sim, v_pred, ratio = run_sim(A=A, delta=delta, alpha=alpha,
                                   N=N_SITES, T=T, dt=DT)
    return delta, A, alpha, v_sim, v_pred, ratio, time.perf_counter() - t0


def run_ensemble(X, T, out_csv, workers, seed, label):
    jobs = [(d, a, al, T) for d, a, al in X]

    # Time the first run alone so the projection is printed before committing
    t0 = time.perf_counter()
    first = one_run(jobs[0])
    per_run = time.perf_counter() - t0
    est = per_run * (len(jobs) - 1) / workers
    print(f"[{label}] first run {per_run:.1f}s -> "
          f"~{est/60:.0f} min for the remaining {len(jobs)-1} on {workers} workers")

    with Pool(workers) as pool:
        rest = pool.map(one_run, jobs[1:])
    rows = [first] + rest
    wall = time.perf_counter() - t0

    with open(out_csv, 'w') as f:
        f.write(f"# uq_sweep.py {label}  {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")
        f.write(f"# seed={seed}  n={len(rows)}  N={N_SITES}  T={T}  dt={DT}  rel_tol={REL}\n")
        f.write(f"# python={platform.python_version()}  numpy={np.__version__}\n")
        f.write(f"# wall_seconds={wall:.0f}  workers={workers}\n")
        f.write("delta,A,alpha,v_sim,v_pred,ratio,run_seconds\n")
        for r in rows:
            f.write(f"{r[0]:.8g},{r[1]:.8g},{r[2]:.8g},{r[3]:.6f},{r[4]:.6f},{r[5]:.6f},{r[6]:.1f}\n")

    n_ok = sum(1 for r in rows if np.isfinite(r[3]))
    print(f"[{label}] wrote {len(rows)} rows ({n_ok} propagated) -> {out_csv}  "
          f"[{wall/60:.1f} min]")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--n-train', type=int, default=None)
    p.add_argument('--n-test', type=int, default=None)
    p.add_argument('--workers', type=int, default=8)
    args = p.parse_args()

    cfg = CONFIG
    n_train = args.n_train if args.n_train is not None else cfg['n_train']
    n_test = args.n_test if args.n_test is not None else cfg['n_test']
    seed_train, seed_test = cfg['seeds']
    prefix, prefix_t = 'uq_train', 'uq_test'

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    os.makedirs(out_dir, exist_ok=True)

    X_train = make_samples(n_train, cfg['centre'], np.random.default_rng(seed_train))
    X_test = make_samples(n_test, cfg['centre'], np.random.default_rng(seed_test))

    run_ensemble(X_train, cfg['T'], os.path.join(out_dir, f'{prefix}.csv'),
                 args.workers, seed_train, 'train')
    run_ensemble(X_test, cfg['T'], os.path.join(out_dir, f'{prefix_t}.csv'),
                 args.workers, seed_test, 'test')


if __name__ == '__main__':
    main()
