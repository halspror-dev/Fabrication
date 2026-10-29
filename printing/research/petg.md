# PETG research: settings, drying, storage, solvents, other materials

Roadmap step 3, topic C (2026-10-29). Filament: Bambu Lab PETG Matte, 8 rolls, P2S, no AMS.

Tags: **[sourced]** = shown on a page fetched for this file (URL given); **[inference]** = my reasoning, not
backed by a fetched page; **[vendor claim]** = a seller's statement with no test data shown. Nothing here is
**[measured]** yet: we have printed nothing. Evidence (raw pages, fetch log) is in
`/mnt/project-files/research/petg/` and stays out of git.

## Sources fetched

| # | Source | URL |
|---|--------|-----|
| S1 | Bambu PETG Matte TDS V1.0 (PDF) | https://store.bblcdn.eu/s8/default/240fb0c791fb4903a9d72934895e9a16/PETG_Matte.pdf |
| S2 | Bambu PETG Matte store page (printing tips) | https://us.store.bambulab.com/products/petg-matte |
| S3 | Bambu wiki: Filament Drying Recommendations | https://wiki.bambulab.com/en/filament-acc/filament/dry-filament |
| S4 | Bambu wiki: PETG guide | https://wiki.bambulab.com/en/filament/petg |
| S5 | Bambu wiki: Filament guide (material table) | https://wiki.bambulab.com/en/general/filament-guide-material-table |
| S6 | Kaptan 2025, *Polymers* 17(12):1637, chemical immersion of 8 FDM filaments (full text via Europe PMC) | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12196949/fullTextXML (DOI 10.3390/polym17121637) |
| S7 | Brett Martin "PETg Sheet Chemical Resistance" data sheet, 2024-09-23 (hosted by sunclear.fr) | https://www.sunclear.fr/img/medias/bt/POLYESTER_PETG_INCOLORE_Chemical%20Resistance.pdf |
| S8 | 3D-Fuel blog: Pro PCTG vs PETG chemical resistance | https://www.3dfuel.com/blogs/news/pro-pctg-filament-chemical-resistance |
| S9 | Rust-Oleum Painter's Touch 2X Ultra Cover technical data PT2X-01 (PDF via Zoro) | https://zoro.com/static/cms/enhanced_pdf/RUST%20OLEUM%20Corp_PT2XxxGlossxxTDS.pdf |
| S10 | Klean-Strip Odorless Mineral Spirits SDS (W.M. Barr, hosted by pcad.edu) | https://www2.pcad.edu/Facilities/health_safety/SDS/3-D%20Workshop/W.M.%20Barr/klean%20strip%20odorless%20mineral%20spirits.pdf |
| S11 | Bambu ASA store page | https://us.store.bambulab.com/products/asa-filament |

Also fetched but not used for claims: Bambu PETG HF, PETG Basic and PETG collection store pages, the PETG Matte SDS
PDF, plasticsintl.com's chemical chart (it covers PET, not PETG), the Prusa PETG article (no relevant matches),
the paper's Europe PMC search record, and two Reddit RSS searches: r/3Dprinting "PETG mineral spirits" and
r/BambuLab "PETG matte dry". Neither search returned a thread about PETG and paint thinner or solvents, so Reddit
adds nothing here.

**Blocked or missing (not read, nothing reported from them):** Eastman copolyester chemical-resistance PDFs
(TRS145, TRS211, SPMBS5320) and the Spectar page all returned 404. Corning's PET vs PETG application note and
mdpi.com returned 403 (the paper was read through Europe PMC instead). Curbell's chemical chart returned 403.
Prusa's chemical-resistance article returned 404. A UF mineral spirits SDS failed to connect. A Bambu PCTG
store page returned 404, so I found no PCTG sold by Bambu. Bambu's wiki has no page for PETG Matte itself: the
wiki rows below are for "PETG" in general, while S1 and S2 are specific to PETG Matte.

## 1. Print settings (baseline for step 4)

From the PETG Matte TDS (S1) **[sourced]**:

| Setting | TDS value |
|---|---|
| Nozzle temperature | 230–260 °C |
| Bed temperature | 65–75 °C |
| Build plate | Textured PEI, Smooth PEI, Cool Plate SuperTack |
| Glue | Recommended (glue stick or liquid glue) |
| Cooling fan | On |
| Print speed | < 250 mm/s |
| Retraction | 0.4–0.8 mm at 30–60 mm/s |
| Chamber temperature | 35–50 °C |
| Max overhang / bridge | ~70° / ~30 mm |
| Nozzles | 0.2, 0.4, 0.6, 0.8 mm |
| Test-bar print settings (for the mechanical data below) | H2 printer, 0.4 mm hardened steel nozzle, 245 °C nozzle, 70 °C bed, 221 mm/s, 100% fill, filament dried 60 °C for 8 h |

Other Bambu guidance:
- PETG Matte "adheres strongly to PEI build plates"; let the plate cool fully before removing the print, or both
  the plate and the part's bottom can be damaged (S2) **[sourced]**.
- Wiki bed temperatures for PETG: Cool Plate "Not recommended"; Engineering, Smooth PEI/High-Temp and Textured PEI
  plates 60–80 °C; remove the upper glass cover "If bed > 70 ℃" (S5) **[sourced]**. For PETG on enclosed printers
  with the bed above 60 °C, the wiki recommends opening the front door and/or removing the upper glass cover so
  chamber heat doesn't soften filament in the extruder, more so when the room is warm (S5) **[sourced]**. The same
  page says an enclosed printer is recommended for PETG so a cold room doesn't reduce interlayer strength (S5)
  **[sourced]**. The two pull in opposite directions; how the P2S chamber behaves is a step 5 measurement **[inference]**.
- Flow ratio for PETG-like filaments: 0.93–0.96. Below 0.93 risks under-extrusion and weak layers; above 0.96 risks
  oozing or clogging. Bambu PETG Basic's default is 0.95 (S4) **[sourced]**. PETG Matte's default flow isn't stated
  in anything fetched; read it from the slicer preset, then calibrate (step 5) **[inference]**.
- Warping: PETG warps more than PLA; the fixes are glue and a brim. More walls and infill raise warping risk (S4)
  **[sourced]**.
- Strength: Bambu suggests at most 6 walls and at most 50% infill, and orienting so the main load is at 90° to the
  layer plane (S4) **[sourced]**.
- Seam: keep the seam away from overhangs (S4) **[sourced]**.

What this means for us **[inference]**: start from the slicer's Bambu PETG Matte preset (the slicer thread confirms
it exists) on the stock plate with glue stick, bed about 70 °C. Don't change temperatures before the flow and
pressure-advance calibrations in step 5. For the accuracy prototypes, the chamber-heat advice matters less than
flow and shrink calibration.

## 2. Material data that affects our parts (S1, PETG Matte TDS) [sourced]

| Property | X-Y (along layers) | Z (across layers) |
|---|---|---|
| Tensile strength | 42.9 ± 1 MPa | 30.1 ± 1 MPa |
| Young's modulus | 3349 ± 130 MPa | 3174 ± 50 MPa |
| Elongation at break | 13.8 ± 2.6 % | 6.5 ± 0.5 % |
| Bending strength | 65 ± 2.5 MPa | 47 ± 2.3 MPa |
| Impact strength (ISO 179) | 32.6 ± 4.1 kJ/m² | 10.0 ± 1.5 kJ/m² |

- Heat deflection 71.2 °C at 1.8 MPa and 72.3 °C at 0.45 MPa; Vicat 75.7 °C; Tg 71 °C. Density 1.37 g/cm³.
  Saturated water absorption 0.29% at 25 °C, 55% RH.
- Annealing: if needed, 60–70 °C for 6–12 h, but "some models may deform or warp after annealing" (S1).

**[inference]** Across the layers, a part has about 70% of its along-layer tensile strength (30.1 / 42.9) and
about 31% of its impact strength (10.0 / 32.6). That is the number behind "orient the grip sleeves so hand loads
and knocks don't pull layers apart" in the step 6 STL review. Skip annealing for the test-fit prototypes, because
Bambu itself warns it can warp parts and accuracy is their whole job. Up to about 70 °C is fine for a handle; don't
leave parts on a hot dashboard.

## 3. Drying the 8 rolls

**Do we need to?**
- Store page: PETG Matte "handles moisture better than most PETG filaments"; it needs drying only after "Extended
  exposure above 72 hours at 50% humidity" (S2) **[sourced]**. The same page also calls it "highly
  moisture-absorbent" and says to dry opened filament before use and keep unused filament sealed with desiccant (S2)
  **[sourced]**. Bambu's own page contradicts itself.
- Wiki PETG row: drying before use "Recommended"; desiccant while printing "Not required but recommended" (S3)
  **[sourced]**.
- Signs of damp PETG: obvious stringing, bubbles, holes, rough surfaces, and lower strength (S3, S4) **[sourced]**.

**How, with what carlie has (P2S, no AMS, no dryer):**

| Method | Settings | Source |
|---|---|---|
| P2S heated bed ("Dry Filament" function on the screen) | TDS: 80 °C, 12 h. Wiki drying table: 75–85 °C, 12 h. | S1, S3, S4 [sourced] |
| Forced-air (convection) oven | 65 °C, 8 h (TDS); 60–65 °C, 8 h (wiki) | S1, S3 [sourced] |
| AMS 2 Pro / AMS HT | 65 °C, 12 h (wiki); TDS gives 60 °C/12 h inserted, 65 °C/8 h not inserted | S1, S3 [sourced] |

Heated-bed drying steps for the P2S (S3, section 2.1) **[sourced]**: unload filament from the toolhead and clear
the bed; tap "Prepare" to move the toolhead and plate to their preset positions; put the spool on the plate and
cover it (with a printed high-temperature cover or the filament's packaging box); pick the filament type, set
temperature and time, press Start; flip the spool halfway (with gloves). When it's done, set the bed to 0 °C, let
the spool cool and store it sealed straight away. The PETG page says to flip every 6 hours and to cover the spool
with the packaging box or a PC box (S4) **[sourced]**. Bambu warns against microwaves and kitchen ovens because
they heat unevenly (S1, S3) **[sourced]**.

**[inference]** Plan for carlie:
- Dry only the roll you're about to use, on the P2S bed at 80 °C for 12 h, overnight, with the box as the cover.
  Drying all 8 at once would tie up the printer for 4 days and the rolls would get damp again on the shelf.
- If the printer is busy or drying becomes routine, a filament dryer box is the upgrade. That's optional; none was
  compared here.
- The step 5 calibration should include a damp vs. dried comparison on the first roll: print a stringing test
  straight from the bag, then again after drying. That shows whether this roll needs drying in carlie's room.

## 4. Storing the rolls

- Bambu storage target: under 20% RH, sealed, with desiccant (S1: "Printing and Keeping Container's Humidity < 20%
  RH (Sealed, with desiccant)") **[sourced]**.
- Normal indoor air is usually 45–65% RH. Most filaments stay dry for only 2–7 days at 20% RH. At about 55% RH,
  freshly dried filament takes up enough moisture to affect print quality within 2–12 hours, depending on the
  material (S3, Appendix II) **[sourced]**. PETG Matte's own figure is longer: about 72 h at 50% RH (S2)
  **[sourced]**.
- Use a hygrometer to check the humidity inside the sealed box (S3) **[sourced]**.
- Silica gel can be regenerated at 80–90 °C, never above 100 °C, for 1–3 h in an oven, on a ceramic, glass or foil
  tray (S3) **[sourced]**. The wiki lists bed-drying desiccant on the X1, X1C and P1S (80 °C, 3–4 h); the P2S isn't
  named in that list (S3) **[sourced]**.
- Store cool, dark and dry, out of sunlight (S2, S4) **[sourced]**.

**[inference]** Leave unopened rolls in their factory bags. I didn't fetch anything showing how Bambu packs PETG
Matte, so check that each bag is sealed with a desiccant pack inside when you open the box. Put opened rolls in one
airtight bin with a cheap digital hygrometer and rechargeable silica gel, and recharge the gel when the hygrometer
reads above about 20%. That costs far less than the filament a wet spool wastes.

## 5. PETG and paint, paint thinner, aerosol runoff (grip sleeves)

**What the maker says (S1, PETG Matte TDS) [sourced]:** acids "Not resistant"; alkalis "Not resistant"; organic
solvents "Not resistant to some organic solvents"; oil and grease "Resistant to most kinds of oil and grease".
The TDS doesn't say which solvents.

**Measured on printed PETG (S6, Kaptan 2025) [sourced]:** printed test bars (Prusa PETG, not Bambu Matte), fully
immersed for 1 h, 24 h and 7 days. Tensile and impact strength retained after 7 days:
- Distilled water, 8% acetic acid, 30% hydrogen peroxide: over 97% tensile, 92–97% impact.
- Ethanol 99.5%: about 94% tensile, about 90% impact.
- Isopropyl alcohol 99%: about 85% tensile, about 64% impact.
- 37% hydrochloric acid: about 80% tensile, about 72% impact.
- Acetone 99.5%: tensile down to about 50% within 24 h and about 30% by day 7, with impact similar. SEM showed
  layers coming apart (interlayer delamination).
- The paper tested no hydrocarbon solvent (mineral spirits, naphtha, xylene, toluene).

**What's in the liquids:**
- Rust-Oleum Painter's Touch 2X Ultra Cover lists its solvents as acetone, n-butyl acetate, naphtha and xylene
  (S9) **[sourced]**. That is one product line. Fabrication's test can is a Rust-Oleum spray, but which line isn't
  recorded, so read the label or SDS of the actual cans **[inference]**.
- Klean-Strip Odorless Mineral Spirits: 100% hydrotreated light distillate (petroleum), CAS 64742-47-8, an
  aliphatic hydrocarbon (S10) **[sourced]**. "Paint thinner" products vary, so check the can carlie actually uses
  **[inference]**.

**Sheet-PETG chart (S7, Brett Martin) [sourced]:** ratings at 20 °C, 1 = stable, 2 = conditionally stable,
3 = unstable. The sheet says it's compiled from public data, is only an indication, and that stress and
concentration change results.
- Acetone 3, methyl ethyl ketone 3, benzene 3.
- Ethyl acetate 2, butyl acetate 2.
- Hexane 1, kerosene 1, petrol/petroleum 1, toluene 1.
- Ethanol (50% and 96%) 1.
- Xylene, white spirit and mineral spirits are not listed.

The chart rates toluene stable but benzene unstable, which is odd for two similar aromatics, so I treat its
aromatic rows as weak **[inference]**.

**Vendor claim (S8, 3D-Fuel):** PETG "Softens or weakens when exposed to hydrocarbons" such as mineral spirits;
the post says their PCTG resists hydrocarbons 2.0× better. No test method or data is shown **[vendor claim]**.

**What this means for the grip sleeves [inference]:**
1. Paint and aerosol runoff (the usual case): acetone and the acetates in spray paint attack PETG, but in an
   overspray film they evaporate within minutes. Expect at most surface marking from brief, occasional wetting;
   that is far milder than the paper's 24 h soak. Clean with a dry or water-damp rag, not acetone.
2. Paint thinner (sometimes): if it's mineral spirits, the sheet data (hexane, kerosene, petrol all "1") points to
   fair resistance, while the vendor claim says it softens PETG. The sources conflict and none tested printed PETG
   in mineral spirits. Lacquer thinner (usually ketones, acetates and aromatics) is the real risk.
3. The bigger risk is stress cracking, not dissolving. A U-sleeve clipped on under load is stressed, and S7 notes
   stress changes resistance. Layer lines are where solvent gets in (S6 SEM).
4. **Proposed test (for the step 4 plan, then measured in step 5):** print 6 small bars in PETG Matte with the
   sleeve's wall settings. Leave 2 dry as controls. Wipe 2 with carlie's actual spray paint and 2 with carlie's
   actual thinner: a wet rag, 10 s, daily for a week. Also soak half a bar for 24 h as a worst case. Then check
   with calipers (swelling), by eye (whitening, crazing), and with a hand bend test against the controls. This
   costs a few grams and replaces guesswork with a measured result.

## 6. When another material is worth buying [inference unless tagged]

carlie wants PETG only until it proves wrong. Nothing fetched shows PETG failing at our jobs:
- **Test-fit prototypes:** PETG is fine. What matters is dimensional calibration, not the material.
- **Grip sleeves:** the only real-use parts. Buy something else only if the section 5 test fails. Candidates:
  - **PP**: best in S6, keeping over 97% of its properties even after 7 days in acetone **[sourced, S6]**. It is
    hard to get to stick to the bed (from general experience, not fetched: check before buying).
  - **ASA**: about as good as PETG in S6, over 90% retention except in acetone **[sourced, S6]**. Bambu sells it.
    It needs an enclosed printer, releases styrene while printing, and warps on large or dense parts **[sourced,
    S11]**. It doesn't fix the solvent problem.
  - **PCTG**: better solvent resistance by vendor claim only **[vendor claim, S8]**. I found no Bambu PCTG.
- **Heat:** about 71 °C HDT (S1) covers handle use. Only something left in a hot car or next to a heater would
  need ASA or PC.

Recommendation: don't buy another material now. Run the section 5 coupon test with carlie's own paint and thinner.
If PETG crazes, softens or swells, reprint the sleeves in PP or ASA, choosing from the same coupon test run on a
sample.

## Open questions for later threads
- Which Rust-Oleum line and which thinner carlie uses (to read their SDS before the coupon test).
- Whether PETG Matte's slicer preset defaults (temperature, flow, max volumetric speed) match the TDS (slicer
  thread).
- The P2S chamber temperature during PETG prints, door closed vs. open (step 5 measurement).
- Whether the factory bags are sealed with desiccant (look when unboxing).

## Research cost
- 2026-10-29, one thread. 32 fetches logged (20 OK, 12 failed or blocked), 2 web searches used only to find URLs
  (no claim rests on a search snippet), and about 60k tokens of context. Run before the Sat 5 AM reset because carlie chose
  to start the roadmap early (2026-10-29).
