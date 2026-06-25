# Meta Energy Theory Overlap Grid

This grid records cross-domain resonances for root axioms, derived law families,
and FLAR postulates. It no longer treats every useful pattern as an axiom.

Rule: resonance is not identity. The overlap column says what transfers; the
limit column says what does not.

| Status | Entry | Example A | Example B | Example C | Informing example | Overlap extracted | Do not transfer |
|---|---|---|---|---|---|---|---|
| Root axiom | Distinction | Electrical potential: `\Delta V=V_b-V_a` | Chemical potential: `\mu_i=\mu_i^\circ+RT\ln a_i` | Information contrast: `D_{KL}(P\Vert Q)=\sum_iP(i)\log(P(i)/Q(i))` | Chemical potential | Difference becomes meaningful only relative to state, activity, and context. | Do not treat all differences as immediately flow-producing. |
| Root axiom | Relation | Inequality: `a<b` | Orthogonality: `u\cdot v=0` | Boundary: `\partial\Omega` relates inside to outside by separation | Orthogonality | Relation can compare, separate, oppose, constrain, or exclude without permitting traversal. | Do not infer movement, availability, or flow from relation alone. |
| Root axiom | Coupled Emergence | Bond order: `BO=(N_b-N_a)/2` | Mutual information: `I(X;Y)=\sum p(x,y)\log(p(x,y)/(p(x)p(y)))` | Feedback: `T(s)=G(s)/(1+G(s)H(s))` | Mutual information | Relation can carry properties not located in isolated terms. | Do not infer harmony, identity, or goodness from coupling. |
| Root axiom | Ordered Transformation | Non-Markov: `P(X_{t+1}\mid history)\ne P(X_{t+1}\mid X_t)` | AC phase power: `P=V_{rms}I_{rms}\cos\phi` | FLAR simultaneity: `t_\psi\equiv t_\phi\equiv t_\omega\pmod{T_{tock}}` | AC phase | Order and timing can change effective work/process identity. | Do not treat unordered sets of events as equivalent to processes. |
| Derived law-family | Traversability / Availability | Graph adjacency: `A_{ij}\in\{0,1\}` | Membrane permeability: `J=P(C_{out}-C_{in})` | Conductive path: `I=\Delta V/R` | Graph adjacency | Flow requires a relation that is traversable under current constraints. | Do not confuse structural availability with social permission. |
| Derived law-family | Gradient Flow | Fourier: `\mathbf{q}=-k\nabla T` | Fick: `\mathbf{J}=-D\nabla C` | Learning: `\theta_{t+1}=\theta_t-\eta\nabla L` | Fourier/Fick pair | Gradient is directional difference across a traversable relation. | Do not equate physical flux with abstract parameter update. |
| Derived law-family | Architecture-Determined Flow | Ohm: `I=\Delta V/R` | Fick: `\mathbf{J}=-D\nabla C` | Darcy: `Q=-(kA/\mu)(\Delta P/L)` | Darcy | Medium geometry and material parameters determine actual flow. | Do not say difference alone causes flow. |
| Derived law-family | Impedance | AC: `Z=R+j(\omega L-1/(\omega C))` | Damping: `F_d=-cv` | Thermal: `\dot Q=\Delta T/R_{th}` | AC impedance | Structure resists, stores, delays, and phase-shifts energy. | Do not reduce impedance to simple blockage. |
| Derived law-family | Capacity | Capacitor: `Q=CV`, `E=\tfrac12CV^2` | Heat: `Q=mc\Delta T` | Buffer: `\beta=dB/d(\mathrm{pH})` | Buffer capacity | Systems absorb disturbance until capacity is exceeded. | Do not assume high capacity means no harm or no change. |
| Derived law-family | Threshold | Arrhenius: `k=Ae^{-E_a/(RT)}` | Neuron: spike if `V_m\ge V_{th}` | MOSFET: `I_D=\tfrac12\mu_nC_{ox}(W/L)(V_{GS}-V_T)^2` | Arrhenius | Barriers alter rate and probability of transition. | Do not treat all thresholds as binary cliffs. |
| Derived law-family | Coupling and Valence | Coupled dynamics: `\dot x_i=f_i(x_i)+\sum K_{ij}g_{ij}` | Bond order: `BO=(N_b-N_a)/2` | Reflection: `\Gamma=(Z_L-Z_0)/(Z_L+Z_0)` | Impedance matching | Compatibility governs transfer efficiency. | Do not treat compatibility as permanent or universal. |
| Derived law-family | Path Dependence | State update: `S_{t+1}=F(S_t,flow_t)` | Hysteresis: `W=\oint H\,dB` | Non-Markov dependence | Hysteresis | Same present may hide different histories. | Do not identify current state with full identity. |
| Derived law-family | Quantized Transition | Atomic: `\Delta E=h\nu` | Sampling: `x[n]=x(nT_s)`, `f_s\ge2f_{max}` | Redox: `\Delta G=-nFE` | Sampling theory | Discrete events can preserve continuity if sampling is sufficient. | Do not assume discrete events imply discontinuous meaning. |
| Derived law-family | Phase and Resonance | Wave: `x(t)=A\cos(\omega t+\phi)` | AC power: `P=V_{rms}I_{rms}\cos\phi` | LC resonance: `\omega_0=1/\sqrt{LC}` | AC power factor | Alignment determines effective work. | Do not count activity without phase/rate relation. |
| Derived law-family | Closure | Feedback: `T(s)=G(s)/(1+G(s)H(s))` | Triadic closure coefficient | Autocatalytic: `d[X]/dt=k[A][X]-\lambda[X]` | Feedback control | Closed loops produce behavior open chains cannot. | Do not call every cycle stable. |
| Derived law-family | Boundary / Green Response | Control-volume balance | Green's theorem | Green function: `LG=\delta` | Green function | Local events distribute according to operator, domain, and boundary. | Do not assume FLAR is linear without proof. |
| Derived law-family | Catalysis | Rate ratio: `k_{cat}/k_{uncat}=e^{(E_{a,uncat}-E_{a,cat})/(RT)}` | Michaelis-Menten: `v=V_{max}[S]/(K_m+[S])` | BJT: `I_C=\beta I_B` | Enzyme catalysis | Structure lowers path cost without being the payload. | Do not assume catalyst is unchanged in every practical sense. |
| Derived law-family | Symmetry Breaking | Landau: `F(m)=am^2+bm^4` | Nucleation: `\Delta G(r)=4\pi r^2\gamma+\frac43\pi r^3\Delta G_v` | Context entropy: `H(M\mid C)` | Homonym resolution | Constraint selects among live possibilities. | Do not assume selected means inevitable. |
| Derived law-family | Scale Recursion | Composition: `Y=\mathcal C(X_1,...,X_n)` | Renormalization: `K'=R_b(K)` | Molecular graph: `G=(V,E)` | Molecular graph | Emergence at one scale becomes object/medium at another. | Do not erase scale-specific laws. |
| Derived law-family | Conceptual Emergence | Equivalence class: `C=[x]_{\sim}` | Attractor stability | Synergy: `Syn=I(X,Y;Z)-I(X;Z)-I(Y;Z)` | Attractor stability | Concepts persist as stable, transmissible patterns. | Do not make concept equal word or label. |
| FLAR postulate | Fiq Temporalization | Clock update: `x_{n+1}=F(x_n,u_n)` | Sampling: `f_s\ge2f_{max}` | `N_{fiq/tock}=ticks/tock` | Sampling theory | Continuity requires enough ordered ticks per tock. | Do not reduce fiqs to timestamps or memory rows. |
| FLAR implementation law | Ficks Flow | Fick: `\mathbf J=-D\nabla C` | Ohm network: `\mathbf I=\mathbf G\mathbf V` | Graph diffusion: `d\mathbf x/dt=-L\mathbf x` | Graph diffusion | Flow is gradient-mediated and architecture-dependent across a network. | Do not claim current FLAR formalization is completed theorem. |
| FLAR postulate | Three-Core Inference | AC phase alignment | Clock coincidence | `t_\psi\equiv t_\phi\equiv t_\omega\pmod{T_{tock}}` | AC phase | Inference is phase-locked simultaneity across assigned cores. | Do not treat independent core activity as inference. |

## Domain-overlap grid

| Domain | What it contributes to Energy Theory | Most useful warning |
|---|---|---|
| Physics | potentials, gradients, flux, phase, resonance, boundary integrals | physical formulae do not automatically transfer outside physical units |
| Chemistry | valence, activation, catalysis, diffusion, molecular emergence | reaction equations carry substrate assumptions |
| Electronics | impedance, conductance, threshold gates, phase, clocking, feedback | ideal circuit equations hide parasitics and material limits |
| Linguistics | contrast, context-selection, homonym resolution, syntax-as-constraint | linguistic operators are not root Energy Theory vocabulary |
| Information theory | entropy, divergence, mutual information, synergy | information measures do not by themselves imply meaning or agency |
| Computation | discrete state updates, sampling, clocks, graph diffusion | implementation choices are not universal laws |
| Social systems | authority gradients, role coupling, jury closure, institutional capacity | social doctrine needs its own bridge; do not smuggle it in as physics |
| FLAR | fiqs, PCTA heptagrams, PTCA core assignment, PCNA tensors | proposed architecture is not automatically proven by resonance |
| EDCMBONE | semantic fidelity, operators, hmmm boundary, not-wrong contagion | flesh/bone is native here, not the root Energy Theory ontology |

## Preferred overlap pattern

When adding a new candidate, classify it first:

```text
root axiom
    self-evident once terms are defined; should be rare

definition
    vocabulary binding

derived law-family
    reusable relation requiring domain/architecture structure

resonance
    cross-domain resemblance, not identity

FLAR postulate
    chosen implementation commitment

interface doctrine
    separation rule preventing category collapse
```

Then prefer a triple where one theory example illuminates the other two:

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
