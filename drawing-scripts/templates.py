import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import Polygon, Point, LineString, box
from shapely import affinity

OUT = sys.argv[1]
PNG = sys.argv[2]
D7 = 0.201  # #7 drill, 10-24 clearance
DF = 0.257  # F drill, 1/4" shoulder


def hole(x, y, d):
    return Point(x, y).buffer(d / 2, 64)


def slot(x1, y1, x2, y2, w):
    return LineString([(x1, y1), (x2, y2)]).buffer(w / 2, 64)


def rounded_rect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, 32)


# ---- Collar (top view: x forward, y left) ----
collar = rounded_rect(-1.70, -1.00, 1.00, 2.80, 0.25)
# v0.3: trim the back strip beside the keeper (back edge x=-0.95 on the keyhole side), R0.25 inside + outside
collar = collar.difference(box(-1.80, 0.10, -0.95, 2.90))
collar = collar.buffer(0.25, join_style=1).buffer(-0.25, join_style=1)  # inside corner
collar = collar.buffer(-0.25, join_style=1).buffer(0.25, join_style=1)  # outside corners
keyhole = hole(0, 0, 1.125).union(box(-0.5625, 0, 0.5625, 0.80)).union(hole(0, 0.80, 1.375))
collar = collar.difference(keyhole)
collar_holes = [(0, 2.45, D7), (-0.95, -0.60, D7), (-1.45, -0.60, D7)]
for x, y, d in collar_holes:
    collar = collar.difference(hole(x, y, d))

# ---- Keeper (notched edge at y=0) ----
keeper = rounded_rect(-0.875, 0, 0.875, 2.75, 0.19)
keeper = keeper.difference(hole(0, 0, 1.30)).difference(slot(0, 0.95, 0, 2.45, D7))

collar = affinity.scale(collar, 1, -1, origin=(0, 0))
keeper = affinity.scale(keeper, 1, -1, origin=(0, 0))
collar_holes = [(x, -y, d) for x, y, d in collar_holes]

# ---- Frame (side view: x forward, z up) ----
import math
pts = [(-0.80, 0), (-0.80, 2.25), (-2.80, 2.25), (-2.80, 1.60), (-4.34, 0), (-5.56, -4.53), (-4.52, -4.53), (-3.51, -0.79), (-1.70, -0.125), (-1.70, 0)]
frame = Polygon(pts)
frame = frame.buffer(-0.2, join_style=1).buffer(0.2, join_style=1)  # R0.2 on outside corners
frame = frame.difference(slot(-2.25, 1.05, -2.25, 1.55, D7))
for x, y in [(-1.05, 0.30), (-1.50, 0.30), (-4.30, -1.80), (-4.87, -3.90)]:
    frame = frame.difference(hole(x, y, D7))

# ---- Trigger (pivot at origin, drawn as it sits on the can) ----
Q = (-1.077, -3.503)
nose = box(0, -0.25, 2.25, 0.25).union(hole(2.25, 0, 0.5))
bump = hole(2.25, -0.25, 0.40)
boss = hole(0, 0, 0.90)
arm = LineString([(0, 0), Q]).buffer(0.25, 32)
# finger flange tab on front edge of finger arm, local z -1.975..-2.975
ux, uz = Q[0] / math.hypot(*Q), Q[1] / math.hypot(*Q)
nx, nz = -uz, ux  # perpendicular
if nx < 0:
    nx, nz = -nx, -nz  # forward-pointing normal

def on_front(z):
    t = z / Q[1]
    return (Q[0] * t + nx * 0.25, z + nz * 0.25)

a, b = on_front(-2.45), on_front(-3.45)
tab = Polygon([a, b, (b[0] + nx * 0.5, b[1] + nz * 0.5), (a[0] + nx * 0.5, a[1] + nz * 0.5)])
trigger = nose.union(bump).union(boss).union(arm).union(tab).difference(hole(0, 0, DF))
bend = (a, b)


# ---- Angle clip, unfolded (u = along length from front end, v = from the corner) ----
clip_flat = box(0, -0.75, 1.10, 0.75)
for u, v in [(0.25, -0.38), (0.75, -0.38), (0.35, 0.30), (0.80, 0.30)]:
    clip_flat = clip_flat.difference(hole(u, v, D7))


def clip_marks(ax, ox, oy):
    ax.plot([ox, ox + 1.10], [oy, oy], "k--", lw=0.6)
    ax.text(ox + 1.18, oy + 0.3, "UPRIGHT leg:\nbolts sideways\ninto handle", fontsize=5)
    ax.text(ox + 1.18, oy - 0.55, "FLAT leg:\nbolts down\ninto collar", fontsize=5)


def draw(ax, geom, title, notes, holes_lbl=(), extra=None):
    geoms = getattr(geom, "geoms", [geom])
    for g in geoms:
        x, y = g.exterior.xy
        ax.plot(x, y, "k-", lw=0.8)
        for i in g.interiors:
            x, y = i.xy
            ax.plot(x, y, "k-", lw=0.8)
    for (x, y, t) in holes_lbl:
        ax.plot([x - 0.08, x + 0.08], [y, y], "k-", lw=0.3)
        ax.plot([x, x], [y - 0.08, y + 0.08], "k-", lw=0.3)
        if t:
            ax.text(x + 0.12, y + 0.06, t, fontsize=5)
    if extra:
        extra(ax)
    minx, miny, maxx, maxy = geom.bounds
    ax.text(minx, maxy + 0.45, title, fontsize=9, weight="bold")
    ax.text(minx, maxy + 0.08, notes, fontsize=5.5, va="bottom")


def page(pdf, items, scale_box=True):
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 11)
    ax.set_aspect("equal")
    ax.axis("off")
    for geom, ox, oy, title, notes, lbls, extra in items:
        g = affinity.translate(geom, ox, oy)
        lb = [(x + ox, y + oy, t) for x, y, t in lbls]
        ex = (lambda f, ox=ox, oy=oy: (lambda ax: f(ax, ox, oy)))(extra) if extra else None
        draw(ax, g, title, notes, lb, ex)
    if scale_box:
        ax.add_patch(plt.Rectangle((0.6, 0.5), 1, 1, fill=False, lw=0.8))
        ax.text(2.0, 0.55, "Spray can trigger handle v0.3, 1:1 templates. All 0.125\" (1/8\") 5052 aluminum.\n"
                "Holes marked #7 = 0.201\" (10-24 clearance). F = 0.257\" (1/4\" shoulder bolt). Inches.\n"
                "Datum: + = can axis. Dims from carlie's build notes (future-builds-spray-can-trigger.md).", fontsize=6)
    pdf.savefig(fig)
    return fig


def bend_line(ax, ox, oy):
    (x1, y1), (x2, y2) = bend
    ax.plot([x1 + ox, x2 + ox], [y1 + oy, y2 + oy], "k--", lw=0.6)


def can_axis(ax, ox, oy):
    ax.plot([ox - 0.15, ox + 0.15], [oy, oy], "r-", lw=0.4)
    ax.plot([ox, ox], [oy - 0.15, oy + 0.15], "r-", lw=0.4)


def pivot_mark(ax, ox, oy):
    ax.text(ox + 0.3, oy + 0.3, "pivot (F hole)", fontsize=5)
    ax.text(ox + 1.3, oy - 0.62, "nose bump\npresses button", fontsize=5)


def frame_marks(ax, ox, oy):
    ax.plot([ox - 1.70, ox - 0.80], [oy, oy], "r:", lw=0.5)
    ax.text(ox - 0.65, oy - 0.05, "<- collar sits here", fontsize=5, color="r")
    ax.text(ox - 0.65, oy + 1.25, "<- pivot slot, #7 wide", fontsize=5)


with PdfPages(OUT) as pdf:
    f1 = page(pdf, [
        (collar, 2.3, 8.6, "COLLAR (top view, qty 1)",
         "Forward (spray) is right; top of page = can's left. Seat 1.125, big hole 1.375. Cut slot 0.02\" small, file to fit.\n3 holes #7: thumbscrew (bottom), 2 clip holes (upper left). + = can center.",
         [(0, -2.45, ""), (-0.95, 0.60, ""), (-1.45, 0.60, "")], can_axis),
        (keeper, 2.0, 4.9, "KEEPER (qty 1)",
         "Notch 1.30 dia. Slot #7 wide.", [], None),
        (trigger, 5.6, 9.0, "TRIGGER (side view, qty 1)",
         "Nose (right) presses button. Pivot hole F (0.257). Dashed line = bend the\nfinger tab 90 deg TOWARD YOU (printed side up). Tab = finger pad.", [], lambda ax, ox, oy: bend_line(ax, ox, oy)),
    ])
    f1.savefig(PNG.replace(".png", "-p1.png"), dpi=80)
    f2 = page(pdf, [
        (frame, 6.8, 6.3, "FRAME / HANDLE (side view, qty 1)",
         "Forward is right. Clip holes #7 at z +0.30; grip-scale holes #7.", [], frame_marks),
        (clip_flat, 5.7, 2.6, "ANGLE CLIP (qty 1)",
         "Cut 1-1/10\" off 3/4\" x 3/4\" x 1/8\" aluminum ANGLE.\nWrap this template around it: dashed line = the corner.\n4 holes #7. Left = front (toward the can).", [], clip_marks),
    ])
    f2.savefig(PNG.replace(".png", "-p2.png"), dpi=80)

    # ---------- Assembly pages (side + top view, 1:1) ----------
    P = (-2.25, 1.215)
    trig_on = affinity.translate(trigger, P[0], P[1])

    def fill(ax, g, ox, oy, fc, ec="k", lw=0.7, alpha=1.0, ls="-", z=1):
        g = affinity.translate(g, ox, oy)
        for gg in getattr(g, "geoms", [g]):
            x, y = gg.exterior.xy
            ax.fill(x, y, fc=fc, ec=ec, lw=lw, alpha=alpha, ls=ls, zorder=z)
            for i in gg.interiors:
                x, y = i.xy
                ax.fill(x, y, fc="white", ec=ec, lw=lw, zorder=z)

    def lab(ax, x, y, tx, ty, t):
        ax.annotate(t, (x, y), (tx, ty), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.4), zorder=10)

    def newpage(title, sub):
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 8.5); ax.set_ylim(0, 11)
        ax.set_aspect("equal"); ax.axis("off")
        ax.text(0.5, 10.5, title, fontsize=11, weight="bold")
        ax.text(0.5, 10.2, sub, fontsize=7, va="top")
        return fig, ax

    # Side view
    fig, ax = newpage("ASSEMBLY: SIDE VIEW (1:1, looking at the right side of the can)",
        "Nozzle sprays to the RIGHT. Your hand holds the grip on the left. The trigger is closest to you, the handle plate behind it,\n"
        "the angle clip on the far side. Gray = the can, which is not a part.")
    ox, oy = 6.4, 6.3
    bead = 0.14
    can = Polygon([(-0.64, bead), (0.64, bead), (0.62, -0.05), (0.75, -0.35), (1.0, -0.65), (1.15, -0.85), (1.28, -0.95), (1.28, -4.4),
                   (-1.28, -4.4), (-1.28, -0.95), (-1.15, -0.85), (-1.0, -0.65), (-0.75, -0.35), (-0.62, -0.05)])
    fill(ax, can, ox, oy, "#dddddd", ec="#999999", z=0)
    button = box(-0.33, bead, 0.33, 0.765)
    fill(ax, button, ox, oy, "white", ec="#777777", z=1)
    ax.plot([ox + 0.33, ox + 0.9], [oy + 0.55, oy + 0.55], ":", color="#777777", lw=0.6)
    ax.text(ox + 0.5, oy + 0.6, "spray", fontsize=6, color="#777777")
    fill(ax, frame, ox, oy, "#f3d9b1", z=2)
    fill(ax, box(-1.70, -0.125, 1.00, 0), ox, oy, "#9ec5ea", z=3)
    fill(ax, box(-0.875, 0, 0.875, 0.125), ox, oy, "#c9e6c3", z=3)
    fill(ax, box(-1.80, 0, -0.70, 0.75), ox, oy, "none", ec="#555555", ls="--", z=4)
    fill(ax, trig_on, ox, oy, "#bfbfbf", z=5)
    ax.add_patch(plt.Circle((ox + P[0], oy + P[1]), 0.19, fc="#555555", ec="k", lw=0.5, zorder=6))
    lab(ax, ox + 0.0, oy - 0.06, ox - 0.3, oy - 1.3, "COLLAR (edge-on)\nunder the valve ring")
    lab(ax, ox + 0.5, oy + 0.07, ox + 0.2, oy + 1.25, "KEEPER (edge-on)\non top of collar")
    lab(ax, ox - 0.2, oy + 0.75, ox + 0.5, oy + 0.85, "BUTTON")
    lab(ax, ox + P[0], oy + P[1] + 0.19, ox - 1.2, oy + 2.8, "shoulder bolt = TRIGGER PIVOT (in the slot)")
    lab(ax, ox + 0.0, oy + 1.0, ox + 0.4, oy + 2.2, "trigger NOSE rests on top of button")
    lab(ax, ox - 1.0, oy + 0.6, ox - 0.4, oy + 1.9, "angle CLIP (far side, dashed)")
    lab(ax, ox - 4.8, oy - 2.6, ox - 6.0, oy - 1.4, "HANDLE / FRAME plate\n(grip, add wood scales)")
    lab(ax, ox - 3.1, oy - 2.1, ox - 2.6, oy - 3.7, "TRIGGER finger arm:\npull back toward grip\n= nose pushes button down")
    ax.text(0.5, 0.9, "Can drawn as a 65 mm (2-9/16\") Rust-Oleum can. Button 5/8\" above the valve ring.", fontsize=6.5)
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p3.png"), dpi=80)

    # Top view
    fig, ax = newpage("ASSEMBLY: TOP VIEW (1:1, looking down on the can)",
        "Nozzle sprays to the RIGHT. Top of page = can's LEFT side (handle side). Keeper is on the can's right. Plates on edge (handle, trigger) look like thin strips from above.")
    ox, oy = 6.4, 5.8
    ax.add_patch(plt.Circle((ox, oy), 1.28, fc="#eeeeee", ec="#999999", lw=0.6, zorder=0))
    fill(ax, collar, ox, oy, "#9ec5ea", z=1)
    fill(ax, keeper, ox, oy, "#c9e6c3", alpha=0.85, z=2)
    ax.add_patch(plt.Circle((ox, oy), 0.64, fc="none", ec="#555555", lw=0.6, ls="--", zorder=3))
    ax.add_patch(plt.Circle((ox, oy), 0.33, fc="white", ec="#777777", lw=0.6, zorder=3))
    fill(ax, box(-1.80, 0.22, -0.70, 0.97), ox, oy, "#e8e8e8", ec="#555555", z=3)
    fill(ax, box(-5.56, 0.095, -0.80, 0.22), ox, oy, "#f3d9b1", z=4)
    tb = trig_on.bounds
    fill(ax, box(tb[0], -0.0625, tb[2], 0.0625), ox, oy, "#bfbfbf", z=5)
    fill(ax, box(-2.35, -0.20, -2.15, 0.10), ox, oy, "#555555", z=6)
    lab(ax, ox + 0.45, oy + 0.45, ox - 0.3, oy + 2.4, "valve ring sits in the keyhole SEAT\n(center of the can)")
    lab(ax, ox + 0.6, oy - 1.8, ox - 4.2, oy - 2.9, "KEEPER: slide toward the can, tighten thumbscrew.\nSlide away (down the page) to take it off.")
    lab(ax, ox, oy - 2.45, ox - 1.8, oy - 2.6, "thumbscrew")
    lab(ax, ox - 1.2, oy + 0.8, ox - 2.6, oy + 1.9, "angle CLIP: bolts down into collar\nand sideways into handle plate")
    lab(ax, ox - 3.2, oy + 0.16, ox - 4.9, oy + 1.0, "HANDLE plate (on edge)")
    lab(ax, ox - 2.6, oy - 0.03, ox - 5.4, oy - 1.0, "TRIGGER (on edge, on the can's centerline)")
    lab(ax, ox - 2.25, oy - 0.2, ox - 3.9, oy - 1.9, "shoulder bolt through trigger\n+ handle; nylon washer between")
    steps = ("ASSEMBLY ORDER\n"
             "1. Collar on can: pull keeper back, drop collar over the valve ring at the big hole, slide it so the ring sits in the seat.\n"
             "2. Keeper: slide it toward the can until the notch hugs the ring, tighten the thumbscrew.\n"
             "3. Handle plate stands on edge, its notch over the back edge of the collar, just left of the centerline.\n"
             "4. Angle clip on the left side of the handle plate: 2 bolts down through clip + collar, 2 bolts sideways through clip + handle.\n"
             "5. Trigger on the right side of the handle (on the centerline): shoulder bolt through trigger, nylon washer, handle slot, nut.\n"
             "6. Turn the button so the nozzle points forward. Slide the pivot in its slot until the nose just touches the button, tighten the nut.\n"
             "For a first rough fit, any bolt works as the pivot and C-clamps can stand in for the angle clip.")
    ax.text(0.5, 1.0, steps, fontsize=6.5, va="bottom")
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p4.png"), dpi=80)

    # ---------- Keeper detail (section through the can center, looking from the front) ----------
    K = 1.15  # drawing scale
    fig, ax = newpage("KEEPER DETAIL: cut through the middle of the can, looking at the nozzle (not a template)",
        "The collar is a flat plate UNDER the valve ring. On the keyhole side there's a gap under the ring (that's how the ring got in).\n"
        "The keeper is a small flat plate lying ON TOP of the collar. It slides sideways along its slot until its curved notch pushes\n"
        "against the side of the ring, closing the gap. One thumbscrew goes down through the keeper's slot into a nut under the collar.")

    def r(ax, y0, z0, y1, z1, ox, oy, fc, ec="k", lw=0.7, ls="-", zo=2):
        ax.add_patch(plt.Rectangle((ox + K * y0, oy + K * z0), K * (y1 - y0), K * (z1 - z0), fc=fc, ec=ec, lw=lw, ls=ls, zorder=zo))

    def panel(ox, oy, shift, title):
        # can dome + ring + button (gray)
        dome = [(-0.53, 0), (-0.60, -0.12), (-0.80, -0.30), (-1.05, -0.55), (-1.25, -0.80), (-1.28, -1.1),
                (1.28, -1.1), (1.25, -0.80), (1.05, -0.55), (0.80, -0.30), (0.60, -0.12), (0.53, 0)]
        ax.fill([ox + K * y for y, z in dome], [oy + K * z for y, z in dome], fc="#e4e4e4", ec="#999999", lw=0.6, zorder=0)
        r(ax, -0.64, 0, 0.64, 0.14, ox, oy, "#bdbdbd", ec="#777777", zo=1)
        r(ax, -0.33, 0.14, 0.33, 0.765, ox, oy, "white", ec="#777777", zo=1)
        # collar section at x=0: keyhole spans y -1.4875..+0.5625
        r(ax, -2.80, -0.125, -1.4875, 0, ox, oy, "#9ec5ea")
        r(ax, 0.5625, -0.125, 1.00, 0, ox, oy, "#9ec5ea")
        # keeper section: material from notch edge (-0.65) to -2.75, slot gap -0.85..-2.55 (centers 0.95..2.45)
        k0 = shift
        r(ax, -2.75 + k0, 0, -0.65 + k0, 0.125, ox, oy, "#c9e6c3")
        # thumbscrew at y=-2.45: shank, knurled head, washer, nut under collar
        y = -2.45
        r(ax, y - 0.095, -0.36, y + 0.095, 0.17, ox, oy, "#777777", zo=3)
        r(ax, y - 0.30, 0.17, y + 0.30, 0.42, ox, oy, "#555555", zo=3)
        r(ax, y - 0.22, 0.125, y + 0.22, 0.17, ox, oy, "#999999", zo=3)
        r(ax, y - 0.19, -0.30, y + 0.19, -0.125, ox, oy, "#555555", zo=3)
        ax.text(0.5, oy + K * 1.35, title, fontsize=9, weight="bold")
        return ox, oy

    ox, oy = panel(5.6, 7.2, 0.0, "LOCKED (using it)")
    lab(ax, ox + K * -0.66, oy + K * 0.07, ox + K * -0.9, oy + K * 1.05, "keeper notch pushes\non the side of the ring")
    lab(ax, ox + K * 0.8, oy - K * 0.06, ox + K * 1.0, oy - K * 0.9, "collar lip under the ring\n(other side of the keyhole)")
    lab(ax, ox + K * -1.4, oy + K * 0.06, ox + K * -2.2, oy + K * 1.05, "KEEPER (green)\nlies on top of collar")
    lab(ax, ox + K * -2.0, oy - K * 0.06, ox + K * -1.6, oy - K * 0.95, "COLLAR (blue)")
    lab(ax, ox + K * -2.75, oy + K * 0.35, ox + K * -4.4, oy + K * 0.85, "thumbscrew")
    lab(ax, ox + K * -2.64, oy - K * 0.22, ox + K * -4.4, oy - K * 0.75, "10-24 nut glued\nunder the collar")
    lab(ax, ox + K * 0.25, oy + K * 0.6, ox + K * 0.7, oy + K * 1.05, "button")

    ox, oy = panel(5.6, 3.9, -1.50, "OPEN (putting it on / taking it off)")
    lab(ax, ox + K * -2.6, oy + K * 0.12, ox + K * -1.3, oy + K * 0.95, "keeper slid 1-1/2\" away from the can:\nthe keyhole is open so the ring can pass")
    ax.annotate("", (ox + K * -2.4, oy + K * -0.45), (ox + K * -1.2, oy + K * -0.45), arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(ox + K * -2.3, oy + K * -0.62, "slide", fontsize=6)
    ax.text(0.5, 0.9,
        "HOW TO USE IT\n"
        "1. Loosen the thumbscrew a couple of turns. Slide the keeper away from the can (to the left here).\n"
        "2. Set the collar over the can so the valve ring comes up through the BIG round hole, then slide the collar sideways\n"
        "    so the ring moves into the small round seat. The collar plate is now under the ring.\n"
        "3. Slide the keeper back toward the can until its curved notch touches the ring. Tighten the thumbscrew.\n"
        "    The ring is now trapped: collar underneath, keeper notch on the open side. It can't slide or twist.\n"
        "The keeper only moves sideways along its slot. The thumbscrew never comes out, it just loosens so the keeper can slide.",
        fontsize=7, va="bottom")
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p5.png"), dpi=80)
print("ok")
