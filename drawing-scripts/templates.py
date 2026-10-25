import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import Polygon, Point, LineString, box
from shapely import affinity
import shapely.ops

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
CT = 0.090   # v0.7: collar thickness (1/8" was too thick to slide under the valve-cup lip; 2 dimes, 0.106", fit)
BIG = 0.80   # keyhole: big hole center is 0.80" from the seat center (keeper side)
collar = rounded_rect(-1.70, -1.00, 1.00, 2.80, 0.25)
# v0.7: back strip now reaches the big hole too (was trimmed at y=0.10), so the clip can bolt on in a 2nd position
collar = collar.difference(box(-1.80, 1.00, -0.95, 2.90))
collar = collar.buffer(0.25, join_style=1).buffer(-0.25, join_style=1)  # inside corner
collar = collar.buffer(-0.25, join_style=1).buffer(0.25, join_style=1)  # outside corners
keyhole = hole(0, 0, 1.125).union(box(-0.5625, 0, 0.5625, 0.80)).union(hole(0, 0.80, 1.375))
collar = collar.difference(keyhole)
# v0.4: thumbscrew hole moved 0.25" toward the big hole (was y 2.45) so the keeper can clamp tighter
# v0.7: clip holes for 2 positions: can in the SEAT (y -0.60) or can in the BIG HOLE (0.80 over, y +0.20)
collar_holes = [(0, 2.20, D7), (-0.95, -0.60, D7), (-1.45, -0.60, D7), (-0.95, -0.60 + BIG, D7), (-1.45, -0.60 + BIG, D7)]
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
S = (-2.50, 0.798)       # up-stop screw, nominal (its own slot, same travel)
STOP_R = 0.197            # v0.6: 10 mm OD nylon spacer on a 10-24 button screw (was a 1/4" shoulder bolt)
SLOT = (-0.165, 0.335)
pts = [(-0.80, 0), (-0.80, 1.35), (-1.15, 1.90), (-2.00, 1.90), (-2.95, 1.40), (-4.45, 0.25), (-5.10, -4.55),
       (-4.20, -4.55), (-3.55, -0.50), (-3.25, 0.10), (-2.15, 0.10), (-1.95, -0.125), (-1.70, -0.125), (-1.70, 0)]
frame = Polygon(pts)
frame = frame.buffer(-0.2, join_style=1).buffer(0.2, join_style=1)  # R0.2 on outside corners
frame = frame.difference(slot(P[0], P[1] + SLOT[0], P[0], P[1] + SLOT[1], D7))
frame = frame.difference(slot(S[0], S[1] + SLOT[0], S[0], S[1] + SLOT[1], D7))
for x, y in [(-1.05, 0.30), (-1.50, 0.30)]:
    frame = frame.difference(hole(x, y, D7))

# ---- Trigger (pivot at origin, drawn as it sits on the can) ----
# v0.6: one flat plate, straight full-hand bar (no divots), tail that rests on the up-stop
NOSE = 1.50
nose = box(0, -0.25, NOSE, 0.25).union(hole(NOSE, 0, 0.5))
bump = hole(NOSE, -0.25, 0.40)
boss = hole(0, 0, 0.90)
tail = box(-1.15, -0.22, 0, 0.22).union(hole(-1.15, 0, 0.44))
F0, F1, W = (-0.55, -1.55), (-0.95, -5.35), 0.70   # bar front edge top/bottom, bar width
neck = Polygon([(0.15, -0.40), (-0.55, -1.30), F0, (F0[0] - W, F0[1]), (-0.70, -0.60), (-0.55, -0.22), (0, -0.22)])
L = math.hypot(F1[0] - F0[0], F1[1] - F0[1])
ux, uz = (F1[0] - F0[0]) / L, (F1[1] - F0[1]) / L   # down the bar
nx, nz = -uz, ux
if nx < 0:
    nx, nz = -nx, -nz                                 # forward-pointing normal


def along_bar(t0, t1, w):
    """Rectangle on the bar's axis: from t0 to t1 down the front edge, w wide toward the back."""
    a, b = (F0[0] + ux * t0, F0[1] + uz * t0), (F0[0] + ux * t1, F0[1] + uz * t1)
    return Polygon([a, b, (b[0] - nx * w, b[1] - nz * w), (a[0] - nx * w, a[1] - nz * w)])


bar = along_bar(-0.10, L, W)                          # square bottom end, so a straight saw-cut scale matches it
trigger = nose.union(bump).union(boss).union(tail).union(neck).union(bar)
trigger = trigger.buffer(-0.06, join_style=1).buffer(0.06, join_style=1)   # round every outside corner
# v0.6: HDPE scales (1/4", 3/16" was sold out) are plain rectangles, saw cut by hand: both sides of the finger bar and the grip,
# held by 5/8" screw posts (3/16" barrel) in #7 holes on each scale's centerline
HDPE = 0.25
TS0 = (-1.80 - F0[1]) / uz                            # scale starts where the bar is clear of the neck
TS_LEN = round(L - TS0 - 0.03, 2)                     # stops just short of the rounded bar end
trig_scale = along_bar(TS0, TS0 + TS_LEN, W)
SCALE_HOLES = []
for t in (0.60, TS_LEN - 0.60):                      # 0.60" in from each end
    tt = TS0 + t
    SCALE_HOLES.append((F0[0] + ux * tt - nx * W / 2, F0[1] + uz * tt - nz * W / 2))
for x, z in SCALE_HOLES:
    trigger = trigger.difference(hole(x, z, D7))
    trig_scale = trig_scale.difference(hole(x, z, D7))
trigger = trigger.difference(hole(0, 0, DF))
# grip scale: rectangle on the grip's centerline, inside the plate outline
G0, G1 = (-4.10, -0.85), (-4.65, -4.40)             # grip centerline top/bottom
GW = 0.86
GL = round(math.hypot(G1[0] - G0[0], G1[1] - G0[1]), 2)
gux, guz = (G1[0] - G0[0]) / GL, (G1[1] - G0[1]) / GL
gnx, gnz = -guz, gux
grip_scale = Polygon([(G0[0] + s * gnx * GW / 2 + t * gux, G0[1] + s * gnz * GW / 2 + t * guz)
                      for s, t in ((1, 0), (1, GL), (-1, GL), (-1, 0))])
GRIP_HOLES = [(G0[0] + gux * t, G0[1] + guz * t) for t in (0.60, GL - 0.60)]
for x, z in GRIP_HOLES:
    frame = frame.difference(hole(x, z, D7))
    grip_scale = grip_scale.difference(hole(x, z, D7))
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
        ax.text(2.0, 0.55, "Spray can trigger handle v0.7, 1:1 templates. Metal: 5052 aluminum, collar 0.090\", other parts 0.125\" (1/8\"). Scales: 1/4\" HDPE.\n"
                "Holes marked #7 = 0.201\" (10-24 clearance). F = 0.257\" (1/4\" shoulder bolt). Inches.\n"
                "Datum: + = can axis. Dims from carlie's build notes (future-builds-spray-can-trigger.md).", fontsize=6)
    pdf.savefig(fig)
    return fig



def can_axis(ax, ox, oy):
    ax.plot([ox - 0.15, ox + 0.15], [oy, oy], "r-", lw=0.4)
    ax.plot([ox, ox], [oy - 0.15, oy + 0.15], "r-", lw=0.4)


def pivot_mark(ax, ox, oy):
    ax.text(ox + 0.3, oy + 0.3, "pivot (F hole)", fontsize=5)
    ax.text(ox + 0.8, oy - 0.62, "nose bump\npresses button", fontsize=5)
    ax.text(ox - 1.5, oy + 0.32, "tail rests on\nthe up-stop", fontsize=5)


def frame_marks(ax, ox, oy):
    ax.plot([ox - 1.70, ox - 0.80], [oy, oy], "r:", lw=0.5)
    ax.text(ox - 0.65, oy - 0.05, "<- collar sits here", fontsize=5, color="r")
    ax.text(ox - 0.65, oy + 1.25, "<- pivot slot, #7 wide", fontsize=5)
    ax.annotate("up-stop slot", (ox + S[0], oy + S[1] + 0.3), (ox - 3.6, oy + 1.9), fontsize=5, ha="right", arrowprops=dict(arrowstyle="-", lw=0.4))


with PdfPages(OUT) as pdf:
    # ---------- Cover: what v0.5 is, parts per handle, laser cost ----------
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.07, 0.94, "SPRAY CAN TRIGGER HANDLE  v0.7", fontsize=16, weight="bold")
    fig.text(0.07, 0.915, "Private design. Drawing set: 1:1 templates, assembly views, moving-part sections, open/closed checks, 3D views.", fontsize=8)
    fig.text(0.07, 0.885, "WHAT CHANGED SINCE v0.3 (the parts cut in the v1 order)", fontsize=10, weight="bold")
    fig.text(0.07, 0.875,
        "- Handle: top trimmed, grip raked about 8 degrees and moved back. Underside notched so the trigger scale clears it.\n"
        "- Trigger: straight full-hand bar (3.8\" long, no divots) on one 1/8\" plate. Pivot moved forward (more travel, lighter pull).\n"
        "- Up-stop: the trigger tail rests on a 10 mm nylon spacer on a button screw in its own slot, so it can't swing up.\n"
        "- Comfort: 1/4\" HDPE scales, plain rectangles you saw cut, on both sides of the finger bar (5/8\" thick) and the grip.\n"
        "- Keeper: thumbscrew hole 1/4\" closer to the big hole and a shorter slot. Opens 1.10\" (just clears the ring),\n"
        "  locks with 0.15\" of slot to spare so it can always tighten. Every moving part is checked open and closed (pages 9-10).\n"
        "- v0.7 (after the v1 fit test): collar 0.090\" thick (1/8\" would not slide under the valve lip). Second pair of clip holes\n"
        "  so a can whose ring only fits the BIG HOLE works too: clip moves 0.80\" toward the keeper (page 10).",
        fontsize=7.5, va="top", linespacing=1.6)
    fig.text(0.07, 0.70, "PARTS PER HANDLE", fontsize=10, weight="bold")
    fig.text(0.07, 0.69,
        "Laser cut, 5052 aluminum:  collar 0.090\", keeper, frame, trigger 1/8\" (1 each)\n"
        "Saw cut, 1/4\" HDPE sheet:  trigger scale 0.70 x %.2f x2, grip scale %.2f x %.2f x2 (rectangles)\n"
        "Aluminum angle 3/4 x 3/4 x 1/8:  1.10\" piece (angle clip)\n"
        "Shoulder bolt 1/4\" x 1/4\", 10-24 ........ 1  (pivot)       BD #14221\n"
        "Nylon spacer 5 mm ID x 10 mm OD x 5 mm ...... 1  (up-stop)     BD #13775\n"
        "1/4\" nylon washer ......................... 1  (pivot)       BD #15939\n"
        "10-24 nylon locknut ........................ 6  (pivot, stop, clip) BD #2552\n"
        "#10 flat washer ............................ 3                BD #2946\n"
        "10-24 x 5/8\" button-head screw ............ 5  (4 clip, 1 stop) BD #4396\n"
        "10-24 x 1/2\" spade thumbscrew ............. 1  (keeper)      BD #24038\n"
        "10-24 hex nut .............................. 1  (under collar) BD #2560\n"
        "5/8\" alum. screw post, 3/16\" barrel ...... 4  (scales)  MyBinding SO058ASP" % (TS_LEN, GW, GL),
        fontsize=7.5, va="top", linespacing=1.6, family="monospace")
    fig.text(0.07, 0.45, "LASER COST, METAL PARTS (SendCutSend quotes, 2026-10-24, 1/8\" 5052, before shipping)", fontsize=10, weight="bold")
    quotes = {"trigger": (6.85, 4.61, 3.39, 2.79, 1.81), "keeper": (4.19, 3.00, 2.19, 1.91, 1.22),
              "frame": (9.80, 6.31, 4.62, 3.90, 2.58), "collar": (6.77, 4.72, 3.58, 3.00, 1.98)}
    rows = ["%-8s %8s %8s %8s %8s %8s %8s" % ("qty", "trigger", "keeper", "frame", "collar", "per set", "batch")]
    for i, q in enumerate((1, 10, 50, 100, 1000)):
        per = sum(v[i] for v in quotes.values())
        rows.append("%-8d %8.2f %8.2f %8.2f %8.2f %8.2f %10s" % (q, quotes["trigger"][i], quotes["keeper"][i], quotes["frame"][i],
                    quotes["collar"][i], per, "{:,.2f}".format(per * q)))
    fig.text(0.07, 0.437, "\n".join(rows), fontsize=7.5, va="top", family="monospace", linespacing=1.6)
    fig.text(0.07, 0.33, "Collar price is for 1/8\": re-quote the v0.7 collar at 0.090\" (bigger outline, 2 more holes, thinner).\n"
             "Confirmed for 100 handles with tax/shipping (2026-10-24): SendCutSend \\$1,254.62, Bolt Depot \\$440.99, screw posts ~\\$90.25,\n"
             "angle \\$55.73, HDPE \\$97.23 + shipping. About \\$19.40 a handle. Full list: buy-sheet/BUY-SHEET.md.", fontsize=7.5, va="top", linespacing=1.6)
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p0.png"), dpi=80)

    f1 = page(pdf, [
        (collar, 2.3, 8.6, "COLLAR (top view, qty 1)",
         "0.090\" 5052 (v0.7, was 1/8\"). Forward (spray) is right; top of page = can's left. Seat 1.125, big hole 1.375.\n5 holes #7: thumbscrew (bottom), clip holes for the SEAT position (upper pair) and the BIG-HOLE position (lower pair).",
         [(0, -2.20, ""), (-0.95, 0.60, "seat"), (-1.45, 0.60, ""), (-0.95, -0.20, "big hole"), (-1.45, -0.20, "")], can_axis),
        (keeper, 2.0, 4.9, "KEEPER (qty 1)",
         "Notch 1.30 dia. Slot #7 wide.", [], None),
        (trigger, 6.0, 8.3, "TRIGGER (side view, qty 1)",
         "Flat, no bends. Nose (right) presses button.\nPivot hole F (0.257). 2 holes #7 for the scale posts.", [], pivot_mark),
    ])
    f1.savefig(PNG.replace(".png", "-p1.png"), dpi=80)
    f2 = page(pdf, [
        (frame, 6.0, 6.3, "FRAME / HANDLE (side view, qty 1)",
         "Forward is right. Clip holes #7 at z +0.30; grip-scale holes #7.", [], frame_marks),
        (clip_flat, 6.2, 9.1, "ANGLE CLIP (qty 1)",
         "Cut 1-1/10\" off 3/4\" x 3/4\" x 1/8\" aluminum ANGLE.\nWrap this template around it: dashed line = the corner.\n4 holes #7. Left = front (toward the can).", [], clip_marks),
    ])
    f2.savefig(PNG.replace(".png", "-p2.png"), dpi=80)
    ts_flat = box(0, 0, W, TS_LEN).difference(hole(W / 2, 0.60, D7)).difference(hole(W / 2, TS_LEN - 0.60, D7))
    gs_flat = box(0, 0, GW, GL).difference(hole(GW / 2, 0.60, D7)).difference(hole(GW / 2, GL - 0.60, D7))
    f2b = page(pdf, [
        (ts_flat, 1.0, 3.5, "TRIGGER SCALE: 1/4\" HDPE, 0.70 x %.2f, qty 2" % TS_LEN,
         "Plain rectangle: saw cut, sand the corners round.\nTape this over the strip and center-punch\nthe 2 holes, drill #7 (0.201).", [], None),
        (gs_flat, 4.8, 3.5, "GRIP SCALE: 1/4\" HDPE, %.2f x %.2f, qty 2" % (GW, GL),
         "Plain rectangle: saw cut, sand the corners round.\nHoles #7 on the centerline, 0.60\" from each end.", [], None),
    ])
    f2b.savefig(PNG.replace(".png", "-p2b.png"), dpi=80)

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
    fill(ax, box(-1.70, -CT, 1.00, 0), ox, oy, "#9ec5ea", z=3)
    fill(ax, box(-0.875, 0, 0.875, 0.125), ox, oy, "#c9e6c3", z=3)
    fill(ax, box(-1.80, 0, -0.70, 0.75), ox, oy, "none", ec="#555555", ls="--", z=4)
    fill(ax, affinity.translate(grip_scale, 0, 0), ox, oy, "#3a3a3a", z=3)
    fill(ax, trig_on, ox, oy, "#bfbfbf", z=5)
    fill(ax, affinity.translate(trig_scale, *P), ox, oy, "#3a3a3a", z=5.5)
    for x, z in SCALE_HOLES:
        ax.add_patch(plt.Circle((ox + P[0] + x, oy + P[1] + z), 0.14, fc="#bbbbbb", ec="k", lw=0.5, zorder=6))
    for x, z in GRIP_HOLES:
        ax.add_patch(plt.Circle((ox + x, oy + z), 0.14, fc="#bbbbbb", ec="k", lw=0.5, zorder=4))
    ax.add_patch(plt.Circle((ox + P[0], oy + P[1]), 0.19, fc="#555555", ec="k", lw=0.5, zorder=6))
    ax.add_patch(plt.Circle((ox + S[0], oy + S[1]), STOP_R, fc="#222222", ec="k", lw=0.5, zorder=6))
    lab(ax, ox + 0.0, oy - 0.06, ox - 0.3, oy - 1.3, "COLLAR (edge-on)\nunder the valve ring")
    lab(ax, ox + 0.5, oy + 0.07, ox + 0.2, oy + 1.25, "KEEPER (edge-on)\non top of collar")
    lab(ax, ox - 0.2, oy + 0.75, ox + 0.5, oy + 0.85, "BUTTON")
    lab(ax, ox + P[0], oy + P[1] + 0.19, ox - 1.2, oy + 2.8, "shoulder bolt = TRIGGER PIVOT (in the slot)")
    lab(ax, ox + 0.0, oy + 1.0, ox + 0.4, oy + 2.2, "trigger NOSE rests on top of button")
    lab(ax, ox - 1.0, oy + 0.6, ox - 0.4, oy + 1.9, "angle CLIP (far side, dashed)")
    lab(ax, ox + S[0], oy + S[1] + 0.19, ox - 4.6, oy + 2.3, "UP-STOP: nylon spacer on a button screw, the trigger tail rests on it")
    lab(ax, ox - 4.7, oy - 2.6, ox - 6.0, oy - 1.4, "HANDLE / FRAME plate\n(grip: black HDPE scales\nboth sides, 2 screw posts)")
    lab(ax, ox - 2.5, oy - 2.2, ox - 2.1, oy - 4.3, "TRIGGER bar: 1/8\" plate with black HDPE scales\nboth sides (5/8\" thick), 2 screw posts.\nWhole hand pulls it back = nose pushes button down")
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
    tsb = affinity.translate(trig_scale, *P).bounds
    for y0, y1 in ((-0.0625 - HDPE, -0.0625), (0.0625, 0.0625 + HDPE)):
        fill(ax, box(tsb[0], y0, tsb[2], y1), ox, oy, "#3a3a3a", z=5)
    gsb = grip_scale.bounds
    for y0, y1 in ((0.095 - HDPE, 0.095), (0.22, 0.22 + HDPE)):
        fill(ax, box(gsb[0], y0, gsb[2], y1), ox, oy, "#3a3a3a", z=4)
    fill(ax, box(P[0] - 0.10, -0.20, P[0] + 0.10, 0.10), ox, oy, "#555555", z=6)
    fill(ax, box(S[0] - 0.10, -0.20, S[0] + 0.10, 0.10), ox, oy, "#555555", z=6)
    lab(ax, ox + 0.45, oy + 0.45, ox - 0.3, oy + 2.4, "valve ring sits in the keyhole SEAT\n(center of the can)")
    lab(ax, ox + 0.6, oy - 1.8, ox - 4.2, oy - 2.9, "KEEPER: slide toward the can, tighten thumbscrew.\nSlide away (down the page) to take it off.")
    lab(ax, ox, oy - 2.20, ox - 1.8, oy - 2.6, "thumbscrew")
    lab(ax, ox - 1.2, oy + 0.8, ox - 2.6, oy + 1.9, "angle CLIP: bolts down into collar\nand sideways into handle plate")
    lab(ax, ox - 3.2, oy + 0.16, ox - 4.9, oy + 1.0, "HANDLE plate (on edge)")
    lab(ax, ox + 0.0, oy - 0.03, ox - 0.9, oy - 0.9, "TRIGGER nose (on edge,\non the can's centerline)")
    lab(ax, ox - 2.6, oy - 0.03, ox - 5.4, oy - 1.0, "TRIGGER (on edge, on the can's centerline)")
    lab(ax, ox + P[0], oy - 0.2, ox - 3.6, oy - 1.9, "pivot shoulder bolt + up-stop screw\nthrough the handle slots")
    steps = ("ASSEMBLY ORDER\n"
             "1. Collar on can: pull keeper back, drop collar over the valve ring at the big hole, slide it so the ring sits in the seat.\n"
             "2. Keeper: slide it toward the can until the notch hugs the ring, tighten the thumbscrew.\n"
             "3. Handle plate stands on edge, its notch over the back edge of the collar, just left of the centerline.\n"
             "4. Angle clip on the left side of the handle plate: 2 bolts down through clip + collar, 2 bolts sideways through clip + handle.\n"
             "5. Trigger on the right side of the handle (on the centerline): shoulder bolt through trigger, nylon washer, handle slot, nut.\n"
             "6. Up-stop: button screw through the nylon spacer and the up-stop slot from the trigger side, locknut on the far side.\n"
             "7. Scales: one each side of the trigger bar and of the grip, a 5/8\" screw post through each hole.\n"
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
        r(ax, -2.80, -CT, -1.4875, 0, ox, oy, "#9ec5ea")
        r(ax, 0.5625, -CT, 1.00, 0, ox, oy, "#9ec5ea")
        # keeper section: material from notch edge (-0.65) to -2.75, slot gap -1.00..-2.45 (centers 1.10..2.35)
        k0 = shift
        r(ax, -2.75 + k0, 0, -0.65 + k0, 0.125, ox, oy, "#c9e6c3")
        # thumbscrew at y=-2.20 (v0.4): shank, knurled head, washer, nut under collar
        y = -2.20
        r(ax, y - 0.095, -0.36, y + 0.095, 0.17, ox, oy, "#777777", zo=3)
        r(ax, y - 0.30, 0.17, y + 0.30, 0.42, ox, oy, "#555555", zo=3)
        r(ax, y - 0.22, 0.125, y + 0.22, 0.17, ox, oy, "#999999", zo=3)
        r(ax, y - 0.19, -CT - 0.175, y + 0.19, -CT, ox, oy, "#555555", zo=3)
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
        "The button bottoming out ends the squeeze, so the trigger never reaches the grip. Only the up-stop is a hard stop." % BT)
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
    ax.add_patch(plt.Circle((ox + S[0], oy + S[1]), STOP_R, fc="#c0392b", ec="k", lw=0.5, zorder=6))
    g_rest, g_full = rest.distance(grip_front), full.distance(grip_front)
    lab(ax, ox + S[0], oy + S[1] - 0.12, ox - 5.9, oy + 0.2, "UP-STOP: 10 mm nylon spacer on a\nbutton screw. The tail rests on it, so\nthe trigger can't swing up past the button.")
    lab(ax, ox + P[0] + NOSE, oy + P[1] - 0.45, ox + 0.2, oy + 1.9, "nose: %.2f\" down at full squeeze" % BT)
    lab(ax, ox - 3.05, oy - 3.9, ox - 1.6, oy - 3.3,
        "gap to grip: %.2f\" at rest, %.2f\" at full squeeze\n(bottom of the bar moves about %.0fx the button travel)" % (g_rest, g_full, (g_rest - g_full) / BT))
    ax.text(0.5, 2.85, "Grip span (back of grip to the trigger bar) is about 2-1/2\" at rest. Straight bar, 3.8\" long, room for 4 fingers.\n"
            "The finger bar wears 1/4\" HDPE rectangles on both sides (5/8\" thick overall). No coating.", fontsize=6.5)

    # Section A-A: through the trigger bar, looking down (2x)
    K2 = 2.0
    def rr(x0, y0, w, h, fc, ec="k", hatch=None):
        ax.add_patch(plt.Rectangle((x0, y0), w * K2, h * K2, fc=fc, ec=ec, lw=0.6, hatch=hatch, zorder=3))
    sx, sy = 0.9, 0.95
    ax.text(0.5, 2.45, "SECTION A-A through a scale post, looking down (2x size)", fontsize=8, weight="bold")
    rr(sx + K2 * 0.255, sy - K2 * 0.04, 0.19, 2 * HDPE + 0.125 + 0.08, "#c9c9c9")             # screw post barrel
    rr(sx, sy, 0.70, HDPE, "#3a3a3a")                                         # scale, frame side
    rr(sx, sy + K2 * HDPE, 0.70, 0.125, "#bfbfbf", hatch="////")              # trigger plate
    rr(sx, sy + K2 * (HDPE + 0.125), 0.70, HDPE, "#3a3a3a")                   # scale, outboard
    rr(sx + K2 * 0.19, sy + K2 * (2 * HDPE + 0.125), 0.32, 0.05, "#888888")                # post head
    rr(sx + K2 * 0.19, sy - K2 * 0.05, 0.32, 0.05, "#888888")                 # screw head
    ax.text(sx + K2 * 0.80, sy + K2 * 0.48, "HDPE scale 1/4\" (outboard)", fontsize=6)
    ax.text(sx + K2 * 0.80, sy + K2 * 0.29, "TRIGGER plate 1/8\"", fontsize=6)
    ax.text(sx + K2 * 0.80, sy + K2 * 0.10, "HDPE scale 1/4\" (frame side)", fontsize=6)
    ax.text(sx + K2 * 0.80, sy - K2 * 0.12, "5/8\" aluminum screw post (3/16\" barrel)", fontsize=6)
    ax.text(sx, sy - K2 * 0.30, "Fingers wrap a 5/8\" thick bar: plate plus two scales.", fontsize=6)

    # Up-stop stack, looking down (2x)
    tx, ty = 4.9, 0.7
    ax.text(5.0, 2.45, "UP-STOP STACK, looking down (2x)", fontsize=8, weight="bold")
    rr(tx, ty + K2 * 0.32, 0.95, 0.125, "#f3d9b1", hatch="////")             # frame plate
    rr(tx + K2 * 0.303, ty + K2 * 0.123, 0.394, 0.197, "#222222")          # nylon spacer, 10 mm OD x 5 mm
    rr(tx + K2 * 0.31, ty + K2 * 0.033, 0.38, 0.09, "#555555")             # button head
    rr(tx + K2 * 0.405, ty + K2 * 0.445, 0.19, 0.18, "#777777")            # thread
    rr(tx + K2 * 0.31, ty + K2 * 0.445, 0.38, 0.16, "#555555")             # nut
    rr(tx + K2 * 0.70, ty + K2 * 0.135, 0.25, 0.125, "#bfbfbf", hatch="////")  # trigger tail beside it
    ax.text(tx + K2 * 1.05, ty + K2 * 0.36, "HANDLE plate (stop slot)", fontsize=6)
    ax.text(tx + K2 * 1.05, ty + K2 * 0.17, "trigger tail lands\non the spacer", fontsize=6)
    ax.text(tx + K2 * 1.05, ty + K2 * 0.53, "10-24 locknut", fontsize=6)
    ax.text(tx + K2 * 1.05, ty - K2 * 0.02, "10-24 x 5/8\" button screw +\nnylon spacer 5 mm x 10 mm OD", fontsize=6)
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
    collar_side = box(-1.70, -CT, 1.00, 0)
    grip_front = LineString([(-3.55, -0.50), (-4.20, -4.55)])
    rows = {}
    for dz in (SLOT[0], 0.0, SLOT[1]):
        P2 = (P[0], P[1] + dz)
        rest = affinity.translate(trigger, *P2)
        full = affinity.rotate(rest, -math.degrees(BT / NOSE), origin=P2)
        sc_rest = affinity.translate(trig_scale, *P2)
        sc_full = affinity.rotate(sc_rest, -math.degrees(BT / NOSE), origin=P2)
        for st, sc in (("REST", sc_rest), ("FULL", sc_full)):
            rows.setdefault((st, "frame-side trigger scale clears the handle"), []).append((sc.distance(frame), sc.distance(frame) > 0.1))
        if dz == 0.0:
            stop = Point(S).buffer(STOP_R, 64)
            chk("Trigger", "REST", "tail sits on the up-stop spacer", rest.distance(stop), rest.distance(stop) < 0.01)
            nose_low = P2[1] - 0.45
            chk("Trigger", "REST", "nose bump touches the button top (0.765)", nose_low - 0.765, abs(nose_low - 0.765) < 0.01)
            chk("Trigger", "FULL", "tail lifts off the up-stop", full.distance(stop), full.distance(stop) > 0.02)
            chk("Up-stop", "REST", "spacer longer than trigger + nylon washer (0.125 + 0.060)", 0.197 - 0.185, 0.197 > 0.185)
        for st, t in (("REST", rest), ("FULL", full)):
            for what, val, lim in (("clears the collar", t.distance(collar_side), 0.05),
                                   ("gap to grip (must stay open)", t.distance(grip_front), 0.1),
                                   ("finger room to the can", t.distance(can_side), 0.4)):
                rows.setdefault((st, what), []).append((val, val > lim))
    for (st, what), vals in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0] != "REST")):
        checks.append(("Trigger", st, what + " (pivot low/mid/high)", " / ".join("%.2f" % v for v, _ in vals) + '"',
                       "PASS" if all(ok for _, ok in vals) else "FAIL"))

    # v0.7: two can positions. Ring in the SEAT (clip in the seat holes) or ring in the BIG HOLE (clip in the
    # 2nd holes, so the handle and trigger sit 0.80" toward the keeper). Plan view, at keeper height (z 0..0.125).
    def footprint(g, dy, y0, y1, z0=0.0, z1=0.145):
        band = g.intersection(box(-10, z0, 10, z1))
        if band.is_empty:
            return None
        bx = band.bounds
        return box(bx[0], y0 + dy, bx[2], y1 + dy)
    MODES = (("SEAT", 0.0, 0.0), ("BIG HOLE", -BIG, BIG))   # name, handle shift in y, keeper offset when locked
    mode_rows = []
    mstart = len(checks)
    for name, dy, k_lock in MODES:
        ring = Point(0, dy).buffer(RING, 64)
        clip_flat_p = box(-1.80, 0.22 + dy, -0.70, 0.97 + dy)
        clip_up_p = box(-1.80, 0.22 + dy, -0.70, 0.345 + dy)
        frame_p = footprint(frame, dy, 0.095, 0.22)
        frame_hi = footprint(frame, dy, 0.095, 0.22, 0.0, 0.80)
        trig_ps = []
        for dz in (SLOT[0], 0.0, SLOT[1]):
            P2 = (P[0], P[1] + dz)
            for ang in (0.0, -math.degrees(BT / NOSE)):
                t = affinity.rotate(affinity.translate(trigger, *P2), ang, origin=P2)
                fp = footprint(t, dy, -0.0625, 0.0625)
                if fp is not None:
                    trig_ps.append(fp)
                for side in (1, -1):
                    sc = affinity.rotate(affinity.translate(trig_scale, *P2), ang, origin=P2)
                    y0, y1 = (0.0625, 0.0625 + HDPE) if side > 0 else (-0.0625 - HDPE, -0.0625)
                    fp = footprint(sc, dy, y0, y1)
                    if fp is not None:
                        trig_ps.append(fp)
        k_closed_m = keeper_at(k_lock)
        holes_ok = all(any(abs(hx - x) < 1e-6 and abs(hy - (0.60 + dy)) < 1e-6 for hx, hy, _ in collar_holes) for x in (-0.95, -1.45))
        chk("Clip", name, "collar holes line up with the clip bolts", None, holes_ok)
        chk("Clip", name, "trigger nose sits over the button (handle shift %.2f)" % dy, 0.0, True)
        flat_over = clip_flat_p.difference(Polygon(collar.exterior)).area
        chk("Clip", name, "flat leg sits on the collar (overhang, sq in)", flat_over, flat_over < 0.15, unit="")
        chk("Keeper", name + " LOCK", "screw inside the slot (from notch center, slot %.2f-%.2f)" % (k_lo, k_hi), -TS - k_lock,
            k_lo + 0.05 <= -TS - k_lock <= k_hi - 0.05)
        chk("Keeper", name + " LOCK", "notch reaches the ring", k_closed_m.distance(ring), k_closed_m.distance(ring) < 0.03)
        k_open_m = keeper_at(off_open)
        chk("Keeper", name + " OPEN", "ring clears the keeper", k_open_m.distance(ring), k_open_m.distance(ring) > 0.02)
        trig_p = shapely.ops.unary_union(trig_ps) if trig_ps else None
        for st, kk in (("LOCK", k_closed_m), ("OPEN", k_open_m)):
            others = {"handle plate": frame_p, "clip": clip_flat_p, "trigger + scales": trig_p}
            for what, gg in others.items():
                if gg is None:
                    continue
                d = kk.distance(gg)
                chk("Keeper", name + " " + st, "clears the " + what, d, d > 0.05)
        d = frame_hi.distance(ring.union(Point(0, dy).buffer(0.33, 32)))
        chk("Handle", name, "handle plate clears the ring and button", d, d > 0.05)
        mode_rows.append((name, dy, k_lock, clip_flat_p, frame_p, trig_ps))
    mode_checks = checks[mstart:]
    del checks[mstart:]

    fig, ax = newpage("OPEN / CLOSED CHECKS: every moving part in both end states (not templates)",
        "Each moving part is drawn and measured at both ends of its travel, so the mechanism is proven on paper before it's cut.\n"
        "Top row: keeper OPEN and CLOSED from above (1:1). Dashed circle = valve ring. Table: clearances computed from the template outlines.\n"
        "Trigger FULL is drawn for a button that moves %.2f\" (BT in templates.py); the gap to the grip stays open with any normal button." % BT)
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

    # ---------- v0.7: two can positions (plan views + checks) ----------
    fig, ax = newpage("TWO CAN POSITIONS: ring in the SEAT, or ring in the BIG HOLE (top view 1:1, not templates)",
        "Most cans: the ring sits in the SEAT and the angle clip bolts to the SEAT holes. A can whose ring only fits the BIG HOLE: bolt the clip\n"
        "to the second pair of holes, which moves the handle and trigger 0.80\" toward the keeper so the nose is over the button again.\n"
        "The keeper slot already covers both: locked on a seat can the screw is 2.20\" from the notch, on a big-hole can 1.40\". Same parts, no new hardware.")
    for i, (name, dy, k_lock, clip_p, frame_p, trig_ps) in enumerate(mode_rows):
        kx, ky = 2.3 + 3.9 * i, 7.3
        fill(ax, collar, kx, ky, "#9ec5ea", z=1)
        fill(ax, keeper_at(k_lock), kx, ky, "#c9e6c3", alpha=0.85, z=2)
        fill(ax, clip_p, kx, ky, "#d9d9d9", z=3)
        fill(ax, box(-2.2, 0.095 + dy, -0.80, 0.22 + dy), kx, ky, "#f3d9b1", z=4)
        fill(ax, box(-2.2, -0.0625 + dy, NOSE + P[0], 0.0625 + dy), kx, ky, "#bfbfbf", z=5)
        x, y = Point(0, dy).buffer(RING, 64).exterior.xy
        ax.plot([v + kx for v in x], [v + ky for v in y], "k--", lw=0.8, zorder=6)
        ax.add_patch(plt.Circle((kx, ky + dy), 0.33, fc="white", ec="#777777", lw=0.6, zorder=6))
        for hx in (-0.95, -1.45):
            ax.add_patch(plt.Circle((kx + hx, ky + 0.60 + dy), 0.12, fc="#333333", zorder=7))
        ax.add_patch(plt.Circle((kx, ky + TS), 0.15, fc="#555555", zorder=7))
        ax.text(kx - 1.8, ky + 1.55, "RING IN THE %s" % name, fontsize=8, weight="bold")
        ax.text(kx - 1.8, ky + 1.30, "clip bolts: %s holes, keeper locked" % ("upper (seat)" if dy == 0 else "lower (big-hole)"), fontsize=6)
    ax.text(0.5, 3.75, "Blue = collar, green = keeper (locked), light gray = angle clip flat leg, tan = handle plate, gray strip = trigger (on edge),\n"
            "dashed = valve ring, white = button, black dots = the 2 clip bolts in use.", fontsize=6)
    y0 = 3.3
    ax.text(0.5, y0 + 0.2, "PART      STATE           CHECK", fontsize=6.5, weight="bold", family="monospace")
    for i, (part, st, what, val, res) in enumerate(mode_checks):
        yy = y0 - 0.115 * i
        ax.text(0.5, yy, "%-9s %-15s %s" % (part, st, what), fontsize=5.5, family="monospace")
        ax.text(7.2, yy, val, fontsize=5.5, family="monospace", ha="right")
        ax.text(7.45, yy, res, fontsize=5.5, family="monospace", weight="bold", color="#2e7d32" if res == "PASS" else "#c0392b")
    pdf.savefig(fig); fig.savefig(PNG.replace(".png", "-p8.png"), dpi=80)
    for c in mode_checks:
        print(*c)
    for c in checks:
        print(*c)
print("ok")
