#!/usr/bin/env python3
"""Renders the house style so it can be eyeballed before the figures adopt it.

    python3 scripts/plotstyle_demo.py      -> figures/style_demo.png

Four panels: the palette by role, a two-curve plot labelled directly instead of
with a legend box, a four-curve plot using the cycle, and the space-time map in
the two state colours.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from plotstyle import use, C, WONG, save, width, label_line, spacetime  # noqa: E402
from dimless import run                                                        # noqa: E402

use()

fig, axes = plt.subplots(2, 2, figsize=(width(1.0), 5.4))
(ax_sw, ax_two), (ax_cyc, ax_st) = axes

# ── 1. the palette, by role ─────────────────────────────────────────────────
roles = [('data', C.data), ('theory', C.theory), ('ref / band', C.ref),
         ('fail', C.fail), ('third', C.third), ('fourth', C.fourth)]
for i, (name, col) in enumerate(roles):
    ax_sw.add_patch(plt.Rectangle((0, -i), 1.0, 0.72, color=col))
    ax_sw.text(1.15, -i + 0.36, f'{name}   {col}', va='center', fontsize=8)
ax_sw.set_xlim(-0.1, 4.2); ax_sw.set_ylim(-len(roles) + 0.2, 1.0)
ax_sw.axis('off')
ax_sw.set_title('Palette by role', loc='left')

# ── 2. two curves, labelled directly -- no legend box ───────────────────────
x = np.linspace(0, 10, 200)
l1, = ax_two.plot(x, 1 - np.exp(-x / 2.5), color=C.data)
l2, = ax_two.plot(x, 1.18 * (1 - np.exp(-x / 1.4)), color=C.theory)
ax_two.axhline(1.0, color=C.ref, lw=0.8, ls='--')
ax_two.axhspan(0.9, 1.1, color=C.band, alpha=0.13, lw=0)
ax_two.set_xlim(0, 13.2)
label_line(ax_two, l1, 'simulation')
label_line(ax_two, l2, 'prediction')
ax_two.set_xlabel(r'time  $\tilde t$'); ax_two.set_ylabel(r'$v/v_{\rm pred}$')
ax_two.set_title('Direct labels, no box', loc='left')

# ── 3. the cycle, for a sweep with several lines ────────────────────────────
for k, om in enumerate([1, 3, 10, 30]):
    ax_cyc.plot(x, np.tanh(x / (0.6 + 0.35 * k)), label=rf'$\Omega = {om}$')
ax_cyc.set_xlabel(r'$\xi$'); ax_cyc.set_ylabel(r'$U$')
ax_cyc.legend(loc='lower right')
ax_cyc.set_title('Default cycle', loc='left')

# ── 4. space-time, in the two state colours ─────────────────────────────────
r = run(80.0, 0.1, 0.115, 10.0, N=120, T=1200.0, save_every=500)
spacetime(ax_st, r['frames'], r['times'], r['u_lo'], r['u_hi'])
ax_st.set_title('Space-time, state colours', loc='left')

print('saved ->', save(fig, 'style_demo'))
