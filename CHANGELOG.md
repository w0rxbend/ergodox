# Changelog

This project uses [Semantic Versioning](https://semver.org/). Each `v*` tag publishes a GitHub release
with STL and STEP archives.

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
