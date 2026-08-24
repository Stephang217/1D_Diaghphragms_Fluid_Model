"""the phenomenon, for the head of Section 3.1.
One wave at the canonical point. Dimensionless throughout, unlike the old
figures/HeatMap.png whose time axis reads 'snapshot index x 500 x dt'."""
from _common import *

T, N = 1200.0, 120
r = run(KAPPA_C/THETA_C, THETA_C, PI, OM, N=N, T=T, save_every=500)

fig, ax = plt.subplots(figsize=(width(0.70), 2.1))
spacetime(ax, r['frames'], r['times'], r['u_lo'], r['u_hi'])
ax.set_title('A transition wave crossing the chain', fontsize=11)
save_figure(fig, 'spacetime')
print(f'spacetime: v={r["speed"]:.4f}   front {r["pos"][0]:.1f} -> {r["pos"][-1]:.1f} sites'
      f'   (N={N}, sponge from {N-10})')
