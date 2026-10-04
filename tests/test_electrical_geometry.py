"""M2.8 electrical geometry (chapter 22): battery on the nose shelf, relays on F22, wire runs, lights, antennas; every part is representational."""

from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from core import electrical_book as eb
from core.fuselage_book import FIDELITIES, build_fuselage, z_of_wl
from core.sources import check_citation

REPO = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = {
    "elec.battery_shelf",
    "elec.battery",
    "elec.relays",
    "elec.wiring",
    "elec.lights",
    "elec.antennas",
}


def volume(shape) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def comp(wp):
    return cq.Compound.makeCompound(wp.vals())


def bb(wp):
    return comp(wp).BoundingBox()


def overlap(sa, sb_) -> float:
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
def parts():
    return eb.build_electrical()


def test_every_component_has_parts_valid_positive_solids_and_is_representational(parts):
    assert set(eb.COMPONENT_PARTS) == EXPECTED_COMPONENTS
    assert {n for ns in eb.COMPONENT_PARTS.values() for n in ns} == set(parts)
    for n, p in parts.items():
        assert p.fidelity == "representational" and p.fidelity in FIDELITIES, n
        assert p.cite and p.note, n
        for c in p.cite:
            check_citation(c)
        for s in p.solid.vals():
            assert s.isValid(), n
        assert comp(p.solid).Volume() > 0, n
    assert eb.FIDELITIES_USED == {"representational"}
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    assert EXPECTED_COMPONENTS <= set(g.components)


def test_battery_is_at_the_middle_of_the_nose_box_range_and_is_not_a_source(parts):
    b = bb(parts["battery"].solid)
    assert (b.xmin + b.xmax) / 2 == pytest.approx(
        11.0
    )  # the illustration station, FS 11
    assert (
        0.0 < b.xmin and b.xmax < 22.0
    )  # inside the nose box range FS 0 to 22 (p155, derived in M2.4)
    assert (
        "illustration only" in parts["battery"].note and "A6" in parts["battery"].note
    )
    assert "not printed" in parts["battery"].note
    s = bb(parts["shelf"].solid)
    assert b.zmin == pytest.approx(
        z_of_wl(2.5) + 0.6
    )  # the shelf pad is 0.6 above the floor mark (p155)
    assert s.zmax == pytest.approx(b.zmin) and s.zmin == pytest.approx(z_of_wl(2.5))


def test_the_battery_sits_clear_of_the_ng30_plates_and_the_pedal_arms(parts):
    b = bb(parts["battery"].solid)
    assert b.ymin > 1.7 + 0.5  # NG30 plates stand at B.L. 1.7; the pedal arms reach 2.3
    from core.nose_book import build_nose

    nose = build_nose()
    for n in ("ng30_plates", "pedals", "pivot_blocks", "ng31_disc", "f6_plate", "door"):
        assert overlap(parts["battery"].solid, nose[n].solid) < 1e-3, n


def test_cover_and_strap_wrap_the_battery_without_touching_it(parts):
    assert overlap(parts["cover"].solid, parts["battery"].solid) < 1e-6
    assert overlap(parts["strap"].solid, parts["battery"].solid) < 1e-6
    assert overlap(parts["strap"].solid, parts["cover"].solid) < 1e-6
    c, b = bb(parts["cover"].solid), bb(parts["battery"].solid)
    assert c.xmin < b.xmin and c.xmax > b.xmax and c.zmax > b.zmax
    assert c.zmin == pytest.approx(b.zmin)  # open at the bottom, on the shelf
    st = bb(parts["strap"].solid)
    assert st.xmax - st.xmin == pytest.approx(0.5)


def test_relays_are_on_the_front_face_of_f22(parts):
    for n in ("start_relay", "overvoltage_unit"):
        r = bb(parts[n].solid)
        assert r.xmax == pytest.approx(22.0)  # the front face of F22, F.S. 22
        assert r.xmax - r.xmin == pytest.approx(1.7)
    a, b = bb(parts["start_relay"].solid), bb(parts["overvoltage_unit"].solid)
    assert a.ymax < b.ymin  # side by side
    f22 = build_fuselage()["f22"].solid
    for n in ("start_relay", "overvoltage_unit"):
        assert overlap(parts[n].solid, f22) < 1e-6


def test_wire_runs_connect_the_places_the_page_names(parts):
    cab = bb(parts["battery_cable"].solid)
    assert cab.xmin > bb(parts["battery"].solid).xmax  # leaves the battery's rear
    assert cab.xmax < bb(parts["start_relay"].solid).xmin  # ends at the relay face
    bun = bb(parts["panel_bundle"].solid)
    assert bun.xmax < 39.75  # the forward side of the panel (p153)
    assert bun.ymin < -9 and bun.ymax > 9  # across it
    fw = bb(parts["firewall_cable"].solid)
    assert fw.xmax < 125.0 and fw.xmax > 124.0  # to the firewall, short of its face
    assert fw.zmax < bun.zmax  # along the floor corner, below the bundle's top run
    assert "access holes" in parts["firewall_cable"].note


def test_lights_sit_on_the_wing_tips_and_mirror(parts):
    r, l_ = bb(parts["light_right"].solid), bb(parts["light_left"].solid)
    assert r.ymin == pytest.approx(
        157.05
    )  # just outboard of the tip rib, BL 157 (p126)
    assert l_.ymax == pytest.approx(-157.05)
    assert r.xmin == pytest.approx(156.0)  # the tip leading edge, FS 156.0 (p126)
    assert (r.xmin, r.xmax, r.zmin, r.zmax) == pytest.approx(
        (l_.xmin, l_.xmax, l_.zmin, l_.zmax)
    )
    assert "green" in parts["light_right"].note and "red" in parts["light_left"].note
    s = bb(parts["strobe_supply"].solid)
    assert s.xmin > 82.28  # behind the front seat bulkhead
    assert s.ymax < 0  # on the left
    assert "no station or size is printed" in parts["strobe_supply"].note


def test_antennas_have_the_cp_lengths(parts):
    for n, sign in (("nav_strip_right", 1), ("nav_strip_left", -1)):
        b = bb(parts[n].solid)
        assert abs(b.ymax - b.ymin) == pytest.approx(22.8)  # CP30 LPC 78, not 24
        assert b.xmax - b.xmin == pytest.approx(0.5)  # 1/2 in tape
        assert sign * (b.ymin if sign > 0 else b.ymax) == pytest.approx(
            13.0
        )  # starts just outside the fuselage side
        assert b.zmax < 1.5  # under the canard's leading-edge plane (model z 1.5)
    c = bb(parts["comm_strips"].solid)
    import math

    length = math.dist((c.xmin, c.ymin, c.zmin), (c.xmax, c.ymax, c.zmax))
    assert length > 20.3  # the bounding diagonal bounds the 20.3 in strip from above
    verts = [v for s in comp(parts["comm_strips"].solid).Solids() for v in s.Vertices()]
    zs = sorted({round(v.Z, 3) for v in verts})
    assert zs[-1] - zs[0] == pytest.approx(
        20.3 * 47.0 / (47.0**2 + (196.6 - 186.8) ** 2) ** 0.5, abs=0.05
    )


def test_clear_of_the_airframe_except_the_pockets_the_pass_throughs_and_the_foam(parts):
    from core import wing_book as wb
    from core import winglet_book as wl
    from core.canopy_book import build_canopy
    from core.firewall_book import build_firewall
    from core.nose_book import build_nose
    from core.spar_book import build_spar

    airframe = {}
    for pref, d in (
        ("fus", build_fuselage()),
        ("nose", build_nose()),
        ("spar", build_spar()),
        ("fw", build_firewall()),
        ("can", build_canopy()),
        ("wingR", wb.build_wing("right")),
        ("wingL", wb.build_wing("left")),
        ("wlR", wl.build_winglet("right")),
        ("wlL", wl.build_winglet("left")),
    ):
        for n, p in d.items():
            if p.void or n in {"jigs", "jig", "jig_lines", "blocks"}:
                continue
            airframe[(pref, n)] = p.solid
    for n, p in parts.items():
        for (pref, k), s in airframe.items():
            v = overlap(p.solid, s)
            if n in eb.POCKET_PARTS and pref == "nose" and k in eb.POCKET_FOAM:
                continue
            if k in eb.PASS_THROUGH.get(n, ()) and pref == "fus":
                continue
            if n in eb.IN_FOAM_PARTS and pref in ("wlR", "wlL") and k == "upper_core":
                continue
            assert v < 1e-3, (n, pref, k, v)


def test_pocket_parts_are_the_ones_the_notes_say_overlap_the_foam(parts):
    for n in eb.POCKET_PARTS:
        assert "pocket" in parts[n].note, n
    assert "overlap the winglet core by design" in parts["comm_strips"].note


def test_wire_run_joints_are_the_only_self_overlaps(parts):
    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            v = overlap(parts[a].solid, parts[b].solid)
            if {a, b} == {"panel_bundle", "firewall_cable"}:
                assert v < 0.05
            else:
                assert v < 1e-3, (a, b, v)
