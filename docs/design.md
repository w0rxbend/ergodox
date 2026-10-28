# Design notes

## Parts

Each half has two parts, joined at the PCB's bottom face:

- **Top** (`ergodox_<side>_top`): a shell with the integrated 1.5 mm switch plate set in a 4 mm key well.
  It also carries:
  - the perimeter walls, 3 mm thick
  - the TRRS notch, plus the USB notch on the right half
  - the PCB clamp bosses, with M2.5 tapped holes
  - the tent-leg mounts: an M3 tapped pad and a flat Ø10 boss on the wall
  - the LED and reset holes, right half only
- **Bottom** (`ergodox_<side>_bottom`): a tray with a 3 mm floor, low walls and posts that support the PCB.
  Its front inner wall (main body and thumb cluster) is 1 mm thicker than the top's
  (`BOTTOM_FRONT_INSET`), which closes the front gap around the PCB.
  It has countersunk M2.5 clearance holes and recesses for the rubber feet.
- **Plate spacer** (`ergodox_<side>_spacer`): a separate 3 mm sheet between the plate and the PCB. It
  covers the plate area, with a 15 mm opening around every switch and clearance around the screw
  bosses and leg pads (`SPACER_*`). It rests against the plate underside and stops 0.5 mm above the PCB.
  It can be 3D-printed (PETG, or TPU/foam for damping) or milled.

The left half is the right half mirrored about the YZ plane.

## Where the geometry comes from

| Feature | Source | Confidence |
|---|---|---|
| 38 switch centres, column stagger, 25° thumb cluster, 1.5u offsets | Original ErgoDox KiCad PCB by Fredrik Atmer, GPLv3 ([bishboria/ErgoDox](https://github.com/bishboria/ErgoDox), `ErgoDOX.kicad_pcb`). EZ keymaps and keycaps use the same matrix. | exact |
| 8 PCB clamp screws | Mounting holes on the original PCB (`ErgoDOXmech` module). Holes measured on an EZ bottom-view photo agree within about 4 mm, which is within photo error. | high, verify |
| TRRS x = 86.3, USB x = 137.6 (right half) | Original PCB. The EZ PCB photo gives 87.8 and 139.0. | high |
| USB on the right half only, 3 LEDs, reset | ZSA schematics ([zsa/docs](https://github.com/zsa/docs)): the right half has the ATmega32U4, USB and LEDs a/b/c; the left half has the MCP23018. | exact |
| Outline: 155 × 130 mm main body, 193 × 166 mm overall, corner radii | Measured from top-view photos, scaled by the 19.05 mm key pitch. TechPowerUp lists 155 mm per half. | ±1–2 mm |
| LED and reset hole positions | Measured from photos | ±1.5 mm |
| Plate 1.5 mm, plate top 5.0 mm above the PCB top | Cherry MX specification | exact |

ZSA has not published CAD for the EZ case. That is why the outline is a photo measurement and not a copy.

## Coordinate frame

All layout constants in `cad/ergodox_case.py` use the **KiCad frame of the right half**: x points towards
the outer edge, y points down (towards the user), units are mm. `P(x, y)` converts a point into the
model frame, which is centred near the origin with y pointing away from the user.

## Z stack (Z = 0 is the bottom face)

| Z (mm) | |
|---|---|
| 0 – 3.0 | bottom floor |
| 3.0 – 7.0 | clearance under the PCB for switch pins and solder; bottom posts |
| **7.0** | parting plane = PCB bottom face |
| 7.0 – 8.6 | PCB (1.6 mm) |
| 8.6 – 12.1 | top bosses clamp the PCB; switch housings |
| 9.1 – 12.1 | plate spacer (separate part), 0.5 mm above the PCB |
| 12.1 – 13.6 | integrated plate (1.5 mm) |
| 13.6 – 17.6 | key well (4 mm) |
| 14.6 – 17.6 | 3 mm skin over the back bezel. The pocket under it gives 6 mm above the PCB for the jacks and chips. |

## Screw bosses near switches

Two clamp screws sit between switches: #0 by the thumb cluster and #4 in the centre. Each boss radius is
shrunk to keep clear of the switch housings, which the model treats as ±7.8 mm squares. The minimum boss
radius is the tap drill radius plus 1 mm (about 2.0 mm). The build report lists the clearance and boss
radius for every screw.

## Known deviations from the injection-moulded EZ

- The EZ shell has many moulding ribs. Here they are replaced by solid aluminium walls, 3 mm thick.
- The stock steel leg brackets aren't used. Each leg screws into an M3 thread in the aluminium and is clamped against a flat boss on the wall ([legs.md](legs.md)). The stock bracket nut has detent teeth; the milled version has none, so the legs hold by friction.
- The outline and radii come from photos, not from ZSA CAD.
- Plate-mount stabilisers are off by default (`STABILIZERS = False`), following the stock EZ 2u thumb keys.
