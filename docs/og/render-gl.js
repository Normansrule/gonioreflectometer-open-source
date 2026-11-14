/* OpenGonio WebGL2 material viewer: the fitted material on a sphere, a shader ball or a scanned mesh.
   Same BRDF as software/src/opengonio/fit.py (Lambert + GGX, metallic-roughness, F0 0.04) and the same sky, tone
   curve and sRGB steps as opengonio/render/raster.py, plus a shadow from the lamp. Shared by docs/render.html and the
   control app (copied by `make build`). Also: .glb read/write and .ply read, so a run's files open here.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const PI = Math.PI, rad = d => d * PI / 180;

  /* ---------------- small matrix kit (column-major, like GLSL) ---------------- */
  const M = {
    mul(a, b) { const o = new Float32Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
      let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k]; o[c * 4 + r] = s; } return o; },
    persp(fovy, asp, n, f) { const t = 1 / Math.tan(fovy / 2), o = new Float32Array(16);
      o[0] = t / asp; o[5] = t; o[10] = (f + n) / (n - f); o[11] = -1; o[14] = 2 * f * n / (n - f); return o; },
    ortho(h, n, f) { const o = new Float32Array(16); o[0] = 1 / h; o[5] = 1 / h; o[10] = -2 / (f - n); o[14] = -(f + n) / (f - n); o[15] = 1; return o; },
    look(e, t, up) {
      const z = norm(sub(e, t)), x = norm(cross(up, z)), y = cross(z, x), o = new Float32Array(16);
      o.set([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, e), -dot(y, e), -dot(z, e), 1]); return o;
    },
  };
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = a => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const sph = (az, el) => [Math.cos(rad(el)) * Math.cos(rad(az)), Math.cos(rad(el)) * Math.sin(rad(az)), Math.sin(rad(el))];

  /* ---------------- meshes ---------------- */
  function computeNormals(p, idx) {
    const n = new Float32Array(p.length);
    for (let t = 0; t < idx.length; t += 3) {
      const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
      const e1 = [p[b] - p[a], p[b + 1] - p[a + 1], p[b + 2] - p[a + 2]], e2 = [p[c] - p[a], p[c + 1] - p[a + 1], p[c + 2] - p[a + 2]];
      const f = cross(e1, e2);
      for (const v of [a, b, c]) { n[v] += f[0]; n[v + 1] += f[1]; n[v + 2] += f[2]; }
    }
    for (let i = 0; i < n.length; i += 3) { const l = Math.hypot(n[i], n[i + 1], n[i + 2]) || 1; n[i] /= l; n[i + 1] /= l; n[i + 2] /= l; }
    return n;
  }
  function merge(list, name) {
    let nv = 0, ni = 0; list.forEach(m => { nv += m.positions.length; ni += m.indices.length; });
    const P = new Float32Array(nv), N = new Float32Array(nv), I = new Uint32Array(ni);
    let ov = 0, oi = 0;
    list.forEach(m => { P.set(m.positions, ov); N.set(m.normals, ov); for (let k = 0; k < m.indices.length; k++) I[oi + k] = m.indices[k] + ov / 3; ov += m.positions.length; oi += m.indices.length; });
    return { positions: P, normals: N, indices: I, name, unitScale: 0.001 };
  }
  function sphere(r = 25, c = [0, 0, 0], nLat = 48, nLon = 96) {
    const P = [], N = [], I = [];
    for (let i = 0; i <= nLat; i++) for (let j = 0; j <= nLon; j++) {
      const th = PI * i / nLat, ph = 2 * PI * j / nLon, n = [Math.sin(th) * Math.cos(ph), Math.sin(th) * Math.sin(ph), Math.cos(th)];
      N.push(...n); P.push(c[0] + r * n[0], c[1] + r * n[1], c[2] + r * n[2]);
    }
    for (let i = 0; i < nLat; i++) for (let j = 0; j < nLon; j++) {
      const a = i * (nLon + 1) + j, b = a + 1, cc = a + nLon + 1, d = cc + 1; I.push(a, cc, b, b, cc, d);
    }
    return { positions: new Float32Array(P), normals: new Float32Array(N), indices: new Uint32Array(I), name: "sphere", unitScale: 0.001 };
  }
  function cylinder(r, z0, z1, n = 96) {
    const parts = [], P = [], N = [], I = [];
    for (let k = 0; k < n; k++) { const a = 2 * PI * k / n, x = Math.cos(a), y = Math.sin(a); P.push(r * x, r * y, z0); N.push(x, y, 0); }
    for (let k = 0; k < n; k++) { const a = 2 * PI * k / n, x = Math.cos(a), y = Math.sin(a); P.push(r * x, r * y, z1); N.push(x, y, 0); }
    for (let j = 0; j < n; j++) { const k = (j + 1) % n; I.push(j, k, j + n, k, k + n, j + n); }
    parts.push({ positions: new Float32Array(P), normals: new Float32Array(N), indices: new Uint32Array(I) });
    for (const [z, up] of [[z1, 1], [z0, -1]]) {
      const p = [0, 0, z], nn = [0, 0, up], ii = [];
      for (let k = 0; k < n; k++) { const a = 2 * PI * k / n; p.push(r * Math.cos(a), r * Math.sin(a), z); nn.push(0, 0, up); }
      for (let j = 0; j < n; j++) { const k = (j + 1) % n; up > 0 ? ii.push(0, j + 1, k + 1) : ii.push(0, k + 1, j + 1); }
      parts.push({ positions: new Float32Array(p), normals: new Float32Array(nn), indices: new Uint32Array(ii) });
    }
    return merge(parts, "cylinder");
  }
  const shaderBall = (r = 25) => merge([sphere(r, [0, 0, 0.9 * r]), cylinder(0.55 * r, -0.25 * r, 0.1 * r)], "shader_ball");

  /* ---------------- files: .glb in / out, .ply in ---------------- */
  function parseGLB(buf) {
    const dv = new DataView(buf);
    if (dv.getUint32(0, true) !== 0x46546C67 || dv.getUint32(4, true) !== 2) throw new Error("not a glTF 2.0 binary (.glb)");
    const jl = dv.getUint32(12, true), doc = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 20, jl)));
    const binOff = 20 + jl + 8, ours = (doc.asset && doc.asset.generator) === "opengonio.render";
    const read = (ai, comps) => {
      const a = doc.accessors[ai], v = doc.bufferViews[a.bufferView], base = binOff + (v.byteOffset || 0) + (a.byteOffset || 0);
      const T = { 5126: Float32Array, 5125: Uint32Array, 5123: Uint16Array, 5121: Uint8Array }[a.componentType];
      const stride = v.byteStride || comps * T.BYTES_PER_ELEMENT, out = new (T === Float32Array ? Float32Array : Uint32Array)(a.count * comps);
      for (let i = 0; i < a.count; i++) for (let c = 0; c < comps; c++) {
        const off = base + i * stride + c * T.BYTES_PER_ELEMENT;
        out[i * comps + c] = T === Float32Array ? dv.getFloat32(off, true) : T === Uint32Array ? dv.getUint32(off, true) : T === Uint16Array ? dv.getUint16(off, true) : dv.getUint8(off);
      }
      return out;
    };
    const parts = [];
    (doc.meshes || []).forEach(m => m.primitives.forEach(pr => {
      if (pr.mode != null && pr.mode !== 4) return;
      let p = read(pr.attributes.POSITION, 3), n = pr.attributes.NORMAL != null ? read(pr.attributes.NORMAL, 3) : null;
      const count = p.length / 3, idx = pr.indices != null ? read(pr.indices, 1) : Uint32Array.from({ length: count }, (_, i) => i);
      if (!ours) {                                                 // glTF is Y-up: turn into this viewer's Z-up
        const sw = a => { for (let i = 0; i < a.length; i += 3) { const y = a[i + 1]; a[i + 1] = -a[i + 2]; a[i + 2] = y; } };
        sw(p); if (n) sw(n);
      }
      parts.push({ positions: p, normals: n || computeNormals(p, idx), indices: idx });
    }));
    if (!parts.length) throw new Error("no triangle mesh in this .glb");
    const mesh = merge(parts, (doc.meshes[0] && doc.meshes[0].name) || "mesh");
    const node = (doc.nodes || []).find(x => x.mesh === 0) || {};
    mesh.unitScale = ours ? 0.001 : ((node.scale && node.scale[0]) || 1);
    let material = null;
    const mj = doc.materials && doc.materials[0], pbr = mj && mj.pbrMetallicRoughness;
    if (pbr) material = { base: (pbr.baseColorFactor || [1, 1, 1]).slice(0, 3), rough: pbr.roughnessFactor ?? 1, metal: pbr.metallicFactor ?? 1,
      name: mj.name || "file material", notes: (mj.extras && mj.extras.opengonio && mj.extras.opengonio.notes) || [] };
    return { mesh, material };
  }

  function parsePLY(buf) {
    const bytes = new Uint8Array(buf), head = new TextDecoder().decode(bytes.subarray(0, Math.min(bytes.length, 4096)));
    const end = head.indexOf("end_header");
    if (!head.startsWith("ply") || end < 0) throw new Error("not a PLY file");
    const lines = head.slice(0, end).split(/\r?\n/), fmt = (lines.find(l => l.startsWith("format")) || "").split(/\s+/)[1];
    const els = [];
    lines.forEach(l => { const w = l.trim().split(/\s+/);
      if (w[0] === "element") els.push({ name: w[1], count: +w[2], props: [] });
      else if (w[0] === "property") els[els.length - 1].props.push(w[1] === "list" ? { list: true, ct: w[2], t: w[3], name: w[4] } : { t: w[1], name: w[2] }); });
    const vEl = els.find(e => e.name === "vertex"), fEl = els.find(e => e.name === "face");
    if (!vEl) throw new Error("PLY without vertices");
    if (!fEl || !fEl.count) throw new Error("PLY has no faces (a point cloud, like hull.ply): open hull_mesh.ply or hull.glb");
    const P = new Float32Array(vEl.count * 3), N = new Float32Array(vEl.count * 3), I = [];
    const vi = k => vEl.props.findIndex(p => p.name === k), hasN = vi("nx") >= 0;
    let start = head.indexOf("\n", end) + 1;
    if (fmt === "ascii") {
      const rows = new TextDecoder().decode(bytes.subarray(start)).split(/\r?\n/);
      let r = 0;
      for (const e of els) for (let i = 0; i < e.count; i++, r++) {
        const w = rows[r].trim().split(/\s+/).map(Number);
        if (e === vEl) { ["x", "y", "z"].forEach((k, c) => P[i * 3 + c] = w[vi(k)]); if (hasN) ["nx", "ny", "nz"].forEach((k, c) => N[i * 3 + c] = w[vi(k)]); }
        else if (e === fEl) { const n = w[0]; for (let k = 2; k < n; k++) I.push(w[1], w[k], w[k + 1]); }
      }
    } else if (fmt === "binary_little_endian") {
      const dv = new DataView(buf), SZ = { char: 1, uchar: 1, int8: 1, uint8: 1, short: 2, ushort: 2, int16: 2, uint16: 2, int: 4, uint: 4, int32: 4, uint32: 4, float: 4, float32: 4, double: 8, float64: 8 };
      const get = (t, o) => ({ char: dv.getInt8(o), int8: dv.getInt8(o), uchar: dv.getUint8(o), uint8: dv.getUint8(o), short: 0, ushort: 0 })[t] ??
        (/^(short|int16)$/.test(t) ? dv.getInt16(o, true) : /^(ushort|uint16)$/.test(t) ? dv.getUint16(o, true) : /^(int|int32)$/.test(t) ? dv.getInt32(o, true)
          : /^(uint|uint32)$/.test(t) ? dv.getUint32(o, true) : /^(float|float32)$/.test(t) ? dv.getFloat32(o, true) : dv.getFloat64(o, true));
      let o = start;
      for (const e of els) for (let i = 0; i < e.count; i++) for (const p of e.props) {
        if (p.list) { const n = get(p.ct, o); o += SZ[p.ct]; const ids = []; for (let k = 0; k < n; k++) { ids.push(get(p.t, o)); o += SZ[p.t]; }
          if (e === fEl) for (let k = 1; k + 1 < n; k++) I.push(ids[0], ids[k], ids[k + 1]); }
        else { const v = get(p.t, o); o += SZ[p.t];
          if (e === vEl) { const c = ["x", "y", "z"].indexOf(p.name), cn = ["nx", "ny", "nz"].indexOf(p.name); if (c >= 0) P[i * 3 + c] = v; if (cn >= 0) N[i * 3 + cn] = v; } }
      }
    } else throw new Error(`PLY format ${fmt} is not read here (ascii or binary_little_endian)`);
    const idx = new Uint32Array(I);
    return { positions: P, normals: hasN ? N : computeNormals(P, idx), indices: idx, name: "ply_mesh", unitScale: 0.001 };
  }

  function glb(mesh, mat, extras) {             /* same layout as opengonio/render/gltf.py: mm, Z-up, node scale + rotation */
    const pad = (n, m = 4) => (m - n % m) % m;
    const pos = mesh.positions, nrm = mesh.normals, idx = mesh.indices instanceof Uint32Array ? mesh.indices : Uint32Array.from(mesh.indices);
    const mn = [Infinity, Infinity, Infinity], mx = [-Infinity, -Infinity, -Infinity];
    for (let i = 0; i < pos.length; i += 3) for (let c = 0; c < 3; c++) { mn[c] = Math.min(mn[c], pos[i + c]); mx[c] = Math.max(mx[c], pos[i + c]); }
    const blobs = [new Uint8Array(pos.buffer, pos.byteOffset, pos.byteLength), new Uint8Array(nrm.buffer, nrm.byteOffset, nrm.byteLength),
      new Uint8Array(idx.buffer, idx.byteOffset, idx.byteLength)];
    let off = 0; const views = blobs.map((b, k) => { const v = { buffer: 0, byteOffset: off, byteLength: b.length, target: k < 2 ? 34962 : 34963 }; off += b.length + pad(b.length); return v; });
    const s = mesh.unitScale || 0.001, q = Math.SQRT1_2;
    const doc = { asset: { version: "2.0", generator: "opengonio.render", ...(extras ? { extras } : {}) }, scene: 0, scenes: [{ nodes: [0] }],
      nodes: [{ name: mesh.name || "mesh", mesh: 0, rotation: [-q, 0, 0, q], scale: [s, s, s] }],
      meshes: [{ name: mesh.name || "mesh", primitives: [{ attributes: { POSITION: 0, NORMAL: 1 }, indices: 2, material: 0, mode: 4 }] }],
      materials: [{ name: mat.name || "opengonio_material", doubleSided: false,
        pbrMetallicRoughness: { baseColorFactor: [...mat.base.map(Number), 1], metallicFactor: +mat.metal, roughnessFactor: +mat.rough },
        extras: { opengonio: { source: mat.source || "viewer", notes: mat.notes || [], model: "Lambert + GGX, metallic-roughness, F0 dielectric 0.04" } } }],
      accessors: [{ bufferView: 0, componentType: 5126, count: pos.length / 3, type: "VEC3", min: mn, max: mx },
        { bufferView: 1, componentType: 5126, count: nrm.length / 3, type: "VEC3" }, { bufferView: 2, componentType: 5125, count: idx.length, type: "SCALAR" }],
      bufferViews: views, buffers: [{ byteLength: off }] };
    let js = new TextEncoder().encode(JSON.stringify(doc)); const jpad = pad(js.length);
    const total = 12 + 8 + js.length + jpad + 8 + off, out = new Uint8Array(total), dv = new DataView(out.buffer);
    dv.setUint32(0, 0x46546C67, true); dv.setUint32(4, 2, true); dv.setUint32(8, total, true);
    dv.setUint32(12, js.length + jpad, true); dv.setUint32(16, 0x4E4F534A, true); out.set(js, 20); out.fill(0x20, 20 + js.length, 20 + js.length + jpad);
    let o = 20 + js.length + jpad; dv.setUint32(o, off, true); dv.setUint32(o + 4, 0x004E4942, true); o += 8;
    blobs.forEach((b, k) => out.set(b, o + views[k].byteOffset));
    return out;
  }

  function engines(m) {
    const c = m.base.map(v => +(+v).toFixed(3)), r = +(+m.rough).toFixed(3), mt = +(+m.metal).toFixed(3);
    return { "glTF / Blender Principled BSDF": { "Base Color": c, Roughness: r, Metallic: mt },
      Unreal: { BaseColor: c, Roughness: r, Metallic: mt, Specular: 0.5 },
      "Unity (URP Lit, metallic)": { "Base Map": c, Smoothness: +(1 - r).toFixed(3), Metallic: mt },
      "three.js MeshStandardMaterial": { color: c, roughness: r, metalness: mt } };
  }

  /* ---------------- shaders ---------------- */
  const VS = `#version 300 es
in vec3 aPos; in vec3 aNrm;
uniform mat4 uVP, uLVP;
out vec3 vPos; out vec3 vNrm; out vec4 vL;
void main() { vPos = aPos; vNrm = aNrm; vL = uLVP * vec4(aPos, 1.0); gl_Position = uVP * vec4(aPos, 1.0); }`;
  const FS = `#version 300 es
precision highp float; precision highp sampler2DShadow;
in vec3 vPos; in vec3 vNrm; in vec4 vL;
uniform vec3 uEye, uL, uBase, uC; uniform float uRough, uMetal, uE, uSky, uExp, uFade, uShadowOn; uniform int uGround;
uniform sampler2DShadow uShadow;
out vec4 o;
const float PI = 3.14159265;
const vec3 BOX = vec3(1.0, 0.97, 0.92), SIDE = vec3(-0.5717, -0.7146, 0.4033);   // a studio: overhead and side softboxes
vec3 grad(vec3 d) { return mix(vec3(0.10, 0.09, 0.08), vec3(0.32, 0.34, 0.38), clamp(0.5 + 0.5 * d.z, 0.0, 1.0)); }
vec3 skyRad(vec3 d) { return grad(d) + BOX * (2.4 * smoothstep(0.86, 0.9, d.z) + 1.4 * smoothstep(0.93, 0.96, dot(d, SIDE))); }
vec3 skyIrr(vec3 n) { return grad(n) + BOX * (0.3 * pow(max(n.z, 0.0), 2.0) + 0.1 * pow(max(dot(n, SIDE), 0.0), 2.0)); }
vec3 brdf(vec3 n, vec3 l, vec3 v) {                      // fit.py's ggx(), world space
  float ci = dot(n, l), co = dot(n, v);
  if (ci <= 0.0 || co <= 0.0) return vec3(0.0);
  vec3 h = normalize(l + v); float a = max(uRough * uRough, 1e-4), a2 = a * a, ch = dot(n, h);
  float d = a2 / (PI * pow(ch * ch * (a2 - 1.0) + 1.0, 2.0));
  float g = 2.0 * ci * co / (co * sqrt(ci * ci * (1.0 - a2) + a2) + ci * sqrt(co * co * (1.0 - a2) + a2));
  vec3 f0 = mix(vec3(0.04), uBase, uMetal), F = f0 + (1.0 - f0) * pow(1.0 - clamp(dot(l, h), 0.0, 1.0), 5.0);
  return d * g * F / (4.0 * ci * co) + (1.0 - uMetal) * (1.0 - F) * uBase / PI;
}
vec2 envBRDF(float r, float nv) { vec4 q = r * vec4(-1.0, -0.0275, -0.572, 0.022) + vec4(1.0, 0.0425, 1.04, -0.04);
  float a = min(q.x * q.x, exp2(-9.28 * nv)) * q.x + q.y; return vec2(-1.04, 1.04) * a + q.zw; }
vec3 aces(vec3 x) { return clamp(x * (2.51 * x + 0.03) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
vec3 srgb(vec3 c) { return mix(12.92 * c, 1.055 * pow(max(c, 0.0), vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }
float shade() {
  if (uShadowOn < 0.5) return 1.0;
  vec3 p = vL.xyz / vL.w * 0.5 + 0.5;
  if (any(lessThan(p, vec3(0.0))) || any(greaterThan(p, vec3(1.0)))) return 1.0;
  vec2 t = 1.0 / vec2(textureSize(uShadow, 0)); float s = 0.0;
  for (int i = -1; i <= 1; i++) for (int j = -1; j <= 1; j++) s += texture(uShadow, vec3(p.xy + vec2(i, j) * t * 1.5, p.z - 0.002));
  return s / 9.0;
}
void main() {
  vec3 n = normalize(vNrm), v = normalize(uEye - vPos);
  if (dot(n, v) < 0.0) n = normalize(n - 2.0 * dot(n, v) * v);
  float nl = max(dot(n, uL), 0.0), nv = clamp(dot(n, v), 1e-4, 1.0);
  vec3 lamp = brdf(n, uL, v) * uE * nl * shade();
  vec3 f0 = mix(vec3(0.04), uBase, uMetal); vec2 ab = envBRDF(uRough, nv); vec3 sp = f0 * ab.x + ab.y;
  vec3 r = 2.0 * nv * n - v;
  vec3 amb = (1.0 - uMetal) * uBase * skyIrr(n) * (1.0 - sp) + mix(skyRad(r), skyIrr(n), uRough) * sp;
  vec3 c = srgb(aces((lamp + uSky * amb) * uExp));
  float al = 1.0;
  if (uGround == 1) { float d = length(vPos.xy - uC.xy) / uFade; al = clamp(1.0 - d * d, 0.0, 1.0) * 0.92; }
  o = vec4(c * al, al);
}`;
  const DVS = `#version 300 es
in vec3 aPos; uniform mat4 uLVP; void main() { gl_Position = uLVP * vec4(aPos, 1.0); }`;
  const DFS = `#version 300 es
precision mediump float; out vec4 o; void main() { o = vec4(1.0); }`;
  const PVS = `#version 300 es
in vec3 aPos; uniform mat4 uVP; uniform float uSize; void main() { gl_Position = uVP * vec4(aPos, 1.0); gl_PointSize = uSize; }`;
  const PFS = `#version 300 es
precision mediump float; uniform vec4 uCol; out vec4 o;
void main() { vec2 d = gl_PointCoord - 0.5; if (dot(d, d) > 0.25) discard; o = vec4(uCol.rgb * uCol.a, uCol.a); }`;

  function program(gl, vs, fs) {
    const mk = (t, s) => { const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh);
      if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(sh)); return sh; };
    const p = gl.createProgram(); gl.attachShader(p, mk(gl.VERTEX_SHADER, vs)); gl.attachShader(p, mk(gl.FRAGMENT_SHADER, fs));
    gl.bindAttribLocation(p, 0, "aPos"); gl.bindAttribLocation(p, 1, "aNrm"); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    const u = {}; const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (let i = 0; i < n; i++) { const a = gl.getActiveUniform(p, i); u[a.name] = gl.getUniformLocation(p, a.name); }
    return { p, u };
  }

  /* ---------------- viewer ---------------- */
  function create(canvas, opts = {}) {
    const gl = canvas.getContext("webgl2", { antialias: true, premultipliedAlpha: true, alpha: true, preserveDrawingBuffer: true });
    if (!gl) return null;
    const S = { camAz: -55, camEl: 22, zoom: 1, lampAz: 35, lampEl: 40, exposure: 1, sky: 1, lampE: 2.6, shadows: true, ground: true,
      turntable: false, dirs: null, ...opts.state };
    let mat = { base: [0.5, 0.5, 0.5], rough: 0.5, metal: 0 }, mesh = null, geo = null, ground = null, dirsBuf = null, dirty = true, raf = 0, last = 0;
    let center = [0, 0, 0], radius = 1, zmin = 0;
    const main = program(gl, VS, FS), depth = program(gl, DVS, DFS), pts = program(gl, PVS, PFS);
    const SM = 2048, smTex = gl.createTexture(), smFb = gl.createFramebuffer(), lampBuf = gl.createBuffer();
    gl.bindTexture(gl.TEXTURE_2D, smTex);
    gl.texStorage2D(gl.TEXTURE_2D, 1, gl.DEPTH_COMPONENT24, SM, SM);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_COMPARE_MODE, gl.COMPARE_REF_TO_TEXTURE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_COMPARE_FUNC, gl.LEQUAL);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.bindFramebuffer(gl.FRAMEBUFFER, smFb); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.TEXTURE_2D, smTex, 0);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);

    function upload(m) {
      const vao = gl.createVertexArray(); gl.bindVertexArray(vao);
      const b = (data, loc) => { const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
        gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 3, gl.FLOAT, false, 0, 0); return buf; };
      const bufs = [b(m.positions, 0), b(m.normals, 1)], ib = gl.createBuffer();
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, m.indices, gl.STATIC_DRAW);
      gl.bindVertexArray(null);
      return { vao, n: m.indices.length, free() { gl.deleteVertexArray(vao); bufs.forEach(x => gl.deleteBuffer(x)); gl.deleteBuffer(ib); } };
    }
    function setMesh(m) {
      mesh = m; if (geo) geo.free(); if (ground) ground.free();
      const p = m.positions, mn = [Infinity, Infinity, Infinity], mx = [-Infinity, -Infinity, -Infinity];
      for (let i = 0; i < p.length; i += 3) for (let c = 0; c < 3; c++) { mn[c] = Math.min(mn[c], p[i + c]); mx[c] = Math.max(mx[c], p[i + c]); }
      center = [(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, (mn[2] + mx[2]) / 2]; zmin = mn[2]; radius = 0;
      for (let i = 0; i < p.length; i += 3) radius = Math.max(radius, Math.hypot(p[i] - center[0], p[i + 1] - center[1], p[i + 2] - center[2]));
      geo = upload(m);
      const g = 6 * radius, z = zmin - 0.002 * radius;
      ground = upload({ positions: new Float32Array([center[0] - g, center[1] - g, z, center[0] + g, center[1] - g, z, center[0] + g, center[1] + g, z, center[0] - g, center[1] + g, z]),
        normals: new Float32Array([0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]), indices: new Uint32Array([0, 1, 2, 0, 2, 3]) });
      setDirs(S.dirs); dirty = true;
      return { triangles: m.indices.length / 3, radius_mm: radius * (m.unitScale || 0.001) * 1000 };
    }
    function setDirs(list) {                     /* measurement directions: [[az, el, kind], ...] on a hemisphere over the object */
      S.dirs = list; if (dirsBuf) { gl.deleteBuffer(dirsBuf.buf); dirsBuf = null; }
      if (!list || !list.length || !mesh) { dirty = true; return; }
      const a = new Float32Array(list.length * 3), R = 1.3 * radius, top = [center[0], center[1], zmin];
      list.forEach((d, i) => { const v = sph(d[0], d[1]); a.set([top[0] + R * v[0], top[1] + R * v[1], top[2] + R * v[2]], i * 3); });
      const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, a, gl.STATIC_DRAW);
      dirsBuf = { buf, kinds: list.map(d => d[2]) }; dirty = true;
    }
    function matrices() {
      const w = canvas.width, h = canvas.height, fov = rad(28), dist = 1.12 * radius / Math.sin(fov / 2) / S.zoom;
      const eye = sph(S.camAz, S.camEl).map((v, i) => center[i] + dist * v);
      const VP = M.mul(M.persp(fov, w / h, dist * 0.05, dist * 4 + radius * 8), M.look(eye, center, [0, 0, 1]));
      const L = sph(S.lampAz, S.lampEl), le = L.map((v, i) => center[i] + 4 * radius * v);
      const up = Math.abs(L[2]) > 0.98 ? [0, 1, 0] : [0, 0, 1];
      const LVP = M.mul(M.ortho(2.2 * radius, 0.5 * radius, 9 * radius), M.look(le, center, up));
      return { VP, LVP, eye, L };
    }
    function draw() {
      if (!geo) return;
      const { VP, LVP, eye, L } = matrices();
      if (S.shadows) {
        gl.bindFramebuffer(gl.FRAMEBUFFER, smFb); gl.viewport(0, 0, SM, SM); gl.clear(gl.DEPTH_BUFFER_BIT);
        gl.enable(gl.DEPTH_TEST); gl.useProgram(depth.p); gl.uniformMatrix4fv(depth.u.uLVP, false, LVP);
        gl.enable(gl.POLYGON_OFFSET_FILL); gl.polygonOffset(2, 4);
        gl.bindVertexArray(geo.vao); gl.drawElements(gl.TRIANGLES, geo.n, gl.UNSIGNED_INT, 0);
        gl.disable(gl.POLYGON_OFFSET_FILL); gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      }
      gl.viewport(0, 0, canvas.width, canvas.height); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.enable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
      const u = main.u; gl.useProgram(main.p);
      gl.uniformMatrix4fv(u.uVP, false, VP); gl.uniformMatrix4fv(u.uLVP, false, LVP);
      gl.uniform3fv(u.uEye, eye); gl.uniform3fv(u.uL, L); gl.uniform3fv(u.uC, center);
      gl.uniform1f(u.uE, S.lampE); gl.uniform1f(u.uSky, S.sky); gl.uniform1f(u.uExp, S.exposure); gl.uniform1f(u.uFade, 4.5 * radius);
      gl.uniform1f(u.uShadowOn, S.shadows ? 1 : 0);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, smTex); gl.uniform1i(u.uShadow, 0);
      if (S.ground) {
        gl.uniform1i(u.uGround, 1); gl.uniform3fv(u.uBase, [0.18, 0.18, 0.18]); gl.uniform1f(u.uRough, 0.85); gl.uniform1f(u.uMetal, 0);
        gl.depthMask(false); gl.bindVertexArray(ground.vao); gl.drawElements(gl.TRIANGLES, ground.n, gl.UNSIGNED_INT, 0); gl.depthMask(true);
      }
      gl.uniform1i(u.uGround, 0); gl.uniform3fv(u.uBase, mat.base); gl.uniform1f(u.uRough, mat.rough); gl.uniform1f(u.uMetal, mat.metal);
      gl.bindVertexArray(geo.vao); gl.drawElements(gl.TRIANGLES, geo.n, gl.UNSIGNED_INT, 0);   // no culling: files from other tools may wind either way
      gl.bindVertexArray(null);
      if (dirsBuf) {
        gl.useProgram(pts.p); gl.uniformMatrix4fv(pts.u.uVP, false, VP); gl.uniform1f(pts.u.uSize, 7 * Math.min(devicePixelRatio || 1, 2));
        gl.bindBuffer(gl.ARRAY_BUFFER, dirsBuf.buf); gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
        const cols = { lamp: [1.0, 0.79, 0.47, 1], camera: [0.53, 0.64, 0.88, 1] };
        let i = 0; while (i < dirsBuf.kinds.length) { let j = i; while (j < dirsBuf.kinds.length && dirsBuf.kinds[j] === dirsBuf.kinds[i]) j++;
          gl.uniform4fv(pts.u.uCol, cols[dirsBuf.kinds[i]] || [1, 1, 1, 1]); gl.drawArrays(gl.POINTS, i, j - i); i = j; }
        const le = L.map((v, k) => center[k] + 1.45 * radius * v);           // the lamp itself
        gl.bindBuffer(gl.ARRAY_BUFFER, lampBuf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(le), gl.DYNAMIC_DRAW);
        gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0); gl.uniform1f(pts.u.uSize, 16 * Math.min(devicePixelRatio || 1, 2));
        gl.uniform4fv(pts.u.uCol, [1.0, 0.88, 0.6, 1]); gl.drawArrays(gl.POINTS, 0, 1);
      }
    }
    function resize() {
      const dpr = Math.min(devicePixelRatio || 1, 2), w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
      if (w && h && (canvas.width !== w || canvas.height !== h)) { canvas.width = w; canvas.height = h; dirty = true; }
    }
    function loop(t) {
      raf = requestAnimationFrame(loop); resize();
      if (S.turntable) { S.camAz += (last ? (t - last) : 16) * 0.012; dirty = true; } last = t;
      if (dirty) { dirty = false; draw(); if (opts.onDraw) opts.onDraw(S); }
    }
    raf = requestAnimationFrame(loop);
    /* orbit: drag; Shift+drag moves the lamp; wheel or pinch zooms; arrow keys orbit, +/- zoom, 0 resets */
    let drag = null; const pointers = new Map();
    canvas.addEventListener("pointerdown", e => { canvas.setPointerCapture(e.pointerId); pointers.set(e.pointerId, [e.clientX, e.clientY]);
      drag = { x: e.clientX, y: e.clientY, lamp: e.shiftKey || opts.dragLamp?.() }; });
    canvas.addEventListener("pointermove", e => {
      if (!pointers.has(e.pointerId)) return;
      const prev = pointers.get(e.pointerId); pointers.set(e.pointerId, [e.clientX, e.clientY]);
      if (pointers.size === 2) { const [a, b] = [...pointers.values()], other = [...pointers.entries()].find(([k]) => k !== e.pointerId)[1];
        const d0 = Math.hypot(prev[0] - other[0], prev[1] - other[1]), d1 = Math.hypot(a[0] - b[0], a[1] - b[1]);
        if (d0 > 0) set({ zoom: S.zoom * d1 / d0 }); return; }
      if (!drag) return;
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
      if (drag.lamp) set({ lampAz: S.lampAz - dx * 0.5, lampEl: S.lampEl + dy * 0.4 });
      else set({ camAz: S.camAz - dx * 0.4, camEl: S.camEl + dy * 0.3 });
    });
    const up = e => { pointers.delete(e.pointerId); if (!pointers.size) drag = null; };
    canvas.addEventListener("pointerup", up); canvas.addEventListener("pointercancel", up);
    canvas.addEventListener("wheel", e => { e.preventDefault(); set({ zoom: S.zoom * Math.exp(-e.deltaY * 0.0015) }); }, { passive: false });
    canvas.addEventListener("keydown", e => {
      const k = { ArrowLeft: { camAz: S.camAz + 5 }, ArrowRight: { camAz: S.camAz - 5 }, ArrowUp: { camEl: S.camEl + 4 }, ArrowDown: { camEl: S.camEl - 4 },
        "+": { zoom: S.zoom * 1.1 }, "=": { zoom: S.zoom * 1.1 }, "-": { zoom: S.zoom / 1.1 }, 0: { camAz: -55, camEl: 22, zoom: 1 } }[e.key];
      if (k) { e.preventDefault(); set(k); }
    });
    function set(p) {
      Object.assign(S, p);
      S.camEl = Math.max(-5, Math.min(85, S.camEl)); S.lampEl = Math.max(2, Math.min(88, S.lampEl)); S.zoom = Math.max(0.4, Math.min(4, S.zoom));
      dirty = true; if (opts.onChange) opts.onChange(S, p);
    }
    return {
      state: S, set, setMesh, setDirs,
      setMaterial(m) { mat = { ...mat, ...m, base: (m.base || mat.base).map(Number) }; dirty = true; },
      material: () => mat, mesh: () => mesh,
      png: () => canvas.toDataURL("image/png"),
      destroy() { cancelAnimationFrame(raf); },
    };
  }

  window.OGRender = { create, sphere, shaderBall, parseGLB, parsePLY, glb, engines, computeNormals,
    webgl2: () => { try { return !!document.createElement("canvas").getContext("webgl2"); } catch (e) { return false; } } };
})();
