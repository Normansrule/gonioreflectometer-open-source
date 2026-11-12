/* Bench walkthroughs (power.html, controller.html, machine.html): one wire at a time on a drawing of the parts as they sit on the bench.
   Steps come from window.WALK (og/walk-*.js); wire and note text from window.WIRING (docs/wiring-guide.js, generated
   from docs/wiring.yaml). SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const W = window.WIRING, WALK = window.WALK;
  if (!W || !WALK) return;
  const STEPS = WALK.steps;
  const NS = "http://www.w3.org/2000/svg";
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const COL = { red: "#c8372d", black: "#1c1b19", grey: "#9b9a95", blue: "#2f7fd6", violet: "#7b62c9", green: "#4f8a3c",
                amber: "#c98a1e", usb: "#8f8a82" };
  const rows = W.groups.flatMap(g => g.wires.filter(w => w.from && w.to));
  const find = s => rows.find(w => w.from.part === s.from[0] && w.from.pin === s.from[1] && w.to.part === s.to[0] && w.to.pin === s.to[1]);
  const wires = $("wires"), rings = $("rings");

  const drawn = STEPS.map(s => {
    if (s.type !== "wire") return null;
    const g = document.createElementNS(NS, "g");
    const halo = document.createElementNS(NS, "path"), p = document.createElementNS(NS, "path");
    halo.setAttribute("d", s.d); halo.setAttribute("class", "pw-halo");
    p.setAttribute("d", s.d); p.setAttribute("class", "pw-wire"); p.setAttribute("stroke", COL[s.colour] || COL.grey);
    if (s.dash) p.style.strokeDasharray = s.dash;
    g.append(halo, p); wires.append(g);
    return { g, p };
  });

  const pills = $("pills");
  STEPS.forEach((s, i) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "pw-pill num" + (s.type === "check" ? " ck" : "");
    b.textContent = s.type === "check" ? "✓" : i;
    b.setAttribute("aria-label", `Step ${i}: ${s.title}`);
    b.addEventListener("click", () => go(i));
    pills.append(b);
  });

  function lists(s) {
    let h = "";
    if (s.warn) h += `<p class="warn">${s.warn}</p>`;
    if (s.items) h += `<ul class="checks">${s.items.map(x => `<li>${x}</li>`).join("")}</ul>`;
    if (s.groups) {
      const checks = W.groups.filter(g => s.groups.some(p => g.title.startsWith(p))).flatMap(g => g.checks);
      h += `<ol class="checks">${checks.map(c => `<li>${c}</li>`).join("")}</ol>`;
    }
    if (s.cmd) h += `<pre class="pw-cmd"><code>${s.cmd.map(esc).join("\n")}</code></pre>`;
    if (s.pass) h += `<p class="pw-pass"><b>Pass:</b> ${esc(s.pass)}</p>`;
    return h;
  }
  function body(s) {
    if (s.type !== "wire") return lists(s);
    const w = find(s);
    return `<dl class="ends"><dt>From</dt><dd><b>${esc(w.from.part)}</b> · ${esc(w.from.pin)}</dd>
      <dt>To</dt><dd><b>${esc(w.to.part)}</b> · ${esc(w.to.pin)}</dd>
      <dt>Wire</dt><dd>${w.wire}</dd></dl>${w.note ? `<p class="note">${w.note}</p>` : ""}`;
  }

  let cur = 0;
  function render(i) {
    cur = i;
    rings.textContent = "";
    drawn.forEach((e, j) => {
      if (!e) return;
      e.g.style.opacity = j <= cur ? 1 : 0.1;
      e.p.classList.toggle("now", j === cur);
      if (j === cur) {
        const L = e.p.getTotalLength();
        [0, L].forEach(l => {
          const pt = e.p.getPointAtLength(l), c = document.createElementNS(NS, "circle");
          c.setAttribute("cx", pt.x); c.setAttribute("cy", pt.y); c.setAttribute("r", 9); c.setAttribute("class", "pw-ring");
          rings.append(c);
        });
      }
    });
    [...pills.children].forEach((b, j) => { b.classList.toggle("on", j === cur); b.classList.toggle("done", j < cur);
      b.setAttribute("aria-current", j === cur ? "step" : "false"); });
    const s = STEPS[cur], nWires = STEPS.filter(x => x.type === "wire").length;
    $("s-title").textContent = s.title;
    $("k-sec").textContent = s.type === "wire" ? `Wire ${STEPS.slice(0, cur + 1).filter(x => x.type === "wire").length} of ${nWires}`
      : s.type === "check" ? "Check" : "Prepare";
    $("s-body").innerHTML = body(s);
    $("k-step").textContent = `Step ${cur} of ${STEPS.length - 1}`;
    $("back").disabled = cur === 0;
    $("next").textContent = cur === STEPS.length - 1 ? WALK.nextLabel : "Next";
    if (location.hash !== `#step-${cur}`) history.replaceState(null, "", `#step-${cur}`);
  }
  function go(i) {
    if (i > STEPS.length - 1) { location.href = WALK.next; return; }
    render(Math.max(0, Math.min(STEPS.length - 1, i)));
  }
  $("back").addEventListener("click", () => go(cur - 1));
  $("next").addEventListener("click", () => go(cur + 1));
  document.addEventListener("keydown", e => {
    if (e.target.closest("input, textarea, select")) return;
    if (e.key === "ArrowRight") go(cur + 1);
    if (e.key === "ArrowLeft") go(cur - 1);
  });
  const fromHash = () => { const m = /^#step-(\d+)$/.exec(location.hash); return m ? +m[1] : 0; };
  window.addEventListener("hashchange", () => { const k = fromHash(); if (k !== cur) go(k); });
  render(Math.min(fromHash(), STEPS.length - 1));
})();
