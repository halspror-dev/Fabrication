# Design state

Read this first in a new thread, then `git log -5 --oneline`. Update it, and commit, before a thread ends.
One design version per thread. Start a fresh thread after two failed fixes of the same problem.

- **Current version:** v0.95 (drawn, not yet printed). Files: `drawing-scripts/`, outputs in the project files
  under `v0.95/` (17-page PDF, 4 DXFs, 8 STLs in mm, zip). LOCKED until the 3D-print test (carlie, 2026-10-26):
  no geometry or exporter changes. 2026-10-26: the 10 flat 2D pages were dropped at carlie's request (printing and
  ordering cuts); `templates.py` now prints the checks, and renders, DXFs and STLs are unchanged.
- **Rules from carlie:** every moving part gets an open and closed state, drawn and checked. No metal orders until a
  printed prototype works (2026-10-25). Design is private until the provisional patent is filed. Size the grip for
  the average man's hand (188 mm). Function first, then cost; fewer parts beats less metal.
- **Decisions behind this version:**
  - Flat grip scales became 2 printed PETG U-sleeves (`sleeves.py`, TRIG_SLV / GRIP_SLV): trigger bar front edge and
    grip back edge, full round across 5/8"; the trigger sleeve bows 0.08" under the middle/ring fingers.
  - Trigger bar front edge moved back 0.30" (top) / 0.10" (bottom): squeezed span 54/55/55/53 mm index to little,
    rest 60-66 mm (Lee 2009 target 50-55 mm). Sleeve starts 0.12" lower to clear the handle at pivot lobe 4.
  - Carried from v0.94: clevis-pin pivot in 4 lobes with hitch clip, pin holes 0.250 for reaming, tab slots 0.128,
    clip holes 0.125 (SCS minimum), keeper slots 0.198.
  - Shims under the pivot pin head and keeper posts are printed (`make_stl.py`, commit 30660c6), not bought.
- **Checks last run (2026-10-26):** `templates.py` 57 PASS, 0 FAIL. `check3d.py` PASS in all 5 states; closest free
  pair 0.047" can | collar (seat states), 0.060" handle plate | trigger (big hole). Render review: every page was
  looked at in the v0.95 thread before it went to carlie (2026-10-25); no render-reviewer pass yet.
- **Tooling (2026-10-26):** 2D pages are gone (PR #7, merged); main rebuilds the same renders, STLs and DXF
  geometry as before it. `check3d.py` now exits 1 on a FAIL, and a PreToolUse hook blocks any `git push` until it passes.
- **Can measurements (2026-10-27):** logged in `MEASUREMENTS.md`. Rust-Oleum lip gap 2.58 mm: the 0.090 collar fits
  with 0.29 mm (0.012") to spare, tighter than the drawn can (0.047"). No geometry change; carlie decides after the print test.
- **Open issues:** none known in the drawings. The real test is the print: fit on real cans in both clip positions,
  trigger travel and up-stop, keeper lock, sleeve comfort.
- **Print test result (2026-10-31) and rethink (2026-11-01):** the first printed v0.95 works but carlie finds the keyhole +
  sliding keeper annoying, the tab hitch clips hang below the collar, tight clips are hard to fit, and it wiggles too much.
  Rethink (suggestions, no geometry changed): `/mnt/project-files/design-rethink/ATTACHMENT-OPTIONS.md`. Main wiggle = tab in
  the 0.090 collar slot; recommended direction B = self-latching keyhole (one-piece collar+handle, spring latch replaces the
  keeper stack and all clips). Waiting on carlie's pick + 4 quick wiggle tests. Next version (v0.96) starts in a fresh thread.
- **Old next step (done):** wait for the P2S printer (planned 2026-10-27), print the v0.95 STLs, and test. Any change from the
  test becomes v0.96 in a new thread, plus a buy-sheet update.
