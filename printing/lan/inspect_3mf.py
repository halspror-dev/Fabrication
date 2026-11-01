"""Report what a sliced .gcode.3mf contains. Run: python -I inspect_3mf.py FILE"""
import json, re, sys, zipfile

z = zipfile.ZipFile(sys.argv[1])
print("entries:")
for i in z.infolist():
    print(f"  {i.filename} | {i.file_size}")

print("\nslice_info.config:")
print(z.read("Metadata/slice_info.config").decode("utf-8"))

g = z.read("Metadata/plate_1.gcode").decode("utf-8", "replace")
print("gcode header:")
for line in g.splitlines()[:40]:
    if re.search(r"HEADER|total|estimated|time|filament|layer|model|weight|density", line, re.I):
        print(" ", line[:110])
print("\ngcode lines:", g.count("\n"))
for pat in (r"^\s*M190\b.*", r"^\s*M109\b.*", r"^\s*M104\b.*", r"^\s*M140\b.*"):  # Studio indents some lines
    hits = re.findall(pat, g, re.M)
    print(f"{pat}: {len(hits)} hits; first {hits[:3]}")

xs, ys, zs = [], [], []
cur_z = 0.0
body = g.split("; CHANGE_LAYER", 1)[-1].split("; EXECUTABLE_BLOCK_END")[0]
for m in re.finditer(r"^G[01] (.*)$", body, re.M):
    a = dict(re.findall(r"([XYZE])(-?[\d.]+)", m.group(1)))
    if "Z" in a:
        cur_z = float(a["Z"])
    if "X" in a and "Y" in a and float(a.get("E", 0)) > 0:
        xs.append(float(a["X"]))
        ys.append(float(a["Y"]))
        zs.append(cur_z)
if xs:
    print(f"extruded XY extent: X {min(xs)}..{max(xs)}, Y {min(ys)}..{max(ys)}, max Z {max(zs)}")

c = json.loads(z.read("Metadata/project_settings.config"))
keys = ["printer_settings_id", "print_settings_id", "filament_settings_id", "printer_model", "nozzle_diameter",
        "curr_bed_type", "wall_loops", "xy_hole_compensation", "xy_contour_compensation",
        "elefant_foot_compensation", "layer_height", "sparse_infill_density", "enable_support",
        "nozzle_temperature", "nozzle_temperature_initial_layer", "textured_plate_temp",
        "textured_plate_temp_initial_layer", "filament_type", "filament_flow_ratio", "different_settings_to_system"]
print("\nproject_settings.config:")
for k in keys:
    print(f"  {k} = {c.get(k)}")
