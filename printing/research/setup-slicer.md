# Research: P2S first-day setup, slicer choice, slicer workflow, LAN-only setup

Step 3, topic A of 4 (2026-10-29). Other step-3 threads cover dimensional accuracy, PETG/materials and
design-for-print/strength; this file touches those only where the slicer or printer setup decides them.

Tags: **[S]** sourced (the URL is a page we fetched and saved), **[F]** forum or Reddit report (sourced, but one
person's experience), **[I]** our inference. Nothing here is **measured** yet: the printer is still boxed.
Evidence (raw pages, text, fetch log) is in `/mnt/project-files/research/printing-setup-slicer/`, not in git.

## Recommendation in short

1. **Slicer: Bambu Studio** (v02.08.04.57 for Windows on the [download page](https://bambulab.com/en/download/studio) today **[S]**), with OrcaSlicer kept only as an
   offline second slicer (files by USB drive, no network) for extra calibration models and, if a measured hole
   coupon says so, for the fit-critical parts (polyholes, precise wall). Reasons below. **[I]** built
   on [S] facts.
2. **Network: none. The printer never joins Wi-Fi; files go from BigGuy to the printer on a USB drive** (decided
   2026-10-30, section 4a). LAN Only (Developer Mode off) is the fallback only if a calibration we need turns out
   to require a connected printer. Never cloud printing, never MakerWorld upload: cloud printing stores the sliced
   G-code on Bambu's servers, and G-code is the part geometry. **[S]** + **[I]**
3. **First day:** let the printer run its own initial calibration (foam left under the bed until it finishes), then
   do the manual calibrations Bambu does not automate on the P2S: flow rate (manual only), and the accuracy checks
   (XY hole/contour compensation) the accuracy thread specifies. **[S]**
4. **Profiles under git:** start from the stock `Bambu PETG Matte @BBL P2S 0.4 nozzle` filament preset, save every
   change as a user preset, export it with Export Preset Bundle into `printing/profiles/`, and slice the test set
   reproducibly with the Bambu Studio command line. **[S]** + **[I]**

## 1. What the P2S calibrates by itself, and what it doesn't

**Automated (printer screen, Settings > Calibration > Print Calibration)** **[S]**
[screen-operation](https://wiki.bambulab.com/en/p2s/manual/screen-operation): "Print Calibration: Includes motor
noise cancellation, vibration compensation, auto bed leveling, high-temperature bed leveling and nozzle offset
calibration."
- *Vibration compensation* is the P2S's version of input shaping: "When any vibration is detected in real-time during
  printing, the toolhead position can be automatically adjusted". **[S]** (same page). So no manual input-shaping or
  ringing test is needed; OrcaSlicer's own guide says to prefer a printer's built-in input shaping where it exists
  ([Orca input shaping](https://www.orcaslicer.com/wiki/calibration/input_shaping_calib.html)). **[S]**
- *Auto bed leveling* uses the eddy-current sensor; per-print leveling is a switch in the send-print dialog and on the
  printer (Advanced Options > Auto Bed Leveling); calibration data is stored in the printer and applied automatically
  ([first-layer guide](https://wiki.bambulab.com/en/p2s/troubleshooting/first-layer-printing-optimization-guide)). **[S]**
- *Nozzle clumping detection calibration* runs during initialization; *live view camera calibration* uses marks on the
  heatbed (screen-operation, [P2S FAQ](https://wiki.bambulab.com/en/p2s/manual/p2s-faq)). **[S]**
- *Flow dynamics (pressure advance, "K value")*: the FAQ says "The printer is equipped with an eddy current sensor and
  supports active flow calibration." **[S]** ([P2S FAQ](https://wiki.bambulab.com/en/p2s/manual/p2s-faq)). The
  flow-dynamics wiki page lists only H2D/X1/A1 by name for automatic mode and describes the eddy-current method (purge
  at the wiper, measure extrusion force) for A1/H2D ([calibration_pa](https://wiki.bambulab.com/en/software/bambu-studio/calibration_pa)). **[S]**
  That page is older than the P2S; we expect the P2S to use the same eddy-current method. **[I]** Confirm on BigGuy in
  Studio's Calibration tab (step 4 check, before calibrating).

**Not automated on the P2S (we do these)**
- *Flow rate (flow ratio)*: "Auto-Calibration ... Only X1 series support Auto calibration." Manual mode has a coarse
  pass (80-120 % in 5 % steps) and a fine pass (1 % steps); you pick the smoothest top surface
  ([calibration_flow_rate](https://wiki.bambulab.com/en/software/bambu-studio/calibration_flow_rate)). **[S]** Visual
  choice of the smoothest block is subjective; for accuracy work we should also check it against caliper
  measurements of a test part. **[I]**
- *Order*: Bambu says run flow dynamics before flow rate
  ([microlidar notes](https://wiki.bambulab.com/en/knowledge-sharing/flowrate-calibration-by-microlidar)). **[S]**
  OrcaSlicer's guide orders it temperature, max volumetric speed, pressure advance, flow ratio, retraction, then
  tolerance last "as the result depends on every calibration above"
  ([Orca calibration guide](https://www.orcaslicer.com/wiki/guides/calibration_guide.html)). **[S]**
- *Before any calibration*: filament dried, hotend and extruder clean, build plate washed; damp filament makes
  flow-dynamics results "unsuitable for use with fresh filament" (calibration_flow_rate, calibration_pa). **[S]**
  Drying is the PETG thread's topic.
- *Redo flow dynamics when*: a new filament brand/model, a worn or replaced nozzle, or a change to max volumetric speed
  or print temperature in the filament preset (calibration_pa). **[S]**
- *XY hole / contour compensation*: manual, from caliper measurements of a hole test; fix shrink, elephant's foot and
  seams first ([xy-hole-contour-compensation](https://wiki.bambulab.com/en/software/bambu-studio/xy-hole-contour-compensation)). **[S]**
  Detail belongs to the accuracy thread.
- *First Layer Quality Calibration* (firmware 01.02.00.00): fine-tunes nozzle-to-bed distance on the first layer; Bambu
  says use it "only as required for advanced troubleshooting"
  ([firmware history](https://wiki.bambulab.com/en/p2s/manual/p2s-firmware-release-history)). **[S]** Relevant to us
  because first-layer squish is elephant's foot, which hurts the collar and plate stand-ins. Use only if a measured
  first layer is off. **[I]**
- *Manual bed leveling* (3 screws, A4 paper, USB G-code) is only for cases auto leveling doesn't fix (first-layer
  guide). **[S]**

**First power-on details** **[S]** ([unboxing](https://wiki.bambulab.com/en/p2s/manual/unboxing-p2s)):
"Keep the foam around the heatbed in place until calibration is complete", build plate on the bed before
calibration, "After calibration, remove the foam under the heatbed", and put a container under the purge chute.
The non-Combo P2S feeds an external spool through the PTFE tube coupler
([first-print](https://wiki.bambulab.com/en/p2s/manual/first-print)). **[S]** Bambu "strongly recommend[s]" a USB
drive in the printer for videos and print-history cache (first-print). **[S]**

**Firmware**: latest listed is 01.03.00.00 (2026-09-21); some of its features need Bambu Studio v2.8.3.66 or later
(firmware history). **[S]** Firmware can be updated offline from a FAT32 USB drive: Settings > Firmware > Update
Offline, 20-30 minutes, don't cut power
([offline-firmware-update](https://wiki.bambulab.com/en/p2s/manual/offline-firmware-update)). **[S]**
After any firmware change, redo motor noise-cancellation calibration (firmware history note). **[S]**

## 2. Slicer choice

| | Bambu Studio | OrcaSlicer |
|---|---|---|
| P2S + PETG Matte profiles | Yes: `Bambu Lab P2S 0.4 nozzle`, 16 P2S process presets, `Bambu PETG Matte @BBL P2S 0.4 nozzle` ([BBL.json](https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL.json)) **[S]** | Same names and same PETG Matte P2S values (both files fetched and compared) ([BBL.json](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/main/resources/profiles/BBL.json)) **[S]** |
| Sending a print in LAN Only mode | Supported by Bambu: bind with the access code ([LAN mode](https://wiki.bambulab.com/en/knowledge-sharing/enable-lan-mode)) **[S]**; a P2S owner reports Studio sending LAN-only jobs without Developer Mode ([Reddit](https://www.reddit.com/r/BambuLab/comments/1revev6/p2s_bambu_developer_mode_questions/)) **[F]** | Authorization firmware blocks third-party slicers from starting prints; they go through Bambu Connect ([Bambu blog](https://blog.bambulab.com/firmware-update-introducing-new-authorization-control-system-2/)) **[S]** or printer Developer Mode ([forum](https://forum.bambulab.com/t/bambu-studio-losing-printers-when-switched-to-lan-only-mode/206035), X1C) **[F]** |
| Auto flow dynamics on P2S | Yes, through Studio's Calibration tab (Bambu's own tool) **[S]**/**[I]** as above | Not documented for P2S **[I]** |
| Extra calibration models | Temp tower, max flowrate, retraction, VFA, PA tower documented for *third-party* printers with Studio's developer mode on ([Calibration for 3rd party](https://wiki.bambulab.com/en/bambu-studio/Calibration)) **[S]**; whether they appear for a P2S is unverified **[I]** | Built in: temperature, max volumetric speed, PA, flow ratio, retraction, tolerance test (hex holes at 0-0.4 mm) and more ([guide](https://www.orcaslicer.com/wiki/guides/calibration_guide.html), [tolerance](https://www.orcaslicer.com/wiki/calibration/tolerance_calib.html)) **[S]** |
| Headless CLI | Yes ([Command-Line-Usage](https://raw.githubusercontent.com/wiki/bambulab/BambuStudio/Command-Line-Usage.md)) **[S]** | Yes, more documented ([CLI mode](https://www.orcaslicer.com/wiki/cli/cli_mode.html)) **[S]** |
| Preset export | Export Preset Bundle: `.bbscfg` (printer + its filament/process presets), `.bbsflmt` (filament) ([export presets](https://wiki.bambulab.com/en/bambu-studio/export-filament)) **[S]** | Export/Import Preset Bundle ([import/export](https://www.orcaslicer.com/wiki/general_settings/import_export.html)) **[S]** |
| Accuracy features (from the accuracy thread, re-checked here) | Precise Z height: yes, Advanced mode ([layer height](https://wiki.bambulab.com/en/software/bambu-studio/layer-height); `precise_z_height`, `comAdvanced` in [PrintConfig.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/PrintConfig.cpp)) **[S]**. Precise wall: exists but hidden in develop mode (`precise_outer_wall`, `comDevelop`) **[S]**. Polyholes: none (no match in PrintConfig.cpp) **[S]**. Auto hole compensation doesn't cover PETG Matte (accuracy thread, Fabrication PR #16) | Precise Z height, Precise wall and Polyholes are all normal settings ([precision](https://www.orcaslicer.com/wiki/print_settings/quality/quality_settings_precision.html), [README](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/main/README.md)) **[S]** |
| License / network code | Bambu's official slicer | AGPL-3.0; the Bambu networking plugin is "based on non-free libraries from BambuLab" and optional ([README](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/main/README.md)) **[S]** |

**Why Bambu Studio** **[I]**:
- It is the one slicer Bambu authorizes to send prints to a LAN-only P2S with Developer Mode off. OrcaSlicer would
  need either Bambu Connect (another Bambu app; adds nothing for privacy) or Developer Mode, which lets third-party
  software "control the printer" on the LAN (LAN-mode wiki) and is outside what Bambu supports. More moving parts,
  more failure modes for first-try prints.
- It runs the P2S's automatic flow dynamics calibration and stores K values in the printer.
- The P2S profiles are the same in both, so Orca gives no better starting point for this printer and filament.
- Its CLI and preset bundles are enough for versioned, reproducible profiles.

**Where OrcaSlicer still helps** **[I]**: accuracy. Polyholes and an exposed Precise wall are real advantages for
the fit-critical holes and slots, and its tolerance and temperature / max volumetric speed tests are well documented.
Precise Z height is *not* a difference: Studio has it too (Advanced mode), so the collar thickness can be handled in
either. Auto hole compensation doesn't help in either, because it doesn't cover PETG Matte, so holes get manual
XY hole compensation from our own coupon whichever slicer slices them.

**So the plan is Studio first, with a measured tie-break** **[I]**: in step 4/5, print the hole/slot coupon twice:
once sliced in Studio (manual XY hole compensation), once in OrcaSlicer (polyholes + precise wall), with the Orca
copy sent **by USB drive** (no network link, no Developer Mode, no Bambu Connect). If the Orca coupon measures
clearly closer to the drawn sizes, slice the fit-critical stand-ins in Orca and print them from USB, and keep Studio
for calibration and everything else. Studio's own Develop mode may also expose Precise wall; check it on BigGuy.
Whether Orca's `.gcode.3mf` files print from a USB drive on the P2S is not confirmed by a page we read (a Reddit
thread title, ["Is it possible to get OrcaSlicer files to show a gcode thumbnail on a P2S screen?"](https://www.reddit.com/r/BambuLab/comments/1tgs0t9/is_it_possible_to_get_orcaslicer_files_to_show_a/),
suggests people do it) **[F]**; test with the first coupon.

**What would change the call** **[I]**: Studio failing to bind or keep the LAN-only printer (forum reports of Studio
losing LAN printers were X1C/X1E, not P2S; [forum](https://forum.bambulab.com/t/bambu-studio-losing-printers-when-switched-to-lan-only-mode/206035) **[F]**),
a calibration we need that only Orca has, or the hole coupon above measuring clearly better from Orca.

Other slicers (PrusaSlicer, Cura) were not researched: neither ships Bambu's P2S profiles we could check, and neither
can send to an authorization-firmware printer without the same Connect/Developer Mode workarounds. **[I]**

## 3. Slicer workflow (Bambu Studio)

- **Presets**: system presets are read-only; every change is saved as a user preset. Export with
  Export > Export Preset Bundle; a printer bundle (`.bbscfg`) includes the printer preset plus its user filament and
  process presets ([export presets](https://wiki.bambulab.com/en/bambu-studio/export-filament)). **[S]**
  → commit each exported bundle to `printing/profiles/` with the date and what changed. **[I]**
- **Baseline filament preset (stock, before calibration)** from `Bambu PETG Matte @BBL P2S 0.4 nozzle` and its parent
  `@base` ([P2S preset](https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/filament/Bambu%20PETG%20Matte%20@BBL%20P2S%200.4%20nozzle.json),
  [base](https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/filament/Bambu%20PETG%20Matte%20@base.json)) **[S]**:
  nozzle 240 °C (first layer 240), flow ratio 0.95, max volumetric speed 13 mm³/s, textured PEI plate 70 °C, fan
  30-60 %, overhang fan 40 %, retraction 0.4 mm, Spiral Lift z-hop, nozzle range 230-270 °C.
  The P2S preset stores three values for several keys (e.g. 240/250/250 °C, 13/15/15 mm³/s); we read the first as the
  stock hotend, but that is unconfirmed. **[I]** Check in Studio's filament settings on BigGuy.
- **Per-object settings and modifiers**: settings can be applied to selected objects
  ([set parameters](https://wiki.bambulab.com/en/software/bambu-studio/set-parameters-for-selected-objects)); modifiers
  change settings inside a volume or a height range (e.g. stronger infill in one region)
  ([modifier](https://wiki.bambulab.com/en/software/bambu-studio/modifier)). **[S]** For the sleeves, a modifier is how
  we would add walls/infill where the load is without changing the test-fit plates. **[I]**
- **Variable layer height**: for a 0.4 nozzle the range is 0.08-0.28 mm, and Bambu advises not to change that limit;
  there is an Adaptive button with a detail/speed slider
  ([variable layer height](https://wiki.bambulab.com/en/software/bambu-studio/adaptive-layer-height)). **[S]**
  Don't use it on the collar: its height must round to whole layers (`printing/STATE.md`), and variable layers would
  make that unpredictable. Fixed layer height for test-fit parts. **[I]**
- **XY hole / contour compensation** is a process setting in Studio (and Orca); values come from the accuracy thread's
  hole test. **[S]** (page above)
- **Headless slicing (CLI)** ([Command-Line-Usage](https://raw.githubusercontent.com/wiki/bambulab/BambuStudio/Command-Line-Usage.md)) **[S]**:
  `bambu-studio --orient --arrange 1 --load-settings "machine.json;process.json" --load-filaments "filament.json" --slice 0 --export-3mf out.3mf part.stl`
  The JSONs must be full configs (not the inherited system files); `--export-settings settings.json` writes one out;
  command-line `--key=value` beats `--load-settings`, which beats the 3MF. **[S]**
  Use: slice the v0.95 test set on BigGuy from committed profile JSONs so every print record can name the exact
  settings, and diff settings between versions. On Windows the binary path will differ; check the install folder. **[I]**
  Avoid `--orient` for our parts: orientation is chosen per part from its load, and written down. **[I]**

## 4. LAN-only, no-cloud setup (keeping the design private)

- **What LAN Only does** **[S]** ([LAN mode](https://wiki.bambulab.com/en/knowledge-sharing/enable-lan-mode)): the
  printer talks to the slicer on the local network "without requiring internet access"; Bambu says it suits "highly
  sensitive models that need to be kept private". Lost: remote printing from outside the LAN, Bambu Handy, print
  history.
- **Bambu's privacy notice** **[S]** ([privacy](https://bambulab.com/en/policies/privacy)): "When LAN Only Mode is
  enabled ... all the printing task-related data stays within your local area network", and it recommends LAN Only
  "for highly private printing tasks". In cloud mode, print history and G-code are kept in Bambu's cloud; even
  "Private Printing Mode" only removes them "in 72 hours". Camera data "is processed locally ... unless you enable
  cloud-based features". So cloud printing is ruled out by our privacy rule, not just discouraged. **[I]**
- **Enabling it on the P2S** **[S]** (LAN mode page, H2/P2S/X section): printer screen Settings > LAN Only, turn on;
  choose LAN liveview; leave **Developer Mode** off ("allows third-party software to control the printer").
  In Bambu Studio: Device tab > printer list, find the printer with a lock icon (20-60 s), enter the access code.
  If they're on different subnets: Device > No Printer > Bind with Access Code, using the IP and access code from the
  printer's LAN Only page. Guest Wi-Fi networks can block discovery.
- **Account / first-time setup: open question.** Bambu's binding guide describes Wi-Fi then Login via Bambu Handy QR
  code ([binding](https://wiki.bambulab.com/en/knowledge-sharing/printer-account-binding-guide)) **[S]**, and does not
  say whether LAN Only works without ever binding. One Reddit commenter says an account is needed for initial setup,
  then LAN mode works offline ([Reddit](https://www.reddit.com/r/BambuLab/comments/1ul9j1h/setup_p2s_completely_offline/)) **[F]**.
  We could not find a Bambu page that settles it. Plan: at first power-on, connect Wi-Fi and look for LAN Only before
  logging in. If the printer insists on a login, a one-time account binding sends no design data (nothing is sliced
  yet) **[I]**; switch to LAN Only straight after and never cloud-print. This is carlie's call at the printer.
- **Bambu Studio without an account**: whether Studio's Device tab binds a LAN printer while logged out isn't stated
  on the pages we fetched; one forum poster was unsure ([forum](https://forum.bambulab.com/t/bambu-studio-losing-printers-when-switched-to-lan-only-mode/206035)) **[F]**.
  Test on BigGuy. **[I]**
- **Firmware without the cloud**: offline USB update (section 1). A LAN-mode owner reports no firmware prompts in LAN
  mode ([Reddit](https://www.reddit.com/r/BambuLab/comments/1revev6/p2s_bambu_developer_mode_questions/)) **[F]**, so
  check the [release history](https://wiki.bambulab.com/en/p2s/manual/p2s-firmware-release-history) by hand before
  each calibration batch. **[I]** LAN-only printing to built-in storage needs Studio 2.3.0.70+ (firmware 01.01.00.00
  notes). **[S]**
- **Belt and braces** **[I]**: reserve a DHCP address for the printer; optionally block its internet access at the
  router (nobody we read has checked whether LAN Only stops all outbound traffic: [Reddit](https://www.reddit.com/r/BambuLab/comments/1revev6/p2s_bambu_developer_mode_questions/) **[F]**).
  Don't log Studio in, don't use MakerWorld/"Publish", and keep `Fabrication` STLs only on BigGuy and the repo.
  The camera has no privacy cover (Bambu offers a printable one: [P2S intro](https://wiki.bambulab.com/en/p2s/manual/p2s-intro)). **[S]**

## 4a. Offline USB-drive printing vs. LAN Only (added 2026-10-30)

carlie's printer has had its initial on-screen calibrations and has never been on the internet or Wi-Fi. Question:
keep it that way and print from a USB drive, or use LAN Only? Evidence in
`/mnt/project-files/research/offline-printing/` (16 fetches, 14 OK, 2 guessed URLs 404; one forum page came back
without its post text, nothing cited from it; 3 web searches used only to find URLs).

**What the USB port is** **[S]** ([P2S intro](https://wiki.bambulab.com/en/p2s/manual/p2s-intro)): "USB Storage Port:
A USB-A port supporting USB 2.0 protocol, which allows offline printing via a USB drive and storing time-lapse video
files." It is a port for a flash drive, not a link to a computer. A USB cable from BigGuy to it would not work:
both ends are hosts, and no Bambu page describes printing over a USB cable. **[I]**

**Drive requirements** **[S]** ([P2S FAQ](https://wiki.bambulab.com/en/p2s/manual/p2s-faq)): USB 2.0 or faster,
write speed above 10 MB/s, FAT32 or exFAT, one drive only (no hub). Windows formats FAT32 only up to 32 GB; the
printer can format a drive itself (Settings > USB Storage > Format External Storage, FAT32 only)
([offline firmware](https://wiki.bambulab.com/en/p2s/manual/offline-firmware-update)). Without a drive there is no
recording/timelapse and no log export (FAQ). **[S]**

**Printing from the drive** **[S]**: the printer screen's homepage has Print Files
([screen operation](https://wiki.bambulab.com/en/p2s/manual/screen-operation)); for the P2S, "tap Print Files, then
select the model ... Confirm the build plate and nozzle settings. Set timelapse and advanced options as needed
(default is auto), then tap Next ... Select the loaded filament and tap Print"
([P2S first print](https://wiki.bambulab.com/en/p2s/manual/first-print)). Bambu Studio writes the file with
Print Plate's arrow > **Export plate sliced file**, saved to the root of the card/drive, not a subfolder (Bambu's
[A1 SD-card guide](https://wiki.bambulab.com/en/a1/manual/how-to-print-from-sd-card) **[S]**; there is no P2S-specific
page, we tried the obvious URL and got 404, so the same menu on a P2S is **[I]**, to confirm on BigGuy).

**Where the file ends up** **[S]** ([internal storage](https://wiki.bambulab.com/en/knowledge-sharing/how-to-use-internal-model-cache-space)):
a print started from a USB drive is also copied into the printer's internal cache (up to 8 files / 500 MB, oldest
deleted first, can't be turned off). The cache is "stored locally on the printer, independent of Bambu cloud
storage". So a copy of each sliced part stays in the printer until pushed out. With no network that copy can't go
anywhere **[I]**; it matters only if the printer is ever sold, serviced or put online. Bambu's own answer for
confidential models is LAN Only + a USB drive + send to external storage (same page), which skips the cache; a print
started on the screen from the drive does not.

**Firmware offline** **[S]** (offline firmware page): format the drive on the printer, download the P2S package on a
computer, copy it unchanged (not unzipped, not renamed) to the drive's root, then Settings > Firmware > Update
Offline, 20-30 min, don't cut power. Latest on the [release history](https://wiki.bambulab.com/en/p2s/manual/p2s-firmware-release-history)
today: 01.03.00.00 (2026-09-21). Redo motor noise cancellation after any firmware change (section 1). **[S]**

**Flow dynamics without a connection** **[S]** ([calibration_pa](https://wiki.bambulab.com/en/software/bambu-studio/calibration_pa)):
on H2D/H2S/P2S/X2D the printer purges at the wiper and measures with the eddy-current sensor; in **Automatic** it
reuses a recent result for the same filament and nozzle, else calibrates; results "will be recorded inside the
machine". The screen's advanced options default to auto (first-print page). So K values work offline. **[S]** + **[I]**
What does *not* obviously work offline is Studio's **Calibration tab** (manual flow rate passes, PA line/pattern,
saving named K profiles to the printer): Bambu's page says "ensure the 3D printer is connected" before calibrating
**[S]** for automatic mode; we assume the tab's manual tests also want a connected printer **[I]**, to check on BigGuy.

**Bambu Network Plugin (Studio asks to install it on first start)** **[S]**
([remote control](https://wiki.bambulab.com/en/software/bambu-studio/remote-control)): "The Bambu Network Plugin is
required for the remote control and monitor features in Bambu Studio. If it is not installed, you cannot send a print
job via the network, and the 'Device' page will be unavailable." It covers both WAN and LAN control (same page).
- USB drive only: **not needed**. Slicing and Export plate sliced file are not network features. **[I]** from [S]
- LAN Only: needed, since sending a job over the LAN goes through it. **[S]**
- What it sends online: no Bambu page we fetched says. Bambu's [privacy notice](https://bambulab.com/en/policies/privacy)
  says that for its apps, Bambu Studio named, "we may automatically collect information about your device, network,
  and activity ... usage data ... diagnostic or performance information" **[S]**; it does not break that down by
  plugin. OrcaSlicer's README calls the plugin "based on non-free libraries from BambuLab" (section 2) **[S]**, so
  nobody outside Bambu can check what it does. **[I]**
- So: **skip it** (Studio keeps working for slicing and export), don't log in, never use Publish/MakerWorld. Install
  it only if we ever move to LAN Only. A forum search for an official "no-cloud" switch in Studio found only
  forum posts, none read, nothing cited. **[I]**

| | USB drive only (printer never on a network) | LAN Only (printer on home Wi-Fi) |
|---|---|---|
| Privacy | Nothing can leave: no network at all. File copies: drive, BigGuy, printer cache. **[I]** | Bambu: task data "stays within your local area network" ([privacy](https://bambulab.com/en/policies/privacy)) **[S]**, but the printer sits on a network that has internet; nobody we read verified it makes no outbound calls (section 4) **[F]** |
| Account / login | None needed: carlie's printer got through setup and its first calibrations without ever going online (carlie, 2026-10-30) | Open question whether it ever forces a login (section 4) |
| Firmware | Offline by USB, by hand **[S]** | Same, offline by USB; no prompts in LAN mode **[F]** |
| Monitoring | Screen and in person only. No live view, no remote stop. Timelapse to the drive (FAQ) **[S]** | Live view and control from Studio on the LAN **[S]** |
| Calibration data | Printer's own calibrations and auto flow dynamics stored on the printer **[S]**. Studio Calibration tab probably unusable **[I]** | Full Studio Calibration tab **[S]** |
| Studio network plugin | Not needed **[I]** | Required **[S]** |
| Effort per print | Export, walk the drive over, pick the file on screen | Click Send in Studio |

**Recommendation** **[I]**: **USB drive only.** It is the only setup where "nothing leaves our machines" holds by
construction, rather than by trusting firmware, and it costs us only live monitoring and Studio's guided
calibration screens. Monitoring: the coupons are small and short, carlie is nearby, and the printer's spaghetti,
clumping and pile-up detection still pause a print on its own (screen operation **[S]**). Calibration: printer
calibrations and flow dynamics run offline; flow rate becomes our own coupon (the same test, several copies of a
block with different flow ratios set per object, sliced on BigGuy) instead of Studio's wizard **[I]**. Revisit only if
batch 1 shows we can't get a good flow ratio or K value that way; the fallback is LAN Only with the printer's
internet blocked at the router.

## 5. First-day sequence to carry into step 4 (draft, [I] built on the [S] items above)

1. Unbox per the wiki, foam in place, plate on, power on, run the on-screen initial calibration; remove the foam.
2. No Wi-Fi (section 4a). Format a USB drive on the printer and leave it in.
3. Check firmware version against the release history; update offline by USB if behind; redo motor noise
   cancellation afterwards.
4. BigGuy: install Bambu Studio from bambulab.com, skip login, don't bind any printer; confirm the P2S
   0.4 nozzle and `Bambu PETG Matte @BBL P2S 0.4 nozzle` presets; export them as the v0 bundle into
   `printing/profiles/`.
5. Dry the PETG (PETG thread), wash the plate, then: flow dynamics (auto), flow rate coarse then fine (manual),
   then the accuracy thread's hole/contour tests, measured with calipers, results into `printing/tests/`.

## Not done / blocked

- github.com and api.github.com pages are blocked from the cloud (403), so Bambu Studio and OrcaSlicer release notes
  were not read; raw.githubusercontent.com worked for profiles, the README and the Bambu Studio CLI wiki.
- `orcaslicer.com/wiki/calibration/Calibration` was a 404; the current guide page was used instead.
- All3DP's developer-mode article came back without readable body text; nothing is cited from it.
- Reddit: "Getting new P2S tomorrow - questions about LAN mode and Orca" failed with repeated 429s; two more threads
  ("P2S Full Manual Filament Calibration?", "P2S and orcaslicer") were not fetched. Only the two Reddit threads
  linked above were read.
- No PrusaSlicer/Cura research (see section 2).

## Research cost

- Fetches: 61 logged, 56 OK, 5 FAILED (github.com x1, api.github.com x2, one Orca 404, one Reddit 429). Two more
  Reddit comment feeds were queued and cancelled after repeated 429s. Plus 7 web searches, used only to find URLs
  (nothing is cited from a search snippet).
- Model usage: about 180k tokens for the thread, from the session counter (an estimate), one thread, no subagents,
  about 25 minutes of wall time including Reddit rate-limit waits.
