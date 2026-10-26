# Tent / tilt legs

Each case mount is an M3 tapped hole with a **toothed detent boss** on the outside of the wall. The
leg is a **custom CNC aluminium part** (`ergodox_leg`) with teeth that are the exact negative of the
boss, held by the stock ErgoDox EZ spring-loaded M3 thumbscrew. The stock steel brackets are not
needed. The stock legs may also fit the bosses, but their tooth form is not known exactly.

![Outer leg section](../renders/leg_section.png)

## How the stock mount works

The stock bracket carries a pressed-in M3 nut. The nut's face has radial teeth, and the leg hub has
matching teeth. The spring thumbscrew pushes the hub onto the nut, so the leg clicks between
positions and holds its angle. The teeth are visible on both parts in `images/next` photos 1–3.

## How this case mounts them

![Assembly with legs deployed](../renders/right_with_legs.png)

| Feature | Value | Parameter |
|---|---|---|
| Thread | M3, tap drill Ø2.5, 5.2–6.0 mm deep from the boss face | `LEG_TAP_D`, `LEG_DEPTH` |
| Thread axis height | Z 12.0 | `LEG_Z` |
| Detent boss | Ø10, 1.2 mm proud of the wall, spans Z 7.0–17.0 on the top part | `LEG_BOSS_D`, `LEG_BOSS_H` |
| Teeth | 36 radial 90° V-teeth (10° steps), from r = 2.2 to the boss edge; flat centre at root depth | `LEG_TEETH`, `LEG_TOOTH_ANGLE`, `LEG_TOOTH_R0` |
| Pad behind the wall | 10 mm along the wall, up to 6 mm deep, Z 9.0–14.6, kept clear of switch housings and the key well | `LEG_PAD` |
| Positions (KiCad right-half frame) | outer wall y = 64, inner wall y = 64, thumb end wall v = 0.56u (stock EZ positions) | `LEG_MAIN_Y`, `LEG_THUMB_V` |

- **Teeth.** The tooth grooves meet at the axis, like the stock nut, so the tooth height grows with
  radius: about 0.44 mm at the rim and 0.19 mm at r = 2.2.
- **Thread depth.** The M3 thread runs through the boss, the 3 mm wall and the pad. On the outer
  wall the drill stops 0.3 mm short of the key well, because the thread passes just under the well
  floor there. The build report prints the depth for each leg.
- **Build check.** The build fails if a boss or pad would run off its straight wall, or if the boss
  wouldn't fit between the parting plane and the top.
- **Top part only.** All leg features are on the top part. The bottom tray is unchanged.

## The custom leg

![Custom leg](../renders/leg.png)

| Toothed face | Seated on the case |
|---|---|
| ![](../renders/leg_teeth.png) | ![](../renders/right_with_legs.png) |

The leg copies the stock leg's shape and size (caliper photos in [`images/leg`](../images/leg)):

| Feature | Value | Parameter |
|---|---|---|
| Hub | Ø10.4 × 8.0, toothed face towards the case | `LEG_HUB_D`, `LEG_HUB_L` |
| Teeth | 36 radial 90° V-teeth, Ø4.4 to the rim: the negative of the boss teeth | from `LEG_TEETH`, `LEG_TOOTH_*` |
| Bore | Ø3.4 through (M3 clearance, no thread) | `LEG_HOLE_D` |
| Spring counterbore | Ø6.5 × 4.0 in the outer face, for the stock thumbscrew spring | `LEG_CBORE` |
| Arm | 7.5 wide at the hub, tapering to 6.0; 6.0 thick, flush with the outer face | `LEG_ARM_W`, `LEG_ARM_T` |
| Foot | Ø6 neck, Ø4.5 × 5 spigot, TPU cap Ø9 with a domed end | `LEG_NECK_D`, `LEG_SPIGOT`, `LEG_FOOT_D` |
| Length | 47 from the pivot to the foot tip | `LEG_LEN` |
| Mass | 5.0 g in 6061 | |

- **Teeth that always mesh.** The boss teeth are cut by 36 V-grooves (`detent_grooves()`). The leg
  hub gets the same 36 groove solids added as teeth, so each leg tooth fills a boss groove exactly.
  The build checks nothing overlaps when seated. The tooth count no longer has to match a stock part:
  change `LEG_TEETH` and both sides follow.
- **One part for all six positions.** The leg is symmetric, so it is not handed. Order 6.
- **Clearance.** The arm is flush with the outer (spring) face, so it sits 2.0 mm off the toothed face
  and 3.2 mm off the wall as it swings.
- **Foot cap.** `ergodox_leg_cap.stl` is a push-on cap to print in TPU 95A. The stock rubber caps may
  also fit the Ø4.5 spigot.
- **Machining.** The leg needs only 3-axis work. Cut a 5° cone on the toothed face, then make 36 radial
  passes with a 90° engraver along the face plane. The drawing `ergodox_leg.pdf` gives the full
  specification.

## Measured dimensions

The readings come from caliper photos in [`images/`](../images) and [`images/next`](../images/next).

| Dimension | Value | Source |
|---|---|---|
| Thumbscrew thread | M3: outer diameter 2.85–2.9 | caliper (`images/next` photos 1, 2) |
| Detent | radial teeth on the leg hub and the nut, spring thumbscrew | `images/next` photos 1–3 |
| Tooth count | about 36–40 on the nut; 36 (10° steps) per [rothgar/ergodox-ez-tent-kit#2](https://github.com/rothgar/ergodox-ez-tent-kit/issues/2) | photo count, **verify** |
| Leg hub diameter | 10.4–10.5 | caliper (`images/` photo 5, `images/leg` photo 2) |
| Leg arm | about 7.5 wide, 7.6 across the hub step | caliper (`images/leg` photo 1), photo pixels |
| Hub back face | spring counterbore about Ø6.5 | `images/leg` photo 5 |
| Leg, pivot to foot tip | 47 ± 3 | photo pixels |

## Check before machining

1. **Tooth count, only for stock legs.** The custom leg always meshes with the boss. If you want the
   stock legs to fit too, count the teeth on a stock hub and set `LEG_TEETH` to match.
2. **Thread length.** With the custom leg seated, the thumbscrew passes the spring, the 4.0 mm web
   behind the counterbore and the teeth before it reaches the case. Measure the stock screw: the thread
   must not reach further into the case than the drill depth in the build report (at least 5.2 mm). If it
   is too long, add a washer under the head or change `LEG_CBORE`.
3. **Leg positions.** These came from photos (±2 mm). Measure your stock shell from its corners and
   adjust `LEG_MAIN_Y` and `LEG_THUMB_V` if needed.

## Machining

The boss outline can be cut with the outer profile. The teeth and the M3 hole sit on vertical walls,
so they need a side setup: a 4th axis, a right-angle head, or the part clamped on its side. The
thumb wall is at 25°.
- **Teeth:** a 90° engraving cutter running radially, 36 passes indexed every 10°. On a 4th axis,
  index the part so each boss faces the spindle.
- **Thread:** drill Ø2.5 and tap M3, or fit a Helicoil (Ø3.2 drill, STI tap) for a hard-wearing thread.

## Known limitations

- **The legs don't fold flat everywhere.** The inner leg at y = 64 can't fold flat forwards, because its
  foot meets the thumb cluster at about y = 115. The thumb leg overhangs a corner when folded. The
  stock EZ has the same layout.
- **Stock legs are a best guess.** The boss teeth model the stock profile from photos. Use the custom
  legs for a guaranteed fit, or test a stock leg on a printed top part first.
- **Leg dimensions are from photos.** The hub, arm and counterbore sizes are within about ±0.3 mm. A
  printed leg on a printed top part will confirm the spring fits and the leg clicks.
