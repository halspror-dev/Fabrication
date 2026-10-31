# Remote printing without the cloud

Thread "Enable remote print jobs without cloud", 2026-10-31. Question (carlie): can I send print jobs while I'm away,
without Bambu cloud? Ideally: talk about an STL with Claude on the go, then print it.

Tags: **[S]** sourced (URL below), **[M]** measured by us, **[I]** my inference. Evidence (13 fetches, 1 failed:
github.com HTML page 403, the raw README was used instead) is in `/mnt/project-files/research/remote-printing/`.

## Short answer

**Yes, no cloud needed.** Bambuddy, which already runs in CT208, can upload a sliced file to the printer over the LAN
and start it. Its print queue sends every print it starts "through the same queue scheduler", with "FTP uploads and
print-start commands" run in the background **[S: README]**. It needs Developer Mode (ours is on) and the same LAN as
the printer **[S: README]**, which CT208 is. The phone already reaches Bambuddy over Tailscale **[M: monitoring.md]**.

One P2S catch: Bambuddy reads and writes files over FTPS on port 990, which "on every Bambu model ... serves external
storage only — the SD card or USB stick"; for P2S "All the routes below need a card or stick in the printer"
**[S: troubleshooting]**. So **a USB stick stays in the printer's top USB-A port**. A missing/broken stick shows as
"refused to store the file — check its SD card or USB drive" and the job waits **[S: troubleshooting]**.

## The routes, compared

| Route | What it is | Verdict |
|---|---|---|
| **A. Bambuddy File Manager, from the phone** | Upload a sliced `.gcode.3mf`, pick printer/plate, print. Print options include bed levelling and "Layer Inspect: Enable AI first layer inspection" (default Off) **[S: print-queue]** | **Use now.** Nothing new to install. |
| **B. Claude on BigGuy slices, Bambuddy prints** | A Claude thread with Remote Control on BigGuy slices in `C:\PrintLocal` with the Bambu Studio CLI (`--slice 0 --export-3mf`, see `setup-slicer.md`) and our committed profiles, then uploads the file to Bambuddy over the LAN with an API key. carlie looks at the camera and taps Print. | **Recommended** for "talk about the STL, then print". |
| C. Bambuddy server-side Slice | Optional `slicer-api/` Docker sidecar (OrcaSlicer ~110 MB, Bambu Studio ~220 MB images, `linux/amd64` only) lets you drop an STL in from the phone and slice in Bambuddy **[S: slicer-api README]**. | Later, for when BigGuy is off. Our tuned profiles would have to be imported, and CT208 has 2 GB RAM **[I: may be tight]**. |
| D. Virtual Printer, Proxy Mode | Bambuddy pretends to be a printer so Bambu Studio's own Send/Print works from anywhere, "end-to-end TLS" **[S: README]**. Needs Bambuddy's CA appended to Studio's `printer.cer`, redone "After slicer updates", plus the VP's own IP/ports (990, 8883, 6000, 322) **[S: virtual-printer]**. | Skip. Fragile, and B already gives remote Studio-quality slicing. |
| E. Bambu Studio on BigGuy sends directly | Works on the LAN in LAN Only mode **[S: Bambu wiki LAN mode]**, but Studio's Print button puts P2S files in internal storage, so Bambuddy archives only a name and time; Send with External works **[S: README, troubleshooting]**. | Fine at home; no remote benefit over B. |

## Why B

- Slicing stays on BigGuy with the profiles we calibrate and version in `printing/profiles/` **[I]**: accuracy is the
  point of this project, and a second set of profiles in a container would drift.
- Files never leave the house: BigGuy → CT208 → printer, all LAN. Allowed by carlie's privacy line (homelab is fine,
  cloud is not). Bambuddy keeps cloud-related options off; API keys have an opt-in "Allow cloud access" scope we never
  tick **[S: api-keys]**.
- The API key can be narrow: **Manage Library** ("Upload new files ... slice a library file") and **Manage Queue**
  ("Add to / remove from / reorder the print queue") **[S: api-keys]**. Keys "cannot perform administrative
  operations" **[S: api-keys]**. We leave out Control Printer, so Claude can stage a job but carlie starts it **[I]**.
- Exact upload/queue endpoints to be checked on our own instance (FastAPI docs page) at setup; the public API page
  documents `X-API-Key` and `POST /queue` **[S: reference/api]**. The wiki is ahead of our 1.2.5.7 in places (it
  mentions 1.2.6 changes) **[S]**, so anything marked "Since 1.2.6" does not apply to us yet.

Needs: BigGuy on and Remote Control reachable while carlie is out; USB stick in the printer; plate cleared before
leaving the house **[I]**.

## Safety when nobody is home

1. **Plate clear.** Bambuddy holds the queue after every print until someone confirms the plate is clear
   ("awaiting_plate_clear ... the queue will not dispatch the next job") **[S: reference/api]**. Rule for us **[I]**:
   before tapping Print, open the live camera and look at the plate. Clear the plate before leaving home.
2. **Spaghetti / foreign objects.** The P2S's own AI camera detection runs on the printer, offline (firmware 01.02 added
   pop-ups for Foreign Object, Spaghetti, Nozzle Clumping) **[S: see `remote-monitoring.md` §4]**. Bambuddy turns
   errors into ntfy alerts (already on) **[M: monitoring.md]**.
3. **First layer.** Turn on "Layer Inspect" in the print dialog **[S: print-queue]** and Bambuddy's "First layer
   complete alert (with camera snapshot)" **[S: README]**, then look at the photo **[I]**.
4. **Filament.** Before a remote print, check the spool has enough left for the job; the first T0a printed air with
   no filament loaded **[M: roadmap lesson 2026-10-31]**. PETG roll open more than ~3 days: dry first (drying rule).
5. **Pause/stop from the phone.** ntfy already tells carlie when a print fails **[M]**; check at setup that Bambuddy's printer card can pause and stop a print **[I: not yet checked]**.

## Setup steps (when carlie says go)

1. Printer: leave a FAT32 USB stick in the top USB-A port.
2. Bambuddy (phone or BigGuy): Settings → turn on default "Layer Inspect" and the first-layer alert; confirm the
   plate-clear confirmation is on.
3. Test route A: upload one small sliced file (a calibration coupon, not a Fabrication part) from the phone, check the
   camera, print. Check it archives with thumbnail.
4. Bambuddy: create an API key with Manage Library + Manage Queue only; store it in Vaultwarden and in a file on
   BigGuy outside OneDrive (`C:\PrintLocal\`), never in git or memory.
5. BigGuy: confirm the Bambu Studio CLI slices a coupon headless into `C:\PrintLocal`, then upload it via the API.
6. End to end from the phone: a Claude thread with Remote Control slices and stages; carlie looks and taps Print.

## Sources (fetched 2026-10-31)

- README: https://raw.githubusercontent.com/maziggy/bambuddy/main/README.md
- CHANGELOG (latest 1.2.5.7, 2026-10-02): https://raw.githubusercontent.com/maziggy/bambuddy/main/CHANGELOG.md
- troubleshooting: https://wiki.bambuddy.cool/reference/troubleshooting/
- print-queue: https://wiki.bambuddy.cool/features/print-queue/
- virtual-printer: https://wiki.bambuddy.cool/features/virtual-printer/
- slicer-api (wiki): https://wiki.bambuddy.cool/features/slicer-api/
- slicer-api README: https://raw.githubusercontent.com/maziggy/bambuddy/main/slicer-api/README.md
- api-keys: https://wiki.bambuddy.cool/features/api-keys/
- reference/api: https://wiki.bambuddy.cool/reference/api/
- Bambu wiki, Developer Mode: https://wiki.bambulab.com/en/knowledge-sharing/enable-developer-mode
- Bambu wiki, LAN mode: https://wiki.bambulab.com/en/knowledge-sharing/enable-lan-mode
- Not read: the file-manager wiki page was fetched but not used.
