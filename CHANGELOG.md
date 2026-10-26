# Changelog

This project uses [Semantic Versioning](https://semver.org/). Each `v*` tag publishes a GitHub release
with STL and STEP archives.

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
