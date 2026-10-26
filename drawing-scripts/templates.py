from shapely.geometry import Polygon, Point, LineString, box
from shapely import affinity
import shapely.ops

D7 = 0.201  # #7 drill, 10-24 clearance
DF = 0.250  # v0.94: 1/4" pin holes cut at 0.250 and finished with a 1/4" reamer (snug slip fit)


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
# v0.9: no angle clip. The handle plate has 2 tabs that drop straight down through 2 collar slots, and a stainless
# hitch pin clip (R-clip, snaps on, nothing to bend) through each tab under the collar holds it down. 2 pairs of slots: can in the SEAT or can in the BIG HOLE (0.80 over).
FY0, FY1 = 0.095, 0.22                   # handle plate faces in y (final, flipped coordinates)
FMID = (FY0 + FY1) / 2
TABS = ((-1.59, -1.27), (-1.16, -0.84))  # tab x extents (rear, front); v0.94: 0.32 long so the 0.125 clip hole keeps 0.0975 of metal each side
SLOT_W = 0.128                           # v0.94: slot for the 0.125 plate, snug (was 0.135 = 6 deg of lean); file to fit
TAB_BOT = -0.33                          # tab bottom (0.13 of metal below the pin hole)
PIN_D = 0.125                            # v0.94: clip hole = SendCutSend minimum hole (sheet thickness); only its bottom edge sets the play
WIRE = 0.080
CT_MAX = CT                              # v0.94: carlie picked the 0.090 collar, so the clip holes are set for it
# v0.94: zero play. The hole bottom sits one wire diameter under the collar, so the clip wire is pinched between the collar
# and the hole. carlie's preload idea: the front tab's hole is PRELOAD higher, so its clip only goes in with the plate
# pulled down tight (file the hole top if it won't go).
PRELOAD = 0.004
PIN_Z = -CT - WIRE + PIN_D / 2           # rear tab hole center
PIN_ZS = (PIN_Z, PIN_Z + PRELOAD)        # (rear, front)
CLIP_DROP = 0.09                         # hitch clip's bent leg wraps this far below the tab bottom
# v0.92: no thumbscrew. The keeper rides on 2 short screw posts in 2 slots (it can only slide straight, can't spin or fall off)
# and locks with a stainless clevis pin through the keeper and collar, with a hitch pin clip under the collar.
PIN_Y, DP = 2.20, DF                     # lock pin hole (old thumbscrew spot); 1/4" clevis pin, cut 0.250 + ream (v0.94, was 0.257)
GUIDES = ((0.55, 2.00), (-0.55, 2.50))   # guide posts; staggered 0.50 along the slide so the keeper can't twist
GSLOT = 0.198                            # guide slot width for the 3/16" (0.1875) post barrel (v0.94: was 0.21; measure the barrel)
K_OPEN = 1.25                            # keeper travel from the seat lock to open; the slot ends are the stops
collar_holes = [(0, PIN_Y, DP)] + [(x, y, D7) for x, y in GUIDES]
for x, y, d in collar_holes:
    collar = collar.difference(hole(x, y, d))

# ---- Keeper (notched edge at y=0) ----
KL = 2.85                                # keeper length (v0.93: was 2.75)
keeper = rounded_rect(-0.875, 0, 0.875, KL, 0.19)
keeper = keeper.difference(hole(0, 0, 1.30))
for x, y in GUIDES:
    keeper = keeper.difference(slot(x, y - K_OPEN, x, y, GSLOT))
for off in (0.0, BIG, K_OPEN):           # pin holes: seat lock, big-hole lock, parked open
    keeper = keeper.difference(hole(0, PIN_Y - off, DP))

collar = affinity.scale(collar, 1, -1, origin=(0, 0))
keeper = affinity.scale(keeper, 1, -1, origin=(0, 0))
collar_holes = [(x, -y, d) for x, y, d in collar_holes]
TAB_SLOTS = [(x0, x1, FMID + dy) for dy in (0.0, -BIG) for x0, x1 in TABS]


def tab_slot(x0, x1, ym):   # near-square slot (small corner radius) so it wastes no collar past the tab ends
    return rounded_rect(x0 - 0.01, ym - SLOT_W / 2, x1 + 0.01, ym + SLOT_W / 2, 0.01)


for x0, x1, ym in TAB_SLOTS:
    collar = collar.difference(tab_slot(x0, x1, ym))

# ---- Frame (side view: x forward, z up) ----
# v0.4: trimmed top, grip raked ~8 deg and moved back, pivot moved forward for more trigger travel
import math
P = (-1.50, 1.215)       # trigger pivot, nominal (lobe 0 of the pivot holes)
S = (-2.50, 0.798)       # up-stop screw, nominal (its own slot, same travel)
STOP_R = 0.197            # v0.6: 10 mm OD nylon spacer on a 10-24 button screw (was a 1/4" shoulder bolt)
SLOT = (-0.165, 0.335)     # up-stop slot travel (it carries no squeeze load, so it stays an adjustable slot)
# v0.94: the pivot is a 1/4" clevis pin + hitch clip in 4 overlapping round lobes (scalloped slot), not a clamped slot.
# Lobes 0.167 apart leave a 0.19 neck, so the 0.250 pin can't slide between positions under load: pull the pin to move it.
PIV = (-0.165, 0.0, 0.167, 0.335)
pts = [(-0.80, 0), (-0.80, 1.35), (-1.15, 1.90), (-2.00, 1.90), (-2.95, 1.40), (-4.45, 0.25), (-5.10, -4.55),
       (-4.20, -4.55), (-3.55, -0.50), (-3.25, 0.10), (-2.15, 0.10), (-1.95, -0.125), (-1.70, -0.125), (-1.70, 0)]
frame = Polygon(pts)
frame = frame.buffer(-0.2, join_style=1).buffer(0.2, join_style=1)  # R0.2 on outside corners
for dz in PIV:
    frame = frame.difference(hole(P[0], P[1] + dz, DF))
frame = frame.difference(slot(S[0], S[1] + SLOT[0], S[0], S[1] + SLOT[1], D7))
for (x0, x1), pz in zip(TABS, PIN_ZS):
    tab = rounded_rect(x0, TAB_BOT, x1, 0.15, 0.05).union(box(x0, -0.01, x1, 0.15))
    frame = frame.union(tab).difference(hole((x0 + x1) / 2, pz, PIN_D))

# ---- Trigger (pivot at origin, drawn as it sits on the can) ----
# v0.6: one flat plate, straight full-hand bar (no divots), tail that rests on the up-stop
NOSE = 1.50
nose = box(0, -0.25, NOSE, 0.25).union(hole(NOSE, 0, 0.5))
bump = hole(NOSE, -0.25, 0.40)
boss = hole(0, 0, 0.90)
tail = box(-1.15, -0.22, 0, 0.22).union(hole(-1.15, 0, 0.44))
# v0.95: bar front edge moved back (top more than bottom) so the printed sleeve sets the grip span for an average man's hand
BAR_BACK = (0.30, 0.10)                              # (top, bottom) shift of the bar front edge toward the grip
F0, F1, W = (-0.55 - BAR_BACK[0], -1.55), (-0.95 - BAR_BACK[1], -5.35), 0.70   # bar front edge top/bottom, bar width
L = math.hypot(F1[0] - F0[0], F1[1] - F0[1])
ux, uz = (F1[0] - F0[0]) / L, (F1[1] - F0[1]) / L   # down the bar
nx, nz = -uz, ux
if nx < 0:
    nx, nz = -nx, -nz                                 # forward-pointing normal
# v0.95: the neck's back edge meets the bar's top back corner, so the raked-back bar leaves no ledge there
neck = Polygon([(0.15, -0.40), (-0.55, -1.30), F0, (F0[0] - ux * 0.10 - nx * W, F0[1] - uz * 0.10 - nz * W), (-0.70, -0.60), (-0.55, -0.22), (0, -0.22)])


def along_bar(t0, t1, w):
    """Rectangle on the bar's axis: from t0 to t1 down the front edge, w wide toward the back."""
    a, b = (F0[0] + ux * t0, F0[1] + uz * t0), (F0[0] + ux * t1, F0[1] + uz * t1)
    return Polygon([a, b, (b[0] - nx * w, b[1] - nz * w), (a[0] - nx * w, a[1] - nz * w)])


bar = along_bar(-0.10, L, W)                          # square bottom end, so a straight saw-cut scale matches it
trigger = nose.union(bump).union(boss).union(tail).union(neck).union(bar)
trigger = trigger.buffer(-0.06, join_style=1).buffer(0.06, join_style=1)   # round every outside corner
HDPE = 0.25                                           # printed sleeve side wall, so the bar and grip are 5/8" thick
# v0.8: trigger plate faces in y. The pivot shoulder (0.25) holds trigger 0.125 + nylon washer 0.060 against the
# handle plate face (y 0.095), with the 0.065 play on the head side, so the trigger sits at y -0.090..+0.035.
TY0, TY1 = -0.090, 0.035
# v0.95: printed U-SLEEVES instead of flat scales (carlie: rounder, more comfortable, sized for an average man's hand).
# One PETG sleeve slides over the FRONT edge of the trigger bar, one over the BACK edge of the grip; each is held by the
# same 2 screw posts. The hand side is a full round across the 5/8" thickness, so no aluminum edge touches the fingers
# or the palm. Lee et al. 2009 (PMID 19424925): 50-55 mm spans grip strongest and most comfortable, about 27-29% of
# hand length; average man's hand 188 mm -> about 51-55 mm. Middle and ring fingers want the widest span (bow-shaped).
SLV_T = 0.06                                          # sleeve wall over the metal edge
SLV_R = (0.125 + 2 * HDPE) / 2                        # full round across the sleeve
SLV_SLOT = 0.135                                      # printed slot for the 0.125 plate (slides on)
BOW, BOW_S = 0.08, (0.45, 3.85)                       # trigger sleeve bulge under the middle/ring fingers, and where it runs


def bow(s):
    a, b = BOW_S
    return BOW * math.sin(math.pi * (s - a) / (b - a)) ** 2 if a < s < b else 0.0


def bar_pt(s, n):                                     # s down the bar front edge, n forward of it
    return (F0[0] + ux * s + nx * n, F0[1] + uz * s + nz * n)


FINGER_Z = (-1.0, -1.75, -2.6, -3.45)                 # finger heights for the span (index, middle, ring, little), can z
TS0 = (-1.92 - F0[1]) / uz                            # sleeve starts where the bar is clear of the neck (v0.95: 0.12 lower, clears the handle at pivot lobe 4)
TS_LEN = round(L - TS0 - 0.03, 2)                     # post holes are placed on this length (as the old scales)
TRIG_SLV = [(s, SLV_T + bow(s)) for s in (TS0 + (L + SLV_T - TS0) * k / 80 for k in range(81))]   # (s, front of sleeve)
trig_sleeve = Polygon([bar_pt(s, f) for s, f in TRIG_SLV] + [bar_pt(s, -W) for s, f in reversed(TRIG_SLV)])
trig_sleeve = trig_sleeve.buffer(-0.04, join_style=1).buffer(0.04, join_style=1)
SCALE_HOLES = []
for t in (0.60, TS_LEN - 0.60):                      # 0.60" in from each end
    SCALE_HOLES.append(bar_pt(TS0 + t, -W / 2))
for x, z in SCALE_HOLES:
    trigger = trigger.difference(hole(x, z, D7))
    trig_sleeve = trig_sleeve.difference(hole(x, z, D7))
trigger = trigger.difference(hole(0, 0, DF))
# grip sleeve: front edge on the old scale's front line, back wraps the plate's back edge (palm side)
G0, G1 = (-4.10, -0.85), (-4.65, -4.40)             # grip centerline top/bottom (post holes sit on it)
GW = 0.86
GL = round(math.hypot(G1[0] - G0[0], G1[1] - G0[1]), 2)
gux, guz = (G1[0] - G0[0]) / GL, (G1[1] - G0[1]) / GL
gnx, gnz = -guz, gux                                  # forward
GRIP_HOLES = [(G0[0] + gux * t, G0[1] + guz * t) for t in (0.60, GL - 0.60)]
for x, z in GRIP_HOLES:
    frame = frame.difference(hole(x, z, D7))


def grip_pt(s, n):
    return (G0[0] + gux * s + gnx * n, G0[1] + guz * s + gnz * n)


PLATE_BOT = min(z for x, z in Polygon(frame.exterior).exterior.coords)
GS0 = -0.35                                           # sleeve top (up near the web of the thumb)
GS1 = (PLATE_BOT - SLV_T - G0[1]) / guz               # sleeve bottom: wraps under the plate bottom
GRIP_SLV, nb_last = [], None
plate_out = Polygon(frame.exterior)
for k in range(81):
    s = GS0 + (GS1 - GS0) * k / 80
    c = grip_pt(s, 0)
    if c[1] > PLATE_BOT + 0.25:                       # above the plate's rounded bottom corner; below it, keep the wall straight
        hit = LineString([c, grip_pt(s, -2.0)]).intersection(plate_out.exterior)
        pts_ = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
        nb_last = -min(math.hypot(p.x - c[0], p.y - c[1]) for p in pts_) - SLV_T
    GRIP_SLV.append((s, nb_last, GW / 2))             # (s, back of sleeve, front of sleeve)
def d_section(n_flat, n_tip, toward, slot):
    """Sleeve cross-section in (n, y): flat side at n_flat, full round (radius SLV_R) whose tip is at n_tip, minus the slot."""
    c = n_tip - toward * SLV_R
    return box(min(n_flat, c), -SLV_R, max(n_flat, c), SLV_R).union(Point(c, 0).buffer(SLV_R, 64)).difference(slot)


TRIG_SEC = d_section(-W, SLV_T + BOW, 1, box(-W - 0.01, -SLV_SLOT / 2, 0, SLV_SLOT / 2))   # at the bow peak
grip_sleeve = Polygon([grip_pt(s, f) for s, b, f in GRIP_SLV] + [grip_pt(s, b) for s, b, f in reversed(GRIP_SLV)])
grip_sleeve = grip_sleeve.buffer(-0.04, join_style=1).buffer(0.04, join_style=1)
for x, z in GRIP_HOLES:
    grip_sleeve = grip_sleeve.difference(hole(x, z, D7))
_s, _b, _f = GRIP_SLV[40]
GRIP_SEC = d_section(_f, _b, -1, box(_b + SLV_T, -SLV_SLOT / 2, _f + 0.01, SLV_SLOT / 2))       # mid grip
STOP_AT = (S[0] - P[0], S[1] - P[1])   # stop bolt in trigger coordinates (under the tail)


# Print every PASS/FAIL clearance check (no pages: parts are 3D printed and cuts ordered from the DXFs).
# The other scripts exec this file for the geometry; under exec __name__ is not "__main__", so this is skipped.
if __name__ == "__main__":
    # ---------- OPEN / CLOSED checks: every moving part in both end states, with clearances computed ----------
    BT = 0.15                      # assumed button travel, inches (measure a real can)
    RING = 0.64                    # valve ring radius (32.5 mm cup)
    TS = collar_holes[0][1]        # lock pin y (negative = keeper side)
    PIN_R, POST_R = 0.25 / 2, 0.1875 / 2      # 1/4" clevis pin, 3/16" screw-post barrel
    big = (0, -0.80)               # keyhole big hole center

    def keeper_at(off):            # keeper slid `off` inches away from the can (toward -y)
        return affinity.translate(keeper, 0, -off)

    off_open = K_OPEN              # guide posts at the near ends of their slots
    posts = [Point(x, -y).buffer(POST_R, 32) for x, y in GUIDES]

    def pin_free(off):             # a keeper hole sits over the collar pin hole, so the pin drops through both
        return keeper_at(off).intersection(Point(0, TS).buffer(PIN_R, 32)).area < 1e-9

    def posts_free(off):           # both guide posts inside their keeper slots
        return all(keeper_at(off).intersection(p).area < 1e-9 for p in posts)
    ring_seat, ring_big = Point(0, 0).buffer(RING, 64), Point(*big).buffer(RING, 64)
    path = ring_seat.union(ring_big).union(box(-RING, big[1], RING, 0))
    k_open, k_closed = keeper_at(off_open), keeper_at(0.0)
    checks = []
    def chk(part, state, what, val, ok, unit='"'):
        checks.append((part, state, what, ("%.2f%s" % (val, unit)) if val is not None else "", "PASS" if ok else "FAIL"))
    d = k_open.distance(path)
    chk("Keeper", "OPEN", "ring slides seat <-> big hole without touching the keeper", d, d > 0.02)
    chk("Keeper", "CLOSED", "slot ends stop it with the notch on the ring", k_closed.distance(ring_seat), k_closed.distance(ring_seat) < 0.03)
    endp = GSLOT / 2 - POST_R      # post-to-slot-end play at each stop
    chk("Keeper", "CLOSED", "slot ends are the stop (play past the lock spot)", endp, posts_free(0.0) and not posts_free(-endp - 0.002))
    chk("Keeper", "OPEN", "stops at the open end of the slots (%.2f\" travel)" % K_OPEN, K_OPEN, posts_free(K_OPEN) and not posts_free(K_OPEN + endp + 0.002))
    chk("Keeper", "ALL", "lock pin drops through: seat lock, big-hole lock, parked open", None,
        all(pin_free(o) for o in (0.0, BIG, K_OPEN)))
    mids = [o / 20 * K_OPEN for o in range(21)]
    chk("Keeper", "ALL", "posts stay in the slots over the whole slide", None, all(posts_free(o) for o in mids))
    tw = math.degrees(2 * (GSLOT / 2 - POST_R) / abs(GUIDES[0][1] - GUIDES[1][1]))
    chk("Keeper", "ALL", "twist with the pin out (staggered posts)", tw, tw < 3, unit=" deg")
    web = min(keeper.exterior.distance(Polygon(i)) for i in keeper.interiors)
    web = min([web] + [Polygon(a).distance(Polygon(b)) for k, a in enumerate(keeper.interiors) for b in keeper.interiors[k + 1:]])
    chk("Keeper", "ALL", "metal between any two holes/slots/edges", web, web > 0.09)
    chk("Keeper", "OPEN", "big hole clears the ring (1.375 vs %.3f)" % (2 * RING), 1.375 / 2 - RING, 1.375 / 2 > RING)

    can_side = Polygon([(-1.28, -0.95), (-1.15, -0.85), (-1.0, -0.65), (-0.75, -0.35), (-0.62, 0.0), (0.62, 0.0), (0.75, -0.35),
                        (1.0, -0.65), (1.15, -0.85), (1.28, -0.95), (1.28, -6), (-1.28, -6)])
    collar_side = box(-1.70, -CT, 1.00, 0)
    grip_front = LineString([(-3.55, -0.50), (-4.20, -4.55)])
    rows = {}
    for dz in PIV:
        P2 = (P[0], P[1] + dz)
        rest = affinity.translate(trigger, *P2)
        full = affinity.rotate(rest, -math.degrees(BT / NOSE), origin=P2)
        sc_rest = affinity.translate(trig_sleeve, *P2)
        sc_full = affinity.rotate(sc_rest, -math.degrees(BT / NOSE), origin=P2)
        for st, sc in (("REST", sc_rest), ("FULL", sc_full)):
            rows.setdefault((st, "trigger sleeve clears the handle plate"), []).append((sc.distance(frame), sc.distance(frame) > 0.1))
            rows.setdefault((st, "trigger sleeve clears the grip sleeve"), []).append((sc.distance(grip_sleeve), sc.distance(grip_sleeve) > 0.1))
        if dz == 0.0:
            stop = Point(S).buffer(STOP_R, 64)
            chk("Trigger", "REST", "tail sits on the up-stop spacer", rest.distance(stop), rest.distance(stop) < 0.01)
            nose_low = P2[1] - 0.45
            chk("Trigger", "REST", "nose bump touches the button top (0.765)", nose_low - 0.765, abs(nose_low - 0.765) < 0.01)
            chk("Trigger", "FULL", "tail lifts off the up-stop", full.distance(stop), full.distance(stop) > 0.02)
            chk("Up-stop", "REST", "spacer longer than trigger + nylon washer (0.125 + 0.060)", 0.197 - 0.185, 0.197 > 0.185)
        for st, t in (("REST", rest.union(sc_rest)), ("FULL", full.union(sc_full))):
            for what, val, lim in (("clears the collar", t.distance(collar_side), 0.05),
                                   ("gap to grip (must stay open)", t.distance(grip_front), 0.1),
                                   ("finger room to the can", t.distance(can_side), 0.4)):
                rows.setdefault((st, what), []).append((val, val > lim))
    tab_geoms = [box(x0, TAB_BOT, x1, 0) for x0, x1 in TABS]
    pins = [box((x0 + x1) / 2 - 0.05, TAB_BOT - CLIP_DROP, (x0 + x1) / 2 + 0.05, PIN_Z + 0.04) for x0, x1 in TABS]   # clip loop around the tab
    d = min(t.distance(can_side) for t in tab_geoms + pins)
    chk("Tabs", "ON CAN", "tab bottoms and clips clear the can top (drawn can)", d, d > 0.05)
    rim = min(min((x1 - x0 - PIN_D) / 2, pz - PIN_D / 2 - TAB_BOT) for (x0, x1), pz in zip(TABS, PIN_ZS))
    chk("Tabs", "ON CAN", "metal around each pin hole (sides and below)", rim, rim >= 0.09)
    gap = (PIN_Z - PIN_D / 2) - (-CT - WIRE)
    chk("Tabs", "ON CAN", "rear clip: wire pinched under the 0.090 collar (play)", gap, abs(gap) < 0.001)
    chk("Tabs", "ON CAN", "front clip: preload, plate pulled down (interference)", PRELOAD, 0 < PRELOAD <= 0.006)
    def min_hole(g):              # smallest hole or slot width in a part (inscribed size of each interior)
        return min(2 * Polygon(i).exterior.distance(Polygon(i).centroid) if Polygon(i).area < 0.2 else 1.0 for i in g.interiors)
    mh = min(min_hole(collar) - CT, min_hole(keeper) - 0.125, min_hole(frame) - 0.125, min_hole(trigger) - 0.125)
    chk("Cutting", "ALL", "every hole/slot at least the sheet thickness (SendCutSend minimum)", max(mh, 0.0), mh >= -0.0005)
    # v0.95 sleeves and grip span
    ch = trig_sleeve.intersection(trigger).difference(along_bar(TS0 - 0.2, L + 0.2, W + 0.002))
    chk("Sleeves", "ALL", "trigger sleeve slides on: no metal in its channel but the bar", ch.area, ch.area < 1e-6, unit=" sq in")
    def spans(ang):                # level span, back of the grip sleeve to the front of the trigger sleeve, per finger (mm)
        sc = affinity.rotate(affinity.translate(trig_sleeve, *P), ang, origin=P)
        cut = lambda gm, z: gm.intersection(LineString([(-9, z), (9, z)])).bounds
        return [(cut(sc, z)[2] - cut(grip_sleeve, z)[0]) * 25.4 for z in FINGER_Z]
    sp = spans(-math.degrees(BT / NOSE))
    chk("Grip", "FULL", "span index/middle/ring/little %s mm (target 51-55, Lee 2009)" % "/".join("%.0f" % v for v in sp),
        None, all(50.5 <= v <= 55.5 for v in sp) and max(sp[1:3]) >= max(sp[0], sp[3]))
    sp = spans(0.0)
    chk("Grip", "REST", "span index/middle/ring/little %s mm (opens as the trigger rests)" % "/".join("%.0f" % v for v in sp), None, max(sp) < 68)
    neck = 2 * math.sqrt((DF / 2) ** 2 - (min(b - a for a, b in zip(PIV, PIV[1:])) / 2) ** 2)
    chk("Pivot", "ALL", "pin can't slide between lobes (neck vs 0.250 pin)", neck, neck < DF - 0.04)
    lobes = shapely.ops.unary_union([hole(P[0], P[1] + dz, DF) for dz in PIV])
    web = min(lobes.distance(Polygon(frame.exterior).exterior), Point(S[0], S[1]).buffer(0.30).distance(lobes))
    chk("Pivot", "ALL", "metal from the pivot lobes to the edge and the up-stop slot", web, web > 0.09)
    for dz in PIV:
        P2 = (P[0], P[1] + dz)
        for st, ang in (("REST", 0.0), ("FULL", -math.degrees(BT / NOSE))):
            t = affinity.rotate(affinity.translate(trigger, *P2), ang, origin=P2).union(
                affinity.rotate(affinity.translate(trig_sleeve, *P2), ang, origin=P2))
            rows.setdefault((st, "clears the tabs + clips"), []).append(
                (min(t.distance(g) for g in tab_geoms + pins), min(t.distance(g) for g in tab_geoms + pins) > 0.1))
    for (st, what), vals in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0] != "REST")):
        checks.append(("Trigger", st, what + " (pivot lobe 1/2/3/4)", " / ".join("%.2f" % v for v, _ in vals) + '"',
                       "PASS" if all(ok for _, ok in vals) else "FAIL"))

    # v0.7: two can positions. Ring in the SEAT (tabs in the seat slots) or ring in the BIG HOLE (tabs in the
    # 2nd holes, so the handle and trigger sit 0.80" toward the keeper). Plan view, at keeper height (z 0..0.125).
    def footprint(g, dy, y0, y1, z0=0.0, z1=0.145):
        band = g.intersection(box(-10, z0, 10, z1))
        if band.is_empty:
            return None
        bx = band.bounds
        return box(bx[0], y0 + dy, bx[2], y1 + dy)
    MODES = (("SEAT", 0.0, 0.0), ("BIG HOLE", -BIG, BIG))   # name, handle shift in y, keeper offset when locked
    for name, dy, k_lock in MODES:
        ring = Point(0, dy).buffer(RING, 64)
        frame_p = footprint(frame, dy, 0.095, 0.22)
        frame_hi = footprint(frame, dy, 0.095, 0.22, 0.0, 0.80)
        trig_ps = []
        for dz in PIV:
            P2 = (P[0], P[1] + dz)
            for ang in (0.0, -math.degrees(BT / NOSE)):
                t = affinity.rotate(affinity.translate(trigger, *P2), ang, origin=P2)
                fp = footprint(t, dy, TY0, TY1)
                if fp is not None:
                    trig_ps.append(fp)
                for side in (1, -1):
                    sc = affinity.rotate(affinity.translate(trig_sleeve, *P2), ang, origin=P2)
                    y0, y1 = (TY1, TY1 + HDPE) if side > 0 else (TY0 - HDPE, TY0)
                    fp = footprint(sc, dy, y0, y1)
                    if fp is not None:
                        trig_ps.append(fp)
        k_closed_m = keeper_at(k_lock)
        tabs_p = [box(x0, FY0 + dy, x1, FY1 + dy) for x0, x1 in TABS]
        slots_m = [tab_slot(x0, x1, ym) for x0, x1, ym in TAB_SLOTS if abs(ym - (FMID + dy)) < 1e-6]
        fit = all(sl.contains(tb) for sl, tb in zip(slots_m, tabs_p))
        play = min(SLOT_W - (FY1 - FY0), min(sl.bounds[2] - tb.bounds[2] for sl, tb in zip(slots_m, tabs_p)))
        chk("Tabs", name, "both tabs drop into their slots (snug, file to fit; play %.3f)" % play, play, fit and play > 0.002)
        web = min(Polygon(collar.exterior).exterior.distance(sl) for sl in slots_m)
        web = min(web, min(sl.distance(Polygon(i)) for sl in slots_m for i in collar.interiors if not Polygon(i).intersects(sl)))
        chk("Tabs", name, "metal left around the slots (to any edge or hole)", web, web > 0.08)
        chk("Tabs", name, "trigger nose sits over the button (handle shift %.2f)" % dy, 0.0, True)
        chk("Keeper", name + " LOCK", "pin hole over the collar hole, posts in the slots", None, pin_free(k_lock) and posts_free(k_lock))
        chk("Keeper", name + " LOCK", "notch reaches the ring", k_closed_m.distance(ring), k_closed_m.distance(ring) < 0.03)
        k_open_m = keeper_at(off_open)
        chk("Keeper", name + " OPEN", "ring clears the keeper", k_open_m.distance(ring), k_open_m.distance(ring) > 0.02)
        trig_p = shapely.ops.unary_union(trig_ps) if trig_ps else None
        for st, kk in (("LOCK", k_closed_m), ("OPEN", k_open_m)):
            others = {"handle plate": frame_p, "trigger + sleeve": trig_p}
            for what, gg in others.items():
                if gg is None:
                    continue
                d = kk.distance(gg)
                chk("Keeper", name + " " + st, "clears the " + what, d, d > 0.05)
        d = frame_hi.distance(ring.union(Point(0, dy).buffer(0.33, 32)))
        chk("Handle", name, "handle plate clears the ring and button", d, d > 0.05)
    for c in checks:
        print(*c)
    print("FAIL" if any(c[4] == "FAIL" for c in checks) else "ok")
