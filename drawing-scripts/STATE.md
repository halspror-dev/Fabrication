# Design state

Read this first in a new thread, then `git log -5 --oneline`. Update it, and commit, before a thread ends.
One design version per thread. Start a fresh thread after two failed fixes of the same problem.

- **Current version:** v0.96 (2026-11-01), cam-lever can clamp, drawn and checked, not yet printed. Scripts:
  `v096.py` (geometry + 38 mechanism checks), `v096_3d.py check|render`, `v096_export.py`. They read v0.95's `templates.py`
  for the trigger, sleeves, plate outline, pivot and up-stop (unchanged) and never edit it. Outputs: project files `v0.96/`
  (README.md = how it works, test plan, files; checks.txt; 9 STLs in mm incl. 3 lever jaw sizes; 4 DXFs; 4 render PNGs).
- **Rules from carlie:** every moving part gets an open and closed state, drawn and checked. No metal orders until a
  printed prototype works (2026-10-25). Design is private until the provisional patent is filed. Size the grip for
  the average man's hand (188 mm). Function first, then cost; fewer parts beats less metal.
- **Why v0.96:** the v0.95 print (2026-11-01) was fiddly (keyhole + sliding keeper, tight clips), the tab clips hung below
  the collar, and it wiggled (tabs in thin slots worst). carlie picked direction D (cam clamp), not B (doubted a spring
  latch holds a big can), and wants on/off and adjusting to be a breeze.
- **Decisions behind v0.96:**
  - Lever picked from 3: thumbscrew-preload (rejected: cup rim ~3.5 mm tall, needs an extra sliding jaw), adjustable stop
    (rejected: sets lock angle, not tightness), **spring-jaw over-centre lever** (picked: 25 mm spring arm, 0.5 mm squeeze at
    the stop, ~28 N, 14-42 N over +-0.25 mm; 8 deg past centre, 0.26 mm snap; nothing to adjust).
  - Clamp on the valve cup OD (standard 32.5 +-0.1) with 2 seat pads at 130/230 deg and the jaw at 0 deg: every can centres
    at the origin, so no second clip position. Seat hole 1.18 (necks to ~29.5 mm, lip overlap 1.27 mm); entry hole 1.375,
    10 mm front-right (-30 deg) of the seat. Lever pivot 1/4" shoulder bolt #14221, head under the collar, nut on top.
  - Handle joint: collar has a printed upright flange bolted to the plate with 2 staggered button screws; plate tabs and
    hitch clips gone, the plate's foot still hooks the collar's back edge.
  - v0.95 rules kept: collar 0.090 (print 2.20, never over 2.29); trigger and sleeves sized for a 188 mm hand.
- **Checks last run (2026-11-01):** `v096.py` 38 PASS. `v096_3d.py check` PASS in 4 states (clamped rest/full, lever open
  can seated / at entry); closest free pair 0.044" cup | collar at the entry hole. Render review (subagent): all 4 pages PASS.
  The push hook now runs both `check3d.py` (v0.95) and `v096_3d.py check`.
- **Open issues / estimates:** PETG E 1.9 GPa and the 27 mm neck are estimates. Metal version of the collar pads, flange
  and spring lever not designed (an aluminium spring arm needs other sizes); DXFs are flat outlines only. Can tipping is held
  by the rear half of the lip plus the clamp grip (front of the lip has no collar under it): watch it in the print test.
- **Next step:** carlie prints v0.96 (collar, 3 levers, handle plate) and runs the test plan in `v0.96/README.md`. Any change
  becomes v0.97 in a fresh thread. Patent: new candidate claim (spring-jaw lever on the valve cup) not searched yet.
- **v0.95 (reference, locked):** templates.py + render3d/check3d/make_stl/make_dxf; outputs project files `v0.95/`.
