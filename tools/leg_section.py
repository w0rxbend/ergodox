# SPDX-License-Identifier: GPL-3.0-or-later
"""Section across the outer wall through the tent-leg pivot: tapped M3 hole in the
pad, the Ø10 leg boss, and the custom leg from the assembly preview.

Usage: leg_section.py <exports_dir> <out.png>
"""
import os, sys, trimesh, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
O = sys.argv[1]
fig, ax = plt.subplots(figsize=(6, 9), dpi=110)
# outer leg pivot: KiCad (210.6, 64.0) -> CAD y = 100 - 64 = 36
for name, col, fill in (("right_assembly_with_legs", "#d08040", False),
                        ("right_top", "#7a8aa0", True), ("right_bottom", "#b0b8c4", True)):
    m = trimesh.load(os.path.join(O, f"ergodox_{name}.stl"))
    sec = m.section(plane_origin=(0, 36, 0), plane_normal=(0, 1, 0))
    for ent in sec.discrete:
        if fill:
            ax.fill(ent[:, 0], ent[:, 2], color=col, alpha=0.9, lw=0.3, ec="k")
        else:
            ax.plot(ent[:, 0], ent[:, 2], color=col, lw=1.2)
for z, lab in ((7.0, "parting plane"), (8.6, "PCB top"), (12.0, "M3 / pivot axis"), (13.6, "plate top")):
    ax.axhline(z, color="r", lw=0.5, ls="--")
    ax.text(0.01, z + 0.2, lab, color="r", fontsize=7, transform=ax.get_yaxis_transform())
ax.set_xlim(66, 92); ax.set_ylim(-42, 19); ax.set_aspect("equal"); ax.grid(alpha=0.3)
ax.set_title("Outer tent leg: M3 tapped pad + Ø10 boss (orange = leg)", fontsize=8)
plt.tight_layout(); plt.savefig(sys.argv[2])
