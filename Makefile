# Push-gate affected mode: `make test-affected BASE=<full-sha>` runs the tests selected for BASE...HEAD by
# scripts/test-affected.py (smoke tests always; unmapped changes select the whole suite). A narrow green is
# not a full-suite green: run `python -m pytest -q` nightly and before releases.
PYTHON ?= $(shell test -x "$(CURDIR)/.venv/bin/python" && echo "$(CURDIR)/.venv/bin/python" || echo python3)
.PHONY: test-affected
test-affected:
	@if [ -z "$(BASE)" ]; then echo "make test-affected: BASE=<full-sha> is required" >&2; exit 2; fi
	"$(PYTHON)" "$(CURDIR)/scripts/test-affected.py" --repo "$(CURDIR)" --base "$(BASE)" --execute
