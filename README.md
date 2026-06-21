# 1D Bistable Diaphragm Metafluid

Continuum and reduced-order modelling of transition waves in a fluid-coupled bistable diaphragm metafluid.

## Overview

A meta-fluid is a fluid whose macroscopic properties can be tuned by engineering its microstructure. This project studies a one-dimensional array of bistable diaphragms placed at regular intervals along a fluid-filled pipe. Each diaphragm sits in one of two stable states and is coupled to its neighbours through the pressure of the compressible fluid trapped in the segments between them. The discrete model tracks the displacement `u_n(t)` of each diaphragm `n`.

The key behaviour is the **transition wave**: a localised front that propagates through the bistable elements, irreversibly switching each one from one stable state to the other while releasing or absorbing energy. Characterising when this wave propagates and how fast is the foundational question for applications in energy harvesting and storage, refrigerant-free refrigeration, mechanical signal processing, and tunable acoustic devices.

Bistable diaphragms have previously been studied with magnetic and spring coupling, but not with fluid coupling. **Fluid coupling is the novel contribution here**: it is what turns the array into a metafluid. The approach is to start from the discrete lattice model, take its continuum limit, and — where that limit is valid — derive a reduced-order continuum model via asymptotics. This introductory project is restricted to 1D; the broader PhD extends it to 2D and 3D.

## Schematic

<!-- ===================================================================
     PASTE YOUR FIGURE HERE.

     Option A (recommended for GitHub): compile your TikZ to PNG/SVG,
     drop the file in figures/, and use the image line below.

     Option B: keep the LaTeX source in the repo for reference by
     pasting it into the code block underneath.
==================================================================== -->

![Schematic of the bistable diaphragm metafluid](figures/schematic.png)

*Bistable diaphragms (blue) placed at regular intervals along a fluid-filled pipe. Each diaphragm is in one of two stable states (curved left or right). The compressible fluid trapped between adjacent diaphragms exerts pressure `p_n` on both bounding diaphragms. A transition wave propagates to the right, switching each diaphragm from one stable state to the other.*

<details>
<summary>LaTeX / TikZ source for the figure</summary>

```latex
% PASTE YOUR LATEX CODE HERE

```

</details>

## Deliverables

This repository provides the following:

**D1 — Discrete lattice equations.** A documented derivation of the discrete lattice equations from first principles: force balance, the fluid equation of state, and the volume–displacement relation.

**D2 — Validated Python simulation.** A validated simulation of the diaphragm–fluid system, including space-time plots and an animation showing how the system evolves over time.

**D3 — Wave speed comparison.** A quantitative comparison of the wave speed predicted by Arrieta's continuum energy balance,

```
        ψ(u_hi) − ψ(u_lo)
v  =  ─────────────────────────
       γ ∫_{−∞}^{∞} (du/dξ)² dξ
```

against measured wave speeds across parameter space — at least 20 parameter combinations spanning the coupling strength `A`, the asymmetry of the bistable potential `δ`, and the damping `α` — with the ratio `v_pred / v_sim` properly tested for uncertainties.

**D4 — Continuum-validity diagnostic.** A diagnostic curve characterising where the continuum approximation holds, identifying a threshold above which the comparison to the formula above accurately predicts the measured wave speed.

**D5 — Kink-width formula.** An analytical kink-width formula derived from the reduced-order continuum PDE.

**Stretch goal.** If all of the above are met, extend the model to 2D.

## Reproducible result

The headline reproducible result is the measured travelling wave speed `v` at a fixed set of parameters in the continuum regime (approximately `A ≈ 1.0`, `δ ≈ 0.009`, `α ≈ 0.05`, on a lattice of `N ≈ 200` diaphragms with time step `Δt ≈ 10⁻⁴`). Uncertainty is quantified by running across lattice sizes (`N = 100, 200, 500`) and initial perturbations, reporting the standard deviation of `v`. The target is a wave speed reproducible to within a few percent across implementations.

## Repository structure

```
.
├── README.md
├── LICENSE
├── requirements.txt
├── diaphragm_metafluid.ipynb   # main simulation notebook (D2)
├── src/                        # simulation + analysis code (D2–D4)
├── docs/                       # analytical derivations (D1, D5)
├── figures/                    # schematic and generated plots
├── results/                    # wave-speed sweeps, space-time data
└── scripts/                    # HPC batch / parameter-sweep scripts
```

## Getting started

```bash
pip install -r requirements.txt
jupyter notebook diaphragm_metafluid.ipynb
```

## References

1. N. Nadkarni, A. F. Arrieta, C. Chong, D. M. Kochmann, C. Daraio. *Unidirectional transition waves in bistable lattices.* Physical Review Letters, 116(24):244501, 2016.
2. O. Peretz, E. Ben Abu, A. Zigelman, S. Givli, A. D. Gat. *A metafluid with multistable density and internal energy states.* Nature Communications, 13(1):1810, 2022.
3. O. Peretz, E. Ben Abu, A. Zigelman, S. Givli, A. D. Gat. *Multistable metafluid based energy harvesting and storage.* Advanced Materials, 35(35):2301483, 2023.
4. J. R. Raney, N. Nadkarni, C. Daraio, D. M. Kochmann, J. A. Lewis, K. Bertoldi. *Stable propagation of mechanical signals in soft media using stored elastic energy.* PNAS, 113(35):9722–9727, 2016.

## License

Released under the MIT License.
