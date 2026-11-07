"""Additional coverage for ``core.upholstery_book`` (plans chapter 26, p170): bulkhead face probes,
bent-slab geometry across path-length regimes, cushion path decomposition, headrest stations,
suitcase prism symmetry and console cutouts, keepout fitting, and provenance/ledger invariants.
"""

from __future__ import annotations

import ast
import io
import math
import tokenize
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from config import config
from config.aircraft_config import GEOMETRY_PROVENANCE
from core import covers_book as cv
from core import upholstery_book as up
from core.fuselage_book import FusePart, build_fuselage, rollover_front_fs
from core.ledger import fuselage_ledger, load_ledger

G = config.geometry
REPO = Path(__file__).resolve().parents[1]


def volume(shape) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def comp(wp: cq.Workplane) -> cq.Compound:
    return cq.Compound.makeCompound(wp.vals())


def bb(wp: cq.Workplane):
    return comp(wp).BoundingBox()


def overlap(sa: cq.Workplane, sb_: cq.Workplane) -> float:
    a, b = comp(sa), comp(sb_)
    ba, bbx = a.BoundingBox(), b.BoundingBox()
    if (
        ba.xmax < bbx.xmin
        or bbx.xmax < ba.xmin
        or ba.ymax < bbx.ymin
        or bbx.ymax < ba.ymin
        or ba.zmax < bbx.zmin
        or bbx.zmax < ba.zmin
    ):
        return 0.0
    return volume(a.intersect(b))


@pytest.fixture(scope="module")
def uph():
    return up.build_upholstery()


@pytest.fixture(scope="module")
def fus():
    return build_fuselage()


@pytest.fixture(scope="module")
def covers():
    return cv.build_covers()


def test_module_metadata_and_part_records_match_chapter_26_conventions(uph):
    assert up.WORKSHOP_PARTS == frozenset()
    assert up.FIDELITIES_USED == frozenset({"representational"})
    expected_parts = {
        "front_cushion",
        "rear_cushion",
        "front_headrest",
        "rear_headrest",
        "suitcase_right",
        "suitcase_left",
    }
    assert set(uph) == expected_parts
    for name, part in uph.items():
        assert isinstance(part, FusePart)
        assert part.name == name
        assert part.void is False
        assert part.fidelity in up.FIDELITIES_USED
        assert part.cite == ("plans-1980:p170",)


def test_fitted_constants_carry_comment_and_stay_out_of_config_and_provenance():
    src = (REPO / "core" / "upholstery_book.py").read_text()
    lines = src.splitlines()
    fitted_names = []
    for node in ast.parse(src).body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.startswith("FITTED_")
        ):
            name = node.targets[0].id
            fitted_names.append(name)
            segment = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            comments = [
                tok.string
                for tok in tokenize.generate_tokens(io.StringIO(segment).readline)
                if tok.type == tokenize.COMMENT
            ]
            assert any("fitted, not book" in c for c in comments), name
            assert not hasattr(G, name) and not hasattr(G, name.lower()), name
            assert (
                name not in GEOMETRY_PROVENANCE
                and name.lower() not in GEOMETRY_PROVENANCE
            ), name
    assert len(fitted_names) == 9


def test_upholstery_carries_no_mass_in_any_ledger_sum():
    banned_tokens = ("upholstery", "cushion", "headrest", "suitcase")
    ledger_parts = {row["part"].lower() for row in fuselage_ledger()}
    for token in banned_tokens:
        assert not any(token in part for part in ledger_parts), token
    proto_rows = load_ledger()["prototype_weights"]["rows"]
    for key in proto_rows:
        assert not any(token in key.lower() for token in banned_tokens), key


def test_faces_probe_linearity_parallel_faces_and_bulkhead_ordering(fus):
    faces = up._faces()
    assert faces is up._faces()
    assert set(faces) == {"front", "rear"}
    specs = (
        ("front", "front_seat_bkhd", G.front_seat_bkhd_thickness),
        ("rear", "rear_seat_bkhd", G.rear_seat_bkhd_thickness),
    )
    for which, bkhd_name, thickness in specs:
        f = faces[which]
        b = bb(fus[bkhd_name].solid)
        assert f["top_z"] == pytest.approx(b.zmax, abs=1e-6)
        assert f["bottom_z"] == pytest.approx(b.zmin, abs=1e-6)
        assert f["slope"] > 0.0
        z_ref = f["z_ref"]
        assert up.face_front_x(which, z_ref) == pytest.approx(f["x_front"], abs=1e-9)
        assert up.face_aft_x(which, z_ref) == pytest.approx(f["x_aft"], abs=1e-9)
        z_lo, z_hi = -12.0, 0.0
        slope_front = (up.face_front_x(which, z_hi) - up.face_front_x(which, z_lo)) / (
            z_hi - z_lo
        )
        slope_aft = (up.face_aft_x(which, z_hi) - up.face_aft_x(which, z_lo)) / (
            z_hi - z_lo
        )
        assert slope_front == pytest.approx(f["slope"], rel=1e-9)
        assert slope_aft == pytest.approx(f["slope"], rel=1e-9)
        horiz_thickness = thickness * math.hypot(1.0, f["slope"])
        for z in (-14.0, -8.0, -2.0, 4.0):
            dx = up.face_aft_x(which, z) - up.face_front_x(which, z)
            assert dx == pytest.approx(f["x_aft"] - f["x_front"], abs=1e-9)
            assert dx == pytest.approx(horiz_thickness, abs=0.1)
    for z in (-14.0, -8.0, -2.0):
        assert up.face_front_x("rear", z) > up.face_aft_x("front", z) + 20.0
    with pytest.raises(KeyError):
        up.face_front_x("unknown", 0.0)
    with pytest.raises(KeyError):
        up.face_aft_x("unknown", 0.0)


def test_bent_slab_exact_volume_bounds_and_path_len_regimes():
    f = up._faces()["front"]
    m = f["slope"]
    k = math.hypot(1.0, m)
    z0, top_z, t, width = -14.0, 4.0, 2.0, 16.0
    xb = up.face_front_x("front", z0) - up.FITTED_CLEAR
    floor_len = 12.0
    x_start = xb - floor_len
    full_face_len = (top_z - z0) * k
    full_path = floor_len + full_face_len

    s_none = up.bent_slab(x_start, z0, "front", t, width, top_z, path_len=None)
    s_long = up.bent_slab(
        x_start, z0, "front", t, width, top_z, path_len=full_path + 10.0
    )
    expected_full_vol = width * (t * full_path + t**2 * (m - k))
    assert volume(comp(s_none)) == pytest.approx(expected_full_vol, rel=1e-4)
    assert volume(comp(s_long)) == pytest.approx(expected_full_vol, rel=1e-4)

    b_none = bb(s_none)
    assert b_none.xmin == pytest.approx(x_start, abs=1e-6)
    assert (b_none.ymin, b_none.ymax) == (
        pytest.approx(-width / 2, abs=1e-6),
        pytest.approx(width / 2, abs=1e-6),
    )
    assert b_none.zmin == pytest.approx(z0, abs=1e-6)
    assert b_none.zmax == pytest.approx(top_z + t * (m / k), abs=1e-6)

    p1 = floor_len + 6.0 * k
    p2 = floor_len + 12.0 * k
    s1 = up.bent_slab(x_start, z0, "front", t, width, top_z, path_len=p1)
    s2 = up.bent_slab(x_start, z0, "front", t, width, top_z, path_len=p2)
    assert volume(comp(s1)) == pytest.approx(
        width * (t * p1 + t**2 * (m - k)), rel=1e-4
    )
    assert volume(comp(s2)) == pytest.approx(
        width * (t * p2 + t**2 * (m - k)), rel=1e-4
    )
    assert volume(comp(s2)) - volume(comp(s1)) == pytest.approx(
        width * t * (p2 - p1), rel=1e-4
    )
    assert bb(s1).zmax == pytest.approx((z0 + 6.0) + t * (m / k), abs=1e-6)
    assert bb(s2).zmax == pytest.approx((z0 + 12.0) + t * (m / k), abs=1e-6)
    assert bb(s1).zmax < bb(s2).zmax < b_none.zmax

    p_short = floor_len + 2.0 * k
    s_short = up.bent_slab(x_start, z0, "front", t, width, top_z, path_len=p_short)
    assert volume(comp(s_short)) == pytest.approx(
        width * (t * p_short + t**2 * (m - k)), rel=1e-4
    )
    assert bb(s_short).zmax == pytest.approx((z0 + 2.0) + t * (m / k), abs=1e-6)
    assert bb(s_short).zmax < bb(s1).zmax

    s_exact = up.bent_slab(x_start, z0, "front", t, width, top_z, path_len=full_path)
    assert volume(comp(s_exact)) == pytest.approx(volume(comp(s_long)), rel=1e-6)
    assert bb(s_exact).zmax == pytest.approx(b_none.zmax, abs=1e-6)


def test_front_cushion_path_decomposition_and_placement(uph):
    length, width, t = G.upl_book_front_cushion_in
    f = up._faces()["front"]
    m = f["slope"]
    k = math.hypot(1.0, m)
    x0 = cv.thigh_x()[1] + up.FITTED_FRONT_FROM_THIGH
    xb = up.face_front_x("front", up.FITTED_FRONT_FLOOR_Z) - up.FITTED_CLEAR
    floor_len = xb - x0
    face_len = (f["top_z"] - up.FITTED_FRONT_FLOOR_Z) * k
    assert floor_len > 0.0 and face_len > 0.0
    path = up.front_cushion_path_in()
    assert path == pytest.approx(floor_len + face_len, rel=1e-12)
    assert 0.0 < path < length

    uncut_vol = width * (t * path + t**2 * (m - k))
    fc = uph["front_cushion"].solid
    assert 0.0 < volume(comp(fc)) < uncut_vol
    b = bb(fc)
    assert b.xmin == pytest.approx(x0, abs=1e-4)
    assert (b.ymin, b.ymax) == (
        pytest.approx(-width / 2, abs=1e-4),
        pytest.approx(width / 2, abs=1e-4),
    )
    assert b.zmin == pytest.approx(up.FITTED_FRONT_FLOOR_Z, abs=1e-4)
    assert overlap(fc, uph["front_headrest"].solid) < 1e-6


def test_rear_cushion_placement_and_suitcase_cutouts(uph):
    seat_d, width, back_h, t = G.upl_book_rear_cushion_in
    f = up._faces()["rear"]
    m = f["slope"]
    k = math.hypot(1.0, m)
    xb = up.face_front_x("rear", up.FITTED_REAR_FLOOR_Z) - up.FITTED_CLEAR
    back_slant = (f["top_z"] - up.FITTED_REAR_FLOOR_Z) * k
    assert back_slant == pytest.approx(back_h, abs=1.5)

    uncut = up.bent_slab(
        xb - seat_d, up.FITTED_REAR_FLOOR_Z, "rear", t, width, f["top_z"]
    )
    sr, sl = uph["suitcase_right"].solid, uph["suitcase_left"].solid
    assert (
        up.left_cut_fs() < xb - seat_d < up._suitcase_x0() + G.upl_book_suitcase_in[0]
    )
    assert bb(sl).xmax < bb(uncut).xmin
    assert overlap(uncut, sr) > 1.0
    assert overlap(uncut, up._suitcase(-1)) > 1.0
    assert overlap(uncut, sl) == pytest.approx(0.0, abs=1e-9)

    rc = uph["rear_cushion"].solid
    assert overlap(rc, sr) < 1e-6
    assert overlap(rc, sl) < 1e-6
    assert 0.0 < volume(comp(rc)) < volume(comp(uncut))
    b = bb(rc)
    assert (b.ymin, b.ymax) == (
        pytest.approx(-width / 2, abs=1e-4),
        pytest.approx(width / 2, abs=1e-4),
    )
    assert b.zmin == pytest.approx(up.FITTED_REAR_FLOOR_Z, abs=1e-4)


def test_headrests_exact_stations_symmetry_and_volumes(uph):
    wf, hf_h, tf = G.upl_book_front_headrest_in
    xf = rollover_front_fs() - up.FITTED_CLEAR
    zf = up.FITTED_FRONT_HEADREST_Z
    hf = bb(uph["front_headrest"].solid)
    assert (hf.xmin, hf.xmax) == (
        pytest.approx(xf - tf, abs=1e-6),
        pytest.approx(xf, abs=1e-6),
    )
    assert (hf.ymin, hf.ymax) == (
        pytest.approx(-wf / 2, abs=1e-6),
        pytest.approx(wf / 2, abs=1e-6),
    )
    assert (hf.zmin, hf.zmax) == (
        pytest.approx(zf, abs=1e-6),
        pytest.approx(zf + hf_h, abs=1e-6),
    )
    assert hf.zmin > up._faces()["front"]["top_z"]
    assert volume(comp(uph["front_headrest"].solid)) == pytest.approx(
        wf * hf_h * tf, rel=1e-6
    )

    wr, hr_h, tr = G.upl_book_rear_headrest_in
    xr, zr = up.FITTED_REAR_HEADREST_POS
    hr = bb(uph["rear_headrest"].solid)
    assert (hr.xmin, hr.xmax) == (
        pytest.approx(xr, abs=1e-6),
        pytest.approx(xr + tr, abs=1e-6),
    )
    assert (hr.ymin, hr.ymax) == (
        pytest.approx(-wr / 2, abs=1e-6),
        pytest.approx(wr / 2, abs=1e-6),
    )
    assert (hr.zmin, hr.zmax) == (
        pytest.approx(zr, abs=1e-6),
        pytest.approx(zr + hr_h, abs=1e-6),
    )
    assert volume(comp(uph["rear_headrest"].solid)) == pytest.approx(
        wr * hr_h * tr, rel=1e-6
    )
    assert hr.xmin > hf.xmax and hr.zmin < hf.zmin


def test_uncut_suitcase_prism_mirror_symmetry_and_trapezoid_volume():
    long_, high, top, thick = G.upl_book_suitcase_in
    x0 = up._suitcase_x0()
    assert x0 == pytest.approx(
        up.face_aft_x("front", up.FITTED_REAR_FLOOR_Z) + up.FITTED_CLEAR, abs=1e-9
    )
    sr_raw = up._suitcase(1)
    sl_raw = up._suitcase(-1)
    expected_vol = 0.5 * (long_ + top) * high * thick
    assert volume(comp(sr_raw)) == pytest.approx(expected_vol, rel=1e-6)
    assert volume(comp(sl_raw)) == pytest.approx(expected_vol, rel=1e-6)

    br, bl = bb(sr_raw), bb(sl_raw)
    for b in (br, bl):
        assert (b.xmin, b.xmax) == (
            pytest.approx(x0, abs=1e-6),
            pytest.approx(x0 + long_, abs=1e-6),
        )
        assert (b.zmin, b.zmax) == (
            pytest.approx(up.FITTED_REAR_FLOOR_Z, abs=1e-6),
            pytest.approx(up.FITTED_REAR_FLOOR_Z + high, abs=1e-6),
        )
    assert (br.ymin, br.ymax) == (
        pytest.approx(up.FITTED_SUITCASE_Y_SPAN, abs=1e-6),
        pytest.approx(up.FITTED_SUITCASE_Y_SPAN + thick, abs=1e-6),
    )
    assert (bl.ymin, bl.ymax) == (
        pytest.approx(-(up.FITTED_SUITCASE_Y_SPAN + thick), abs=1e-6),
        pytest.approx(-up.FITTED_SUITCASE_Y_SPAN, abs=1e-6),
    )


def test_left_cut_fs_and_suitcase_notches_clear_consoles(uph, covers):
    long_, _high, _top, _thick = G.upl_book_suitcase_in
    x0 = up._suitcase_x0()
    assert up.left_cut_fs() == pytest.approx(
        x0 + long_ - up.FITTED_LEFT_SHORTEN_IN, abs=1e-9
    )
    sr = uph["suitcase_right"].solid
    sl = uph["suitcase_left"].solid
    br, bl = bb(sr), bb(sl)
    assert (br.xmin, br.xmax) == (
        pytest.approx(x0, abs=1e-4),
        pytest.approx(x0 + long_, abs=1e-4),
    )
    assert (bl.xmin, bl.xmax) == (
        pytest.approx(x0, abs=1e-4),
        pytest.approx(up.left_cut_fs(), abs=1e-4),
    )
    assert br.xmax - bl.xmax == pytest.approx(up.FITTED_LEFT_SHORTEN_IN, abs=1e-4)

    rc_box = up._solid(up._right_console_box())
    assert overlap(up._suitcase(1), rc_box) > 1.0
    assert overlap(sr, rc_box) < 1e-6
    assert volume(comp(sr)) < volume(comp(up._suitcase(1)))

    assert overlap(sl, covers["lc5"].solid) < 1e-6
    assert overlap(sl, covers["lc6"].solid) < 1e-6
    assert volume(comp(sl)) < volume(comp(sr))


def test_keepouts_cache_and_fit_cuts_extra_solids():
    ks = up._keepouts()
    assert ks is up._keepouts()
    assert isinstance(ks, tuple) and len(ks) >= 10
    for k in ks:
        assert volume(k) > 0.0

    probe = up._solid(up._box(60.0, 64.0, -2.0, 2.0, 80.0, 82.0))
    fitted_plain = up._fit(probe)
    assert volume(comp(fitted_plain)) == pytest.approx(32.0, rel=1e-6)

    cutter = up._box(62.0, 66.0, -2.0, 2.0, 80.0, 82.0)
    fitted_cut = up._fit(probe, (cutter,))
    assert volume(comp(fitted_cut)) == pytest.approx(16.0, rel=1e-6)
    assert bb(fitted_cut).xmax == pytest.approx(62.0, abs=1e-6)
