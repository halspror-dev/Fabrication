# T4 elephant foot cube + T5 shrink bars (+ T1 flow dynamics), 2026-10-31 (prediction written before printing)

One plate, three tests: T1 flow dynamics runs at print start, T4 is the cube, T5 the two bars.

- Job: calibration. T4 measures the bottom flare with elephant foot compensation 0; T5 measures X and Y shrinkage
  over 100 mm. No load, no fit.
- File: `../coupons/make_coupons.py` B1 (C2 cube 25 × 25 × 10 plus two C3 bars 100 × 10 × 4, X bar along the front,
  Y bar along the left), commit ____. Plain shapes, no design sizes.
- Printer: P2S firmware 01.03.00.00, stock 0.4 nozzle, Textured PEI washed then glue stick, air deflector ____
  (in after T3), door closed, lid on.
- Filament: Bambu PETG Matte white, roll 1, from bag (not dried; T0a 0 strings), resealed between sessions.
- Room: ____ °C, ____ % RH.
- Slicer: Bambu Studio; printer/filament stock (`bundle-p2s-stock-v0`); process `process-fit-0.20-v0` = `0.20mm
  Standard @BBL P2S` + 3 walls + elephant foot compensation 0 (only for this test; v1 sets it from the result),
  supports off, fixed layers. Flow ratio stock (____). T2 flow rate runs after this plate: flow changes widths by
  hundredths, so neither the flare (bottom minus top) nor 100 mm lengths should move noticeably **[I]**.
- Print-start options: flow dynamics calibration on (T1), timelapse off.
- Predictions (copied from `../PLAN.md` batch 1):
  - T1: runs and stores a K value on the printer; no number predicted **[S]**.
  - T4: cube bottom minus top 0.10-0.25 mm per axis **[I]** (stock 0.15 sits in that band, `accuracy.md` **[S]**).
  - T5: each bar 99.5-100.0 mm (0-0.5 % shrink) **[I]**. T0a hinted -0.18 % over 55 mm.
- Result: ____.
- Measured (caliper NEIKO, mm, room temperature):

  | Feature | Nominal | Target band | Readings (3) | Mean | Spread | Error vs nominal | In band? |
  |---|---|---|---|---|---|---|---|
  | Cube X, bottom (flare) | 25.00 | | | | | | |
  | Cube X, near top | 25.00 | | | | | | |
  | Cube Y, bottom (flare) | 25.00 | | | | | | |
  | Cube Y, near top | 25.00 | | | | | | |
  | Flare X (bottom - top) | | 0.10-0.25 | | | | | |
  | Flare Y (bottom - top) | | 0.10-0.25 | | | | | |
  | Cube height | 10.00 | none | | | | | |
  | Bar X length | 100.00 | 99.5-100.0 | | | | | |
  | Bar Y length | 100.00 | 99.5-100.0 | | | | | |

- T1 K value (printer screen, if shown): ____.
- Score: ____.
- Print time and filament: ____.
- Next: elephant foot compensation into `process-fit-0.20-v1`: Bambu enters the full bottom-minus-top difference [S2];
  apply it, reprint the cube, and check it does not over-correct 2x (`../research/accuracy.md` open point) [I]. Shrinkage %
  = measured / 100 × 100 into `filament-petg-matte-p2s-v1`.
