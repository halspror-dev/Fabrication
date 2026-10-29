# Calibration and test plan (roadmap step 4)

Written 2026-10-29, before anything is printed. Step 5 works through it one batch per thread: each batch thread
reads `STATE.md` and this file, hands carlie the steps, records every print in `tests/`, scores it in
`tests/SCORES.md`, commits profile changes in `profiles/`, ticks the batch below and resolves. Nothing here is
measured yet.

Tags: **[S]** sourced (in the `research/` file named, which holds the URL), **[F]** Fabrication's fit targets
(project-notes `archive/printing/2026-10-29-fabrication-fit-tolerances.md`), **[I]** our inference.
Research files: `petg.md`, `design-strength.md`, `setup-slicer.md`, `accuracy.md`.

## Rules for every batch

- **Predict, then print.** Every test below has its prediction and pass band written now. Don't edit a prediction
  after printing; score it hit/miss in `tests/SCORES.md` and write why it missed. **[I]**
- **One change at a time.** A test changes one setting against the last good profile; everything else stays on the
  named profile version. **[I]**
- **Measure the same way every time** **[S]** `accuracy.md`: part at room temperature, caliper zeroed with clean
  closed jaws, light even force, middle of flat faces (not corners or the seam), 3 readings per feature, record mean
  and spread. On the bed face just touch the flare. First session: confirm which caliper it is (carlie said Seiko,
  `MEASUREMENTS.md` says NEIKO) and check it against the 1/4" clevis pin shank (should read about 6.3 mm). **[I]**
- **Real hardware is the final gauge** for fit features: the clevis pin, hitch clips, 10-24 screws and keeper posts
  as go/no-go, alongside caliper numbers **[S]** `accuracy.md`, **[F]**.
- **Same conditions as the real parts:** stock 0.4 nozzle, same plate, glue stick, the dried roll, door and lid as
  set in batch 1. Record room temperature and humidity. **[I]**
- **Privacy:** coupons that carry Fabrication sizes are generated on BigGuy from `printing/coupons/` (a script, no
  STLs in git), sliced locally, sent over LAN or USB. Never MakerWorld, cloud printing or a logged-in slicer. **[S]**
  `setup-slicer.md` §4.
- **Threads don't wait on carlie.** A batch thread hands carlie the steps, records what is already measured, commits
  and resolves; her results start the next fresh thread. Her decisions (the login question in batch 0, the paint
  and thinner names before batch 3) are asked up front, not waited on mid-thread. **[I]**
- **Stop rule:** two failed fixes of the same thing: write it in `STATE.md` "What failed" and start a fresh thread.

## Fit targets (from Fabrication, the pass bands below use these) [F]

| # | Feature | Drawn | Print target |
|---|---|---|---|
| 1 | Collar thickness | 2.286 mm | 2.20 (11 layers at 0.20); OK 2.10-2.29; **never above 2.29** |
| 2 | Keeper, frame, trigger plate thickness | 3.175 mm | 3.10-3.20 |
| 3 | Pivot and lock pin holes | 6.35 mm | 6.35-6.45, real pin slides in by hand, no rock |
| 3a | Pivot lobe neck | 4.83 mm | under 5.3 |
| 4 | Collar tab slots | 3.25 mm | 3.25-3.35, never under the printed plate thickness |
| 5 | Keeper guide slots | 5.03 mm | 4.95-5.15, slides over 3/16" posts full travel |
| 6 | Hitch-clip holes | 3.18 mm | 2.6-3.3 |
| 7 | 10-24 screw holes | 5.11 mm | 5.0-5.3 |
| 8 | Sleeve plate slot | 3.43 mm | 3.30-3.50 |
| 9 | Collar keyhole edges | per STL | within 0.1 |
| 10 | Other outlines, sleeve outer shape | per STL | within 0.2-0.3 |

Shims (not in Fabrication's table): 1/32" = 0.794 mm thick, slices to 0.80 at 0.20 layers **[I]** from the
rounding rule in `accuracy.md`.

## Batches

Status: `[ ]` not started, `[x]` done (with the date and test record names).

### Batch 0: first day, no coupons yet [ ]

Where: front porch to the bench, printer screen, BigGuy. Source for every step: `setup-slicer.md` §1, §4, §5 **[S]**
unless tagged.

1. **Unbox** per Bambu's P2S unboxing page. Leave the foam under the bed until the first calibration is done; build
   plate on the bed; a container under the purge chute; a FAT32 USB drive in the printer.
   Look in the filament box: is each roll's bag sealed with a desiccant pack? (`petg.md` open question.)
2. **Power on, Wi-Fi, then LAN Only before any login.** Printer screen: Settings > LAN Only on, Developer Mode
   **off**. If the printer refuses to go further without a Bambu account login, that's carlie's call at the
   printer; our recommendation: a one-time login is acceptable because nothing is sliced yet, then switch to LAN Only
   straight away and never cloud-print **[I]**. Optional: reserve the printer's IP in the router.
3. **Initial calibration** on the screen (bed leveling, vibration compensation, motor noise cancellation, nozzle
   offset). Then remove the foam under the bed.
4. **Firmware:** compare Settings > Firmware with the P2S release history page (latest listed 01.03.00.00,
   2026-09-21). If behind, update offline from the USB drive (20-30 min, don't cut power), then rerun motor noise
   cancellation.
5. **BigGuy: Bambu Studio.** Install from bambulab.com/en/download/studio, skip the login, Device tab, bind the
   printer with its access code (lock icon). Record the Studio version.
   Check and write down in the batch 0 record (each is an open question from step 3):
   - Studio sees and controls the printer while logged out (yes/no).
   - The `Bambu PETG Matte @BBL P2S 0.4 nozzle` preset shows nozzle 240 °C, flow ratio 0.95, max volumetric speed
     13 mm³/s, plate 70 °C (which of the three stored values the stock hotend uses).
   - The Calibration tab for the P2S lists: flow dynamics auto/manual, flow rate, and any temp tower, max flowrate,
     retraction or tolerance tests.
   - Develop mode (Preferences) shows **Precise wall** for the P2S (yes/no).
6. **Export the v0 bundle** (stock, untouched presets): Export Preset Bundle into `printing/profiles/` as
   `bundle-p2s-stock-v0.bbscfg`. That is the baseline every later version is diffed against.
7. **BigGuy: OrcaSlicer**, for the Studio-vs-Orca hole test only: install, don't install the Bambu network plugin,
   don't log in, never connect it to the printer; files go by USB drive. Record the version.
8. **Coupons:** the batch 0 thread writes `printing/coupons/make_coupons.py` (manifold3d, like `make_stl.py`) for
   coupons C2 to C6 below, then runs it on BigGuy (Remote Control session) into a local folder. STLs stay on BigGuy.
9. **Room and filament:** a cheap hygrometer next to the printer and in the filament bin; record both. Open roll 1
   only.
10. **First print, from the bag: stringing check T0a** (two thin towers, see C1) on roll 1 straight from the bag,
    stock profile. Then put roll 1 on the bed to dry overnight: printer screen Dry Filament, 80 °C, 12 h, spool on
    the plate under its box, flip at 6 h if awake **[S]** `petg.md` §3.

### Batch 1: flow and first-layer basics (roll 1 dried) [ ]

Order from `setup-slicer.md` §1 (flow dynamics before flow rate) and `accuracy.md` (flow first, size second) **[S]**.
Wash the plate (dish soap, water), glue stick on, roll 1 dried.

| ID | Test | What it proves | Prediction (pass band) | Profile change |
|---|---|---|---|---|
| T0b | Stringing towers C1, dried roll 1, stock profile | Whether this roll in this room needs drying | Fewer or equal strings than T0a; if T0a was already clean, drying is optional for fresh rolls **[I]** (Bambu says PETG Matte needs drying only after >72 h at 50% RH, `petg.md` **[S]**) | none; the result sets the drying rule in `STATE.md` |
| T1 | Flow dynamics, Studio Calibration tab, auto if the P2S offers it, else manual PA line | Pressure advance (K) for this filament | Runs and stores a K value in the printer; record it **[S]**. No number predicted: no source gave a PETG Matte K for the P2S | K saved on the printer, noted in `filament-petg-matte-p2s-v1` |
| T2 | Flow rate, coarse then fine (manual, Studio) | Flow ratio | Fine pass lands 0.93-0.97 around the stock 0.95 **[S]** (`petg.md`: PETG-like 0.93-0.96) | flow ratio |
| T3 | Bambu air deflector (download the .3mf from Bambu's "preventing warping P2S/X2D" page, print only the shorter one, in PETG) | Not a test: the accessory Bambu recommends for PETG-only prints | Prints clean on the stock profile **[S]** `accuracy.md` S14 | install it in the deflecting position for every PETG print |
| T4 | Elephant foot cube C2 on `process-fit-0.20-v0`: 25 × 25 × 10 mm, elephant foot compensation 0, no brim, cool on the bed | Bottom flare to compensate | Bottom minus top 0.10-0.25 mm per axis **[I]** (the stock 0.15 sits in that band, `accuracy.md` **[S]**) | elephant foot compensation (process) |
| T5 | Shrink bars C3 on `process-fit-0.20-v0`: 100 × 10 × 4 mm, one along X, one along Y, same plate as T4 | Filament shrinkage in X and Y | 99.5-100.0 mm (0-0.5 % shrink) **[I]**, which includes forum reports of 19.9 on 20 mm cubes (`accuracy.md` R2, a forum report) | shrinkage % (filament) = measured / 100 × 100 |

Before T4, save `process-fit-0.20-v0`: the stock process plus the fixed choices in the profile table below (3
walls, fixed layer height, no supports), so the cube is measured on the walls the real parts use. After batch 1:
commit `filament-petg-matte-p2s-v1` (flow ratio, shrinkage, K noted) and `process-fit-0.20-v1` (elephant foot only). Reprint C2 once with the new values: the cube's bottom must read within 0.05 mm of its top.
This also settles the step 3 doubt whether Bambu's elephant-foot formula over-corrects by 2× (`accuracy.md`).

### Batch 2: fit and Z (the numbers the v0.95 test depends on) [ ]

| ID | Test | What it proves | Prediction (pass band) | Profile change |
|---|---|---|---|---|
| T6 | Fit coupon C4 in Bambu Studio, `process-fit-0.20-v1`, XY hole and contour compensation 0 | How far each fit feature prints off drawn | Holes small: 6.35 → 6.00-6.25; 3.18 → 2.85-3.10; 5.11 → 4.80-5.05 (0.1-0.35 mm under, `design-strength.md` **[S]**/**[I]**). Slots 0.05-0.25 under **[I]**. Outline within 0.15 after shrinkage **[I]** | none (baseline) |
| T6b | Only if T5 set shrinkage away from 100 %: C4 in Studio again with shrinkage 100 % | Settles the `accuracy.md` conflict: does filament shrinkage scale holes too (code tooltip) or only outlines (wiki)? | Holes change by the shrinkage % (they are scaled) **[I]** from the code tooltip **[S]** | none; write the answer in `STATE.md`, since it decides whether a new roll's shrinkage shifts every hole |
| T7 | Same coupon C4 in OrcaSlicer, same filament and process values, polyholes on, precise wall on, compensation 0, by USB drive | Whether Orca's polyholes and precise wall beat Studio. This is deliberately a package (the question is which slicer setup to use, not which setting); if Orca wins and Studio's develop mode shows Precise wall (batch 0), T7b prints C4 in Studio with Precise wall on to see how much of the gain Studio can get | Orca holes 0.05-0.15 mm closer to drawn than T6 **[I]** (polyholes fix facet loss, `accuracy.md` S9/S11 **[S]**). Also proves Orca files print from USB on the P2S (unconfirmed, `setup-slicer.md`) | none |
| T8 | C4 again in each slicer with compensation = (target − measured) / 2, target = middle of the Fabrication band (pins 6.40) **[S]** `accuracy.md` | Whether one hole compensation value lands every fit feature in its band | Pin holes 6.35-6.45 and every row of the target table in band in at least one slicer **[I]** | XY hole and contour compensation, `process-fit-0.20-v2` |
| T9 | Real hardware on T8: clevis pin in each pin hole, hitch clip in each clip hole, screws, keeper post through the keeper slot, plate edge in the tab and sleeve slots | Function, not just numbers | All go, pin with no rock **[F]** | none |
| T10 | Z coupon C5 at 0.20 layers: collar-thickness disc (a) plain, (b) Precise Z height on; one plate-thickness square; one shim | Printed thickness vs. whole-layer rounding | Slicer preview (a) 2.20, (b) 2.29, plate 3.20, shim 0.80 **[S]**/**[I]** `accuracy.md`. Measured (a) 2.15-2.25, plate 3.12-3.22, shim 0.75-0.85 **[I]**. Pass is Fabrication's band, not the prediction: collar 2.10-2.29, plate 3.10-3.20 **[F]**; a plate over 3.20 goes to Fabrication (it must still enter the 3.25 slot) | none if (a) passes; Precise Z stays **off** for the collar |

Decisions written down after batch 2:
- **Slicer for the fit-critical stand-ins** (collar, keeper, frame, trigger): Orca only if T8 shows it holds every
  row in band and Studio doesn't, or its mean hole error is at least 0.05 mm smaller. Otherwise Studio for
  everything. **[I]** (`setup-slicer.md` tie-break)
- **One value or several:** if no single hole compensation puts both the 6.35 pin holes and the 3.25 tab slots in
  band (users report small holes tighter than big ones with one value, `accuracy.md`, a forum report), try outer/inner
  wall order once (`accuracy.md` R1, a forum report); if that fails too, send a note to Fabrication's inbox with the
  measured numbers rather than changing anything in the design. **[F]**
- **Collar:** print at 0.20 with Precise Z off (2.20, Fabrication's "err thinner"). Precise Z (b) is measured only
  so we know; it is too close to the 2.29 cap to use. **[F]**/**[I]**
- **Pin holes that print tight on the real part:** open with a 1/4" drill bit by hand, per Fabrication. **[F]**

### Batch 3: overhangs, strength, solvents (only the sleeves need the last two) [ ]

| ID | Test | What it proves | Prediction (pass band) |
|---|---|---|---|
| T11 | Overhang coupon C6: ramps at 30, 40, 45, 50, 60, 70° from the bed, no supports, `process-fit-0.20-v2` | The overhang limit for this filament on this printer | Clean to 45°, droopy but usable to about 60°, poor at 70° **[I]**; Bambu's rule is 45° (`design-strength.md` **[S]**); the TDS "~70°" is ambiguous |
| T12 | Strength bars C7: 60 × 10 × 6 mm, 2 flat at 240 °C, 2 standing at 240 °C, 2 standing at 250 °C (after its own flow dynamics run at 250 °C, so K matches), 4 walls, 25 % infill | Layer-line weakness and whether hotter printing helps bonding on our printer | Standing bars break at a layer line at 0.6-0.8 of the flat bars' load (TDS Z/XY: tensile 70 %, bending 72 % **[S]**); 250 °C standing beats 240 °C standing (CNC Kitchen, `design-strength.md` **[S]**). Load: hang a bucket from the bar's end with the other end clamped, add water until it breaks, weigh the bucket. Flat bars bend a lot before breaking (CNC Kitchen: PETG stretched) **[S]** |
| T13 | Solvent coupons C8: 7 bars in the sleeve's wall settings. 2 dry controls; 2 wiped daily for 7 days with carlie's spray paint; 2 wiped with carlie's thinner (wet rag, 10 s); 1 half-soaked 24 h in the thinner | Whether PETG Matte survives the sleeves' real chemicals | Paint wipes: surface marks only, no swelling over 0.05 mm, bends like the controls. Mineral-spirits thinner: same. Lacquer thinner (ketones/acetates): softening or whitening, and the soak bar fails **[I]** from `petg.md` §5 (Kaptan 2025 acetone result **[S]**). Any common spray paint and thinner will do (carlie 2026-10-29: product, general aerosol mess); record which |

After T12 the sleeve process gets its temperature (240 or 250 °C; 250 needs its own flow dynamics run, `setup-slicer.md`
**[S]**). If T13 fails, the sleeves need another material; that becomes a question to carlie (`petg.md` §6). The
7-day wipe runs alongside batch 4.

### Batch 4: validation, then hand over to step 7 [ ]

| ID | Test | Prediction |
|---|---|---|
| T14 | Fit coupon C4 once more on the final `process-fit` and filament profiles, sliced from the committed profiles with the CLI of whichever slicer batch 2 chose for the fit parts (Studio or Orca, both have one, `setup-slicer.md` §2-3), on BigGuy | Every row of the fit table in band, the same as T8 within 0.05 mm (repeatability) **[I]** |

If T14 passes, the profiles are frozen for the v0.95 test print (step 7) and `STATE.md` says so.

## Coupons (made locally by `printing/coupons/make_coupons.py`, written in batch 0)

| ID | Shape | Notes |
|---|---|---|
| C1 | Two 5 mm round towers, 20 mm tall, 50 mm apart, on a thin base | Stringing check; no Fabrication sizes |
| C2 | 25 × 25 × 10 mm cube | Bambu's elephant foot procedure (`accuracy.md` S2) |
| C3 | 100 × 10 × 4 mm bar | One along X, one along Y |
| C4 | Fit plate, 3.175 mm thick (prints 3.20), about 70 × 45 mm outline: vertical holes at 6.35 (two, plus 6.45 and 6.25 beside them), 3.18, 5.11; slots 15 mm long at 3.25, 5.03 and 3.43 wide; plus a 10 mm-wide block with one horizontal 6.35 hole for comparison | Holes as vertical as they are in the parts; sizes from the fit table. Real sizes stay off the internet |
| C5 | 20 mm discs at 2.286 mm (two: plain and Precise Z), a 20 mm square at 3.175 mm, a shim at 0.794 mm | Z rounding |
| C6 | Overhang ramps 30-70° | No Fabrication sizes |
| C7 | 60 × 10 × 6 mm bars | Strength |
| C8 | 60 × 10 × 3 mm bars | Solvent wipes, sleeve wall settings |

## Baseline profiles to build (in `profiles/`, each export committed with the test record that justifies it)

| Profile | Starts from | Set by | Used for |
|---|---|---|---|
| `bundle-p2s-stock-v0` | Stock P2S 0.4 printer, `Bambu PETG Matte @BBL P2S 0.4 nozzle`, `0.20mm Standard @BBL P2S` | Batch 0 | Baseline to diff against; Bambu's own calibration prints |
| `filament-petg-matte-p2s-v1` | Stock PETG Matte preset | T1 (K noted), T2 flow ratio, T5 shrinkage | All prints |
| `process-fit-0.20` v0, v1, v2 | `0.20mm Standard @BBL P2S` (0.20 layers, first layer 0.20, 2 walls, 15 % grid, top 5, bottom 3, elephant foot 0.15, seam aligned **[S]** `accuracy.md` S8) | v0 (before T4): 3 walls so holes and slots sit in solid wall, fixed layer height (no variable layers), Precise Z off, no supports **[I]**; v1: T4 elephant foot; v2: T8 hole and contour compensation | Collar, keeper, frame, trigger, shims, coupons |
| `process-sleeve-0.20-v1` | Same | 4 walls, 25 % infill (walls beat infill per gram, `design-strength.md` **[S]**), temperature from T12; orientation per part from the step 6 review | Grip and trigger sleeves |

Each change bumps the version and names its test record in the commit message (`profiles/README.md`).

## Order with the rest of the roadmap

Batches 0-4 are step 5, one thread each, starting from `STATE.md` and this file; they never wait on carlie inside a
thread (see the rule above). Step 6 (the STL review) needs no printer and can run any time. Step 7 (the v0.95 test print) waits for T14.
