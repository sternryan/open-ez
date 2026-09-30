# tests/guide/test_layup_geometry.py
"""Ply solids: valid, exact BL extents, stacked outward, and no overlap with the foam."""
from pathlib import Path

import pytest

from guide import layup
from guide.layup_geometry import Planform, _loft, build_layup
from guide.schema import load_graph
from core.structures import CanardGenerator

ROOT = Path(__file__).resolve().parents[2]
G = load_graph(ROOT / "guide" / "graph")


@pytest.fixture(scope="module")
def built():
    return build_layup(G)


def ply_solids(built):
    return {n: s for cid, v in built.items() if isinstance(v, dict) for n, s in v.items()}


def test_every_ply_is_a_valid_solid(built):
    solids = ply_solids(built)
    assert set(solids) == {p.node for p in layup.plies(G)}
    for n, s in solids.items():
        assert s.isValid() and s.Volume() > 1e-3, n


def test_bl_extents_are_exact(built):
    semi = CanardGenerator().span / 2
    solids = ply_solids(built)
    for p in layup.plies(G):
        ymax = solids[p.node].BoundingBox().ymax
        assert abs(ymax - (p.bl_max if p.bl_max is not None else semi)) < 1e-3, p.node


def test_skin_plies_stack_outward(built):
    top = [built["canard.skin_top"][f"canard.skin_top.p{i}"] for i in range(1, 5)]
    bot = [built["canard.skin_bottom"][f"canard.skin_bottom.p{i}"] for i in range(1, 4)]
    assert [s.BoundingBox().zmax for s in top] == sorted(s.BoundingBox().zmax for s in top)
    assert [s.BoundingBox().zmin for s in bot] == sorted((s.BoundingBox().zmin for s in bot), reverse=True)
    for a, b in zip(top, top[1:]):
        assert a.intersect(b).Volume() < 1e-4


def test_foam_does_not_overlap_web_or_caps(built):
    foam = built["canard.core"]
    assert foam.isValid() and foam.Volume() > 100.0
    for cid in ("canard.shear_web", "canard.spar_cap_bottom", "canard.spar_cap_top"):
        for n, s in built[cid].items():
            assert foam.intersect(s).Volume() < 1e-3, n


def test_surfaces_are_ordered_le_to_te_and_split_top_bottom():
    pf = Planform.from_generator(CanardGenerator())
    top, bot = pf.surface(5.0, "top"), pf.surface(5.0, "bottom")
    assert top[0, 0] < top[-1, 0] and bot[0, 0] < bot[-1, 0]
    assert top[:, 1].mean() > bot[:, 1].mean()


def vol(shape):
    """Accurate volume. cq's Shape.Volume() under-reads the BSPLINE-faced generator core by ~14% (598.6 vs 698.6)."""
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


CUTTERS = ("canard.shear_web", "canard.spar_cap_bottom", "canard.spar_cap_top")


def test_foam_volume_is_core_minus_cutters(built):
    core = CanardGenerator().generate_geometry().val()
    foam = built["canard.core"]
    # Ledger row 2: core.intersect(cutter) on the BSPLINE generator core is nondeterministic in OCCT
    # (a spar cap returned 0.0, then 32.4 on repeat), so measure the cutters against the same ruled
    # loft build_layup cuts, and check that loft still matches the generator core.
    pf = Planform.from_generator(CanardGenerator())
    base = _loft(lambda bl: pf.outline(bl)[:-1], 0.0, pf.semi_span)
    assert abs(vol(base) - vol(core)) < 0.01 * vol(core)
    removed = sum(vol(base.intersect(s)) for cid in CUTTERS for s in built[cid].values())
    assert vol(foam) <= vol(core) * 1.01
    assert abs(vol(foam) - (vol(base) - removed)) < 0.01 * vol(core)


def test_foam_section_at_bl5_is_whole_with_cavities(built):
    import cadquery as cq

    gen = CanardGenerator()
    core = gen.generate_geometry().val()
    foam = built["canard.core"]
    pf = Planform.from_generator(gen)
    slab = cq.Solid.makeBox(200, 0.1, 200, cq.Vector(-50, 4.95, -100))
    fs, cs = foam.intersect(slab), core.intersect(slab)
    bb = fs.BoundingBox()
    assert (bb.xmax - bb.xmin) >= 0.9 * pf.chord(5.0)
    assert vol(fs) < vol(cs) - 1e-3
    assert vol(fs) > 0.5 * vol(cs)


def test_cavity_cutters_overshoot_the_surface():  # coplanar tool faces broke the foam boolean
    from guide.layup_geometry import CUT_PAD, _spar_cap, _web_ply

    pf = Planform.from_generator(CanardGenerator())
    for p in layup.plies(G):
        if p.component == "canard.shear_web":
            plain, pad = _web_ply(pf, p).BoundingBox(), _web_ply(pf, p, CUT_PAD).BoundingBox()
            assert pad.zmax > plain.zmax + CUT_PAD / 2 and pad.zmin < plain.zmin - CUT_PAD / 2, p.node
        elif p.op in layup.SPAR_CAP_OPS:
            plain, pad = _spar_cap(pf, p).BoundingBox(), _spar_cap(pf, p, CUT_PAD).BoundingBox()
            out = pad.zmax - plain.zmax if p.component == "canard.spar_cap_top" else plain.zmin - pad.zmin
            assert out > CUT_PAD / 2, p.node


@pytest.mark.parametrize("side", ["top", "bottom"])
def test_surface_survives_a_one_ulp_tie_at_the_leading_edge(side):
    # The airfoil loop starts and ends on the LE point. On Linux the closing point came out 1 ULP below
    # the first, so a bare argmin picked the LAST point and the surface slice was empty.
    import dataclasses
    import numpy as np
    pf = Planform.from_generator(CanardGenerator())
    xn = pf.xn.copy()
    xn[-1] = np.nextafter(xn[0], -np.inf)
    nudged = dataclasses.replace(pf, xn=xn)
    assert np.allclose(nudged.surface(10.0, side), pf.surface(10.0, side), atol=1e-9)
