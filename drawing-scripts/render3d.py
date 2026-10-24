import sys, math
import numpy as np
import shapely
from shapely.geometry import box
from shapely import affinity

src = open(sys.argv[1]).read().split("\ndef draw(")[0]
src = src.replace("OUT = sys.argv[1]", "").replace("PNG = sys.argv[2]", "")
g = {}; exec(src, g)
collar, keeper, frame, trigger = g["collar"], g["keeper"], g["frame"], g["trigger"]
P, S = g["P"], g["S"]
trig = affinity.translate(trigger, *P)
TS = g["collar_holes"][0][1]   # thumbscrew y
T = 0.125

# ---------- mesh building: list of (tri[3x3], part_id, color) ----------
TRIS, PID, COL = [], [], []
def add_tri(a, b, c, pid, col):
    TRIS.append((a, b, c)); PID.append(pid); COL.append(col)

def extrude(poly, plane, t0, t1, pid, col, off=(0, 0, 0)):
    if poly.geom_type == "MultiPolygon":
        for pp in poly.geoms: extrude(pp, plane, t0, t1, pid, col, off)
        return
    poly = poly.simplify(0.004)
    def to3(u, v, t):
        p = (u, v, t) if plane == "xy" else (u, t, v)
        return (p[0] + off[0], p[1] + off[1], p[2] + off[2])
    for tr in shapely.constrained_delaunay_triangles(poly).geoms:
        c = list(tr.exterior.coords)[:3]
        add_tri(*[to3(u, v, t0) for u, v in c], pid, col)
        add_tri(*[to3(u, v, t1) for u, v in c], pid, col)
    for ring in [poly.exterior] + list(poly.interiors):
        cs = list(ring.coords)
        for (u1, v1), (u2, v2) in zip(cs, cs[1:]):
            a, b, c, d = to3(u1, v1, t0), to3(u2, v2, t0), to3(u2, v2, t1), to3(u1, v1, t1)
            add_tri(a, b, c, pid, col); add_tri(a, c, d, pid, col)

def revolve(profile, pid, col, n=72, axis="z", center=(0, 0, 0)):
    th = np.linspace(0, 2 * np.pi, n + 1)
    def pt(r, h, a):
        cx, cy, cz = center
        if axis == "z": return (cx + r * math.cos(a), cy + r * math.sin(a), cz + h)
        return (cx + r * math.cos(a), cy + h, cz + r * math.sin(a))  # axis y
    for (r1, h1), (r2, h2) in zip(profile, profile[1:]):
        for a, b in zip(th, th[1:]):
            p1, p2, p3, p4 = pt(r1, h1, a), pt(r1, h1, b), pt(r2, h2, b), pt(r2, h2, a)
            add_tri(p1, p2, p3, pid, col); add_tri(p1, p3, p4, pid, col)

def bolt_z(x, y, z0, z1, pid):
    revolve([(0, z0), (0.095, z0), (0.095, z1), (0.18, z1), (0.18, z1 + 0.09), (0, z1 + 0.09)], pid, (0.22, 0.22, 0.22), n=24, center=(x, y, 0))

def bolt_y(x, z, y0, y1, pid, r=0.095, head=0.18):
    revolve([(0, y0), (r, y0), (r, y1), (head, y1), (head, y1 + 0.09), (0, y1 + 0.09)], pid, (0.22, 0.22, 0.22), n=24, axis="y", center=(x, 0, z))

COLORS = dict(collar=(0.55, 0.74, 0.92), keeper=(0.62, 0.84, 0.58), frame=(0.93, 0.78, 0.55),
              clip=(0.70, 0.70, 0.72), trigger=(0.45, 0.45, 0.48), can=(0.86, 0.86, 0.86), ring=(0.75, 0.75, 0.75), button=(0.98, 0.98, 0.98))

def build(explode=0.0, show_can=True, show_trigger=True):
    TRIS.clear(); PID.clear(); COL.clear()
    e = explode
    if show_can:
        revolve([(0, -3.6), (1.28, -3.6), (1.28, -0.95), (1.15, -0.85), (1.0, -0.65), (0.75, -0.35), (0.6, -0.15), (0.53, -0.13), (0, -0.13)], 1, COLORS["can"])
        revolve([(0, 0), (0.64, 0), (0.64, 0.14), (0, 0.14)], 2, COLORS["ring"])
        revolve([(0, 0.14), (0.33, 0.14), (0.33, 0.765), (0, 0.765)], 3, COLORS["button"], n=48)
    extrude(collar, "xy", -T, 0, 10, COLORS["collar"])
    extrude(keeper, "xy", 0, T, 11, COLORS["keeper"])
    extrude(frame, "xz", 0.095, 0.22, 12, COLORS["frame"])
    dy, dz = 2.2 * e, 2.2 * e
    D7 = g["D7"]; H = g["hole"]
    flat = box(-1.80, 0.22, -0.70, 0.97).difference(H(-0.95, 0.60, D7)).difference(H(-1.45, 0.60, D7))
    upr = box(-1.80, 0.0, -0.70, 0.75).difference(H(-1.05, 0.30, D7)).difference(H(-1.50, 0.30, D7))
    flat = flat.difference(box(-1.81, 0.21, -0.69, 0.345))  # corner belongs to the upright leg
    extrude(flat, "xy", 0, T, 13, COLORS["clip"], off=(0, dy, dz))
    extrude(upr, "xz", 0.22, 0.345, 13, COLORS["clip"], off=(0, dy, dz))
    if show_trigger:
        extrude(trig, "xz", -0.0625, 0.0625, 14, COLORS["trigger"])
        # pivot shoulder bolt: head outboard, shoulder through trigger to the frame
        revolve([(0, -0.16), (0.22, -0.16), (0.22, -0.07), (0.125, -0.07), (0.125, 0.30), (0, 0.30)], 20, (0.22, 0.22, 0.22), n=24, axis="y", center=(P[0], 0, P[1]))
    # up-stop shoulder bolt: head outboard, 1/4" shoulder under the trigger tail, nut on the far side of the frame
    revolve([(0, -0.25), (0.19, -0.25), (0.19, -0.155), (0.125, -0.155), (0.125, 0.095), (0.095, 0.095), (0.095, 0.36), (0, 0.36)],
            25, (0.75, 0.22, 0.18), n=24, axis="y", center=(S[0], 0, S[1]))
    revolve([(0, 0.22), (0.19, 0.22), (0.19, 0.36), (0, 0.36)], 26, (0.22, 0.22, 0.22), n=6, axis="y", center=(S[0], 0, S[1]))
    # keeper thumbscrew: knurled head, washer, shank, nut under collar
    revolve([(0, -0.36), (0.095, -0.36), (0.095, 0.125), (0.22, 0.125), (0.22, 0.17), (0.30, 0.17), (0.30, 0.42), (0, 0.42)],
            30, (0.30, 0.30, 0.30), n=32, center=(0, TS, 0))
    revolve([(0, -0.30), (0.19, -0.30), (0.19, -0.125), (0, -0.125)], 31, (0.22, 0.22, 0.22), n=6, center=(0, TS, 0))
    pid = 21
    for x in (-0.95, -1.45):
        z0 = -0.30 + 6.5 * e
        bolt_z(x, 0.60 + dy, z0, z0 + 0.6 - 0.09 + T * 0 + 0.0 if False else z0 + 0.42, pid); pid += 1
    for x in (-1.05, -1.50):
        y0 = 0.0 + 4.6 * e
        bolt_y(x, 0.30 + dz, y0, y0 + 0.36, pid); pid += 1

# ---------- rasterizer ----------
def render(elev, azim, W=1400, H=1400, fit_ids=None, margin=0.06):
    tr = np.array(TRIS, float)          # (n,3,3)
    pid = np.array(PID); col = np.array(COL, float)
    el, az = math.radians(elev), math.radians(azim)
    view = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])  # toward camera
    right = np.cross([0, 0, 1], view); right /= np.linalg.norm(right)
    up = np.cross(view, right)
    pts = tr.reshape(-1, 3)
    u = pts @ right; v = pts @ up; d = pts @ view
    sel = np.isin(np.repeat(pid, 3), fit_ids) if fit_ids is not None else np.ones(len(u), bool)
    umin, umax, vmin, vmax = u[sel].min(), u[sel].max(), v[sel].min(), v[sel].max()
    s = min(W, H) * (1 - 2 * margin) / max(umax - umin, vmax - vmin)
    cu, cv = (umin + umax) / 2, (vmin + vmax) / 2
    X = (u - cu) * s + W / 2; Y = H / 2 - (v - cv) * s
    X = X.reshape(-1, 3); Y = Y.reshape(-1, 3); D = d.reshape(-1, 3)
    # normals + shading
    nrm = np.cross(tr[:, 1] - tr[:, 0], tr[:, 2] - tr[:, 0])
    ln = np.linalg.norm(nrm, axis=1); ok = ln > 1e-12
    nrm[ok] /= ln[ok][:, None]
    nrm[(nrm @ view) < 0] *= -1
    light = view + 0.45 * up + 0.2 * right; light /= np.linalg.norm(light)
    shade = 0.62 + 0.38 * np.clip(nrm @ light, 0, 1)
    zbuf = np.full((H, W), -np.inf); img = np.ones((H, W, 3)); idb = np.full((H, W), -1)
    nbuf = np.zeros((H, W, 3))
    for i in np.where(ok)[0]:
        x0, x1 = int(max(0, math.floor(X[i].min()))), int(min(W - 1, math.ceil(X[i].max())))
        y0, y1 = int(max(0, math.floor(Y[i].min()))), int(min(H - 1, math.ceil(Y[i].max())))
        if x1 < x0 or y1 < y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax_, bx, cx), (ay, by, cy) = X[i], Y[i]
        den = (by - cy) * (ax_ - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12: continue
        w1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w2 = ((cy - ay) * (xs - cx) + (ax_ - cx) * (ys - cy)) / den
        w3 = 1 - w1 - w2
        inside = (w1 >= -1e-6) & (w2 >= -1e-6) & (w3 >= -1e-6)
        if not inside.any(): continue
        z = w1 * D[i, 0] + w2 * D[i, 1] + w3 * D[i, 2]
        zb = zbuf[y0:y1 + 1, x0:x1 + 1]
        m = inside & (z > zb)
        zb[m] = z[m]
        img[y0:y1 + 1, x0:x1 + 1][m] = col[i] * shade[i]
        idb[y0:y1 + 1, x0:x1 + 1][m] = pid[i]
        nbuf[y0:y1 + 1, x0:x1 + 1][m] = nrm[i]
    # outlines: part change, crease, or depth jump
    edge = np.zeros((H, W), bool)
    for dy_, dx_ in ((0, 1), (1, 0)):
        a = slice(0, H - dy_), slice(0, W - dx_)
        b = slice(dy_, H), slice(dx_, W)
        e1 = idb[a] != idb[b]
        e2 = (np.sum(nbuf[a] * nbuf[b], axis=2) < 0.9) & (idb[a] >= 0) & (idb[b] >= 0)
        za, zb_ = zbuf[a], zbuf[b]
        with np.errstate(invalid='ignore'):
            e3 = (idb[a] == idb[b]) & (idb[a] >= 0) & (np.abs(za - zb_) > 0.35)
        ee = e1 | e2 | e3
        edge[a] |= ee
    # thicken slightly
    th = edge.copy(); th[1:] |= edge[:-1]; th[:, 1:] |= edge[:, :-1]
    img[th] = img[th] * 0.25
    return img, (s, cu, cv, right, up, W, H)

def project(p, info):
    s, cu, cv, right, up, W, H = info
    p = np.array(p)
    return ((p @ right - cu) * s + W / 2, H / 2 - (p @ up - cv) * s)

if __name__ == "__main__":
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    out = sys.argv[2]
    def panel(fig, rect, img, info, cap, labels):
        ax = fig.add_axes(rect); ax.imshow(img, interpolation="lanczos"); ax.axis("off")
        ax.set_title(cap, fontsize=8, weight="bold", loc="left")
        for p3, txt, (dx, dy) in labels:
            x, y = project(p3, info)
            ax.annotate(txt, (x, y), (x + dx, y + dy), fontsize=6.5,
                        arrowprops=dict(arrowstyle="-", lw=0.5), bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5))
    with PdfPages(out) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.06, 0.965, "3D VIEWS: assembled on a can", fontsize=11, weight="bold")
        fig.text(0.06, 0.95, "Blue = collar, green = keeper, tan = handle plate, light gray = angle clip, dark gray = trigger, black = bolts, red = up-stop bolt.\n"
                 "Nozzle sprays toward the +x direction (away from the handle).", fontsize=7, va="top")
        build()
        img, info = render(12, -75)
        panel(fig, [0.03, 0.465, 0.94, 0.43], img, info, "From the front-right (trigger side)", [
            ((0.95, -0.4, -0.06), "COLLAR (under the valve ring)", (150, 170)),
            ((0.6, -1.9, 0.125), "KEEPER", (260, 60)),
            ((0.0, TS, 0.42), "thumbscrew", (300, -90)),
            ((0.0, 0.0, 0.765), "button", (260, -150)),
            ((P[0], -0.2, P[1]), "pivot bolt", (-260, -160)),
            ((S[0], -0.25, S[1]), "up-stop bolt", (-330, -60)),
            ((-1.0, -0.06, 1.2), "TRIGGER", (-200, -200)),
            ((-2.3, -0.06, -2.4), "TRIGGER bar, 4 finger divots", (-420, 30)),
            ((-4.7, 0.1, -3.4), "HANDLE plate", (-220, 40))])
        img, info = render(22, 125)
        panel(fig, [0.03, 0.02, 0.94, 0.43], img, info, "From the back-left (angle clip side)", [
            ((-1.25, 0.97, 0.06), "ANGLE CLIP", (-330, 120)),
            ((0.8, 0.6, 0.0), "COLLAR", (-260, -140)),
            ((P[0], 0.3, P[1]), "pivot bolt end (in the slot)", (220, -120)),
            ((S[0], 0.36, S[1]), "up-stop nut (in its slot)", (260, 40)),
            ((-4.1, 0.22, -2.6), "HANDLE plate", (250, 60))])
        pdf.savefig(fig); fig.savefig(out.replace(".pdf", "-p1.png"), dpi=110)

        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.06, 0.965, "ANGLE CLIP CLOSE-UP (can and trigger hidden)", fontsize=11, weight="bold")
        fig.text(0.06, 0.95, "The clip is a 1-1/10\" piece of 3/4\" x 3/4\" aluminum ANGLE (an L-shaped bar from the hardware store).\n"
                 "Its FLAT leg lies on top of the collar: 2 bolts go DOWN through it and the collar.\n"
                 "Its UPRIGHT leg stands against the handle plate: 2 bolts go SIDEWAYS through it and the handle.\n"
                 "That's its whole job: hold the upright handle square to the flat collar.", fontsize=7, va="top")
        ids = [10, 12, 13, 21, 22, 23, 24]
        build(show_can=False, show_trigger=False)
        img, info = render(30, 115, fit_ids=None)
        # crop to the clip area by fitting on a box around it
        TR = list(TRIS)
        build(show_can=False, show_trigger=False)
        img, info = render(28, 115, fit_ids=[13, 21, 22, 23, 24, 10], margin=0.02)
        panel(fig, [0.03, 0.47, 0.94, 0.41], img, info, "Assembled", [
            ((-1.0, 0.85, 0.125), "FLAT leg: lies on the collar", (-450, 230)),
            ((-1.25, 0.345, 0.65), "UPRIGHT leg: against the handle", (-520, -260)),
            ((0.4, 0.4, -0.06), "COLLAR", (-150, 260)),
            ((-2.1, 0.22, 1.9), "HANDLE plate", (250, -150))])
        build(explode=0.4, show_can=False, show_trigger=False)
        img, info = render(28, 115, fit_ids=[13, 21, 22, 23, 24, 10], margin=0.02)
        panel(fig, [0.03, 0.02, 0.94, 0.41], img, info, "Pulled apart along the bolt lines", [
            ((-1.6, 0.345 + 0.88, 0.62 + 0.88), "ANGLE CLIP (L-shaped)", (-420, -160)),
            ((-1.2, 0.60, 0.0), "2 bolts go down into these collar holes", (-560, 220)),
            ((-1.28, 0.22, 0.30), "2 bolts go sideways into these handle holes", (150, -330))])
        pdf.savefig(fig); fig.savefig(out.replace(".pdf", "-p2.png"), dpi=110)
    print("ok")
