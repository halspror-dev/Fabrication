# Dimensional accuracy for test-fit prototypes (P2S, Bambu PETG Matte)

Step 3 research, topic B (2026-10-29). Question: how close to the drawn size can the P2S print Fabrication's
test-fit stand-ins in Bambu PETG Matte, and how do we measure and correct the error with a 6 inch digital caliper?
Working target until Fabrication answers (`inbox/fabrication/2026-10-29-printing-fit-tolerances.md`): about 0.1 mm on
the collar, holes and slots, about 0.2 mm on plate outlines and sleeves.

Tags: **[S]** sourced (the URL is in the Sources list, the claim is copied from the saved page), **[I]** our
inference, **[M]** measured by us (none yet: nothing has been printed). Tags are inline, on every claim, because
the project rule labels each recommendation; anything without a URL behind it is [I]. Evidence pages are saved in
`/mnt/project-files/research/accuracy/` (not in git). Nothing from the design was sent anywhere: all searches and
fetches used generic terms.

## What to do, in order (feeds step 4)

1. **Calibrate flow first, compensate size second.** Bambu lists shrinkage, elephant foot, damp filament, untuned
   flow dynamics, holes near nozzle size, missing chamfers and the seam as things to check *before* touching XY
   hole/contour compensation [S1]. Ellis: tune extrusion multiplier first, then shrinkage; "Shrinkage occurs much
   less in the Z axis" [S10]. Topic A (P2S setup) owns the flow steps.
2. **Elephant foot coupon.** Bambu's procedure: 25 x 25 x 10 mm cube, elephant foot compensation 0, no brim, let
   the bed cool to room temperature before removing, measure mid-side (not corners) at the top and at the bed face,
   compensation = mean of (bottom - top) for X and Y [S2]. The value is plate-specific: re-measure after changing
   plates [S2]. P2S default for 0.20 mm layers is already 0.15 mm [S8], so the coupon tells us whether that is right.
3. **Shrinkage coupon (per filament).** Shrinkage % = measured / designed x 100, entered under Filament Settings >
   Basic Information > Shrinkage; 100 % means no scaling [S3]. In code it scales the part in XY and only the
   perimeter filament counts [S7]. Use a long dimension so the caliper's error is a small fraction of it [I]:
   Bambu suggests a 20 mm or 100 mm cube [S3]; a 100 mm bar in X and another in Y fits the 150 mm caliper [I].
4. **Contour compensation** if outlines are still off after shrinkage: contour compensation = (target - measured)/2
   per side, e.g. Bambu's spool test uses (55 - measured)/2 [S1].
5. **Hole and slot coupon.** Hole compensation grows each hole by the setting on every side, so the diameter grows
   by twice the value [S1]; compensation = (design - measured)/2 [I from S1]. Iterate by adding the next correction
   to the current value [S1]. Make the coupon ourselves, locally, with the real feature sizes (pin holes, tab and
   keeper slots) at nominal and in small steps around it [I]. FTC's similar advice: print 2.8 to 3.2 mm holes and
   see which fits [S12].
6. **Z coupon for the collar.** See "Layer height and the collar" below.
7. Re-validate with one reprint; record every number in `printing/tests/` [I].

## Error sources and the Bambu Studio setting for each

| Source | What it does | Setting (P2S default) | Tag |
|---|---|---|---|
| Material shrinkage | Part shrinks as it cools, mostly in X and Y; makes holes smaller | Filament > Shrinkage (100 %) | [S3][S1] |
| Elephant foot | First layer (sometimes a few) flares outward from bed heat and the weight above | Process > Quality > Precision > Elephant foot compensation (0.15 mm at 0.20 mm layers) | [S2][S8] |
| Hole shrinkage | Holes print small: STL facets sit inside the circle by cos(pi/n), the extrusion cuts the corner on arcs | X-Y hole compensation (0) | [S11][S7][S8] |
| Outline error | Outer size off after shrinkage is set | X-Y contour compensation (0) | [S1][S8] |
| Wall overlap | Slic3r-family slicers overlap walls; with inner/outer order the outer wall can be pushed out | Order of walls (inner/outer by default) | [S9][S7] |
| Seam | Can affect hole precision | Seam position (aligned), scarf seam | [S1][S8] |
| Layer rounding | Heights snap to whole layers | Precise Z height (off) | [S5][S7] |
| Damp PETG | Inconsistent extrusion, poorer adhesion and warping | Dry and store sealed (topic C) | [S1][S14] |
| Cold chamber air on PETG | Local fast cooling raises shrinkage stress and warping | Print Bambu's P2S air deflector, set to deflecting for PETG-only prints | [S14] |
| Loose belts | Circles print as ellipses; the P2S checks belt tension by a frequency sweep | Belt tensioning procedure | [S13] |

Notes on the Bambu Studio settings:
- **Auto circle contour-hole compensation does not cover our filament.** The code limits it to PLA Basic, PLA CF,
  PET CF, PETG CF and PETG HF [S7]; only complete horizontal circles under 50 mm; Bambu says it is mainly optimized
  for the H2D [S3][S6]. Bambu PETG Matte is not on the list, so we use manual hole compensation [I].
- **No polyholes in Bambu Studio.** OrcaSlicer has `hole_to_polyhole` (sides about twice the hole diameter in mm
  with a 0.4 mm nozzle) [S9]; that setting was not found in Bambu Studio's `PrintConfig.cpp` (master, fetched
  2026-10-29) [S7]. Feeds the slicer-choice topic.
- **Precise wall is hidden in Bambu Studio** (`precise_outer_wall` exists with mode `comDevelop`) [S7]; in OrcaSlicer
  it is a normal setting that zeroes the outer/inner wall overlap to improve size accuracy [S9].
- The Bambu PETG Matte profile sets flow ratio 0.95 [S8]; flow calibration (topic A) checks it on our printer.
- XY hole compensation only works on closed paths; layers where a hole opens to the side are not compensated and
  can show layer separation [S1]. Open-sided notches get only contour compensation [S1].
- Hole compensation is one number for every hole; users report small holes tighter and big ones looser with one
  setting [S16]. If our pin holes and slots need different values, use a per-object or per-part modifier or ask
  Fabrication to size them in CAD [I].

## Layer height and the collar (Z)

- Rounding rule: Bambu Studio keeps a top layer if its centre Z is below the model height, so with 0.20 mm layers a
  0.50 mm part prints 2 layers and a 0.51 mm part 3 [S5].
- Applied to the 2.286 mm collar with 0.20 mm layers: layer 11 centre 2.10 < 2.286 (kept), layer 12 centre 2.30 >
  2.286 (dropped), so **2.20 mm**, as `drawing-scripts/MEASUREMENTS.md` already predicts [I].
- **Precise Z height** retunes the last 5 layers so the sliced height matches the model; it is skipped below 6 layers
  or if a layer would leave the nozzle's layer-height limits [S5]; Bambu calls it experimental [S7]. For the collar:
  11 layers, the last 5 would each grow by about 0.017 mm to about 0.217 mm, inside the 0.08 to 0.28 mm range for a
  0.4 nozzle [S5] (the P2S 0.4 machine profile inherits min 0.08 / max 0.28 from `fdm_machine_common.json` [S8]),
  so it should give 2.286 mm in the slicer [I]. Check the preview height, then measure.
- Slicer height is not printed height: first-layer squish and elephant foot change the bottom [S2]. The Z coupon
  should print the collar thickness three ways (0.20 mm layers, 0.20 mm + precise Z, and 0.16 mm layers) and record
  measured thickness against the 2.58 mm gap under the can lip [I].

## Measuring with the 6 inch caliper

- Zero the caliper with the jaws closed and clean before each session; use light, constant force: too much force
  causes inaccuracy and poor repeatability; keep the part close to the scale and the jaws untilted [S15].
- Measure only after the part is at room temperature [S2]. Measure the middle of flat faces, not corners (flow
  dynamics bulge) or seams [S2][S10]. On the bed face, just touch the flared edge: pressing deforms it and reads
  small [S2]. Bambu asks for a caliper or micrometer with at least 0.01 mm resolution [S2].
- Take 3 readings of each feature and record the mean and spread, so a 0.1 mm target is judged against how well we
  can measure it [I].
- Small holes: the caliper's inside jaws read small holes poorly [I]. Hydraraptor gauged holes with drill shanks
  (and warns shanks run a little under the tip size) [S11]; Bambu's own test uses a known screw as a go/no-go and
  notes ISO 6g M6 screws are about 5.9 mm, not 6.0 [S1]. Use the real clevis pin, hitch clip and keeper as go/no-go
  gauges alongside caliper numbers [I].
- The caliper's accuracy spec is **unverified**: the NEIKO manual page and a review were blocked (403), and carlie
  named a Seiko. Record the caliper in every test record (already in `printing/STATE.md`).

## What accuracy to expect

- Bambu: "it is impossible to reach a perfect precision as both machine tolerances and reading tolerances impact
  the final dimensions" (this sentence is in a commented-out block of the XY compensation page source, so it may not
  be shown on the live page) [S1]. Ellis: "You will not reliably get 0.01mm tolerances everywhere" [S10].
- Forum and Reddit reports (claims, other printers): holes 0.23 mm undersized and round outlines 0.14 mm undersized
  on an H2D at default settings [S17]; a 20 mm cube printing 19.9 and a 40 mm cube 39.8 on an H2C, and one commenter
  says Bambu "has never promised better than +/- 0.2mm" (unsourced claim) [R2]; holes 1 to 6 mm printing 0 to 5.5 mm
  on an A1 at defaults, and a suggestion that outer/inner wall order is more accurate [R1].
- PETG literature: a PETG study found layer thickness, speed, temperature and raster width all affect dimensional
  error; its optimum was 50 mm/s, 0.1 mm layers, 230 C, 0.6 mm raster width [S18]. Different printer and slicer, so
  only a direction, not settings for us [I].
- Our reading: about 0.1 mm on holes and slots is plausible only after per-feature compensation measured on our own
  coupons; about 0.2 mm on outlines is plausible after shrinkage and elephant foot are set [I]. Step 5 measures it.

## Conflicts and open questions

- Bambu's shrinkage page says Shrinkage only scales outer XY size and does not affect holes [S3]; the code tooltip
  says the part is scaled in XY [S7], which would scale holes too [I]. Settle it on the hole coupon.
- Auto-circle "User Customized Offset": the wiki says positive makes the fit looser [S6]; the code tooltip says
  positive means tightening [S7]. Moot for PETG Matte, which the feature does not support.
- Elephant foot: Bambu's formula enters the full bottom-minus-top width difference [S2], while hole and contour
  compensation work per side [S1]. If elephant foot compensation also shrinks each side by the value, Bambu's
  formula would over-correct by 2x [I]. Settle it on the elephant foot cube: apply the value, reprint, re-measure.
- Elephant foot compensation layers (spreading the correction over several layers) is documented in OrcaSlicer [S9];
  not checked for Bambu Studio.

## Sources (all fetched 2026-10-29)

- S1 https://wiki.bambulab.com/en/software/bambu-studio/xy-hole-contour-compensation
- S2 https://wiki.bambulab.com/en/software/bambu-studio/parameter/elephant-foot
- S3 https://wiki.bambulab.com/en/knowledge-sharing/3d-prints-shrinkage
- S4 https://wiki.bambulab.com/en/software/bambu-studio/calibration_flow_rate (background for topic A)
- S5 https://wiki.bambulab.com/en/software/bambu-studio/layer-height
- S6 https://wiki.bambulab.com/en/software/bambu-studio/manual/auto-circle-contour-compensation
- S7 https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/PrintConfig.cpp
- S8 Bambu Studio profiles, `https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/`:
  `process/0.20mm Standard @BBL P2S.json`, `process/fdm_process_single_0.20.json`, `process/fdm_process_common.json`,
  `filament/Bambu PETG Matte @BBL P2S 0.4 nozzle.json`, `filament/Bambu PETG Matte @base.json`,
  `filament/fdm_filament_common.json`, `BBL.json`, `machine/Bambu Lab P2S 0.4 nozzle.json`,
  `machine/fdm_bbl_3dp_001_common.json`, `machine/fdm_machine_common.json`
- S9 https://www.orcaslicer.com/wiki/print_settings/quality/quality_settings_precision
- S10 https://ellis3dp.com/Print-Tuning-Guide/articles/extrusion_multiplier.html
- S11 https://hydraraptor.blogspot.com/2011/02/polyholes.html
- S12 https://ftc-docs.firstinspires.org/manufacturing/3d_printing/designing_and_slicing/tolerancing/tolerancing.html
- S13 https://wiki.bambulab.com/en/p2s/maintenance/belt-tension
- S14 https://wiki.bambulab.com/en/x2d/troubleshooting/preventing-warping-p2s-x2d
- S15 https://www.regionaltech.com.sg/quick-guide-for-calipers/ (reseller guide using Mitutoyo calipers)
- S16 https://forum.bambulab.com/t/hole-size-issues/100439 (forum)
- S17 https://forum.bambulab.com/t/x-y-hole-compensation-undersized-round-holes-and-outer-diameters/169100 (forum)
- S18 https://pmc.ncbi.nlm.nih.gov/articles/PMC9919812/ (peer-reviewed, abstract and introduction read)
- R1 https://www.reddit.com/r/BambuLab/comments/1rw5szs/best_practices_to_make_sure_hole_dimensions_are/.rss
- R2 https://www.reddit.com/r/BambuLab/comments/1ssjq8o/dimensional_accuracy_xy/.rss
- Also fetched, nothing used: Bambu wiki seam, printer calibration, P2S FAQ, P2S first-layer guide, model warping;
  Bambu forum "invisible errors"; Prusa elephant-foot article (page text did not extract); two Reddit search feeds
  and two more Reddit threads (one a Bambu Studio shrinkage-warning thread for PETG, one an A1 XY fault).

**Blocked or missing:** CNC Kitchen: the blog index fetched but listed nothing on holes or dimensional accuracy, so
no CNC Kitchen result is used. 404: Bambu wiki `elephant-foot` (old path), Ellis `dimensional_accuracy.html`,
Prusa `xy-size-compensation_112487`, OrcaSlicer `calibration/tolerance-calib`, Bambu Studio `quality` parameter
page, `Bambu PETG HF @BBL P2S.json`. 403: manuals.plus (NEIKO manual), machinistguides.com (NEIKO review), mdpi.com.
GitHub API listing for the Bambu Studio repo is blocked in this session; raw.githubusercontent.com works.

## Research cost

56 fetches (47 OK, 9 failed), about 13.2 MB saved, plus 7 web searches used only to find URLs (search summaries are not
used as evidence). About 40 minutes and about 100k tokens of this thread's context.
