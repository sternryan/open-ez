"""Frozen layout of the book O-235 engine module: fitted dimensions and densities only.

This file holds NO geometry and NO mass code yet. The values below are set from the TCDS bore and
stroke and from stated proportions, never steered toward a result, and are hashed (layout_sha256)
and recorded in docs/geometry-correction-ledger.md row 70 before any centre-of-gravity code exists.
Changing any value needs a new ledger row with a new hash and a source.

Engine frame E (all lengths in inches):
- origin on the crankshaft centreline at the prop flange front face (the TCDS CG datum);
- u = inches FORWARD of the flange along the crank axis, toward the crankcase. On this pusher that
  is toward the firewall, so before the 2 deg pitch the airplane station is FS = flange_fs - u;
- v = lateral, positive to the airplane RIGHT (B.L. right positive, as core/fuselage_book);
- w = up from the crankshaft centreline.
Only the crank stub and flange disc may lie aft of the flange (u < 0 is allowed for the disc only);
every other part has u >= 0 including its extents. Nothing may pass the firewall (FS 125), so every
extent stays below 155.8 - 125 = 30.8 in of u, less an allowance for the pitch.

Part layout: crank stub runs from the flange (u = 0) to the case front; the disc sits aft of the
flange. Cylinders are horizontal (axis along v, at w = 0). Each bank has two cylinders at the
cylinder pitch; the engine-left bank is staggered toward the anti-prop (accessory) end. Cylinder
numbering (no. 1 front right) is from the inventory; the stagger direction is an assumption.

Left/right convention (assumed, not printed in a held source): Lycoming engine left/right is taken
as seen from the accessory end looking toward the prop. On this pusher the engine is turned end for
end, so engine-LEFT is airplane RIGHT. FITTED_LYCOMING_LEFT_V_SIGN = +1 records that: an engine-left
item sits at positive v. Set it to -1 only with a source. Any TCDS "left" number is engine-left.

Every FITTED_* constant is representational: a proportion of the bore or stroke (TCDS E-223 p1) or
a stated clearance, because no public dimensioned drawing of the engine exists. Pad positions follow
TCDS E-223 p4 NOTE 4 (starter, generator, plunger fuel pump, tach drives), magnetos at the
anti-prop rear upper left and right, carburettor on the sump bottom pad, starter and alternator at
the prop end (CP27 p4 puts them at FS 150 and aft). Accessory sizes are placeholders for the
residual-mass volume split; the accessories get published masses later.

Densities (lb/in^3) are handbook values for aluminium and steel with no registry source: flagged
unsourced.
"""

import hashlib
import json

from config.aircraft_config import config

_BORE = config.geometry.eng_o235_bore_in  # book: tcds-e223:p1
_STROKE = config.geometry.eng_o235_stroke_in  # book: tcds-e223:p1

# --- Left/right convention (see docstring) ---
FITTED_LYCOMING_LEFT_V_SIGN = 1  # representational: engine-left = airplane right on a pusher; unsourced assumption

# --- Crank stub and flange disc (the disc is the only part aft of the flange) ---
FITTED_CRANK_STUB_LEN = 1.0 * _BORE  # representational: shaft nose between flange and case about one bore
FITTED_CRANK_STUB_DIAM = 0.5 * _BORE  # representational: nose diameter about half a bore
FITTED_FLANGE_DISC_DIAM = 1.2 * _BORE  # representational: prop flange about 1.2 bore (AS-127 size not retrieved)
FITTED_FLANGE_DISC_THK = 0.125 * _BORE  # representational: disc thickness one eighth bore; extends aft of u = 0

# --- Crankcase ---
FITTED_CASE_U_START = FITTED_CRANK_STUB_LEN  # representational: case front face at the end of the stub
FITTED_CYL_OD = _BORE + 2 * 0.75  # representational: barrel OD = bore plus 0.75 in fin depth each side
FITTED_CYL_PITCH = FITTED_CYL_OD + 0.5  # representational: front-to-rear pair spacing = barrel OD plus 0.5 in clearance
FITTED_BANK_STAGGER = 0.25 * _BORE  # representational: opposed-bank stagger about a rod width, one quarter bore
FITTED_CASE_LEN = FITTED_CYL_PITCH + FITTED_CYL_OD + FITTED_BANK_STAGGER  # representational: spans both cylinder pairs and the stagger
FITTED_CASE_WIDTH = 3.0 * _STROKE  # representational: case between the banks about three strokes (crank swing plus webs)
FITTED_CASE_HEIGHT = 2.5 * _STROKE  # representational: case height about two and a half strokes, centred on the crank

# --- Cylinders (horizontal, axis along v at w = 0) ---
FITTED_BARREL_LEN = 1.5 * _STROKE  # representational: barrel length from the case face about 1.5 strokes
FITTED_HEAD_LEN = 1.0 * _BORE  # representational: head length beyond the barrel about one bore
FITTED_CYL_FRONT_U = FITTED_CASE_U_START + FITTED_CYL_OD / 2  # representational: engine-right front cylinder centre, one barrel radius inside the case front

# --- Sump (below the case) ---
FITTED_SUMP_U_START = FITTED_CASE_U_START + FITTED_CASE_LEN / 3  # representational: sump covers the rear two thirds of the case
FITTED_SUMP_LEN = FITTED_CASE_LEN * 2 / 3  # representational: rear two thirds of the case
FITTED_SUMP_WIDTH = 2.0 * _BORE  # representational: sump about two bores wide
FITTED_SUMP_DEPTH_BELOW_CL = FITTED_CASE_HEIGHT / 2 + _STROKE  # representational: case half-height plus one stroke of sump depth

# --- Accessory housing (anti-prop end, FORWARD end on this pusher) ---
FITTED_ACC_U_START = FITTED_CASE_U_START + FITTED_CASE_LEN  # representational: housing starts at the case rear face
FITTED_ACC_DEPTH = 1.0 * _STROKE  # representational: housing depth about one stroke
FITTED_ACC_WIDTH = 2.5 * _STROKE  # representational: housing width about 2.5 strokes
FITTED_ACC_HEIGHT = 2.0 * _STROKE  # representational: housing height about two strokes

# --- Accessories: (u, v, w) centre and size. Boxes are (du, dv, dw). ---
_ACC_END_U = FITTED_ACC_U_START + FITTED_ACC_DEPTH  # private: the anti-prop face of the housing
_L = FITTED_LYCOMING_LEFT_V_SIGN
FITTED_STARTER_SIZE = (0.8 * FITTED_CRANK_STUB_LEN, 1.0 * _BORE, 1.0 * _BORE)  # representational: starter at the prop end, inside the stub length, one bore across
FITTED_STARTER_POS = (0.5 * FITTED_CRANK_STUB_LEN, _L * 0.25 * FITTED_CASE_WIDTH, -0.25 * FITTED_CASE_HEIGHT)  # representational: CP27 p4 prop end; engine-left lower side assumed
FITTED_ALTERNATOR_SIZE = (0.6 * FITTED_CRANK_STUB_LEN, 0.8 * _BORE, 0.8 * _BORE)  # representational: belt alternator at the prop end, 0.8 bore across
FITTED_ALTERNATOR_POS = (0.5 * FITTED_CRANK_STUB_LEN, -_L * 0.25 * FITTED_CASE_WIDTH, 0.25 * FITTED_CASE_HEIGHT)  # representational: CP27 p4 prop end; engine-right upper side assumed
FITTED_MAGNETO_SIZE = (1.0 * _BORE, 0.8 * _BORE, 0.8 * _BORE)  # representational: magneto one bore long, 0.8 bore across
FITTED_MAGNETO_LEFT_POS = (_ACC_END_U + 0.5 * FITTED_MAGNETO_SIZE[0], _L * 0.3 * FITTED_ACC_WIDTH, 0.3 * FITTED_ACC_HEIGHT)  # representational: rear (anti-prop) face, upper engine-left
FITTED_MAGNETO_RIGHT_POS = (_ACC_END_U + 0.5 * FITTED_MAGNETO_SIZE[0], -_L * 0.3 * FITTED_ACC_WIDTH, 0.3 * FITTED_ACC_HEIGHT)  # representational: rear face, upper engine-right
FITTED_CARB_SIZE = (1.0 * _BORE, 1.0 * _BORE, 0.8 * _BORE)  # representational: carburettor about one bore square
FITTED_CARB_POS = (FITTED_SUMP_U_START + FITTED_SUMP_LEN / 2, 0.0, -(FITTED_SUMP_DEPTH_BELOW_CL + 0.5 * FITTED_CARB_SIZE[2]))  # representational: sump bottom pad, centred on the sump, on the centreline
FITTED_FUEL_PUMP_SIZE = (0.5 * _BORE, 0.7 * _BORE, 0.7 * _BORE)  # representational: plunger pump about 0.7 bore across
FITTED_FUEL_PUMP_POS = (_ACC_END_U + 0.5 * FITTED_FUEL_PUMP_SIZE[0], _L * 0.3 * FITTED_ACC_WIDTH, -0.25 * FITTED_ACC_HEIGHT)  # representational: TCDS p4 NOTE 4 plunger pump, rear pad, engine-left, lower

# --- Dynafocal mount pads: four, each (u, v, w); size is (diameter, length along u) ---
FITTED_MOUNT_PAD_SIZE = (0.4 * _BORE, 0.4 * _BORE)  # representational: small pad, 0.4 bore
FITTED_MOUNT_PAD_POS = (
    (FITTED_ACC_U_START, 0.4 * FITTED_CASE_WIDTH, 0.4 * FITTED_CASE_HEIGHT),
    (FITTED_ACC_U_START, -0.4 * FITTED_CASE_WIDTH, 0.4 * FITTED_CASE_HEIGHT),
    (FITTED_ACC_U_START, 0.4 * FITTED_CASE_WIDTH, -0.4 * FITTED_CASE_HEIGHT),
    (FITTED_ACC_U_START, -0.4 * FITTED_CASE_WIDTH, -0.4 * FITTED_CASE_HEIGHT),
)  # representational: four pads on a rectangle at the case rear face (Section IIL not held)

# --- Densities, lb per cubic inch ---
DENSITY_ALUMINIUM = 0.0975  # unsourced: handbook aluminium alloy, no registry source
DENSITY_STEEL = 0.283  # unsourced: handbook steel, no registry source
DENSITY_BY_PART = {
    "crankcase": "aluminium",
    "crank_stub": "steel",
    "flange_disc": "steel",
    "cylinder_barrel": "steel",
    "cylinder_head": "aluminium",
    "sump": "aluminium",
    "accessory_housing": "aluminium",
    "carburettor": "aluminium",
    "fuel_pump": "aluminium",
}  # representational: material per residual-mass part (starter, alternator, magnetos get published masses)


def _canon(v):
    if isinstance(v, dict):
        return {k: _canon(v[k]) for k in sorted(v)}
    if isinstance(v, (tuple, list)):
        return [_canon(x) for x in v]
    return v


def layout_sha256() -> str:
    """sha256 hex of every FITTED_* and DENSITY_* global, read at call time, sorted by name."""
    names = sorted(n for n in globals() if n.startswith(("FITTED_", "DENSITY_")))
    blob = json.dumps({n: _canon(globals()[n]) for n in names}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


# =====================================================================================================================
# Task 3 and 4 code: geometry, placement and mass properties. Nothing above this line may change (row 70 hash).
# Every function reads the FITTED_* and DENSITY_* globals at call time (no cache, no default-argument capture), so a
# monkeypatched constant takes effect on the next build. No new global here starts with FITTED_ or DENSITY_.
# =====================================================================================================================
import math
from typing import NamedTuple

import cadquery as cq

from .fuselage_book import z_of_wl

_G = config.geometry


# ---- the one shared transform: frame E <-> fuselage frame ------------------------------------------------------------
def _datum() -> tuple[float, float, float]:
    """The flange point in the fuselage frame: (FS of the prop flange face, crank BL, z of the crank centreline).
    The crank-line WL (eng_book_block_wl) is unsourced: no held page gives a crank or prop height."""
    return _G.eng_o235_flange_fs, _G.eng_book_crank_bl, z_of_wl(_G.eng_book_block_wl)


def to_fuselage(u: float, v: float, w: float) -> tuple[float, float, float]:
    """Engine frame E (u forward of the flange along the crank, v airplane right, w up) -> fuselage frame (x = FS, y = BL, z = z_of_wl).
    Unpitched: x = flange_fs - u, y = crank_bl + v, z = z_crank + w. Then a turn about +y through the flange point by -DOWN_THRUST_DEG,
    which takes +x (aft, the prop flange end) toward +z: the flange end is higher than the magneto end, as engine_book.block() did."""
    fx, fy, fz = _datum()
    dx, dz = -u, w
    a = math.radians(-_G.eng_book_down_thrust_deg)
    return (
        fx + dx * math.cos(a) + dz * math.sin(a),
        fy + v,
        fz - dx * math.sin(a) + dz * math.cos(a),
    )


def to_engine(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Inverse of to_fuselage: a fuselage point -> (u, v, w) in frame E."""
    fx, fy, fz = _datum()
    a = math.radians(-_G.eng_book_down_thrust_deg)
    px, pz = x - fx, z - fz
    dx = px * math.cos(a) - pz * math.sin(a)
    dz = px * math.sin(a) + pz * math.cos(a)
    return -dx, y - fy, dz


def _place(shape):
    """Rotate an unpitched, flange-anchored shape about the flange point (the same turn as to_fuselage)."""
    fx, fy, fz = _datum()
    return shape.rotate(
        cq.Vector(fx, fy, fz), cq.Vector(fx, fy + 1.0, fz), -_G.eng_book_down_thrust_deg
    )


def _ebox(u0, u1, v0, v1, w0, w1):
    """An unpitched box given in frame E extents."""
    fx, fy, fz = _datum()
    return cq.Solid.makeBox(
        u1 - u0, v1 - v0, w1 - w0, cq.Vector(fx - u1, fy + v0, fz + w0)
    )


def _ecyl_u(u0, u1, v, w, r):
    fx, fy, fz = _datum()
    return cq.Solid.makeCylinder(
        r, u1 - u0, cq.Vector(fx - u1, fy + v, fz + w), cq.Vector(1, 0, 0)
    )


def _ecyl_v(u, v0, v1, w, r):
    fx, fy, fz = _datum()
    return cq.Solid.makeCylinder(
        r, v1 - v0, cq.Vector(fx - u, fy + v0, fz + w), cq.Vector(0, 1, 0)
    )


def _wp(shapes) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound([_place(s) for s in shapes]))


def _centred_box(pos, size):
    (pu, pv, pw), (du, dv, dw) = pos, size
    return _ebox(
        pu - du / 2, pu + du / 2, pv - dv / 2, pv + dv / 2, pw - dw / 2, pw + dw / 2
    )


# ---- components (each a placed cq.Workplane in the fuselage frame) -----------------------------------------------------
def _crankcase_solids():
    u0 = FITTED_CASE_U_START
    return [
        _ebox(
            u0,
            u0 + FITTED_CASE_LEN,
            -FITTED_CASE_WIDTH / 2,
            FITTED_CASE_WIDTH / 2,
            -FITTED_CASE_HEIGHT / 2,
            FITTED_CASE_HEIGHT / 2,
        )
    ]


def crankcase() -> cq.Workplane:
    return _wp(_crankcase_solids())


def _cylinder_solids():
    """(barrels, heads): four horizontal cylinders, two per bank. Engine-left is at v = LEFT_V_SIGN * (+). The engine-left bank is staggered toward the accessory end."""
    barrels, heads = [], []
    r = FITTED_CYL_OD / 2
    half = FITTED_CASE_WIDTH / 2
    for side, stagger in (
        (-FITTED_LYCOMING_LEFT_V_SIGN, 0.0),
        (FITTED_LYCOMING_LEFT_V_SIGN, FITTED_BANK_STAGGER),
    ):
        for k in (0, 1):
            u = FITTED_CYL_FRONT_U + stagger + k * FITTED_CYL_PITCH
            b0, b1 = side * half, side * (half + FITTED_BARREL_LEN)
            h1 = side * (half + FITTED_BARREL_LEN + FITTED_HEAD_LEN)
            barrels.append(_ecyl_v(u, min(b0, b1), max(b0, b1), 0.0, r))
            heads.append(_ecyl_v(u, min(b1, h1), max(b1, h1), 0.0, r))
    return barrels, heads


def cylinders() -> cq.Workplane:
    b, h = _cylinder_solids()
    return _wp(b + h)


def _sump_solids():
    w0 = -FITTED_SUMP_DEPTH_BELOW_CL
    return [
        _ebox(
            FITTED_SUMP_U_START,
            FITTED_SUMP_U_START + FITTED_SUMP_LEN,
            -FITTED_SUMP_WIDTH / 2,
            FITTED_SUMP_WIDTH / 2,
            w0,
            -FITTED_CASE_HEIGHT / 2,
        )
    ]


def sump() -> cq.Workplane:
    return _wp(_sump_solids())


def _housing_solids():
    return [
        _ebox(
            FITTED_ACC_U_START,
            FITTED_ACC_U_START + FITTED_ACC_DEPTH,
            -FITTED_ACC_WIDTH / 2,
            FITTED_ACC_WIDTH / 2,
            -FITTED_ACC_HEIGHT / 2,
            FITTED_ACC_HEIGHT / 2,
        )
    ]


def accessory_housing() -> cq.Workplane:
    return _wp(_housing_solids())


def _stub_solids():
    return [_ecyl_u(0.0, FITTED_CRANK_STUB_LEN, 0.0, 0.0, FITTED_CRANK_STUB_DIAM / 2)]


def _disc_solids():
    return [
        _ecyl_u(-FITTED_FLANGE_DISC_THK, 0.0, 0.0, 0.0, FITTED_FLANGE_DISC_DIAM / 2)
    ]


def crank_flange() -> cq.Workplane:
    """The crank stub (u 0 to the case front) and the prop flange disc (the only solid aft of u = 0)."""
    return _wp(_stub_solids() + _disc_solids())


def _starter_solids():
    return [_centred_box(FITTED_STARTER_POS, FITTED_STARTER_SIZE)]


def starter() -> cq.Workplane:
    return _wp(_starter_solids())


def _alternator_solids():
    return [_centred_box(FITTED_ALTERNATOR_POS, FITTED_ALTERNATOR_SIZE)]


def alternator() -> cq.Workplane:
    return _wp(_alternator_solids())


def _magneto_solids():
    return [
        _centred_box(FITTED_MAGNETO_LEFT_POS, FITTED_MAGNETO_SIZE),
        _centred_box(FITTED_MAGNETO_RIGHT_POS, FITTED_MAGNETO_SIZE),
    ]


def magnetos() -> cq.Workplane:
    return _wp(_magneto_solids())


def _carb_solids():
    return [_centred_box(FITTED_CARB_POS, FITTED_CARB_SIZE)]


def carburettor() -> cq.Workplane:
    return _wp(_carb_solids())


def _pump_solids():
    return [_centred_box(FITTED_FUEL_PUMP_POS, FITTED_FUEL_PUMP_SIZE)]


def fuel_pump() -> cq.Workplane:
    return _wp(_pump_solids())


def _pad_solids():
    d, ln = FITTED_MOUNT_PAD_SIZE
    return [
        _ecyl_u(pu - ln / 2, pu + ln / 2, pv, pw, d / 2)
        for pu, pv, pw in FITTED_MOUNT_PAD_POS
    ]


def mount_pads() -> cq.Workplane:
    """The four dynafocal pads: small cylinders along the crank axis. The mount is owned by the closure row engine_mount, not by this module's dry weight."""
    return _wp(_pad_solids())


# ---- mass properties ------------------------------------------------------------------------------------------------------
class MassRow(NamedTuple):
    name: str
    mass_lb: float
    band: tuple | None  # published band (lb), None for a residual core row
    cg_xyz: tuple  # volume centroid of the placed solid, fuselage frame (FS, BL, z)
    status: str  # "derived" (sourced mass) or "representational" (residual share)
    cite: tuple


class EngineMass(NamedTuple):
    total_lb: float
    cg_fs: float
    cg_bl: float
    cg_wl: float
    rows: list


def _centroid(shapes) -> tuple[float, float, float]:
    c = cq.Compound.makeCompound([_place(s) for s in shapes]).Center()
    return c.x, c.y, c.z


def _volume(shapes) -> float:
    return sum(s.Volume() for s in shapes)


_VARIANTS = {
    "H2C",
    "C1C",
}  # both dynafocal-capable C-series dash numbers on one TCDS NOTE 8 weight and CG
_DENS = {"aluminium": "DENSITY_ALUMINIUM", "steel": "DENSITY_STEEL"}


def _density(part: str) -> float:
    return globals()[_DENS[DENSITY_BY_PART[part]]]


def _wl_of_z(z: float) -> float:
    return z - z_of_wl(0.0)


def dry_weight_lb() -> float:
    from config.aircraft_config import PropulsionConfig

    return (
        PropulsionConfig().engine_dry_weight_lb
    )  # derived: tcds-e223:p7 NOTE 8, the closure engine row figure


def engine_mass_properties(variant: str = "H2C") -> EngineMass:
    """Component mass table. Sourced rows (starter, alternator, magnetos) carry their published masses; the core is TCDS dry weight less those, shared by
    solid volume times DENSITY_BY_PART density and scaled so the core sums exactly to the residual. Each row's cg_xyz is its placed solid's volume centroid.
    The mount pads are NOT in the dry weight (the closure row engine_mount owns the mount) and are excluded here."""
    if variant not in _VARIANTS:
        raise ValueError(f"variant {variant!r} not in {sorted(_VARIANTS)}")
    sourced = [
        ("starter", 17.0, (16.7, 17.2), _starter_solids(), ("cp-text:p49",)),
        (
            "alternator",
            7.0,
            (4.25, 9.0),
            _alternator_solids(),
            ("cp-text:p49", "cp-text:p26"),
        ),
        # TCDS names Slick 4251/4250 for C1C/H2C; the vendor weight is the 4300 series, so this is a nearest-type figure
        (
            "magnetos",
            2 * 3.75,
            (2 * 3.75, 2 * 6.25),
            _magneto_solids(),
            ("vendor-slick-4300:p1", "tcds-e223:p7"),
        ),
    ]
    barrels, heads = _cylinder_solids()
    core = [
        ("crankcase", "crankcase", _crankcase_solids()),
        ("crank_stub", "crank_stub", _stub_solids()),
        ("flange_disc", "flange_disc", _disc_solids()),
        ("cylinder_barrels", "cylinder_barrel", barrels),
        ("cylinder_heads", "cylinder_head", heads),
        ("sump", "sump", _sump_solids()),
        ("accessory_housing", "accessory_housing", _housing_solids()),
        ("carburettor", "carburettor", _carb_solids()),
        ("fuel_pump", "fuel_pump", _pump_solids()),
    ]
    residual = dry_weight_lb() - sum(m for _n, m, _b, _s, _c in sourced)
    raw = {n: _volume(s) * _density(d) for n, d, s in core}
    scale = residual / sum(raw.values())
    rows = [MassRow(n, m, b, _centroid(s), "derived", c) for n, m, b, s, c in sourced]
    rows += [
        MassRow(
            n, raw[n] * scale, None, _centroid(s), "representational", ("tcds-e223:p7",)
        )
        for n, _d, s in core
    ]
    total = sum(r.mass_lb for r in rows)
    cg = [sum(r.mass_lb * r.cg_xyz[i] for r in rows) / total for i in range(3)]
    return EngineMass(total, cg[0], cg[1], _wl_of_z(cg[2]), rows)


def cg_in_engine_frame(m: EngineMass) -> tuple[float, float, float]:
    """The CG of an EngineMass as (u, v, w) in frame E, through the inverse transform."""
    return to_engine(m.cg_fs, m.cg_bl, m.cg_wl + z_of_wl(0.0))
