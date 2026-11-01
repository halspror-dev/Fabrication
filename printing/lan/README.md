# LAN printing through Bambuddy (no cloud)

Set up 2026-11-01 (thread "Set up LAN printing through Bambuddy"). Plan: `../research/remote-printing.md` route B.
First job printed this way: C1 stringing towers, 2026-11-01 (`../tests/2026-11-01-lan-C1-stringing.md`).

Flow: Claude (Remote Control on BigGuy) slices headless in `C:\PrintLocal\lan\` -> uploads to Bambuddy (CT208,
`http://192.168.68.208:8000`) -> queues it **held** (`manual_start: true`) -> carlie checks the camera and plate,
then taps Print in Bambuddy -> Bambuddy sends it over FTPS to the USB stick in the printer and starts it.
Nothing leaves the LAN. The USB stick must stay in the printer.

## Files (copies of what runs on BigGuy in `C:\PrintLocal\lan\`)
- `flatten_profiles.py`: resolves Studio's stock P2S profiles (`inherits` / `include`) into flat JSONs in
  `C:\PrintLocal\lan\profiles\`, and writes `process-fit-0.20-v1.json` (stock 0.20mm Standard @BBL P2S, plus
  `wall_loops` 3 and `xy_hole_compensation` 0.16). Profiles live as files, so a PC restart or a lost Studio
  preset changes nothing. Rerun after a Studio update. Stock profile set 02.08.00.05 (Studio 02.08.02.61).
- `bambuddy_queue.py FILE.gcode.3mf`: upload + held queue. Never starts a print. Reads the API key at run time
  from `C:\PrintLocal\bambuddy-api-key.txt` (never in git, memory or chat). Finds the printer by IP, so update
  `PRINTER_IP` if the DHCP address moves (it moved .78 -> .51 after a power loss on 2026-11-01).
- `inspect_3mf.py FILE.gcode.3mf`: prints what the sliced file holds (time, grams, temps, walls, compensation).

## Slice command (BigGuy)
```
"C:\Program Files\Bambu Studio\bambu-studio.exe" --datadir "C:\PrintLocal\lan\datadir" --debug 2 --slice 0 --arrange 1 --orient 0 --curr-bed-type "Textured PEI Plate" --load-settings "C:\PrintLocal\lan\profiles\machine.json;C:\PrintLocal\lan\profiles\process-fit-0.20-v1.json" --load-filaments "C:\PrintLocal\lan\profiles\filament.json" --outputdir "C:\PrintLocal\lan" --export-3mf NAME.gcode.3mf "C:\PrintLocal\PART.stl"
```
- The CLI prints nothing to the console. Check the exit code, that the output exists, and `result.json`
  (`return_code`, `error_string` "Success.") in the output dir. `plate_1.gcode` and `result.json` are overwritten
  each run.
- `--datadir` keeps the CLI away from Studio's real config. `--arrange 1` centres the part (STLs start at 0,0).
- Known gap: `printer_model_id` is blank in the file's `slice_info.config` (P2S is N7). Harmless when queued with
  an explicit `printer_id`, as the script does.

## Bambuddy API (1.2.5.7, from its own `/openapi.json`)
- Auth: `X-API-Key` header. Key "claude-bigguy", scopes chosen by carlie: Read Status, Manage Queue, Control
  Printer, Manage Library, Manage Maintenance, Send Notifications; **Allow cloud access off**.
  Only Read Status, Manage Library and Manage Queue are used. Starting stays carlie's tap unless they say otherwise.
- `GET /api/v1/printers/` (P2S is id 1), `GET /api/v1/printers/{id}/status`.
- `POST /api/v1/library/files/` multipart `file` -> `id`.
- `POST /api/v1/queue/` JSON: `library_file_id, printer_id, plate_id, manual_start, use_ams` (default true; send
  false, no AMS), `bed_levelling`/`flow_cali` (off/on/auto), `vibration_cali`, `layer_inspect`, `timelapse`.
- `POST /api/v1/queue/{id}/start` releases a held item (carlie's tap does the same). Not used by Claude.
- `/library/files/add-to-queue` has no `manual_start`, so it can't hold a job: don't use it.

## Things seen on the first run
- Bambuddy's `store_to_sdcard` reads false, but the FTPS send to the USB stick worked anyway.
- `ams_exists` reads true although no AMS is attached; `use_ams: false` printed fine from the external spool.
- HMS 0500-0200-0003-000A was active before and during the print and didn't stop it. Bambu's code list
  (https://e.bambulab.com/query.php?lang=en) has it with a blank description; meaning unknown.
