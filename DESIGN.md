---
name: OpenGonio
colors:
  velvet-ground: "#0c0b0a"
  velvet-ground-2: "#151310"
  velvet-ground-3: "#1e1b17"
  velvet-ground-4: "#2a2620"
  velvet-rule: "#2e2a24"
  bone-ink: "#efe9df"
  bone-ink-2: "#b9b1a5"
  bone-ink-3: "#8c857a"
  tungsten: "#ffc978"
  tungsten-text: "#ffcf8a"
  tungsten-ink: "#1b1306"
  scale-red: "#e06a5a"
  scale-green: "#7fb276"
  scale-blue: "#86a4e0"
  scale-white: "#f2f0eb"
  scale-grey: "#7b7975"
  scale-black: "#111110"
  grey-card: "#e6e5e2"
  grey-card-2: "#dcdbd7"
  grey-card-3: "#d0cec9"
  grey-card-4: "#c2c0ba"
  grey-card-rule: "#bdbab3"
  grey-card-ink: "#141311"
  grey-card-ink-2: "#45423d"
  grey-card-ink-3: "#625e57"
  tungsten-day: "#ffb547"
  tungsten-day-text: "#7c4500"
  tungsten-day-mark: "#9a5a00"
  scale-red-day: "#a8392b"
  scale-green-day: "#3e6f36"
  scale-blue-day: "#2f5aa8"
  stop-ink-day: "#ffffff"
  camera-frame: "#000000"
typography:
  display:
    fontFamily: "Gloock, Iowan Old Style, Georgia, serif"
    fontSize: "clamp(2.75rem, 1rem + 6vw, 6rem)"
    fontWeight: 400
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Gloock, Iowan Old Style, Georgia, serif"
    fontSize: "clamp(2rem, 1.25rem + 3vw, 3.5rem)"
    fontWeight: 400
    lineHeight: 1.04
    letterSpacing: "-0.015em"
  code:
    fontFamily: "ui-monospace, Cascadia Mono, Menlo, monospace"
    fontSize: "0.88em"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "normal"
  body:
    fontFamily: "Hanken Grotesk, system-ui, sans-serif"
    fontSize: "clamp(1.0625rem, 1rem + 0.25vw, 1.1875rem)"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "normal"
rounded:
  xs: "1px"
  sm: "2px"
  switch: "14px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "32px"
  xl: "64px"
  xxl: "144px"
components:
  button-primary:
    backgroundColor: "{colors.tungsten}"
    textColor: "{colors.tungsten-ink}"
    rounded: "{rounded.sm}"
    padding: "0 24px"
  button:
    backgroundColor: "{colors.velvet-ground-3}"
    textColor: "{colors.bone-ink}"
    rounded: "{rounded.sm}"
    padding: "0 24px"
---

# Design: Raking light

The design system for the OpenGonio website (`docs/`) and the control app (`software/src/opengonio/app/static/`).
Tokens live in one file, [`docs/og/og.css`](docs/og/og.css); `make build` copies it (with `og.js`, the fonts and the
icon) into the app, and `make check` fails if the copies drift.

## Concept

Conservators photograph a painting with a lamp held low and moved around it, so brush strokes and cracks show up as
light and shadow. OpenGonio does the same with motors and a fixed camera. So the interface is a dark room with one
warm lamp in it: the lamp is the only bright colour, and it marks the one thing to do next.

## Principles

1. **Evidence before claims.** Every number says whether it is simulated, modeled or measured; blocked and untested are
   shown, never hidden (PRODUCT.md).
2. **Show the light.** The clearest explanation of a reflectance measurement is light moving over real surfaces, so
   the landing page opens on one.
3. **One light per screen.** The tungsten colour is reserved for the lamp and the single primary action.
4. **Motion means something.** Springs for things that follow you, slow crossfades for light shifting, short presses
   for buttons. Nothing moves just to move.

## Colour

| Token | Dark (default) | Light | Use |
|---|---|---|---|
| `--ground` | `#0c0b0a` | `#e6e5e2` | page |
| `--ground-2` / `-3` / `-4` | `#151310` / `#1e1b17` / `#2a2620` | `#dcdbd7` / `#d0cec9` / `#c2c0ba` | panels, controls, tracks |
| `--ink` | `#efe9df` | `#141311` | text |
| `--ink-2` | `#b9b1a5` | `#45423d` | secondary text |
| `--ink-3` | `#8c857a` | `#625e57` | large text and marks only |
| `--rule` | `#2e2a24` | `#bdbab3` | table and field edges only |
| `--light` | `#ffc978` | `#ffb547` | the lamp, the primary button, focus ring, selection |
| `--light-text` | `#ffcf8a` | `#7c4500` | tungsten-coloured text (passes AA on the ground) |
| `--patch-red/green/blue` | `#e06a5a` / `#7fb276` / `#86a4e0` | `#a8392b` / `#3e6f36` / `#2f5aa8` | status and data, always with a word |

Status patches (10 px squares): blue = simulated, grey = modeled, hollow = not yet tested, red = blocked or failed,
green = passed, tungsten = needs attention. The camera is always blue and the lamp always tungsten, in every drawing.

Contrast: body text ≥ 4.5:1 and large text ≥ 3:1 in both themes (checked with Impeccable's detector). The theme follows
the system setting until the visitor picks one; the choice is kept in `localStorage` when the browser allows it.

## Type

- **Gloock** (display serif): headlines and big numbers. Never below 28 px.
- **Hanken Grotesk** (variable): everything else, weights 400–600.
- Monospace only for commands and code.
- Tabular figures for every number that changes.

| Step | Size | Use |
|---|---|---|
| display | `clamp(2.75rem, 1rem + 6vw, 6rem)` | page titles |
| head | `clamp(2rem, 1.25rem + 3vw, 3.5rem)` | section headlines (two lines at most) |
| lead | `clamp(1.25rem, 1.08rem + 0.7vw, 1.75rem)` | the sentence under a headline |
| body | `clamp(1.0625rem, 1rem + 0.25vw, 1.1875rem)` | running text |
| small | `0.875rem` | captions, chart labels, metadata |

## Space and shape

4 px base: `--s-1` 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 144 · 216 (`--s-11`). Page margin
`clamp(20px, 4vw, 56px)`. Corners 2 px. No gradients, no drop shadows at rest, no glass, no outlined cards: surfaces
are separated by tone and space.

## Motion

| Token | Value | Use |
|---|---|---|
| `--ease-out` | `cubic-bezier(0.23, 1, 0.32, 1)` | entering, pressing, following |
| `--ease-in-out` | `cubic-bezier(0.77, 0, 0.175, 1)` | crossfades between pictures |
| `--t-press` | 140 ms | button press (`scale(0.97)`) |
| `--t-ui` | 200 ms | colour and state changes |
| `--t-exposure` | 600 ms | the slow crossfade: stage pictures, the section rail |

- The hero lamp follows the pointer on a critically damped spring (`OG.spring`) and drifts on a slow Lissajous path
  after four idle seconds; it renders only while it moves and is on screen.
- On load the title rises line by line out of a mask while the lamp warms up over 1.8 s, like a tungsten filament.
- Section headlines are uncovered left to right by a band of light (a clip-path wipe, 1.1 s) and sections fade up 14 px as they arrive (desktop only).
- The app's pose drawing eases to each reported position on the same spring.
- Hover effects only on devices that hover. With `prefers-reduced-motion: reduce`, the lamp is still (parked where the
  mirror just catches it), nothing slides, and the drag row does not coast.

## Components

| Component | Where | Notes |
|---|---|---|
| Specimen | landing hero, full bleed (`og/specimen.js`) | WebGL, behind the copy and shifted right of centre: PTFE, mirror and printed ABS under a 3000 K point lamp; Lambert + GGX with Schlick Fresnel and height-correlated Smith, as in `opengonio.brdf.models.ggx_brdf`. Arrow keys move the lamp; a polite live region says where it is. Falls back to `og/img/specimen.png`. |
| Story | landing, straight under the hero (`#machine`) | a pinned stage 6 screens tall that the scroll drives (Apple-style): the CAD parts fly in from an exploded view, lowest first; then M4, M3, M2, M1 play in turn; then the view swings round behind the fixed camera. Big crossfading captions, a chapter index on the right (click to jump), θi and θr live. The scroll value follows with a little inertia. Reduced motion: no pinning, one still picture and every chapter as text. |
| Lamp cursor | hero, fine pointers | a tungsten ring on a stiff spring replaces the arrow over the specimen; the CTAs lean up to a few pixels toward the pointer |
| Big numbers | after "Drive it" | four Gloock figures (axes, CAD parts, build steps, planned cost) that count up once on arrival; from `site-data.js` |
| Four-axis rig | "Drive it yourself" (`og/rigview.js`) | the CAD assembly (`og/model/rig.js`, written by `tools/site_model.py` during `make cad`) in WebGL, moved with the rotations of `tools/cad/poses.py` and lit only by the lamp on its arm. Plays M4, M3, M2, M1 in turn with the moving parts rimmed in tungsten; a slider per axis drives it by hand (pauses the play); drag to orbit; θi and θr from the software's kinematics. Loads when it nears the screen; falls back to `og/img/assembly.png`. |
| Lamp gauge | hero, app | half circle: camera dot (blue) fixed at 35°, lamp dot (tungsten) at θi |
| Midline rail | landing, ≥ 1280 px | fixed at the vertical centre, appears after the hero, marks the section in view |
| Drag row | "How a measurement happens" | scroll-snap row, mouse drag with momentum, arrow buttons and arrow keys |
| Panels | results | unequal spans (7/5, 4/8); charts drawn from `og/sim-examples.js` in the page's colours |
| Ledger | evidence | two columns (claim, evidence), alternate rows toned, patch + word per row |
| Sticky stage picture | build stages | the simulator at each build stage, crossfading as the list scrolls |
| Q and A | questions | large serif question, answer beside it |
| Inverted footer | landing | ink ground, full-width wordmark |
| Page footer | lab, wiring guide, build book (`.site-foot` in `og.css`) | the same ink ground, smaller: Gloock mark, links to every page, licences; the current page bold, no underline |
| Wiring guide | `docs/wiring.html` (`og/wiring-page.js`, `og/guide.css`) | every wire from `docs/wiring.yaml`, one per step: the section diagram in SVG, wires already made stay drawn, the current wire thick with a moving-dot arrow and pulsing tungsten rings on its two pins, the next wire dashed. Wire kinds told apart by colour and line pattern (ground = black core with a light edge). Section chips with progress (bone bar, scaleX); `#step-N` links; arrow keys. Wide screens show the whole section; phones scroll to the wire's start pin. |
| Build book | `docs/build.html` (`og/build-page.js`, `og/guide.css`) | toy-brick instruction book from `docs/assembly.yaml` (`tools/build_book.py`): the CAD assembly (`og/model/rig.js`) in WebGL, parts already on in flat grey, this step's parts lit: tungsten = print it (the thing to do now, as the lamp marks it), bone = buy it. They slide in once per step along dashed ink arrows with a ground halo (900 ms each, 70 ms apart, exponential ease-out), then the page stops drawing; "Play again" repeats it. Parts box top left (a WebGL thumbnail per part, ×count, screws drawn to length), Gloock step number with "/total" bottom left, words from the stage checklist. Chips = parts of the machine (`section`). Drag to turn, double-click or "Reset view" to put it back; reduced motion: parts in place, arrows only. `?print`: one A4 landscape page per step, light theme (`exports/build-book.pdf`). |
| Pose view | app | top view: ring, lamp, sample and normal, camera; dashed ghost = target; drag or arrow-key the lamp |
| Switch | app lights | `role="switch"`; blocked lights disabled with the reason under "Blocked" |
| STOP | app header | always enabled, red patch colour, Esc |
| Device strip | app, under the header; connect screen | one cell per device from `/api/state` `devices`: motion board, camera, lamp, spectral sensor, button hub. Status = patch + word (simulated = blue, connected = green, standby, offline, not built, not in this app), the stage that builds it, and why. Scrolls sideways on phones. |
| Spectral bars | app sensors panel | ten AS7341 channels (F1–F8, Clear, NIR), each bar in its wavelength's hue, raw counts 0–65535; "Read once" calls `POST /api/spectral`. Simulator only: on hardware the app says the sensor reads through the button hub, which it doesn't open yet. |
| Run quality | app sensors panel | four tiles: lamp drift, mirror peak error, exposure, homed axes. A dash and the reason until a run supplies the number. |
| Position trust | app, above the sensors | one cell per axis from `/api/state` `trust` (the slip model, `gantry/slip.py`): the 2σ angle error bound as a Gloock number and a band on a track whose two notches are the budget; the band turns tungsten when the axis is due for its home switch. Under it: travel since the switch, the drift being corrected, the creep learned. "Check on the switches" re-references now. Simulator only: a select injects belt creep or lost steps, labelled as simulated. |
| Slip lab | `docs/lab.html#slip` (`og/slip-lab.js`) | the same filter in JavaScript on a made-up axis: angle error with nothing done (red), with the model (blue) inside its 2σ bound, the budget as a green band, dashed lines where the axis re-referenced; drawn left to right over 5 s once it scrolls into view. Under it the control loop as a block diagram: the feedback half is dim in mode `off`, the switch branch lit only in `probe`. Sliders: creep, budget; buttons: mode, lose steps, play again. |
| Session log | app sensors panel | the last 40 actions with time and patch (done, refused, finished, failed); `aria-live="polite"` |

## States (app)

| State | What shows |
|---|---|
| Loading | "Connecting to the app…" |
| Server gone | "The app's server isn't answering. Restart it with: opengonio app" |
| Not connected | choice of the simulated machine (with material) or the machine over USB, marked untested |
| Not homed | tungsten note "Home the axes before moving"; sliders and Run disabled; Run says "Home first to capture" |
| Busy | header patch breathes, controls disabled except STOP, progress bar with shots done |
| Error / refused | dismissible banner with the server's own message (unsafe pose, not homed, blocked light) |
| Stopped | banner: controller reset, home again |
| Results | verify verdict with patch, curve, notes; earlier runs list |
| Sensor not ready | spectral panel says why (not connected, simulator only, nothing read yet); quality tiles show a dash and what they need |

## Pictures

All pictures are made by `tools/site_pictures.py` (CAD render in raking light, simulator frames, specimen fallback) and
`tools/readme_screens.py` (README screenshots and the lamp GIF). No stock images, no photographs: nothing has been
built. Captions say "render" or "simulator".

## Checks

- `impeccable detect` over the site and app: no findings.
- taste-skill `lint.mjs`: no FAILs (warnings kept: zero-padded stage file names; the outline on the app's ghost buttons).
- taste-skill `inspect.mjs` at 1440, 768 and 390 px: no FAILs on the landing page and the app. The lab page keeps the
  KaTeX math fonts (two extra typefaces) because its equations need them.
