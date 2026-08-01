# 1D Bistable Diaphragm Metafluid

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Jupyter](https://img.shields.io/badge/Jupyter-notebook-orange.svg)

Continuum and reduced-order modelling of transition waves in a fluid-coupled bistable diaphragm metafluid.

## Overview

A meta-fluid is a fluid whose macroscopic properties can be tuned by engineering its microstructure. This project studies a one-dimensional array of bistable diaphragms placed at regular intervals along a fluid-filled pipe. Each diaphragm sits in one of two stable states and is coupled to its neighbours through the pressure of the compressible fluid trapped in the segments between them. The discrete model tracks the displacement `u_n(t)` of each diaphragm `n`.

The key behaviour is the transition wave: a localised front that propagates through the bistable elements, irreversibly switching each one from one stable state to the other while releasing or absorbing energy. Characterising when this wave propagates and how fast is the foundational question for applications in energy harvesting and storage, refrigerant-free refrigeration, mechanical signal processing, and tunable acoustic devices.

Bistable diaphragms have previously been studied with magnetic and spring coupling, but not with fluid coupling. Fluid coupling is the novel contribution here: it is what turns the array into a metafluid. The approach is to start from the discrete lattice model, take its continuum limit, and — where that limit is valid — derive a reduced-order continuum model via asymptotics. This introductory project is restricted to 1D; the broader PhD extends it to 2D and 3D.

## Schematic

![Schematic of the bistable diaphragm metafluid](figures/figure.png)

*Bistable diaphragms (blue) placed at regular intervals along a fluid-filled pipe. Each diaphragm is in one of two stable states (curved left or right). The compressible fluid trapped between adjacent diaphragms exerts pressure `p_n` on both bounding diaphragms. A transition wave propagates to the right, switching each diaphragm from one stable state to the other.*

<details>
<summary>LaTeX / TikZ source for the figure</summary>

```latex
\documentclass[border=2pt]{standalone}
\usepackage{graphicx} % Required for inserting images
\usepackage{tikz}
\usepackage{xcolor}
\definecolor{wongblue}{RGB}{0, 114, 178}
\definecolor{wongorange}{RGB}{230, 159, 0}
\definecolor{wonggrey}{RGB}{100, 100, 100}

\begin{document}

\begin{tikzpicture}[scale=1]
    % pipe walls
    \draw[thick] (0, 1.5) -- (12, 1.5);
    \draw[thick] (0, -1.5) -- (12, -1.5);
    
    % diaphragms - some bent right (behind wave, snapped), some bent left (ahead of wave)
    % "snapped" diaphragms behind the wave: bent right (curve opens left)
    \draw[thick, wongblue] (1, -1.5) .. controls (1.5, -0.5) and (1.5, 0.5) .. (1, 1.5);
    \draw[thick, wongblue] (3, -1.5) .. controls (3.5, -0.5) and (3.5, 0.5) .. (3, 1.5);
    \draw[thick, wongblue] (5, -1.5) .. controls (5.5, -0.5) and (5.5, 0.5) .. (5, 1.5);
    
    % "unsnapped" diaphragms ahead of the wave: bent left (curve opens right)
    \draw[thick, wongblue] (7, -1.5) .. controls (6.5, -0.5) and (6.5, 0.5) .. (7, 1.5);
    \draw[thick, wongblue] (9, -1.5) .. controls (8.5, -0.5) and (8.5, 0.5) .. (9, 1.5);
    \draw[thick, wongblue] (11, -1.5) .. controls (10.5, -0.5) and (10.5, 0.5) .. (11, 1.5);
    
    % diaphragm labels (under)
    \node at (1, -1.9) {\small $n-2$};
    \node at (3, -1.9) {\small $n-1$};
    \node at (5, -1.9) {\small $n$};
    \node at (7, -1.9) {\small $n+1$};
    \node at (9, -1.9) {\small $n+2$};
    \node at (11, -1.9) {\small $n+3$};
    
    % pressure labels with arrows pointing into the segments
    \node at (2, 0) {$p_{n-1}$};
    \draw[->, thick, wonggrey] (1.7, 0.3) -- (1.3, 0.3);
    \draw[->, thick, wonggrey] (2.3, 0.3) -- (2.7, 0.3);
    
    \node at (4, 0) {$p_n$};
    \draw[->, thick, wonggrey] (3.7, 0.3) -- (3.3, 0.3);
    \draw[->, thick, wonggrey] (4.3, 0.3) -- (4.7, 0.3);
    
    \node at (6, 0) {$p_{n+1}$};
    \draw[->, thick, wonggrey] (5.7, 0.3) -- (5.3, 0.3);
    \draw[->, thick, wonggrey] (6.3, 0.3) -- (6.7, 0.3);
    
    \node at (8, 0) {$p_{n+2}$};
    \draw[->, thick, wonggrey] (7.7, 0.3) -- (7.3, 0.3);
    \draw[->, thick, wonggrey] (8.3, 0.3) -- (8.7, 0.3);
    
    \node at (10, 0) {$p_{n+3}$};
    \draw[->, thick, wonggrey] (9.7, 0.3) -- (9.3, 0.3);
    \draw[->, thick, wonggrey] (10.3, 0.3) -- (10.7, 0.3);
    
    % wave direction arrow above the pipe
    \draw[->, very thick, wongorange] (4, 2.2) -- (8, 2.2);
    \node at (6, 2.6) {transition wave};
    
\end{tikzpicture}

\end{document}


```

</details>

## Simulation

The transition wave propagating through 120 diaphragms ($N=120, A=1, \delta=0.009, \alpha=0.05, \Delta t=10^{-4}$):

![Transition wave animation](figures/wave_animation.gif)

**Effect of damping** — underdamped ($\alpha=0.01$, left) vs overdamped ($\alpha=0.30$, right). At low damping, diaphragms ring down after snapping, creating an oscillatory wake. At high damping, each snap is clean and the front is sharp:

![Damping comparison](figures/wave_comparison.gif)

## Key results

- **Four-group reduction.** The dynamics depend on exactly four dimensionless numbers $(\eta, \theta, \Pi, \Omega)$. Two physical systems built with deliberately unlike dimensional parameters but matched groups produce trajectories agreeing to $10^{-14}$ — integrator round-off, not a modelling residual.
- **Where the speed formula works.** The controlling quantity is the front width in lattice spacings, $w = \sqrt{2\eta\theta}$. The energy-balance prediction is accurate to $2.8\%$ once the front spans three sites and stays within $10\%$ down to two, degrading to $66\%$ at one site where the travelling profile it assumes is no longer resolved.
- **Pinning is a lattice effect.** Weakening the *drive* never stalls the wave — speed falls in exact proportion to $\delta$ over two decades with no threshold. Weakening the *coupling* does: below $\eta\theta \approx 0.3$ the front freezes, verified stationary to machine precision over a twenty-fold span of run time. The threshold is not a fixed width but follows $w_c = 0.085 - 0.303\ln\Pi$ ($R^2 = 0.96$), the signature of a barrier exponential in width competing against the energy released per snap.
- **The fluid fingerprint.** Waves that compress the gas pockets run faster than their mirror image that stretches them — $2.6\%$ at $\theta = 0.1$ rising to $10.8\%$ at $\theta = 0.4$, linear in $\theta$. A spring chain gives identically zero, so this is the signature of the gas coupling specifically.
- **Reproducible result.** $v = 0.2206 \pm 0.0001$ (numerical) $\pm 0.0215$ (parametric) at the protocol point. Per-diaphragm disorder self-averages and contributes an order of magnitude less than a uniform batch offset.

> **Superseded results.** Earlier versions of this README reported that post-snap ringing accounts for ~34% of dissipation and is the reason the formula overpredicts at low damping, and that volume collapse above $A \approx 1.8$ stalls the wave. Both were later overturned by better-sized tests. In steady state the ringing wake carries only a few percent of the dissipation, and the low-damping overprediction survives long after the ringing has fully decayed — it is a genuine steady-state effect (neglected front inertia and lattice radiation), not a measurement artefact. The $A$ limit did not reproduce once the damping and initial conditions were corrected.

### Wave-speed sweep (selected results, 45 combinations total)

| $A$ | $\delta$ | $\alpha$ | $v_{sim}$ | $v_{pred}$ | ratio |
|---|---|---|---|---|---|
| 1.0 | 0.001 | 0.10 | 0.2208 | 0.2233 | **1.01** |
| 1.0 | 0.001 | 0.05 | 0.4085 | 0.4199 | **1.03** |
| 1.0 | 0.003 | 0.10 | 0.5533 | 0.5653 | **1.02** |
| 1.0 | 0.009 | 0.05 | 0.7972 | 1.4480 | 1.82 |
| 0.5 | 0.009 | 0.02 | 0.4655 | 1.8804 | 4.04 |
| 2.0 | 0.009 | 0.02 | 0.3052 | 9.4502 | 30.97 |

Full results in [`results/wave_speed_sweep.csv`](results/wave_speed_sweep.csv).

## Deliverables

This repository provides the following:

**D1 — Discrete lattice equations.** A documented derivation of the discrete lattice equations from first principles: force balance, the fluid equation of state, and the volume–displacement relation.

**D2 — Validated Python simulation.** A validated simulation of the diaphragm–fluid system, including space-time plots and an animation showing how the system evolves over time.

**D3 — Wave speed comparison.** A quantitative comparison of the wave speed predicted by Arrieta's continuum energy balance,

$$
\begin{equation}
v = \frac{\psi(u_{\text{hi}}) - \psi(u_{\text{lo}})}{\gamma \int_{-\infty}^{\infty} \left(\frac{du}{d\xi}\right)^2 d\xi}
\end{equation}
$$

against measured wave speeds across parameter space — at least 20 parameter combinations spanning the coupling strength `A`, the asymmetry of the bistable potential `δ`, and the damping `α` — with the ratio `v_pred / v_sim` properly tested for uncertainties.

**D4 — Continuum-validity diagnostic.** A diagnostic curve characterising where the continuum approximation holds, identifying a threshold above which the comparison to the formula above accurately predicts the measured wave speed.

**D5 — Kink-width formula.** An analytical kink-width formula derived from the reduced-order continuum PDE.

**Stretch goal.** If all of the above are met, extend the model to 2D.

## Repository structure

```
.
├── README.md
├── LICENSE
├── requirements.txt
├── diaphragm_metafluid.ipynb      # dimensional model: validation, sweeps, dissipation
├── dimensionless_model.ipynb      # four groups: validity map, pinning, gas-vs-spring
├── uq_reproducible_result.ipynb   # reproducible result, GP surrogate, Sobol, disorder
├── src/                           # shared simulator (run_sim) used by the scripts
├── scripts/                       # ensembles + SCRTP batch wrapper
├── paper/                         # report drafts, appendices, bibliography
├── docs/                          # analytical derivations
├── figures/                       # schematic, plots and animations
└── results/                       # cached sweep outputs (CSV, with metadata headers)
```

## Getting started

```bash
pip install -r requirements.txt
jupyter notebook diaphragm_metafluid.ipynb
```

Every expensive sweep is cached in `results/`, so the notebooks run top to bottom in
minutes without recomputing them; set `FORCE_RERUN = True` in a notebook's setup cell
to regenerate instead of load. The two slowest (`pinning_boundary.csv`, ~70 min, and
the low-damping window test) ship pre-computed with the scripts that generate them.
`paper/appendix_c_protocol.tex` gives the exact command to reproduce the headline wave
speed and the reference value to check it against.

## References

1. N. Nadkarni, A. F. Arrieta, C. Chong, D. M. Kochmann, C. Daraio. *Unidirectional transition waves in bistable lattices.* Physical Review Letters, 116(24):244501, 2016.
2. O. Peretz, E. Ben Abu, A. Zigelman, S. Givli, A. D. Gat. *A metafluid with multistable density and internal energy states.* Nature Communications, 13(1):1810, 2022.
3. O. Peretz, E. Ben Abu, A. Zigelman, S. Givli, A. D. Gat. *Multistable metafluid based energy harvesting and storage.* Advanced Materials, 35(35):2301483, 2023.
4. J. R. Raney, N. Nadkarni, C. Daraio, D. M. Kochmann, J. A. Lewis, K. Bertoldi. *Stable propagation of mechanical signals in soft media using stored elastic energy.* PNAS, 113(35):9722–9727, 2016.

## License

Released under the MIT License.
