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
# v0.4: thumbscrew hole moved 0.25" toward the big hole (was y 2.45) so the keeper can clamp tighter
collar_holes = [(0, 2.20, D7), (-0.95, -0.60, D7), (-1.45, -0.60, D7)]
for x, y, d in collar_holes:
    collar = collar.difference(hole(x, y, d))

# ---- Keeper (notched edge at y=0) ----
keeper = rounded_rect(-0.875, 0, 0.875, 2.75, 0.19)
# v0.4: slot shortened (was 0.95..2.45): opens just enough to clear the ring, 0.15" extra push when locked
keeper = keeper.difference(hole(0, 0, 1.30)).difference(slot(0, 1.10, 0, 2.35, D7))

collar = affinity.scale(collar, 1, -1, origin=(0, 0))
keeper = affinity.scale(keeper, 1, -1, origin=(0, 0))
collar_holes = [(x, -y, d) for x, y, d in collar_holes]

# ---- Frame (side view: x forward, z up) ----
# v0.4: trimmed top, grip raked ~8 deg and moved back, pivot moved forward for more trigger travel
import math
P = (-1.50, 1.215)       # trigger pivot, nominal (slot lets it move -0.165/+0.335)
S = (-2.50, 0.87)        # up-stop shoulder bolt, nominal (its own slot, same travel)
SLOT = (-0.165, 0.335)
pts = [(-0.80, 0), (-0.80, 1.35), (-1.15, 1.90), (-2.00, 1.90), (-2.95, 1.40), (-4.45, 0.25), (-5.10, -4.55),
       (-4.20, -4.55), (-3.55, -0.50), (-1.70, -0.125), (-1.70, 0)]
frame = Polygon(pts)
frame = frame.buffer(-0.2, join_style=1).buffer(0.2, join_style=1)  # R0.2 on outside corners
frame = frame.difference(slot(P[0], P[1] + SLOT[0], P[0], P[1] + SLOT[1], D7))
frame = frame.difference(slot(S[0], S[1] + SLOT[0], S[0], S[1] + SLOT[1], D7))
for x, y in [(-1.05, 0.30), (-1.50, 0.30), (-4.23, -1.60), (-4.57, -3.90)]:
    frame = frame.difference(hole(x, y, D7))

# ---- Trigger (pivot at origin, drawn as it sits on the can) ----
# v0.4: full-hand bar with 4 finger divots, tail that rests on the up-stop, second "finger plate" spaced 3/8" outboard
NOSE = 1.50
nose = box(0, -0.25, NOSE, 0.25).union(hole(NOSE, 0, 0.5))
bump = hole(NOSE, -0.25, 0.40)
boss = hole(0, 0, 0.90)
tail = box(-1.15, -0.22, 0, 0.22).union(hole(-1.15, 0, 0.44))
F0, F1, W = (-0.55, -1.55), (-0.95, -5.35), 0.70   # bar front edge top/bottom, bar width
neck = Polygon([(0.15, -0.40), (-0.55, -1.30), F0, (F0[0] - W, F0[1]), (-0.70, -0.60), (-0.55, -0.22), (0, -0.22)])
bar = Polygon([F0, F1, (F1[0] - W, F1[1]), (F0[0] - W, F0[1])])
L = math.hypot(F1[0] - F0[0], F1[1] - F0[1])
ux, uz = (F1[0] - F0[0]) / L, (F1[1] - F0[1]) / L   # down the bar
nx, nz = -uz, ux
if nx < 0:
    nx, nz = -nx, -nz                                 # forward-pointing normal
DIV_R, DIV_D = 0.70, 0.12                             # divot radius and depth
divots = []
for i in range(4):
    t = (i + 0.5) / 4 * L
    divots.append(hole(F0[0] + ux * t + nx * (DIV_R - DIV_D), F0[1] + uz * t + nz * (DIV_R - DIV_D), 2 * DIV_R))
trigger = nose.union(bump).union(boss).union(tail).union(neck).union(bar)
trigger = trigger.difference(divots[0].union(divots[1]).union(divots[2]).union(divots[3]))
trigger = trigger.buffer(-0.06, join_style=1).buffer(0.06, join_style=1)   # round every outside corner
spacers = []
for z in (-1.95, -3.60, -5.05):
    t = (z - F0[1]) / uz
    spacers.append((F0[0] + ux * t - nx * (W / 2 + 0.06), z))
finger = trigger.intersection(box(-3, -6, 3, -1.40)).buffer(-0.06, join_style=1).buffer(0.06, join_style=1)
for x, z in spacers:
    trigger = trigger.difference(hole(x, z, D7))
    finger = finger.difference(hole(x, z, D7))
trigger = trigger.difference(hole(0, 0, DF))
STOP_AT = (S[0] - P[0], S[1] - P[1])   # stop bolt in trigger coordinates (under the tail)


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
        ax.text(2.0, 0.55, "Spray can trigger handle v0.4, 1:1 templates. All 0.125\" (1/8\") 5052 aluminum.\n"
                "Holes marked #7 = 0.201\" (10-24 clearance). F = 0.257\" (1/4\" shoulder bolt). Inches.\n"
                "Datum: + = can axis. Dims from carlie's build notes (future-builds-spray-can-trigger.md).", fontsize=6)
    pdf.savefig(fig)
    return fig


def spacer_marks(ax, ox, oy):
    for x, z in spacers:
        ax.text(x + ox + 0.13, z + oy - 0.03, "S", fontsize=5)


def can_axis(ax, ox, oy):
    ax.plot([ox - 0.15, ox + 0.15], [oy, oy], "r-", lw=0.4)
    ax.plot([ox, ox], [oy - 0.15, oy + 0.15], "r-", lw=0.4)


def pivot_mark(ax, ox, oy):
    ax.text(ox + 0.3, oy + 0.3, "pivot (F hole)", fontsize=5)
    ax.text(ox + 0.8, oy - 0.62, "nose bump\npresses button", fontsize=5)
    ax.text(ox - 1.5, oy + 0.32, "tail rests on\nthe up-stop", fontsize=5)
    spacer_marks(ax, ox, oy)


def frame_marks(ax, ox, oy):
    ax.plot([ox - 1.70, ox - 0.80], [oy, oy], "r:", lw=0.5)
    ax.text(ox - 0.65, oy - 0.05, "<- collar sits here", fontsize=5, color="r")
    ax.text(ox - 0.65, oy + 1.25, "<- pivot slot, #7 wide", fontsize=5)
    ax.annotate("up-stop slot", (ox + S[0], oy + S[1] + 0.3), (ox - 3.6, oy + 1.9), fontsize=5, ha="right", arrowprops=dict(arrowstyle="-", lw=0.4))


with PdfPages(OUT) as pdf:
    f1 = page(pdf, [
        (collar, 2.3, 8.6, "COLLAR (top view, qty 1)",
         "Forward (spray) is right; top of page = can's left. Seat 1.125, big hole 1.375. Cut slot 0.02\" small, file to fit.\n3 holes #7: thumbscrew (bottom, v0.4: 1/4\" closer to the big hole), 2 clip holes (upper left). + = can center.",
         [(0, -2.20, ""), (-0.95, 0.60, ""), (-1.45, 0.60, "")], can_axis),
        (keeper, 2.0, 4.9, "KEEPER (qty 1)",
         "Notch 1.30 dia. Slot #7 wide.", [], None),
        (trigger, 6.0, 8.3, "TRIGGER (side view, qty 1)",
         "Flat, no bends. Nose (right) presses button.\nPivot hole F (0.257). S = 3 spacer holes #7.", [], pivot_mark),
    ])
    f1.savefig(PNG.replace(".png", "-p1.png"), dpi=80)
    f2 = page(pdf, [
        (frame, 6.0, 6.3, "FRAME / HANDLE (side view, qty 1)",
         "Forward is right. Clip holes #7 at z +0.30; grip-scale holes #7.", [], frame_marks),
        (finger, 7.3, 6.5, "FINGER PLATE (qty 1)",
         "Same divots as the trigger.\nS = 3 spacer holes #7.", [], spacer_marks),
        (clip_flat, 6.2, 9.1, "ANGLE CLIP (qty 1)",
         "Cut 1-1/10\" off 3/4\" x 3/4\" x 1/8\" aluminum ANGLE.\nWrap this template around it: dashed line = the corner.\n4 holes #7. Left = front (toward the can).", [], clip_marks),
    ])
    f2.savefig(PNG.replace(".png", "-p2.png"), dpi=80)

    # ---------- Assembly pages (side + top view, 1:1) ----------
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
    fill(ax, affinity.translate(finger, *P), ox, oy, "#d6d6d6", z=6)
    for x, z in spacers:
        ax.add_patch(plt.Circle((ox + P[0] + x, oy + P[1] + z), 0.17, fc="#555555", ec="k", lw=0.5, zorder=7))
    ax.add_patch(plt.Circle((ox + P[0], oy + P[1]), 0.19, fc="#555555", ec="k", lw=0.5, zorder=6))
    ax.add_patch(plt.Circle((ox + S[0], oy + S[1]), 0.19, fc="#555555", ec="k", lw=0.5, zorder=6))
    lab(ax, ox + 0.0, oy - 0.06, ox - 0.3, oy - 1.3, "COLLAR (edge-on)\nunder the valve ring")
    lab(ax, ox + 0.5, oy + 0.07, ox + 0.2, oy + 1.25, "KEEPER (edge-on)\non top of collar")
    lab(ax, ox - 0.2, oy + 0.75, ox + 0.5, oy + 0.85, "BUTTON")
    lab(ax, ox + P[0], oy + P[1] + 0.19, ox - 1.2, oy + 2.8, "shoulder bolt = TRIGGER PIVOT (in the slot)")
    lab(ax, ox + 0.0, oy + 1.0, ox + 0.4, oy + 2.2, "trigger NOSE rests on top of button")
    lab(ax, ox - 1.0, oy + 0.6, ox - 0.4, oy + 1.9, "angle CLIP (far side, dashed)")
    lab(ax, ox + S[0], oy + S[1] + 0.19, ox - 4.6, oy + 2.3, "UP-STOP shoulder bolt: the trigger tail rests on it")
    lab(ax, ox - 4.7, oy - 2.6, ox - 6.0, oy - 1.4, "HANDLE / FRAME plate\n(grip, add scales later)")
    lab(ax, ox - 2.5, oy - 2.2, ox - 2.1, oy - 4.3, "TRIGGER bar + FINGER PLATE (near side),\n3 spacer screws. Whole hand pulls\nit back = nose pushes button down")
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
    fill(ax, box(frame.bounds[0], 0.095, -0.80, 0.22), ox, oy, "#f3d9b1", z=4)
    tb = trig_on.bounds
    fill(ax, box(tb[0], -0.0625, tb[2], 0.0625), ox, oy, "#bfbfbf", z=5)
    fb = affinity.translate(finger, *P).bounds
    fill(ax, box(fb[0], -0.5625, fb[2], -0.4375), ox, oy, "#d6d6d6", z=5)
    for x, z in spacers:
        fill(ax, box(P[0] + x - 0.125, -0.4375, P[0] + x + 0.125, -0.0625), ox, oy, "#999999", z=5)
    fill(ax, box(P[0] - 0.10, -0.20, P[0] + 0.10, 0.10), ox, oy, "#555555", z=6)
    fill(ax, box(S[0] - 0.10, -0.20, S[0] + 0.10, 0.10), ox, oy, "#555555", z=6)
    lab(ax, ox + 0.45, oy + 0.45, ox - 0.3, oy + 2.4, "valve ring sits in the keyhole SEAT\n(center of the can)")
    lab(ax, ox + 0.6, oy - 1.8, ox - 4.2, oy - 2.9, "KEEPER: slide toward the can, tighten thumbscrew.\nSlide away (down the page) to take it off.")
    lab(ax, ox, oy - 2.20, ox - 1.8, oy - 2.6, "thumbscrew")
    lab(ax, ox - 1.2, oy + 0.8, ox - 2.6, oy + 1.9, "angle CLIP: bolts down into collar\nand sideways into handle plate")
    lab(ax, ox - 3.2, oy + 0.16, ox - 4.9, oy + 1.0, "HANDLE plate (on edge)")
    lab(ax, ox + 0.0, oy - 0.03, ox - 0.9, oy - 0.9, "TRIGGER nose (on edge,\non the can's centerline)")
    lab(ax, ox - 2.6, oy - 0.5, ox - 5.4, oy - 1.0, "FINGER PLATE, 3/8\" spacers")
    lab(ax, ox + P[0], oy - 0.2, ox - 3.6, oy - 1.9, "pivot + up-stop shoulder bolts\nthrough the handle slots")
    steps = ("ASSEMBLY ORDER\n"
             "1. Collar on can: pull keeper back, drop collar over the valve ring at the big hole, slide it so the ring sits in the seat.\n"
             "2. Keeper: slide it toward the can until the notch hugs the ring, tighten the thumbscrew.\n"
             "3. Handle plate stands on edge, its notch over the back edge of the collar, just left of the centerline.\n"
             "4. Angle clip on the left side of the handle plate: 2 bolts down through clip + collar, 2 bolts sideways through clip + handle.\n"
             "5. Bolt the finger plate to the trigger: 3 screws, a 3/8\" spacer on each, locknuts.\n"
             "6. Trigger on the right side of the handle (on the centerline): shoulder bolt through trigger, nylon washer, handle slot, nut.\n"
             "7. Up-stop: second shoulder bolt through the up-stop slot from the trigger side, nut on the far side, under the trigger tail.\n"
             "8. Turn the button so the nozzle points forward. Slide the pivot until the nose just touches the button, tighten.\n"
             "    Then slide the up-stop up under the tail until it touches, tighten. The trigger now can't flip up.\n"
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
        # keeper section: material from notch edge (-0.65) to -2.75, slot gap -1.00..-2.45 (centers 1.10..2.35)
        k0 = shift
        r(ax, -2.75 + k0, 0, -0.65 + k0, 0.125, ox, oy, "#c9e6c3")
        # thumbscrew at y=-2.20 (v0.4): shank, knurled head, washer, nut under collar
        y = -2.20
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
    lab(ax, ox + K * -2.5, oy + K * 0.35, ox + K * -4.4, oy + K * 0.85, "thumbscrew")
    lab(ax, ox + K * -2.39, oy - K * 0.22, ox + K * -4.4, oy - K * 0.75, "10-24 nut glued\nunder the collar")
    lab(ax, ox + K * 0.25, oy + K * 0.6, ox + K * 0.7, oy + K * 1.05, "button")

    ox, oy = panel(5.6, 3.9, -1.10, "OPEN (putting it on / taking it off)")
    lab(ax, ox + K * -2.6, oy + K * 0.12, ox + K * -1.3, oy + K * 0.95, "keeper slid 1.10\" away from the can:\nthe keyhole is open so the ring can pass")
    ax.annotate("", (ox + K * -2.4, oy + K * -0.45), (ox + K * -1.2, oy + K * -0.45), arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(ox + K * -2.3, oy + K * -0.62, "slide", fontsize=6)
    ax.text(0.5, 0.9,
        "HOW TO USE IT\n"
        "1. Loosen the thumbscrew a couple of turns. Slide the keeper away from the can (to the left here).\n"
        "2. Set the collar over the can so the valve ring comes up through the BIG round hole, then slide the collar sideways\n"
        "    so the ring moves into the small round seat. The collar plate is now under the ring.\n"
        "3. Slide the keeper back toward the can until its curved notch touches the ring. Tighten the thumbscrew.\n"
        "    The ring is now trapped: collar underneath, keeper notch on the open side. It can't slide or twist.\n"
        "The keeper only moves sideways along its slot. The thumbscrew never comes out, it just loosens so the keeper can slide.\n"
        "v0.4: thumbscrew hole 1/4\" closer to the can and a shorter slot: it opens just enough to clear the ring,\n"
        "and when locked the screw still has 0.15\" of slot left, so it can't bottom out before the notch is tight.",
        fontsize=7, va="bottom")
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p5.png"), dpi=80)
    # ---------- Trigger motion + sections (moving parts) ----------
    BT = 0.15  # assumed button travel for the drawing, inches (measure a real can)
    th = math.degrees(BT / NOSE)
    fig, ax = newpage("TRIGGER DETAIL: rest vs. full squeeze, and sections (not templates)",
        "Side view 1:1. Solid gray = trigger at rest (tail on the up-stop). Dashed = full squeeze, drawn for a button that moves %.2f\".\n"
        "The button bottoming out is what ends the squeeze, so the trigger never reaches the grip. Measure a real can's button travel." % BT)
    ox, oy = 6.9, 7.6
    grip_front = LineString([(-3.55, -0.50), (-4.20, -4.55)])
    rest = trig_on
    full = affinity.rotate(trig_on, -th, origin=P)
    fill(ax, frame, ox, oy, "#f6e6cc", ec="#b9a07a", z=1)
    fill(ax, rest, ox, oy, "#bfbfbf", z=3)
    for ring in [full.exterior] + list(full.interiors):
        x, y = ring.xy
        ax.plot([v + ox for v in x], [v + oy for v in y], "k--", lw=0.7, zorder=4)
    fill(ax, box(-0.33, 0.14, 0.33, 0.765), ox, oy, "white", ec="#777777", z=2)
    ax.add_patch(plt.Circle((ox + P[0], oy + P[1]), 0.19, fc="#555555", zorder=6))
    ax.add_patch(plt.Circle((ox + S[0], oy + S[1]), 0.125, fc="#c0392b", ec="k", lw=0.5, zorder=6))
    g_rest, g_full = rest.distance(grip_front), full.distance(grip_front)
    lab(ax, ox + S[0], oy + S[1] - 0.12, ox - 5.9, oy + 0.2, "UP-STOP: 1/4\" shoulder of the bolt.\nThe tail rests on it, so the trigger\ncan't swing up past the button.")
    lab(ax, ox + P[0] + NOSE, oy + P[1] - 0.45, ox + 0.2, oy + 1.9, "nose: %.2f\" down at full squeeze" % BT)
    lab(ax, ox - 3.05, oy - 3.9, ox - 1.6, oy - 3.3,
        "gap to grip: %.2f\" at rest, %.2f\" at full squeeze\n(bottom of the bar moves about %.0fx the button travel)" % (g_rest, g_full, (g_rest - g_full) / BT))
    ax.text(0.5, 2.85, "Grip span (back of grip to trigger divots) is about 2-1/2\" at rest. 4 divots, 0.95\" apart, 0.12\" deep, R0.70.\n"
            "Plasti Dip later: mask the pivot hole, the nose bump and the tail where it touches the stop.", fontsize=6.5)

    # Section A-A: through the trigger bar at a spacer, looking down (2x)
    K2 = 2.0
    def rr(x0, y0, w, h, fc, ec="k", hatch=None):
        ax.add_patch(plt.Rectangle((x0, y0), w * K2, h * K2, fc=fc, ec=ec, lw=0.6, hatch=hatch, zorder=3))
    sx, sy = 0.9, 0.55
    ax.text(0.5, 2.45, "SECTION A-A through a spacer, looking down (2x size)", fontsize=8, weight="bold")
    rr(sx + K2 * 0.255, sy - K2 * 0.04, 0.19, 0.92, "#777777")             # screw shank through all
    rr(sx + K2 * 0.17, sy - K2 * 0.13, 0.36, 0.09, "#555555")             # button head (frame side)
    rr(sx, sy, 0.70, 0.125, "#bfbfbf", hatch="////")                        # trigger plate (bar width 0.70)
    rr(sx + K2 * 0.225, sy + K2 * 0.125, 0.25, 0.375, "#999999")           # spacer
    rr(sx, sy + K2 * 0.5, 0.70, 0.125, "#d6d6d6", hatch="////")            # finger plate
    rr(sx + K2 * 0.16, sy + K2 * 0.625, 0.38, 0.25, "#555555")             # locknut (outboard)
    ax.text(sx + K2 * 0.80, sy + K2 * 0.70, "10-24 locknut", fontsize=6)
    ax.text(sx + K2 * 0.80, sy + K2 * 0.53, "FINGER PLATE (outboard)", fontsize=6)
    ax.text(sx + K2 * 0.80, sy + K2 * 0.28, "3/8\" long spacer, #10 x 1/4\" OD", fontsize=6)
    ax.text(sx + K2 * 0.80, sy + K2 * 0.03, "TRIGGER plate (frame side)", fontsize=6)
    ax.text(sx + K2 * 0.80, sy - K2 * 0.13, "10-24 x 1\" button-head screw", fontsize=6)
    ax.text(sx + K2 * 0.80, sy - K2 * 0.25, "Fingers wrap the front edge of both plates:\n5/8\" wide overall.", fontsize=6)

    # Up-stop stack, looking down (2x)
    tx, ty = 5.3, 0.7
    ax.text(5.0, 2.45, "UP-STOP STACK, looking down (2x)", fontsize=8, weight="bold")
    rr(tx, ty + K2 * 0.32, 0.95, 0.125, "#f3d9b1", hatch="////")             # frame plate
    rr(tx + K2 * 0.375, ty + K2 * 0.07, 0.25, 0.25, "#777777")             # shoulder
    rr(tx + K2 * 0.32, ty - K2 * 0.06, 0.36, 0.13, "#555555")              # head
    rr(tx + K2 * 0.40, ty + K2 * 0.445, 0.20, 0.20, "#777777")             # thread
    rr(tx + K2 * 0.31, ty + K2 * 0.445, 0.38, 0.16, "#555555")             # nut
    rr(tx + K2 * 0.68, ty + K2 * 0.135, 0.27, 0.125, "#bfbfbf", hatch="////")  # trigger tail beside it
    ax.text(tx + K2 * 1.05, ty + K2 * 0.36, "HANDLE plate (stop slot)", fontsize=6)
    ax.text(tx + K2 * 1.05, ty + K2 * 0.17, "trigger tail lands\non the shoulder", fontsize=6)
    ax.text(tx + K2 * 1.05, ty + K2 * 0.53, "10-24 locknut", fontsize=6)
    ax.text(tx + K2 * 1.05, ty - K2 * 0.06, "shoulder bolt 1/4\" x 1/4\",\nsame part as the pivot", fontsize=6)
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p6.png"), dpi=80)
    # ---------- OPEN / CLOSED checks: every moving part in both end states, with clearances computed ----------
    RING = 0.64                    # valve ring radius (32.5 mm cup)
    TS = collar_holes[0][1]        # thumbscrew y (negative = keeper side)
    k_lo, k_hi = 1.10, 2.35        # keeper slot centers, from the notch center
    big = (0, -0.80)               # keyhole big hole center

    def keeper_at(off):            # keeper slid `off` inches away from the can (toward -y)
        return affinity.translate(keeper, 0, -off)

    off_open = -TS - k_lo          # screw at the near end of the slot
    off_stop = -TS - k_hi          # screw at the far end: furthest the keeper can push toward the can
    ring_seat, ring_big = Point(0, 0).buffer(RING, 64), Point(*big).buffer(RING, 64)
    path = ring_seat.union(ring_big).union(box(-RING, big[1], RING, 0))
    k_open, k_closed = keeper_at(off_open), keeper_at(0.0)
    checks = []
    def chk(part, state, what, val, ok, unit='"'):
        checks.append((part, state, what, ("%.2f%s" % (val, unit)) if val is not None else "", "PASS" if ok else "FAIL"))
    d = k_open.distance(path)
    chk("Keeper", "OPEN", "ring slides seat <-> big hole without touching the keeper", d, d > 0.02)
    chk("Keeper", "CLOSED", "notch reaches the ring (gap at notch-centered)", k_closed.distance(ring_seat), True)
    chk("Keeper", "CLOSED", "slot travel left past the ring (screw not bottomed)", -off_stop, -off_stop > 0.05)
    chk("Keeper", "OPEN", "big hole clears the ring (1.375 vs %.3f)" % (2 * RING), 1.375 / 2 - RING, 1.375 / 2 > RING)

    can_side = Polygon([(-1.28, -0.95), (-1.15, -0.85), (-1.0, -0.65), (-0.75, -0.35), (-0.62, 0.0), (0.62, 0.0), (0.75, -0.35),
                        (1.0, -0.65), (1.15, -0.85), (1.28, -0.95), (1.28, -6), (-1.28, -6)])
    collar_side = box(-1.70, -0.125, 1.00, 0)
    grip_front = LineString([(-3.55, -0.50), (-4.20, -4.55)])
    rows = {}
    for dz in (SLOT[0], 0.0, SLOT[1]):
        P2 = (P[0], P[1] + dz)
        rest = affinity.translate(trigger, *P2)
        fin = affinity.translate(finger, *P2)
        full = affinity.rotate(rest, -math.degrees(BT / NOSE), origin=P2)
        ffull = affinity.rotate(fin, -math.degrees(BT / NOSE), origin=P2)
        if dz == 0.0:
            stop = Point(S).buffer(0.125, 32)
            chk("Trigger", "REST", "tail sits on the up-stop shoulder", rest.distance(stop), rest.distance(stop) < 0.01)
            nose_low = P2[1] - 0.45
            chk("Trigger", "REST", "nose bump touches the button top (0.765)", nose_low - 0.765, abs(nose_low - 0.765) < 0.01)
            chk("Trigger", "FULL", "tail lifts off the up-stop", full.distance(stop), full.distance(stop) > 0.02)
        for st, t, f in (("REST", rest, fin), ("FULL", full, ffull)):
            for what, val, lim in (("clears the collar", t.distance(collar_side), 0.05),
                                   ("gap to grip (must stay open)", min(t.distance(grip_front), f.distance(grip_front)), 0.1),
                                   ("finger room to the can", min(t.distance(can_side), f.distance(can_side)), 0.4)):
                rows.setdefault((st, what), []).append((val, val > lim))
    for (st, what), vals in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0] != "REST")):
        checks.append(("Trigger", st, what + " (pivot low/mid/high)", " / ".join("%.2f" % v for v, _ in vals) + '"',
                       "PASS" if all(ok for _, ok in vals) else "FAIL"))

    fig, ax = newpage("OPEN / CLOSED CHECKS: every moving part in both end states (not templates)",
        "Each moving part is drawn and measured at both ends of its travel, so the mechanism is proven on paper before it's cut.\n"
        "Top row: keeper OPEN and CLOSED from above (1:1). Dashed circle = valve ring. Table: clearances computed from the template outlines.\n"
        "Trigger FULL assumes the button moves %.2f\" (BT in templates.py). Measure a real can and rerun." % BT)
    for (kx, ky, kk, ring, ttl) in ((2.3, 8.0, k_open, ring_big, "KEEPER OPEN: slid out, ring comes up\nthrough the big hole"),
                                    (6.0, 8.0, k_closed, ring_seat, "KEEPER CLOSED: notch hugs the ring\nin the seat, screw not bottomed")):
        fill(ax, collar, kx, ky, "#9ec5ea", z=1)
        fill(ax, kk, kx, ky, "#c9e6c3", alpha=0.85, z=2)
        x, y = ring.exterior.xy
        ax.plot([v + kx for v in x], [v + ky for v in y], "k--", lw=0.8, zorder=4)
        ax.add_patch(plt.Circle((kx, ky + TS), 0.15, fc="#555555", zorder=5))
        ax.text(kx - 1.7, ky + 1.35, ttl, fontsize=7, weight="bold")
    y0 = 3.7
    ax.text(0.5, y0 + 0.25, "PART      STATE    CHECK", fontsize=6.5, weight="bold", family="monospace")
    for i, (part, st, what, val, res) in enumerate(checks):
        yy = y0 - 0.19 * i
        ax.text(0.5, yy, "%-9s %-8s %s" % (part, st, what), fontsize=6, family="monospace")
        ax.text(6.6, yy, val, fontsize=6, family="monospace", ha="right")
        ax.text(6.9, yy, res, fontsize=6, family="monospace", weight="bold", color="#2e7d32" if res == "PASS" else "#c0392b")
    ax.text(0.5, y0 - 0.19 * len(checks) - 0.25,
            "Real-life check when the parts arrive: do each state by hand on a can (keeper open, can on, keeper closed and tight;\n"
            "trigger at rest on the stop, squeeze until it sprays) and confirm each PASS line above.", fontsize=6.5, va="top")
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p7.png"), dpi=80)
    for c in checks:
        print(*c)
print("ok")
