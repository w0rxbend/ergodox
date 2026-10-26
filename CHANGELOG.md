# Changelog

This project uses [Semantic Versioning](https://semver.org/). Each `v*` tag publishes a GitHub release
with STL and STEP archives.

## [0.4.0] - 2026-10-26

### Added

- Custom CNC tent leg (`ergodox_leg`) based on caliper photos of the stock leg: Ø10.4 hub, spring
  counterbore, tapered arm, foot spigot. Its 36 hub teeth are the exact negative of the case boss
  teeth, so the two always mesh. Uses the stock M3 spring thumbscrew. One part fits all 6 positions.
- TPU foot cap (`ergodox_leg_cap.stl`).
- Leg drawing (`ergodox_leg.pdf`): hub tooth specification, features, quantity 6. It is part of the
  order package.
- Leg renders, and the caliper photos in `images/leg`.
- Clearance pockets for the electrolytic capacitor that lies on the top side of each EZ PCB, measured
  from top-side photos in `images/pcb`. The left PCB has it above the 3rd column from the outer edge,
  at (146.6, 39.35). The right PCB has it just inward of the middle back screw, at (121.15, 45.1). Each
  half gets its own pocket (`CAPS`). The pockets fill the back strip around the capacitor, keep the
  screw bosses, and reach 7.5 mm above the PCB, leaving 1.5 mm under the top face. The build checks
  both, and the fit-check DXF marks the right one.

### Changed

- The back wall moved out 1.5 mm on both halves (`CASE_Y_TOP` 28.6 → 27.1). Each half is now 168.0 mm
  deep. In the v0.3.0 printed test fit, the EZ PCB (PCB-P2308 rev. B) was pushed about 1.2 mm towards the
  front wall, so the switch footprints sat off-centre in the plate cutouts (`images/testfit`).
- The assembly preview shows the custom legs.
- The boss and the leg teeth now come from one shared groove generator (`detent_grooves()`).
- Boss drawing: the mating part is now the custom leg.

## [0.3.0] - 2026-10-26

### Added

- Manufacturing drawings, as one A3 PDF per part, generated from the STEP files by `cad/drawings.py`:
  - a thread table (size, right-hand, 6H, tap drill, depth, location);
  - the detent-boss sheet: 36 teeth, profile, section, specification;
  - tolerances, finish and cosmetic surfaces.
- JLCCNC order package (`make order`, released as `*-jlccnc-order.zip`): STEP + PDF per part,
  `hole_table.csv`, and `ORDER_NOTES.md` with remarks in English and Chinese.
- `docs/jlccnc-order.md`: the ordering guide and answers to likely engineering questions.

### Fixed

- Screw list: holes T1 and T5 are both blind under the key well, so each half needs 2 × M2.5×12 and
  6 × M2.5×14. The list said 1 and 7.

## [0.2.0] - 2026-10-26

### Added

- Mounts for the stock ErgoDox EZ tent/tilt legs and their M3 spring thumbscrews. Each mount is a
  tapped M3 hole in a pad behind the wall, with a Ø10 boss on the outer face carrying 36 radial
  detent teeth, so the stock brackets are not needed. See `docs/legs.md`.
- Assembly preview with the stock legs (`ergodox_right_assembly_with_legs.step/.stl`).
- The build fails if a leg boss or pad runs off its straight wall.
- Leg section and assembly renders, plus caliper photos of the stock brackets and legs in `images/`.

### Changed

- Leg positions moved to match the stock EZ: y = 64 on both main walls, v = 0.56u on the thumb wall.

### Removed

- The M4 leg thread. The stock thumbscrews are M3, measured with a caliper.

## [0.1.0] - 2026-10-25

### Added

- A parametric build123d model of an ErgoDox EZ-compatible two-piece aluminium case:
  - an integrated 1.5 mm plate in a 4 mm key well,
  - 8-screw M2.5 PCB clamp,
  - TRRS on both halves; USB, LEDs and reset on the right half,
  - tapped tent-leg pads,
  - recesses for the rubber feet.
- Exports: STEP and STL for both halves, and a 1:1 fit-check DXF for the PCB.
- Preview tools: z-buffer renderer, cross-sections, overlay on a photo.
- Docs: design notes, fit check, machining guide, sources.
- CI: builds on every push; tags publish a GitHub release with the archives.
