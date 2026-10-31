# Remote monitoring: how it is set up

Set up 2026-10-31 with carlie (thread "Set up Bambuddy remote monitoring"), from `research/remote-monitoring.md` §6.
No secrets here: the access code, Bambuddy login and ntfy topic live only in Vaultwarden.

## What runs where
- **Printer** (P2S, shows as "3DP-22E-845" in Bambuddy): LAN Only ON, LAN Only Liveview ON, Developer Mode ON, on the main home Wi-Fi at
  192.168.68.78 (DHCP lease; it can change after a router restart until the router reservation is done, then
  update the IP in Bambuddy). LAN Only was switched on before the printer first joined Wi-Fi, so it has never
  connected to Bambu Cloud. Printing still goes by USB drive.
- **Bambuddy 1.2.5.7** (`ghcr.io/maziggy/bambuddy:1.2.5.7`, pinned) in Docker in CT208 on pve
  (192.168.68.208, Debian 13, 2 cores, 2 GB). Compose and data in `/opt/bambuddy` (`data/`, `logs/`).
  Page: `http://192.168.68.208:8000` on the LAN, or from the phone over Tailscale. Login required.
  CT208 is homelab's (backup in the 03:00 job, Uptime Kuma HTTP monitor); see project-notes
  `archive/printing/2026-10-31-homelab-bambuddy-host-answers.md`.
- **Alerts:** ntfy.sh, private random topic, events Print Completed / Failed / Stopped, Printer Error, Printer Offline.

## Privacy line (carlie 2026-10-31)
The home network is fine; the cloud is the line. So, in Bambuddy:
- OFF: Check printer firmware (calls Bambu), Git Backup (GitHub), MakerWorld (hidden from the sidebar),
  AI Failure Detection (needs an Obico server we don't run; the printer's own spaghetti detection is used).
- ON, kept on the lab: auto-archive of sliced files, thumbnails, finish photos.
- Photos in ntfy alerts are carlie's choice: "photos of prints isnt the same as giving away stl files".
  Sliced files and STLs never leave the house. No telemetry setting exists (Settings checked 2026-10-31;
  the announcements feed only downloads a signed file from GitHub).

## Upgrading Bambuddy
In CT208 (`pct enter 208` alone, check the prompt says `root@bambuddy`): edit the image tag in
`/opt/bambuddy/docker-compose.yml`, then `docker compose pull && docker compose up -d`, after that night's backup
exists. Never `:latest` (homelab rule).

## Follow-ups
- Router (postponed by carlie): DHCP reservation for the printer, block its internet.
- Homelab: HTTPS name `bambuddy.home.arpa` via Caddy (optional), record CT208 in SPEC.md, check the next morning
  that a `vzdump-lxc-208` backup exists.
- Check on the next print that it shows in Bambuddy when started from the USB drive, and that the alert arrives.

## Gotcha
- After adding the printer, temps read 0 °C and Bambuddy's diagnostic said "the printer has not published any
  status reports": the serial number was mistyped (it is case-sensitive). Retyping it fixed it at once.
