# Print records

One file per print, calibration coupons included: `YYYY-MM-DD-<test-id>-<part-or-test>-<n>.md` (test IDs from
`../PLAN.md`, e.g. `2026-11-01-T4-elephant-foot-1.md`; real parts use `part` as the ID). Write the prediction
before printing; fill in the rest after. Add one line per scored prediction to `SCORES.md`.

```markdown
# <test ID> <part or test>, <date>

- Job: what loads it, which way, how hot it gets, what it must fit (prototype stand-in, calibration or real use).
- File: source and version (e.g. v0.95 `make_stl.py` output at commit <hash>, or `coupons/make_coupons.py` C4 at
  commit <hash>, or the slicer's built-in calibration).
- Printer: P2S firmware <version>, stock 0.4 nozzle, plate <type>, glue (yes/no), air deflector (in/out),
  door/lid (closed/open).
- Filament: Bambu PETG Matte <colour>, roll <n>, dried (hours at °C, or "from bag"), roll-bin RH %.
- Room: temperature °C, RH %.
- Slicer: Bambu Studio or OrcaSlicer <version>; profiles from `../profiles/` with versions.
- Settings that differ from the profiles: orientation, layer height, walls, infill, supports, modifiers.
- Prediction (written before printing, copied from `../PLAN.md`): the number and pass band, and why.
- Result: what was seen; photos kept on BigGuy.
- Measured (caliper <make>, mm, part at room temperature):

  | Feature | Nominal | Target band | Readings (3) | Mean | Spread | Error vs nominal | In band? |
  |---|---|---|---|---|---|---|---|

- Go/no-go with real hardware (pin, clip, screw, post): which went in, how it felt.
- Score: hit or miss against the prediction; if a miss, why.
- Print time and filament: slicer estimate vs. actual.
- Next: what changes, and in which profile version.
```
