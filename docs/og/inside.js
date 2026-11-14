/* docs/inside.html: renders window.INSIDE (docs/inside-data.js, written by tools/inside_data.py from the sources).
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const D = window.INSIDE;
  if (!D) return;
  const $ = id => document.getElementById(id);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const md = s => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");
  const src = (path, line) => `${D.repo}${path}${line ? "#L" + line : ""}`;
  const short = m => m.replace(/^opengonio\./, "");
  const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;

  /* ---------- numbers ---------- */
  const steps = D.roadmap.stages.flatMap(s => s.milestones.flatMap(m => m.steps));
  const benchChecks = steps.reduce((a, s) => a + s.verify.length, 0);
  const nCases = D.tests.reduce((a, t) => a + t.cases.length, 0);
  const pyLines = D.modules.reduce((a, m) => a + m.lines, 0);
  const wires = D.wiring.filter(g => !g.blocked).reduce((a, g) => a + g.wires, 0);
  const stats = [
    [D.modules.length, "Python modules", "#software"], [pyLines.toLocaleString(), "lines of Python", "#software"],
    [nCases, "automated tests", "#tests"], [D.tools.length, "build and check tools", "#tools"],
    [D.hub.commands.length, "hub commands", "#firmware"], [wires, "wires, each one drawn", "#wiring"],
    [D.roadmap.stages.length, "stages", "#roadmap"], [benchChecks, "bench checks to pass", "#roadmap"],
  ];
  $("stats").innerHTML = stats.map(([n, w, h]) => `<a class="in-stat" href="${h}" style="text-decoration:none;color:inherit"><b>${n}</b><span>${w}</span></a>`).join("");

  /* ---------- software ---------- */
  const GROUPS = { core: "Core: runs, calibration, fitting", gantry: "Machine control", plans: "Measurement plans", brdf: "Reflectance models",
                   camera: "Camera", hdr: "High dynamic range", scan: "3D scanning", render: "Rendering", app: "Control app" };
  const usedBy = {};
  D.modules.forEach(m => m.imports.forEach(i => (usedBy[i] = usedBy[i] || []).push(m.module)));
  const testedBy = {};
  D.tests.forEach(t => t.covers.forEach(c => (testedBy[c] = testedBy[c] || []).push(t.file.split("/").pop())));
  let group = "all", query = "";
  const groups = ["all", ...Object.keys(GROUPS).filter(g => D.modules.some(m => m.group === g))];
  $("sw-groups").innerHTML = groups.map(g => `<button type="button" class="in-chip" data-g="${g}" aria-pressed="${g === "all"}">${g === "all" ? "All" : esc(GROUPS[g])}</button>`).join("");
  $("sw-groups").addEventListener("click", e => {
    const b = e.target.closest("button[data-g]"); if (!b) return;
    group = b.dataset.g;
    [...$("sw-groups").children].forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    drawModules();
  });
  $("sw-search").addEventListener("input", e => { query = e.target.value.trim().toLowerCase(); drawModules(); });
  const chips = (list, cls = "") => list.length ? list.map(x => `<span class="in-chip ${cls}">${esc(x)}</span>`).join("") : '<span class="in-note">none</span>';
  function moduleCard(m) {
    const tb = testedBy[m.module] || [];
    return `<details class="in-item" id="mod-${esc(m.module)}"><summary>
      <span class="t">${esc(short(m.module))}</span>
      <span class="s">${md(m.summary)}</span>
      <span class="m">${m.lines} lines · ${plural(m.names.length, "public name")} · ${tb.length ? "tested by " + plural(tb.length, "test file") : "no direct test file"}</span>
      </summary><div>
      <p>${md(m.doc)}</p>
      ${m.names.length ? `<ul class="in-list">${m.names.map(n => `<li><a href="${src(m.path, n.line)}"><code>${esc(n.name)}</code></a> <span class="in-note">${n.kind}</span>${n.doc ? " · " + md(n.doc) : ""}</li>`).join("")}</ul>` : ""}
      <p class="in-note">Uses: ${chips(m.imports.map(short))}</p>
      <p class="in-note">Used by: ${chips((usedBy[m.module] || []).map(short))}</p>
      <p class="in-note">Tested by: ${chips(tb, "ok")}</p>
      <p><a href="${src(m.path)}">Read ${esc(m.path)} on GitHub</a></p>
      </div></details>`;
  }
  function drawModules() {
    const list = D.modules.filter(m => (group === "all" || m.group === group) &&
      (!query || (m.module + " " + m.doc + " " + m.names.map(n => n.name).join(" ")).toLowerCase().includes(query)));
    $("sw-list").innerHTML = list.length ? list.map(moduleCard).join("") : '<p class="in-note">No module matches.</p>';
    $("sw-count").textContent = `${list.length} of ${D.modules.length} modules`;
  }
  drawModules();
  $("tool-list").innerHTML = D.tools.map(t => `<li><a href="${src(t.path)}"><code>${esc(t.path)}</code></a>
    ${t.in_build ? '<span class="in-chip ok">runs in make build</span>' : ""} ${md(t.doc)}</li>`).join("");

  /* ---------- tests ---------- */
  $("t-sum").textContent = `${plural(D.tests.length, "test file")}, ${nCases} test functions (some run once per material or setting).`;
  $("t-list").innerHTML = D.tests.map(t => `<details class="in-item"><summary>
      <span class="t">${esc(t.file.split("/").pop())}</span><span class="s">${md(t.doc)}</span>
      <span class="m">${plural(t.cases.length, "test")} · checks ${plural(t.covers.length + t.tools.length, "file")}</span></summary><div>
      <p class="in-note">Checks: ${chips([...t.covers.map(short), ...t.tools])}</p>
      <ol class="in-list">${t.cases.map(c => `<li><a href="${src(t.file, c.line)}">${esc(c.says)}</a>${c.doc ? ` <span class="in-note">· ${md(c.doc)}</span>` : ""}</li>`).join("")}</ol>
      <p><a href="${src(t.file)}">Read ${esc(t.file)} on GitHub</a></p></div></details>`).join("");
  $("bench-n").textContent = benchChecks;

  /* ---------- firmware ---------- */
  const g = D.grbl;
  $("grbl-axes").innerHTML = `<thead><tr><th>Axis</th><th>Motor</th>${g.columns.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>` +
    g.axes.map(a => `<tr><td class="in-k">${esc(a.axis)}</td><td>${esc(a.motor || "")}</td>${g.columns.map(c => `<td class="num">${esc(a[c] || "")}</td>`).join("")}</tr>`).join("") + "</tbody>";
  $("grbl-general").innerHTML = g.general.map(s => `<li><span class="in-k">${esc(s.set)}</span> ${md(s.note)}</li>`).join("");
  const h = D.hub;
  $("hub-meta").textContent = `${h.runtime} · ${h.lines} lines · keys debounced ${h.debounce_ms} ms`;
  $("hub-cmds").innerHTML = `<thead><tr><th>Laptop sends</th><th>The hub does</th></tr></thead><tbody>` +
    h.commands.map(c => `<tr><td class="in-k">${esc(c.cmd)}</td><td>${md(c.does)}</td></tr>`).join("") + "</tbody>";
  $("hub-events").innerHTML = `<thead><tr><th>Hub sends</th><th>When</th></tr></thead><tbody>` +
    h.events.map(c => `<tr><td class="in-k">${esc(c.line)}</td><td>${md(c.does)}</td></tr>`).join("") + "</tbody>";
  $("hub-pins").innerHTML = `<thead><tr><th>GPIO</th><th>Use</th></tr></thead><tbody>` +
    h.pins.map(p => `<tr class="${p.kind === "blocked" ? "in-kind-blocked" : ""}"><td class="num">${p.gpio}</td><td>${esc(p.use)}</td></tr>`).join("") + "</tbody>";
  $("hub-i2c").innerHTML = h.i2c.map(i => `<li><span class="in-k">${esc(i.addr)}</span> ${esc(i.part)}</li>`).join("");

  /* ---------- wiring ---------- */
  $("w-table").innerHTML = `<thead><tr><th>Section</th><th>Stage</th><th>Wires</th><th>Step by step</th></tr></thead><tbody>` +
    D.wiring.map(w => `<tr><td>${esc(w.title)}</td><td class="num">${esc(w.stage)}</td><td class="num">${w.blocked ? "blocked" : w.wires}</td>
      <td>${w.walk ? `<a href="${w.walk}">${esc(w.walk.replace(".html", ""))} walkthrough</a>` : w.blocked ? "do not wire" : '<a href="wiring.html">wiring guide</a>'}</td></tr>`).join("") + "</tbody>";

  /* ---------- roadmap ---------- */
  const R = D.roadmap;
  const ERAS = [["00", "Build the machine"], ["10", "Colour and 3D"], ["14", "Software, standalone and release"], ["17", "After release"]];
  $("r-sum").textContent = `${R.closed} of ${steps.length} steps closed on GitHub` + (R.updated ? ` (checked ${R.updated})` : "") +
    ". A step counts as done only when its issue is closed.";
  $("r-list").innerHTML = R.stages.map(s => {
    const n = s.folder.slice(0, 2), st = s.milestones.flatMap(m => m.steps), done = st.filter(x => x.done).length;
    const era = ERAS.find(e => e[0] === n);
    const pct = st.length ? Math.round(100 * done / st.length) : 0;
    return (era ? `<p class="in-era">${esc(era[1])}</p>` : "") + `<details class="in-item in-stage" id="stage-${n}"><summary>
      <span class="n">${n}</span>
      <span><span class="t">${esc(s.title)}</span><br><span class="m">${plural(s.milestones.length, "milestone")} · ${plural(st.length, "step")} · ${st.reduce((a, x) => a + x.verify.length, 0)} checks</span></span>
      <span class="p"><span class="in-bar" aria-hidden="true"><i style="width:${pct}%"></i></span><span class="m">${done}/${st.length} closed</span></span>
      </summary><div>
      ${s.milestones.map(m => `<div class="in-ms"><h4>${esc(m.id)} · ${esc(m.title)}${m.weeks ? ` <span class="in-note">· ${esc(m.weeks)} wk</span>` : ""}</h4>
        <p class="in-note">${md(m.goal)}</p>
        ${m.steps.map(x => `<div class="in-step"><b>${x.done ? '<span class="in-done">✓</span> ' : ""}${esc(x.id)} ${esc(x.title)}</b>${x.time ? ` <span class="in-note">· ${esc(x.time)}</span>` : ""}
          ${x.verify.length ? `<ul>${x.verify.map(v => `<li>${md(v)}</li>`).join("")}</ul>` : ""}</div>`).join("")}</div>`).join("")}
      <p><a href="${src(s.readme)}">Stage ${n} checklist on GitHub</a></p></div></details>`;
  }).join("");

  /* ---------- jump bar: mark the section in view ---------- */
  const links = [...document.querySelectorAll(".in-jump a")];
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) links.forEach(a => a.setAttribute("aria-current", String(a.getAttribute("href") === "#" + e.target.id)));
    }), { rootMargin: "-40% 0px -55% 0px" });
    document.querySelectorAll(".in-sec").forEach(s => io.observe(s));
  }
  const open = () => { const t = location.hash && document.querySelector(location.hash); if (t && t.tagName === "DETAILS") t.open = true; };
  window.addEventListener("hashchange", open); open();
})();
