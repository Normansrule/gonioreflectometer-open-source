# Theory and equations

- **Bidirectional reflectance distribution function (BRDF):** how much light arriving from one direction leaves toward another. The machine sets both directions: the light arm (M4) sets where light comes from; the fixed camera is where it goes; the sample axes (M3, M2, M1) turn the sample between them.
- **Isotropic vs anisotropic:** most materials look the same when spun about their normal (3 angles). Brushed metal, satin and hair do not (4 angles), so they need M1.
- **Microfacet model:** a rough surface is many tiny mirrors; GGX describes how they are tilted, Fresnel how much each reflects, Smith how they shadow each other. Fitting roughness, colour and metalness to measurements gives a game-engine material.
- **Mirror check:** a mirror only reflects when the incident and reflected angles are equal, so with no tilt the peak must sit at M3 = M4 / 2. That calibrates the angles.
- **Calibration:** the mirror peak gives the angle offset; a lamp-off image gives the dark level; a PTFE tile (≈ 99 % white, diffuse) at 45° turns camera counts into absolute BRDF units; repeating the first pose at the end of every run shows whether the lamp drifted.
- **3D scan:** the camera never moves, so every photo's pose is known from the axes; silhouettes give a quick shape (visual hull), photogrammetry gives the full mesh, and (with the optional LED bank) lights from several known directions give surface detail (photometric stereo).

**BRDF and reflection equation** [@R2; @G1]

```math
f_r(\omega_i\to\omega_r)=\frac{dL_r(\omega_i\to\omega_r)}{dE_i}\;[\mathrm{sr}^{-1}],\qquad L_r(x,\omega_r)=\int_{H^2} f_r\,L_i(x,\omega_i)\cos\theta_i\,d\omega_i
```

**Reciprocity, isotropy, energy** [@R2]

```math
f_r(\omega_r\to\omega_i)=f_r(\omega_i\to\omega_r),\qquad f_r^{\mathrm{iso}}=f_r(\theta_i,\theta_r,|\varphi_r-\varphi_i|),\qquad \int_{H^2} f_r\cos\theta_r\,d\omega_r\le 1
```

**Anisotropic (needs M1)** [@G9]

```math
f_r^{\mathrm{aniso}}=f_r(\theta_i,\varphi_i,\theta_r,\varphi_r)\quad\text{(4 angles; } \varphi \text{ measured from the brushing direction)}
```

**Mirror, Snell, total internal reflection** [@R2]

```math
\hat R=\hat I-2(\hat I\cdot\hat N)\hat N,\qquad \eta_i\sin\theta_i=\eta_t\sin\theta_t,\qquad 1-\mu^2\left(1-(\hat I\cdot\hat N)^2\right)<0
```

**Fresnel (Schlick), Lambert** [@R7; @R2]

```math
F(\theta)=F_0+(1-F_0)(1-\cos\theta)^5,\quad F_0=\left(\tfrac{\eta-1}{\eta+1}\right)^2,\qquad f_{r,d}=\frac{\rho_d}{\pi}
```

**Fitted model (Lambert + GGX)** [@R6; @T11; @T17]

```math
f_r=(1-m)(1-F)\frac{\rho}{\pi}+\frac{D\,G_2\,F}{4\cos\theta_i\cos\theta_r},\quad D=\frac{\alpha^2}{\pi\left((h\cdot n)^2(\alpha^2-1)+1\right)^2},\quad h=\frac{\omega_i+\omega_r}{\lVert\omega_i+\omega_r\rVert}
```

Energy: this model (the glTF metallic-roughness form, so a fit loads into a game engine unchanged) weights the diffuse term by $1-F(\omega\cdot h)$ per direction, not by the specular albedo. For bright dielectrics at grazing incidence it reflects more than it receives: computed directional albedo 1.01 at 60°, 1.08 at 80° for base colour 1.0, roughness 0.5 (0.82 and 0.89 for base colour 0.8). Fits are therefore scored on measured angles only, and `tests/test_brdf_tools.py` pins these numbers.

**Sample orientation and angles** [@R1]

```math
R=R_z(M_3)\,R_y(-M_2)\,R_x(M_1),\quad \omega^s=R^\top\omega^w,\quad \theta=\arccos(\omega^s\cdot\hat n),\quad \varphi=\mathrm{atan2}(\omega^s_z,\omega^s_y)
```

**Light and camera directions** [@R1]

```math
\hat l=R_z(M_4)\,\hat x,\qquad \hat c=\hat x\;(\text{fixed}),\qquad \omega_i(p)=\frac{P_L-p}{\lVert P_L-p\rVert},\quad \omega_r(p)=\frac{P_C-p}{\lVert P_C-p\rVert}
```

**In-plane geometry (M2 = M1 = 0)** [@R1]

```math
\theta_r=M_3,\qquad \theta_i=M_4-M_3,\qquad \text{specular: } M_3=\tfrac{M_4}{2}
```

**Step size** 

```math
\Delta\theta=\frac{360^\circ}{200\cdot 16\cdot G}\;\Rightarrow\;0.0047^\circ\,(M_4,\,G=24),\;0.0225^\circ\,(M_3,M_2);\;M_1\text{ direct at }1/64\text{: }0.028^\circ
```

**Optics** [@R1]

```math
\frac{1}{p'}-\frac{1}{p}=\frac{1}{f},\quad m=\frac{p'}{p},\quad d_{\mathrm{Airy}}=2.44\,\lambda N,\quad \mathrm{DOF}\approx\frac{2Nc(1+m)}{m^2}
```

**HDR** [@R5]

```math
g(Z_{ij})=\ln E_i+\ln\Delta t_j
```

**Repeatability from the mirror** [@R1]

```math
\Delta\theta_L=\frac{s\,p_{px}\,P}{f\,D_L}
```

**Slip model (open-loop axes)** [@T59]

Stepper axes have no encoder: belt creep and lost steps move the true angle away from the controller's count. Per axis, $d$ = true − controller angle, $s$ = creep per degree travelled, $a$ = degrees travelled in a move:

```math
\begin{bmatrix}d\\ s\end{bmatrix}_{k+1}=\begin{bmatrix}1&a\\0&1\end{bmatrix}\begin{bmatrix}d\\ s\end{bmatrix}_k+w,\quad w\sim\mathcal N\!\left(0,\begin{bmatrix}q\,a&0\\0&q_s a\end{bmatrix}\right),\qquad y=d+v,\quad v\sim\mathcal N(0,r)
```

```math
K=\frac{P H^\top}{H P H^\top+r},\quad \hat x\leftarrow\hat x+K\,(y-\hat d),\quad P\leftarrow(I-KH)P,\qquad \text{due when } 2\sqrt{P_{dd}}>\text{budget}
```

$y$ is the home-switch edge found again (probe) compared with where it was after homing. Each command is corrected by $\hat d$ (feedforward); a due axis is re-homed, which resets $d$ to $0\pm\sqrt r$; $|y-\hat d|>4\sigma$ is reported as lost steps; $|y|>1^\circ$ stops the run. Travel allowed between references with the nominal values ($q=10^{-6}\,\deg^2/\deg$, creep spread 0.02 %, switch 0.02°, budget 0.1°): 217°, longer once the creep is measured. Details: [Calibration](Calibration.md).

**Calibration: angle offset, camera response, absolute BRDF, lamp drift** [@R1; @R2; @R5]

```math
\delta_{M3}\leftarrow\delta_{M3}-\overline{\left(M_3^{\mathrm{peak}}-\tfrac{M_4}{2}\right)},\qquad
\ln(C-C_d)=\tfrac{1}{\gamma}\ln t+k,\qquad C_{\mathrm{lin}}=(C-C_d)^{\gamma}
```

```math
f_r=\frac{C_{\mathrm{lin}}}{C_{w,\mathrm{lin}}}\cdot\frac{\rho_w}{\pi}\cdot\frac{\cos 45^\circ}{\cos\theta_i},\qquad
\mathrm{drift}=\frac{C_{\mathrm{end}}-C_{\mathrm{start}}}{C_{\mathrm{start}}-C_d}\le 2\,\%
```

$C$ = camera counts (centre of the sample), $C_d$ = lamp off, $t$ = exposure, $\gamma$ = camera response (1 = linear), $C_w$ = PTFE at $\theta_i=45^\circ$, $\rho_w$ = PTFE reflectance, $\delta$ = angle offset (true = commanded + $\delta$). Same exposure for all shots.

**Out-of-plane poses from BRDF angles (inverse kinematics, stages 08–09)** [@R1; @R2]

```math
\cos\alpha=\cos\theta_i\cos\theta_r+\sin\theta_i\sin\theta_r\cos\Delta\varphi,\quad M_4=\alpha,\quad
\hat n=a\hat c+b\hat l+g(\hat c\times\hat l),\quad M_2=\arcsin n_z,\quad M_3=\mathrm{atan2}(n_y,n_x)
```

$a, b$ from $\hat n\cdot\hat c=\cos\theta_r$, $\hat n\cdot\hat l=\cos\theta_i$; $g$ from $|\hat n|=1$. Light on the camera axis ($\alpha<20^\circ$) is out of reach, so pure back-scatter is not measured.

**3D scan: projection, view elevation** [@S1; @S11]

```math
\lambda[u,v,1]^\top=K(R_{oc}p_O+t_{oc}),\quad R_{oc}=R_{wc}RP,\qquad \epsilon=90^\circ-M_2+e_{cam}
```

**3D scan: camera calibration (AX = YB)** [@V15]

```math
\min_{X,Y}\sum_i\left\lVert\log\left(A_i^{-1}XB_iY\right)\right\rVert^2
```

**3D scan: visual hull, photometric stereo** [@S5; @S4]

```math
V=\bigcap_j\{p:\pi_j(p)\in S_j\},\qquad I=L\,g,\;g=L^{+}I,\;\rho=\lVert g\rVert,\;\hat n=g/\rho
```

Full notes: [theory.md]({{REPO}}/phases/00-plan/research.md) · [scan methods]({{REPO}}/phases/12-scan-mesh/research.md).
