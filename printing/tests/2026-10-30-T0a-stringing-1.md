# T0a stringing towers, from the bag (prediction written 2026-10-30)

File named for the day the prediction was written; the print date goes in Result.

- Job: calibration. Shows whether roll 1 strings straight from its sealed bag, before drying. No load, no fit.
- File: `../coupons/make_coupons.py` C1 (two 5 mm towers, 20 mm tall, 50 mm apart on a 0.6 mm strip), commit ____.
- Printer: P2S firmware 01.03.00.00, stock 0.4 nozzle, plate Textured PEI, glue stick (yes, centre patch), air deflector out (not printed yet), door
  closed, lid on.
- Filament: Bambu PETG Matte white, roll 1, from the bag (not dried), bag sealed with desiccant: yes.
- Room: ____ °C, ____ % RH.
- Slicer: Bambu Studio ____; stock presets (`bundle-p2s-stock-v0`): `0.20mm Standard @BBL P2S`,
  `Bambu PETG Matte @BBL P2S 0.4 nozzle`. Print-start advanced options auto (flow dynamics on).
- Settings that differ from the profiles: none. Placed where Studio drops it, not rotated.
- Prediction: few or no strings (0-3) between the towers. Why: fresh sealed roll; Bambu says PETG Matte needs drying
  only after more than 72 h at 50% RH (`../research/petg.md` S2) **[S]**/**[I]**. Compared with T0b (same towers,
  dried roll) in batch 1.
- Result: attempt 1 (2026-10-31 ~01:55) printed nothing: filament had not been loaded (screen showed "Ext ?"), stopped at layer 6. Loaded roll 1, restarted ~02:10. Printed clean, ~02:35. Strings: **0** (none seen while printing or on the part, photo 2026-10-31). Strip flat and fully stuck; tiny nub at the left end of the strip (line start/end).
- Measured (caliper ____, mm, room temperature), information only:

  | Feature | Nominal | Target band | Readings (3) | Mean | Spread | Error vs nominal | In band? |
  |---|---|---|---|---|---|---|---|
  | A: tower 1 diameter, mid-height | 5.00 | none yet | 4.98 / 4.98 / 4.98 | 4.98 | 0.00 | -0.02 | n/a |
  | B: tower 2 diameter, mid-height | 5.00 | none yet | 4.95 / 4.97 / 4.97 | 4.963 | 0.02 | -0.04 | n/a |
  | C: height, strip bottom to tower 1 top | 20.00 | none yet | 20.14 (carlie: "etc", similar) | ~20.14 | n/a | +0.14 | n/a |
  | D: height, strip bottom to tower 2 top | 20.00 | none yet | 20.15 (similar) | ~20.15 | n/a | +0.15 | n/a |
  | Outside across both towers | 55.00 | none yet | ~54.9 | 54.9 | n/a | -0.10 (-0.18 %) | n/a |

  Reading (inference): XY slightly small (towers -0.02/-0.04, span -0.18 %), consistent with a little shrinkage; batch 1 T5 measures it properly. Height +0.15: the textured plate leaves a bumpy bottom face the jaws ride on, plus top-surface ridges; T4 cube and C5 settle Z.

- Go/no-go: none.
- Score: **hit** (predicted 0-3 strings, got 0).
- Print time and filament: slicer 25 min 58 s total (18 min 56 s printing) / 1.33 g, 0.40 m; actual about 25 min (second attempt).
- Next: dry roll 1 (80 °C, 12 h, bed), then batch 1 starts with T0b.
