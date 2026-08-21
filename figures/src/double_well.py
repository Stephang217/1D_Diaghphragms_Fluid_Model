"""the double well the whole paper rests on.

Changes from v1:
  - "barrier" -> "unstable equilibrium". The hump between the wells is NOT the
    Peierls-Nabarro barrier of Section 3.2, and a reader who meets "barrier"
    here will carry the wrong picture into that section.
  - Delta psi is now a bracket between two horizontal guide lines, so it reads
    as a difference between levels rather than a distance at one displacement.
  - Wong colourblind-safe palette, matching the colours already defined in the
    LaTeX preamble for the schematic.
"""
from _common import *

# the two wells carry the two state colours of the schematic and the
# space-time maps, so the same physical state is the same ink throughout
WBLUE, WGREEN, WVERM, WGREY = C.ref, C.state_lo, C.state_hi, C.ref

u = np.linspace(-1.42, 1.42, 800)
psi = lambda x, P: x**4/4 - x**2/2 + P*x
lo, mid, hi = wells(PI)
p_lo, p_hi, p_mid = psi(lo, PI), psi(hi, PI), psi(mid, PI)
XB = 1.30                                    # where the bracket sits

fig, ax = plt.subplots(figsize=(width(0.72), 3.3))
ax.plot(u, psi(u, 0.0), color='0.75', lw=1.2, ls=':', zorder=1,
        label=r'$\Pi = 0$: wells equal')
ax.plot(u, psi(u, PI), color=WBLUE, lw=2.3, zorder=2,
        label=rf'$\Pi = {PI}$: one well lower')

# guide lines out to the bracket, so the gap reads as a difference of levels
for y in (p_lo, p_hi):
    ax.plot([lo if y == p_lo else hi, XB], [y, y], color=WGREY, lw=0.8,
            ls='--', alpha=0.7, zorder=1)
ax.annotate('', xy=(XB, p_hi), xytext=(XB, p_lo),
            arrowprops=dict(arrowstyle='<->', color=C.ref, lw=1.3))
ax.text(XB - 0.07, 0.5*(p_lo + p_hi), r'$\Delta\tilde\psi \simeq 2\Pi$',
        fontsize=11, va='center', ha='right',
        bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))

ax.plot(lo,  p_lo,  'o', color=WGREEN, ms=10, zorder=4)
ax.plot(hi,  p_hi,  'o', color=WVERM,  ms=10, zorder=4)
ax.plot(mid, p_mid, 'o', color=WGREY,  ms=7,  zorder=4)

ax.annotate('low-energy state\n(the wave leaves this behind)',
            xy=(lo, p_lo), xytext=(lo + 0.62, -0.452),
            ha='center', va='bottom', fontsize=9, color=WGREEN,
            arrowprops=dict(arrowstyle='-', color=WGREEN, lw=0.8, alpha=0.7))
ax.annotate('high-energy state\n(the wave arrives here)',
            xy=(hi, p_hi), xytext=(0.46, 0.075),
            ha='center', va='bottom', fontsize=9, color=WVERM,
            arrowprops=dict(arrowstyle='-', color=WVERM, lw=0.8, alpha=0.7))
ax.annotate('unstable equilibrium', xy=(mid, p_mid), xytext=(mid - 0.52, p_mid + 0.062),
            ha='center', fontsize=9, color=WGREY,
            arrowprops=dict(arrowstyle='-', color=WGREY, lw=0.8, alpha=0.7))

ax.set_xlim(-1.42, 1.42); ax.set_ylim(-0.47, 0.20)
ax.set_xlabel(r'displacement  $\tilde u$', fontsize=12)
ax.set_ylabel(r'on-site potential  $\tilde\psi(\tilde u)$', fontsize=12)
ax.set_title(r'Each diaphragm sits in a double well tilted by $\Pi$', fontsize=11)
ax.grid(True, alpha=0.25); ax.legend(fontsize=9, loc='upper left', framealpha=0.9)
save_figure(fig, 'double_well')
print(f'double_well: wells {lo:.4f} / {hi:.4f}, unstable at {mid:.4f}; '
      f'depth difference {p_hi-p_lo:.5f}  vs  2*Pi = {2*PI:.3f}')
