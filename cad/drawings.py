# SPDX-License-Identifier: GPL-3.0-or-later
"""
Manufacturing drawings (A3 PDF) and the CNC order package for the ErgoDox case.

For every part it writes <part>.pdf next to <part>.step: views generated from the
STEP file, the thread / hole table, general notes and, for the top parts, the detent
boss sheet (tooth count, profile, section). Also writes hole_table.csv.

Usage: drawings.py <exports_dir> <order_dir> [version]
The STEP files must already exist in <exports_dir> (run ergodox_case.py first).
"""
from __future__ import annotations

import csv
import datetime
import math
import os
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Circle as MCircle, Polygon as MPoly, Rectangle as MRect  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ergodox_case as E  # noqa: E402
from build123d import import_step  # noqa: E402

REPO_URL = "https://github.com/w0rxbend/ergodox"
A3 = (420.0, 297.0)
LW = 0.45            # visible edge line width (pt)
FS = 6.0             # base font size (pt)

# view name -> (camera position, up vector, 3D point -> 2D viewport mapping)
VIEWS = {
    "under": ((0, 0, -500), (0, 1, 0), lambda x, y, z: (-x, y)),
    "+X": ((500, 0, 0), (0, 0, 1), lambda x, y, z: (y, z)),
    "-X": ((-500, 0, 0), (0, 0, 1), lambda x, y, z: (-y, z)),
}

TOP_MATERIAL = "Aluminium 6061-T6 (7075-T6 acceptable)"
FINISH = "Fine bead blast + anodize Type II, colour per order"


# --------------------------------------------------------------------------
# hole / feature data (STEP coordinates, mm)
# --------------------------------------------------------------------------
def _mx(right: bool) -> int:
    return 1 if right else -1


def top_threads(right: bool) -> list[dict]:
    m = _mx(right)
    well = E.well_face()
    rows = []
    for i, (sx, sy) in enumerate(E.SCREWS):
        x, y = E.P(sx, sy)
        under = E.screw_under_plate(sx, sy, well)
        depth = E.TAP_DEPTH_PLATE if under else E.TAP_DEPTH
        rows.append(dict(
            id=f"T{i + 1}", thread="M2.5x0.45", hand="RH", cls="6H", drill=E.TAP_D, depth=depth,
            full=round(depth - 0.4, 1), x=m * x, y=y, z=E.Z_PCB_TOP,
            direction="+Z (from PCB face)",
            note=("BLIND under key well: 1.1 mm skin, must not break through" if under else "blind")))
    for j, ((px, py), (nx, ny)) in enumerate(E.leg_mounts()):
        depth = E.leg_hole_depth(px, py, nx, ny, well)
        fx, fy = px + nx * E.LEG_BOSS_H, py + ny * E.LEG_BOSS_H
        rows.append(dict(
            id=f"L{j + 1}", thread="M3x0.5", hand="RH", cls="6H", drill=E.LEG_TAP_D, depth=round(depth, 1),
            full=round(depth - 0.5, 1), x=m * fx, y=fy, z=E.LEG_Z,
            direction=f"normal to wall, into part ({-m * nx:+.3f}, {-ny:+.3f}, 0)",
            note="in toothed detent boss, see sheet 2"))
    return rows


def bottom_holes(right: bool) -> list[dict]:
    m = _mx(right)
    rows = []
    for i, (sx, sy) in enumerate(E.SCREWS):
        x, y = E.P(sx, sy)
        rows.append(dict(id=f"C{i + 1}", feature=f"Ø{E.SCREW_CLEAR_D} THRU, 90° CSK Ø{E.SCREW_CSK_D}",
                         x=m * x, y=y, note="for M2.5 ISO 10642 countersunk screw"))
    for i, (fx, fy) in enumerate(E.FEET):
        x, y = E.P(fx, fy)
        rows.append(dict(id=f"F{i + 1}", feature=f"Ø{E.FOOT_D} x {E.FOOT_DEPTH} deep recess",
                         x=m * x, y=y, note="rubber foot"))
    return rows


# --------------------------------------------------------------------------
# drawing helpers (sheet coordinates in mm, origin bottom-left)
# --------------------------------------------------------------------------
def new_sheet():
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, A3[0])
    ax.set_ylim(0, A3[1])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(MRect((10, 10), A3[0] - 20, A3[1] - 20, fill=False, lw=1.0))
    return fig, ax


def text(ax, x, y, s, size=FS, **kw):
    ax.text(x, y, s, fontsize=size, family="DejaVu Sans", va=kw.pop("va", "top"), **kw)


def title_block(ax, part: str, dwg_no: str, sheet: str, scale: str, version: str, material: str):
    x0, y0, w, h = A3[0] - 190, 10, 180, 42
    ax.add_patch(MRect((x0, y0), w, h, fill=False, lw=0.8))
    for yy in (y0 + 14, y0 + 28):
        ax.plot([x0, x0 + w], [yy, yy], color="k", lw=0.5)
    ax.plot([x0 + 110, x0 + 110], [y0, y0 + 28], color="k", lw=0.5)
    text(ax, x0 + 2, y0 + h - 1.5, "ErgoDox EZ CNC aluminium case", size=10, weight="bold")
    text(ax, x0 + 2, y0 + h - 8, f"{part}   —   {REPO_URL}", size=6.5)
    text(ax, x0 + 2, y0 + 26.5, f"Drawing no.: {dwg_no}", size=7)
    text(ax, x0 + 2, y0 + 21.5, f"Material: {material}", size=6)
    text(ax, x0 + 2, y0 + 17.5, f"Finish: {FINISH}", size=6)
    text(ax, x0 + 112, y0 + 26.5, f"Sheet {sheet}", size=7)
    text(ax, x0 + 112, y0 + 21.5, f"Scale {scale}", size=6)
    text(ax, x0 + 112, y0 + 17.5, "Units: mm", size=6)
    text(ax, x0 + 2, y0 + 12.5, f"Revision {version}   Date {datetime.date.today().isoformat()}", size=6)
    text(ax, x0 + 2, y0 + 8, "General tolerance ISO 2768-mK. Threads ISO metric, RIGHT-HAND, 6H.", size=6)
    text(ax, x0 + 2, y0 + 4, "The STEP file governs geometry; this drawing governs threads, tolerances, finish.",
         size=5.5)
    text(ax, x0 + 112, y0 + 12.5, "Do not scale drawing", size=6)


def place_view(ax, shape, view: str, cx: float, cy: float, scale: float = 1.0, hidden=False):
    """Draw a hidden-line projection centred at (cx, cy); return a 3D->sheet mapper."""
    cam, up, fn = VIEWS[view]
    vis, hid = shape.project_to_viewport(cam, up, (0, 0, 0))
    bb = shape.bounding_box()
    corners = [fn(x, y, z) for x in (bb.min.X, bb.max.X) for y in (bb.min.Y, bb.max.Y)
               for z in (bb.min.Z, bb.max.Z)]
    u0 = (min(c[0] for c in corners) + max(c[0] for c in corners)) / 2
    v0 = (min(c[1] for c in corners) + max(c[1] for c in corners)) / 2

    def to_sheet(u, v):
        return cx + (u - u0) * scale, cy + (v - v0) * scale

    for edges, style in ((vis, dict(color="k", lw=LW)),
                         (hid if hidden else [], dict(color="0.55", lw=0.25, ls=(0, (2, 1.5))))):
        for e in edges:
            n = 2 if "LINE" in str(e.geom_type) else max(8, min(80, int(e.length / 0.4)))
            pts = [e.position_at(i / (n - 1)) for i in range(n)]
            xs, ys = zip(*(to_sheet(p.X, p.Y) for p in pts))
            ax.plot(xs, ys, **style, solid_capstyle="round")
    return lambda x, y, z: to_sheet(*fn(x, y, z))


def label(ax, p, s, dx=5.0, dy=5.0, color="#c00000"):
    x, y = p
    ax.plot([x, x + dx * 0.8], [y, y + dy * 0.8], color=color, lw=0.4)
    ax.add_patch(MCircle((x, y), 0.6, color=color, lw=0))
    text(ax, x + dx, y + dy, s, size=6.5, color=color, weight="bold", va="center",
         ha="left" if dx >= 0 else "right")


def table(ax, x, y, cols, rows, size=5.4, row_h=3.6):
    """cols: [(header, width_mm)], rows: list of lists of str. (x, y) = top-left."""
    w = sum(c[1] for c in cols)
    ax.add_patch(MRect((x, y - row_h * (len(rows) + 1)), w, row_h * (len(rows) + 1), fill=False, lw=0.6))
    cx = x
    for hdr, cw in cols:
        text(ax, cx + 0.8, y - 0.6, hdr, size=size, weight="bold")
        cx += cw
        ax.plot([cx, cx], [y, y - row_h * (len(rows) + 1)], color="k", lw=0.3)
    for r, row in enumerate(rows):
        yy = y - row_h * (r + 1)
        ax.plot([x, x + w], [yy, yy], color="k", lw=0.3 if r else 0.6)
        cx = x
        for (hdr, cw), cell in zip(cols, row):
            text(ax, cx + 0.8, yy - 0.6, str(cell), size=size)
            cx += cw
    return y - row_h * (len(rows) + 1)


def notes(ax, x, y, title, lines, size=6.0, width=95):
    import textwrap
    text(ax, x, y, title, size=7, weight="bold")
    yy = y - 4.5
    for i, line in enumerate(lines, 1):
        wrapped = textwrap.wrap(line, width)
        for k, w in enumerate(wrapped):
            text(ax, x + (0 if k == 0 else 4), yy, (f"{i}. " if k == 0 else "") + w, size=size)
            yy -= size * 0.5
        yy -= 0.8
    return yy


def dim(ax, p1, p2, s, off=(0, 0), size=5.5):
    ax.annotate("", xy=p1, xytext=p2, arrowprops=dict(arrowstyle="<|-|>", lw=0.4, mutation_scale=4,
                                                      shrinkA=0, shrinkB=0, color="k"))
    mx, my = (p1[0] + p2[0]) / 2 + off[0], (p1[1] + p2[1]) / 2 + off[1]
    text(ax, mx, my, s, size=size, ha="center", va="center",
         bbox=dict(facecolor="white", edgecolor="none", pad=0.3))


# --------------------------------------------------------------------------
# sheets
# --------------------------------------------------------------------------
def top_sheet1(pdf, shape, right, part, dwg, version):
    fig, ax = new_sheet()
    to = place_view(ax, shape, "under", 115, 175, 1.0)
    text(ax, 20, 282, "VIEW FROM BELOW (−Z), parting face up — scale 1:1", size=8, weight="bold")
    rows = top_threads(right)
    for r in rows:
        if r["id"].startswith("T"):
            label(ax, to(r["x"], r["y"], r["z"]), r["id"])
        else:
            label(ax, to(r["x"], r["y"], r["z"]), r["id"], dx=-6 if (r["x"] > 0) == right else 6)
    y = table(ax, 222, 283, [("ID", 9), ("Thread", 17), ("Hand", 9), ("Cls", 8), ("Tap drill", 13),
                             ("Drill depth", 15), ("Min full thr.", 16), ("X", 14), ("Y", 14), ("Z", 10),
                             ("Note", 63)],
              [[r["id"], r["thread"], r["hand"], r["cls"], f"Ø{r['drill']}", f"{r['depth']}",
                f"{r['full']}", f"{r['x']:.2f}", f"{r['y']:.2f}", f"{r['z']:.1f}", r["note"]] for r in rows])
    text(ax, 222, y - 1.5, "X/Y/Z = hole start point in STEP coordinates. T holes: drilled +Z from the PCB "
         "face of the boss. L holes: drilled into the part, normal to the wall, from the boss face.", size=5.2)
    tq = sum(1 for r in rows if r["id"].startswith("T"))
    lq = len(rows) - tq
    notes(ax, 222, y - 8, "GENERAL NOTES", [
        f"Geometry per {part}.step. Dimensions not shown are taken from the STEP model.",
        f"Material: {TOP_MATERIAL}.",
        f"THREADS: {tq}x M2.5x0.45-6H and {lq}x M3x0.5-6H, ISO metric coarse, ALL RIGHT-HAND (clockwise to "
        "tighten). Holes are modelled at tap-drill diameter in the STEP; tap them per the table. Use bottoming "
        "taps or thread-forming taps to reach the minimum full-thread depth.",
        ("This is a LEFT-hand part: a mirror image of the right-hand part. Threads stay RIGHT-HAND; do not "
         "mirror the thread direction." if not right else
         "The left-hand part is a mirror image of this part. Its threads are also RIGHT-HAND."),
        "Holes marked BLIND under key well: 1.1 mm of material remains to the cosmetic key-well floor. "
        "Must not break through or leave witness marks on the top surface.",
        "Switch cutouts (38x): 14.00 +0.05/-0 square, corner R0.5 max. Plate thickness 1.50 ±0.05. "
        "Plate flatness 0.2 over the part.",
        "Detent bosses L1-L3 carry 36 radial teeth: see sheet 2. Tooth count is critical.",
        "Cosmetic surfaces: top face, key well, outer walls, detent bosses: no tool marks, scratches or "
        "clamp marks. Inside (cavity) surfaces are non-cosmetic.",
        "Break sharp edges 0.1-0.2 mm, except detent tooth crests and switch-cutout edges (0.1 max).",
        f"Finish: {FINISH}. Mask threads during anodizing, or re-tap after anodizing.",
    ], width=118)
    title_block(ax, part, dwg, "1 of 2", "1:1", version, TOP_MATERIAL)
    pdf.savefig(fig)
    plt.close(fig)


def top_sheet2(pdf, shape, right, part, dwg, version):
    fig, ax = new_sheet()
    rows = [r for r in top_threads(right) if r["id"].startswith("L")]
    # elevations
    for view, cy, title in (("+X", 262, "VIEW FROM +X"), ("-X", 222, "VIEW FROM −X")):
        to = place_view(ax, shape, view, 115, cy, 1.0)
        text(ax, 20, cy + 16, f"{title} — scale 1:1", size=7, weight="bold")
        for r in rows:
            nx = -float(r["direction"].split("(")[1].split(",")[0])     # outward normal x
            if (view == "+X" and nx > 0.5) or (view == "-X" and nx < -0.3):
                label(ax, to(r["x"], r["y"], r["z"]), r["id"], dx=7, dy=9)

    # detail: boss face, 5:1
    s = 5.0
    cx, cy = 70, 120
    r1, r0 = E.LEG_BOSS_D / 2, E.LEG_TOOTH_R0
    ax.add_patch(MCircle((cx, cy), r1 * s, fill=False, lw=0.8))
    ax.add_patch(MCircle((cx, cy), r0 * s, fill=False, lw=0.6))
    ax.add_patch(MCircle((cx, cy), E.LEG_TAP_D / 2 * s, fill=False, lw=0.6))
    th = [math.radians(a) for a in range(0, 271, 6)]                     # 3/4 thread arc
    ax.plot([cx + 1.5 * s * math.cos(t) for t in th], [cy + 1.5 * s * math.sin(t) for t in th], color="k", lw=0.3)
    for i in range(E.LEG_TEETH):
        a = 2 * math.pi * i / E.LEG_TEETH
        ax.plot([cx + r0 * s * math.cos(a), cx + r1 * s * math.cos(a)],
                [cy + r0 * s * math.sin(a), cy + r1 * s * math.sin(a)], color="k", lw=0.35)        # crest
        b = a + math.pi / E.LEG_TEETH
        ax.plot([cx + r0 * s * math.cos(b), cx + r1 * s * math.cos(b)],
                [cy + r0 * s * math.sin(b), cy + r1 * s * math.sin(b)], color="0.5", lw=0.25)      # root
    a10 = 2 * math.pi / E.LEG_TEETH
    for a in (0, a10):
        ax.plot([cx, cx + (r1 + 3) * s * math.cos(a)], [cy, cy + (r1 + 3) * s * math.sin(a)],
                color="#0050a0", lw=0.3, ls="--")
    text(ax, cx + (r1 + 3.2) * s, cy + 2, f"{360 / E.LEG_TEETH:.0f}° pitch", size=6, color="#0050a0", va="center")
    dim(ax, (cx - r1 * s, cy - r1 * s - 5), (cx + r1 * s, cy - r1 * s - 5), f"Ø{E.LEG_BOSS_D:.1f} ±0.1")
    dim(ax, (cx - r0 * s, cy - 4), (cx + r0 * s, cy - 4), f"Ø{2 * r0:.1f}", size=5)
    text(ax, cx, cy + r1 * s + 9, f"DETAIL A — DETENT BOSS L1-L3, face view, scale 5:1  ({E.LEG_TEETH} TEETH)",
         size=7, weight="bold", ha="center")
    ax.plot([cx + 1.2 * s * 0.7, cx - 9 * s * 0.7 - 6], [cy + 1.2 * s * 0.7, cy + r1 * s + 2], color="k", lw=0.3)
    text(ax, cx - 9 * s * 0.7 - 7, cy + r1 * s + 2, "M3x0.5-6H RH\ntap drill Ø2.5", size=5.5, va="center",
         ha="right")

    # section B-B through boss axis, 5:1 (wall-local: u = depth into part, v = Z - LEG_Z)
    ox, oy = 165, 110
    pad_d = E.LEG_PAD[1]

    def P2(u, v):
        return ox + u * s, oy + v * s
    zr = lambda z: z - E.LEG_Z  # noqa: E731
    hatch = dict(fc="#e8ecf2", ec="k", lw=0.6, hatch="////")
    ax.add_patch(MPoly([P2(0, zr(E.Z_SPLIT)), P2(E.WALL, zr(E.Z_SPLIT)), P2(E.WALL, zr(E.Z_TOP)),
                        P2(0, zr(E.Z_TOP))], closed=True, **hatch))
    ax.add_patch(MPoly([P2(E.WALL, zr(E.Z_PCB_TOP + 0.4)), P2(E.WALL + pad_d, zr(E.Z_PCB_TOP + 0.4)),
                        P2(E.WALL + pad_d, zr(E.Z_POCKET_CEIL)), P2(E.WALL, zr(E.Z_POCKET_CEIL))],
                       closed=True, **hatch))
    r1 = E.LEG_BOSS_D / 2
    ax.add_patch(MPoly([P2(-E.LEG_BOSS_H, -r1), P2(0, -r1), P2(0, r1), P2(-E.LEG_BOSS_H, r1)], closed=True, **hatch))
    depth = max(r["depth"] for r in rows)
    ax.add_patch(MRect(P2(-E.LEG_BOSS_H, -E.LEG_TAP_D / 2), depth * s, E.LEG_TAP_D * s, fc="white", ec="k", lw=0.5))
    for v in (-1.5, 1.5):
        ax.plot(*zip(P2(-E.LEG_BOSS_H, v), P2(-E.LEG_BOSS_H + depth - 0.5, v)), color="k", lw=0.3)
    ax.plot(*zip(P2(-E.LEG_BOSS_H - 2, 0), P2(E.WALL + pad_d + 1, 0)), color="#0050a0", lw=0.3, ls="-.")
    dim(ax, P2(-E.LEG_BOSS_H, r1 + 1.6), P2(0, r1 + 1.6), f"{E.LEG_BOSS_H} ±0.05", off=(0, 3.5))
    dim(ax, P2(-E.LEG_BOSS_H - 2, -r1), P2(-E.LEG_BOSS_H - 2, r1), f"Ø{E.LEG_BOSS_D:.0f}", off=(-5, 0))
    dim(ax, P2(0, zr(E.Z_SPLIT) - 1.2), P2(E.WALL, zr(E.Z_SPLIT) - 1.2), f"wall {E.WALL:.0f}", off=(0, -3))
    dim(ax, P2(-E.LEG_BOSS_H, zr(E.Z_SPLIT) - 3.4), P2(-E.LEG_BOSS_H + depth, zr(E.Z_SPLIT) - 3.4),
        f"drill depth {min(r['depth'] for r in rows)}-{depth} per table", off=(0, -3))
    text(ax, ox + (E.WALL + pad_d / 2) * s, oy + zr(E.Z_PCB_TOP + 0.4) * s - 2, f"thread axis (dash-dot): "
         f"Z = {E.LEG_Z} in STEP", size=5.5, color="#0050a0", ha="center")
    text(ax, ox + (E.WALL + pad_d / 2) * s, oy + zr(E.Z_POCKET_CEIL) * s + 2,
         "pad behind wall\n(depth 3.5-6, see STEP)", size=5.5, ha="center", va="bottom")
    text(ax, ox - E.LEG_BOSS_H * s, oy + zr(E.Z_TOP) * s + 13, "outer wall face", size=5.5, ha="center")
    ax.plot(*zip(P2(0, zr(E.Z_TOP) + 2.2), P2(0, zr(E.Z_TOP))), color="k", lw=0.3)
    text(ax, ox + 15, oy + (zr(E.Z_TOP) + 7) * s, "SECTION B-B through boss axis, scale 5:1 (schematic)",
         size=7, weight="bold", ha="center")

    # tooth profile, 20:1, at the boss rim
    k = math.tan(math.pi / E.LEG_TEETH) / math.tan(math.radians(E.LEG_TOOTH_ANGLE) / 2)
    pitch = 2 * math.pi * r1 / E.LEG_TEETH
    hgt = r1 * k
    S2 = 20.0
    px0, py0 = 285, 215
    pts = []
    for i in range(4):
        pts += [(px0 + i * pitch * S2, py0), (px0 + (i + 0.5) * pitch * S2, py0 - hgt * S2)]
    pts.append((px0 + 4 * pitch * S2, py0))
    ax.plot(*zip(*pts), color="k", lw=0.7)
    ax.plot([px0 - 4, px0 + 4 * pitch * S2 + 2], [py0, py0], color="#0050a0", lw=0.3, ls="--")
    text(ax, px0 - 5, py0, "tip plane", size=5.5, color="#0050a0", ha="right", va="center")
    dim(ax, (px0, py0 + 4), (px0 + pitch * S2, py0 + 4), f"pitch {pitch:.3f} at Ø{E.LEG_BOSS_D:.0f}", off=(0, 3))
    dim(ax, (px0 + 4 * pitch * S2 + 4, py0), (px0 + 4 * pitch * S2 + 4, py0 - hgt * S2),
        f"{hgt:.3f}", off=(6, 0))
    text(ax, px0 + 1.5 * pitch * S2, py0 - hgt * S2 + 1, f"{E.LEG_TOOTH_ANGLE:.0f}°", size=6, ha="center",
         va="bottom")
    text(ax, px0 + 2 * pitch * S2, py0 + 13, "DETAIL C — TOOTH PROFILE at boss rim (Ø10), scale 20:1",
         size=7, weight="bold", ha="center")

    # tooth spec table
    tilt = math.degrees(math.atan(k))
    spec = [
        ["Number of teeth", f"{E.LEG_TEETH}  (CRITICAL — must match the stock ErgoDox EZ leg hub)"],
        ["Angular pitch", f"{360 / E.LEG_TEETH:.3f}°, equally spaced, no clocking requirement"],
        ["Tooth form", f"symmetric V, {E.LEG_TOOTH_ANGLE:.0f}° included angle, radial (Hirth / face-serration type)"],
        ["Toothed annulus", f"Ø{2 * r0:.1f} to Ø{E.LEG_BOSS_D:.1f} (to boss rim)"],
        ["Tooth height", f"{hgt:.3f} at Ø{E.LEG_BOSS_D:.0f};  {r0 * k:.3f} at Ø{2 * r0:.1f}  (proportional to radius)"],
        ["Groove bottom", f"straight line inclined {tilt:.2f}° to the tip plane, meeting the boss axis in the tip "
                          "plane"],
        ["Crest / root", "sharp, R0.1 max;  crests are the tip plane (no flat land on teeth)"],
        ["Centre land", f"Ø{2 * r0:.1f} flat, recessed {r0 * k:.3f} below tip plane (= root depth at Ø{2 * r0:.1f})"],
        ["Tip plane", f"{E.LEG_BOSS_H} ±0.05 proud of the wall face, parallel to wall, perpendicular to thread axis"],
        ["Thread", f"M3x0.5-6H RIGHT-HAND, concentric with boss within Ø0.05; tap drill Ø{E.LEG_TAP_D}"],
        ["Quantity", f"{len(rows)} bosses per part (L1-L{len(rows)}), identical"],
        ["Machining hint", f"90° engraving cutter, {E.LEG_TEETH} radial passes indexed {360 / E.LEG_TEETH:.0f}°, "
                           f"each a straight ramp of {tilt:.2f}°; 4th axis or right-angle head"],
        ["Mating part", "stock ErgoDox EZ tilt/tent leg hub (Ø10.4, radial teeth) + M3 spring thumbscrew"],
    ]
    yb = table(ax, 225, 182, [("Detent teeth specification", 38), ("", 147)], spec, size=5.6, row_h=4.0)
    loc = [[r["id"], f"{r['x']:.2f}", f"{r['y']:.2f}", f"{r['z']:.1f}", r["direction"].split("wall, ")[-1],
            f"{r['depth']}"] for r in rows]
    table(ax, 225, yb - 4, [("Boss", 12), ("X face", 18), ("Y face", 18), ("Z", 10),
                            ("Thread direction (into part)", 62), ("Drill depth", 18)], loc, size=5.6, row_h=4.0)
    text(ax, 225, yb - 4 - 4.0 * (len(loc) + 1) - 1.5, "X/Y/Z: centre of the boss tip plane in STEP coordinates.",
         size=5.2)
    title_block(ax, part, dwg, "2 of 2", "1:1, 5:1, 20:1", version, TOP_MATERIAL)
    pdf.savefig(fig)
    plt.close(fig)


def bottom_sheet(pdf, shape, right, part, dwg, version):
    fig, ax = new_sheet()
    to = place_view(ax, shape, "under", 115, 175, 1.0)
    text(ax, 20, 282, "VIEW FROM BELOW (−Z), outside (cosmetic) face — scale 1:1", size=8, weight="bold")
    rows = bottom_holes(right)
    for r in rows:
        label(ax, to(r["x"], r["y"], 0), r["id"], dx=5 if r["id"].startswith("C") else -6)
    y = table(ax, 222, 283, [("ID", 9), ("Feature", 52), ("X", 15), ("Y", 15), ("Note", 50)],
              [[r["id"], r["feature"], f"{r['x']:.2f}", f"{r['y']:.2f}", r["note"]] for r in rows])
    text(ax, 222, y - 1.5, "X/Y in STEP coordinates; features are on the underside (Z = 0).", size=5.2)
    notes(ax, 222, y - 8, "GENERAL NOTES", [
        f"Geometry per {part}.step. Dimensions not shown are taken from the STEP model.",
        f"Material: {TOP_MATERIAL}.",
        "NO THREADS in this part. C1-C8: clearance holes with 90° countersink for M2.5 ISO 10642 / DIN 7991 "
        "countersunk screws; heads must sit flush or up to 0.2 below the underside.",
        ("This is a LEFT-hand part: a mirror image of the right-hand part." if not right else
         "The left-hand part is a mirror image of this part."),
        "Cosmetic surfaces: underside and outer walls: no tool marks, scratches or clamp marks. Inside "
        "(pocket) surfaces are non-cosmetic.",
        "Break sharp edges 0.1-0.2 mm unless modelled.",
        f"Finish: {FINISH}.",
    ], width=118)
    title_block(ax, part, dwg, "1 of 1", "1:1", version, TOP_MATERIAL)
    pdf.savefig(fig)
    plt.close(fig)


def main(exports: str, order: str, version: str):
    os.makedirs(order, exist_ok=True)
    csv_rows = []
    for side in ("right", "left"):
        right = side == "right"
        for kind in ("top", "bottom"):
            part = f"ergodox_{side}_{kind}"
            step = os.path.join(exports, part + ".step")
            shape = import_step(step)
            dwg = f"EDX-{kind.upper()}-{side[0].upper()}"
            with PdfPages(os.path.join(order, part + ".pdf")) as pdf:
                if kind == "top":
                    top_sheet1(pdf, shape, right, part, dwg, version)
                    top_sheet2(pdf, shape, right, part, dwg, version)
                    for r in top_threads(right):
                        csv_rows.append([part, r["id"], r["thread"], r["hand"], r["cls"], r["drill"], r["depth"],
                                         r["full"], f"{r['x']:.3f}", f"{r['y']:.3f}", f"{r['z']:.3f}",
                                         r["direction"], r["note"]])
                else:
                    bottom_sheet(pdf, shape, right, part, dwg, version)
                    for r in bottom_holes(right):
                        csv_rows.append([part, r["id"], r["feature"], "", "", "", "", "", f"{r['x']:.3f}",
                                         f"{r['y']:.3f}", "0.000", "-Z face", r["note"]])
            shutil.copy(step, os.path.join(order, part + ".step"))
            print(f"  {part}: drawing + STEP")
    with open(os.path.join(order, "hole_table.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["part", "id", "thread_or_feature", "hand", "class", "tap_drill", "drill_depth",
                    "min_full_thread", "x", "y", "z", "direction", "note"])
        w.writerows(csv_rows)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "dev")
