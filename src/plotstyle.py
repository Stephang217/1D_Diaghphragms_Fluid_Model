r"""House plotting style for the report figures.

One import fixes the palette, the font sizes and the figure geometry, so every
figure in the report prints at the same scale and in the same colours as the
Figure 1 schematic.

    from plotstyle import use, C, save, one_panel, two_panel
    use()
    fig, ax = plt.subplots(figsize=one_panel())
    ax.plot(t, v, color=C.data, label='simulation')
    save(fig, 'my_figure')

Colours are Wong's colourblind-safe set (Wong, Nat. Methods 8, 441 (2011)) --
the same three the TikZ schematic defines as wongblue / wongorange / wonggrey,
extended with three further Wong colours for the figures that need more than
three categories. Nothing outside that set is used anywhere.

Geometry: every figure is authored at the report's \linewidth and included at
width=\linewidth, so LaTeX never rescales it and a 10pt axis label really is
10pt on the page. Set LINEWIDTH_IN below to whatever `\the\linewidth` prints
in the Overleaf log if it is not 6.3in.
"""

import os
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.colors import LinearSegmentedColormap

# ── Palette ─────────────────────────────────────────────────────────────────
# The three from the schematic, plus three more of Wong's for extra categories.
WONG = {
    'blue':   '#0072B2',   # RGB 0, 114, 178   -- wongblue   (schematic)
    'orange': '#E69F00',   # RGB 230, 159, 0   -- wongorange (schematic)
    'grey':   '#646464',   # RGB 100, 100, 100 -- wonggrey   (schematic)
    'green':  '#009E73',   # RGB 0, 158, 115
    'purple': '#CC79A7',   # RGB 204, 121, 167
    'vermil': '#D55E00',   # RGB 213, 94, 0
}


class C:
    """Colours by role, not by name. Change the mapping here, not in the figures."""

    data   = WONG['blue']      # anything measured from a simulation
    theory = WONG['orange']    # anything predicted: tanh, closed form, energy balance
    ref    = WONG['grey']      # reference lines, guides, y = 1, zero lines
    band   = WONG['grey']      # tolerance / acceptance shading (was green)
    fail   = WONG['vermil']    # pinned, stalled, collapsed -- used sparingly
    third  = WONG['green']     # third category when one is genuinely needed
    fourth = WONG['purple']    # fourth

    # The two stable states of the diaphragm, matching the schematic's two
    # states. Everything that shows a front -- the space-time maps, the double
    # well, the tanh overlay -- reads in these two colours.
    state_lo = WONG['blue']
    state_hi = WONG['orange']


CYCLE = [C.data, C.theory, C.third, C.fourth, C.ref]

# Diverging map for the space-time heatmaps, built from the two state colours
# so the schematic and every result plot show the same object in the same ink.
DIVERGING = LinearSegmentedColormap.from_list(
    'wong_div', [C.state_lo, '#F4F1EA', C.state_hi], N=256)
try:
    mpl.colormaps.register(DIVERGING)
except (ValueError, AttributeError):
    pass                                   # already registered, or old mpl

# ── Geometry ────────────────────────────────────────────────────────────────
# The report is a4paper with geometry{margin=2.5cm}, so
#     \linewidth = 210mm - 2*25mm = 160mm = 6.299in.
# Author every figure at the width it is included at, so LaTeX never rescales
# and a 9pt label really is 9pt on the page.
LINEWIDTH_IN = 6.30
DPI = 200

# Saved figures carry no axes title: in the report the LaTeX \caption is the
# title, and duplicating it inside the PNG says the same thing twice in two
# different fonts. Titles are still drawn in the notebook, where there is no
# caption -- save() strips them for the file and puts them straight back.
TITLES_IN_SAVED_FIGURES = False
FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')


def width(frac=1.0):
    r"""Inches for a figure included at `frac` * \linewidth."""
    return frac * LINEWIDTH_IN


# The two slots the document should settle on. Heights keep each axes near 4:3.
def full(h=3.6):
    r"""Full width: \includegraphics[width=\linewidth]."""
    return (width(1.00), h)


def half(h=2.5):
    r"""Half width, for the side-by-side minipage pairs (0.48\textwidth)."""
    return (width(0.48), h)


def two_panel(h=2.9):
    """Full width, two axes side by side under a single caption."""
    return (width(1.00), h)


def stacked(h=5.0):
    """Full width, two axes one above the other."""
    return (width(1.00), h)


# ── Style ───────────────────────────────────────────────────────────────────
def use(base=9.0, serif=True, titles_in_saved_figures=False):
    """Apply the house style. Call once, at the top of a notebook or script.

    `base` is the tick-label size in points; labels and titles sit one point
    above it. At LINEWIDTH_IN with no LaTeX rescaling these are the sizes that
    reach the page, so base=9 against 11pt body text is about right.

    Set titles_in_saved_figures=True to keep axes titles in the PNG, for a
    figure that is not going into the document under a caption.
    """
    global TITLES_IN_SAVED_FIGURES
    TITLES_IN_SAVED_FIGURES = titles_in_saved_figures
    plt.rcParams.update({
        'figure.figsize':    full(),
        'figure.dpi':        110,
        'savefig.dpi':       DPI,
        'savefig.bbox':      'tight',
        'savefig.pad_inches': 0.02,

        # TrueType, not matplotlib's default Type 3. Type 3 renders badly in
        # some viewers and several journals refuse it; 42 also keeps the text
        # in the vector output selectable and searchable.
        'pdf.fonttype':      42,
        'ps.fonttype':       42,

        'font.size':         base,
        'axes.labelsize':    base + 1,
        'axes.titlesize':    base + 1,
        'xtick.labelsize':   base - 0.5,
        'ytick.labelsize':   base - 0.5,
        'legend.fontsize':   base - 0.5,
        'figure.titlesize':  base + 1,

        # STIX is matplotlib's built-in Times-alike and pairs with STIX maths.
        # For true Computer Modern set text.usetex=True (needs a LaTeX install).
        'font.family':       'STIXGeneral' if serif else 'DejaVu Sans',
        'mathtext.fontset':  'stix' if serif else 'dejavusans',

        'axes.prop_cycle':   cycler(color=CYCLE),
        'axes.grid':         True,
        'axes.axisbelow':    True,
        'axes.linewidth':    0.8,
        'axes.spines.top':   False,
        'axes.spines.right': False,
        'grid.alpha':        0.25,
        'grid.linewidth':    0.6,

        'lines.linewidth':   1.6,
        'lines.markersize':  4.5,
        'legend.frameon':    False,
        'legend.handlelength': 1.8,
        'legend.borderaxespad': 0.4,

        'image.cmap':        'wong_div',
    })


# ── Helpers ─────────────────────────────────────────────────────────────────
def _layout(fig):
    """tight_layout, quietly skipped for figures it cannot handle (shared colorbars)."""
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='.*not compatible with tight_layout.*')
        fig.tight_layout(pad=0.4)


def _strip_titles(fig):
    """Remove axes titles and suptitle, returning what is needed to restore them."""
    stashed = [(ax, ax.get_title()) for ax in fig.axes if ax.get_title()]
    for ax, _ in stashed:
        ax.set_title('')
    sup = fig.get_suptitle() if hasattr(fig, 'get_suptitle') else ''
    if sup:
        fig.suptitle('')
    return stashed, sup


def save(fig, name, dpi=DPI, titles=None):
    """Lay out, save into figures/, return the path.

    Axes titles are dropped from the file unless `titles` (or the module
    default) says otherwise, then restored, so the notebook still shows them.
    """
    keep = TITLES_IN_SAVED_FIGURES if titles is None else titles
    stashed, sup = ([], '') if keep else _strip_titles(fig)
    _layout(fig)
    stem = name[:-4] if name.endswith('.png') else name
    path = os.path.normpath(os.path.join(FIG_DIR, stem + '.png'))
    # Both formats, deliberately. The PDF is what the report includes -- vector,
    # so the axis text and thin lines stay sharp at any zoom, and \includegraphics
    # picks it over the PNG without being told. The PNG is what GitHub renders in
    # the README, which cannot display a PDF.
    for ext in ('.png', '.pdf'):
        fig.savefig(os.path.normpath(os.path.join(FIG_DIR, stem + ext)),
                    dpi=dpi, bbox_inches='tight', pad_inches=0.02)
    if stashed or sup:
        for ax, t in stashed:
            ax.set_title(t)
        if sup:
            fig.suptitle(sup)
        _layout(fig)                 # re-fit so the inline display is not cramped
    return path


def label_line(ax, line, text, frac=1.0, dx=5, dy=0, **kw):
    """Write `text` at the end of `line`, in the line's own colour.

    The replacement for a two-entry legend: no box, no reserved corner. Give
    the axes room first (ax.margins(x=0.18) or an explicit set_xlim), since the
    text sits outside the data range and tight_layout will not make space for it.
    """
    xd, yd = line.get_xdata(), line.get_ydata()
    i = min(int(round((len(xd) - 1) * frac)), len(xd) - 1)
    ax.annotate(text, (xd[i], yd[i]), textcoords='offset points',
                xytext=(dx, dy), color=line.get_color(),
                ha='left' if dx >= 0 else 'right', va='center',
                fontsize=plt.rcParams['legend.fontsize'], **kw)


def spacetime(ax, field, times, u_lo, u_hi, cbar=True, label=r'displacement  $\tilde u_n$'):
    """Site index up the y-axis, time along x, in the two state colours."""
    im = ax.imshow(field.T, aspect='auto', origin='lower', cmap='wong_div',
                   vmin=u_lo, vmax=u_hi,
                   extent=[times[0], times[-1], 0, field.shape[1]])
    ax.set_xlabel(r'time  $\tilde t$')
    ax.set_ylabel(r'diaphragm  $n$')
    ax.grid(False)
    if cbar:
        cb = plt.colorbar(im, ax=ax, pad=0.02)
        cb.set_label(label)
        cb.outline.set_linewidth(0.6)
    return im
