# Fit check before machining

The key layout is exact. The outline and a few holes are measured from photos, so check them against
your own keyboard before ordering aluminium parts.

## 1. PCB holes and outline (paper)

1. Print `ergodox_right_fitcheck.dxf` at **100 %**. It is in the `-step.zip` release archive, or run `make model`.
   Check the scale with a ruler: the key pitch is 19.05 mm.
2. Lay your EZ right-hand PCB on the print. Check that:
   - the 8 circles on layer `SCREWS` fall on the PCB mounting holes, and
   - the PCB sits inside the dashed `WALL_INNER` line. The tightest spots are the two back corners, with 0.3 mm to spare.
3. If something is off, edit `SCREWS`, `CASE_*` or `R_TOP_CORNERS` in `cad/ergodox_case.py` and rebuild.

DXF layers: `OUTLINE`, `WALL_INNER`, `KEY_WELL`, `SWITCH_CUTOUTS`, `SCREWS`, `FEATURES` (jacks, LEDs, reset).

## 2. Tent/tilt leg thread

ZSA doesn't publish the leg thread size. The model uses an M4 tap drill (`LEG_TAP_D = 3.3`) at
Z = 11 mm on 3 legs. Measure your leg screw and change `LEG_TAP_D` if needed.

## 3. Jack openings

The TRRS opening is 8 mm wide and the USB opening 12 mm wide; both rise to Z = 15 mm. A straight,
slim plug fits. A bulky right-angle cable may not. The widths are in `TRRS` and `USB`.

## 4. Stabilisers

These are off by default. Set `STABILIZERS = True` to add Cherry plate-mount stabiliser cutouts for the
2u thumb keys.

## 5. 3D-printed test fit (recommended)

Print the STL files from the `-stl.zip` release archive in PLA or PETG, at 0.2 mm layers with 3 walls.
Build up the keyboard in the printed case:
- the switches should click into the plate,
- the screws should line up with the PCB holes,
- the cables should plug in,
- the legs should thread in.
