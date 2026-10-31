# T0a stringing towers, from the bag (prediction written 2026-10-30)

File named for the day the prediction was written; the print date goes in Result.

- Job: calibration. Shows whether roll 1 strings straight from its sealed bag, before drying. No load, no fit.
- File: `../coupons/make_coupons.py` C1 (two 5 mm towers, 20 mm tall, 50 mm apart on a 0.6 mm strip), commit ____.
- Printer: P2S firmware ____, stock 0.4 nozzle, plate ____, glue ____, air deflector out (not printed yet), door
  closed, lid on.
- Filament: Bambu PETG Matte white, roll 1, from the bag (not dried), bag sealed with desiccant: yes.
- Room: ____ °C, ____ % RH.
- Slicer: Bambu Studio ____; stock presets (`bundle-p2s-stock-v0`): `0.20mm Standard @BBL P2S`,
  `Bambu PETG Matte @BBL P2S 0.4 nozzle`. Print-start advanced options auto (flow dynamics on).
- Settings that differ from the profiles: none. Placed where Studio drops it, not rotated.
- Prediction: few or no strings (0-3) between the towers. Why: fresh sealed roll; Bambu says PETG Matte needs drying
  only after more than 72 h at 50% RH (`../research/petg.md` S2) **[S]**/**[I]**. Compared with T0b (same towers,
  dried roll) in batch 1.
- Result: printed ____; strings ____ (0, 1-3, 4-10, more); photo on BigGuy.
- Measured (caliper ____, mm, room temperature), information only:

  | Feature | Nominal | Target band | Readings (3) | Mean | Spread | Error vs nominal | In band? |
  |---|---|---|---|---|---|---|---|
  | Tower 1 diameter, mid-height | 5.00 | none yet | | | | | |
  | Tower 2 diameter, mid-height | 5.00 | none yet | | | | | |
  | Tower 1 height | 20.00 | none yet | | | | | |
  | Tower 2 height | 20.00 | none yet | | | | | |

- Go/no-go: none.
- Score: ____ (add to `SCORES.md`).
- Print time and filament: slicer 25 min 58 s total (18 min 56 s printing) / 1.33 g, 0.40 m; actual ____ min.
- Next: dry roll 1 (80 °C, 12 h, bed), then batch 1 starts with T0b.
