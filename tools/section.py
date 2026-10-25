# SPDX-License-Identifier: GPL-3.0-or-later
"""Two cross-sections through the right half (top + bottom).

Usage: section.py <exports_dir> <out.png>
"""
import os, sys, numpy as np, trimesh, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
O = sys.argv[1]
fig, axs = plt.subplots(2, 1, figsize=(16, 7), dpi=110)
for ax, (origin, normal, axis, title) in zip(axs, [
        ((-0.46 + 0 , 0, 0), (1, 0, 0), 1, "Section X = middle-finger column (Y horizontal)"),
        ((0, 100 - 37.13, 0), (0, 1, 0), 0, "Section through back-edge screws / LEDs (X horizontal)")]):
    for name, col in (("right_top", "#7a8aa0"), ("right_bottom", "#b0b8c4")):
        m = trimesh.load(os.path.join(O, f"ergodox_{name}.stl"))
        sec = m.section(plane_origin=origin, plane_normal=normal)
        if sec is None: continue
        for ent in sec.discrete:
            ax.fill(ent[:, axis], ent[:, 2], color=col, alpha=0.9, lw=0.3, ec="k")
    for z, lab in ((7.0, "PCB bottom"), (8.6, "PCB top"), (13.6, "plate top")):
        ax.axhline(z, color="r", lw=0.5, ls="--"); ax.text(0.005, z + 0.2, lab, color="r", fontsize=7, transform=ax.get_yaxis_transform())
    ax.set_aspect("equal"); ax.set_title(title, fontsize=9); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(sys.argv[2])
