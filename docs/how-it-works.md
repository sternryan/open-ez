# How it works

A longer, still plain-language walk through the pieces in the [README](../README.md). Names in
backticks are real files you can open.

## 1. One file holds the numbers

`config/aircraft_config.py` is the only place a dimension or weight is typed in. Everything else
(the 3D parts, the physics checks, the build rehearsal) reads from it. Change a value there and it
changes everywhere, which is also how a wrong value gets found: it shows up in more than one place.

## 2. Every number has a receipt

Each number carries a label in `GEOMETRY_PROVENANCE`:

- **book** or **derived**: it comes from a page of a registered source, or is calculated from such
  values. The citation looks like `om-1980:p28` (a document id and a page).
- **cp-corrected**: the plans were later corrected in the Canard Pusher newsletter, and the value
  follows the correction (with its citation). The printed plans page is not the final word there.
- **conflict**: two sources disagree and both are kept.
- **unsourced**: no page has been found.
- **converted-unsourced**: a number that was shifted from one station frame to another and never checked
  against a page.
  Both stay visible and marked, not hidden and not trusted.

The registered documents are listed in `data/sources/registry.yaml`. A citation to an unregistered
document is rejected by the code.

## 3. The build rehearsal

`guide/graph/` holds the construction chapters as data: each chapter is a list of operations, such as
cut the cores, lay the plies, join the parts. The viewer in `guide/lab` replays them in 3D, with a
cut-through of the layup and the paths loads take through the structure. The text is written fresh
and cites the plans by page; it does not copy them.

## 4. Physics checks

- **Neutral point**, the balance point of the airplane's lift, computed two ways: a hand-derived
  formula, and a vortex-lattice simulation (OpenVSP/VSPAERO). If the two disagree by more than a set
  limit, the check fails. The center of gravity must sit ahead of the neutral point: then a nose
  bump naturally returns to level (stable). Behind it, the disturbance grows (unstable).
- **VSPAERO** is free, NASA-origin software (the solver in OpenVSP). It computes the neutral point
  from a 3D model of the wings and canard, which makes it an independent cross-check on the hand formula.
- **Static margin**, how far the centre of gravity sits ahead of the neutral point.
- **Centre of gravity and weight**, from a part-by-part ledger (`data/mass_ledger.yaml`) that is
  meant to add up to the sample empty airplane in the owner's manual.

## 5. Failing on purpose

When the model disagrees with the book, the test is kept failing and marked as an expected failure
(strict `xfail`: a test expected to fail, which turns the suite red if it ever passes, so a change that
silently closes a gap is noticed and the ledger updated), and the disagreement is logged in `docs/geometry-correction-ledger.md`. The
alternative is adjusting a fitted number until the test passes, which is how the code this project
started from ended up with numbers that matched by construction. A failing check here is a to-do
item with an address.

## 6. Where the work records live

`docs/harness/` holds the working logs and reports from the AI agents that did much of the
implementation; `docs/superpowers/` holds the design specs and plans; `docs/history/` holds retired
planning documents. Read the specs for intent, the Block 1 report for the current state of the numbers.
