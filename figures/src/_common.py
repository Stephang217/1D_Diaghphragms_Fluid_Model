"""Shared setup for the figures that are not produced by a notebook.

Everything visual comes from src/plotstyle.py, so these and the notebook
figures share one palette, one set of font sizes and one figure geometry.
"""
import os
import sys

import numpy as np                                          # noqa: F401 (re-export)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                             # noqa: F401 (re-export)

REPO = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'src'))

from dimless import run, wells                              # noqa: E402,F401
from plotstyle import (use, C, WONG, width, full, half,     # noqa: E402,F401
                       two_panel, stacked, label_line, spacetime,
                       _layout, _strip_titles, TITLES_IN_SAVED_FIGURES)

use()

PI, OM, THETA_C, KAPPA_C = 0.115, 10.0, 0.1, 8.0


def pockets(frames, theta):
    """Pocket volumes  Vtilde_n = 1 + theta (u_{n+1} - u_n),  one per gas pocket."""
    return 1.0 + theta * (frames[:, 1:] - frames[:, :-1])


def save_figure(fig, name):
    """Write straight into figures/, where the report reads them from."""
    d = os.path.join(REPO, 'figures')
    os.makedirs(d, exist_ok=True)
    stashed, sup = ([], '') if TITLES_IN_SAVED_FIGURES else _strip_titles(fig)
    _layout(fig)
    path = os.path.join(d, name if name.endswith('.png') else name + '.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', pad_inches=0.02)
    for ax, t in stashed:
        ax.set_title(t)
    if sup:
        fig.suptitle(sup)
    print('saved ->', path)
    return path
