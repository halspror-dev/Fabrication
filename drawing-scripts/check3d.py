# Real-shape clearance check: builds the same 3D model as render3d.py (plates, scales, the can, every bolt, nut, washer,
# pin and clip) and measures the gap between every pair of bodies by sampling their actual surfaces.
# Pairs that touch on purpose (a bolt in its hole, a scale on its plate, the tabs in their slots) are listed as "by design";
# every other pair must keep at least MIN_GAP.
# Usage: python3 check3d.py templates.py [page.pdf]  -> prints the table; with a pdf name it also draws the page.
import sys, math
import numpy as np
from scipy.spatial import cKDTree

sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "templates.py"] + sys.argv[2:]
import render3d as R

STEP = 0.012      # surface sample spacing, inches (gaps read about this much high at most)
NEAR = 0.25       # pairs further apart than this are not listed
MIN_GAP = 0.03    # smallest allowed gap between parts that are not meant to touch
PARTS = {1: "can", 2: "valve ring", 3: "button", 10: "collar", 11: "keeper", 12: "handle plate", 14: "trigger",
         16: "trigger scale (frame side)", 17: "trigger scale (outside)", 18: "grip scale (outside)", 19: "grip scale (inside)"}
TRIG_IDS = {14, 16, 17}
FIXED_TO_COLLAR = ("keeper lock", "keeper guide")   # hardware that stays with the collar when the can sits in the big hole
# hardware joint -> the parts it fastens (it touches them, and the other hardware in the same joint, by design)
JOINT_PARTS = {"pivot": {"trigger", "handle plate"}, "up-stop": {"handle plate", "trigger"}, "tab pin": {"handle plate", "collar"},
               "trigger scales": {"trigger", "trigger scale (frame side)", "trigger scale (outside)"},
               "grip scales": {"handle plate", "grip scale (outside)", "grip scale (inside)"},
               "keeper lock": {"keeper", "collar"}, "keeper guide": {"keeper", "collar"}}
TOUCH = [("can", "valve ring"), ("valve ring", "button"), ("valve ring", "collar"), ("valve ring", "keeper"), ("collar", "keeper"),
         ("handle plate", "collar"), ("handle plate", "grip scale (outside)"), ("handle plate", "grip scale (inside)"),
         ("trigger", "trigger scale (frame side)"), ("trigger", "trigger scale (outside)"), ("trigger", "button")]
WHY = {("trigger", "button"): "nose rests on the button", ("valve ring", "keeper"): "notch hugs the ring",
       ("handle plate", "collar"): "tabs in the collar slots", ("collar", "keeper"): "keeper lies on the collar"}


def sample(tris):
    """Points on the triangles about STEP apart: corners, edges and faces (vectorized)."""
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    pts = [a, b, c]
    for p, q in ((a, b), (b, c), (c, a)):
        n = np.maximum(1, np.ceil(np.linalg.norm(q - p, axis=1) / STEP).astype(int))
        k = np.repeat(np.arange(len(n)), n)
        t = (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)) / np.repeat(n, n)
        pts.append(p[k] + t[:, None] * (q - p)[k])
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    m = np.ceil(area / STEP ** 2).astype(int)
    k = np.repeat(np.arange(len(m)), m)
    rng = np.random.default_rng(1)
    u, v = rng.random(len(k)), rng.random(len(k))
    flip = u + v > 1
    u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
    pts.append(a[k] + u[:, None] * (b - a)[k] + v[:, None] * (c - a)[k])
    return np.concatenate(pts)


def bodies():
    """pid -> (name, joint, points)."""
    R.build()
    tri = np.array(R.TRIS, float); pid = np.array(R.PID)
    names, joints, count = dict(PARTS), {}, {}
    for p, num, joint, _ in R.INST:
        k = (num, joint); count[k] = count.get(k, 0) + 1
        names[p] = "#%d %s (%s)" % (num, R.HW[num][0].split(",")[0].split(" (")[0], joint) + (" %d" % count[k] if count[k] > 1 else "")
        joints[p] = joint
    return {p: (names.get(p, str(p)), joints.get(p), sample(tri[pid == p])) for p in sorted(set(pid.tolist()))}


def moved(pts, ang=0.0, piv=None, dy=0.0):
    q = pts.copy()
    if ang:
        cx, cz = piv
        x, z = q[:, 0] - cx, q[:, 2] - cz
        c, s = math.cos(ang), math.sin(ang)
        q[:, 0], q[:, 2] = cx + x * c - z * s, cz + x * s + z * c
    q[:, 1] += dy
    return q


def by_design(a, ja, b, jb):
    if ja and jb and ja == jb:
        return True
    if ja and b in JOINT_PARTS.get(ja, ()) or jb and a in JOINT_PARTS.get(jb, ()):
        return True
    return (a, b) in TOUCH or (b, a) in TOUCH


def gaps(B):
    items = list(B.values())
    lo = [pts.min(0) for _, _, pts in items]; hi = [pts.max(0) for _, _, pts in items]
    res = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if np.any(np.maximum(lo[i], lo[j]) - np.minimum(hi[i], hi[j]) > NEAR):
                continue
            (n, jn, p), (m, jm, q) = items[i], items[j]
            box_lo, box_hi = np.maximum(lo[i], lo[j]) - NEAR, np.minimum(hi[i], hi[j]) + NEAR
            p = p[np.all((p >= box_lo) & (p <= box_hi), axis=1)]
            q = q[np.all((q >= box_lo) & (q <= box_hi), axis=1)]
            if not len(p) or not len(q):
                continue
            small, big = (p, q) if len(p) < len(q) else (q, p)
            d, _ = cKDTree(big).query(small, distance_upper_bound=NEAR)
            dm = float(d.min())
            if dm < NEAR:
                res.append((dm, n, m, by_design(n, jn, m, jm)))
    return sorted(res)


STATES = (("SEAT", "REST", 0.0), ("SEAT", "FULL", 0.0), ("SEAT", "KEEPER OPEN", 0.0), ("BIG HOLE", "REST", 0.0), ("BIG HOLE", "FULL", 0.0))


def run():
    base = bodies()
    P = R.P
    full = -0.15 / 1.50       # radians: nose down 0.15" (button travel BT in templates.py) at 1.50" from the pivot
    out = {}
    for mode, st, _ in STATES:
        dy = -R.g["BIG"] if mode == "BIG HOLE" else 0.0
        B = {}
        for p, (n, j, pts) in base.items():
            if st == "FULL" and (p in TRIG_IDS or j in ("pivot", "trigger scales")):
                pts = moved(pts, ang=full, piv=P)
            if st == "KEEPER OPEN" and p == 11:
                pts = moved(pts, dy=-R.g["K_OPEN"])
            if p != 10 and j not in FIXED_TO_COLLAR:   # the can, handle and keeper sit 0.80 over in the big-hole position
                pts = moved(pts, dy=dy)
            B[p] = (n, j, pts)
        out[(mode, st)] = gaps(B)
    return out


def page(res, pdf_name):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.06, 0.965, "REAL-SHAPE 3D CLEARANCE CHECK: every part against every other part (not a template)", fontsize=11, weight="bold")
    fig.text(0.06, 0.95,
             "The 3D model on the next pages (plates, HDPE scales, the can, every bolt, nut, washer, pin and clip at catalog size) is sampled about\n"
             "every %.3f\" over its real surfaces, and the gap between each pair of parts is measured in 5 states. Parts meant to touch (a bolt in its\n"
             "hole, a scale on its plate, the tabs in their slots, the nose on the button) are counted as BY DESIGN. Every other pair must keep %.2f\"\n"
             "or more. Listed: the closest pairs that are NOT meant to touch, in each state. Hardware sizes are nominal catalog sizes; the can is\n"
             "the 65 mm Rust-Oleum can from the drawings. Gaps can read up to about %.2f\" high from the sampling." % (STEP, MIN_GAP, STEP),
             fontsize=7, va="top")
    y = 0.865
    allok = True
    for (mode, st), rows in res.items():
        free = [r for r in rows if not r[3]]
        nd = sum(1 for r in rows if r[3])
        ok = all(d >= MIN_GAP for d, *_ in free)
        allok &= ok
        fig.text(0.06, y, "%s, %s   (%d pairs touch by design)   %s" % (
            "CAN IN THE " + mode, {"REST": "trigger at rest", "FULL": "trigger at full squeeze",
                                   "KEEPER OPEN": "keeper slid open (pin parked)"}[st], nd, "PASS" if ok else "FAIL"),
                 fontsize=7.5, weight="bold", color="#000000" if ok else "#c0392b")
        y -= 0.013
        for d, a, b, _ in free[:9]:
            fig.text(0.08, y, "%-40s %-40s" % (a[:40], b[:40]), fontsize=5.8, family="monospace")
            fig.text(0.86, y, "%.3f\"" % d, fontsize=5.8, family="monospace", ha="right")
            fig.text(0.885, y, "PASS" if d >= MIN_GAP else "FAIL", fontsize=5.8, family="monospace", weight="bold",
                     color="#2e7d32" if d >= MIN_GAP else "#c0392b")
            y -= 0.0115
        y -= 0.01
    fig.text(0.06, y - 0.005, "RESULT: %s. Closest by-design contacts are not listed (they are supposed to be 0)." % (
        "every pair not meant to touch keeps %.2f\" or more in every state" % MIN_GAP if allok else "SEE FAIL LINES"), fontsize=7.5, weight="bold")
    fig.savefig(pdf_name)
    fig.savefig(pdf_name.replace(".pdf", ".png"), dpi=80)


if __name__ == "__main__":
    res = run()
    for k, v in res.items():
        print("==", k)
        for d, a, b, des in v:
            if not des or d < 0.02:
                print("%.3f  %-45s | %-45s %s" % (d, a, b, "by design" if des else ""))
    if len(sys.argv) > 2:
        page(res, sys.argv[2])
