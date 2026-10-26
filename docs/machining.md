# Machining guide

## Bill of materials (per half)

| Qty | Part | Notes |
|---|---|---|
| 1 | Top shell, 6061-T6 (or 7075 for a stiffer plate) | stock ≥ 195 × 168 × 11 mm |
| 1 | Bottom tray, 6061-T6 | stock ≥ 195 × 168 × 8 mm |
| 6 | M2.5 × 14 countersunk screw, ISO 10642 / DIN 7991 | bezel and edge bosses (T2–T4, T6–T8), about 5.4 mm thread engagement |
| 2 | M2.5 × 12 countersunk screw | the two bosses under the key well (T1 by the thumb cluster, T5 in the centre); the holes are blind and leave 1.1 mm of skin |
| 4 | Rubber foot, Ø10 mm | recesses are Ø10.5 × 0.6 mm |
| 3 | Custom leg `ergodox_leg`, 6061-T6 | 3-axis; teeth match the case bosses ([legs.md](legs.md)) |
| 3 | Foot cap `ergodox_leg_cap`, TPU 95A print | or the stock rubber caps |
| 3 | Stock EZ M3 spring thumbscrews (with springs) | brackets not needed |
| — | Stock EZ PCB, switches, keycaps | |

## Top shell: 3 setups

1. **Underside up.** Mill the main cavity, the relief pockets, the bosses, and the M2.5 tap drill holes
   (Ø2.05, 6 mm deep). The jack notches open towards the parting plane, so a vertical end mill cuts them in this setup.
2. **Top up.** Mill the key well, then the switch cutouts through the plate. The cutouts are 14.0 mm square
   with R 0.5 corners and need a Ø1 mm tool. Set `DOGBONES = True` if the shop prefers dog-bones.
   Then cut the LED holes (Ø1.8), the reset hole (Ø1.5), the top-edge fillet (R 1.5), the parting chamfer
   and the outer profile with the 3 Ø10 leg bosses.
3. **Side ops (4th axis or right-angle head).** On each leg boss, cut the 36 radial V-teeth with a 90°
   engraver, then drill Ø2.5 and tap M3, 5.2–6.0 mm deep. The thumb wall is at 25°.

## Bottom tray: 2 setups

1. **Inside up.** Mill the pocket, the posts and the clearance holes.
2. **Outside up.** Cut the countersinks, the feet recesses and the bottom edge fillet (R 1).

## Leg: 2 setups (3-axis)

1. **Toothed face up.** Face the hub, cut a 5° cone from Ø4.4 to the rim, then make 36 radial passes
   of a 90° engraver along the face plane, indexed 10°. Drill the Ø3.4 bore.
2. **Back face up.** Cut the Ø6.5 × 4 counterbore, the arm profile and the R1.5 arm edges. Turn or
   mill the neck and spigot.

## General notes

- Internal pocket corners are R ≥ 1 mm (`TOOL_R`), so a Ø2 mm end mill finishes them.
- The plate is only 1.5 mm thick. When cutting the switch openings, support it with a fixture plate or a
  vacuum fixture, or leave tabs.
- Bead-blast, then anodize. Mask the tapped holes, or chase the threads after anodizing.
- Send the CNC shop the STEP files, not the STLs.
