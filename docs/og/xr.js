/* AR / VR training view (docs/xr.html): the axis arcs with their travel limits, the light path and the BRDF lobe, drawn
   over the real machine in a headset (WebXR "immersive-ar"), around a ghost of the CAD model ("immersive-vr"), or in
   this page. One code path for every device, so two headsets can be compared on the same content.
   Geometry: og/model/rig.js (axes, travel, lamp and camera points; machine millimetres, z up).
   Pose: R = Rz(M3) Ry(-M2) Rx(M1), sample normal = R e_x (opengonio/gantry/kinematics.py, tools/cad/poses.py).
   BRDF: Lambert + GGX, metallic-roughness, F0 0.04 (opengonio/fit.py ggx(); tests/test_xr.py compares the two).
   Not yet run on a headset: see wiki/src/XR-training.md.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const D2R = Math.PI / 180;
  const LESSONS = [
    { id: "arcs", title: "Arcs and limits", text: "Each axis draws its travel. Solid: where it can go. Red: where it must not (the lamp arm stops before the camera)." },
    { id: "incident", title: "Incident light", text: "Light leaves the lamp and reaches the sample. θi is the angle between the ray and the sample normal." },
    { id: "reflect", title: "Reflection", text: "The mirror direction leaves at the same angle on the other side of the normal. The camera sits at θr; it sees the highlight only when it is near the mirror direction." },
    { id: "lobe", title: "BRDF lobe", text: "The surface sends light in every direction. The lobe's radius is the BRDF times cos θr for the lamp where it is now (square-root scale). Rough: wide and low. Smooth: narrow and tall." },
    { id: "scan", title: "Measure", text: "The lamp sweeps its arc. Each bar is what the camera reads at that lamp angle: one row of the measurement." },
  ];

  /* ---------- vectors and 4 x 4 matrices (column-major, like WebGL) ---------- */
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const mulS = (a, s) => [a[0] * s, a[1] * s, a[2] * s], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const len = a => Math.hypot(a[0], a[1], a[2]), norm = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const I4 = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  function mul(a, b) { const o = new Array(16).fill(0);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]; return o; }
  const T = t => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, t[0], t[1], t[2], 1];
  const S = s => [s, 0, 0, 0, 0, s, 0, 0, 0, 0, s, 0, 0, 0, 0, 1];
  function rot(d, deg) { const a = deg * D2R, c = Math.cos(a), s = Math.sin(a), C = 1 - c, [x, y, z] = d;
    return [c + x * x * C, y * x * C + z * s, z * x * C - y * s, 0, x * y * C - z * s, c + y * y * C, z * y * C + x * s, 0,
            x * z * C + y * s, y * z * C - x * s, c + z * z * C, 0, 0, 0, 0, 1]; }
  const rotAbout = (p, d, deg) => mul(T(p), mul(rot(d, deg), T(mulS(p, -1))));
  const apply = (m, v) => [0, 1, 2].map(r => m[r] * v[0] + m[4 + r] * v[1] + m[8 + r] * v[2] + m[12 + r]);
  const applyDir = (m, v) => [0, 1, 2].map(r => m[r] * v[0] + m[4 + r] * v[1] + m[8 + r] * v[2]);
  function lookAt(eye, at, up) { const z = norm(sub(eye, at)), x = norm(cross(up, z)), y = cross(z, x);
    return [x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, eye), -dot(y, eye), -dot(z, eye), 1]; }
  function persp(fov, asp, n, f) { const t = 1 / Math.tan(fov / 2);
    return [t / asp, 0, 0, 0, 0, t, 0, 0, 0, 0, (f + n) / (n - f), -1, 0, 0, 2 * f * n / (n - f), 0]; }

  /* ---------- the physics the lessons show ---------- */
  /** fit.py ggx(): BRDF in 1/sr for unit vectors n (normal), l (to the lamp), v (to the camera). */
  function brdf(n, l, v, m) {
    const ci = dot(n, l), co = dot(n, v);
    if (ci <= 0 || co <= 0) return 0;
    const h = norm(add(l, v)), a = Math.max(m.rough * m.rough, 1e-4), a2 = a * a, ch = dot(n, h);
    const d = a2 / (Math.PI * Math.pow(ch * ch * (a2 - 1) + 1, 2));
    const g = 2 * ci * co / (co * Math.sqrt(ci * ci * (1 - a2) + a2) + ci * Math.sqrt(co * co * (1 - a2) + a2));
    const f0 = 0.04 * (1 - m.metal) + m.base * m.metal;
    const f = f0 + (1 - f0) * Math.pow(1 - Math.min(Math.max(dot(l, h), 0), 1), 5);
    return d * g * f / (4 * ci * co) + (1 - m.metal) * (1 - f) * m.base / Math.PI;
  }
  /** Sample frame for a pose: columns of R = Rz(M3) Ry(-M2) Rx(M1). n is the normal, t and b lie in the sample face. */
  function frame(p) {
    const R = mul(rot([0, 0, 1], p.M3), mul(rot([0, 1, 0], -p.M2), rot([1, 0, 0], p.M1)));
    return { n: applyDir(R, [1, 0, 0]), t: applyDir(R, [0, 1, 0]), b: applyDir(R, [0, 0, 1]) };
  }
  /** Everything a lesson needs for one pose (machine millimetres, z up). */
  function optics(R, p, m) {
    const O = [0, 0, R.zero_z], rl = Math.hypot(R.lamp[0], R.lamp[1]);
    const lamp = [rl * Math.cos(p.M4 * D2R), rl * Math.sin(p.M4 * D2R), R.lamp[2]];
    const f = frame(p), l = norm(sub(lamp, O)), v = norm(sub(R.camera, O));
    const ci = dot(f.n, l), co = dot(f.n, v), mirror = norm(sub(mulS(f.n, 2 * ci), l));
    const deg = x => Math.acos(Math.min(1, Math.max(-1, x))) / D2R;
    const value = brdf(f.n, l, v, m);
    return { O, lamp, cam: R.camera, n: f.n, t: f.t, b: f.b, l, v, mirror, ti: deg(ci), tr: deg(co),
             off: deg(dot(mirror, v)), brdf: value, reading: value * Math.max(ci, 0), lit: ci > 0, seen: co > 0 };
  }
  /** Placement of the machine in headset space (metres, y up) from two touched points: the zero point and the camera lens. */
  function place(R, p0, p1) {
    const dx = p1[0] - p0[0], dz = p1[2] - p0[2], yaw = Math.atan2(-dz, dx) / D2R;
    const want = len(sub(R.camera, [0, 0, R.zero_z])) / 1000, got = len(sub(p1, p0));
    return { matrix: mul(T(p0), mul(rot([0, 1, 0], yaw), mul(rot([1, 0, 0], -90), mul(S(0.001), T([0, 0, -R.zero_z]))))),
             residual_mm: (got - want) * 1000, yaw_deg: yaw };
  }
  /** Frame-time summary for the platform comparison (milliseconds between frames). */
  function summary(dts) {
    if (!dts.length) return { frames: 0 };
    const s = dts.slice().sort((a, b) => a - b), q = f => s[Math.min(s.length - 1, Math.floor(f * s.length))];
    const mean = dts.reduce((a, b) => a + b, 0) / dts.length, med = q(0.5);
    return { frames: dts.length, mean_ms: +mean.toFixed(3), median_ms: +med.toFixed(3), p95_ms: +q(0.95).toFixed(3), p99_ms: +q(0.99).toFixed(3),
             fps: +(1000 / mean).toFixed(2), late_frames: dts.filter(d => d > 1.5 * med).length };
  }

  /** Run data, rows of [theta_i, phi_i, theta_r, phi_r, BRDF] in the sample frame (curve.csv), placed on the lobe for the
      lamp direction of `o`: the rows whose theta_i is nearest the current one, if within `tol` degrees. */
  function dataPoints(o, rows, tol) {
    const lp = sub(o.l, mulS(o.n, dot(o.n, o.l))), have = [...new Set(rows.filter(r => r[4] != null).map(r => r[0]))].sort((a, b) => a - b);
    if (!o.lit || len(lp) < 1e-6 || !have.length) return { theta_i: null, have, pts: [] };
    const best = have.reduce((a, b) => Math.abs(b - o.ti) < Math.abs(a - o.ti) ? b : a);
    if (Math.abs(best - o.ti) > tol) return { theta_i: null, have, pts: [] };
    const el = norm(lp), ep = cross(o.n, el), pts = [];
    rows.forEach(r => { if (r[4] == null || r[0] !== best) return;
      const th = r[2] * D2R, ph = (r[3] - r[1]) * D2R;                 // azimuth measured from the lamp's side of the normal
      pts.push({ dir: add(mulS(o.n, Math.cos(th)), add(mulS(el, Math.sin(th) * Math.cos(ph)), mulS(ep, Math.sin(th) * Math.sin(ph)))),
                 value: r[4] * Math.cos(th) }); });
    return { theta_i: best, have, pts };
  }
  /** curve.csv text to rows of [theta_i, phi_i, theta_r, phi_r, BRDF]; throws if a column is missing. */
  function parseCurve(text) {
    const lines = text.split(/\r?\n/).filter(l => l.trim()), head = lines[0].split(",").map(h => h.trim());
    const idx = ["theta_i", "phi_i", "theta_r", "phi_r", "brdf_per_sr"].map(k => { const i = head.indexOf(k); if (i < 0) throw new Error("no column " + k); return i; });
    return lines.slice(1).map(l => { const c = l.split(","); return idx.map(i => c[i] === undefined || c[i].trim() === "" ? null : +c[i]); })
      .filter(r => r.slice(0, 4).every(v => v !== null && Number.isFinite(v)) && (r[4] === null || Number.isFinite(r[4])));
  }

  /* ---------- overlay geometry: triangles only, so lines keep their width in a headset ---------- */
  function builder() {
    const pos = [], col = [];
    const tri = (a, b, c, k) => { pos.push(...a, ...b, ...c); col.push(...k, ...k, ...k); };
    function tube(a, b, w, k) {                              // two crossed ribbons from a to b, w wide
      const d = sub(b, a); if (len(d) < 1e-6) return;
      let u = cross(d, [0, 0, 1]); if (len(u) < 1e-6) u = [1, 0, 0];
      u = mulS(norm(u), w / 2); const q = mulS(norm(cross(d, u)), w / 2);
      [u, q].forEach(e => { const a0 = sub(a, e), a1 = add(a, e), b0 = sub(b, e), b1 = add(b, e); tri(a0, a1, b1, k); tri(a0, b1, b0, k); });
    }
    function path(pts, w, k, dashed) { for (let i = 0; i + 1 < pts.length; i++) if (!dashed || i % 2 === 0) tube(pts[i], pts[i + 1], w, k); }
    function blob(p, r, k) {                                 // octahedron
      const e = [[r, 0, 0], [-r, 0, 0], [0, r, 0], [0, -r, 0], [0, 0, r], [0, 0, -r]].map(o => add(p, o));
      [[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]].forEach(f => tri(e[f[0]], e[f[1]], e[f[2]], k));
    }
    return { tri, tube, path, blob, data: () => ({ pos: new Float32Array(pos), col: new Float32Array(col), n: pos.length / 3 }) };
  }
  const circle = (c, u, w, r, a0, a1, step) => { const out = [];
    for (let a = a0; a <= a1 + 1e-6; a += step) out.push(add(c, add(mulS(u, r * Math.cos(a * D2R)), mulS(w, r * Math.sin(a * D2R))))); return out; };
  const C = { m4: [0.16, 0.78, 0.62], m3: [0.95, 0.66, 0.20], m2: [0.62, 0.52, 0.95], m1: [0.33, 0.62, 0.98], stop: [0.92, 0.26, 0.24],
              ray: [1.0, 0.80, 0.42], mirror: [1.0, 0.95, 0.80], view: [0.72, 0.76, 0.84], normal: [0.95, 0.95, 0.97], lobe: [1.0, 0.62, 0.22], data: [0.40, 0.90, 1.0] };
  const rgba = (c, a) => [c[0], c[1], c[2], a];

  /** The overlay for one frame. `s` is the state (pose, mat, lesson, clock, sweep), `R` the rig. */
  function scene(R, s) {
    const g = builder(), o = optics(R, s.pose, s.mat), L = s.lesson, dim = L === 0 ? 1 : 0.4, O = o.O;
    const rl = Math.hypot(R.lamp[0], R.lamp[1]), X = [1, 0, 0], Y = [0, 1, 0];
    // M4: the lamp's arc, its allowed travel and the gap it must not enter
    const [a0, a1] = R.ranges.M4;
    g.path(circle(O, X, Y, rl, a0, a1, 4), 5, rgba(C.m4, dim));
    g.path(circle(O, X, Y, rl, a1, a0 + 360, 4), 5, rgba(C.stop, dim), true);
    [a0, a1].forEach(a => { const p = circle(O, X, Y, rl, a, a, 1)[0]; g.tube(add(p, [0, 0, -22]), add(p, [0, 0, 22]), 6, rgba(C.stop, dim)); });
    // M3: the table ring; a spoke shows where it points
    const base = [0, 0, 6], rt = 140;
    g.path(circle(base, X, Y, rt, 0, 360, 6), 4, rgba(C.m3, dim));
    g.tube(base, add(base, [rt * Math.cos(s.pose.M3 * D2R), rt * Math.sin(s.pose.M3 * D2R), 0]), 4, rgba(C.m3, dim));
    // M2: the path of the sample normal as the cradle tilts
    const [t0, t1] = R.ranges.M2, tilt = [];
    for (let a = t0; a <= t1 + 1e-6; a += 5) tilt.push(add(O, mulS(frame({ M1: 0, M2: a, M3: s.pose.M3 }).n, 92)));
    g.path(tilt, 4, rgba(C.m2, dim));
    [tilt[0], tilt[tilt.length - 1]].forEach(p => g.blob(p, 6, rgba(C.stop, dim)));
    // M1: the spin, drawn round the normal
    const hub = add(O, mulS(o.n, 62));
    g.path(circle(hub, o.t, o.b, 26, 0, 360, 12), 3, rgba(C.m1, dim));
    g.blob(add(hub, mulS(o.t, 26)), 5, rgba(C.m1, dim));
    // the things every lesson needs: normal, lamp, camera
    g.tube(O, add(O, mulS(o.n, 118)), 4, rgba(C.normal, 0.95));
    g.blob(o.lamp, 13, rgba(C.ray, 1)); g.blob(o.cam, 11, rgba(C.view, 1));
    if (L >= 1) {                                            // incident ray, photons, θi
      g.tube(o.lamp, O, 5, rgba(C.ray, o.lit ? 0.95 : 0.25));
      if (o.lit) for (let i = 0; i < 4; i++) { const k = (s.clock * 0.6 + i / 4) % 1; g.blob(add(o.lamp, mulS(sub(O, o.lamp), k)), 7, rgba(C.ray, 1)); }
      const ax = norm(cross(o.n, o.l)); if (len(cross(o.n, o.l)) > 1e-4) g.path(circle(O, o.n, cross(ax, o.n), 48, 0, o.ti, 4), 3, rgba(C.ray, 0.9));
    }
    if (L >= 2 && o.lit) {                                   // mirror direction, view ray, θr
      g.tube(O, add(O, mulS(o.mirror, 270)), 5, rgba(C.mirror, 0.9));
      for (let i = 0; i < 3; i++) { const k = (s.clock * 0.6 + i / 3) % 1; g.blob(add(O, mulS(o.mirror, 270 * k)), 6, rgba(C.mirror, 1)); }
      g.tube(O, o.cam, 4, rgba(C.view, o.seen ? 0.9 : 0.25));
      const ax = norm(cross(o.n, o.v)); if (len(cross(o.n, o.v)) > 1e-4) g.path(circle(O, o.n, cross(ax, o.n), 62, 0, o.tr, 4), 3, rgba(C.view, 0.9));
    }
    if (L >= 3 && o.lit) {                                   // the lobe: radius = sqrt(f cos θr), capped
      const rad = d => 150 * Math.min(Math.sqrt(brdf(o.n, o.l, d, s.mat) * Math.max(dot(o.n, d), 0)), 1.35);
      const NT = 14, NP = 28, dir = (i, j) => { const th = (i / NT) * 88 * D2R, ph = (j / NP) * 2 * Math.PI;
        return add(mulS(o.n, Math.cos(th)), add(mulS(o.t, Math.sin(th) * Math.cos(ph)), mulS(o.b, Math.sin(th) * Math.sin(ph)))); };
      const P = []; for (let i = 0; i <= NT; i++) { P.push([]); for (let j = 0; j <= NP; j++) { const d = dir(i, j); P[i].push(add(O, mulS(d, rad(d)))); } }
      for (let i = 0; i < NT; i++) for (let j = 0; j < NP; j++) {
        const k = rgba(C.lobe, (i + j) % 2 ? 0.34 : 0.22);
        g.tri(P[i][j], P[i + 1][j], P[i + 1][j + 1], k); g.tri(P[i][j], P[i + 1][j + 1], P[i][j + 1], k);
      }
      if (o.seen) g.blob(add(O, mulS(o.v, rad(o.v))), 8, rgba(C.normal, 1));   // where the camera samples the lobe
    }
    let data = null;
    if (L >= 3 && s.data && s.showData) {                   // run data on the same scale as the lobe
      data = dataPoints(o, s.data.rows, 5);
      data.pts.forEach(q => g.blob(add(O, mulS(q.dir, 150 * Math.min(Math.sqrt(Math.max(q.value, 0)), 1.35))), 6, rgba(C.data, 1)));
    }
    if (L >= 4) {                                            // the sweep: one bar per lamp angle already visited
      for (let a = a0; a <= Math.min(s.sweep, a1) + 1e-6; a += 4) {
        const q = optics(R, Object.assign({}, s.pose, { M4: a }), s.mat), h = 170 * Math.min(Math.sqrt(q.reading), 1.35);
        const p = add(O, [(rl + 26) * Math.cos(a * D2R), (rl + 26) * Math.sin(a * D2R), 0]);
        if (h > 0.5) g.tube(p, add(p, [0, 0, h]), 7, rgba(C.lobe, 0.9));
      }
    }
    return { geo: g.data(), optics: o, data };
  }

  /* ---------- pose of each CAD group (tools/cad/poses.py) ---------- */
  function groupMatrices(R, pose) {
    const ang = { M1: pose.M1 - R.shown.M1, M2: R.shown.M2 - pose.M2, M3: pose.M3 - R.shown.M3, M4: pose.M4 - R.shown.M4 };
    return R.groups.map(g => { let M = I4();
      R.order.forEach(k => { const ax = R.axes[k]; if (ax.moves.includes(g) && Math.abs(ang[k]) > 1e-9) M = mul(rotAbout(ax.point, ax.dir, ang[k]), M); });
      return M; });
  }
  /** What the lessons do on their own (headset, or "Play" in the page): t in seconds. */
  function animate(R, s, t) {
    const tri = (period, lo, hi) => { const k = (t % period) / period; return lo + (hi - lo) * (k < 0.5 ? 2 * k : 2 - 2 * k); };
    const [a0, a1] = R.ranges.M4, p = { M1: 0, M2: 90, M3: 0, M4: 90 };
    if (s.lesson === 0) { const k = Math.floor(t / 8) % 4;
      if (k === 0) p.M4 = tri(8, a0, a1); if (k === 1) p.M3 = tri(8, -90, 90); if (k === 2) p.M2 = tri(8, 20, 90); if (k === 3) p.M1 = tri(8, -180, 180); }
    else if (s.lesson === 4) { p.M2 = 0; p.M3 = 45; s.sweep = a0 + ((t % 14) / 14) * (a1 - a0); p.M4 = s.sweep; }
    else { p.M2 = 0; p.M3 = 45; p.M4 = tri(12, 50, 130); }
    if (s.lesson !== 4) s.sweep = a1;
    s.pose = p;
  }

  /* ---------- WebGL ---------- */
  const MESH_V = `attribute vec3 aPos; attribute vec3 aNrm; attribute float aGroup;
uniform mat4 uVP; uniform mat4 uG[5]; uniform float uScale; varying vec3 vN; varying vec3 vW;
mat4 pick(float g){ if (g < 0.5) return uG[0]; if (g < 1.5) return uG[1]; if (g < 2.5) return uG[2]; if (g < 3.5) return uG[3]; return uG[4]; }
void main(){ mat4 M = pick(aGroup); vec4 w = M * vec4(aPos * uScale, 1.0); vW = w.xyz; vN = normalize(mat3(M) * aNrm); gl_Position = uVP * w; }`;
  const MESH_F = `precision mediump float; varying vec3 vN; varying vec3 vW; uniform vec3 uLamp; uniform float uAlpha; uniform vec3 uTint;
void main(){ vec3 n = normalize(vN); vec3 l = normalize(uLamp - vW); float d = abs(dot(n, l));
  gl_FragColor = vec4(uTint * (0.30 + 0.70 * d), uAlpha); }`;
  const OVER_V = `attribute vec3 aPos; attribute vec4 aCol; uniform mat4 uVP; varying vec4 vC; void main(){ vC = aCol; gl_Position = uVP * vec4(aPos, 1.0); }`;
  const OVER_F = `precision mediump float; varying vec4 vC; void main(){ gl_FragColor = vec4(vC.rgb * vC.a, vC.a); }`;

  async function inflate(b64) {
    const bin = Uint8Array.from(atob(b64), ch => ch.charCodeAt(0));
    return new Uint8Array(await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream("deflate"))).arrayBuffer());
  }

  async function start() {
    const R = window.RIG, canvas = document.getElementById("xr-gl"), $ = id => document.getElementById(id);
    const status = t => { $("xr-status").textContent = t; };
    const gl = canvas.getContext("webgl", { antialias: true, alpha: true, xrCompatible: true, premultipliedAlpha: true });
    if (!gl || !R) { $("xr-nogl").hidden = false; status("No WebGL: the 3D view is off."); return; }
    const sh = (t, src) => { const x = gl.createShader(t); gl.shaderSource(x, src); gl.compileShader(x);
      if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; };
    const prog = (v, f) => { const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, v)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, f));
      gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; };
    const PM = prog(MESH_V, MESH_F), PO = prog(OVER_V, OVER_F), U = (p, n) => gl.getUniformLocation(p, n);

    // the CAD model, as a ghost (optional: it needs a 32-bit index buffer and DecompressionStream)
    let mesh = null;
    if (typeof DecompressionStream !== "undefined" && gl.getExtension("OES_element_index_uint")) {
      const raw = await inflate(R.data), ST = R.stride || 12, vbytes = R.vertices * ST;
      const vb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vb); gl.bufferData(gl.ARRAY_BUFFER, raw.subarray(0, vbytes), gl.STATIC_DRAW);
      const ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib);
      gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint32Array(raw.buffer.slice(raw.byteOffset + vbytes, raw.byteOffset + raw.byteLength)), gl.STATIC_DRAW);
      mesh = { vb, ib, ST, n: (raw.byteLength - vbytes) / 4 };
    }
    const ob = gl.createBuffer(), oc = gl.createBuffer();

    const s = { pose: { M1: 0, M2: 0, M3: 45, M4: 120 }, mat: { base: 0.8, rough: 0.35, metal: 0 }, lesson: 0, clock: 0, sweep: R.ranges.M4[1],
                play: false, ghost: true, occlude: true, showData: true, data: null, view: { yaw: -58, pitch: 26, zoom: 1 }, xr: null, placement: null, align: null, logs: [] };

    /** Build the overlay once per frame (not once per eye) and upload it. */
    function prepare() {
      const sc = scene(R, s);
      gl.bindBuffer(gl.ARRAY_BUFFER, ob); gl.bufferData(gl.ARRAY_BUFFER, sc.geo.pos, gl.DYNAMIC_DRAW);
      gl.bindBuffer(gl.ARRAY_BUFFER, oc); gl.bufferData(gl.ARRAY_BUFFER, sc.geo.col, gl.DYNAMIC_DRAW);
      return sc;
    }
    function draw(VP, mode, sc) {
      const o = sc.optics;
      gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);
      const ghost = mode === "immersive-ar" ? 0 : (s.ghost ? (mode ? 0.55 : 1) : 0);
      const depthOnly = mode === "immersive-ar" && s.occlude;   // AR: the model writes depth only, so real parts hide lines behind them
      if (mesh && (ghost > 0 || depthOnly)) {
        gl.useProgram(PM); gl.bindBuffer(gl.ARRAY_BUFFER, mesh.vb); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, mesh.ib);
        const A = { pos: gl.getAttribLocation(PM, "aPos"), nrm: gl.getAttribLocation(PM, "aNrm"), grp: gl.getAttribLocation(PM, "aGroup") };
        gl.enableVertexAttribArray(A.pos); gl.vertexAttribPointer(A.pos, 3, gl.SHORT, false, mesh.ST, 0);
        gl.enableVertexAttribArray(A.nrm); gl.vertexAttribPointer(A.nrm, 3, gl.BYTE, true, mesh.ST, 6);
        gl.enableVertexAttribArray(A.grp); gl.vertexAttribPointer(A.grp, 1, gl.BYTE, false, mesh.ST, 9);
        gl.uniformMatrix4fv(U(PM, "uVP"), false, VP); gl.uniformMatrix4fv(U(PM, "uG"), false, groupMatrices(R, s.pose).flat());
        gl.uniform1f(U(PM, "uScale"), R.scale); gl.uniform3fv(U(PM, "uLamp"), o.lamp); gl.uniform1f(U(PM, "uAlpha"), 1);
        gl.uniform3f(U(PM, "uTint"), 0.30 * ghost, 0.31 * ghost, 0.34 * ghost);
        if (ghost <= 0) gl.colorMask(false, false, false, false);
        gl.disable(gl.BLEND); gl.depthMask(true); gl.drawElements(gl.TRIANGLES, mesh.n, gl.UNSIGNED_INT, 0);
        gl.colorMask(true, true, true, true);
        [A.pos, A.nrm, A.grp].forEach(a => gl.disableVertexAttribArray(a));
      }
      gl.useProgram(PO); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false);
      const p = gl.getAttribLocation(PO, "aPos"), c = gl.getAttribLocation(PO, "aCol");
      gl.bindBuffer(gl.ARRAY_BUFFER, ob); gl.enableVertexAttribArray(p); gl.vertexAttribPointer(p, 3, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, oc); gl.enableVertexAttribArray(c); gl.vertexAttribPointer(c, 4, gl.FLOAT, false, 0, 0);
      gl.uniformMatrix4fv(U(PO, "uVP"), false, VP); gl.drawArrays(gl.TRIANGLES, 0, sc.geo.n);
      gl.disableVertexAttribArray(p); gl.disableVertexAttribArray(c); gl.depthMask(true); gl.disable(gl.BLEND);
      o.data = sc.data; return o;
    }

    /* ----- the page view ----- */
    function readout(o) {
      $("xr-ti").textContent = o.lit ? o.ti.toFixed(1) + "°" : "behind";
      $("xr-tr").textContent = o.seen ? o.tr.toFixed(1) + "°" : "behind";
      $("xr-off").textContent = o.lit && o.seen ? o.off.toFixed(1) + "°" : "–";
      $("xr-f").textContent = o.brdf.toFixed(3) + " /sr";
      const d = o.data, n = $("xr-data-note");
      if (!s.data) n.textContent = "No run data loaded.";
      else if (!s.showData) n.textContent = s.data.label + ": hidden.";
      else if (s.lesson < 3) n.textContent = s.data.label + ": shown from lesson 4.";
      else if (d && d.pts.length) n.textContent = s.data.label + ": " + d.pts.length + " points at θi = " + d.theta_i + "°.";
      else n.textContent = s.data.label + ": no rows within 5° of this θi. Rows exist at θi = " + (d ? d.have.join("°, ") + "°" : "–") + ".";
    }
    function pageFrame(t) {
      if (s.xr) return;
      s.clock = t / 1000;
      if (s.play) { animate(R, s, s.clock); syncSliders(); } else if (s.lesson === 4) s.sweep = s.pose.M4;
      const dpr = Math.min(window.devicePixelRatio || 1, 2), w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
      if (w && h) {
        if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
        gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, w, h);
        const bg = window.OG ? OG.rgb(OG.tokens().ground) : [0.05, 0.05, 0.05];
        gl.clearColor(bg[0], bg[1], bg[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        const yaw = s.view.yaw * D2R, pit = s.view.pitch * D2R, dist = 1150 * s.view.zoom / Math.min(1, (w / h) / 1.2), at = [40, 0, 150];
        const eye = [at[0] + dist * Math.cos(pit) * Math.cos(yaw), at[1] + dist * Math.cos(pit) * Math.sin(yaw), at[2] + dist * Math.sin(pit)];
        readout(draw(mul(persp(0.62, w / h, 10, 8000), lookAt(eye, at, [0, 0, 1])), null, prepare()));
      }
      requestAnimationFrame(pageFrame);
    }

    /* ----- controls ----- */
    const sliders = { M4: $("xr-m4"), M3: $("xr-m3"), M2: $("xr-m2"), M1: $("xr-m1") };
    Object.keys(sliders).forEach(k => { const e = sliders[k]; e.min = R.ranges[k][0]; e.max = R.ranges[k][1]; e.step = 1; e.value = s.pose[k];
      e.addEventListener("input", () => { s.pose[k] = +e.value; s.play = false; $("xr-play").checked = false; e.nextElementSibling.textContent = e.value + "°"; }); });
    function syncSliders() { Object.keys(sliders).forEach(k => { sliders[k].value = s.pose[k]; sliders[k].nextElementSibling.textContent = Math.round(s.pose[k]) + "°"; }); }
    [["xr-rough", "rough"], ["xr-metal", "metal"], ["xr-base", "base"]].forEach(([id, k]) => { const e = $(id); e.value = s.mat[k]; e.nextElementSibling.textContent = (+e.value).toFixed(2);
      e.addEventListener("input", () => { s.mat[k] = +e.value; e.nextElementSibling.textContent = (+e.value).toFixed(2); }); });
    function setLesson(i) { s.lesson = (i + LESSONS.length) % LESSONS.length; s.sweep = s.lesson === 4 && !s.play ? s.pose.M4 : R.ranges.M4[1];
      document.querySelectorAll("#xr-lessons button").forEach((b, j) => b.setAttribute("aria-checked", String(j === s.lesson)));
      $("xr-lesson-title").textContent = (s.lesson + 1) + ". " + LESSONS[s.lesson].title; $("xr-lesson-text").textContent = LESSONS[s.lesson].text; }
    LESSONS.forEach((l, i) => { const b = document.createElement("button"); b.type = "button"; b.setAttribute("role", "radio"); b.textContent = (i + 1) + " " + l.title;
      b.addEventListener("click", () => setLesson(i)); $("xr-lessons").appendChild(b); });
    $("xr-play").addEventListener("change", e => { s.play = e.target.checked; });
    $("xr-ghost").addEventListener("change", e => { s.ghost = e.target.checked; });
    $("xr-occlude").addEventListener("change", e => { s.occlude = e.target.checked; });
    $("xr-data").addEventListener("change", e => { s.showData = e.target.checked; });
    const setMat = m => { [["xr-rough", "rough"], ["xr-metal", "metal"], ["xr-base", "base"]].forEach(([id, k]) => { s.mat[k] = m[k]; const e = $(id); e.value = m[k]; e.nextElementSibling.textContent = (+m[k]).toFixed(2); }); };
    const ex = window.SIM_EXAMPLES && window.SIM_EXAMPLES.plastic;
    if (ex) s.data = { rows: ex.rows, label: "Simulated run, not a measurement", fit: { base: ex.fit.base_color, rough: ex.fit.roughness, metal: ex.fit.metallic } };
    $("xr-fit").disabled = !(s.data && s.data.fit);
    $("xr-fit").addEventListener("click", () => { if (s.data && s.data.fit) setMat(s.data.fit); });
    $("xr-file").addEventListener("change", async e => { const f = e.target.files[0]; if (!f) return;
      try { const rows = parseCurve(await f.text()); if (!rows.length) throw new Error("no rows");
        s.data = { rows, label: "Loaded " + f.name + " (" + rows.length + " rows)", fit: null }; $("xr-fit").disabled = true; status("Loaded " + f.name + "."); }
      catch (err) { status("Could not read " + f.name + ": " + err.message + ". Expected a run's curve.csv."); } });
    let drag = null;
    canvas.addEventListener("pointerdown", e => { drag = [e.clientX, e.clientY]; canvas.setPointerCapture(e.pointerId); });
    canvas.addEventListener("pointermove", e => { if (!drag) return; s.view.yaw -= (e.clientX - drag[0]) * 0.4; s.view.pitch = Math.max(-5, Math.min(85, s.view.pitch + (e.clientY - drag[1]) * 0.3)); drag = [e.clientX, e.clientY]; });
    canvas.addEventListener("pointerup", () => { drag = null; });
    canvas.addEventListener("wheel", e => { e.preventDefault(); s.view.zoom = Math.max(0.4, Math.min(2.5, s.view.zoom * (e.deltaY > 0 ? 1.08 : 0.93))); }, { passive: false });
    canvas.addEventListener("keydown", e => { const k = e.key;
      if (k === "ArrowLeft") s.view.yaw += 6; else if (k === "ArrowRight") s.view.yaw -= 6; else if (k === "ArrowUp") s.view.pitch = Math.min(85, s.view.pitch + 4);
      else if (k === "ArrowDown") s.view.pitch = Math.max(-5, s.view.pitch - 4); else if (k === "+" || k === "=") s.view.zoom = Math.max(0.4, s.view.zoom * 0.93);
      else if (k === "-") s.view.zoom = Math.min(2.5, s.view.zoom * 1.08); else return; e.preventDefault(); });
    setLesson(0); syncSliders();

    /* ----- headset sessions ----- */
    function pointer(frame, src, ref) {                      // fingertip if the headset tracks hands, else the controller grip
      if (src.hand && frame.getJointPose) { const j = src.hand.get("index-finger-tip"), p = j && frame.getJointPose(j, ref); if (p) return [p.transform.position.x, p.transform.position.y, p.transform.position.z]; }
      const sp = src.gripSpace || src.targetRaySpace, p = sp && frame.getPose(sp, ref);
      return p ? [p.transform.position.x, p.transform.position.y, p.transform.position.z] : null;
    }
    async function enter(mode) {
      let session;
      try { session = await navigator.xr.requestSession(mode, { optionalFeatures: ["local-floor", "hand-tracking"] }); }
      catch (e) { status("The headset refused the " + mode + " session: " + e.message); return; }
      let ref, floor = true;
      try {
        await gl.makeXRCompatible();
        session.updateRenderState({ baseLayer: new XRWebGLLayer(session, gl) });
        try { ref = await session.requestReferenceSpace("local-floor"); } catch (e) { ref = await session.requestReferenceSpace("local"); floor = false; }
      } catch (e) { status("The headset session could not be set up: " + e.message); session.end(); return; }
      const front = [0, floor ? 0.75 : -0.45, -0.75];        // no alignment: the zero point 0.75 m ahead, at bench height
      s.placement = place(R, front, add(front, [0.35, 0, 0]));
      s.align = mode === "immersive-ar" && $("xr-align").checked ? { pts: [], src: null } : null;
      s.xr = session; s.play = true; setLesson(0);
      const log = { mode, started: new Date().toISOString(), user_agent: navigator.userAgent, reference_space: floor ? "local-floor" : "local",
                    views: 0, framebuffer: null, alignment: null, occlusion: mode === "immersive-ar" && s.occlude, lessons_seen: [], dts: [] };
      let last = 0, t0 = 0, pending = null;
      session.addEventListener("select", ev => { pending = ev.inputSource; });
      session.addEventListener("end", () => {
        s.xr = null; s.play = $("xr-play").checked; const dts = log.dts; delete log.dts;
        log.ended = new Date().toISOString(); log.frame_times = summary(dts); s.logs.push(log);
        $("xr-log").textContent = JSON.stringify(log, null, 1); $("xr-save").disabled = false;
        status("Session ended: " + log.frame_times.frames + " frames, " + (log.frame_times.fps || 0) + " frames per second."); requestAnimationFrame(pageFrame);
      });
      session.requestAnimationFrame(function tick(t, frame) {
        if (s.xr !== session) return;
        session.requestAnimationFrame(tick);
        if (!t0) t0 = t; if (last) { if (log.dts.length < 60000) log.dts.push(t - last); } last = t;
        const pose = frame.getViewerPose(ref); if (!pose) return;
        if (pending) {                                       // a pinch or trigger: align first, then step through the lessons
          const p = pointer(frame, pending, ref);
          if (s.align && p) { s.align.pts.push(p);
            if (s.align.pts.length === 2) { s.placement = place(R, s.align.pts[0], s.align.pts[1]);
              log.alignment = { method: "two points: zero point, camera lens", residual_mm: +s.placement.residual_mm.toFixed(1), yaw_deg: +s.placement.yaw_deg.toFixed(1) }; s.align = null; } }
          else if (!s.align) setLesson(s.lesson + 1);
          pending = null;
        }
        s.clock = (t - t0) / 1000; animate(R, s, s.clock);
        if (!log.lessons_seen.includes(LESSONS[s.lesson].id)) log.lessons_seen.push(LESSONS[s.lesson].id);
        const layer = session.renderState.baseLayer;
        gl.bindFramebuffer(gl.FRAMEBUFFER, layer.framebuffer);
        gl.clearColor(0, 0, 0, mode === "immersive-ar" ? 0 : 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        log.views = pose.views.length; log.framebuffer = [layer.framebufferWidth, layer.framebufferHeight];
        const sc = prepare();
        for (const view of pose.views) {
          const vp = layer.getViewport(view); gl.viewport(vp.x, vp.y, vp.width, vp.height);
          draw(mul(Array.from(view.projectionMatrix), mul(Array.from(view.transform.inverse.matrix), s.placement.matrix)), mode, sc);
        }
      });
      status(mode === "immersive-ar" && s.align ? "In the headset: pinch at the sample centre, then at the camera lens." : "In the headset: pinch or pull the trigger for the next lesson.");
    }
    async function offer(mode, btn, note) {
      const ok = navigator.xr && await navigator.xr.isSessionSupported(mode).catch(() => false);
      btn.disabled = !ok; note.textContent = ok ? "available on this device" : "not offered by this browser";
      if (ok) btn.addEventListener("click", () => { if (s.xr) s.xr.end(); else enter(mode); });
    }
    await offer("immersive-ar", $("xr-ar"), $("xr-ar-note")); await offer("immersive-vr", $("xr-vr"), $("xr-vr-note"));
    $("xr-save").addEventListener("click", () => { const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([JSON.stringify(s.logs, null, 1)], { type: "application/json" })); a.download = "opengonio-xr-log.json"; a.click(); URL.revokeObjectURL(a.href); });
    status(navigator.xr ? "Ready. Headset buttons are enabled where the browser offers them." : "Ready. This browser has no WebXR: the page view works; open the page in a headset browser for AR or VR.");
    requestAnimationFrame(pageFrame);
  }

  window.XRTrain = { LESSONS, brdf, frame, optics, place, summary, dataPoints, parseCurve, scene, animate, start };
  if (typeof document !== "undefined" && document.getElementById("xr-gl")) start().catch(e => { const n = document.getElementById("xr-status"); if (n) n.textContent = "Could not start: " + e.message; });
})();
