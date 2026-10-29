# Print records

One file per print, calibration coupons included: `YYYY-MM-DD-<part-or-test>-<n>.md`.

```markdown
# <part or test>, <date>

- Job: what loads it, which way, how hot it gets, what it must fit (prototype stand-in or real use).
- File: source and version (e.g. v0.95 `make_stl.py` output, commit <hash>), or the calibration model used.
- Printer / filament: P2S, nozzle, filament brand, colour, spool, dried (yes/no, how long).
- Slicer and profiles: slicer + version; printer, filament and process profile files from `../profiles/`.
- Settings that differ from the profiles: orientation, layer height, walls, infill, supports, modifiers.
- Prediction (written before printing): the number expected and why.
- Result: pass/fail, what was seen, photos kept locally.
- Measured (calipers, mm): nominal | reading(s) | error, for every feature that matters.
- Print time and filament used (slicer estimate vs. actual).
- Next: what changes, and in which profile version.
```
