# Figure sources

Everything here produces a figure in `figures/` that no notebook generates.

| source | output |
|---|---|
| `schematic.tex` | `../figure.png` — the Figure 1 schematic (TikZ, also pasted inline in the report) |
| `double_well.py` | `../double_well.png` — the on-site potential, report Figure 2 |
| `spacetime.py` | `../spacetime.png` — the space-time heatmap, report Figure 3 |

The Python scripts share `_common.py`, which applies the house style from
`src/plotstyle.py` and writes straight into `figures/`. Run them from anywhere:

    python3 figures/src/double_well.py
