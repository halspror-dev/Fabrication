"""v0.96 geometry: cam-lever clamp on the valve cup (carlie picked direction D, 2026-11-01).

Builds on templates.py (v0.95 trigger, printed sleeves, handle-plate outline, pivot lobes, up-stop) and never edits it.
What changed from v0.95:
  - No keyhole keeper, guide posts, lock pin or hitch clips. The collar has a short entry hole and a seat; 2 raised pads
    behind the seat and an over-centre LEVER in front clamp the valve cup (a standard 32.5 mm) from 3 sides, so every can
    sits in the same spot under the trigger nose (no second clip position).
  - The lever's jaw is on a built-in spring arm: it bends about 0.5 mm when the lever snaps shut, so the clamp stays tight
    over print and brand tolerances with nothing to adjust.
  - No tabs in collar slots. The collar has a printed upright flange that bolts flat to the handle plate with 2 screws.
Run:  python3 v096.py      prints every PASS/FAIL check, ends with "ok" or "FAIL".
Units inches; same axes as templates.py (origin = can centre at the collar top, x forward, y left, z up).
"""
import math, os
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely import affinity
import shapely.ops

HERE = os.path.dirname(os.path.abspath(__file__))
g = {}
exec(open(os.path.join(HERE, "templates.py")).read(), g)          # v0.95 parts, read only
hole, slot, rr = g["hole"], g["slot"], g["rounded_rect"]
CT, D7, DF = g["CT"], g["D7"], g["DF"]
FY0, FY1 = g["FY0"], g["FY1"]
MM = 25.4

# ---------------- the can ----------------
CUP_R, CUP_H = 0.64, 0.14      # valve cup 32.5 mm OD (EN 14848: 32.5 +-0.1); v0.96 clamps on it
NECK_R = 0.53                  # neck under the lip, ESTIMATE (27 mm); measure 2-3 brands

# ---------------- collar opening: entry hole + seat ----------------
SEAT_D = 1.18                  # 30.0 mm: necks up to ~29.5 mm fit; the collar reaches 1.25 mm under the lip
ENTRY_D = 1.375                # 34.9 mm (v0.95 big hole): the cup drops straight through
ENTRY_ANG, ENTRY_OFF = -30.0, 0.40   # entry hole sits front-right of the seat; slide 0.40" (10 mm) back into the seat
EC = (ENTRY_OFF * math.cos(math.radians(ENTRY_ANG)), ENTRY_OFF * math.sin(math.radians(ENTRY_ANG)))
opening = hole(0, 0, SEAT_D).union(slot(0, 0, EC[0], EC[1], SEAT_D)).union(hole(EC[0], EC[1], ENTRY_D))

# ---------------- seat pads (raised on the collar, behind the cup) ----------------
PAD_ANGS = (130.0, 230.0)      # contact points on the cup; the lever pushes from 0 deg, so the 3 contacts are 100-130 deg apart
PAD_HALF, PAD_DEPTH, PAD_H = 0.17, 0.24, 0.15


def u(a):
    return (math.cos(math.radians(a)), math.sin(math.radians(a)))


def pad(a):
    n = u(a); t = (-n[1], n[0])
    T = (CUP_R * n[0], CUP_R * n[1])
    p = [(T[0] + s * PAD_HALF * t[0] + d * PAD_DEPTH * n[0], T[1] + s * PAD_HALF * t[1] + d * PAD_DEPTH * n[1])
         for s, d in ((-1, 0), (1, 0), (1, 1), (-1, 1))]
    q = Polygon(p)
    return q.buffer(-0.05, join_style=1).buffer(0.05, join_style=1)   # round the corners
pads = [pad(a) for a in PAD_ANGS]

# ---------------- lever (drawn in its own frame: pivot at the origin, the cup centre at (-RO, 0)) ----------------
RO = 1.35                      # pivot distance in front of the cup centre
O = (RO, 0.0)                  # pivot, world
LT = 0.15                      # lever thickness (3.8 mm print; 19 layers at 0.20)
RP = 0.15                      # jaw pad radius (convex, so it rolls on the cup)
DELTA0 = 0.030                 # jaw pad interference at dead centre (0.76 mm), taken by the spring arm
THETA_S = 8.0                  # closed: 8 deg past dead centre, on the stop
THETA_OPEN = -85.0             # open: flipped 85 deg (forward)
HUB_R = 0.25
PADC = (CUP_R + RP - DELTA0 - RO, 0.0)        # jaw pad centre, lever frame
ARM_Y0, ARM_Y1 = -0.02, 1.00                  # spring arm: tip (at the pad) .. root (at the bridge)
ARM_IN = (-0.56, -0.57)                       # arm edge toward the cup, (tip, root)
ARM_OUT = (-0.34, -0.22)                      # arm edge toward the tab, (tip, root)
TAB_X, TAB_Y1 = (-0.14, 0.16), 1.45           # rigid tab from the hub out to the thumb pad
THUMB = ((0.02, 1.45), 0.25)                  # thumb pad (centre, radius)
BRIDGE = box(-0.62, ARM_Y1, 0.0, 1.20)        # joins the arm root to the tab
LEVER_HOLE = 0.255                            # turns on the 1/4" shoulder

rigid = Point(0, 0).buffer(HUB_R, 64).union(rr(TAB_X[0], -0.10, TAB_X[1], TAB_Y1, 0.06)).union(
    Point(*THUMB[0]).buffer(THUMB[1], 64)).union(BRIDGE)


def lever_shape(extra=0.0):
    """Lever outline in its own frame; extra (inches) moves the jaw pad toward the cup (print-test variants)."""
    jaw_ = Point(PADC[0] - extra, PADC[1]).buffer(RP, 96)
    arm_ = Polygon([(ARM_IN[0], ARM_Y0), (ARM_OUT[0], ARM_Y0), (ARM_OUT[1], ARM_Y1), (ARM_IN[1], ARM_Y1)])
    arm_ = arm_.union(shapely.ops.unary_union([jaw_, box(ARM_IN[0], -0.08, ARM_OUT[0], 0.08)]).convex_hull)
    lv = arm_.union(rigid).buffer(0.03, join_style=1).buffer(-0.03, join_style=1)
    return lv.difference(Point(0, 0).buffer(LEVER_HOLE / 2, 48)), arm_, jaw_


lever_local, arm, jaw = lever_shape()


def place(geom, th):
    """Lever-frame geometry -> world, lever turned th degrees (0 = dead centre, + = past centre toward the stop)."""
    return affinity.translate(affinity.rotate(geom, th, origin=(0, 0)), *O)


def place_pt(p, th):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    return (O[0] + p[0] * c - p[1] * s, O[1] + p[0] * s + p[1] * c)


lever = lambda th: place(lever_local, th)
lever_closed, lever_open = lever(THETA_S), lever(THETA_OPEN)

# stop post (raised on the collar): the thumb pad's back edge lands on it at THETA_S
STOP_R = 0.12
stop_c = place_pt((THUMB[0][0] - THUMB[1] - STOP_R, THUMB[0][1]), THETA_S)
stop_post = Point(*stop_c).buffer(STOP_R, 48)

# ---------------- collar ----------------
COLLAR_BACK = -1.695           # rear edge, just in front of the handle plate's foot (x -1.70)
collar = shapely.ops.unary_union([
    opening.buffer(0.26, 64),
    rr(COLLAR_BACK, -0.60, -0.20, 0.80, 0.18),
    Point(*O).buffer(0.42, 64),
    lever_closed.buffer(0.06),
    stop_post.buffer(0.10),
] + [p.buffer(0.04) for p in pads])
collar = collar.buffer(0.30, join_style=1).buffer(-0.30, join_style=1)
collar = collar.intersection(box(COLLAR_BACK, -9, 9, 9))
collar = collar.difference(opening).difference(Point(*O).buffer(DF / 2, 48))

# ---------------- handle plate: v0.95 outline, no tabs; 2 flange screw holes ----------------
FL_X, FL_TOP = (-1.69, -0.80), 0.88            # collar flange (upright, against the plate's +y face)
FL_HOLES = ((-1.43, 0.29), (-1.025, 0.65))     # 2 x 10-24 button screws, staggered: under the trigger neck and nose, washers clear
frame = Polygon(g["pts"]).buffer(-0.2, join_style=1).buffer(0.2, join_style=1)
for dz in g["PIV"]:
    frame = frame.difference(hole(g["P"][0], g["P"][1] + dz, DF))
frame = frame.difference(slot(g["S"][0], g["S"][1] + g["SLOT"][0], g["S"][0], g["S"][1] + g["SLOT"][1], D7))
for x, z in list(g["GRIP_HOLES"]) + list(FL_HOLES):
    frame = frame.difference(hole(x, z, D7))
flange = rr(FL_X[0], -0.10, FL_X[1], FL_TOP, 0.08).intersection(box(-9, 0, 9, 9))
for x, z in FL_HOLES:
    flange = flange.difference(hole(x, z, D7))
FL_Y = (FY1, FY1 + CT)                         # flange faces in y

trigger, trig_sleeve = g["trigger"], g["trig_sleeve"]
P, NOSE = g["P"], g["NOSE"]
BT = 0.15                                      # button travel (as v0.95)
E_PETG = 1900.0                                # MPa, PETG ESTIMATE (datasheets 1.8-2.1 GPa)


def arm_spring():
    """Tapered cantilever from the root (ARM_Y1) to the jaw pad (y 0): tip stiffness N/mm and peak stress per N."""
    L = (ARM_Y1 - 0.0) * MM
    t = LT * MM
    n = 400
    s = np.linspace(0, L, n + 1)                      # from the root
    w = ((ARM_OUT[1] - ARM_IN[1]) + ((ARM_OUT[0] - ARM_IN[0]) - (ARM_OUT[1] - ARM_IN[1])) * s / L) * MM
    I = t * w ** 3 / 12
    flex = np.trapezoid((L - s) ** 2 / (E_PETG * I), s)   # mm per N
    stress = np.max(6 * (L - s) / (t * w ** 2))       # MPa per N
    return 1 / flex, stress


def gap_at(th, cup_c=(0.0, 0.0)):
    """Jaw pad gap to the cup (negative = interference) with the lever at th."""
    c = place_pt(PADC, th)
    return math.hypot(c[0] - cup_c[0], c[1] - cup_c[1]) - RP - CUP_R


if __name__ == "__main__":
    out = []

    def chk(part, state, what, val, ok, unit='"'):
        v = "" if val is None else ("%.3f%s (%.2f mm)" % (val, unit, val * MM) if unit == '"' else "%.2f%s" % (val, unit))
        out.append(("PASS" if ok else "FAIL", part, state, what, v))

    cup = lambda c=(0, 0): Point(*c).buffer(CUP_R, 128)
    neck = lambda c=(0, 0): Point(*c).buffer(NECK_R, 128)
    k, s_per_n = arm_spring()
    # --- lever: over-centre clamp ---
    d0, ds = -gap_at(0.0), -gap_at(THETA_S)
    hump = d0 - ds
    chk("Lever", "CLOSED", "jaw squeeze on the cup at the stop (want 0.3-0.7 mm)", ds, 0.3 / MM <= ds <= 0.7 / MM)
    chk("Lever", "CLOSING", "over-centre bump: extra squeeze at dead centre (snap you feel, want >= 0.15 mm)", hump, hump >= 0.15 / MM)
    Fs, F0 = k * ds * MM, k * d0 * MM
    chk("Lever", "CLOSED", "spring arm %.0f N/mm: clamp force at the stop %.0f N (%.1f lbf), want 20-45 N" % (k, Fs, Fs / 4.448), None, 20 <= Fs <= 45)
    chk("Lever", "CLOSING", "arm stress at dead centre %.0f MPa (PETG yield ~50, EST), want <= 25" % (F0 * s_per_n), None, F0 * s_per_n <= 25)
    for tol in (-0.25, 0.25):        # print / cup tolerance on the squeeze, mm
        f = k * (ds * MM + tol)
        ok = f > 8 and k * (d0 * MM + tol) * s_per_n <= 35
        chk("Lever", "TOL %+.2f mm" % tol, "clamp force %.0f N at the stop, dead-centre stress %.0f MPa (still clamps, under 35)" % (f, k * (d0 * MM + tol) * s_per_n), None, ok)
    c = place_pt(PADC, THETA_S)
    F = np.array([c[0], c[1]]) / math.hypot(*c)                     # cup pushes the pad outward along this line
    r = np.array(c) - np.array(O)
    tau = r[0] * F[1] - r[1] * F[0]
    arm_off = abs(tau)
    chk("Lever", "CLOSED", "clamp force pushes the lever INTO its stop (not open): lever arm %.3f\"" % arm_off, None, tau > 0)
    # the thumb pad is on the stop post at THETA_S, and clear of it when open
    th_closed = place(Point(*THUMB[0]).buffer(THUMB[1], 64), THETA_S)
    chk("Lever", "CLOSED", "thumb pad sits on the stop post", th_closed.distance(stop_post), th_closed.distance(stop_post) < 0.002)
    rest = lever_closed.difference(place(jaw.buffer(0.02), THETA_S))
    chk("Lever", "CLOSED", "lever (except the jaw pad) clears the cup", rest.distance(cup()), rest.distance(cup()) >= 0.03)
    chk("Lever", "CLOSED", "lever clears both seat pads", min(lever_closed.distance(p) for p in pads), min(lever_closed.distance(p) for p in pads) >= 0.03)
    other = lever_closed.difference(place(Point(*THUMB[0]).buffer(THUMB[1] + 0.02), THETA_S))
    chk("Lever", "CLOSED", "stop post touches nothing but the thumb pad", other.distance(stop_post), other.distance(stop_post) >= 0.03)
    # the spring arm's slot stays open under the full squeeze
    sl = arm.buffer(-1e-4).distance(rigid.difference(BRIDGE.buffer(0.01)).difference(arm.buffer(0.005)))
    chk("Lever", "CLOSING", "slot beside the spring arm stays open at full bend (slot %.3f, bend %.3f)" % (sl, d0), sl - d0, sl - d0 >= 0.03)
    # opening: once the pad leaves the cup the lever clears the cup's whole slide to the entry hole
    th_free = next(t for t in np.arange(0.0, -40, -0.25) if gap_at(t) > 0)
    chk("Lever", "OPENING", "jaw lets go of the cup %.1f deg before dead centre (flip-open angle %.0f deg)" % (-th_free, THETA_S - THETA_OPEN), None, -th_free < 15)
    path = shapely.ops.unary_union([cup((EC[0] * t, EC[1] * t)) for t in np.linspace(0, 1, 21)])
    chk("Lever", "OPEN", "flipped open: lever clears the cup sliding seat -> entry hole", lever_open.distance(path), lever_open.distance(path) >= 0.03)
    sweep = min(lever(t).distance(cup()) for t in np.arange(-20.0, THETA_OPEN - 0.1, -1.0))
    chk("Lever", "OPENING", "swinging open (20-85 deg) the lever touches nothing on the seated can", sweep, sweep >= 0.03)
    chk("Lever", "OPEN", "flipped open: lever clears the seat pads and stop", min(lever_open.distance(p) for p in pads + [stop_post]),
        min(lever_open.distance(p) for p in pads + [stop_post]) >= 0.03)
    # --- can on and off ---
    chk("Collar", "ON/OFF", "cup drops through the entry hole (side clearance)", ENTRY_D / 2 - CUP_R, ENTRY_D / 2 - CUP_R >= 0.03)
    others = shapely.ops.unary_union(pads + [stop_post, Point(*O).buffer(HUB_R)])
    chk("Collar", "ON/OFF", "cup at the entry hole clears the pads, hub and stop", cup(EC).distance(others), cup(EC).distance(others) >= 0.03)
    for a in PAD_ANGS:
        sep = math.cos(math.radians(a)) * EC[0] + math.sin(math.radians(a)) * EC[1]
        chk("Collar", "ON/OFF", "sliding out, the cup moves away from the %d deg pad (no rubbing)" % a, None, sep <= 1e-9)
    lap = CUP_R - SEAT_D / 2
    chk("Collar", "SEAT", "collar reaches under the lip all round the seat's back half (lip overlap)", lap, lap >= 0.04)
    chk("Collar", "SLIDE", "lip stays over the collar while the can slides (slot narrower than the cup)", CUP_R - SEAT_D / 2, SEAT_D < 2 * CUP_R)
    chk("Collar", "SEAT", "neck clears the seat hole (27 mm neck, EST)", SEAT_D / 2 - NECK_R, SEAT_D / 2 - NECK_R >= 0.03)
    chk("Collar", "SEAT", "biggest neck that fits the seat: %.1f mm (v0.95 seat 28.6)" % (SEAT_D * MM - 0.5), None, SEAT_D * MM - 0.5 > 28.6)
    # lip support arc at the seat: where the collar is under the lip ring (r between SEAT_D/2 and CUP_R)
    angs = [a for a in range(0, 360, 2) if collar.contains(Point(0.5 * (SEAT_D / 2 + CUP_R) * math.cos(math.radians(a)), 0.5 * (SEAT_D / 2 + CUP_R) * math.sin(math.radians(a))))]
    chk("Collar", "SEAT", "collar under the lip around %d deg of the cup (back half, the jaw holds the front)" % (2 * len(angs)), None, 2 * len(angs) >= 175)
    # every cup clamps in the same place (3 contacts), so the trigger nose stays on the button
    shift = 0.1 / MM / math.sin(math.radians(180 - PAD_ANGS[0]))
    chk("Collar", "SEAT", "cup centre moves at most %.2f mm for a +-0.1 mm cup (no second clip position)" % (shift * MM), None, shift * MM < 0.3)
    # --- webs and cutting ---
    web = min(Point(*O).buffer(DF / 2).distance(Polygon(i)) for i in collar.interiors if not Polygon(i).contains(Point(*O)))
    web = min(web, Point(*O).buffer(DF / 2).distance(Polygon(collar.exterior).exterior))
    chk("Collar", "ALL", "metal around the lever pivot hole", web, web >= 0.15)
    ring = Polygon(collar.exterior).exterior.distance(opening)
    chk("Collar", "ALL", "narrowest collar rim around the opening", ring, ring >= 0.20)
    fe = min(min(Point(x, z).buffer(D7 / 2).distance(flange.exterior), Point(x, z).buffer(D7 / 2).distance(Polygon(frame.exterior).exterior)) for x, z in FL_HOLES)
    chk("Flange", "ALL", "flange screw holes to the flange and plate edges", fe, fe >= 0.12)
    (ax_, az_), (bx_, bz_) = FL_HOLES
    sp = math.hypot(bx_ - ax_, bz_ - az_) - 0.50
    chk("Flange", "ALL", "the 2 screws' #10 washers (0.50 OD) and nuts clear each other", sp, sp >= 0.03)
    lowz = min(z for x, z in FL_HOLES) - 0.25
    chk("Flange", "ALL", "lowest washer/nut clears the collar top", lowz, lowz >= 0.03)
    chk("Flange", "ALL", "flange stays behind the plate's front edge and inside the collar", None,
        FL_X[1] <= -0.80 and collar.contains(box(FL_X[0], FL_Y[0], FL_X[1], FL_Y[1])))
    under = frame.intersection(box(-9, -0.01, 9, 0.01))
    chk("Flange", "ALL", "handle plate bottom edge bears on the collar top: %.2f\" long" % under.length, None, under.length > 0.6)
    lw = min(lever_local.exterior.distance(Point(0, 0)) - LEVER_HOLE / 2, 1)
    chk("Lever", "ALL", "metal around the lever's pivot hole", lw, lw >= 0.09)
    mh = min(2 * Polygon(i).exterior.distance(Polygon(i).centroid) for i in frame.interiors if Polygon(i).area < 0.2)
    chk("Cutting", "ALL", "smallest hole in the handle plate vs its 0.125 thickness", mh, mh >= 0.125 - 0.0005)
    # --- trigger (v0.95 trigger, pivot and sleeves unchanged) ---
    noseb = P[1] - 0.45
    chk("Trigger", "REST", "nose bump sits on the button top (0.765), can clamped at the origin", noseb - 0.765, abs(noseb - 0.765) < 0.01)
    for st, ang in (("REST", 0.0), ("FULL", -math.degrees(BT / NOSE))):
        t = affinity.rotate(affinity.translate(trigger, *P), ang, origin=P)
        hd = min(t.distance(Point(x, z).buffer(0.1875)) for x, z in FL_HOLES)
        chk("Trigger", st, "trigger clears the flange screw heads (side view)", hd, hd >= 0.05)
    for row in out:
        print("%-4s %-8s %-11s %-95s %s" % row)
    print("FAIL" if any(r[0] == "FAIL" for r in out) else "ok")
