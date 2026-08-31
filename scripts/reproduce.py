#!/usr/bin/env python3
"""Reproduce the wave speed of report Section 3.4 from a clean checkout.

This is the front door for the reproducible-result protocol: one simulation at
the protocol point, compared against the reference value the report quotes.

It imports numpy and nothing else, so it needs neither Jupyter, pandas nor
matplotlib. That is deliberate. The only job of this script is to succeed on a
machine that is not the author's, and every dependency it does not have is a
failure mode it cannot hit. uq_reproducible_result.ipynb is the fuller route,
for anyone who also wants the tolerance ensembles, the disorder study and the
figures; it calls the same run_sim from src/model.py that this script calls, so
the two cannot disagree.

The simulation is deterministic, with no compiled extensions, no GPU and no
randomness anywhere, so a rerun should match the reference to floating-point
round-off. TOLERANCE below is the wider numerical uncertainty the report quotes
from the convergence studies of Appendix F.

Usage
-----
    python3 scripts/reproduce.py

Takes about a minute on one core. Exits 0 on a match, 1 otherwise.
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from model import run_sim  # noqa: E402  (path set above)

# The protocol point, in the dimensional variables run_sim takes. run_sim fixes
# the remaining parameters at m = k = 1 and a^2 = 0.09, so in the four groups of
# report equation (5) this point is
#     eta = 37.04,  theta = 0.300,  Pi = 0.0370,  Omega = 0.3333
# giving a coupling kappa = 11.11 and a front width w = sqrt(2 kappa) = 4.71
# lattice spacings. Speeds below are in sites per unit dimensional time, the
# convention of report Figures 10 and 11.
PARAMS = dict(A=1.0, delta=0.001, alpha=0.10, N=200, T=400, dt=1e-4)

REFERENCE = 0.2205603205452594   # results/protocol_point.csv, v_sim
TOLERANCE = 1e-4                 # the numerical uncertainty quoted in Section 3.4


def main():
    print('Protocol point: ' + '  '.join(f'{k}={v}' for k, v in PARAMS.items()))
    print('Running (about a minute) ...', flush=True)

    t0 = time.time()
    v_sim, v_pred, ratio = run_sim(**PARAMS)
    wall = time.time() - t0

    print(f'\n  measured speed   v_sim  = {v_sim:.10f}')
    print(f'  energy balance   v_pred = {v_pred:.10f}')
    print(f'  ratio                   = {ratio:.6f}')
    print(f'  reference               = {REFERENCE:.10f}')
    print(f'  difference              = {abs(v_sim - REFERENCE):.3e}   (tolerance {TOLERANCE:.0e})')
    print(f'  wall time               = {wall:.1f} s')

    if abs(v_sim - REFERENCE) <= TOLERANCE:
        print('\nREPRODUCED: within the quoted numerical uncertainty.')
        return 0

    print('\nNOT REPRODUCED: outside the quoted numerical uncertainty.')
    print('Check the numpy version against requirements.txt before reading anything into this.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
