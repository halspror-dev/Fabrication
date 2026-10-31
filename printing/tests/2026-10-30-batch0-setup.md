# Batch 0 setup checks, 2026-10-30

Not a print: the first-day facts every later record depends on (`../PLAN.md` batch 0). carlie's steps:
project file `plans/batch0-steps.md`. Blanks are filled in from carlie's answers by the next batch thread.

- Printer: P2S, stock 0.4 nozzle, never online, USB-drive printing only (`../research/setup-slicer.md` §4a).
  Initial on-screen calibration: done 2026-10-30 (second run in progress when this was written).
- Firmware: **01.00.05.00** (carlie screen photo 2026-10-30; no Wi-Fi, no account, no USB drive yet). Older than the
  latest listed, 01.03.00.00 (2026-09-21), so update offline by USB before T0a. Updated 2026-10-31: **01.03.00.00** (screen photo). Speed mode Standard.
- Build plate type: Textured PEI (Studio selection 2026-10-31).
- Flash drive formatted on the printer (FAT32): ____.
- Bambu Studio version: Help > About wouldn't show it; update check says latest (2026-10-31). Network plugin: not installed. Login: none.
- Stock `Bambu PETG Matte @BBL P2S 0.4 nozzle` shows (Studio screenshots 2026-10-31): nozzle **240** °C (first and other layers), Textured PEI plate **70** °C, recommended nozzle range 230-270, softening temp 70, part fan 30-60 %, first 3 layers fan 0, aux fan 0. Process `0.20mm Standard @BBL P2S`, seam Aligned. Flow ratio
  ____, max volumetric speed ____ mm³/s. Expected 240, 70, 0.95, 13 **[S]** `../research/petg.md`.
- Calibration tab offline: ____ (list, or greyed out).
- Develop mode shows Precise wall for the P2S: ____.
- v0 preset bundle exported: ____ (goes to `../profiles/bundle-p2s-stock-v0.bbscfg`).
- OrcaSlicer: not needed until batch 2 (T7); install then.
- Filament: roll 1 colour **white** (easy to write on); bag perfectly sealed with desiccant: **yes** (2026-10-31).
- Caliper: make ____ (Seiko or NEIKO?); 1/4" clevis pin shank ____ / ____ / ____ mm (expect about 6.30-6.35 **[I]**).
- Room: ____ °C, ____ % RH (hygrometer: ____).
- Drying decision **[S]**: Bambu PETG Matte TDS V1.0 gives "Blast Drying Oven: 65 °C, 8 h" and "X Series & P Series
  & H2 Series Printer Heatbed: 80 °C, 12 h". The box label's 65 °C 8 h is the oven line, so it doesn't conflict with
  `../research/petg.md`: roll 1 dries on the bed at 80 °C, 12 h, under its box.
- Roll 1 dried: started ____, 80 °C 12 h, flipped at 6 h ____, sealed with desiccant after ____.

## Coupons
`../coupons/make_coupons.py` written 2026-10-30. Checked in the cloud container: all 11 STLs watertight, one body;
C4 cross-section at mid-height reads every hole and slot at its drawn size (pins 6.350 ×2, 6.450, 6.250; clip 3.175;
screw 5.105; slots 3.251, 5.029, 3.429 × 15.0; 4-lobe hole 6.350 × 19.050). Only the plain C1 STL left the
container (to carlie, for T0a). C4 and C5 (`--private`) get generated on BigGuy outside OneDrive before batch 2.
