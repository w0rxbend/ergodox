# ErgoDox EZ CNC Aluminium Case

[![build](../../actions/workflows/build.yml/badge.svg)](../../actions/workflows/build.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

A parametric, two-piece **aluminium replacement case for the ErgoDox EZ**, designed for CNC milling.
It takes the stock EZ PCB, switches and keycaps. The whole model is one Python script
([build123d](https://github.com/gumyr/build123d)). It produces STEP files for the machine shop,
STL files for a 3D-printed test fit, and a 1:1 DXF drawing for checking your PCB before cutting metal.

![Both halves, top shells](renders/pair_top_iso.png)

## Features

- **Exact key layout.** The 38 switch positions per half, the column stagger and the 25° thumb cluster
  come from the original ErgoDox KiCad PCB. The EZ uses the same key matrix.
- **Integrated top-mount plate.** The 1.5 mm switch plate is milled into the top shell and sits in
  a 4 mm key well, so the case has no separate plate.
- **PCB clamped between top and bottom.** The PCB sits between bosses in the top shell and posts in the
  bottom tray, held by 8 × M2.5 countersunk screws on the original ErgoDox hole pattern.
- **Matches the EZ:**
  - TRRS openings on both halves.
  - USB, 3 LED windows and the reset hole on the right half only.
  - Mounts for the **stock EZ tent/tilt legs and M3 thumbscrews**: a tapped M3 hole with a toothed
    Ø10 detent boss, so the legs keep their click-stop positions. See [docs/legs.md](docs/legs.md).
- **Designed for milling.** Internal corners are R ≥ 1 mm, and the jack notches open towards the
  parting plane. The top takes 2 setups plus a side setup for the leg bosses; the bottom takes 2 setups.
- **Fully parametric.** Every dimension is a named constant at the top of
  [`cad/ergodox_case.py`](cad/ergodox_case.py).

| | |
|---|---|
| Size per half | 194.4 × 166.5 × 17.6 mm (including the leg bosses) |
| Mass per half (6061-T6) | ≈ 350 g (top 142 g + bottom 209 g) |
| Fasteners per half | 7 × M2.5×14 + 1 × M2.5×12 countersunk (ISO 10642) |
| Feet | 4 × Ø10 mm rubber bumpers in 0.6 mm recesses |
| Tent/tilt legs | 3 stock EZ legs and M3 thumbscrews per half; the brackets are not needed |

## Download

Ready-made files are attached to every [GitHub release](../../releases):

- `ergodox-cnc-case-<version>-stl.zip` contains the 4 STL files, for a 3D-printed test fit.
- `ergodox-cnc-case-<version>-step.zip` contains the 4 STEP files and `ergodox_right_fitcheck.dxf`, for CAM or a CNC shop.

> [!WARNING]
> The case outline was measured from photos (±1–2 mm). Work through
> [docs/fit-check.md](docs/fit-check.md) and **3D-print a test fit before machining aluminium**.

## Build from source

You need Python **3.10–3.13**. build123d/OCP has no wheels for 3.14 yet.

```sh
make setup      # creates .venv and installs requirements.txt
make model      # writes exports/*.step, *.stl and the fit-check DXF
make renders    # refreshes renders/*.png from the exports
make help       # lists all targets
```

`make model` prints a build report: screw-to-switch clearances, tent-leg wall checks, and each part's
mass, size and geometry validity. It exits non-zero if any part is not a single valid solid.

To use another interpreter, run `make PYTHON=/path/to/python model`.

## Repository layout

```
cad/ergodox_case.py      parametric model: all dimensions, geometry and export
tools/                   preview helpers: z-buffer renderer, cross-section, photo overlay
renders/                 preview images used in the docs
docs/                    design notes, fit check, machining guide, sources
docs/photos/             reference photos of a stock ErgoDox EZ
.github/workflows/       CI: build on every push, publish a release on v* tags
exports/                 (git-ignored) generated STEP/STL/DXF
```

## Documentation

| Document | Contents |
|---|---|
| [docs/design.md](docs/design.md) | Where each dimension comes from, the coordinate frame, the Z stack, part breakdown |
| [docs/legs.md](docs/legs.md) | Tent/tilt legs: the M3 detent boss, measurements, what to check |
| [docs/fit-check.md](docs/fit-check.md) | What to measure on your keyboard before machining |
| [docs/machining.md](docs/machining.md) | Bill of materials, setups, tooling, finishing |
| [docs/sources.md](docs/sources.md) | References and prior art |

## Previews

| Top shell, underside | Bottom tray |
|---|---|
| ![](renders/right_top_underside.png) | ![](renders/right_bottom_tray.png) |

The model overlaid on a photo of a real EZ. Red is the outline, blue the key well, green the switch
cutouts and magenta the holes:

![Overlay on photo](renders/overlay_on_photo.png)

The stock tent legs, deployed, with a section through the outer leg mount:

| Assembly preview | Leg mount section |
|---|---|
| ![](renders/right_with_legs.png) | ![](renders/leg_section.png) |

The cross-sections show the PCB clamped between the top bosses and the bottom posts:

![Sections](renders/section.png)

## Releasing

Push a version tag and CI builds, packages and publishes the release:

```sh
git tag -a v0.2.0 -m "v0.2.0" && git push origin v0.2.0
```

## License

[GPL-3.0-or-later](LICENSE). The switch and mounting-hole coordinates are taken from the original
ErgoDox PCB by Fredrik Atmer, which is GPLv3, so this derivative uses the same licence.
"ErgoDox EZ" is a product of ZSA Technology Labs. This project is not affiliated with or endorsed by ZSA.
