/* docs/render.html: live viewer, measured-vs-fitted chart, scan numbers, engine table. Data: window.RENDER
   (docs/render-data.js, tools/render_assets.py). SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const D = window.RENDER, R = window.OGRender, $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const cap = s => s[0].toUpperCase() + s.slice(1);
  const NAMES = Object.keys(D.materials);
  let which = "fit", current = NAMES[0], custom = null, fileMesh = null, fileMat = null, tint = [1, 1, 1];

  /* ---------- materials ---------- */
  function preset(name, w) {
    if (name === "custom") return custom;
    if (name === "file") return fileMat;
    const m = D.materials[name][w];
    return { base: [m.base_color, m.base_color, m.base_color], rough: m.roughness, metal: m.metallic,
      name: `${name}_${w}`, source: w === "fit" ? `fit of simulated ${name} samples` : "simulated truth (sim.py)", notes: [] };
  }
  function fillMaterials() {
    const opts = NAMES.map(n => `<option value="${n}">${cap(n)}</option>`);
    if (custom) opts.push('<option value="custom">Your fit.json</option>');
    if (fileMat) opts.push('<option value="file">From the mesh file</option>');
    $("mat").innerHTML = opts.join(""); $("mat").value = current;
  }
  const active = () => preset(current, which);
  const tinted = m => ({ ...m, base: m.base.map((b, i) => +(b * tint[i]).toFixed(4)) });

  /* ---------- viewer ---------- */
  const canvas = $("gl");
  const viewer = R.webgl2() ? R.create(canvas, { onChange: syncLamp }) : null;
  if (!viewer) { $("nogl").hidden = false; canvas.hidden = true; }
  let meshes = { ball: R.shaderBall(), sphere: R.sphere(25) }, info = null;
  async function loadMug() {
    if (meshes.mug) return meshes.mug;
    const r = await fetch(D.mesh.mug); if (!r.ok) throw new Error("mug_hull.glb not found");
    meshes.mug = R.parseGLB(await r.arrayBuffer()).mesh; meshes.mug.name = "scanned_mug"; return meshes.mug;
  }
  async function setObject(v) {
    if (!viewer) return;
    try {
      const m = v === "file" ? fileMesh : v === "mug" ? await loadMug() : meshes[v];
      info = viewer.setMesh(m); status();
    } catch (e) { say(e.message); }
  }
  function dirs() {
    if (!$("dirs").checked || current === "custom" || current === "file") return null;
    const c = D.materials[current].curve, out = [];
    [...new Set(c.theta_i)].forEach(t => out.push([0, 90 - t, "lamp"]));
    [...new Set(c.theta_r)].forEach(t => out.push([180, 90 - t, "camera"]));
    return out;
  }
  function apply() {
    const m = active(); if (!m) return;
    ["base", "rough", "metal"].forEach(k => { const el = $(k), v = k === "base" ? m.base[0] : m[k]; el.value = v; el.nextElementSibling.textContent = (+v).toFixed(3); });
    const tm = tinted(m);
    if (viewer) { viewer.setMaterial(tm); viewer.setDirs(dirs()); }
    engines(tm); status(); drawChart();
  }
  function fromSliders() {
    const m = { base: [+$("base").value, +$("base").value, +$("base").value], rough: +$("rough").value, metal: +$("metal").value,
      name: "custom", source: "typed in the viewer", notes: [] };
    ["base", "rough", "metal"].forEach(k => $(k).nextElementSibling.textContent = (+$(k).value).toFixed(3));
    custom = m; if (current !== "custom") { current = "custom"; fillMaterials(); }
    const tm = tinted(m); if (viewer) { viewer.setMaterial(tm); viewer.setDirs(null); } engines(tm); status();
  }
  function status() {
    const m = active(); if (!m) return;
    const parts = [];
    if (info) parts.push(`${info.triangles.toLocaleString()} triangles · ${Math.round(2 * info.radius_mm)} mm across`);
    parts.push(esc(m.source || ""));
    (m.notes || []).forEach(n => parts.push(esc(n)));
    if (tint.some(t => t !== 1)) parts.push("tint typed by hand (the fit is grey)");
    $("vstat").innerHTML = parts.join(" · ");
    $("vstat").className = "status" + (current in D.materials ? " ok" : " spec");
  }
  function say(msg) { $("vstat").textContent = msg; $("vstat").className = "status bad"; }
  function syncLamp(S, p) {
    if (p && ("lampAz" in p || "lampEl" in p)) { $("lth").value = Math.round(90 - S.lampEl); $("laz").value = Math.round(((S.lampAz + 180) % 360 + 360) % 360 - 180); outs(); }
  }
  function outs() {
    $("lth").nextElementSibling.textContent = `${$("lth").value}°`; $("laz").nextElementSibling.textContent = `${$("laz").value}°`;
    $("exp").nextElementSibling.textContent = (+$("exp").value).toFixed(2); $("sky").nextElementSibling.textContent = (+$("sky").value).toFixed(2);
  }

  /* ---------- controls ---------- */
  fillMaterials();
  $("obj").addEventListener("change", e => setObject(e.target.value));
  $("mat").addEventListener("change", e => { current = e.target.value; apply(); });
  $("which").addEventListener("click", e => {
    const b = e.target.closest("[data-w]"); if (!b) return; which = b.dataset.w;
    [...$("which").children].forEach(x => x.setAttribute("aria-checked", String(x === b)));
    if (!(current in D.materials)) { current = NAMES[0]; fillMaterials(); }
    apply();
  });
  ["base", "rough", "metal"].forEach(k => $(k).addEventListener("input", fromSliders));
  $("tint").addEventListener("input", e => { const h = e.target.value; tint = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
    const m = active(); const tm = tinted(m); if (viewer) viewer.setMaterial(tm); engines(tm); status(); });
  const lamp = () => viewer && viewer.set({ lampEl: 90 - +$("lth").value, lampAz: +$("laz").value });
  $("lth").addEventListener("input", () => { outs(); lamp(); }); $("laz").addEventListener("input", () => { outs(); lamp(); });
  $("exp").addEventListener("input", () => { outs(); viewer && viewer.set({ exposure: +$("exp").value }); });
  $("sky").addEventListener("input", () => { outs(); viewer && viewer.set({ sky: +$("sky").value }); });
  $("dirs").addEventListener("change", () => viewer && viewer.setDirs(dirs()));
  $("shadows").addEventListener("change", e => viewer && viewer.set({ shadows: e.target.checked }));
  $("turn").addEventListener("change", e => viewer && viewer.set({ turntable: e.target.checked }));
  const save = (blob, name) => { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000); };
  $("dl-glb").addEventListener("click", () => {
    if (!viewer) return;
    const m = tinted(active()), mesh = viewer.mesh();
    save(new Blob([R.glb(mesh, m, { opengonio: { simulated: current in D.materials, viewer: "render.html" } })], { type: "model/gltf-binary" }),
      `${mesh.name || "object"}_${(m.name || "material").replace(/[^\w-]+/g, "_")}.glb`);
  });
  $("dl-png").addEventListener("click", () => viewer && fetch(viewer.png()).then(r => r.blob()).then(b => save(b, "opengonio_render.png")));

  /* ---------- your files ---------- */
  async function openFile(f) {
    const name = f.name.toLowerCase();
    try {
      if (name.endsWith(".json")) {
        const j = JSON.parse(await f.text());
        const b = Array.isArray(j.base_color) ? j.base_color : [j.base_color, j.base_color, j.base_color];
        if (b[0] == null || j.roughness == null || j.metallic == null) throw new Error("this JSON has no base_color / roughness / metallic: open a fit.json");
        const notes = [];
        if (j.provenance && j.provenance.relative_only) notes.push("fitted to relative values: base colour is not absolute");
        if (j.holdout) notes.push(`holdout RMS ${j.holdout.rms_pct_of_peak} % of peak`);
        custom = { base: b.map(Number), rough: +j.roughness, metal: +j.metallic, name: f.name.replace(/\.json$/i, ""), source: `your file: ${f.name}`, notes };
        current = "custom"; fillMaterials(); apply(); if (viewer) viewer.setDirs(null);
      } else if (name.endsWith(".glb") || name.endsWith(".ply")) {
        const buf = await f.arrayBuffer();
        const r = name.endsWith(".glb") ? R.parseGLB(buf) : { mesh: R.parsePLY(buf), material: null };
        fileMesh = r.mesh; fileMesh.name = f.name.replace(/\.(glb|ply)$/i, "");
        const o = $("obj").querySelector('option[value="file"]'); o.disabled = false; o.textContent = `Your mesh (${f.name})`;
        $("obj").value = "file"; await setObject("file");
        if (r.material) { fileMat = { ...r.material, source: `material in ${f.name}` }; current = "file"; fillMaterials(); apply(); }
      } else throw new Error("open fit.json, a .glb or a .ply");
    } catch (e) { say(`${f.name}: ${e.message}`); }
  }
  $("f-fit").addEventListener("change", e => e.target.files[0] && openFile(e.target.files[0]));
  $("f-mesh").addEventListener("change", e => e.target.files[0] && openFile(e.target.files[0]));
  const stage = $("stage");
  stage.addEventListener("dragover", e => { e.preventDefault(); $("drop").hidden = false; });
  stage.addEventListener("dragleave", () => { $("drop").hidden = true; });
  stage.addEventListener("drop", e => { e.preventDefault(); $("drop").hidden = true; [...e.dataTransfer.files].forEach(openFile); });

  /* ---------- engines ---------- */
  function engines(m) {
    const E = R.engines(m), fmt = v => Array.isArray(v) ? `(${v.join(", ")})` : v;
    $("eng").innerHTML = "<thead><tr><th>Tool</th><th>Field</th><th>Value</th></tr></thead><tbody>" +
      Object.entries(E).map(([tool, f]) => Object.entries(f).map(([k, v], i) =>
        `<tr>${i ? "<td></td>" : `<td><b>${esc(tool)}</b></td>`}<td>${esc(k)}</td><td class="num">${esc(fmt(v))}</td></tr>`).join("")).join("") + "</tbody>";
  }

  /* ---------- measured vs fitted ---------- */
  function ggx(ti, tr, b, r, mt) {                                  // fit.py ggx(), in-plane: phi_i 0, phi_r 180
    const wi = [Math.sin(ti), 0, Math.cos(ti)], wo = [-Math.sin(tr), 0, Math.cos(tr)], ci = wi[2], co = wo[2];
    if (ci <= 0 || co <= 0) return 0;
    let h = [wi[0] + wo[0], 0, wi[2] + wo[2]]; const l = Math.hypot(h[0], h[2]); h = [h[0] / l, 0, h[2] / l];
    const a = Math.max(r * r, 1e-4), a2 = a * a, ch = h[2], d = a2 / (Math.PI * (ch * ch * (a2 - 1) + 1) ** 2);
    const g = 2 * ci * co / (co * Math.sqrt(ci * ci * (1 - a2) + a2) + ci * Math.sqrt(co * co * (1 - a2) + a2));
    const f0 = 0.04 * (1 - mt) + b * mt, F = f0 + (1 - f0) * (1 - Math.max(0, Math.min(1, wi[0] * h[0] + wi[2] * h[2]))) ** 5;
    return d * g * F / (4 * ci * co) + (1 - mt) * (1 - F) * b / Math.PI;
  }
  function drawChart() {
    const name = current in D.materials ? current : NAMES[0], M = D.materials[name], c = M.curve, f = M.fit;
    const cv = $("chart"), dpr = Math.min(devicePixelRatio || 1, 2), W = cv.clientWidth || 900, H = Math.round(W * 0.51);
    cv.width = W * dpr; cv.height = H * dpr; cv.style.height = H + "px";
    const x = cv.getContext("2d"); x.setTransform(dpr, 0, 0, dpr, 0, 0);
    const T = window.OG ? OG.tokens() : { ink: "#eee", ink2: "#aaa", ink3: "#777", rule: "#333", g2: "#151412", light: "#ffc978", text: "sans-serif" };
    x.clearRect(0, 0, W, H);
    const L = 58, Rm = 16, Tm = 30, B = 40, pw = W - L - Rm, ph = H - Tm - B;
    const ys = c.f.filter(v => v > 0), lo = Math.floor(Math.log10(Math.min(...ys) * 0.8)), hi = Math.ceil(Math.log10(Math.max(...ys) * 1.3));
    const X = t => L + pw * t / 80, Y = v => Tm + ph * (1 - (Math.log10(Math.max(v, 10 ** lo)) - lo) / (hi - lo));
    x.font = `12px ${T.text}`; x.fillStyle = T.ink2; x.strokeStyle = T.rule; x.lineWidth = 1;
    for (let e = lo; e <= hi; e++) { x.beginPath(); x.moveTo(L, Y(10 ** e)); x.lineTo(W - Rm, Y(10 ** e)); x.stroke(); x.textAlign = "right"; x.fillText(`10${e < 0 ? "⁻" : ""}${String(Math.abs(e)).split("").map(d => "⁰¹²³⁴⁵⁶⁷⁸⁹"[d]).join("")}`, L - 8, Y(10 ** e) + 4); }
    for (let t = 0; t <= 80; t += 20) { x.textAlign = "center"; x.fillText(`${t}°`, X(t), H - B + 18); }
    x.textAlign = "left"; x.fillText("BRDF (1/sr), log", L, 16); x.textAlign = "right"; x.fillText("θr, in the plane of incidence", W - Rm, H - 6);
    const tis = [...new Set(c.theta_i)], cols = [T.theme === "light" ? T.lightText : T.light, T.blue || "#86a4e0", T.green || "#7fb276", T.red || "#e06a5a"];
    tis.forEach((ti, k) => {
      x.strokeStyle = cols[k % 4]; x.lineWidth = 2; x.beginPath();
      for (let s = 0; s <= 160; s++) { const tr = 80 * s / 160, v = ggx(ti * Math.PI / 180, tr * Math.PI / 180, f.base_color, f.roughness, f.metallic); s ? x.lineTo(X(tr), Y(v)) : x.moveTo(X(tr), Y(v)); }
      x.stroke(); x.fillStyle = cols[k % 4];
      c.theta_i.forEach((t, i) => { if (t === ti) { x.beginPath(); x.arc(X(c.theta_r[i]), Y(c.f[i]), 3.2, 0, 2 * Math.PI); x.fill(); } });
      x.textAlign = "left"; x.fillText(`θi ${ti}°`, L + 8 + k * 70, Tm + 14);
    });
    x.fillStyle = T.ink; x.textAlign = "right"; x.fillText(`${cap(name)}: fit RMS ${M.rms_pct_of_peak} % of peak`, W - Rm, Tm + 14);
  }
  function fitTable() {
    const r = (a, b) => `${a} <span class="dim">→ ${b}</span>`;
    $("fit-table").insertAdjacentHTML("beforeend", "<thead><tr><th>Material</th><th>Base colour</th><th>Roughness</th><th>Metallic</th><th>RMS</th><th>Holdout</th></tr></thead><tbody>" +
      NAMES.map(n => { const m = D.materials[n]; return `<tr data-m="${n}"><td><button type="button" class="linkish" data-m="${n}">${cap(n)}</button></td>` +
        `<td class="num">${r(m.truth.base_color, m.fit.base_color)}</td><td class="num">${r(m.truth.roughness, m.fit.roughness)}</td>` +
        `<td class="num">${r(m.truth.metallic, m.fit.metallic)}</td><td class="num">${m.rms_pct_of_peak} %</td><td class="num">${m.holdout_rms_pct_of_peak ?? "–"} %</td></tr>`; }).join("") +
      "</tbody>");
    $("fit-table").insertAdjacentHTML("beforeend", '<tfoot><tr><td colspan="6" class="small dim">truth → fit</td></tr></tfoot>');
    $("fit-table").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (!b) return; current = b.dataset.m; fillMaterials(); apply(); });
  }

  /* ---------- scan + pictures ---------- */
  function scanBlock() {
    const s = D.scan;
    $("scan-read").innerHTML = [["Views", s.views], ["Image", `${s.image_px[0]} × ${s.image_px[1]} px`], ["Voxel", `${s.voxel_mm} mm`],
      ["Triangles", s.triangles.toLocaleString()], ["Hull volume", `${s.hull_volume_cm3} cm³`], ["True volume", `${s.true_volume_cm3} cm³`]]
      .map(([k, v]) => `<div><small>${k}</small><span>${v}</span></div>`).join("");
    $("scan-why").textContent = `The hull is ${(s.hull_volume_cm3 / s.true_volume_cm3).toFixed(1)}× the mug: ${s.why_larger}.`;
    $("vol").textContent = `${s.hull_volume_cm3} cm³ against ${s.true_volume_cm3} cm³ here`;
    $("balls").innerHTML = ["truth", "fit"].map(w => NAMES.map(n => `<figure><img src="assets/render/ball_${n}_${w}.png" width="300" height="300" loading="lazy"
      alt="${cap(n)} on a shader ball, ${w === "fit" ? "fitted values" : "simulated truth"}, software renderer."><figcaption>${cap(n)} · ${w === "fit" ? "fit" : "truth"}</figcaption></figure>`).join("")).join("");
  }

  outs(); fitTable(); scanBlock();
  setObject("ball").then(apply);
  if (!viewer) apply();
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawChart, 120); });
  window.addEventListener("og:theme", drawChart);
})();
