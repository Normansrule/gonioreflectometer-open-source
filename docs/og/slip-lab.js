/* Slip lab (docs/lab.html#slip): the estimator of software/src/opengonio/gantry/slip.py, step for step, on a made-up
   axis whose belt creeps and loses steps. Nothing here is a measurement. tests/test_slip.py checks NOMINAL below
   against slip.py DEFAULTS.  SPDX-License-Identifier: GPL-3.0-or-later */
(() => {
  const $ = id => document.getElementById(id);
  if (!$("slipc")) return;
  const NOMINAL = { k_sigma: 2.0, q_deg2_per_deg: 1.0e-6, creep_sd: 2.0e-4, creep_walk: 1.0e-12, switch_sd_deg: 0.02, gate: 4.0, max_correct_deg: 1.0 };
  const TRAVEL = 3600;                                        // degrees of axis travel shown
  const U = { creep: 0.06, budget: 0.1, mode: "probe", lost: null };

  function rng(seed) { let s = seed >>> 0; const u = () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296;
    return { u, n: () => Math.sqrt(-2 * Math.log(u() + 1e-12)) * Math.cos(2 * Math.PI * u()) }; }

  /* AxisSlip in slip.py: same names, same order of operations */
  function filter(c) {
    const f = { d: 0, s: 0, pdd: c.switch_sd_deg ** 2, pds: 0, pss: c.creep_sd ** 2, travel: 0,
      get sigma() { return Math.sqrt(Math.max(f.pdd, 0)); }, get bound() { return c.k_sigma * f.sigma; },
      predict(a) { f.d += f.s * a; f.pdd += 2 * a * f.pds + a * a * f.pss + c.q_deg2_per_deg * a; f.pds += a * f.pss; f.pss += c.creep_walk * a; f.travel += a; },
      update(y) {
        const innov = y - f.d, sv = f.pdd + c.switch_sd_deg ** 2, nsig = Math.abs(innov) / Math.sqrt(sv);
        if (Math.abs(y) > c.max_correct_deg) return "fault";
        if (nsig > c.gate) { if (f.travel > 0) f.pss = Math.max(f.pss, (innov / f.travel) ** 2); f.d = y; f.pdd = c.switch_sd_deg ** 2; f.pds = 0; return "step loss"; }
        const kd = f.pdd / sv, ks = f.pds / sv; f.d += kd * innov; f.s += ks * innov; f.pss -= ks * f.pds; f.pds -= kd * f.pds; f.pdd -= kd * f.pdd; return null;
      },
      rehomed() { f.d = 0; f.pdd = c.switch_sd_deg ** 2; f.pds = 0; f.travel = 0; } };
    return f;
  }

  /* one run: random strokes; D = true - controller angle. raw: nothing done. kept: what the model leaves uncorrected */
  function simulate() {
    const c = NOMINAL, R = rng(7), f = filter(c), creep = U.creep / 100;
    const rows = [], refs = [], events = [];
    let x = 0, raw = 0, D = 0, lostDone = false, stopped = null;
    while (x < TRAVEL) {
      const a = 20 + 70 * R.u();
      let step = creep * a + Math.sqrt(c.q_deg2_per_deg * a) * R.n();
      if (U.lost != null && !lostDone && x + a >= U.lost) { step -= 0.5; lostDone = true; events.push({ x: x + a, kind: "lost" }); }
      x += a; raw += step;
      if (U.mode === "off" || stopped) { rows.push({ x, raw, err: raw, bound: null }); continue; }
      D += step; f.predict(a);
      if (f.bound > U.budget) {                                // due: back to the switch before the next shot
        let ev = null;
        if (U.mode === "probe") { ev = f.update(D + c.switch_sd_deg * R.n());
          if (ev === "fault") { stopped = x; events.push({ x, kind: "fault" }); rows.push({ x, raw, err: D - f.d, bound: f.bound }); continue; }
          if (ev) events.push({ x, kind: "step" }); }
        rows.push({ x, raw, err: D - f.d, bound: f.bound });   // the instant before re-homing
        D = c.switch_sd_deg * R.n(); f.rehomed(); refs.push(x);
      }
      rows.push({ x, raw, err: D - f.d, bound: f.bound });
    }
    const worst = k => rows.reduce((m, r) => Math.max(m, Math.abs(r[k])), 0);
    return { rows, refs, events, stopped, creepHat: f.s, creepSd: Math.sqrt(Math.max(f.pss, 0)), worstRaw: worst("raw"), worstErr: worst("err") };
  }

  let run = simulate(), shown = 1, raf = 0;
  function draw() {
    const cv = $("slipc"), dpr = Math.min(window.devicePixelRatio || 1, 2), W = cv.clientWidth, H = Math.round(W * (W < 560 ? 0.72 : 0.46));
    cv.style.height = H + "px"; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    const g = cv.getContext("2d"), K = OG.tokens(); g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const L = 52, Rm = 30, T = 30, B = 40, all = run.rows.flatMap(r => [r.raw, r.err]);
    const ymax = Math.max(0.3, Math.min(2.4, Math.ceil(Math.max(...all) * 11) / 10)), ymin = -Math.max(0.3, Math.min(2.4, Math.ceil(-Math.min(...all) * 11) / 10));
    const X = x => L + x / TRAVEL * (W - L - Rm), Y = y => T + (ymax - Math.max(ymin, Math.min(ymax, y))) / (ymax - ymin) * (H - T - B);
    g.clearRect(0, 0, W, H); g.font = `12px ${K.text}`; g.lineWidth = 1;
    g.fillStyle = OG.alpha(K.green, 0.1); g.fillRect(L, Y(U.budget), W - L - Rm, Y(-U.budget) - Y(U.budget));      // the budget
    g.strokeStyle = K.rule; g.fillStyle = K.ink2;
    const yt = ymax - ymin <= 1 ? 0.1 : ymax - ymin <= 2 ? 0.25 : 0.5;
    for (let y = Math.ceil(ymin / yt - 1e-9) * yt; y <= ymax + 1e-9; y += yt) { g.beginPath(); g.moveTo(L, Y(y)); g.lineTo(W - Rm, Y(y)); g.stroke();
      g.fillText((y > 0 ? "+" : y < 0 ? "−" : "") + Math.abs(y).toFixed(yt < 0.2 ? 1 : 2) + "°", 6, Y(y) + 4); }
    for (let x = 0; x <= TRAVEL; x += 720) g.fillText(x + "°", X(x) - (x ? 14 : 0), H - B + 16);
    g.fillText("axis travel since homing", L, H - 8);
    const upto = shown * TRAVEL, rows = run.rows.filter(r => r.x <= upto);
    if (U.mode !== "off") {                                    // the bound the software believes (2 sigma)
      g.fillStyle = OG.alpha(K.blue, 0.16); g.beginPath();
      const br = rows.filter(r => r.bound != null);
      br.forEach((r, i) => i ? g.lineTo(X(r.x), Y(r.bound)) : g.moveTo(X(r.x), Y(r.bound)));
      for (let i = br.length - 1; i >= 0; i--) g.lineTo(X(br[i].x), Y(-br[i].bound));
      g.closePath(); g.fill();
      run.refs.filter(x => x <= upto).forEach(x => { g.strokeStyle = K.ink3; g.setLineDash([2, 4]); g.beginPath(); g.moveTo(X(x), T); g.lineTo(X(x), H - B); g.stroke(); g.setLineDash([]); });
    }
    const line = (k, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(X(0), Y(0)); rows.forEach(r => g.lineTo(X(r.x), Y(r[k]))); g.stroke(); };
    line("raw", K.red, 1.5);
    if (U.mode !== "off") line("err", K.blue, 2);
    run.events.filter(e => e.x <= upto).forEach(e => { g.fillStyle = e.kind === "lost" ? K.red : K.light; g.beginPath();
      g.arc(X(e.x), e.kind === "lost" ? Y(run.rows.find(r => r.x >= e.x).raw) : T + 6, 5, 0, 7); g.fill(); });
    g.font = `500 12px ${K.text}`; let lx = L;
    [[K.red, "angle error, nothing done"], ...(U.mode === "off" ? [] : [[K.blue, "angle error with the model"], [OG.alpha(K.blue, 0.4), "its 2σ bound"]]),
     [OG.alpha(K.green, 0.5), `budget ±${U.budget.toFixed(2)}°`]].forEach(([col, txt]) => {
      if (lx + g.measureText(txt).width + 28 > W) return;
      g.fillStyle = col; g.fillRect(lx, 9, 10, 10); g.fillStyle = K.ink; g.fillText(txt, lx + 16, 18); lx += g.measureText(txt).width + 34; });
    document.querySelectorAll("#sliploop [data-on]").forEach(el => el.classList.toggle("on", U.mode !== "off" && (el.dataset.on !== "probe" || U.mode === "probe")));
  }
  function readout() {
    const pct = v => (v >= 0 ? "+" : "−") + Math.abs(100 * v).toFixed(3) + " %";
    $("sl-refs").textContent = U.mode === "off" ? "0" : String(run.refs.length);
    $("sl-raw").textContent = "±" + run.worstRaw.toFixed(2) + "°";
    $("sl-err").textContent = U.mode === "off" ? "±" + run.worstRaw.toFixed(2) + "°" : "±" + run.worstErr.toFixed(2) + "°";
    $("sl-creep").textContent = U.mode === "probe" ? pct(run.creepHat) : "not measured";
    $("sl-every").textContent = U.mode === "off" || run.refs.length < 2 ? "–" : Math.round((run.refs[run.refs.length - 1] - run.refs[0]) / (run.refs.length - 1)) + "°";
    const st = $("sl-stat"), step = run.events.some(e => e.kind === "step");
    st.className = "status " + (run.stopped ? "bad" : U.mode === "off" ? "warn" : run.worstErr > U.budget * 1.5 ? "warn" : "ok");
    st.textContent = run.stopped ? `Run stopped at ${Math.round(run.stopped)}° of travel: measured slip beyond 1°, a mechanical fault (belt, set screw, acceleration).`
      : U.mode === "off" ? `No model: the error reaches ${run.worstRaw.toFixed(2)}° and no run would know.`
      : U.mode === "rehome" ? `Re-homing bounds the error, but the creep is never measured, so references stay ${$("sl-every").textContent} apart and the drift between them is not corrected.`
      : step ? "The filter did not believe one reference (more than 4σ from its prediction): reported as lost steps, then re-homed."
      : `The creep is learned from the first references, every command is corrected, and references get rarer.`;
  }
  function play() {
    cancelAnimationFrame(raf);
    if (OG.reduced) { shown = 1; draw(); return; }
    const t0 = performance.now(); shown = 0;
    const tick = t => { shown = Math.min(1, (t - t0) / 5200); draw(); if (shown < 1) raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
  }
  function update(animate) { run = simulate(); readout(); if (animate) play(); else { cancelAnimationFrame(raf); shown = 1; draw(); } }

  [["sl-creep-in", v => U.creep = v, v => v.toFixed(2) + " %"], ["sl-budget-in", v => U.budget = v, v => "±" + v.toFixed(2) + "°"]].forEach(([id, set, fmt]) => {
    const el = $(id), out = el.nextElementSibling, upd = () => { set(+el.value); out.textContent = fmt(+el.value); update(false); };
    el.addEventListener("input", upd); set(+el.value); out.textContent = fmt(+el.value); });
  document.querySelectorAll("#sl-mode button").forEach(b => b.addEventListener("click", () => { U.mode = b.dataset.mode;
    document.querySelectorAll("#sl-mode button").forEach(x => { x.classList.toggle("on", x === b); x.setAttribute("aria-pressed", String(x === b)); }); update(true); }));
  $("sl-lost").addEventListener("click", () => { U.lost = U.lost == null ? 1500 : null; $("sl-lost").classList.toggle("on", U.lost != null);
    $("sl-lost").setAttribute("aria-pressed", String(U.lost != null)); update(true); });
  $("sl-play").addEventListener("click", () => play());
  window.addEventListener("og:theme", draw); window.addEventListener("resize", draw);
  readout();
  const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); play(); } }, { threshold: 0.35 });
  io.observe($("slipc")); draw();
})();
