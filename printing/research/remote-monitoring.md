# Research: watching the P2S from away (live camera + failure alerts) without Bambu cloud

Added 2026-10-31 (thread "Find open-source remote monitoring for P2S"). Question from carlie: can I see a live
camera feed and get told when a print fails, using open-source tools, while the design stays private?

Tags: **[S]** sourced (a page we fetched and saved), **[F]** forum/Reddit (sourced, one person's view),
**[I]** our inference. Nothing here is **measured**: none of it has been tried on carlie's printer.
Evidence (raw pages, fetch log) is in `/mnt/project-files/research/remote-monitoring/`, not in git: 38 fetches,
25 OK. github.com and the GitHub API were blocked from the cloud (403), so READMEs were read through
raw.githubusercontent.com; two Obico pages and two ha-bambulab doc pages were guessed URLs that 404'd, and the
OctoPrint-BambuPrinter README came back empty, so nothing is cited from them.

**The gap:** the 2026-10-29/30 research (`setup-slicer.md` §4a) answered "how do I print with no network" and
stopped there. It never asked what you give up (watching from away, alerts) or how people get those back without
the cloud. That should have been in it. This file fills it.

## Answer in short

Yes. There are good open-source tools and they support the P2S. All of them need one thing you don't have today:
**the printer on your home network** (LAN Only mode plus Developer Mode). Nothing has to touch Bambu's cloud.

**Recommended setup [I], built on [S] facts below:**
1. Printer joins your home Wi-Fi in **LAN Only** mode, with **LAN Only Liveview** and **Developer Mode** on.
   You keep printing from the USB drive exactly as now.
2. **Bambuddy** (free, open source, self-hosted) runs on your Proxmox lab or on BigGuy. It shows the camera in a
   web page and sends alerts.
3. You open that page from your phone **over your VPN**. Nothing is opened to the internet.
4. Alerts go to your phone through **ntfy**, text only (no photos attached), so no picture of a part leaves home.
5. Failure detection: the printer's own AI spaghetti detection (runs on the printer, works offline) pauses the
   print; Bambuddy turns that error into a phone alert. A second, self-hosted Obico detector is optional, later.

This **reverses your 2026-10-31 decision "USB only, no Wi-Fi, for good"**, so it's your call. The cost is security,
explained in "Tradeoffs" below. If you'd rather stay fully offline, the honest answer is: no remote camera and no
alerts are possible, because the printer has no other way out.

## 1. What firmware 01.03 changed, and the "Authorization Control" fight

- **01.03.00.00 (2026-09-21) changed nothing about access or security.** Its notes list: E3D High-Flow hotend
  support, Z-axis motor noise cancellation, 1000 mm/s travel, faster timelapse loading in Handy, and menu links to
  terms/privacy. **[S]** [P2S firmware history](https://wiki.bambulab.com/en/p2s/manual/p2s-firmware-release-history)
- **The controversy is from January 2025** and was about the older X1/P1/A1 printers. Bambu's firmware "introduce[d]
  authorization controls that require official authorization for critical printer operations", including
  "Initiating a print job (via LAN or cloud mode)"; after updating, third-party tools "will only be able to monitor
  print progress and status (e.g., status updates in HomeAssistant)". **[S]**
  [Bambu blog, 2025-01-16](https://blog.bambulab.com/firmware-update-introducing-new-authorization-control-system-2/)
- **The fix Bambu added after the backlash is Developer Mode:** "an option will be available to leave the MQTT
  channel, live stream, and FTP open. This feature must be manually enabled on the printer, and users who select
  this option will assume full responsibility for securing their local network environment." **[S]**
  [Bambu blog, 2025-01-20](https://blog.bambulab.com/updates-and-third-party-integration-with-bambu-connect/)
- **The P2S has Developer Mode.** Bambu's wiki has an "H2 Series/P2S" section: Settings > LAN Only > turn on LAN Only,
  "Choose whether to enable LAN mode liveview", then turn on Developer Mode after reading a risk warning. "Enabling
  this will open the MQTT channel, live stream, and FTP, giving you full control over your printer and its network
  security." **[S]** [enable Developer Mode](https://wiki.bambulab.com/en/knowledge-sharing/enable-developer-mode)
- 2026 side-story: Bambu sent a cease-and-desist over an OrcaSlicer fork that impersonated the official client on
  Bambu's cloud; a Reddit megathread collects it. **[F]** [r/BambuLab megathread](https://www.reddit.com/r/BambuLab/comments/1tckb9z/)
  It's about cloud access, so it doesn't affect a LAN-only setup. **[I]**

## 2. What can see the P2S camera

- **The P2S runs a local video stream**: "The X1 series and P2S printers run a RTSP server",
  `rtsps://{PRINTER_IP}:322/streaming/live/1`, user `bblp`, password = the LAN access code. **[S]**
  [OpenBambuAPI video.md](https://raw.githubusercontent.com/Doridian/OpenBambuAPI/main/video.md) (community
  reverse-engineering notes). The same page says on H2 printers the stream is off until "LAN Only Liveview" is
  turned on; the P2S likely behaves the same, so turn it on **[I]**.
- **Bambu Studio** can show it with no extra software: "Turn on 'LAN Only Liveview' to view the printer live screen
  in Bambu Studio." **[S]** [enable LAN mode](https://wiki.bambulab.com/en/knowledge-sharing/enable-lan-mode)
  That only helps if you remote-desktop into BigGuy over the VPN; clunky on a phone. **[I]**
- **Bambu Handy over VPN does not work in LAN mode**: "Bambu Handy app is not available when using LAN Mode." **[S]**
  (same LAN mode page). Handy needs the cloud, so it's out.
- **Bambu Connect** (Bambu's own LAN tool): "Liveview functionality is not yet supported." **[S]**
  [Bambu Connect wiki](https://wiki.bambulab.com/en/software/bambu-connect)

## 3. The open-source options, compared

| Tool | P2S? | Camera | Alerts | Needs | Notes |
|---|---|---|---|---|---|
| **Bambuddy** | Yes, listed under "P2 \| P2S" **[S]** | Live MJPEG in browser, one shared stream **[S]** | ntfy, Pushover, Telegram, email, Home Assistant, more; HMS errors, AI failure alerts **[S]** | Developer Mode, same network **[S]** | Docker or a Windows installer **[S]**. Best fit. |
| **ha-bambulab** (Home Assistant) | Has P2S-only entities (airduct mode) **[S]** | Camera entity **[S]** | Through Home Assistant automations **[I]** | LAN + Developer Mode for control; read-only status otherwise **[S]** | Good only if you already run Home Assistant. |
| **go2rtc** | Any RTSP source **[I]** | Re-streams RTSP to WebRTC/MJPEG for browsers **[S]** | None | The RTSP stream (so Developer Mode/Liveview) | A building block, not a full answer. |
| **Obico** (spaghetti detection) | Not directly: its server is built for OctoPrint/Klipper **[S]** | — | Via Bambuddy, which can use a self-hosted Obico ML API to "notify / pause / pause-and-off" **[S]** | Self-hosted server; GPU optional **[S]** | Optional second detector later. |
| **Bambu Open Network** (HA add-on) | ? | Cloud camera | — | Bambu cloud login **[F]** | Uses the cloud. Not for us. |
| OctoPrint-BambuPrinter | Not checked | — | — | — | README fetch came back empty; nothing to report. |

Sources: [Bambuddy README](https://raw.githubusercontent.com/maziggy/bambuddy/main/README.md),
[Bambuddy camera wiki](https://wiki.bambuddy.cool/features/camera/),
[Bambuddy notifications wiki](https://wiki.bambuddy.cool/features/notifications/),
[Hackaday on Bambuddy, 2026-06-13](https://hackaday.com/2026/06/13/bambuddy-says-bye-to-bambu-lab-cloud-services/),
[ha-bambulab docs](https://docs.page/greghesp/ha-bambulab) and [entities](https://docs.page/greghesp/ha-bambulab/entities),
[go2rtc README](https://raw.githubusercontent.com/AlexxIT/go2rtc/master/README.md),
[Obico server README](https://raw.githubusercontent.com/TheSpaghettiDetective/obico-server/release/README.md),
[Bambu Open Network post](https://www.reddit.com/r/BambuLab/comments/1xfizge/home_assistant_reclaim_your_bambu_lab_printer/).

Quotes worth knowing:
- Bambuddy: "Most Bambu printers accept only one camera connection at a time ... Bambuddy opens a single stream to
  the printer and fans the frames out". "Camera access requires Developer Mode". **[S]** (camera wiki)
- Bambuddy: "AI failure detection alerts", "First layer complete alert (with camera snapshot)", "Camera snapshots in
  notifications ... with an **Attach photo** switch per provider". **[S]** (README)
- ha-bambulab: "If you wish to update to these firmware versions and retain write functionality, you must put your
  printer into LAN Mode, and enable Developer Lan Mode." "All read functionality will continue to work." **[S]**

## 4. Failure detection

- **The P2S has its own AI camera detection**, and Bambu keeps improving it: "Optimized AI vision spaghetti
  detection to reduce false alarm"; 01.02 added live-feed pop-ups "for Camera Obstruction, Foreign Object,
  Spaghetti, and Nozzle Clumping Detection." **[S]** (firmware history)
- **It works without the cloud**: in LAN mode "the printer behaves just like when it is not connected to the
  internet and uses local processing", but the model only updates with firmware. **[S]** (LAN mode page; written for
  X1, applying it to the P2S is **[I]**). You already update firmware by USB, so that's covered.
- What's missing offline is the **phone alert**: the printer pauses, but nobody tells you. Bambuddy fills that gap
  by reading the printer's error messages ("HMS error monitoring with history" **[S]**) and pushing them. **[I]**

## 5. Tradeoffs and how to cover them

What Developer Mode opens, in plain words: anyone on your home network who knows the access code (shown on
the printer screen) can watch the camera, control the printer, and **download files from it by FTP**. **[S]** for
what opens; the rest **[I]**. That last part matters for the patent: the printer keeps the last 8 sliced files in
its internal cache, even prints started from the USB drive (`setup-slicer.md` §4a **[S]**). Sliced files are the
part shapes.

How to cover it **[I]** unless marked:
1. **Never forward a port** to the printer or to Bambuddy. Reach them only through your VPN.
2. **Block the printer from the internet at the router** (a firewall rule or parental-control block on its address).
   LAN Only already avoids the cloud **[S]**; the block is a second lock in case a setting flips.
3. **Put the printer on a guest/IoT network** if your router has one, with only the Bambuddy machine allowed to
   reach it. Then a hacked smart plug or visitor's phone can't get at it.
4. **Turn on Bambuddy's login** (its README lists it under "Optional Authentication" **[S]**, so assume it starts off **[I]**) and use a strong password.
5. **Text-only alerts.** Turn the "Attach photo" switch off **[S]** so no picture of a part goes through ntfy's or
   Telegram's servers. Look at the picture over the VPN instead.
6. **Check Bambuddy's settings for any usage/telemetry reporting and turn it off.** A Reddit commenter said
   telemetry was "enabled by default" **[F]** ([thread](https://www.reddit.com/r/BambuLab/comments/1qg4515/bambuddy_stay_connected_to_your_prints/));
   its README doesn't mention it, so we couldn't confirm either way.
7. Know the quality risk: commenters in that thread call it heavily AI-written ("vibe coded") and point out it turns
   off TLS certificate checks for the printer's self-signed certificate **[F]**. Inside a locked-down home network
   that's acceptable **[I]**; it's another reason never to expose it to the internet.
8. Developer Mode means "Bambu Lab will not be able to provide customer support" for problems it causes **[S]**
   (2025-01-20 blog). It can be switched off again on the printer screen. **[I]**

## 6. If carlie says yes: setup order (one step at a time when we do it)

All **[I]**, to be done in its own thread, one literal step per message:
1. Printer screen: Settings > LAN Only: join Wi-Fi, turn on LAN Only, turn on LAN Only Liveview, turn on Developer
   Mode. Write down the printer's IP address and access code (on that page **[S]**, LAN mode wiki).
2. Router: give the printer a fixed address and block its internet.
3. Install Bambuddy (Docker on the Proxmox lab, or the Windows installer on BigGuy, outside OneDrive), add the
   printer by IP + access code + serial number, turn on login.
4. Check the camera shows in Bambuddy on BigGuy, then on the phone over the VPN.
5. Set up ntfy alerts (print failed, paused/error, finished), photos off. Test with a small print.
6. Later, optional: self-hosted Obico ML API as a second spaghetti detector.

Not researched yet: whether Bambuddy sees prints started from the USB drive on the printer screen (it reads live
status over MQTT, so progress and errors should show **[I]**; its README warns that prints sent to internal storage
archive without thumbnails **[S]**).
