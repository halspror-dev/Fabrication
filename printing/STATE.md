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
- `PLAN.md`: the calibration and test plan (step 4): batches, predictions, coupons, baseline profiles.
- `research/`: step 3 findings, one file per topic (claims tagged sourced/inference; raw evidence stays in
  `/mnt/project-files/research/<topic>/`, not in git).
- `profiles/`: exported slicer profiles, one file per profile, versioned by git. See `profiles/README.md`.
- `tests/`: one record per print, calibration coupons included. See `tests/README.md` for the format; prediction
  scores in `tests/SCORES.md`.

## Roadmap (carlie, 2026-10-29; each step is its own thread)
1. Catch up and set up `printing/`. **Done 2026-10-29.**
2. Ask carlie one short batch of plan-changing questions; save answers to project memory. **Done 2026-10-29.**
3. Research, one thread per topic (P2S setup/calibration, dimensional accuracy, PETG data sheets and drying, slicer
   choice, design-for-print, measured strength tests, Bambu Studio workflow/CLI). Findings file with every claim
   tagged sourced/inference; research cost recorded. **Done 2026-10-29** (`research/`: petg, design-strength,
   setup-slicer, accuracy).
4. Design the calibration and test-coupon sequence (what each proves, expected number written before printing),
   baseline profiles and the print record format. Show carlie before printing. **Done 2026-10-29: `PLAN.md`.**
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

- 2026-10-29 (step 2): carlie's answers (thread "Answer setup questions for print plan"):
  - **Printed so far:** nothing. The P2S is still boxed (on the porch); no auto-calibration run yet.
  - **Fit accuracy:** carlie left it to our judgement and asked us to ask Fabrication. Sent as project-notes
    `inbox/fabrication/2026-10-29-printing-fit-tolerances.md`; Fabrication's answer sets the targets in step 4.
    Until then the working target (inference, to be checked in step 3 research and step 5 calibration) is: printed
    size within about 0.1 mm on the fit-critical features (collar thickness, pin and clip holes, tab and keeper slots),
    looser on plate outlines.
  - **Measuring:** 6 inch digital calipers, large display, about $25 (carlie named them Seiko).
    `drawing-scripts/MEASUREMENTS.md` says the can was measured with a NEIKO caliper: confirm which is used and record
    the caliper in every test record. No pin or feeler gauges mentioned.
  - **Filament:** Bambu Lab matte PETG, 8 rolls. PETG only until it proves wrong for a part, so we learn one material.
    No dryer mentioned: drying and storage are part of the step 3 PETG research.
  - **Hardware:** stock (nozzle and plate as shipped).
  - **Software:** nothing installed on BigGuy yet; the printer is not bound to any account yet. So the slicer choice
    and LAN-only / no-cloud setup can be decided before first power-on (step 3 slicer research, step 4 plan).
  - **Handle sleeves in use:** mostly paint and aerosol runoff, sometimes paint thinner. PETG's resistance to
    paint thinner is unverified: research it in step 3 (maker data sheets first).

- 2026-10-29 (step 3, topic C, PETG): `research/petg.md`. PETG Matte TDS settings (nozzle 230-260 C, bed 65-75 C,
  glue recommended, Z tensile 30.1 vs X-Y 42.9 MPa, HDT ~71 C). Dry one roll at a time on the P2S bed, 80 C for
  12 h, box as cover; store opened rolls under 20% RH with desiccant and a hygrometer. Solvents: acetone cut printed
  PETG to ~30% tensile in 7 days of immersion (Kaptan 2025); no source tested printed PETG in mineral spirits, and
  sources conflict. Proposed a wipe/soak coupon test with carlie's own paint and thinner for the step 4 plan. No
  other material worth buying until that test fails.

- 2026-10-29 (step 3, design-for-print and measured-strength topics): `research/design-strength.md`. Key points:
  our filament's own data sheet (Bambu PETG Matte TDS V1.0) gives Z/X-Y of 70 % tensile but only 31 % impact, so
  orient every loaded part so the load runs along layers; walls beat infill for strength per gram; layers 0.2 mm or
  less; fit holes print vertical and are fixed by slicer compensation from our own coupon, never by changing the
  design; no AMS, so design and orient for no supports. No source above forum level gave PETG clearance numbers:
  step 4 needs a fit coupon. ~95k tokens; 30 fetches (27 OK).

- 2026-10-29 (step 3, topic A: setup, slicer, workflow, LAN-only): findings in `research/setup-slicer.md`.
  - **Slicer: Bambu Studio** (only slicer Bambu authorizes to print to a LAN-only P2S without Developer Mode; runs
    the P2S auto flow dynamics; same P2S/PETG Matte profiles as OrcaSlicer; has a CLI and preset bundles; has Precise Z
    height). OrcaSlicer as an offline second slicer, files by USB drive: Orca has polyholes and an exposed precise
    wall, Studio doesn't, so steps 4/5 print the hole/slot coupon from both and let the calipers decide which slices
    the fit-critical parts.
  - **Privacy:** LAN Only on, Developer Mode off, no cloud printing (cloud keeps G-code, i.e. geometry, on Bambu's
    servers), no Studio login if it works without one. Open: whether the P2S forces a one-time account login before
    LAN Only; carlie decides at the printer.
  - **P2S automates:** bed leveling, vibration compensation (input shaping), motor noise cancellation, clumping and
    camera calibration, flow dynamics (eddy sensor). **We do:** flow rate (manual coarse then fine), XY hole/contour
    compensation, first-layer check; firmware updates offline by USB.

- 2026-10-29 (step 3, topic B: dimensional accuracy): findings in `research/accuracy.md`. Key points: calibrate flow
  first, then elephant foot (P2S default 0.15 mm), shrinkage per filament, contour, then hole compensation (diameter
  grows by twice the value); auto circle compensation does not support PETG Matte and Bambu Studio has no polyholes;
  the collar slices to 2.20 mm at 0.20 mm layers, and Precise Z height should give 2.286 mm (check preview, then
  measure); print Bambu's P2S air deflector for PETG-only prints. Caliper accuracy spec unverified (pages blocked).

- 2026-10-29 (step 4): `PLAN.md`. Five batches: 0 first day (unbox, LAN Only before any login, firmware, Studio
  and Orca on BigGuy, v0 profile export, coupon script, stringing from the bag, dry roll 1); 1 flow dynamics, flow
  rate, air deflector, elephant foot, shrink bars; 2 fit coupon Studio vs. Orca, compensation, real-hardware fit,
  Z coupon (collar 2.20 at 0.20, Precise Z off); 3 overhang, strength bars, solvent coupons; 4 validation reprint via
  the Studio CLI. Every test has its prediction and pass band written before printing; scores go in
  `tests/SCORES.md`. Fit bands come from Fabrication's reply (project-notes
  `archive/printing/2026-10-29-fabrication-fit-tolerances.md`). Step 3 research PRs #13-#16 were merged
  into this branch with their `STATE.md` conflicts resolved.

## Next
- Step 5, batch 0 of `PLAN.md`, in a fresh thread, when carlie unboxes the printer. That thread also writes
  `coupons/make_coupons.py` and runs it on BigGuy.
- Before batch 3: carlie names the spray paint and thinner cans used near the sleeves (read their SDS first).
- Step 6 (STL review) needs no printer and can run any time.

## What failed
- Nothing yet.
