# C1 stringing towers, first LAN print through Bambuddy (prediction written 2026-11-01 ~04:16 UTC)

- Job: pipeline test. Proves the LAN route (BigGuy CLI slice -> Bambuddy upload -> held queue -> carlie taps Print
  -> FTPS to the USB stick -> print) and that the headless slice matches a Studio GUI slice. No load, no fit.
- File: C1 from `../coupons/make_coupons.py` (`C:\PrintLocal\C1-stringing-towers.stl`, same STL as T0a), sliced
  headless to `C1-test.gcode.3mf` (105,205 bytes). Command and profiles: `../lan/README.md`.
- Printer: P2S firmware 01.03.00.00, stock 0.4 nozzle, Textured PEI plate, at 192.168.68.51. Bambuddy 1.2.5.7 queue
  item 1, library file 1, started by carlie 2026-11-01 04:12:23 UTC.
- Filament: Bambu PETG Matte, roll 1 (opened 2026-10-31, not dried), external spool, `use_ams: false`.
- Slicer: Bambu Studio 02.08.02.61 CLI, stock profile set 02.08.00.05: `Bambu Lab P2S 0.4 nozzle`,
  `Bambu PETG Matte @BBL P2S 0.4 nozzle` (flow ratio 0.95, 240 °C), bed 70 °C, process **fit-0.20-v1**.
- Settings that differ from T0a: `wall_loops` 3 (T0a 2), `xy_hole_compensation` 0.16 (no holes in C1, so no
  effect expected), arranged by `--arrange 1`. Print-start options: bed levelling auto, flow calibration auto,
  vibration calibration on.
- Slicer estimate: 25 min 34 s (18 min 32 s printing), 1.33 g, 0.40 m, 100 layers.
- Prediction **[I]**: prints the same as T0a. 0-3 strings (roll open about one day, under the 3-day drying rule);
  tower width within 0.05 of T0a (4.94-5.02); span ~54.9.
- Result: printed clean via LAN, 04:12:23-04:37:42 UTC (25 min 19 s vs 25 min 34 s estimate), Bambuddy status completed, no errors. File reached the USB stick by FTPS with no problem. Strings: **0**.
- Measured (NEIKO caliper, mm, carlie 2026-11-01):

  | Feature | Nominal | Readings | Mean | Error | T0a (USB, 2 walls) |
  |---|---|---|---|---|---|
  | Tower diameter | 5.00 | 4.90 / 4.92 / 4.86 | 4.893 | -0.11 | 4.98 / 4.96 (mean 4.97) |
  | Height | 20.00 | 20.07 / 20.06 / 20.08 | 20.07 | +0.07 | 20.14 / 20.15 |

- Why smaller (checked on BigGuy, read-only): the slice is not the cause. Sliced headless four ways (2/3 walls x hole
  comp 0/0.16): the outer-wall centreline is identical in all four, 4.573 x 4.576 mm at Z 10 (+0.42 line width =
  4.99), so the G-code aims at 5.00 and neither 3 walls nor hole comp 0.16 moves the outline. A real GUI project with
  the same P2S presets matches the flattened CLI profiles on every print-relevant key (12 differing keys, all
  AMS/colour/bookkeeping). Remaining causes **[I]**: caliper squeeze on a thin round tower (spread 0.06 within
  today's set), 3 walls making a solid tower that pulls in more as it cools, or filament state. Settle with one plate
  holding a 2-wall and a 3-wall tower, measured the same way. Note: `C:\PrintLocal\C1-stringing-towers.3mf` is
  misnamed: it holds the 8 v0.95 parts (no G-code), not the T0a towers.
- Seen during the run: camera view dropped once around 04:12-04:13 UTC; repeated status read at 04:14:00 did not
  drop it, so not caused by the API reads (carlie). HMS 0500-0200-0003-000A active, blank in Bambu's code list,
  didn't stop the print. Nozzle target 250 °C during the filament-change stage before printing (stock start G-code,
  inference).
- Score: strings **hit** (0). Width **miss** (predicted 4.94-5.02, got 4.89). Height better than T0a.
- Pipeline verdict: LAN route works end to end (slice, upload, held queue, carlie's tap, FTPS, print, archive).
