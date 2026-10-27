"""Assemble the GitHub Pages microsite: static files from site/, STL models from the exports,
the preview renders, and a manifest.json with part sizes, masses and leg placements.

usage: build_site.py <exports dir> <out dir> [version]
"""
import json
import math
import os
import shutil
import struct
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "cad"))
import ergodox_case as ec  # noqa: E402
from build123d import Pos, Rot  # noqa: E402

AL_DENSITY = 2.70e-3  # g/mm3, 6061
PARTS = {  # stl name -> label, material
    "right_top": ("Right top shell", "alu"),
    "right_bottom": ("Right bottom tray", "alu"),
    "left_top": ("Left top shell", "alu"),
    "left_bottom": ("Left bottom tray", "alu"),
    "right_spacer": ("Right plate spacer", "print"),
    "left_spacer": ("Left plate spacer", "print"),
    "leg": ("Tent leg", "alu"),
    "leg_cap": ("Leg foot cap", "tpu"),
}


def stl_stats(path):
    """Bounding box and enclosed volume of a binary STL."""
    with open(path, "rb") as f:
        data = f.read()
    n = struct.unpack("<I", data[80:84])[0]
    rec = np.frombuffer(data[84:84 + 50 * n], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    v = rec["v"].astype(np.float64)
    vol = np.einsum("ij,ij->i", v[:, 0], np.cross(v[:, 1], v[:, 2])).sum() / 6
    pts = v.reshape(-1, 3)
    return pts.min(0), pts.max(0), abs(vol), n


def leg_placements():
    """4x4 row-major matrix per mount (right half) that seats a leg on its boss with swing 0;
    the viewer appends the swing rotation about local Z."""
    out = []
    for (px, py), (nx, ny) in ec.leg_mounts():
        loc = (Pos(px, py, 0) * Rot(0, 0, math.degrees(math.atan2(-ny, -nx)))
               * Pos(0, 0, ec.LEG_Z) * Rot(0, -90, 0) * Pos(0, 0, ec.LEG_BOSS_H))
        t = loc.wrapped.Transformation()
        m = [[t.Value(r, c) for c in range(1, 5)] for r in range(1, 4)] + [[0, 0, 0, 1]]
        out.append([round(x, 6) for row in m for x in row])
    return out


def main(exports, out, version):
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(os.path.join(ROOT, "site"), out)
    shutil.copytree(os.path.join(ROOT, "renders"), os.path.join(out, "renders"))
    os.makedirs(os.path.join(out, "models"))
    parts = {}
    for name, (label, mat) in PARTS.items():
        src = os.path.join(exports, f"ergodox_{name}.stl")
        shutil.copy(src, os.path.join(out, "models", f"{name}.stl"))
        lo, hi, vol, tris = stl_stats(src)
        parts[name] = dict(label=label, material=mat, file=f"models/{name}.stl", triangles=int(tris),
                           size=[round(float(x), 1) for x in hi - lo],
                           mass_g=round(vol * AL_DENSITY, 1) if mat == "alu" else None,
                           volume_cm3=round(vol / 1000, 1))
    manifest = dict(version=version, repo="https://github.com/w0rxbend/ergodox", parts=parts,
                    legs=leg_placements(), leg_step_deg=10)
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    open(os.path.join(out, ".nojekyll"), "w").close()
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)
    print(f"site: {out} ({total / 1e6:.1f} MB), version {version}")
    for name, p in parts.items():
        print(f"  {name:13s} {p['triangles']:6d} tris  {p['size']}  {p['mass_g']} g")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "dev")
