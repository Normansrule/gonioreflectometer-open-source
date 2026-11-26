# Contributing

Thank you for helping. Builders, testers and developers are all welcome.

| You want to | Do this |
|---|---|
| Report a problem or ask for help | Open a [GitHub issue](https://github.com/Normansrule/gonioreflectometer-open-source/issues): the step ID (for example `M19.1`), what you did, what you saw, and the run folder's `manifest.json` if there is one. |
| Report a build step that was unclear | Open an issue naming the step; that is how the build guide gets better. |
| Change code, CAD or docs | Fork, branch, change, then run `make all` (build, checks, tests, paper, exports) and open a pull request. |
| Add a part | Edit `phases/*/bom.csv` (the source of truth); `make build` regenerates the README tables, `PARTS.md` and the budget. |

## Rules the checks enforce

- Parts from Digi-Key, Amazon or Adafruit only, the cheapest that meets the spec, with the price checked on the store page.
- No soldering, drilling, sawing or crimping; printed parts in black ABS; M2 screws into printed pilots.
- Never invent links, part numbers, prices or results: mark unknowns `[TBD]`.
- Generated files (`README.md` tables, `PARTS.md`, `wiki/`, `exports/`, `paper/generated/`) come from their sources: edit the source.

## Licences

Hardware: CERN-OHL-S-2.0. Software: GPL-3.0-or-later. Documentation: CC BY-SA 4.0. By contributing you agree that your
contribution is released under the licence of the part you changed.
