# Printing state

Read this first in a new printing thread, then `git log -5 --oneline -- printing/`. Update it, and commit, before
the thread ends. One roadmap step per thread; after two failed fixes of the same thing, write it here and start fresh.

- **Goal:** prints from the Bambu Lab P2S (no AMS, PETG) that are accurate, strong and right for the job on the first
  or second try, with the least filament, time and rework, starting with Fabrication's v0.95 prototype parts.
- **Rules that shape this folder:** this work never edits `drawing-scripts/` or `laser-order/`; design changes go to
  Fabrication as a project-notes inbox note. Nothing from the design (STLs, renders, dimensions) leaves our machines:
  slice locally on carlie's PC BigGuy, no slicer cloud. Every recommendation is labelled measured, sourced (URL) or
  inference. Test prints and calibration coupons come before real parts.

## Layout
- `STATE.md`: this file (goal, done, next, what failed).
- `profiles/`: exported slicer profiles, one file per profile, versioned by git. See `profiles/README.md`.
- `tests/`: one record per print, calibration coupons included. See `tests/README.md` for the format.

## Roadmap (carlie, 2026-10-29; each step is its own thread)
1. Catch up and set up `printing/`. **Done 2026-10-29.**
2. Ask carlie one short batch of plan-changing questions; save answers to project memory.
3. Research, one thread per topic (P2S setup/calibration, dimensional accuracy, PETG data sheets and drying, slicer
   choice, design-for-print, measured strength tests, Bambu Studio workflow/CLI). Findings file with every claim
   tagged sourced/inference; research cost recorded.
4. Design the calibration and test-coupon sequence (what each proves, expected number written before printing),
   baseline profiles and the print record format. Show carlie before printing.
5. Calibrate, one batch per thread; record results, score predictions, commit profiles.
6. Review the 8 v0.95 STLs locally (trimesh, nothing uploaded); findings to Fabrication's inbox.
7. Print the v0.95 test set with tuned profiles; fit/function results to Fabrication's inbox.
8. Report.

## Done
- 2026-10-29 (step 1): caught up and created this folder. Catch-up summary:
  - Design: v0.95 is drawn, not printed, and LOCKED until the print test (`drawing-scripts/STATE.md`). Last checks
    2026-10-26: `templates.py` 57 PASS, `check3d.py` PASS in all 5 states.
  - The 8 STLs (mm) come from `cd drawing-scripts && python3 make_stl.py templates.py OUTDIR`: 2 PETG U-sleeves
    (trigger, grip; the only parts for real use) plus flat plate stand-ins for the laser-cut parts and printed shims.
    Sleeves are written standing on their open side so they print without supports.
  - `MEASUREMENTS.md`: the collar must slide under the real Rust-Oleum can's lip with very little to spare, and the
    printed collar's height rounds to whole layers, so layer height matters for that part (check the slicer preview).
  - Hardware for about 6 printed test handles was ordered 2026-10-26 (project-notes `status/fabrication.md`).
  - project-notes: no inbox notes for fabrication or printing. graphify is not installed and there is no
    `graphify-out/graph.json`, so plain grep was used. `halspror-dev/print-lab` is an empty repo, unused so far.
  - Nothing printed yet; slicer not chosen.

## Next
- Step 2: ask carlie the questions that change the plan (what has been printed or failed so far, how accurate the
  test fits must be in mm, other filament coming, which filament brand/colour, slicer already installed on BigGuy?).

## What failed
- Nothing yet.
