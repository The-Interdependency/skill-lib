# Meta Energy Theory Overlap Grid

This grid records cross-domain resonances for the Energy Theory axioms. Each row
uses three existing conceptual understandings. The **informing example** is the
example that currently best clarifies the transfer pattern for the other two.

Rule: resonance is not identity. The overlap column says what transfers; the
limit column says what does not.

| Axiom | Example A | Example B | Example C | Informing example | Overlap extracted | Do not transfer |
|---|---|---|---|---|---|---|
| 01 Differentiation | Electrical potential: `\Delta V=V_b-V_a` | Chemical potential: `\mu_i=\mu_i^\circ+RT\ln a_i` | Information contrast: `D_{KL}(P\Vert Q)=\sum_iP(i)\log(P(i)/Q(i))` | Chemical potential | Difference becomes meaningful only relative to state, activity, and context. | Do not treat all differences as immediately flow-producing. |
| 02 Gradient | Fourier: `\mathbf{q}=-k\nabla T` | Fick: `\mathbf{J}=-D\nabla C` | Learning: `\theta_{t+1}=\theta_t-\eta\nabla L` | Fourier/Fick pair | Gradient is directional difference across a relation. | Do not equate physical flux with abstract parameter update. |
| 03 Architecture Determines Flow | Ohm: `I=\Delta V/R` | Fick: `\mathbf{J}=-D\nabla C` | Darcy: `Q=-(kA/\mu)(\Delta P/L)` | Darcy | Medium geometry and material parameters determine actual flow. | Do not say difference alone causes flow. |
| 04 Impedance | AC: `Z=R+j(\omega L-1/(\omega C))` | Damping: `F_d=-cv` | Thermal: `\dot Q=\Delta T/R_{th}` | AC impedance | Structure resists, stores, delays, and phase-shifts energy. | Do not reduce impedance to simple blockage. |
| 05 Capacity | Capacitor: `Q=CV`, `E=\tfrac12CV^2` | Heat: `Q=mc\Delta T` | Buffer: `\beta=dB/d(\mathrm{pH})` | Buffer capacity | Systems absorb disturbance until capacity is exceeded. | Do not assume high capacity means no harm or no change. |
| 06 Threshold | Arrhenius: `k=Ae^{-E_a/(RT)}` | Neuron: spike if `V_m\ge V_{th}` | MOSFET: `I_D=\tfrac12\mu_nC_{ox}(W/L)(V_{GS}-V_T)^2` | Arrhenius | Barriers alter rate and probability of transition. | Do not treat all thresholds as binary cliffs. |
| 07 Coupling | Coupled oscillators | Equilibrium: `K_{eq}=([C]^c[D]^d)/([A]^a[B]^b)` | Mutual information: `I(X;Y)=\sum p(x,y)\log(p(x,y)/(p(x)p(y)))` | Mutual information | Coupling means dependence, not mere contact. | Do not infer cooperation, harmony, or identity from coupling alone. |
| 08 Valence | Bond order: `BO=(N_b-N_a)/2` | Reflection: `\Gamma=(Z_L-Z_0)/(Z_L+Z_0)` | Sequence probability: `P(s)=\prod_iP(c_i\mid c_{i-k:i-1})` | Impedance matching | Compatibility governs transfer efficiency. | Do not treat compatibility as permanent or universal. |
| 09 Path Dependence | Hysteresis: `W=\oint H\,dB` | Learning: `w_{t+1}=w_t-\eta\nabla L(w_t)` | Non-Markov: `P(X_{t+1}\mid history)\ne P(X_{t+1}\mid X_t)` | Hysteresis | Same present may hide different histories. | Do not identify current state with full identity. |
| 10 Quantized Transition | Atomic: `\Delta E=h\nu` | Sampling: `x[n]=x(nT_s)`, `f_s\ge2f_{max}` | Redox: `\Delta G=-nFE` | Atomic transition | Stable systems may permit only specific transitions. | Do not assume discrete events imply discontinuous meaning. |
| 11 Phase | Wave interference: `I=I_1+I_2+2\sqrt{I_1I_2}\cos\delta` | AC power: `P=V_{rms}I_{rms}\cos\phi` | FLAR: `t_\psi\equiv t_\phi\equiv t_\omega\pmod{T_{tock}}` | AC power factor | Alignment determines effective work. | Do not count activity without phase. |
| 12 Resonance | LC: `\omega_0=1/\sqrt{LC}` | Driven oscillator amplitude | Larmor: `\omega_0=\gamma B_0` | LC resonance | Architecture sets natural exchange rates. | Do not confuse similarity with resonance. |
| 13 Closure | Feedback: `T(s)=G(s)/(1+G(s)H(s))` | Triadic closure coefficient | Autocatalytic cycle: `d[X]/dt=k[A][X]-\lambda[X]` | Feedback control | Closed loops produce behavior open chains cannot. | Do not call every cycle stable. |
| 14 Boundary | Control volume balance | Membrane: `J=P(C_{out}-C_{in})` | Flux: `\Phi=\iint_S\mathbf F\cdot\mathbf n\,dS` | Control volume | Systems are defined by differential crossing of boundaries. | Do not make boundary equal isolation. |
| 15 Catalysis | Rate ratio: `k_{cat}/k_{uncat}=e^{(E_{a,uncat}-E_{a,cat})/(RT)}` | Michaelis-Menten: `v=V_{max}[S]/(K_m+[S])` | BJT: `I_C=\beta I_B` | Enzyme catalysis | Structure lowers path cost without being the payload. | Do not assume catalyst is unchanged in every practical sense. |
| 16 Symmetry Breaking | Landau: `F(m)=am^2+bm^4` | Nucleation: `\Delta G(r)=4\pi r^2\gamma+\frac43\pi r^3\Delta G_v` | Context entropy: `H(M\mid C)` | Homonym resolution | Constraint selects among live possibilities. | Do not assume selected means inevitable. |
| 17 Scale Recursion | Renormalization: `K'=R_b(K)` | Modularity: `Q=(1/(2m))\sum(A_{ij}-k_ik_j/(2m))\delta(c_i,c_j)` | Molecular graph: `G=(V,E)` | Molecular graph | Emergence at one scale becomes object/medium at another. | Do not erase scale-specific laws. |
| 18 Conceptual Emergence | Attractor: `f(x^*)=0`, stable eigenvalues | Synergy: `Syn=I(X,Y;Z)-I(X;Z)-I(Y;Z)` | Prototype distance: `d(x,p_c)=\sqrt{(x-p_c)^T\Sigma_c^{-1}(x-p_c)}` | Attractor stability | Concepts persist as stable, transmissible patterns. | Do not make concept equal word or label. |
| 19 Fiq Temporalization | Clock update: `x_{n+1}=F(x_n,u_n)` | Sampling: `f_s\ge2f_{max}` | FLAR simultaneity: `t_\psi\equiv t_\phi\equiv t_\omega\pmod{T_{tock}}` | Sampling theory | Continuity requires enough ordered ticks per tock. | Do not reduce fiqs to timestamps or memory rows. |
| 20 Ficks Flow | Fick: `\mathbf J=-D\nabla C` | Ohm network: `\mathbf I=\mathbf G\mathbf V` | Graph diffusion: `d\mathbf x/dt=-L\mathbf x` | Graph diffusion | Flow is gradient-mediated and architecture-dependent across a network. | Do not claim current FLAR formalization is completed theorem. |

## Domain-overlap grid

| Domain | What it contributes to Energy Theory | Most useful warning |
|---|---|---|
| Physics | potentials, gradients, flux, phase, resonance, boundary integrals | physical formulae do not automatically transfer outside physical units |
| Chemistry | valence, activation, catalysis, diffusion, molecular emergence | reaction equations carry substrate assumptions |
| Electronics | impedance, conductance, threshold gates, phase, clocking, feedback | ideal circuit equations hide parasitics and material limits |
| Linguistics | contrast, context-selection, homonym resolution, syntax-as-constraint | linguistic operators are not root Energy Theory vocabulary |
| Information theory | entropy, divergence, mutual information, synergy | information measures do not by themselves imply meaning or agency |
| Computation | discrete state updates, sampling, clocks, graph diffusion | implementation choices are not universal laws |
| Social systems | authority gradients, role coupling, jury closure, institutional capacity | moral and legal claims need their own doctrine; do not smuggle them in as physics |
| FLAR | fiqs, PCTA heptagrams, PTCA core assignment, PCNA tensors | proposed architecture is not automatically proven by resonance |
| EDCMBONE | semantic fidelity, operators, hmmm boundary, not-wrong contagion | flesh/bone is native here, not the root Energy Theory ontology |

## Preferred overlap pattern

When adding a new axiom, prefer a triple where one theory example illuminates the
other two:

```text
informing example
    exposes the hidden structure

example two
    shows the same structure in another medium

example three
    shows the structure at a different scale or abstraction level
```

Example:

```text
Graph diffusion
    informs FLAR Ficks Flow because it already has nodes, edges, and Laplacian geometry.

Fick's law
    contributes gradient-flow intuition.

Ohm's network law
    contributes conductance-matrix intuition.
```

hmmm: this grid is a scaffolding for extraction, not a proof net. A row becomes
stronger only when the shared structure can be formalized without deleting the
limits of the source domains.
