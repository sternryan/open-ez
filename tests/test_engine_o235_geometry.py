"""O-235 component geometry (ledger rows 70 and 71): valid solids, placed from the flange datum, nothing aft of the flange but the stub and disc."""

import math

import cadquery as cq
import pytest

import core.engine_o235_book as L
from core import engine_book as ng
from core.fuselage_book import z_of_wl

G = L.config.geometry
FLANGE = G.eng_o235_flange_fs
OLD_KEYS = {"block", "bracket", "cowl", "rib_right", "rib_left"}
NEW_KEYS = {
    "starter",
    "alternator",
    "magnetos",
    "carburettor",
    "fuel_pump",
    "mount_pads",
}
BUILDERS = {
    "crankcase": L.crankcase,
    "cylinders": L.cylinders,
    "sump": L.sump,
    "accessory_housing": L.accessory_housing,
    "crank_flange": L.crank_flange,
    "starter": L.starter,
    "alternator": L.alternator,
    "magnetos": L.magnetos,
    "carburettor": L.carburettor,
    "fuel_pump": L.fuel_pump,
    "mount_pads": L.mount_pads,
}
NOT_AFT_LIMITED = {"crank_flange"}  # the stub and disc may lie aft of the flange


def comp(wp):
    return cq.Compound.makeCompound(wp.vals())


@pytest.mark.parametrize("name", sorted(BUILDERS))
def test_every_part_is_a_valid_positive_solid(name):
    wp = BUILDERS[name]()
    assert wp.vals()
    for s in wp.vals():
        assert s.isValid(), name
    assert comp(wp).Volume() > 0, name


@pytest.mark.parametrize("name", sorted(set(BUILDERS) - NOT_AFT_LIMITED))
def test_nothing_but_the_flange_is_aft_of_the_flange(name):
    assert comp(BUILDERS[name]()).BoundingBox().xmax <= FLANGE + 1e-6, name


def test_the_flange_disc_and_stub_are_what_pass_the_datum():
    b = comp(L.crank_flange()).BoundingBox()
    assert b.xmax > FLANGE  # the disc sits aft of the front face
    assert (
        b.xmax < FLANGE + 1.0
    )  # about one eighth bore, plus the pitch of the stub radius


@pytest.mark.parametrize("name", sorted(BUILDERS))
def test_nothing_is_forward_of_the_firewall(name):
    assert comp(BUILDERS[name]()).BoundingBox().xmin > G.fs_firewall, name


def test_four_cylinders_are_bore_sized():
    solids = comp(L.cylinders()).Solids()
    barrels = [
        s for s in solids if abs(s.BoundingBox().ylen - L.FITTED_BARREL_LEN) < 1e-6
    ]
    assert len(solids) == 8 and len(barrels) == 4  # four barrels and four heads
    for s in barrels:
        b = s.BoundingBox()
        d = max(b.xlen, b.zlen)
        assert G.eng_o235_bore_in <= d <= 1.5 * G.eng_o235_bore_in
    # two per bank, banks on both sides of the crank line
    ys = sorted(round(s.Center().y - G.eng_book_crank_bl, 3) for s in barrels)
    assert ys[0] < 0 < ys[-1] and ys[0] == ys[1] and ys[2] == ys[3]


def test_mount_pads_are_inside_the_cowl():
    cb = comp(ng.cowl()).BoundingBox()
    p = comp(L.mount_pads()).BoundingBox()
    assert len(comp(L.mount_pads()).Solids()) == 4
    assert cb.xmin <= p.xmin and p.xmax <= cb.xmax
    assert cb.ymin <= p.ymin and p.ymax <= cb.ymax
    assert cb.zmin + ng.FITTED_COWL_T <= p.zmin and p.zmax <= cb.zmax - ng.FITTED_COWL_T


def test_the_transform_round_trips_and_pitches_the_flange_end_up():
    for e in ((0.0, 0.0, 0.0), (12.3, -4.5, 6.7), (30.0, 2.0, -9.0)):
        assert L.to_engine(*L.to_fuselage(*e)) == pytest.approx(e, abs=1e-9)
    assert L.to_fuselage(0.0, 0.0, 0.0) == pytest.approx(
        (FLANGE, G.eng_book_crank_bl, z_of_wl(G.eng_book_block_wl))
    )
    # a point one inch toward the magneto end is one inch forward along the crank axis, a little LOWER than the flange point
    x, _y, z = L.to_fuselage(10.0, 0.0, 0.0)
    assert x < FLANGE and z < z_of_wl(G.eng_book_block_wl)
    assert math.degrees(
        math.atan2(z_of_wl(G.eng_book_block_wl) - z, FLANGE - x)
    ) == pytest.approx(G.eng_book_down_thrust_deg)


def test_a_monkeypatched_constant_takes_effect_on_rebuild(monkeypatch):
    before = comp(L.crankcase()).Volume()
    monkeypatch.setattr(L, "FITTED_CASE_WIDTH", L.FITTED_CASE_WIDTH * 1.25)
    assert comp(L.crankcase()).Volume() == pytest.approx(before * 1.25)


def test_build_engine_keeps_every_old_key_and_adds_the_accessories():
    parts = ng.build_engine()
    assert OLD_KEYS <= set(parts)
    assert NEW_KEYS <= set(parts)
    for k in NEW_KEYS:
        p = parts[k]
        assert p.fidelity == "representational" and p.cite and p.note
    # the block is now the crankcase, cylinders, sump, housing and crank flange: it holds case, 8 cylinder solids, sump, housing, stub and disc
    assert len(comp(parts["block"].solid).Solids()) == 1 + 8 + 1 + 1 + 2
    for k in ("crankcase", "cylinders", "sump", "accessory_housing", "crank_flange"):
        assert comp(BUILDERS[k]()).Volume() < comp(parts["block"].solid).Volume() + 1e-6


def test_every_new_alias_group_lists_real_parts():
    parts = ng.build_engine()
    assert {n for ns in ng.COMPONENT_PARTS.values() for n in ns} == set(parts)
    for k in NEW_KEYS:
        assert f"engine.{k}" in ng.COMPONENT_PARTS


def test_the_block_front_face_is_derived_from_the_flange():
    b = comp(ng.build_engine()["block"].solid).BoundingBox()
    assert ng.block_front_fs() == pytest.approx(b.xmin, abs=1e-6)
    assert ng.block_front_fs() < FLANGE
