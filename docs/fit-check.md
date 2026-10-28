# Fit check before machining

The key layout is exact. The outline and a few holes are measured from photos, so check them against
your own keyboard before ordering aluminium parts.

## 1. PCB holes and outline (paper)

1. Print `ergodox_right_fitcheck.dxf` at **100 %**. It is in the `-step.zip` release archive, or run `just model`.
   Check the scale with a ruler: the key pitch is 19.05 mm.
2. Lay your EZ right-hand PCB on the print. Check that:
   - the 8 circles on layer `SCREWS` fall on the PCB mounting holes, and
   - the PCB sits inside the dashed `WALL_INNER` line. The tightest spots used to be the two back corners; the back wall now sits 1.5 mm further out.
3. If something is off, edit `SCREWS`, `CASE_*` or `R_TOP_CORNERS` in `cad/ergodox_case.py` and rebuild.

DXF layers: `OUTLINE`, `WALL_INNER`, `KEY_WELL`, `SWITCH_CUTOUTS`, `SCREWS`, `FEATURES` (jacks, LEDs, reset, capacitor).

### PCB position in a test print

Look through the switch cutouts: the centre hole of each switch footprint must be in the middle of its
cutout. The PCB must sit on the screw bosses with the screws going in straight, and it must not be pressed
against a wall. In the v0.3.0 test print, the EZ PCB (PCB-P2308 rev. B) was pushed about 1.2 mm towards
the front, so v0.4.0 moves the back wall out 1.5 mm. If you still see an offset, measure it and compare
the PCB screw holes with the bosses: an offset on the holes as well means a wall is pushing the PCB;
centred holes with offset footprints mean `KEYS` or `SCREWS` is wrong.

## 2. Capacitor in the back strip

Each EZ PCB carries a radial electrolytic capacitor on its top side. It lies on its side in the
back strip, with its leads bent towards the outer edge. The two PCBs put it in different places
([`images/pcb`](../images/pcb)), so each top shell has its own pocket (`CAPS` in the model, right-half
coordinates, about ±1 mm):

| Half | Capacitor | Pocket |
|---|---|---|
| Left | above the 3rd column from the outer edge, centre (146.6, 39.35), 11.6 × 6.1 incl. leads | x 124.5–167.0, about 910 mm² |
| Right | just inward of the screw at (118.2, 37.1), centre (121.15, 45.1), 11.1 × 7.0 incl. leads | x 109–131, y 40.4–51.7 (in front of the screw boss), about 226 mm² |

Each pocket runs to 2 mm short of the key well: the left one from the back wall, the right one from just in front of the screw boss. It reaches 7.5 mm above the PCB and
leaves 1.5 mm under the top face (`CAP_SKIN`).

- On the paper print (right half), the rectangle on layer `FEATURES` next to the middle back screw must
  cover the capacitor.
- The capacitor must not stand more than **7.5 mm** above the PCB. Press it flat against the board.
  The build report prints both pockets, and the build fails if a capacitor (plus 1 mm) doesn't fit its
  pocket or would touch a PCB boss.

## 2b. Plate spacer

The spacer (`ergodox_<side>_spacer.stl`) is a separate 3 mm sheet that fills the space between the
plate and the PCB. It has a 15 mm opening around each switch, 0.5 mm clear of the 14 mm lower
housing. It rests against the plate underside and stops **0.5 mm above the PCB**.

- Check the PCB's top side between the switches: anything taller than 0.5 mm there hits the spacer.
  Cut it out of the spacer or leave the spacer out.
- In the test print, fit the spacer before the switches. The switches must still clip into the
  plate, and the spacer must not press on the PCB when the screws are tight.

## 3. Tent/tilt legs

The model reuses the stock legs and M3 thumbscrews. Before cutting, check the 3 items listed in
[legs.md](legs.md#check-before-machining): the thread length and the leg positions.

## 4. Jack openings

The TRRS opening is 8 mm wide and the USB opening 12 mm wide; both rise to Z = 15 mm. A straight,
slim plug fits. A bulky right-angle cable may not. The widths are in `TRRS` and `USB`.

## 5. Stabilisers

These are off by default. Set `STABILIZERS = True` to add Cherry plate-mount stabiliser cutouts for the
2u thumb keys.

## 6. 3D-printed test fit (recommended)

Print the STL files from the `-stl.zip` release archive in PLA or PETG, at 0.2 mm layers with 3 walls.
Build up the keyboard in the printed case:
- the switches should click into the plate,
- the screws should line up with the PCB holes,
- nothing on the PCB top should sit under the webs that join the six edge bosses to the wall (the strip between each screw and the board edge),
- the cables should plug in,
- the capacitor should sit in its pocket without touching,
- the legs should screw in and hold their angle on the bosses (tap M3 in the print, or use M3 heat-set inserts). Print `ergodox_leg.stl` (PETG, bearing face down) and `ergodox_leg_cap.stl` (TPU) and try them with the stock thumbscrew.
