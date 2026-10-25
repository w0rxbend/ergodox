# SPDX-License-Identifier: GPL-3.0-or-later
"""Overlay the model (outline, key well, switch cutouts, holes) on photo 15.

Usage: overlay.py <photo_15.jpg> <out.png>
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cad"))
import ergodox_case as E
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
# photo_15 right half calibration: KiCad (129.54, 52.7) -> px (455.6, 173), 1.417 px/mm
S, X0, Y0, PX0, PY0 = 1.417, 129.54, 52.7, 455.6, 173.0
def tp(kx, ky): return (PX0 + (kx - X0) * S, PY0 + (ky - Y0) * S)
def cad2px(x, y): return tp(x + E.OX, -y + E.OY)
im = Image.open(src).convert("RGB")
sc = 3
im = im.resize((im.width * sc, im.height * sc), Image.LANCZOS)
d = ImageDraw.Draw(im)
def poly(face, col):
    pts = []
    for e in face.outer_wire().edges():
        for i in range(21):
            p = e.position_at(i / 20)
            x, y = cad2px(p.X, p.Y); pts.append((x * sc, y * sc))
    d.line(pts + [pts[0]], fill=col, width=2)
poly(E.outline_face(), (255, 0, 0))
for wf in E.well_face(): poly(wf, (0, 160, 255))
for kx, ky, w, h, rot in E.KEYS:
    f = E.switch_cut(kx, ky, rot).faces()[0]; poly(f, (0, 180, 0))
for x, y in E.LEDS + [E.RESET] + E.SCREWS:
    px, py = tp(x, y); d.ellipse([px * sc - 4, py * sc - 4, px * sc + 4, py * sc + 4], outline=(255, 0, 255), width=2)
im.crop((300 * sc, 120 * sc, 590 * sc, 380 * sc)).save(out)
