# Can measurements

Real cans, measured by carlie with the NEIKO digital caliper. Inches in brackets. Checked against the current
version without changing geometry (v0.95 is locked until the print test).

| Date | Can | What | Reading | Notes |
|---|---|---|---|---|
| 2026-10-27 | Rust-Oleum (main test can) | Gap under the valve-cup lip, underside of the rolled lip down to the can shoulder | 2.58 mm (0.1016) | 1 reading; spot around the lip not recorded |

## v0.95 against these numbers

- Only the collar goes under the lip. The keeper (0.125) sits on top of the collar, level with the lip; the shims, post
  heads and hitch clips are all on top or well outside the can top.
- Collar 0.090 = 2.286 mm (the collar STL measures 2.286 mm). Rust-Oleum 2.58 mm gap: **fits, 0.29 mm (0.012) to
  spare.** That is under the 0.03 clearance `check3d.py` asks for; the drawn can has a 0.13 (3.3 mm) gap, so the
  model shows 0.047 where the real can gives about 0.012.
- The old 1/8 (3.175 mm) metal collar is 0.60 mm too thick, which matches the v1 fit test.
- The v0.7 "two dimes" note was carlie's eyeball estimate (one dime held up looked like about half the gap), not a
  fit test, so it does not conflict with this reading.
- Printing: the slicer rounds 2.286 mm to whole layers. At 0.20 mm layers it should come out 2.2 mm (0.38 mm spare);
  2.4 mm would leave 0.18 mm. Check the height in the slicer preview.
