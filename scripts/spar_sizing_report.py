"""Print the main-wing spar cap sizing (core.spar_sizing) as JSON and as a plain table.

Design-analysis output, NOT a certification or airworthiness substantiation.
Writes to stdout only, or the JSON to the path given by --out.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.spar_sizing import size_spar_caps  # noqa: E402

COLS = (
    ("y_in", "y", "{:7.2f}"),
    ("chord_in", "chord", "{:6.2f}"),
    ("cap_depth_in", "depth", "{:6.3f}"),
    ("moment_ultimate", "M_ult", "{:9.0f}"),
    ("I_in4", "I", "{:7.3f}"),
    ("sigma_psi", "sigma", "{:8.0f}"),
    ("R", "R", "{:8.3f}"),
    ("margin", "margin", "{:8.3f}"),
    ("plies_solved", "n", "{:3d}"),
    ("plies_book", "book", "{:>7s}"),
    ("margin_book", "m_book", "{:8.3f}"),
    ("mass_lb", "mass", "{:7.4f}"),
)


def table(result) -> str:
    head = " ".join(
        f"{h:>{len(f.format(0) if 'd' in f or 'f' in f else f.format(''))}}"
        for _, h, f in COLS
    )
    lines = [head]
    for s in result.stations:
        cells = []
        for key, _, f in COLS:
            v = getattr(s, key)
            if key == "plies_book":
                v = f"{v[0]}/{v[1]}"
            cells.append(f.format(v))
        lines.append(" ".join(cells))
    lines.append(
        f"per wing, both caps: solved {result.total_mass_solved_lb:.3f} lb, "
        f"book {result.total_mass_book_lb:.3f} lb, extra over book {result.extra_ply_mass_lb:.3f} lb"
    )
    lines.append("UNSOURCED: " + ", ".join(result.unsourced))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, help="write the JSON here instead of stdout")
    a = ap.parse_args(argv)
    r = size_spar_caps()
    text = json.dumps(r.as_dict(), indent=2)
    if a.out:
        a.out.write_text(text + "\n")
    else:
        print(text)
    print(table(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
