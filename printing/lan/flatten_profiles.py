"""Resolve Bambu Studio's stock "inherits" chains into flat JSON profiles.

Reads the system profiles shipped with Studio (read-only) and writes flat
copies to lan/profiles/ for the headless CLI, plus the fit-0.20-v1 process.
Run on BigGuy from C:\\PrintLocal\\lan: python -I flatten_profiles.py
"""
import json
from pathlib import Path

BBL = Path(r"C:\Program Files\Bambu Studio\resources\profiles\BBL")
OUT = Path(__file__).parent / "profiles"

TARGETS = {
    "machine": "Bambu Lab P2S 0.4 nozzle",
    "process": "0.20mm Standard @BBL P2S",
    "filament": "Bambu PETG Matte @BBL P2S 0.4 nozzle",
}
# fit-0.20-v1: 3 walls (set 1), X-Y hole compensation 0.16 (measured: collar reprint 2026-10-31, pin fits)
VARIANT = {"wall_loops": "3", "xy_hole_compensation": "0.16"}


def index(kind):
    """Map profile name -> path for one profile folder."""
    out = {}
    for p in (BBL / kind).rglob("*.json"):
        name = json.loads(p.read_text(encoding="utf-8")).get("name")
        if name:
            out[name] = p
    return out


def resolve(name, names, chain):
    data = json.loads(names[name].read_text(encoding="utf-8"))
    chain.append(names[name].name)
    merged = {}
    if data.get("inherits"):
        merged = resolve(data["inherits"], names, chain)
    for inc in data.get("include", []):
        merged.update(resolve(inc, names, chain))
    keep = {k: v for k, v in merged.items() if k not in ("name", "setting_id", "description")}
    keep.update({k: v for k, v in data.items() if k not in ("inherits", "include")})
    return keep


def main():
    OUT.mkdir(exist_ok=True)
    flat = {}
    for kind, name in TARGETS.items():
        chain = []
        d = resolve(name, index(kind), chain)
        d["type"], d["name"], d["from"] = kind, name, "system"
        d["instantiation"] = "true"
        d.pop("inherits", None)
        flat[kind] = d
        path = OUT / f"{kind}.json"
        path.write_text(json.dumps(d, indent=2), encoding="utf-8")
        print(f"{kind}: {path.name}, {len(d)} keys, chain: {' <- '.join(chain)}")

    v = dict(flat["process"])
    before = {k: v.get(k) for k in VARIANT}
    v.update(VARIANT)
    v["name"] = "fit-0.20-v1"
    v["from"] = "User"
    v.pop("setting_id", None)
    path = OUT / "process-fit-0.20-v1.json"
    path.write_text(json.dumps(v, indent=2), encoding="utf-8")
    print(f"variant: {path.name}, stock values were {before}, now {VARIANT}")


if __name__ == "__main__":
    main()
