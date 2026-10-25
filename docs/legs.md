# Tent / tilt legs

The case reuses the stock ErgoDox EZ legs and their spring-loaded M3 thumbscrews. The stock steel
brackets are not needed. Each mount is the v0.1.0 tapped hole and pad, switched to M3, plus a
**toothed detent boss** on the outside of the wall. The boss replaces the bracket nut's toothed face.

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

## Measured dimensions

The readings come from caliper photos in [`images/`](../images) and [`images/next`](../images/next).

| Dimension | Value | Source |
|---|---|---|
| Thumbscrew thread | M3: outer diameter 2.85–2.9 | caliper (`images/next` photos 1, 2) |
| Detent | radial teeth on the leg hub and the nut, spring thumbscrew | `images/next` photos 1–3 |
| Tooth count | about 36–40 on the nut; 36 (10° steps) per [rothgar/ergodox-ez-tent-kit#2](https://github.com/rothgar/ergodox-ez-tent-kit/issues/2) | photo count, **verify** |
| Leg hub diameter | 10.4–10.5 | caliper (photo 5) |
| Leg, pivot to foot tip | 47 ± 3 | photo pixels |

## Check before machining

1. **Count the teeth on the leg hub.** `LEG_TEETH` must match it exactly, or the leg won't seat. If you
   can, also measure the tooth angle and the toothed ring's inner diameter (`LEG_TOOTH_ANGLE`,
   `LEG_TOOTH_R0`).
2. **Thread length.** Measure how far the thumbscrew thread sticks out past the hub face with the leg
   seated. It must not be longer than the drill depth in the build report, which is at least 5.2 mm.
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
- **The teeth are a model of the stock profile.** The count, angle and inner radius are best estimates.
  A test print of the top part (or a printed boss) will show whether the stock leg clicks properly.
