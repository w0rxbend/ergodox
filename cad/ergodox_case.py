# SPDX-License-Identifier: GPL-3.0-or-later
"""
ErgoDox EZ replica case for CNC aluminium milling (build123d, parametric).

Two parts per half:
  * TOP    - shell with integrated 1.5 mm switch plate in a recessed key well,
             perimeter walls, TRRS/USB notches, PCB clamp bosses, tent-leg detent bosses.
  * BOTTOM - tray: floor + low walls + PCB support posts, countersunk M2.5 holes.

Coordinate sources
  * Switch centres / thumb cluster / PCB mounting holes / jack positions:
    original ErgoDox PCB (Fredrik Atmer, GPLv3), github.com/bishboria/ErgoDox,
    "ErgoDOX pcb/ErgoDOX.kicad_pcb". The ErgoDox EZ (PCB-P2295) keeps the same
    key matrix; its bottom-screw pattern, TRRS and USB positions were checked
    against photos and match the original within photo accuracy (~1-4 mm).
  * Case outline, LED/reset positions: measured from top/bottom photos of an
    ErgoDox EZ, scaled by the 19.05 mm key pitch.

All layout numbers below are in the KiCad frame of the RIGHT half
(x -> outer/right, y -> down/towards user, mm). The left half is the mirror.
"""
from __future__ import annotations

import math
import os
import sys

from build123d import (
    Align, Axis, Box, Circle, Cylinder, Face, Kind, Location, Mode, Plane, Pos,
    Rectangle, RectangleRounded, Rot, Sketch, Solid, Vector, chamfer, export_step,
    export_stl, extrude, fillet, offset, Polyline, make_face, Compound, Sphere,
)

# --------------------------------------------------------------------------
# Parameters (mm)
# --------------------------------------------------------------------------
PITCH = 19.05

# Vertical stack, Z = 0 at the bottom face of the case
FLOOR_T = 3.0            # bottom tray floor thickness
Z_SPLIT = 7.0            # top/bottom parting plane == PCB bottom face
PCB_T = 1.6
Z_PCB_TOP = Z_SPLIT + PCB_T                    # 8.6
PLATE_T = 1.5                                  # Cherry MX plate thickness
Z_PLATE_BOT = Z_PCB_TOP + 5.0 - PLATE_T        # 12.1 (MX: plate top 5.0 above PCB top)
Z_PLATE_TOP = Z_PLATE_BOT + PLATE_T            # 13.6
WELL_DEPTH = 4.0                               # key well depth below top surface
Z_TOP = Z_PLATE_TOP + WELL_DEPTH               # 17.6
TOP_SKIN = 3.0                                 # material above the component pocket
Z_POCKET_CEIL = Z_TOP - TOP_SKIN               # 14.6 (>= 6 mm above PCB for TRRS/USB)

WALL = 3.0               # perimeter wall thickness
TOP_EDGE_FILLET = 1.5    # rounded top outer edge
SEAM_CHAMFER = 0.5       # small chamfer on both sides of the parting line
TOOL_R = 1.0             # min internal corner radius of pockets (2 mm end mill)

SWITCH_CUT = 14.0        # MX plate cutout
SWITCH_CUT_R = 0.5       # corner radius (use a 1 mm tool, or switch DOGBONES on)
DOGBONES = False
WELL_CLEAR = 0.6         # well clearance around each key cell
STABILIZERS = False      # plate-mount Cherry stab cutouts on the two 2u thumb keys

# Case outline (KiCad frame, right half), measured from photos
CASE_X_IN = 55.6         # inner (thumb side) edge
CASE_X_OUT = 210.6       # outer edge
CASE_Y_TOP = 27.1        # back edge (1.5 mm more room for the jacks and back-strip parts)
CASE_Y_BOT = 158.6       # front edge of the main body
THUMB_MARGIN = 5.5       # case margin around thumb key cells
R_TOP_CORNERS = 10.0
R_FRONT_OUTER = 12.0
R_THUMB = 8.0
R_CONCAVE_TOP = 6.0      # where main body meets thumb, back side
R_CONCAVE_FRONT = 14.0   # where main body meets thumb, front side

# Fasteners
SCREW_CLEAR_D = 2.9      # M2.5 clearance
SCREW_CSK_D = 5.2        # ISO 10642 M2.5 head (90 deg)
TAP_D = 2.05             # M2.5 tap drill
TAP_DEPTH = 6.0          # thread depth into top bosses (bezel area)
TAP_DEPTH_PLATE = 3.9    # for bosses under the plate (leaves ~1.1 mm skin)
BOSS_D = 6.5
POST_D = 6.5

# Tent / tilt legs: reuses the stock EZ legs and their spring thumbscrews (M3). The stock
# bracket is not used: the M3 thread is tapped into the wall and a pad behind it, and a
# toothed boss on the outside of the wall replaces the bracket nut's detent face. The
# leg hub's radial teeth mesh with it. See docs/legs.md.
LEG_Z = 12.0             # thread axis; the Ø10 boss then spans Z 7.0-17.0 on the top part
LEG_TAP_D = 2.5          # M3 tap drill
LEG_DEPTH = 6.0          # max drill depth from the boss face
LEG_PAD = (10.0, 6.0)    # pad (along wall, into case) behind the wall
LEG_BOSS_D = 10.0        # detent boss on the outer wall face
LEG_BOSS_H = 1.2         # boss height above the wall face (tooth tips)
LEG_TEETH = 36           # radial detent teeth (stock: 10 deg steps) - count yours
LEG_TOOTH_R0 = 2.2       # teeth run from this radius to the boss edge
LEG_TOOTH_ANGLE = 90.0   # included angle of the V teeth
# Custom CNC leg (replaces the stock leg; reuses the stock M3 spring thumbscrew). Hub and
# arm sizes are from caliper photos of the stock leg. The hub teeth are the exact negative
# of the boss teeth above, so the pair always meshes. See docs/legs.md.
LEG_HUB_D = 10.4         # stock: 10.4-10.5
LEG_HUB_L = 8.0          # hub length along the screw, toothed face to spring face
LEG_HOLE_D = 3.4         # M3 clearance
LEG_CBORE = (6.5, 4.0)   # spring counterbore in the outer face (diameter, depth)
LEG_ARM_W = 7.5          # arm width in the swing plane at the hub (stock ~7.5)
LEG_ARM_T = 6.0          # arm thickness along the screw, flush with the spring face
LEG_NECK_D = 6.0         # round neck behind the foot cap (= arm width there)
LEG_LEN = 47.0           # pivot to foot tip, cap fitted
LEG_FOOT_D = 9.0         # foot cap outside diameter
LEG_CAP_L = 8.5          # foot cap length (Ø9 cylinder + dome)
LEG_SPIGOT = (4.5, 5.0)  # spigot for the cap (diameter, length)
LEG_EDGE = 0.3           # edge chamfer on the hub

# Rubber feet recesses
FOOT_D = 10.5
FOOT_DEPTH = 0.6

# --------------------------------------------------------------------------
# Layout (original ErgoDox PCB, right half, KiCad frame)
# --------------------------------------------------------------------------
# (x, y, cap_w_u, cap_h_u, rot_deg_ccw_screen)
KEYS: list[tuple[float, float, float, float, float]] = []
for y in (67.0052, 86.05266, 105.10266, 124.15266):
    KEYS.append((186.69 + 4.7625, y, 1.5, 1.0, 0))       # outer 1.5u column
KEYS.append((186.69, 143.20266, 1, 1, 0))
for x, ys in (
    (167.64, (67.0052, 86.05266, 105.10266, 124.15266, 143.20266)),
    (148.59, (63.82766, 82.87766, 101.92766, 120.97766, 140.02766)),
    (129.54, (62.23, 81.28, 100.33, 119.38, 138.43)),
    (110.49, (63.82766, 82.87766, 101.92766, 120.97766, 140.02766)),
    (91.44, (65.1002, 84.14766, 103.19766, 122.24766)),
):
    for y in ys:
        KEYS.append((x, y, 1, 1, 0))
KEYS.append((72.39, 65.1002, 1, 1, 0))
KEYS.append((72.39, 88.91016, 1, 1.5, 0))                   # 1.5u vertical
KEYS.append((72.39, 117.48516, 1, 1.5, 0))

THUMB_ANGLE = 25.0
THUMB_O = (34.69894, 143.2687)
_c, _s = math.cos(math.radians(THUMB_ANGLE)), math.sin(math.radians(THUMB_ANGLE))
U = (_c, -_s)            # along thumb rows (screen: right & up)
V = (_s, _c)             # along thumb columns (screen: right & down)


def thumb_pt(u: float, v: float) -> tuple[float, float]:
    return (THUMB_O[0] + PITCH * (u * U[0] + v * V[0]),
            THUMB_O[1] + PITCH * (u * U[1] + v * V[1]))


THUMB_KEYS = [(0, 0, 1, 1), (1, 0, 1, 1), (0, 1, 1, 1), (0, 2, 1, 1),
              (1, 1.5, 1, 2), (2, 1.5, 1, 2)]
for u, v, w, h in THUMB_KEYS:
    KEYS.append((*thumb_pt(u, v), w, h, THUMB_ANGLE))

assert len(KEYS) == 38

# PCB mounting holes (original ErgoDox, also the EZ bottom-screw pattern)
_H = (50.8, 177.8)
SCREWS = [(_H[0] + dx, _H[1] + dy) for dx, dy in (
    (3.0988, -11.9634), (8.8646, -56.134), (54.6354, -20.0406),
    (150.9776, -37.7444), (88.2396, -86.2076), (150.3426, -140.6652),
    (67.4116, -140.6652), (16.6116, -140.6652))]

# Jacks on the back edge (x position, opening width, opening top Z)
TRRS = (86.3092, 8.0, 15.0)
USB = (137.6426, 12.0, 15.0)            # right half only
LEDS = [(147.7, 43.0), (151.8, 43.0), (155.9, 43.0)]   # right half only
LED_D = 1.8
RESET = (190.9, 42.6)                   # right half only
RESET_D = 1.5
# Radial electrolytic capacitor lying on its side on the PCB top, in the back strip, leads bent
# towards the outer edge. Measured from top-side photos of the EZ PCBs (images/pcb, about
# ±1 mm). The two PCBs differ, so each half has its own position and pocket.
#   left:  above the 3rd column from the outer edge, x 140.8-152.4 (photo 3)
#   right: just inward of the screw at (118.2, 37.1), x 115.6-126.7 (photo 18-49-10 #2)
# Each pocket fills the back strip between pocket_x, from the back wall to the key-well wall,
# keeps the PCB screw bosses, and leaves CAP_SKIN under the cosmetic top face.
CAPS = {
    True: dict(pos=(121.15, 45.1), size=(11.1, 7.0), pocket_x=(109.0, 131.0)),     # right half
    False: dict(pos=(146.6, 39.35), size=(11.6, 6.1), pocket_x=(124.5, 167.0)),    # left half
}                        # size: length along the back wall (body + leads) x body diameter
CAP_H = 6.5              # max part height above the PCB top (lying body + margin)
CAP_CLEAR = 1.0          # min clearance around it inside the pocket
CAP_SKIN = 1.5

# Tent leg positions, as on the stock EZ (measured from photos, ±2 mm)
LEG_MAIN_Y = 64.0        # outer and inner main walls
LEG_THUMB_V = 0.56       # along the thumb-cluster end wall, in key units

# Feet (KiCad frame)
FEET = [(68.0, 45.0), (198.0, 45.0), (198.0, 150.0), (45.0, 178.0)]

# --------------------------------------------------------------------------
# helpers: KiCad frame -> CAD frame (X right, Y up), centred-ish at origin
# --------------------------------------------------------------------------
OX, OY = 130.0, 100.0


def P(x: float, y: float) -> tuple[float, float]:
    return (x - OX, -(y - OY))


def cad_rot(deg_screen: float) -> float:
    # KiCad rotation (screen CCW with y down) == CAD CCW with y up
    return deg_screen


# --------------------------------------------------------------------------
# 2D geometry
# --------------------------------------------------------------------------
def outline_face() -> Face:
    """Outer case outline with filleted corners."""
    x0, y0 = P(CASE_X_IN, CASE_Y_BOT)
    x1, y1 = P(CASE_X_OUT, CASE_Y_TOP)
    main = Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)

    # Thumb block: key cells + margin, extended towards the main body
    u0, u1 = -0.5 * PITCH - THUMB_MARGIN, 2.5 * PITCH + 60.0
    v0, v1 = -0.5 * PITCH - THUMB_MARGIN, 2.5 * PITCH + THUMB_MARGIN
    cu, cv = (u0 + u1) / 2 / PITCH, (v0 + v1) / 2 / PITCH
    cx, cy = P(*thumb_pt(cu, cv))
    thumb = Pos(cx, cy) * Rot(0, 0, THUMB_ANGLE) * Rectangle(u1 - u0, v1 - v0)

    sk = Sketch() + [main, thumb]
    face = sk.faces()[0]
    # Fillet: classify vertices as convex/concave by testing a probe point
    verts = face.vertices()
    convex_main_back = []
    rad_map = []
    for vx in verts:
        p = Vector(vx.X, vx.Y)
        # concave vertex if a tiny circle around it is mostly inside
        inside = sum(face.is_inside(p + Vector(math.cos(a), math.sin(a)) * 0.3)
                     for a in [i * math.pi / 4 for i in range(8)])
        concave = inside > 4
        kx, ky = p.X + OX, -p.Y + OY
        if concave:
            r = R_CONCAVE_TOP if ky < 130 else R_CONCAVE_FRONT
        elif ky < 60:
            r = R_TOP_CORNERS
        elif abs(kx - CASE_X_OUT) < 1:
            r = R_FRONT_OUTER
        else:
            r = R_THUMB
        rad_map.append((vx, r))
    for r in sorted({r for _, r in rad_map}):
        vs = [v for v, rr in rad_map if rr == r]
        # vertices change after each fillet -> re-find by position
        cur = []
        for v in vs:
            cur.append(min(face.vertices(),
                           key=lambda w: (w.X - v.X) ** 2 + (w.Y - v.Y) ** 2))
        face = fillet(cur, r)
        if not isinstance(face, Face):
            face = face.faces()[0]
    return face


def key_cell(x, y, w, h, rot, grow) -> Face:
    cx, cy = P(x, y)
    return (Pos(cx, cy) * Rot(0, 0, cad_rot(rot)) *
            Rectangle(w * PITCH + 2 * grow, h * PITCH + 2 * grow)).faces()[0]


def _cell_poly(x, y, w, h, rot, grow):
    from shapely.geometry import box
    from shapely.affinity import rotate, translate
    cx, cy = P(x, y)
    b = box(-(w * PITCH) / 2 - grow, -(h * PITCH) / 2 - grow,
            (w * PITCH) / 2 + grow, (h * PITCH) / 2 + grow)
    return translate(rotate(b, cad_rot(rot), origin=(0, 0)), cx, cy)


def _filleted_polygon_face(coords, radius: float) -> Face:
    """Straight-edged polygon -> Face with convex corners filleted (pocket tool radius)."""
    face = make_face(Polyline(*coords, close=True))
    convex = []
    n = len(coords)
    area2 = sum(coords[i][0] * coords[(i + 1) % n][1] - coords[(i + 1) % n][0] * coords[i][1]
                for i in range(n))
    for i in range(n):
        a, b, c = coords[i - 1], coords[i], coords[(i + 1) % n]
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if cross * area2 > 0:
            convex.append(b)
    verts = [min(face.vertices(), key=lambda v: (v.X - p[0]) ** 2 + (v.Y - p[1]) ** 2)
             for p in convex]
    out = fillet(verts, radius)
    return out if isinstance(out, Face) else out.faces()[0]


def well_face(extra: float = 0.0) -> list[Face]:
    from shapely.ops import unary_union
    polys = [_cell_poly(*k, grow=WELL_CLEAR) for k in KEYS]
    u = unary_union(polys)
    # close slivers between staggered columns, keep sharp (mitred) corners
    u = u.buffer(1.5, join_style="mitre").buffer(-1.5, join_style="mitre")
    if extra:
        u = u.buffer(extra, join_style="mitre")
    u = u.simplify(0.05)
    geoms = list(u.geoms) if hasattr(u, "geoms") else [u]
    faces = []
    for g in geoms:
        coords = list(g.exterior.coords)[:-1]
        faces.append(_filleted_polygon_face(coords, TOOL_R))
    return faces


def switch_cut(x, y, rot) -> Sketch:
    cx, cy = P(x, y)
    if DOGBONES:
        s = Rectangle(SWITCH_CUT, SWITCH_CUT)
        d = SWITCH_CUT / 2 - 0.5 * 0.7071
        for sx in (-1, 1):
            for sy in (-1, 1):
                s += Pos(sx * d, sy * d) * Circle(0.5)
    else:
        s = RectangleRounded(SWITCH_CUT, SWITCH_CUT, SWITCH_CUT_R)
    return Pos(cx, cy) * Rot(0, 0, cad_rot(rot)) * s


def stab_cuts(x, y, rot) -> Sketch:
    """Cherry plate-mount stab for a vertical 2u key (wire across u)."""
    cx, cy = P(x, y)
    s = Sketch()
    for sv in (-1, 1):
        s += Pos(0.58, sv * 11.938) * Rectangle(12.3, 6.65)
    return Pos(cx, cy) * Rot(0, 0, cad_rot(rot)) * s


# --------------------------------------------------------------------------
# 3D parts
# --------------------------------------------------------------------------
def prism(face_or_sketch, z0: float, z1: float) -> Solid:
    return extrude(Plane.XY.offset(z0) * face_or_sketch, amount=z1 - z0)


def clearance_report(r_boss: float) -> list[str]:
    out = []
    for i, (sx, sy) in enumerate(SCREWS):
        worst = 1e9
        for kx, ky, w, h, rot in KEYS:
            # distance from screw centre to switch housing square (15.6 incl. clips)
            a = math.radians(rot)
            dx, dy = sx - kx, sy - ky
            # rotate into key frame (screen coords, y down)
            lu = dx * math.cos(a) - dy * math.sin(a)
            lv = dx * math.sin(a) + dy * math.cos(a)
            ex = max(abs(lu) - 7.8, 0)
            ey = max(abs(lv) - 7.8, 0)
            worst = min(worst, math.hypot(ex, ey))
        out.append((i, sx, sy, worst))
    return out


def boss_radius(sx, sy) -> float:
    d = [w for i, x, y, w in clearance_report(0) if (x, y) == (sx, sy)][0]
    return max(min(BOSS_D / 2, d - 0.3), TAP_D / 2 + 1.0)


def screw_under_plate(sx, sy, well: list[Face]) -> bool:
    return any(f.is_inside(Vector(*P(sx, sy))) for f in well)


def leg_mounts():
    """(cad point on outer surface, outward unit normal) for 3 legs."""
    legs = [
        (P(CASE_X_OUT, LEG_MAIN_Y), (1.0, 0.0)),
        (P(CASE_X_IN, LEG_MAIN_Y), (-1.0, 0.0)),
    ]
    u = -0.5 * PITCH - THUMB_MARGIN
    tx, ty = P(*thumb_pt(u / PITCH, LEG_THUMB_V))
    a = math.radians(THUMB_ANGLE)
    legs.append(((tx, ty), (-math.cos(a), -math.sin(a))))
    return legs


def _leg_frame(px, py, nx, ny, shape):
    """Place a shape built in the wall-local frame (X = inward depth from the outer
    face, Y = along the wall, Z = absolute) at a leg position."""
    return Pos(px, py, 0) * Rot(0, 0, math.degrees(math.atan2(-ny, -nx))) * shape


def _in_housing(x: float, y: float, margin: float) -> bool:
    """KiCad-frame point inside any switch housing (15.6 mm square incl. clips)?"""
    for kx, ky, w, h, rot in KEYS:
        a = math.radians(rot)
        dx, dy = x - kx, y - ky
        lu = dx * math.cos(a) - dy * math.sin(a)
        lv = dx * math.sin(a) + dy * math.cos(a)
        if abs(lu) < 7.8 + margin and abs(lv) < 7.8 + margin:
            return True
    return False


def leg_pad_depth(px, py, nx, ny) -> float:
    """Inward pad depth behind the wall that stays clear of switch housings."""
    tx, ty = -ny, nx
    depth = 0.0
    while depth < LEG_PAD[1]:
        d = WALL + depth + 0.25
        hit = False
        for t in (-LEG_PAD[0] / 2, 0.0, LEG_PAD[0] / 2):
            cx, cy = px - nx * d + tx * t, py - ny * d + ty * t
            if _in_housing(cx + OX, -cy + OY, 0.5):
                hit = True
        if hit:
            break
        depth += 0.25
    return depth


def leg_hole_depth(px, py, nx, ny, well: list[Face]) -> float:
    """Tap drill depth from the boss face: inside the pad, and stopped short of the key
    well when the thread would pass just under the well floor."""
    depth = LEG_BOSS_H + WALL + leg_pad_depth(px, py, nx, ny) - 0.5
    if LEG_Z + 1.5 > Z_PLATE_TOP - 0.5:
        d = 0.0
        while d < depth and not any(f.is_inside(Vector(px - nx * d, py - ny * d)) for f in well):
            d += 0.1
        depth = min(depth, LEG_BOSS_H + d - 0.3)
    return min(LEG_DEPTH, depth)


def tooth_k() -> float:
    """Tooth height / radius of the radial V teeth (sharp V, full pitch)."""
    return math.tan(math.pi / LEG_TEETH) / math.tan(math.radians(LEG_TOOTH_ANGLE) / 2)


def detent_grooves(r_out: float, z_tip: float) -> list:
    """LEG_TEETH V-groove solids, axis +Z, tip plane at z_tip, apex lines meeting the axis in
    the tip plane. Cut from the boss they make its teeth; added to the leg hub they make
    its teeth, so the hub is the exact negative of the boss."""
    from build123d import loft
    half, k = math.pi / LEG_TEETH, tooth_k()
    grooves = []
    for i in range(LEG_TEETH):
        secs = []
        for r in (LEG_TOOTH_R0, r_out):
            w = r * math.tan(half)
            pts = [(r, -w, z_tip + 0.01), (r, w, z_tip + 0.01), (r, 0, z_tip - r * k)]
            secs.append(make_face(Polyline(*pts, close=True)))
        grooves.append(Rot(0, 0, i * 360 / LEG_TEETH) * loft(secs))
    return grooves


def detent_boss() -> Solid:
    """Toothed boss in a local frame: axis along +Z, wall face at Z = 0, tooth tips at
    LEG_BOSS_H. V grooves with apexes on the axis, like the stock nut (Hirth-style)."""
    r1 = LEG_BOSS_D / 2
    boss = Pos(0, 0, -WALL / 2) * Cylinder(r1, WALL / 2 + LEG_BOSS_H,
                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
    boss -= detent_grooves(r1 + 0.3, LEG_BOSS_H)
    # flat land inside the teeth at root depth, so the hub seats on the teeth only
    root = LEG_TOOTH_R0 * tooth_k()
    boss -= Pos(0, 0, LEG_BOSS_H - root) * Cylinder(LEG_TOOTH_R0, 1,
                                                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    return boss


def cap_pocket(right: bool) -> Face:
    """Pocket outline (part frame, right-half coordinates) for one half: the back strip between
    pocket_x, inside the wall and WALL / 2 + 0.5 away from the key well, around the PCB screw
    bosses, convex corners rounded to the tool radius."""
    cap = CAPS[right]
    inner = offset(outline_face(), -WALL, kind=Kind.ARC).faces()[0]
    (xa, ya), (xb, yb) = P(cap["pocket_x"][0], CASE_Y_TOP - 5), P(cap["pocket_x"][1], CASE_Y_TOP + 40)
    s = Sketch() + inner
    s &= Pos((xa + xb) / 2, (ya + yb) / 2) * Rectangle(abs(xb - xa), abs(yb - ya))
    for wf in well_face(extra=WALL / 2 + 0.5):
        s -= wf
    for sx, sy in SCREWS:
        s -= Pos(*P(sx, sy)) * Circle(boss_radius(sx, sy))
    s = offset(offset(s, -TOOL_R, kind=Kind.ARC), TOOL_R, kind=Kind.ARC)
    c = Vector(*P(*cap["pos"]))
    return next(f for f in s.faces() if f.is_inside(c))


def cap_check():
    """Each capacitor (plus CAP_CLEAR) must sit inside its pocket, clear of the PCB bosses."""
    ceil = Z_TOP - CAP_SKIN
    for right, cap in CAPS.items():
        pocket = cap_pocket(right)
        c = Vector(*P(*cap["pos"]))
        w, h = cap["size"][0] / 2 + CAP_CLEAR, cap["size"][1] / 2 + CAP_CLEAR
        edge = [c + Vector(w * u, h * v) for u in (-1, -0.5, 0, 0.5, 1) for v in (-1, 1)]
        if not all(pocket.is_inside(p) for p in edge):
            sys.exit(f"{'right' if right else 'left'} capacitor (plus clearance) does not fit in its pocket")
        for sx, sy in SCREWS:
            b = Vector(*P(sx, sy))
            dx, dy = max(abs(b.X - c.X) - w, 0), max(abs(b.Y - c.Y) - h, 0)
            if math.hypot(dx, dy) < boss_radius(sx, sy):
                sys.exit(f"capacitor clearance hits the PCB boss at ({sx:.1f},{sy:.1f})")
        bb = pocket.bounding_box()
        print(f"  {'right' if right else 'left '} capacitor {cap['size'][0]}x{cap['size'][1]} at "
              f"{cap['pos']}: pocket x {bb.min.X + OX:.1f}-{bb.max.X + OX:.1f}, "
              f"y {OY - bb.max.Y:.1f}-{OY - bb.min.Y:.1f}, area {pocket.area:.0f} mm2, ceiling {ceil:.1f} "
              f"= {ceil - Z_PCB_TOP:.1f} above PCB (skin {CAP_SKIN})")


def leg_check():
    """Each boss and pad must sit on a straight wall, inside the top part."""
    if LEG_Z - LEG_BOSS_D / 2 < Z_SPLIT - 1e-6 or LEG_Z + LEG_BOSS_D / 2 > Z_TOP:
        sys.exit("tent-leg boss does not fit between the parting plane and the top")
    outline = outline_face()
    well = well_face()
    half = max(LEG_PAD[0], LEG_BOSS_D) / 2 + 0.5
    for (px, py), (nx, ny) in leg_mounts():
        tx, ty = -ny, nx
        for t in (-half, half):
            qx, qy = px + tx * t, py + ty * t
            on_wall = (outline.is_inside(Vector(qx - nx * 0.05, qy - ny * 0.05)) and
                       not outline.is_inside(Vector(qx + nx * 0.05, qy + ny * 0.05)))
            if not on_wall:
                sys.exit(f"tent leg at ({px + OX:.1f},{-py + OY:.1f}) runs off its straight wall")
        print(f"  tent leg at ({px + OX:6.1f},{-py + OY:6.1f}): pad depth {leg_pad_depth(px, py, nx, ny):4.2f}"
              f"  M3 drill depth {leg_hole_depth(px, py, nx, ny, well):4.2f} mm from boss face")


def build_top(right: bool) -> Solid:
    outline = outline_face()
    inner = offset(outline, -WALL, kind=Kind.ARC).faces()[0]
    well = well_face()

    body = prism(outline, Z_SPLIT, Z_TOP)
    body = fillet(body.edges().group_by(Axis.Z)[-1], TOP_EDGE_FILLET)
    body = chamfer(body.edges().group_by(Axis.Z)[0], SEAM_CHAMFER)

    # main cavity below the plate
    body -= prism(inner, Z_SPLIT - 1, Z_PLATE_BOT)
    # component / weight-relief pocket above, kept away from the well
    relief = Sketch() + inner
    for wf in well_face(extra=WALL / 2 + 0.5):
        relief -= wf
    for f in relief.faces():
        if f.area > 4:
            body -= prism(f, Z_PLATE_BOT - 0.01, Z_POCKET_CEIL)
    # key well
    for wf in well:
        body -= prism(wf, Z_PLATE_TOP, Z_TOP + 1)
    # switch cutouts through the plate
    for kx, ky, w, h, rot in KEYS:
        body -= prism(switch_cut(kx, ky, rot), Z_PLATE_BOT - 1, Z_PLATE_TOP + 0.01)
        if STABILIZERS and h == 2:
            body -= prism(stab_cuts(kx, ky, rot), Z_PLATE_BOT - 1, Z_PLATE_TOP + 0.01)

    # PCB clamp bosses + tapped holes
    for sx, sy in SCREWS:
        cx, cy = P(sx, sy)
        r = boss_radius(sx, sy)
        under = screw_under_plate(sx, sy, well)
        ceil = Z_PLATE_BOT if under else Z_POCKET_CEIL
        body += Pos(cx, cy, Z_PCB_TOP) * Cylinder(r, ceil - Z_PCB_TOP + 0.01,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))
        depth = TAP_DEPTH_PLATE if under else TAP_DEPTH
        body -= Pos(cx, cy, Z_PCB_TOP - 0.01) * Cylinder(TAP_D / 2, depth,
                                                       align=(Align.CENTER, Align.CENTER, Align.MIN))

    # tent legs: pad behind the wall, toothed detent boss outside, tapped M3 hole
    boss = detent_boss()
    for (px, py), (nx, ny) in leg_mounts():
        pad_d = leg_pad_depth(px, py, nx, ny)
        pad = Pos(0, 0, Z_PCB_TOP + 0.4) * Box(WALL + pad_d, LEG_PAD[0], Z_POCKET_CEIL - Z_PCB_TOP - 0.4,
                                               align=(Align.MIN, Align.CENTER, Align.MIN))
        pad = _leg_frame(px, py, nx, ny, pad) & prism(outline, Z_SPLIT, Z_TOP)
        for wf in well:
            pad -= prism(wf, Z_PLATE_TOP, Z_TOP + 1)
        body += pad
        body += _leg_frame(px, py, nx, ny, Pos(0, 0, LEG_Z) * Rot(0, -90, 0) * boss)
        depth = leg_hole_depth(px, py, nx, ny, well)
        body -= _leg_frame(px, py, nx, ny, Pos(-LEG_BOSS_H - 0.01, 0, LEG_Z) * Rot(0, 90, 0) * Cylinder(
            LEG_TAP_D / 2, depth + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN)))

    # capacitor clearance pocket, 0.5 above the tallest allowed part
    body -= prism(cap_pocket(right), Z_PCB_TOP - 0.01, Z_TOP - CAP_SKIN)

    # jack notches in the back wall (open towards the parting plane)
    yb = P(0, CASE_Y_TOP)[1]
    jacks = [TRRS] + ([USB] if right else [])
    for jx, jw, jz in jacks:
        cx = P(jx, 0)[0]
        body -= Pos(cx, yb, Z_SPLIT - 1) * Box(jw, WALL * 4, jz - Z_SPLIT + 1,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))
    if right:
        for lx, ly in LEDS:
            cx, cy = P(lx, ly)
            body -= Pos(cx, cy, Z_POCKET_CEIL - 1) * Cylinder(
                LED_D / 2, TOP_SKIN + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        cx, cy = P(*RESET)
        body -= Pos(cx, cy, Z_POCKET_CEIL - 1) * Cylinder(
            RESET_D / 2, TOP_SKIN + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body


def build_bottom(right: bool) -> Solid:
    outline = outline_face()
    inner = offset(outline, -WALL, kind=Kind.ARC).faces()[0]
    body = prism(outline, 0, Z_SPLIT)
    body = fillet(body.edges().group_by(Axis.Z)[0], 1.0)
    body = chamfer(body.edges().group_by(Axis.Z)[-1], SEAM_CHAMFER)
    body -= prism(inner, FLOOR_T, Z_SPLIT + 1)
    for sx, sy in SCREWS:
        cx, cy = P(sx, sy)
        r = boss_radius(sx, sy)
        body += Pos(cx, cy, FLOOR_T - 0.01) * Cylinder(
            r, Z_SPLIT - FLOOR_T + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
        body -= Pos(cx, cy, -1) * Cylinder(SCREW_CLEAR_D / 2, Z_SPLIT + 2,
                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
        # 90 deg countersink
        h = (SCREW_CSK_D - SCREW_CLEAR_D) / 2
        body -= Pos(cx, cy, 0) * Solid.make_cone(SCREW_CSK_D / 2 + 0.01, SCREW_CLEAR_D / 2, h + 0.01,
                                                 Plane.XY.offset(-0.01))
    for fx, fy in FEET:
        cx, cy = P(fx, fy)
        body -= Pos(cx, cy, -0.01) * Cylinder(FOOT_D / 2, FOOT_DEPTH + 0.01,
                                             align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body


def build_leg() -> Solid:
    """Custom tent leg, own frame: hub axis +Z, toothed face at Z = 0 with the teeth below
    it (towards the case), spring face at Z = LEG_HUB_L, arm along +Y. One part fits all
    six positions (it is symmetric about the YZ plane)."""
    r = LEG_HUB_D / 2
    hub = Cylinder(r, LEG_HUB_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hub = chamfer(hub.edges().group_by(Axis.Z)[-1], LEG_EDGE)
    zc = LEG_HUB_L - LEG_ARM_T / 2                       # arm flush with the spring face
    y_neck = LEG_LEN - LEG_CAP_L                         # shoulder the foot cap sits on
    neck_l = 4.0
    y1 = y_neck - neck_l
    plan = make_face(Polyline((-LEG_ARM_W / 2, 0), (LEG_ARM_W / 2, 0), (LEG_NECK_D / 2, y1),
                              (-LEG_NECK_D / 2, y1), close=True))
    arm = Pos(0, 0, LEG_HUB_L - LEG_ARM_T) * extrude(plan, LEG_ARM_T)
    arm = fillet([e for e in arm.edges() if abs((e.end_point() - e.start_point()).normalized().Y) > 0.9],
                 min(1.5, LEG_ARM_T / 2 - 0.2))
    neck = Pos(0, y_neck - neck_l, zc) * Rot(-90, 0, 0) * Cylinder(
        LEG_NECK_D / 2, neck_l, align=(Align.CENTER, Align.CENTER, Align.MIN))
    spigot = Pos(0, y_neck, zc) * Rot(-90, 0, 0) * Cylinder(
        LEG_SPIGOT[0] / 2, LEG_SPIGOT[1], align=(Align.CENTER, Align.CENTER, Align.MIN))
    spigot = chamfer(spigot.edges().sort_by(Axis.Y)[-1], 0.4)
    leg = hub + arm + neck + spigot
    leg -= Cylinder(LEG_HOLE_D / 2, 3 * LEG_HUB_L)
    leg -= Pos(0, 0, LEG_HUB_L - LEG_CBORE[1]) * Cylinder(
        LEG_CBORE[0] / 2, LEG_HUB_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    teeth = Pos(0, 0, -2) * Cylinder(r, 2.005, align=(Align.CENTER, Align.CENTER, Align.MIN))
    leg += [teeth & g for g in detent_grooves(r + 0.3, 0.0)]
    return leg


def build_leg_cap() -> Solid:
    """Foot cap (print in TPU), in the leg frame: slides onto the spigot."""
    y0, zc = LEG_LEN - LEG_CAP_L, LEG_HUB_L - LEG_ARM_T / 2
    body_l = LEG_CAP_L - LEG_FOOT_D / 2
    cap = Pos(0, y0, zc) * Rot(-90, 0, 0) * Cylinder(
        LEG_FOOT_D / 2, body_l, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap += Pos(0, y0 + body_l, zc) * Sphere(LEG_FOOT_D / 2)
    cap &= Pos(0, y0, zc) * Box(2 * LEG_FOOT_D, LEG_CAP_L, 2 * LEG_FOOT_D, align=(Align.CENTER, Align.MIN, Align.CENTER))
    cap -= Pos(0, y0 - 0.01, zc) * Rot(-90, 0, 0) * Cylinder(
        LEG_SPIGOT[0] / 2 - 0.1, LEG_SPIGOT[1], align=(Align.CENTER, Align.CENTER, Align.MIN))
    return cap


def leg_parts(swing_deg: float = 90.0) -> list:
    """Legs + caps seated on each detent boss for the assembly preview. swing_deg turns the
    leg about the screw in 10 deg detent steps (90 = straight down, 0 / 180 = along the wall)."""
    leg = build_leg() + build_leg_cap()
    parts = []
    for (px, py), (nx, ny) in leg_mounts():
        seat = Pos(0, 0, LEG_Z) * Rot(0, -90, 0) * Pos(0, 0, LEG_BOSS_H) * Rot(0, 0, swing_deg)
        parts.append(_leg_frame(px, py, nx, ny, seat * leg))
    return parts


def export_fitcheck_dxf(path: str):
    """1:1 top-view drawing (right half): outline, wall, well, switch cutouts,
    PCB screw holes, jacks. Print at 100 % and lay the EZ PCB on it."""
    from build123d import ExportDXF, Unit, LineType
    outline = outline_face()
    inner = offset(outline, -WALL, kind=Kind.ARC).faces()[0]
    dxf = ExportDXF(unit=Unit.MM)
    dxf.add_layer("OUTLINE")
    dxf.add_layer("WALL_INNER", line_type=LineType.DASHED)
    dxf.add_layer("KEY_WELL")
    dxf.add_layer("SWITCH_CUTOUTS")
    dxf.add_layer("SCREWS")
    dxf.add_layer("FEATURES")
    dxf.add_shape(outline.outer_wire(), layer="OUTLINE")
    dxf.add_shape(inner.outer_wire(), layer="WALL_INNER")
    for wf in well_face():
        dxf.add_shape(wf.outer_wire(), layer="KEY_WELL")
    for kx, ky, w, h, rot in KEYS:
        dxf.add_shape(switch_cut(kx, ky, rot).faces()[0].outer_wire(), layer="SWITCH_CUTOUTS")
    for sx, sy in SCREWS:
        dxf.add_shape((Pos(*P(sx, sy)) * Circle(SCREW_CLEAR_D / 2)).faces()[0].outer_wire(), layer="SCREWS")
        dxf.add_shape((Pos(*P(sx, sy)) * Circle(boss_radius(sx, sy))).faces()[0].outer_wire(), layer="SCREWS")
    for x, y in LEDS + [RESET]:
        dxf.add_shape((Pos(*P(x, y)) * Circle(0.9)).faces()[0].outer_wire(), layer="FEATURES")
    cap = CAPS[True]
    dxf.add_shape((Pos(*P(*cap["pos"])) * Rectangle(*cap["size"])).faces()[0].outer_wire(), layer="FEATURES")
    yb = P(0, CASE_Y_TOP)[1]
    for jx, jw, _ in (TRRS, USB):
        dxf.add_shape((Pos(P(jx, 0)[0], yb + WALL / 2) * Rectangle(jw, WALL)).faces()[0].outer_wire(),
                      layer="FEATURES")
    dxf.write(path)


def mirror_x(shape):
    from build123d import mirror
    return mirror(shape, about=Plane.YZ)


def main(outdir: str):
    os.makedirs(outdir, exist_ok=True)
    print("Screw clearances to switch housings (mm):")
    for i, sx, sy, w in clearance_report(0):
        print(f"  #{i} ({sx:7.2f},{sy:7.2f}) clearance {w:5.2f}  boss r {boss_radius(sx, sy):.2f}")
    leg_check()
    cap_check()
    export_fitcheck_dxf(os.path.join(outdir, "ergodox_right_fitcheck.dxf"))
    parts = {}
    for side in ("right", "left"):
        right = side == "right"
        top = build_top(right)
        bot = build_bottom(right)
        if not right:
            top, bot = mirror_x(top), mirror_x(bot)
        parts[f"{side}_top"] = top
        parts[f"{side}_bottom"] = bot
    for name, s in parts.items():
        export_step(s, os.path.join(outdir, f"ergodox_{name}.step"))
        export_stl(s, os.path.join(outdir, f"ergodox_{name}.stl"), tolerance=0.02)
        bb = s.bounding_box()
        print(f"{name:13s} vol {s.volume/1000:7.1f} cm3  mass(6061) {s.volume*2.70e-3:6.0f} g  "
              f"bbox {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}  valid={s.is_valid}  solids={len(s.solids())}")
    leg, cap = build_leg(), build_leg_cap()
    for name, s in (("leg", leg), ("leg_cap", cap)):
        export_step(s, os.path.join(outdir, f"ergodox_{name}.step"))
        export_stl(s, os.path.join(outdir, f"ergodox_{name}.stl"), tolerance=0.01, angular_tolerance=0.1)
        bb = s.bounding_box()
        print(f"{name:13s} vol {s.volume/1000:7.2f} cm3  mass(6061) {s.volume*2.70e-3:6.1f} g  "
              f"bbox {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}  valid={s.is_valid}  solids={len(s.solids())}")
    parts_ok = dict(parts, leg=leg, leg_cap=cap)
    asm = Compound([parts["right_top"], parts["right_bottom"], *leg_parts()])
    export_step(asm, os.path.join(outdir, "ergodox_right_assembly_with_legs.step"))
    export_stl(asm, os.path.join(outdir, "ergodox_right_assembly_with_legs.stl"), tolerance=0.05)
    bad = [name for name, s in parts_ok.items() if not s.is_valid or len(s.solids()) != 1]
    if bad:
        sys.exit(f"invalid geometry: {', '.join(bad)}")
    return parts


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports"))
