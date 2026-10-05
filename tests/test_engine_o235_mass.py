"""O-235 mass properties and the TCDS acceptance checks (ledger rows 70 and 71).

Weight is bookkeeping (the core is a residual, so the sum equals the TCDS figure by construction). The centre of gravity is the falsifiable test:
the layout is frozen and hashed (row 70) before any CG was computed, and a miss stays an UNCONDITIONAL strict xfail citing row 70 with the recorded value (a repair XPASSes and goes red, so nothing authorises itself); the layout is
never re-tuned to pass. The frame-E checks read the CG through the inverse of the one placement transform.

test_cg_check_discriminates scales every FITTED_ dimension and DENSITY_ value by 0.75 and 1.25, one at a time, and prints the sensitivity table (pytest -s).
The verdict, written after the run: see the assertion message and ledger row 70.
"""

import copy

import pytest

import core.engine_o235_book as L
from config.aircraft_config import config
from core.ledger import load_ledger

G = config.geometry
M = L.engine_mass_properties()
E = L.cg_in_engine_frame(M)  # (u, v, w) in frame E
LONG = E[0]  # inches from the flange along the crank, toward the crankcase
BELOW = -E[2]  # inches below the crank centreline
LEFT_ENGINE = (
    L.FITTED_LYCOMING_LEFT_V_SIGN * E[1]
)  # inches toward engine-left (the sign convention is the assumption in the layout docstring)
LEFT_ALT = -LEFT_ENGINE  # the other convention, reported only


def _engine_row():
    return next(r for r in load_ledger()["closure"]["rows"] if r["name"] == "engine")


def test_weight_bookkeeping():
    assert M.total_lb == pytest.approx(243.0, abs=0.5)
    assert M.total_lb == pytest.approx(sum(r.mass_lb for r in M.rows))
    for r in M.rows:
        if r.status != "representational":
            assert r.band[0] <= r.mass_lb <= r.band[1], r.name
        assert r.mass_lb > 0 and r.cite, r.name
    assert "mount_pads" not in {
        r.name for r in M.rows
    }  # the closure row engine_mount owns the mount


def _long_ok(cg_long_in: float) -> bool:
    """The one longitudinal acceptance predicate: distance from the flange toward the crankcase, TCDS 14.75 +-0.5."""
    return abs(cg_long_in - G.eng_o235_cg_from_flange_in) <= 0.5


def _long_from_fs(cg_fs: float) -> float:
    return (
        G.eng_o235_flange_fs - cg_fs
    )  # a pusher: the CG is FORWARD of the flange, so a smaller FS is a longer distance


@pytest.mark.xfail(
    strict=True,
    reason="ledger row 70: component CG 11.09 in from the flange vs TCDS 14.75 +-0.5 (recorded; frozen layout, not re-tuned). A repair XPASSes and goes red.",
)
def test_cg_matches_tcds_from_the_flange():
    assert _long_ok(LONG)


@pytest.mark.xfail(
    strict=True,
    reason="ledger row 70: component CG 0.56 in below the crank centreline vs TCDS 1.13 +-0.3 (recorded, frame E; frozen layout, not re-tuned). A repair XPASSes and goes red.",
)
def test_cg_vertical_below_the_crank_centreline():
    assert abs(BELOW - G.eng_o235_cg_below_cl_in) <= 0.3


def test_cg_lateral_engine_left_of_the_crank_centreline():
    # passes under LEFT_V_SIGN +1 (0.131 in vs 0.20 +-0.25); under the opposite convention it would read -0.131 and miss (ledger row 70)
    assert abs(LEFT_ENGINE - G.eng_o235_cg_left_in) <= 0.25


def test_flipped_datum_goes_red():
    # break-it: the predicate must accept an independently built passing point and reject its mirror about the flange
    assert _long_ok(_long_from_fs(G.eng_o235_flange_fs - 14.75))  # long 14.75: passes
    assert not _long_ok(
        _long_from_fs(G.eng_o235_flange_fs + 14.75)
    )  # long -14.75: the flipped datum fails
    assert (
        M.cg_fs < G.eng_o235_flange_fs
    )  # and the model's CG is forward of the flange, as on a pusher


def test_snapshot_of_the_recorded_cg_and_weight():
    """A SNAPSHOT of code output (ledger row 70 record), not truth: it pins the frame-E CG and total so an unrecorded change to the layout or mass code shows."""
    assert E == pytest.approx((11.089096, 0.130958, -0.558749), abs=0.005)
    assert M.total_lb == pytest.approx(243.0, abs=0.005)


def test_the_frame_e_cg_matches_the_fuselage_cg():
    # the inverse transform and the fuselage numbers describe one point
    x, y, _z = L.to_fuselage(*E)
    assert (x, y) == pytest.approx((M.cg_fs, M.cg_bl), abs=1e-9)
    assert L.to_engine(M.cg_fs, M.cg_bl, M.cg_wl + L.z_of_wl(0.0)) == pytest.approx(
        E, abs=1e-9
    )


def test_module_weight_agrees_with_the_frozen_closure_row():
    eng = _engine_row()  # read only: the closure block is frozen (ledger row 65)
    assert eng["weight_band_lb"][0] <= M.total_lb <= eng["weight_band_lb"][1]
    assert M.total_lb == pytest.approx(eng["weight_lb"], abs=0.5)


@pytest.mark.xfail(
    strict=True,
    reason="ledger row 70: module CG FS 144.74 (recorded) is outside the frozen closure engine band 140.8 to 141.3 (row 65); the row is never edited. A repair XPASSes and goes red.",
)
def test_module_cg_agrees_with_the_frozen_closure_row():
    eng = _engine_row()
    assert eng["arm_band_fs"][0] <= M.cg_fs <= eng["arm_band_fs"][1]


# ---- sensitivity: can the CG check discriminate? ---------------------------------------------------------------------------------------------
def _leaves(v, path=()):
    if isinstance(v, (tuple, list)):
        for i, x in enumerate(v):
            yield from _leaves(x, path + (i,))
    elif isinstance(v, (int, float)) and not isinstance(v, bool) and v != 0:
        yield path, v


def _scaled(v, path, k):
    if not path:
        return v * k
    out = list(v)
    out[path[0]] = _scaled(v[path[0]], path[1:], k)
    return tuple(out)


def _named_solids():
    """(name, placed solid) for every solid of the mass model, built from the live globals."""
    out = []
    barrels, heads = L._cylinder_solids()
    groups = [
        ("case", L._crankcase_solids()),
        ("stub", L._stub_solids()),
        ("disc", L._disc_solids()),
        ("barrel", barrels),
        ("head", heads),
        ("sump", L._sump_solids()),
        ("housing", L._housing_solids()),
        ("starter", L._starter_solids()),
        ("alternator", L._alternator_solids()),
        ("magneto", L._magneto_solids()),
        ("carb", L._carb_solids()),
        ("pump", L._pump_solids()),
    ]
    for g, shapes in groups:
        for i, sh in enumerate(shapes):
            out.append((f"{g}{i}", L._place(sh)))
    return out


def _overlaps():
    sol = _named_solids()
    res = {}
    for i, (na, a) in enumerate(sol):
        ba = a.BoundingBox()
        for nb, b in sol[i + 1 :]:
            bb = b.BoundingBox()
            if (
                ba.xmax < bb.xmin
                or bb.xmax < ba.xmin
                or ba.ymax < bb.ymin
                or bb.ymax < ba.ymin
                or ba.zmax < bb.zmin
                or bb.zmax < ba.zmin
            ):
                continue
            v = a.intersect(b).Volume()
            if v > 1e-6:
                res[(na, nb)] = v
    return res


def _admissible(baseline) -> bool:
    """No new overlap beyond the baseline, nothing aft of the flange but the stub and disc, nothing forward of the firewall."""
    for n, sh in _named_solids():
        b = sh.BoundingBox()
        if b.xmin <= G.fs_firewall:
            return False
        if not n.startswith(("stub", "disc")) and b.xmax > G.eng_o235_flange_fs + 1e-6:
            return False
    return all(v <= baseline.get(k, 0.0) + 1e-6 for k, v in _overlaps().items())


def sensitivity_table(monkeypatch):
    """[(name, delta CG_long at x0.75, delta at x1.25, admissible)] for every scalar FITTED_ dimension, every nonzero tuple component and every scalar DENSITY_ value,
    each moved alone with its dependents NOT following (independent frozen-scalar sensitivity). FITTED_LYCOMING_LEFT_V_SIGN (a convention flag) and DENSITY_BY_PART
    (material names) are left out. A perturbation is admissible when both x0.75 and x1.25 builds are admissible."""
    base = L.cg_in_engine_frame(L.engine_mass_properties())[0]
    baseline = _overlaps()
    rows = []
    for name in sorted(n for n in vars(L) if n.startswith(("FITTED_", "DENSITY_"))):
        if name in {"FITTED_LYCOMING_LEFT_V_SIGN", "DENSITY_BY_PART"}:
            continue
        orig = getattr(L, name)
        for path, _val in _leaves(orig):
            label = name + ("" if not path else "[" + "][".join(map(str, path)) + "]")
            d, ok = [], []
            for k in (0.75, 1.25):
                with monkeypatch.context() as mp:
                    mp.setattr(L, name, _scaled(copy.deepcopy(orig), path, k))
                    d.append(L.cg_in_engine_frame(L.engine_mass_properties())[0] - base)
                    ok.append(_admissible(baseline))
            rows.append((label, d[0], d[1], all(ok)))
    return rows


def test_cg_check_discriminates(monkeypatch):
    """Independent frozen-scalar sensitivity: each FITTED_ dimension and DENSITY_ value is scaled by 0.75 and 1.25 alone (dependent constants do not follow),
    the layout is rebuilt from the live globals, and the longitudinal CG shift is recorded with an admissibility flag (no new solid overlap, nothing aft of
    the flange but the stub and disc, nothing forward of FS 125). Only ADMISSIBLE perturbations count toward discrimination. VERDICT (recorded after the run, mirrored in ledger row 70): discriminating, but thinly. 2 of 70
    inputs exceed 0.5 in; only 1 of them is admissible (FITTED_CYL_FRONT_U, +-0.80 in); FITTED_CASE_LEN exceeds it but creates a new overlap.
    If a later layout leaves no admissible input above 0.5 in, the CG check is NON-DISCRIMINATING and this docstring and row 70 must say so. The dependency-consistent experiment (constants stored resolved so dependents follow) is NOT built (open issue)."""
    rows = sensitivity_table(monkeypatch)
    print(
        f"\nindependent frozen-scalar sensitivity, longitudinal CG inches from the flange (baseline {LONG:.4f})"
    )
    print(f"  {'input':44s} {'x0.75':>9s} {'x1.25':>9s}  admissible")
    for label, lo, hi, ok in sorted(rows, key=lambda r: -max(abs(r[1]), abs(r[2]))):
        flag = "  <-- exceeds 0.5 in" if max(abs(lo), abs(hi)) > 0.5 else ""
        print(f"  {label:44s} {lo:+9.4f} {hi:+9.4f}  {'yes' if ok else 'NO '}{flag}")
    exceeds = [r for r in rows if max(abs(r[1]), abs(r[2])) > 0.5]
    adm = [r for r in exceeds if r[3]]
    print(
        f"  {len(exceeds)} of {len(rows)} inputs exceed 0.5 in; {len(adm)} of those are admissible"
    )
    print("verdict:", "discriminating" if adm else "NON-DISCRIMINATING")
    assert rows  # the sweep ran; the verdict is reported, not forced
