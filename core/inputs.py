"""One model input row with its provenance: sourced, derived, assumption or unsourced.

SOURCED: read from a registered page (`source` is a `<id>:p<page>` citation).
DERIVED: computed in the repo from sourced rows by a stated, cited method; `source` is the method's
    citation and `also` lists the citations of the values it combines.
ASSUMPTION: no source exists; the conservative engineering value was chosen and `note` must say why.
UNSOURCED: no source and no recorded engineering choice; a gate reading the row must say so.

Every citation (source and also) is checked against data/sources/registry.yaml on construction.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.sources import check_citation

SOURCED = "sourced"
DERIVED = "derived"
ASSUMPTION = "ASSUMPTION"
UNSOURCED = "UNSOURCED"
STATUSES = (SOURCED, DERIVED, ASSUMPTION, UNSOURCED)
CITED = (SOURCED, DERIVED)


@dataclass(frozen=True)
class Input:
    """One model input. SOURCED and DERIVED need a registered citation; the other two carry none."""

    name: str
    value: object
    unit: str
    status: str
    source: str | None
    note: str = ""
    also: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"{self.name}: status must be one of {STATUSES}")
        if self.status in CITED:
            if not self.source or not str(self.source).strip():
                raise ValueError(f"{self.name}: a {self.status} input needs a citation")
            check_citation(self.source)  # raises on an unknown registry id or bad form
        elif self.source:
            raise ValueError(
                f"{self.name}: an {self.status} input may not carry a citation"
            )
        if self.also and self.status != DERIVED:
            raise ValueError(
                f"{self.name}: only a derived input lists `also` citations"
            )
        for c in self.also:
            check_citation(c)
        if self.status == ASSUMPTION and not self.note.strip():
            raise ValueError(f"{self.name}: an assumption must state its rationale")

    def as_row(self) -> dict:
        v = self.value
        if isinstance(v, tuple):
            v = list(v)
        return {
            "name": self.name,
            "value": v,
            "unit": self.unit,
            "status": self.status,
            "source": self.source if self.status in CITED else self.status,
            "also": list(self.also),
            "note": self.note,
        }
