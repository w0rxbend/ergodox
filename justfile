# ErgoDox CNC case - build recipes.
# Override the interpreter with:  just python=/path/to/python model

python  := ".venv/bin/python"
exports := "exports"
renders := "renders"
photo   := "docs/photos/photo_15_2026-10-25_14-30-30.jpg"
version := `git describe --tags --always --dirty 2>/dev/null || echo dev`

# Build CAD exports and preview renders
all: model renders

# List recipes
help:
    @just --list --unsorted

# Create .venv (Python 3.12) and install requirements
setup:
    python3.12 -m venv .venv
    .venv/bin/pip install -r requirements.txt

# Generate STEP, STL and fit-check DXF into exports/
model:
    {{python}} cad/ergodox_case.py {{exports}}

# Regenerate PNG previews in renders/ (needs exports)
renders:
    @mkdir -p {{renders}}
    {{python}} tools/zrender.py {{renders}}/pair_top_iso.png 1400 -50 0 \
        {{exports}}/ergodox_left_top.stl:-125,0,0 {{exports}}/ergodox_right_top.stl:125,0,0
    {{python}} tools/zrender.py {{renders}}/right_top_underside.png 1000 140 15 {{exports}}/ergodox_right_top.stl
    {{python}} tools/zrender.py {{renders}}/right_bottom_tray.png 1000 -45 15 {{exports}}/ergodox_right_bottom.stl
    {{python}} tools/zrender.py {{renders}}/right_with_legs.png 1200 -60 -60 \
        {{exports}}/ergodox_right_assembly_with_legs.stl
    {{python}} tools/zrender.py {{renders}}/leg.png 900 35 30 {{exports}}/ergodox_leg.stl {{exports}}/ergodox_leg_cap.stl
    {{python}} tools/zrender.py {{renders}}/spacer.png 1000 -50 35 {{exports}}/ergodox_right_spacer.stl
    {{python}} tools/zrender.py {{renders}}/leg_face.png 900 -150 20 {{exports}}/ergodox_leg.stl
    {{python}} tools/section.py {{exports}} {{renders}}/section.png
    {{python}} tools/leg_section.py {{exports}} {{renders}}/leg_section.png
    {{python}} tools/overlay.py {{photo}} {{renders}}/overlay_on_photo.png

# PDF drawings + JLCCNC order package in exports/order (needs exports)
order:
    rm -rf {{exports}}/order
    {{python}} cad/drawings.py {{exports}} {{exports}}/order {{quote(version)}}
    cp docs/jlccnc-order.md {{exports}}/order/ORDER_NOTES.md

# GitHub Pages microsite with the 3D viewer in _site/ (needs exports)
site:
    {{python}} tools/build_site.py {{exports}} _site {{quote(version)}}

# Build the site and serve it on http://localhost:8000
serve: site
    cd _site && python3 -m http.server 8000

# Remove Python caches
clean:
    find . -name __pycache__ -type d -prune -exec rm -rf {} +
