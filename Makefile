# ErgoDox CNC case - build targets.
# Override the interpreter with:  make PYTHON=/path/to/python model

PYTHON  ?= .venv/bin/python
EXPORTS := exports
RENDERS := renders
PHOTO   := docs/photos/photo_15_2026-10-25_14-30-30.jpg
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo dev)

.PHONY: all setup model renders order clean help

all: model renders ## Build CAD exports and preview renders

help: ## List targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

setup: ## Create .venv (Python 3.12) and install requirements
	python3.12 -m venv .venv
	.venv/bin/pip install -r requirements.txt

model: ## Generate STEP, STL and fit-check DXF into exports/
	$(PYTHON) cad/ergodox_case.py $(EXPORTS)

renders: ## Regenerate PNG previews in renders/ (needs exports)
	@mkdir -p $(RENDERS)
	$(PYTHON) tools/zrender.py $(RENDERS)/pair_top_iso.png 1400 -50 0 \
		$(EXPORTS)/ergodox_left_top.stl:-125,0,0 $(EXPORTS)/ergodox_right_top.stl:125,0,0
	$(PYTHON) tools/zrender.py $(RENDERS)/right_top_underside.png 1000 140 15 $(EXPORTS)/ergodox_right_top.stl
	$(PYTHON) tools/zrender.py $(RENDERS)/right_bottom_tray.png 1000 -45 15 $(EXPORTS)/ergodox_right_bottom.stl
	$(PYTHON) tools/zrender.py $(RENDERS)/right_with_legs.png 1200 -60 -60 \
		$(EXPORTS)/ergodox_right_assembly_with_legs.stl
	$(PYTHON) tools/section.py $(EXPORTS) $(RENDERS)/section.png
	$(PYTHON) tools/leg_section.py $(EXPORTS) $(RENDERS)/leg_section.png
	$(PYTHON) tools/overlay.py $(PHOTO) $(RENDERS)/overlay_on_photo.png

order: ## PDF drawings + JLCCNC order package in exports/order (needs exports)
	rm -rf $(EXPORTS)/order
	$(PYTHON) cad/drawings.py $(EXPORTS) $(EXPORTS)/order $(VERSION)
	cp docs/jlccnc-order.md $(EXPORTS)/order/ORDER_NOTES.md

clean: ## Remove Python caches
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
