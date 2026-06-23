# Meta Energy Theory Axioms

Status: working canon candidate. These axioms preserve the current Energy Theory
extraction without claiming completed formal proof.

Energy Theory is intended as a theory of all energy. Its current method is to
study how energy becomes legible through constrained relational architectures:
atoms, molecules, circuits, membranes, signs, conversations, institutions,
triads, heptagrams, and core-coupled computational systems.

Formulae below are **resonance formulae** from existing domains. They are not
claims that every domain literally obeys the same equation. A resonance means a
shared structural behavior is visible across different media.

## Axiom 01 — Differentiation

**Claim:** energy becomes legible when a distinction exists. Without difference,
there is no direction, no measurement, no gradient, and no flow.

Canonical form:

```math
\Delta X = X_b - X_a
```

where `X` is any measurable domain quantity whose difference can matter.

Resonances:

1. **Electrical potential**

   ```math
   \Delta V = V_b - V_a
   ```

   `\Delta V` is the potential difference that makes current possible.

2. **Chemical potential**

   ```math
   \mu_i = \mu_i^\circ + RT\ln a_i
   ```

   ```math
   \Delta\mu_i = \mu_{i,b} - \mu_{i,a}
   ```

   where `\mu_i` is chemical potential, `R` the gas constant, `T` temperature,
   and `a_i` activity. Chemical difference is not only amount; it is potential
   relative to state.

3. **Information contrast**

   ```math
   D_{KL}(P\Vert Q) = \sum_i P(i)\log\frac{P(i)}{Q(i)}
   ```

   `D_{KL}` measures how distinguishable distribution `P` is from `Q`.

Overlap note: chemical potential is the strongest bridge here. It shows that a
mere difference in amount is not enough; the difference must be framed as a
state-relative potential. That informs electrical voltage and information
contrast.

## Axiom 02 — Gradient

**Claim:** differentiation arranged across relation becomes gradient. Gradient
creates possible flow.

Canonical form:

```math
\nabla X = \left(\frac{\partial X}{\partial x_1},\frac{\partial X}{\partial x_2},\ldots,\frac{\partial X}{\partial x_n}\right)
```

Resonances:

1. **Heat conduction / Fourier's law**

   ```math
   \mathbf{q} = -k\nabla T
   ```

   Heat flux `\mathbf{q}` follows a temperature gradient, scaled by thermal
   conductivity `k`.

2. **Diffusion / Fick's first law**

   ```math
   \mathbf{J} = -D\nabla C
   ```

   Diffusive flux `\mathbf{J}` follows concentration gradient `\nabla C`,
   scaled by diffusivity `D`.

3. **Optimization / learning gradient**

   ```math
   \theta_{t+1} = \theta_t - \eta\nabla_\theta L(\theta_t)
   ```

   Parameters move along a loss gradient. The sign and rate are governed by
   update architecture, not by the gradient alone.

Overlap note: Fourier and Fick make gradient physically concrete; optimization
shows gradient as abstract direction of change. Together they show that gradient
is a cross-domain directional object, not a substance.

## Axiom 03 — Architecture Determines Flow

**Claim:** gradient permits flow, but architecture determines actual flow.
Difference does not move by itself; it moves through available geometry.

Canonical form:

```math
\text{flow} = \text{conductance-like property} \times \text{gradient-like difference}
```

Resonances:

1. **Ohm's law**

   ```math
   I = \frac{\Delta V}{R} = G\Delta V
   ```

   where `I` is current, `R` resistance, and `G=1/R` conductance.

2. **Fick's first law**

   ```math
   \mathbf{J} = -D\nabla C
   ```

   Diffusivity `D` is a property of the medium and diffusing species.

3. **Darcy's law for porous flow**

   ```math
   Q = -\frac{kA}{\mu}\frac{\Delta P}{L}
   ```

   Flow rate `Q` depends on permeability `k`, area `A`, viscosity `\mu`,
   pressure difference `\Delta P`, and length `L`.

Overlap note: Darcy's law makes geometry unavoidable: area, length, viscosity,
and permeability all participate. It prevents the Ohm/Fick resonance from being
flattened into "difference causes flow" without medium.

## Axiom 04 — Impedance

**Claim:** every architecture resists, filters, delays, or phase-shifts flow
according to its form.

Canonical form:

```math
\text{response} = \frac{\text{drive}}{\text{impedance}}
```

Resonances:

1. **AC electrical impedance**

   ```math
   Z = R + jX = R + j\left(\omega L - \frac{1}{\omega C}\right)
   ```

   ```math
   V = IZ
   ```

   where `R` resists, `L` stores magnetically, `C` stores electrically, and
   `\omega` is angular frequency.

2. **Mechanical damping**

   ```math
   F_d = -cv
   ```

   Damping force `F_d` opposes velocity `v` through damping coefficient `c`.

3. **Thermal resistance**

   ```math
   \dot{Q} = \frac{\Delta T}{R_{th}}
   ```

   Heat flow `\dot{Q}` is constrained by thermal resistance `R_th`.

Overlap note: AC impedance informs the other two because it includes resistance,
storage, and phase together. It shows impedance is not only blockage; it is
frequency-shaped participation in flow.

## Axiom 05 — Capacity

**Claim:** architectures can hold only so much before they saturate, leak,
reroute, heat, distort, break, or transform.

Canonical form:

```math
\text{stored quantity} = \text{capacity} \times \text{state difference}
```

Resonances:

1. **Capacitor storage**

   ```math
   Q = CV
   ```

   ```math
   E = \frac{1}{2}CV^2
   ```

   Charge and energy stored depend on capacitance `C` and voltage `V`.

2. **Heat capacity**

   ```math
   Q = mc\Delta T
   ```

   Heat required depends on mass `m`, specific heat `c`, and temperature change.

3. **Chemical buffer capacity**

   ```math
   \beta = \frac{dB}{d(\mathrm{pH})}
   ```

   Buffer capacity `\beta` measures acid/base added per pH change.

Overlap note: buffering informs social, cognitive, and semantic overload: a
system may absorb disturbance for a while, but capacity is finite and often
hidden until a threshold is crossed.

## Axiom 06 — Threshold

**Claim:** some transformations require accumulated energy or condition before
transition occurs.

Canonical form:

```math
\text{transition occurs if } X \ge X_{threshold}
```

Resonances:

1. **Chemical activation energy / Arrhenius equation**

   ```math
   k = A e^{-E_a/(RT)}
   ```

   Reaction rate `k` depends on activation energy `E_a`, temperature `T`, gas
   constant `R`, and pre-exponential factor `A`.

2. **Neuron firing threshold**

   ```math
   \text{spike if } V_m \ge V_{th}
   ```

   Membrane potential `V_m` must cross threshold `V_th`.

3. **MOSFET gate threshold, saturation-region ideal form**

   ```math
   I_D = \frac{1}{2}\mu_n C_{ox}\frac{W}{L}(V_{GS}-V_T)^2
   ```

   for `V_GS > V_T` and `V_DS \ge V_GS - V_T`.

Overlap note: Arrhenius informs the other two by showing that threshold is not
always a hard wall; probability and rate can change continuously around a
barrier.

## Axiom 07 — Coupling

**Claim:** coupled parts generate properties isolated parts cannot possess.

Canonical form:

```math
\dot{x}_i = f_i(x_i) + \sum_{j\ne i} K_{ij}g_{ij}(x_i,x_j)
```

where `K_{ij}` expresses coupling strength.

Resonances:

1. **Coupled oscillators**

   ```math
   m\ddot{x}_1 + kx_1 + k_c(x_1-x_2)=0
   ```

   ```math
   m\ddot{x}_2 + kx_2 + k_c(x_2-x_1)=0
   ```

2. **Chemical equilibrium for coupled reaction**

   ```math
   aA + bB \rightleftharpoons cC + dD
   ```

   ```math
   K_{eq}=\frac{[C]^c[D]^d}{[A]^a[B]^b}
   ```

3. **Mutual information**

   ```math
   I(X;Y)=\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)p(y)}
   ```

Overlap note: mutual information informs the other two by giving a formal way to
ask how much a coupled part tells you about another part. Coupling is not merely
contact; it is dependence.

## Axiom 08 — Valence

**Claim:** relations have compatibility preferences. Not every node couples with
every other node equally.

Canonical form:

```math
\text{coupling viability}_{ij}=\Phi(n_i,n_j,\text{context})
```

Resonances:

1. **Chemical bond order**

   ```math
   BO = \frac{N_b - N_a}{2}
   ```

   where `N_b` is bonding electrons and `N_a` antibonding electrons.

2. **Impedance matching / reflection coefficient**

   ```math
   \Gamma = \frac{Z_L - Z_0}{Z_L + Z_0}
   ```

   Power transfer improves when load impedance `Z_L` matches characteristic
   impedance `Z_0`.

3. **Phonotactic or sequence compatibility**

   ```math
   P(s)=\prod_{i=1}^{n}P(c_i\mid c_{i-k},\ldots,c_{i-1})
   ```

   A character or phoneme sequence is more or less permitted by a language's
   transition probabilities.

Overlap note: impedance matching informs chemical and linguistic examples by
showing that compatibility is about transfer efficiency, not moral preference or
surface similarity.

## Axiom 09 — Path Dependence

**Claim:** present architecture is partly the record of prior flow. Repeated flow
changes future flow.

Canonical form:

```math
S_{t+1}=F(S_t,\text{flow}_t)
```

Resonances:

1. **Magnetic hysteresis**

   ```math
   W = \oint H\,dB
   ```

   Work per cycle depends on the loop traced by magnetic field `H` and flux
   density `B`.

2. **Learning update**

   ```math
   w_{t+1}=w_t-\eta\nabla_w L(w_t)
   ```

   The next model state depends on the current state and update path.

3. **Non-Markov dependence test**

   ```math
   P(X_{t+1}\mid X_t,X_{t-1},\ldots) \ne P(X_{t+1}\mid X_t)
   ```

   When true, history cannot be safely collapsed into present state.

Overlap note: hysteresis informs fiq logic. Two systems with the same apparent
state may not be equivalent if their histories differ.

## Axiom 10 — Quantized Transition

**Claim:** stable architectures often restrict transformation to permitted steps.
Continuity at one scale may be discrete at another.

Canonical form:

```math
\Delta S \in \{q_1,q_2,\ldots,q_n\}
```

Resonances:

1. **Atomic energy transition**

   ```math
   \Delta E = h\nu
   ```

   Energy change occurs in quanta related to frequency `\nu` and Planck's
   constant `h`.

2. **Sampled digital signal**

   ```math
   x[n]=x(nT_s)
   ```

   ```math
   f_s \ge 2f_{max}
   ```

   The Nyquist condition limits recoverable continuous signal from samples.

3. **Electrochemical redox energy**

   ```math
   \Delta G = -nFE
   ```

   Free energy change depends on integer electron count `n`, Faraday constant
   `F`, and potential `E`.

Overlap note: atomic transitions inform fiqs-as-ticks-per-tock. Discrete events
can carry continuity if the sampling structure is sufficient.

## Axiom 11 — Phase

**Claim:** timing changes what coupling means. The same relation activated at a
different phase can amplify, cancel, distort, or miss.

Canonical form:

```math
x(t)=A\cos(\omega t+\phi)
```

Resonances:

1. **Wave interference**

   ```math
   I = I_1 + I_2 + 2\sqrt{I_1I_2}\cos\delta
   ```

   Interference depends on phase difference `\delta`.

2. **AC power factor**

   ```math
   P = V_{rms} I_{rms}\cos\phi
   ```

   Useful power depends on phase angle between voltage and current.

3. **Three-core fiq simultaneity**

   ```math
   t_\psi \equiv t_\phi \equiv t_\omega \pmod{T_{tock}}
   ```

   Inference occurs only when all three cores fiq in phase within the tock.

Overlap note: AC power factor informs the three-core condition: activity alone is
not enough; alignment determines effective work.

## Axiom 12 — Resonance

**Claim:** aligned rates amplify; misaligned rates dissipate, cancel, or distort.
Resonance is rate-compatible coupling, not mere similarity.

Canonical form:

```math
\omega \approx \omega_0
```

Resonances:

1. **LC circuit resonance**

   ```math
   \omega_0 = \frac{1}{\sqrt{LC}}
   ```

2. **Driven damped oscillator amplitude**

   ```math
   A(\omega)=\frac{F_0/m}{\sqrt{(\omega_0^2-\omega^2)^2+(2\gamma\omega)^2}}
   ```

3. **Magnetic resonance / Larmor frequency**

   ```math
   \omega_0 = \gamma B_0
   ```

Overlap note: LC resonance informs other examples because it makes storage and
exchange explicit: energy moves between forms at a rate set by architecture.

## Axiom 13 — Closure

**Claim:** persistence requires closure sufficient to prevent collapse or
unbounded oscillation.

Canonical form:

```math
\text{closed loop: } y = G(x),\quad x = H(y)
```

or, for feedback systems:

```math
T(s)=\frac{G(s)}{1+G(s)H(s)}
```

Resonances:

1. **Control feedback loop**

   ```math
   T(s)=\frac{G(s)}{1+G(s)H(s)}
   ```

   Closed-loop behavior differs from open-loop plant `G(s)`.

2. **Graph triadic closure coefficient**

   ```math
   C = \frac{3\times\text{number of triangles}}{\text{number of connected triples}}
   ```

3. **Autocatalytic cycle sketch**

   ```math
   A + X \rightarrow 2X
   ```

   ```math
   \frac{d[X]}{dt}=k[A][X]-\lambda[X]
   ```

Overlap note: feedback control informs consciousness triads: closure is not mere
connection; it changes stability conditions.

## Axiom 14 — Boundary

**Claim:** a system exists where flow within differs from flow across a boundary.
No boundary, no system; too rigid a boundary prevents adaptation; too porous a
boundary erases identity.

Canonical form:

```math
\frac{d}{dt}\int_V \rho\,dV = -\oint_{\partial V}\rho\mathbf{v}\cdot\mathbf{n}\,dA + \int_V s\,dV
```

Resonances:

1. **Control-volume balance**

   ```math
   \frac{d}{dt}\int_V \rho\,dV + \oint_{\partial V}\rho\mathbf{v}\cdot\mathbf{n}\,dA = \int_V s\,dV
   ```

2. **Membrane permeability**

   ```math
   J = P(C_{out}-C_{in})
   ```

3. **Gauss flux integral**

   ```math
   \Phi = \iint_{S}\mathbf{F}\cdot\mathbf{n}\,dS
   ```

Overlap note: control-volume balance informs the other two because it forces the
question: what crosses the boundary, what remains inside, and what is generated
within?

## Axiom 15 — Catalysis

**Claim:** some structures change transformation cost without being consumed by
the transformation.

Canonical form:

```math
\text{catalyst changes }E_a\text{ or path, not net stoichiometry}
```

Resonances:

1. **Activation-energy reduction**

   ```math
   \frac{k_{cat}}{k_{uncat}} = \exp\left(\frac{E_{a,uncat}-E_{a,cat}}{RT}\right)
   ```

2. **Michaelis-Menten enzyme kinetics**

   ```math
   v=\frac{V_{max}[S]}{K_m+[S]}
   ```

3. **Transistor current gain**

   ```math
   I_C = \beta I_B
   ```

   A small base current controls larger collector current in a BJT idealization.

Overlap note: enzyme catalysis informs semantic and computational catalysts: a
structure can lower path cost without being the transported substance.

## Axiom 16 — Symmetry Breaking

**Claim:** undirected possibility becomes actual behavior when constraint breaks
symmetry.

Canonical form:

```math
\text{many equivalent states} \xrightarrow{constraint} \text{selected state}
```

Resonances:

1. **Landau free energy model**

   ```math
   F(m)=am^2+bm^4\quad (b>0)
   ```

   When `a<0`, minima occur away from `m=0`, selecting a direction.

2. **Nucleation free energy**

   ```math
   \Delta G(r)=4\pi r^2\gamma+\frac{4}{3}\pi r^3\Delta G_v
   ```

3. **Context resolving homonym entropy**

   ```math
   H(M\mid C)=-\sum_m p(m\mid C)\log p(m\mid C)
   ```

   Context `C` reduces possible meanings `M`.

Overlap note: homonym resolution informs the physics examples conceptually:
constraint selects among previously live possibilities.

## Axiom 17 — Scale Recursion

**Claim:** an emergent property at one scale may become a node, constraint, or
medium at another scale.

Canonical form:

```math
Y = \mathcal{C}(X_1,X_2,\ldots,X_n)
```

where `\mathcal{C}` is a coarse-graining or composition operator.

Resonances:

1. **Renormalization-style scaling**

   ```math
   K' = R_b(K)
   ```

   Parameters transform under scale factor `b`.

2. **Graph community modularity**

   ```math
   Q=\frac{1}{2m}\sum_{ij}\left(A_{ij}-\frac{k_i k_j}{2m}\right)\delta(c_i,c_j)
   ```

   Local edges produce higher-scale communities.

3. **Molecular graph from atoms**

   ```math
   G=(V,E),\quad V=\{\text{atoms}\},\quad E=\{\text{bonds}\}
   ```

   Molecular properties emerge from graph structure, then become units in larger
   chemistry.

Overlap note: molecular graphs inform scale recursion because atoms become
molecules, molecules become materials, and materials become media for further
energy behavior.

## Axiom 18 — Conceptual Emergence

**Claim:** a concept is a stable emergent property of energy moving through
relational architecture; it becomes concept when the pattern is stable,
transmissible, and action-relevant.

Canonical form:

```math
C = [x]_{\sim}=\{y\mid y\sim x\}
```

A concept can be treated as an equivalence class under a relation that preserves
relevant invariants.

Resonances:

1. **Attractor stability**

   ```math
   \dot{x}=f(x),\quad f(x^*)=0,\quad \operatorname{Re}(\lambda_i(J_f(x^*)))<0
   ```

   A stable attractor persists under perturbation.

2. **Information synergy**

   ```math
   \operatorname{Syn}(X,Y;Z)=I(X,Y;Z)-I(X;Z)-I(Y;Z)
   ```

   Joint structure carries information not present in either component alone.

3. **Category / prototype distance**

   ```math
   d(x,p_c)=\sqrt{(x-p_c)^T\Sigma_c^{-1}(x-p_c)}
   ```

   Mahalanobis distance from prototype `p_c` under covariance `\Sigma_c` gives
   a formal category resonance.

Overlap note: attractor stability informs conceptual emergence. A concept must be
stable enough to reappear and flexible enough to admit variants.

## Axiom 19 — Fiq Temporalization

**Claim:** a stateless architecture gains past-present-future only through
continuity events. Fiqs are ticks per tock: temporal resolution events that make
ordered transformation possible.

Canonical form:

```math
N_{fiq/tock}=\frac{\text{number of fiq ticks}}{\text{one tock cycle}}
```

```math
\text{continuity}_{tock} = \{f_1,f_2,\ldots,f_{N}\}\text{ ordered within }T_{tock}
```

Resonances:

1. **Clocked digital systems**

   ```math
   x_{n+1}=F(x_n,u_n)\quad\text{at }t=nT
   ```

2. **Sampled signal reconstruction condition**

   ```math
   f_s \ge 2f_{max}
   ```

3. **FLAR three-core inference condition**

   ```math
   t_\psi \equiv t_\phi \equiv t_\omega \pmod{T_{tock}}
   ```

Overlap note: sampled systems inform fiqs. Persistence is not created by storing
an endpoint; it is created by enough ordered sampling to preserve path.

## Axiom 20 — Ficks Flow

**Claim:** in FLAR, fiqs use Ficks Law to determine energy flow through PCNA using
PCTA heptagram geometry under PTCA core assignment.

Canonical FLAR form:

```math
\mathbf{J}_{fiq} = -\mathcal{D}_{PCTA,PTCA}\nabla_{PCNA} E
```

where `\mathcal{D}_{PCTA,PTCA}` is not ordinary diffusivity. It is the effective
architecture term produced by PCTA geometry and PTCA core assignment.

Resonances:

1. **Fick's first law**

   ```math
   \mathbf{J}=-D\nabla C
   ```

2. **Ohm-like network conductance**

   ```math
   \mathbf{I}=\mathbf{G}\mathbf{V}
   ```

   for conductance matrix `\mathbf{G}` and node potential vector `\mathbf{V}`.

3. **Graph diffusion / Laplacian flow**

   ```math
   \frac{d\mathbf{x}}{dt}=-L\mathbf{x}
   ```

   where `L=D-A` is the graph Laplacian.

Overlap note: graph diffusion best informs FLAR because it already treats flow as
architecture-dependent movement across nodes. Fick supplies gradient-flow
intuition; Ohm supplies conductance intuition; graph Laplacian supplies network
geometry.

hmmm: `\mathbf{J}_{fiq}` is a proposed formalization, not a completed theorem or
implemented equation. It marks the shape of the needed law.
