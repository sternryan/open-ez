# Fabric requests are built here and submitted by an operator; this repo holds no node names or addresses.
SUITE ?= fast
PY ?= .venv/bin/python

.PHONY: fabric-request
fabric-request:
	$(PY) scripts/fabric_request.py --suite $(SUITE)
