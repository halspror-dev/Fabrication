"""v0.96 3D model: real-shape clearance check (every pair of bodies, open and closed) and the render pages.
Usage (from drawing-scripts/):
  python3 v096_3d.py check            short PASS/FAIL per state (full table: check3d-v096-table.txt); exits 1 on a FAIL
  python3 v096_3d.py render OUTDIR    writes the preview pages v096-p1..p4.png
Same renderer and hardware models as render3d.py / check3d.py (v0.95); geometry comes from v096.py.
"""
import sys, os, math
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv
sys.argv = ["render3d.py", os.path.join(HERE, "templates.py")]
import render3d as R            # renderer, mesh helpers, v0.95 trigger and sleeve solids (its __main__ does not run)
sys.argv = _argv
import v096 as V

C = R.COLORS
LEVER_COL = (0.85, 0.35, 0.30)
CT, LT = V.CT, V.LT
TY0, TY1, HD = R.TY0, R.TY1, R.HD
FULL = -V.BT / V.NOSE           # radians: nose down 0.15" at 1.50" from the pivot

# num: (name, source, qty per handle, where)
HW = {
    1: ("Clevis pin 1/4\" x 1/2\", stainless", "Rivetsonline CLPF-0250-0500", 1, "trigger pivot, in a handle-plate lobe"),
    2: ("Nylon washer 1/4\" (0.265 x 0.625 x 0.060)", "Bolt Depot #15939", 1, "trigger pivot, between trigger and handle"),
    3: ("Nylon-insert locknut 10-24", "Bolt Depot #2552", 4, "up-stop, 2 flange screws, lever pivot"),
    4: ("Button-head screw 10-24 x 5/8\"", "Bolt Depot #4396", 3, "up-stop, 2 flange screws (heads on the trigger side)"),
    5: ("Shoulder bolt 1/4\" x 1/4\" shoulder, 10-24", "Bolt Depot #14221", 1, "lever pivot, head under the collar"),
    6: ("Nylon spacer 5 mm ID x 10 mm OD x 5 mm", "Bolt Depot #13775", 1, "up-stop, under the trigger tail"),
    7: ("#10 flat washer", "Bolt Depot #2946", 4, "up-stop nut, flange nuts, lever pivot nut"),
    10: ("Screw post, barrel half, 3/16\" x 5/8\"", "MyBinding SO058ASP", 4, "sleeves (head on the outside)"),
    11: ("Screw post, screw half", "MyBinding SO058ASP", 4, "sleeves (head on the inside)"),
    14: ("Hitch pin clip, stainless, 0.080\" wire", "Bolt Depot #27207", 1, "through the trigger pivot pin, outside the handle"),
    15: ("Shim washer 1/32\" (printed)", "printed PETG", 1, "under the trigger pivot pin head"),
}
PARTS = {1: "can", 2: "valve cup", 3: "button", 10: "collar", 11: "lever", 12: "handle plate", 14: "trigger",
         16: "trigger sleeve", 18: "grip sleeve"}
JOINT_PARTS = {"pivot": {"trigger", "handle plate"}, "up-stop": {"handle plate", "trigger"},
               "trigger sleeve": {"trigger", "trigger sleeve"}, "grip sleeve": {"handle plate", "grip sleeve"},
               "flange": {"handle plate", "collar"}, "lever pivot": {"lever", "collar"}}
TOUCH_ALL = [("can", "valve cup"), ("valve cup", "button"), ("handle plate", "collar"), ("handle plate", "grip sleeve"),
             ("trigger", "trigger sleeve"), ("trigger", "button"), ("collar", "lever")]
# (name, lever angle, can centre, trigger full?, extra by-design pairs)
STATES = (("CLAMPED", "REST", V.THETA_S, (0, 0), False, [("valve cup", "collar"), ("valve cup", "lever")]),
          ("CLAMPED", "FULL", V.THETA_S, (0, 0), True, [("valve cup", "collar"), ("valve cup", "lever")]),
          ("LEVER OPEN", "can seated", V.THETA_OPEN, (0, 0), False, [("valve cup", "collar")]),
          ("LEVER OPEN", "can at entry", V.THETA_OPEN, V.EC, False, []))


def build(th=V.THETA_S, can_c=(0.0, 0.0), full=False, show_can=True, show_trigger=True, show_hw=True, explode=0.0):
    R.TRIS.clear(); R.PID.clear(); R.COL.clear(); R.INST.clear()
    e = explode
    O_ = lambda dx=0.0, dy=0.0, dz=0.0: (dx * e, dy * e, dz * e)
    OFF = dict(collar=O_(dz=-1.0), lever=O_(dz=0.55), trigger=O_(dy=-1.35), tsc=O_(dx=0.8, dy=-1.35), gsc=O_(dx=-0.8))
    cx, cy = can_c
    if show_can and e == 0:
        R.revolve([(0, -3.6), (1.28, -3.6), (1.28, -0.95), (1.15, -0.85), (1.0, -0.65), (0.75, -0.35), (0.6, -0.15), (V.NECK_R, -0.13),
                   (V.NECK_R, 0.0), (0, 0.0)], 1, C["can"], center=(cx, cy, 0))
        R.revolve([(0, 0), (V.CUP_R, 0), (V.CUP_R, V.CUP_H), (0, V.CUP_H)], 2, C["ring"], center=(cx, cy, 0))
        R.revolve([(0, V.CUP_H), (0.33, V.CUP_H), (0.33, 0.765), (0, 0.765)], 3, C["button"], n=48, center=(cx, cy, 0))
    oc = OFF["collar"]
    R.extrude(V.collar, "xy", -CT, 0, 10, C["collar"], off=oc)
    for p in V.pads:
        R.extrude(p, "xy", 0, V.PAD_H, 10, C["collar"], off=oc)
    R.extrude(V.stop_post, "xy", 0, LT, 10, C["collar"], off=oc)
    R.extrude(V.flange, "xz", V.FL_Y[0], V.FL_Y[1], 10, C["collar"], off=oc)
    R.extrude(V.lever(th), "xy", 0, LT, 11, LEVER_COL, off=OFF["lever"])
    R.extrude(V.frame, "xz", R.FY0, R.FY1, 12, C["frame"])
    for t in R.GSL:
        R.add_tri(*[tuple(v + np.array(OFF["gsc"])) for v in t], 18, R.SLEEVE)
    if show_trigger:
        R.extrude(R.trig, "xz", TY0, TY1, 14, C["trigger"], off=OFF["trigger"])
        for t in R.TSL:
            R.add_tri(*[tuple(v + np.array(OFF["tsc"])) for v in t], 16, R.SLEEVE)
    if show_hw:
        pid = [100]
        def add(num, joint, anchor, fn, off=(0, 0, 0)):
            p = pid[0]; pid[0] += 1
            fn(p, *off)
            R.INST.append((p, num, joint, tuple(a + o for a, o in zip(anchor, off))))
        px, pz = V.P
        sx, sz = V.g["S"]
        SR = V.g["STOP_R"]
        if show_trigger:      # trigger pivot, as v0.95
            yh = TY0 - 0.031
            add(15, "pivot", (px, yh + 0.015, pz + 0.22), lambda p, ox, oy, oz: R.hw_washer("y", px + ox, 0, pz + oz, yh + oy, 1, p, 0.1325, 0.25, 0.031, R.NYLON), O_(dy=-1.8))
            add(1, "pivot", (px, yh - 0.06, pz), lambda p, ox, oy, oz: R.hw_clevis_y(px + ox, pz + oz, yh + oy, p), O_(dy=-2.3))
            add(2, "pivot", (px, TY1 + 0.03, pz + 0.30), lambda p, ox, oy, oz: R.hw_washer("y", px + ox, 0, pz + oz, TY1 + oy, 1, p, 0.1325, 0.3125, 0.060, R.NYLON), O_(dy=-0.65))
            add(14, "pivot", (px + 0.4, yh + 0.40, pz), lambda p, ox, oy, oz: R.hw_rclip_y(px + ox, yh + 0.40 + oy, pz + oz, p), O_(dy=0.9))
        # up-stop, as v0.95
        add(4, "up-stop", (sx, R.FY0 - 0.197 - 0.105, sz), lambda p, ox, oy, oz: R.hw_button("y", sx + ox, 0, sz + oz, R.FY0 - 0.197 + oy, 1, p), O_(dy=-2.3))
        add(6, "up-stop", (sx, R.FY0 - 0.1, sz + SR), lambda p, ox, oy, oz: R.hw_spacer("y", sx + ox, 0, sz + oz, R.FY0 - 0.197 + oy, 1, p), O_(dy=-0.7))
        add(7, "up-stop", (sx, R.FY1 + 0.03, sz + 0.25), lambda p, ox, oy, oz: R.hw_washer("y", sx + ox, 0, sz + oz, R.FY1 + oy, 1, p, 0.1095, 0.25, 0.049, R.STEEL), O_(dy=0.45))
        add(3, "up-stop", (sx, R.FY1 + 0.049 + 0.236, sz), lambda p, ox, oy, oz: R.hw_locknut("y", sx + ox, 0, sz + oz, R.FY1 + 0.049 + oy, 1, p), O_(dy=0.85))
        # v0.96 flange: 2 button screws from the trigger side through plate + flange, washer + locknut on the outside
        yo = V.FL_Y[1]
        for fx, fz in V.FL_HOLES:
            add(4, "flange", (fx, R.FY0 - 0.06, fz), lambda p, ox, oy, oz, fx=fx, fz=fz: R.hw_button("y", fx + ox, 0, fz + oz, R.FY0 + oy, 1, p), O_(dy=-1.2))
            add(7, "flange", (fx, yo + 0.03, fz + 0.25), lambda p, ox, oy, oz, fx=fx, fz=fz: R.hw_washer("y", fx + ox, 0, fz + oz, yo + oy, 1, p, 0.1095, 0.25, 0.049, R.STEEL), O_(dy=0.7))
            add(3, "flange", (fx, yo + 0.049 + 0.2, fz), lambda p, ox, oy, oz, fx=fx, fz=fz: R.hw_locknut("y", fx + ox, 0, fz + oz, yo + 0.049 + oy, 1, p), O_(dy=1.1))
        # v0.96 lever pivot: shoulder bolt up from under the collar, #10 washer on the shoulder end, locknut on top
        lx, ly = V.O
        zs = -CT + 0.25
        add(5, "lever pivot", (lx, ly, -CT - 0.12), lambda p, ox, oy, oz: R.hw_shoulder("z", lx + ox, ly + oy, 0, -CT + oz, 1, p), O_(dz=-1.7))
        add(7, "lever pivot", (lx + 0.2, ly, zs + 0.03), lambda p, ox, oy, oz: R.hw_washer("z", lx + ox, ly + oy, 0, zs + oz, 1, p, 0.1095, 0.25, 0.049, R.STEEL), O_(dz=0.9))
        add(3, "lever pivot", (lx, ly, zs + 0.049 + 0.2), lambda p, ox, oy, oz: R.hw_locknut("z", lx + ox, ly + oy, 0, zs + 0.049 + oz, 1, p), O_(dz=1.2))
        if show_trigger:
            for hx, hz in V.g["SCALE_HOLES"]:
                x, z = hx + px, hz + pz
                add(10, "trigger sleeve", (x, TY0 - HD - 0.06, z), lambda p, ox, oy, oz, x=x, z=z: R.hw_post_barrel("y", x + ox, 0, z + oz, TY0 - HD + oy, 1, p), O_(dy=-2.55))
                add(11, "trigger sleeve", (x, TY1 + HD + 0.06, z), lambda p, ox, oy, oz, x=x, z=z: R.hw_post_screw("y", x + ox, 0, z + oz, TY1 + HD + oy, -1, p), O_(dy=-0.25))
        for x, z in V.g["GRIP_HOLES"]:
            add(10, "grip sleeve", (x, R.FY1 + HD + 0.06, z), lambda p, ox, oy, oz, x=x, z=z: R.hw_post_barrel("y", x + ox, 0, z + oz, R.FY1 + HD + oy, -1, p), O_(dy=1.1))
            add(11, "grip sleeve", (x, R.FY0 - HD - 0.06, z), lambda p, ox, oy, oz, x=x, z=z: R.hw_post_screw("y", x + ox, 0, z + oz, R.FY0 - HD + oy, 1, p), O_(dy=-1.1))
    if full:                 # trigger, its sleeve and the pivot hardware turn about the pivot
        moving = {14, 16} | {p for p, n, j, a in R.INST if j in ("pivot", "trigger sleeve")}
        for i, p in enumerate(R.PID):
            if p in moving:
                R.TRIS[i] = tuple(tuple(_rot(np.array(v))) for v in R.TRIS[i])
        R.INST[:] = [(p, n, j, tuple(_rot(np.array(a))) if p in moving else a) for p, n, j, a in R.INST]


def _rot(v):
    cx, cz = V.P
    c, s = math.cos(FULL), math.sin(FULL)
    x, z = v[..., 0] - cx, v[..., 2] - cz
    out = np.array(v, float)
    out[..., 0], out[..., 2] = cx + x * c - z * s, cz + x * s + z * c
    return out


# ---------------- real-shape clearance check ----------------
STEP, NEAR, MIN_GAP = 0.012, 0.25, 0.03
sys.argv = ["check3d.py", os.path.join(HERE, "templates.py")]
import check3d as K            # reuse its surface sampler (its __main__ does not run)
sys.argv = _argv


def bodies():
    tri = np.array(R.TRIS, float); pid = np.array(R.PID)
    names, joints, count = dict(PARTS), {}, {}
    for p, num, joint, _ in R.INST:
        k = (num, joint); count[k] = count.get(k, 0) + 1
        names[p] = "#%d %s (%s)" % (num, HW[num][0].split(",")[0].split(" (")[0], joint) + (" %d" % count[k] if count[k] > 1 else "")
        joints[p] = joint
    return {p: (names.get(p, str(p)), joints.get(p), K.sample(tri[pid == p])) for p in sorted(set(pid.tolist()))}


def run_check():
    res = {}
    for name, sub, th, can_c, full, extra in STATES:
        build(th, can_c, full)
        B = bodies()
        touch = TOUCH_ALL + extra
        def by_design(a, ja, b, jb):
            if ja and jb and ja == jb:
                return True
            if ja and b in JOINT_PARTS.get(ja, ()) or jb and a in JOINT_PARTS.get(jb, ()):
                return True
            return (a, b) in touch or (b, a) in touch
        items = list(B.values())
        lo = [q.min(0) for _, _, q in items]; hi = [q.max(0) for _, _, q in items]
        rows = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if np.any(np.maximum(lo[i], lo[j]) - np.minimum(hi[i], hi[j]) > NEAR):
                    continue
                (n, jn, p), (m, jm, q) = items[i], items[j]
                blo, bhi = np.maximum(lo[i], lo[j]) - NEAR, np.minimum(hi[i], hi[j]) + NEAR
                p = p[np.all((p >= blo) & (p <= bhi), axis=1)]; q = q[np.all((q >= blo) & (q <= bhi), axis=1)]
                if not len(p) or not len(q):
                    continue
                small, big = (p, q) if len(p) < len(q) else (q, p)
                d, _ = cKDTree(big).query(small, distance_upper_bound=NEAR)
                if d.min() < NEAR:
                    rows.append((float(d.min()), n, m, by_design(n, jn, m, jm)))
        res[(name, sub)] = sorted(rows)
    return res


if __name__ == "__main__":
    if sys.argv[1] == "check":
        res = run_check()
        bad, table = 0, []
        for (st, sub), rows in res.items():
            table.append("== %s, %s" % (st, sub))
            table += ["%.3f  %-45s | %-45s %s" % (d, a, b, "by design" if des else "") for d, a, b, des in rows if not des or d < 0.02]
            free = [r for r in rows if not r[3]]
            fails = [r for r in free if r[0] < MIN_GAP]
            bad += len(fails)
            near = free[0] if free else None
            print("%-10s %-13s %s  closest free pair %s" % (st, sub, "FAIL" if fails else "PASS",
                  "%.3f\" %s | %s" % (near[0], near[1], near[2]) if near else "none"))
            for d, a, b, _ in fails:
                print("   FAIL %.3f\"  %s | %s" % (d, a, b))
        open(os.path.join(HERE, "check3d-v096-table.txt"), "w").write("\n".join(table) + "\n")
        print("RESULT: %s (min gap %.2f\"). Full table: check3d-v096-table.txt" % ("PASS" if not bad else "%d FAIL" % bad, MIN_GAP))
        sys.exit(1 if bad else 0)

    # ---------------- render pages ----------------
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    RED, GREEN = "#c0392b", "#1e7b34"

    def panel(fig, rect, img, info, cap, labels=(), balloons=True, only=None, min_px=150, capcol="black"):
        ax = fig.add_axes(rect); ax.imshow(img, interpolation="lanczos"); ax.axis("off")
        ax.set_title(cap, fontsize=8, weight="bold", loc="left", color=capcol)
        for p3, txt, (dx, dy) in labels:
            x, y = R.project(p3, info)
            ax.annotate(txt, (x, y), (x + dx, y + dy), fontsize=7, weight="bold", color=RED,
                        arrowprops=dict(arrowstyle="-", lw=0.6, color=RED), bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))
        if not balloons:
            return ax
        idb = R.LAST_IDB; Hh, Ww = idb.shape; used = []
        for p, num, joint, anchor in R.INST:
            if only is not None and num not in only:
                continue
            ys, xs = np.nonzero(idb == p)
            if len(xs) < min_px:
                continue
            cx, cy = xs.mean(), ys.mean()
            k = np.argmin((xs - cx) ** 2 + (ys - cy) ** 2); cx, cy = xs[k], ys[k]
            dx, dy = cx - Ww / 2, cy - Hh / 2; n = math.hypot(dx, dy) or 1.0
            bx, by = cx + 90 * dx / n, cy + 90 * dy / n
            for _ in range(12):
                if all(math.hypot(bx - ux, by - uy) > 44 for ux, uy in used):
                    break
                bx, by = bx - 30 * dy / n, by + 30 * dx / n
            bx, by = min(max(bx, 25), Ww - 25), min(max(by, 25), Hh - 25)
            used.append((bx, by))
            ax.annotate(str(num), (cx, cy), (bx, by), fontsize=6, weight="bold", ha="center", va="center",
                        arrowprops=dict(arrowstyle="-", lw=0.5, color=RED), bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=RED, lw=0.7))
        return ax

    def legend(fig, y_top):
        fig.text(0.05, y_top, "HARDWARE (balloon numbers). All on hand (BUY-SHEET 'On hand'); printed PETG: collar, lever, handle plate, trigger, 2 sleeves, shim.", fontsize=7.5, weight="bold")
        rows = ["%-3s %-44s %-27s %4s  %s" % ("#", "part", "buy", "qty", "where")]
        rows += ["%-3d %-44s %-27s %4d  %s" % (k, n, s, q, w) for k, (n, s, q, w) in HW.items()]
        fig.text(0.05, y_top - 0.008, "\n".join(rows), fontsize=5.6, family="monospace", va="top", linespacing=1.45)

    def cup_rim(ax, info, c):
        a = np.linspace(0, 2 * np.pi, 200)
        xs, ys = zip(*[R.project((c[0] + V.CUP_R * math.cos(t), c[1] + V.CUP_R * math.sin(t), V.CUP_H), info) for t in a])
        ax.plot(xs, ys, "--", lw=1.6, color="#1f5fbf")

    # page 1: assembled, clamped
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.05, 0.968, "v0.96 ON A CAN: lever CLAMPED (trigger at rest)", fontsize=11, weight="bold")
    fig.text(0.05, 0.953, "Blue = collar (one printed piece: plate under the lip, 2 seat pads, stop post, upright flange). Red = cam lever on a shoulder bolt.\n"
             "Tan = handle plate, bolted flat to the collar flange with 2 screws (no tabs, no clips). Dark gray = trigger, charcoal = printed sleeves.\n"
             "Trigger, sleeves, pivot lobes and up-stop are v0.95, unchanged. Red balloons = hardware number (list at the bottom).", fontsize=7, va="top")
    build()
    img, info = R.render(14, -60)
    panel(fig, [0.03, 0.535, 0.94, 0.36], img, info, "From the front-right (trigger side)",
          [(V.place_pt(V.THUMB[0], V.THETA_S) + (LT,), "CAM LEVER (clamped)", (130, -160)), ((-1.0, 0.0, 1.3), "TRIGGER", (-230, -170)),
           ((-4.7, -0.1, -3.4), "GRIP", (-200, 30))])
    build()
    img, info = R.render(22, 130)
    panel(fig, [0.03, 0.185, 0.94, 0.35], img, info, "From the back-left (flange side)",
          [((-1.3, V.FL_Y[1], 0.55), "COLLAR FLANGE + 2 screws", (-360, 150)), ((-3.0, 0.22, 0.2), "HANDLE plate", (300, 130))])
    legend(fig, 0.17)
    fig.savefig(os.path.join(out, "v096-p1.png"), dpi=110); plt.close(fig)

    # page 2: lever open vs clamped, 3/4 and top views
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.05, 0.968, "CAM LEVER: OPEN (can going on or off) and CLAMPED", fontsize=11, weight="bold")
    fig.text(0.05, 0.953, "ON: flip the lever open (forward), drop the valve cup through the big entry hole, slide the can 10 mm back into the seat, fold the\n"
             "lever back until it snaps over centre onto its stop. The jaw on the spring arm squeezes the cup into the 2 seat pads (3-point clamp).\n"
             "OFF: flip the lever forward, slide the can 10 mm out to the entry hole, lift. Right column: top view, trigger and handle hidden; dashed blue = valve cup rim.", fontsize=7, va="top")
    for r, (cap, th, cc, col) in enumerate((("OPEN: lever flipped 93 deg, can at entry hole", V.THETA_OPEN, V.EC, RED),
                                            ("CLAMPED: lever 8 deg past centre, on its stop", V.THETA_S, (0, 0), GREEN))):
        yb = 0.49 - r * 0.45
        build(th, cc)
        img, info = R.render(30, -55, W=1000, H=1000, fit_ids=[10, 11], margin=0.10)
        tip = V.place_pt(V.THUMB[0], th)
        panel(fig, [0.02, yb, 0.47, 0.40], img, info, cap, [((tip[0], tip[1], LT), "lever", (60, -90)),
              ((V.O[0], V.O[1], 0.45), "pivot", (90, -60))], only=(3, 5, 7), min_px=60, capcol=col)
        build(th, cc, show_trigger=False, show_hw=True)
        lhw = {p for p, n, j, a in R.INST if j == "lever pivot"}
        keep = [i for i, p in enumerate(R.PID) if (p < 100 and p not in (12, 18)) or p in lhw]
        R.TRIS[:] = [R.TRIS[i] for i in keep]; R.COL[:] = [R.COL[i] for i in keep]; R.PID[:] = [R.PID[i] for i in keep]
        R.TRIS.append(((-1.0, -1.2, 0), (-1.0, -1.2, 0), (-1.0, -1.2, 0))); R.PID.append(99); R.COL.append(C["collar"])
        R.TRIS.append(((3.25, 1.9, 0), (3.25, 1.9, 0), (3.25, 1.9, 0))); R.PID.append(99); R.COL.append(C["collar"])
        img, info = R.render(90, -90, W=1000, H=1000, fit_ids=[99], margin=0.04)
        ax = panel(fig, [0.51, yb, 0.47, 0.40], img, info, "Top view (collar close-up left)", [], balloons=False)
        cup_rim(ax, info, cc)
        for a, nm in zip(V.PAD_ANGS, ("seat pad", "seat pad")):
            q = V.u(a)
            x, y = R.project((1.0 * q[0], 1.0 * q[1], V.PAD_H), info)
            ax.annotate(nm, (x, y), (x - 70, y + (-40 if a < 180 else 40)), fontsize=7, color=RED, weight="bold",
                        arrowprops=dict(arrowstyle="-", lw=0.6, color=RED))
        if th == V.THETA_S:
            x, y = R.project(V.place_pt(V.PADC, th) + (LT,), info)
            ax.annotate("jaw on spring arm", (x, y), (x + 90, y + 140), fontsize=7, color=RED, weight="bold", arrowprops=dict(arrowstyle="-", lw=0.6, color=RED))
            x, y = R.project(tuple(V.stop_c) + (LT,), info)
            ax.annotate("stop post", (x, y), (x - 120, y - 60), fontsize=7, color=RED, weight="bold", arrowprops=dict(arrowstyle="-", lw=0.6, color=RED))
        else:
            x, y = R.project((V.EC[0], V.EC[1] - 0.69, 0), info)
            ax.annotate("entry hole", (x, y), (x + 60, y + 70), fontsize=7, color=RED, weight="bold", arrowprops=dict(arrowstyle="-", lw=0.6, color=RED))
    fig.savefig(os.path.join(out, "v096-p2.png"), dpi=110); plt.close(fig)

    # page 3: trigger rest and full squeeze, side view (trigger side), lever clamped
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.05, 0.968, "TRIGGER: AT REST and AT FULL SQUEEZE (lever clamped)", fontsize=11, weight="bold")
    fig.text(0.05, 0.953, "Seen from the trigger side. The nose presses the button down 0.15\" at full squeeze. Trigger, sleeves, pivot lobes and up-stop are v0.95;\n"
             "the 2 new flange screw heads (4) sit below the trigger's neck and stay clear in both states (check3d-v096).", fontsize=7, va="top")
    for r, (cap, full, col) in enumerate((("AT REST: tail on the up-stop, nose on the button", False, RED), ("FULL SQUEEZE: nose 0.15\" down", True, GREEN))):
        build(full=full)
        img, info = R.render(4, -90, W=1100, H=1100, margin=0.05)
        panel(fig, [0.05, 0.47 - r * 0.46, 0.90, 0.40], img, info, cap, [], only=(4, 6), min_px=80, capcol=col)
    fig.savefig(os.path.join(out, "v096-p3.png"), dpi=110); plt.close(fig)

    # page 4: exploded
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.05, 0.968, "EXPLODED VIEW: how it goes together (can hidden)", fontsize=11, weight="bold")
    fig.text(0.05, 0.953, "Each part pulled straight out along its bolt line. Collar down, lever up, pivot bolt down, washer and nut up; flange screws out the\n"
             "trigger side, washers and nuts out the flange side. Trigger, sleeves and their hardware come apart as in v0.95.", fontsize=7, va="top")
    build(explode=1.0, show_can=False)
    img, info = R.render(18, -40, W=1600, H=1600, margin=0.03)
    panel(fig, [0.02, 0.25, 0.96, 0.68], img, info, "", [], min_px=300)
    legend(fig, 0.235)
    fig.savefig(os.path.join(out, "v096-p4.png"), dpi=110); plt.close(fig)
    print("ok")
