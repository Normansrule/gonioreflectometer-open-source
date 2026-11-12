/* Control app web demo: the page is the real app (copied by tools/site_app.py); its /api/ calls go to docs/app/worker.js,
   which runs the opengonio package (simulated machine) in Pyodide, instead of to `opengonio app` on a laptop.
   SPDX-License-Identifier: GPL-3.0-or-later */
(function () {
  "use strict";
  const worker = new Worker("worker.js");
  const waiting = new Map();
  let next = 1;
  worker.onmessage = e => {
    const m = e.data;
    if (m.type === "status") {
      const el = document.getElementById("loading");
      if (el) el.textContent = m.text;
      return;
    }
    const done = waiting.get(m.id);
    if (!done) return;
    waiting.delete(m.id);
    done(m.png ? new Response(new Blob([m.png], { type: "image/png" }), { status: m.status })
               : new Response(m.body, { status: m.status, headers: { "Content-Type": "application/json" } }));
  };
  const real = window.fetch.bind(window);
  window.fetch = function (input, init) {
    const url = new URL(typeof input === "string" ? input : input.url, location.href);
    const i = url.pathname.indexOf("/api/");
    if (i < 0) return real(input, init);
    const id = next++;
    return new Promise(resolve => {
      waiting.set(id, resolve);
      worker.postMessage({ id, method: (init && init.method) || "GET", path: url.pathname.slice(i),
                           query: url.search.slice(1), body: (init && init.body) || "" });
    });
  };
})();
