# Ordering from JLCCNC

This page explains how to order one keyboard (4 case parts + 6 legs) from [JLCCNC](https://jlccnc.com). The same files
work for any other CNC service.

## The order package

Download `ergodox-cnc-case-<version>-jlccnc-order.zip` from the [latest release](https://github.com/w0rxbend/ergodox/releases/latest),
or build it with `just order`. It contains:

| File | Upload as | Purpose |
|---|---|---|
| `ergodox_right_top.step` | 3D model (part 1) | Geometry |
| `ergodox_right_top.pdf` | 2D drawing for part 1 | Sheet 1: threads T1–T8 and L1–L3, notes. Sheet 2: detent boss and teeth |
| `ergodox_right_bottom.step` / `.pdf` | part 2 | Countersunk holes and foot recesses (no threads) |
| `ergodox_left_top.step` / `.pdf` | part 3 | Mirror of part 1. The threads stay right-hand |
| `ergodox_left_bottom.step` / `.pdf` | part 4 | Mirror of part 2 |
| `ergodox_leg.step` / `.pdf` | part 5, **quantity 6** | Tent leg: hub teeth, bore, counterbore (no threads) |
| `ergodox_leg_cap.stl` | (print yourself, TPU) | Foot cap for the leg; not for CNC |
| `hole_table.csv` | (keep for reference) | Every hole and thread, in STEP coordinates |
| `ORDER_NOTES.md` | (this page) | Form settings, remarks text, answers |

The STEP files model every threaded hole at its **tap-drill diameter**: Ø2.05 for M2.5 and Ø2.5 for M3.
They contain no thread geometry, which is why each part needs its PDF drawing.

## Steps

1. Go to jlccnc.com and choose **CNC Machining → Instant Quote**.
2. Upload the 5 STEP files. Each one becomes a separate part. Set the leg's quantity to 6.
3. For each part, attach the PDF with the same name as the 2D drawing.
4. Set the options as in the table below, then paste the remarks into each part's remarks field.
5. Submit. Engineering review usually takes a day. Use the answers further down when they ask questions.

### Form settings

| Option | Top parts (right + left) | Bottom parts (right + left) | Leg |
|---|---|---|---|
| Process | CNC milling | CNC milling | CNC milling |
| Material | Aluminium 6061-T6. 7075-T6 also works and gives a stiffer plate | Aluminium 6061-T6 | Aluminium 6061-T6 |
| Surface finish | Bead blasting + anodizing. Pick a colour; black or silver hides tool marks best | Same as the top, for matching colour | Same as the top |
| Threads | **Yes. 11 per part: 8 × M2.5 + 3 × M3, all right-hand** | **No** | **No** |
| Tolerance | Standard (ISO 2768-m); the critical values are on the drawing | Standard | Standard; the teeth are on the drawing |
| Inspection | Standard | Standard | Standard |
| Quantity | 1 each (1 keyboard). Also ask for a price on 2 | 1 each | **6** (ask for 7–8 to have spares) |

If the form wants one thread type per part, choose M2.5 and give the M3 holes in the remarks; the
drawing lists them all.

### Remarks (paste for the TOP parts)

```
Threads per 2D drawing: 8x M2.5x0.45-6H (T1-T8) + 3x M3x0.5-6H (L1-L3), ALL RIGHT-HAND.
The STEP models holes at tap-drill size. Left part is a mirror image, but threads stay RIGHT-HAND.
T1 and T5 are BLIND under the key well (1.1 mm skin): do not break through.
L1-L3: Ø10 bosses on the outer walls with 36 radial V-teeth (90°, 10° pitch, face serration),
see sheet 2. Tooth count is critical. Needs 4th axis or right-angle head.
Switch cutouts 14.00 +0.05/-0. Cosmetic: top face, key well, outer walls.
Mask threads during anodizing, or re-tap afterwards.

螺纹见2D图纸：8个 M2.5x0.45-6H（T1-T8）+ 3个 M3x0.5-6H（L1-L3），全部为右旋螺纹。
STEP中螺纹孔按底孔直径建模。左侧零件为镜像件，但螺纹仍为右旋。
T1、T5为盲孔，顶面仅剩1.1mm，不可打穿。
L1-L3：侧壁上Ø10凸台，端面有36个径向V形齿（90°，齿距10°），见图纸第2页，齿数必须准确。
开关孔 14.00 +0.05/0。外观面：顶面、键位槽、外侧壁。阳极氧化时请保护螺纹，或氧化后回攻。
```

### Remarks (paste for the BOTTOM parts)

```
No threads. 8x Ø2.9 through holes with 90° countersink Ø5.2 for M2.5 countersunk screws
(C1-C8), 4x Ø10.5 x 0.6 recesses for rubber feet (F1-F4). Left part is a mirror image.
Cosmetic: underside and outer walls.

无螺纹。8个 Ø2.9 通孔，带90°沉头 Ø5.2（C1-C8，用于M2.5沉头螺钉）；4个 Ø10.5 x 0.6 脚垫槽（F1-F4）。
左侧零件为镜像件。外观面：底面和外侧壁。
```

### Remarks (paste for the LEG)

```
Quantity 6, identical (not left/right). No threads.
Toothed face: 36 radial V-teeth (90°, 10° pitch), Ø4.4 to Ø10.4, see drawing details D and E.
Tooth count is critical: the teeth must mesh with the case bosses (drawing EDX-TOP sheet 2).
Ø3.4 through bore + Ø6.5 x 4 counterbore on the back face. Spigot Ø4.5 -0.05.
Same anodize colour as the case parts.

数量6件，完全相同（不分左右）。无螺纹。
齿面：36个径向V形齿（90°，齿距10°），Ø4.4 至 Ø10.4，见图纸详图D和E。
齿数必须准确，需与外壳凸台啮合（图纸EDX-TOP第2页）。
Ø3.4 通孔 + 背面 Ø6.5 x 4 沉孔。端部轴 Ø4.5 -0.05。阳极氧化颜色与外壳相同。
```

## Prepared answers to engineering questions

| Likely question | Answer |
|---|---|
| Thread direction? | All threads are right-hand (clockwise to tighten), on both the right and the left parts. |
| The left part is mirrored. Should its threads be mirrored too? | No. Mirroring applies to the geometry only. All threads are standard right-hand. |
| Thread depth? | See the table on sheet 1. M2.5 bezel holes: drill 6.0, at least 5.6 full thread. T1/T5: drill 3.9, at least 3.5 full thread, blind. M3: drill 5.2–6.0, at least depth − 0.5 full thread. Bottoming taps or thread-forming taps are fine. |
| Holes T1/T5 are close to the top surface. | Intended. Leave 1.1 mm of skin and don't break through. A shallower thread (minimum 3.0) is acceptable if needed. |
| The teeth on the side bosses can't be machined, or cost extra. | Ask for the cost difference. Fallback: make the bosses plain (flat face, Ø10, 1.2 high) and keep the M3 threads; I'll fit a friction washer. Don't drop the bosses. |
| Can the tooth count or angle change? | No for the count, which must be 36. The angle can be 90° ± 2°, and crests may be slightly flattened (≤ 0.1). |
| Switch-cutout corners are R0.5: is a smaller tool needed? | R0.5 is the maximum. If they prefer, dog-bone reliefs are acceptable; a dog-bone version can be supplied. |
| The plate is thin (1.5 mm). | Expected. Support it while cutting. Flatness 0.2 over the part. |
| Sharp internal corners in pockets? | All pocket corners are R ≥ 1 mm (Ø2 tool), except the switch cutouts (R0.5, Ø1 tool). |
| Cosmetic surfaces? | Top: top face, key well, outer walls and bosses. Bottom: underside and outer walls. Inside surfaces may show tool marks. |
| Anodizing threads? | Mask them, or re-tap after anodizing. The screws must turn by hand. |
| Tolerances not given? | ISO 2768-m. The STEP model is the reference geometry. |
| Edge breaks? | Break sharp edges 0.1–0.2 mm. Keep tooth crests and switch-cutout edges sharp (≤ 0.1). |
| Text, logo or engraving? | None. |
| Leg: how to cut the hub teeth? | 3-axis, toothed face up. Cut a 5° cone from Ø4.4 to the rim, then 36 radial passes of a 90° engraver with its tip on the face plane, indexed 10°. Detail E shows the profile. |
| Leg: are left and right different? | No. All 6 legs are identical. |
| Leg: can the teeth be skipped or simplified? | No. Without teeth the leg will not hold its angle. If needed, the teeth can be slightly flattened (≤ 0.1). |

## After delivery

Check that the screws turn by hand in every thread before assembly. Print the foot caps in TPU and push
them on. Fit each leg with the stock spring thumbscrew and check that it clicks through its positions. Hardware is listed in [machining.md](https://github.com/w0rxbend/ergodox/blob/main/docs/machining.md#bill-of-materials-per-half).
