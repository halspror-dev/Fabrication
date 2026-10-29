# Design-for-print and measured strength (PETG, 0.4 mm nozzle)

Roadmap step 3, topics "design-for-print" and "measured strength tests". Researched 2026-10-29. Every claim is tagged:
**[sourced]** = shown on a page we fetched (URL in the claim or its section), **[inference]** = our reasoning, not
yet measured. Nothing here is **[measured]** yet: the P2S has not printed anything. Evidence (raw pages, text, fetch
log) is in `/mnt/project-files/research/design-strength/` (project files), not in git.

## Our filament first: Bambu PETG Matte data sheet

Source: Bambu "TDS of Bambu PETG Matte V1.0",
https://store.bblcdn.eu/s8/default/240fb0c791fb4903a9d72934895e9a16/PETG_Matte.pdf (linked from
https://us.store.bambulab.com/products/petg-matte). Specimens: H2 printer, 0.4 mm nozzle, 245 °C nozzle, 70 °C bed,
221 mm/s, 100 % infill, filament dried 60 °C 8 h.

| Property | X-Y (in layer) | Z (across layers) | Z / X-Y |
|---|---|---|---|
| Tensile strength (ISO 527) | 42.9 ± 1 MPa | 30.1 ± 1 MPa | 70 % |
| Elongation at break | 13.8 ± 2.6 % | 6.5 ± 0.5 % | 47 % |
| Bending strength (ISO 178) | 65 ± 2.5 MPa | 47 ± 2.3 MPa | 72 % |
| Impact strength (ISO 179) | 32.6 ± 4.1 kJ/m² | 10.0 ± 1.5 kJ/m² | 31 % |
| Young's modulus | 3349 ± 130 MPa | 3174 ± 50 MPa | 95 % |

- **[sourced]** HDT 71.2 °C at 1.8 MPa, 72.3 °C at 0.45 MPa; Tg 71 °C; Vicat 75.7 °C; density 1.37 g/cm³.
- **[sourced]** Nozzle 230-260 °C, bed 65-75 °C, max overhang ~70°, max bridge ~30 mm, glue recommended, keep and
  print below 20 % RH. Resistance to organic solvent: "Not resistant to some organic solvents" (no list given;
  paint-thinner resistance stays with the PETG/solvent research topic).
- **[sourced]** Annealing, if wanted: 60-70 °C for 6-12 h, and "some models may deform or warp after annealing".
- **[sourced]** The store page says PETG Matte uses a modified formula for "easy support removal" and "greatly
  improves same-material support peel performance" (https://us.store.bambulab.com/products/petg-matte).
- **[sourced]** For comparison, Bambu PETG Basic TDS V3.0 lists tensile 32 ± 4 (X-Y) / 28 ± 4 MPa (Z), impact
  52.7 (X-Y) / 13.6 kJ/m² (Z), HDT 65 °C
  (https://cdn.shopify.com/s/files/1/0645/5876/0155/files/Bambu_PETG_Basic_Technical_Data_Sheet_b1d7a52e-ddf4-47b3-8e3e-694084b5197e.pdf).
- **[inference]** The number to design around is the Z impact strength: a knock that loads layer lines across their
  bond gets under a third of the in-plane toughness. Static tension across layers keeps about 70 %. Stiffness is
  nearly the same both ways, so orientation changes when a part breaks more than how much it bends.
- **[inference]** Bambu's specimens are 100 % infill on a tuned machine. Our parts with walls and sparse infill will
  be weaker than the table; use it to compare directions, not as an allowable stress.

## 1. Orientation vs. layer-line strength

- **[sourced]** CNC Kitchen, PETG temperature test: standing (across-layer) PETG peaked at 32 MPa at 245 °C against
  a lying reference of 55 MPa, so "about 60% of the base material strength" at best; 18 MPa at 200 °C, 30 at 230,
  24 at 260. "Printing too hot hurts layer adhesion as much as printing too cold"; "go to the lower end of the
  recommended range for looks and the upper end, even slightly above, for strength, and keep the filament dry"
  (https://www.cnckitchen.com/blog/the-influence-of-extrusion-temperature-on-layer-adhesion).
- **[sourced]** CNC Kitchen, transparent PETG: reference PETG 52 MPa flat and 34 standing (65 % layer adhesion);
  slow, hot-flow, 100 %-dense settings reached 59 / 44 MPa (75 %), past 80 % with 30 % cooling
  (https://www.cnckitchen.com/blog/transparent-fdm-3d-prints-are-clearly-stronger).
- **[sourced]** CNC Kitchen, Prusament comparison: hooks printed flat PLA 73 kg, ASA 57 kg, PETG 55 kg, but "PETG
  never snapped through, it just stretched"; layer adhesion PETG 25 kg (46 % of flat); PETG stiffness about 70 % of
  PLA; PETG gives at 80 °C in their heat test
  (https://www.cnckitchen.com/blog/comparing-pla-petg-amp-asa-feat-prusament).
- **[sourced]** Bembenek et al., Polymers 2022 (57 PET-G specimens): the order of influence on UTS was "spatial
  orientation->infill percentage->hot-end temperature"; for PET-G, lines infill gave the highest strength
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC9230522/).
- **[inference] Rule:** for every part, name the load direction first, then orient so that load runs along the
  layers (in X-Y), never pulls layers apart. If a part sees impact or bending across layers, that is the weakest
  case on the data sheet (31 % impact).
- **[inference] Rule:** for test-fit stand-ins, orientation is chosen for accuracy, not strength: lay flat plates flat
  (their thickness then becomes layer stacks, see the layer-height rule below) and keep fit-critical holes as
  vertical holes (axis along Z) so they are true circles in each layer.

## 2. Walls vs. infill

- **[sourced]** CNC Kitchen beginner guide: "more walls add more strength than more infill"; "Avoid adding too much
  infill, as you will eventually reach diminishing returns"
  (https://www.cnckitchen.com/blog/the-beginner-3d-printing-guide-i-wish-i-had).
- **[sourced]** CNC Kitchen extrusion width (PLA, standing hooks, 20 % infill): 2 perimeters at 100 % width failed at
  20 kg, 4 perimeters 33 kg, 3 at 133 % 37 kg, 2 at 200 % 39 kg; layer adhesion peaked near 150 % width
  (https://www.cnckitchen.com/blog/the-effect-of-extrusion-width-on-strength-and-quality-of-3d-prints).
- **[sourced]** CNC Kitchen big nozzles: "Strength is basically proportional to the amount of material"; at equal wall
  thickness 0.4 and 0.8 mm nozzles averaged the same, and a 0.4 mm nozzle at 210 % width matched the 0.8 mm one
  (https://www.cnckitchen.com/blog/big-nozzles-how-do-they-make-your-3d-prints-stronger).
- **[sourced]** HackSpace bending test: each extra 10 % infill added 1.5 kg at 0.64 m filament per kg; each two extra
  perimeters added 1.67 kg at 0.25 m filament per kg. Extra perimeters "didn't make the structure significantly
  stiffer" but let it flex further before breaking
  (https://hackspace.raspberrypi.com/articles/experiments-with-strong-3d-prints).
- **[sourced]** Bembenek et al.: raising PET-G infill raised UTS 24.42 % but lowered strength per weight 37.69 %
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC9230522/).
- **[inference] Rule:** strength per gram comes from walls. Start loaded parts at 4 walls and modest infill (15-25 %)
  rather than 2 walls and high infill; check in the slicer that thin features are fully walls (no sparse infill)
  anyway. Exact counts are set in step 4 and tested in step 5.

## 3. Layer height

- **[sourced]** CNC Kitchen (PLA, 0.4 mm nozzle): 0.05-0.2 mm layers all strong, 0.15 mm best, 0.3 mm held about half
  standing; "past a ratio of 2, so layers thicker than half the nozzle, strength starts to suffer"; thin layers did
  not bond better; 0.15 mm was the sweet spot for overhangs and bridging
  (https://www.cnckitchen.com/blog/the-influence-of-layer-height-on-the-strength-of-fdm-3d-prints).
- **[inference] Rule:** 0.2 mm or less on the 0.4 mm nozzle. For any part whose thickness is a fit dimension (the
  collar, shims, plates), pick a layer height that divides that thickness into whole layers, and read the sliced
  height in the preview (already flagged in `printing/STATE.md` from MEASUREMENTS.md).

## 4. Holes, tolerances and fits

(XY/hole compensation and shrinkage calibration belong to the dimensional-accuracy topic; only the design rules are
here.)

- **[sourced]** Bambu wiki: XY hole compensation changes only closed holes; contour compensation changes the outer
  size; "The hole diameter will increase by twice the compensation value"; in their example an M6 hole measured
  5.66 mm, which they call 0.24 mm undersized because they measure against the real screw ("typically around
  5.9 mm"), and half that value fixed it to 0.04 mm oversize (against the 6.0 mm drawn size it was 0.34 mm small); "it is impossible to reach a
  perfect precision"; calibration "is specific to each filament". Listed causes to fix first include shrinkage,
  elephant's foot, moist filament, untuned flow dynamics, holes near nozzle size ("holes below 1 mm can be
  challenging"), no chamfers or lead-ins, and the seam
  (https://wiki.bambulab.com/en/software/bambu-studio/xy-hole-contour-compensation).
- **[sourced]** Bambu wiki: filament "Shrinkage" in the filament profile scales outer X-Y only, as measured / designed
  × 100 %; "For high assembly requirements: We recommend calibrating the error for each model separately"; "Auto
  circle contour-hole compensation" is "mainly optimized for the H2D" and on other printers "you do not need to
  enable the feature" (https://wiki.bambulab.com/en/knowledge-sharing/3d-prints-shrinkage).
- **[sourced]** CNC Kitchen: printed holes came out about 0.25 mm small on a CORE One L (PLA) and 0.1 mm small on a
  Prusa with Prusament; horizontal holes can come out smaller at the top "due to material hanging down"
  (https://www.cnckitchen.com/blog/are-our-heat-set-insert-datasheets-wrong,
  https://www.cnckitchen.com/blog/threaded-inserts-for-3d-prints-cheap-vs-expensive,
  https://www.cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts).
- **[inference] Rules for this project:**
  - Holes print small; expect roughly 0.1-0.35 mm under on diameter (0.1 and 0.25 in CNC Kitchen's tests, 0.34
    against drawn size in Bambu's example) until our own coupon says otherwise. Coupon steps must span that range.
  - Fit holes (the 0.250 in, about 6.35 mm, pin holes) print with their axis vertical. A hole drawn for reaming can be left slightly
    undersize on purpose and reamed; a printed stand-in should instead be compensated in the slicer so it matches
    the drawn size, since its job is to show how the cut part will fit.
  - Never change a Fabrication dimension to make a print fit; compensate in the slicer profile, and send any
    design change to Fabrication's inbox.
  - Press/slide/snap clearances: we found no source tier above forums with numbers for PETG on a Bambu printer
    (Core77's snap-fit article returned a block page; BASF/Bayer manuals were only on Scribd copies, not fetched).
    So clearances come from our own fit coupon in step 4/5, not from a rule of thumb.

## 5. Bridging, overhangs and supports

- **[sourced]** Bambu wiki overhangs: under 45° from the bed, add supports; steeper than 45° usually needs none; for
  overhang quality lower nozzle temperature 5-10 °C within range, slow overhangs (10-60 mm/s), more cooling
  (https://wiki.bambulab.com/en/filament-acc/filament/print-quality/overhang).
- **[sourced]** PETG Matte TDS: max overhang ~70°, max bridge ~30 mm (see top). The TDS does not say how that angle
  is measured. **[inference]** Read from vertical it would mean about 20° from the bed, which is far beyond the
  wiki's 45° rule, so treat 45° from the bed as the design limit until our own overhang coupon says otherwise.
- **[sourced]** Bambu wiki bridges: bridge lines keep a round section and may not touch; more bridge flow helps them
  bond; thick bridges span further; shorter spans sag less
  (https://wiki.bambulab.com/en/software/bambu-studio/parameter/bridge).
- **[sourced]** Bambu wiki supports: with the same filament for model and support there must be a Top Z gap, a
  trade between easy removal and surface quality; with dedicated support filament the gap can be 0. For PETG the
  listed support filament is Bambu Support for PLA/PETG. Tree and normal supports exist; tree (manual) only on
  painted enforcers (https://wiki.bambulab.com/en/software/bambu-studio/support).
- **[inference] Rules:** no AMS means a second support filament needs a manual swap, so design and orient for no
  supports. Where supports cannot be avoided, keep them off fit faces (a supported face is rough and not to size)
  and paint them on manually. Bridges under 30 mm are fine; a hole drilled horizontally through a part is a bridge
  at its top, which is one more reason to print fit holes vertically.

## 6. Heat-set inserts and threads

v0.95 uses a clevis pin and hitch clip, not threads, so this is for later designs.

- **[sourced]** Soldering-iron temperature 10-20 °C above print temperature, which the source puts at about 245 °C
  (iron) for PETG; blind hole about 1 mm deeper than the
  insert; straight, not tapered; no chamfer; size the hole so the insert pre-seats with a bit of resistance
  (https://www.cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts).
- **[sourced]** M3 pull-out peaked about 1400 N in small holes; 4.2 mm CAD hole was the as-printed sweet spot
  (~90 % of max, no burr) on that printer; "For smaller inserts I simply add 0.2 to 0.3 mm in CAD"
  (https://www.cnckitchen.com/blog/are-our-heat-set-insert-datasheets-wrong).
- **[sourced]** In PETG, M3 torque-out: insert 3 Nm, nuts 2 Nm, direct screw and Helicoil 1 Nm; pull-out roughly equal
  (118-120 kg) for direct screw, insert and Helicoil, bottom-pocket nut 166 kg
  (https://www.cnckitchen.com/blog/helicoils-threaded-insets-and-embedded-nuts-in-3d-prints-strength-amp-strength-assessment).

## 7. Shrink and heat

- **[sourced]** Bambu wiki: shrinkage "is most noticeable along the X and Y axes"; measure a cube and set the filament
  shrinkage value (https://wiki.bambulab.com/en/knowledge-sharing/3d-prints-shrinkage).
- **[sourced]** PETG Matte HDT 71 °C at 1.8 MPa (TDS above).
- **[inference]** Sleeves left in a car or sun could approach that range; flag in the sleeve job statement, not a
  reason to change material now. Annealing is not worth it for test-fit parts because the TDS warns of warping.

## What this means for the v0.95 parts (all [inference], checked in step 6)

- **Sleeves (real use):** state the load first (hand grip squeezing the U, knocks against cans). Orient so the grip
  load bends the U within layers, not across them. Prefer more walls over infill; print at the upper half of the
  temperature range for layer bond, filament dried. The current "standing on the open side" orientation avoids
  supports; step 6 must check which way the squeeze loads the layer lines.
- **Plate stand-ins and shims:** accuracy over strength. Flat, holes vertical, whole-layer thicknesses, slicer
  compensation from our own coupons; strength settings can stay light (fewer walls is fine) to save filament.
- **Collar:** thickness rounds to whole layers; pick the layer height that lands on the drawn value.

## What step 4 should test (proposals, not results)

1. A fit coupon in PETG Matte: vertical holes at the drawn pin size and steps across 0 to +0.35 mm, a slot at the tab
   size, a horizontal hole for comparison. Measure, then set hole/contour compensation.
2. A layer-height check: a coupon at the collar thickness sliced at 0.2/0.16/0.12 mm, measured.
3. Optional strength check for the sleeves: two identical bars, one flat, one standing, snapped by hand or with a
   hanging weight, to confirm the TDS anisotropy on our printer.
4. An overhang coupon in PETG Matte (30-70° from the bed) to settle which overhang limit applies to us.

## Source log and cost

- Fetched with `.claude/skills/research/research.py` (RESEARCH_DIR `/mnt/project-files/research/design-strength/`).
  30 logged fetches: 27 OK, 3 failed, plus 1 that never completed.
- **Failed / blocked:** Core77 snap-fit article (block page); two guessed Bambu wiki URLs (404, not used);
  one Reddit RSS search (r/3Dprinting, press-fit) did not complete (rate-limit wait, stopped).
- **Reddit:** one r/BambuLab RSS search fetched; nothing in it bore on these rules, so no claim here uses it.
- **Search:** about 16 web searches, used only to find URLs; no claim comes from a search snippet.
- **Not read:** BASF/Bayer snap-fit manuals (only Scribd copies), PETG Matte SDS, CNC Kitchen videos (blog text only).
- **Token cost:** about 95k tokens of this thread's context for research and writing (session counter; no dollar
  figure available inside the thread).
