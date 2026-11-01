"""Upload a sliced .gcode.3mf to Bambuddy and queue it HELD for manual start.

Never calls /queue/{id}/start: carlie starts the print in Bambuddy after a camera check.
Never prints the key, serial or access code: only the whitelisted fields below reach the output.
The key is read at run time from C:\\PrintLocal\\bambuddy-api-key.txt (never in git).
Run on BigGuy: python -I bambuddy_queue.py FILE.gcode.3mf
"""
import json, sys, urllib.error, urllib.request, uuid
from pathlib import Path

HOST = "http://192.168.68.208:8000"
KEY = Path(r"C:\PrintLocal\bambuddy-api-key.txt").read_text(encoding="utf-8-sig").strip()
PRINTER_IP = "192.168.68.51"  # DHCP until reserved on the router; update if the printer moves


def call(method, path, body=None, ctype="application/json"):
    req = urllib.request.Request(HOST + path, data=body, method=method)
    req.add_header("X-API-Key", KEY)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:500]


def pick(d, *keys):
    return {k: d.get(k) for k in keys}


def stop(step, status, detail):
    print(f"STOPPED at {step}: HTTP {status}: {detail}")
    sys.exit(1)


def main():
    path = Path(sys.argv[1])

    status, printers = call("GET", "/api/v1/printers/")
    if status != 200:
        stop("GET printers", status, printers)
    print("printers:", [pick(p, "id", "name", "model", "ip_address", "is_active") for p in printers])
    match = [p for p in printers if p.get("ip_address") == PRINTER_IP]
    if len(match) != 1:
        stop("choose printer", 0, f"{len(match)} printers at {PRINTER_IP}")
    pid = match[0]["id"]

    status, st = call("GET", f"/api/v1/printers/{pid}/status")
    if status == 200:
        print("printer status:", pick(st, "connected", "state", "store_to_sdcard", "ams_exists", "door_open", "hms_errors"),
              "sdcard:", st.get("sdcard"))
    else:
        print(f"printer status: HTTP {status}: {st}")

    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n").encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    status, up = call("POST", "/api/v1/library/files/", body, f"multipart/form-data; boundary={boundary}")
    if status != 200:
        stop("upload", status, up)
    print("upload:", pick(up, "id", "filename", "file_type", "file_size", "duplicate_of"))
    fid = up["id"]

    status, queue = call("GET", f"/api/v1/queue/?printer_id={pid}")
    if status == 200:
        dupes = [q for q in queue if q.get("library_file_id") == fid and q.get("status") == "pending"]
        if dupes:
            print("already queued, not adding again:", [pick(q, "id", "status", "manual_start") for q in dupes])
            return

    item = {"library_file_id": fid, "printer_id": pid, "plate_id": 1, "manual_start": True, "use_ams": False,
            "bed_levelling": "auto", "flow_cali": "auto", "vibration_cali": True, "layer_inspect": False,
            "timelapse": False}
    status, q = call("POST", "/api/v1/queue/", json.dumps(item).encode())
    if status not in (200, 201):
        stop("queue", status, q)
    print("queued:", pick(q, "id", "status", "position", "printer_id", "library_file_id", "library_file_name",
                          "plate_id", "manual_start", "use_ams", "waiting_reason", "error_message"))

    status, q2 = call("GET", f"/api/v1/queue/{q['id']}")
    print("re-read:", pick(q2, "id", "status", "manual_start", "started_at", "waiting_reason") if status == 200 else (status, q2))


if __name__ == "__main__":
    main()
