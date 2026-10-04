"""
Open-EZ PDE: Single Source of Truth (SSOT)
==========================================

This configuration file defines ALL parametric constants for the Long-EZ.
NEVER hard-code dimensions elsewhere. All geometry, analysis, and documentation
derive from these variables.

Safety Mandate: Roncz R1145MS canard airfoil is the DEFAULT.
The original GU25-5(11)8 caused dangerous pitch-down in rain.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class AirfoilType(Enum):
    """Supported airfoil profiles."""

    RONCZ_R1145MS = "roncz_r1145ms"  # MANDATORY canard airfoil (rain-safe)
    EPPLER_1230_MOD = "eppler_1230_mod"  # Main wing (with reflex)
    GU25_5_11_8 = "gu25_5_11_8"  # DEPRECATED - unsafe in rain


class FoamType(Enum):
    """Foam core materials with thermal properties for hot-wire cutting."""

    STYROFOAM_BLUE = "styrofoam_blue"  # 2 lb/ft³ - Standard wing cores
    URETHANE_2LB = "urethane_2lb"  # 2 lb/ft³ - Higher temp resistance
    DIVINYCELL_H45 = "divinycell_h45"  # Structural foam - fuselage


class BuildMethod(Enum):
    """Fuselage construction method."""

    BOW_FOAM = "bow_foam"  # Classic Rutan: flat slabs bowed into curves
    CNC_MILLED = "cnc_milled"  # Modern: 5-axis CNC milled foam blocks


class PropulsionType(Enum):
    """Powerplant options."""

    LYCOMING_O235 = "lycoming_o235"  # 115 HP gasoline (baseline)
    LYCOMING_O320 = "lycoming_o320"  # 150 HP gasoline (performance)
    ELECTRIC_LIFEPO4 = "electric_lifepo4"  # LiFePO4 battery electric
    ELECTRIC_NMC = "electric_nmc"  # NMC battery electric (higher density)


class GrainConstraint(Enum):
    """Material grain/fiber orientation constraints for nesting."""

    NONE = "none"  # No grain constraint
    PARALLEL = "parallel"  # Grain must align with primary load path
    PERPENDICULAR = "perpendicular"  # Grain perpendicular to load path
    SPECIFIC = "specific"  # Specific angle required (see grain_angle)


@dataclass
class Ply:
    """Single composite ply definition."""

    material: str
    orientation: float
    thickness: Optional[float] = None


@dataclass
class LaminateDefinition:
    """Stack of plies used for layups and manufacturing prep."""

    name: str
    plies: List[Ply] = field(default_factory=list)
    notes: str = ""

    def total_thickness(self, ply_lookup: Dict[str, float]) -> float:
        """Compute total laminate thickness using a ply thickness lookup."""
        thickness = 0.0
        for ply in self.plies:
            base = ply.thickness
            if base is None:
                base = ply_lookup.get(ply.material.lower(), 0.0)
            thickness += base
        return thickness

    def cut_order_steps(self) -> List[str]:
        """Describe recommended CAM steps for this laminate."""
        return ["engrave_labels", "pocket_features", "profile_cut"]


# Canard chord: the Roncz chord was not found (docs/block1-source-notes.md, Roncz canard); the GU
# planform from the manual is used: 12.8 sq ft * 144 / 141.6 in (11.8 ft).
CHORD = 13.02
CHORD_STATUS = "conflict"
CHORD_SOURCE = "om-1980:p3 GU canard 11.8 ft, 12.8 sq ft"


@dataclass
class GeometricParams:
    """Primary aircraft geometry - all dimensions in inches unless noted."""

    # === MAIN WING (Eppler 1230 Modified) ===
    wing_span: float = 314.0  # Total span, 2 x tip rib BL 157 (plans-1980:p126); OM 26.1 ft = 313.2 is a conflict
    wing_root_chord: float = (
        49.97  # Root chord at BL 23.0, derived (see GEOMETRY_PROVENANCE)
    )
    wing_tip_chord: float = 20.0  # Tip chord at B.L. 157 (plans-1980:p126)
    wing_sweep_le: float = 22.98  # Leading edge sweep (degrees), plans-1980:p126
    wing_dihedral: float = 0.0  # wing jigged flat (plans-1980:p134); no angle printed
    wing_washout: float = 1.0  # Tip washout (degrees)
    wing_incidence: float = 0.0  # Relative to longerons (degrees)
    wing_oswald_e: float = 0.80  # Oswald efficiency factor (typical for tapered wing)

    # === CANARD (Roncz R1145MS - SAFETY CRITICAL) ===
    canard_span: float = 141.6  # GU planform 11.8 ft (om-1980:p3); Roncz planform unconfirmed (core jig blocks 126 apart, cobelu:p13)
    canard_chord: float = (
        CHORD  # constant chord (GU planform rectangle); see GEOMETRY_PROVENANCE
    )
    canard_sweep_le: float = 0.0  # zero sweep (plans p.71)
    canard_incidence: float = -1.5  # Relative to longerons (degrees)
    canard_oswald_e: float = 0.75  # Oswald efficiency factor (lower AR, less efficient)

    # === FUSELAGE STATIONS (FS) ===
    fs_nose: float = -6.8  # book: plans-1980:p171 nose tip F.S. -6.8
    fs_canard_le: float = 18.7  # plans back cover, p.171
    fs_pilot_seat: float = 59.0  # book: pilot CG station, om-1980:p25 (not a bulkhead; F22 is a forward bulkhead)
    fs_rear_seat: float = 103.0  # book: passenger CG station, om-1980:p25 (not a bulkhead; F28 is a forward bulkhead)
    fs_firewall: float = 125.0  # book: plans-1980:p101 firewall line at F.S. 125
    fs_tail: float = 168.5  # converted-unsourced (internal 214.0 shifted); no printed aft-end station
    wing_root_bl: float = 23.0  # wing root butt line, plans-1980:p118/p119/p126/p147
    wing_le_anchor: Tuple[float, float] = (
        113.9,
        58.0,
    )  # (FS, BL): wing LE at the strake junction, CP25 LPC 7

    # === FUSELAGE BOOK GEOMETRY (chapters 4-6) ===
    # FS = side x + 22: side length 103 (plans-1980:p36) ends at fs_firewall 125 (plans-1980:p101).
    fs_f22: float = 22.0  # derived: 125 - 103
    fs_f28: float = 27.65  # derived: side x 5.65
    fs_panel: float = 39.75  # derived: side x 17.75
    fs_front_seat_bkhd_bottom: float = 63.55  # derived: side x 41.55
    fs_front_seat_bkhd_top: float = 81.75  # derived: side x 59.75
    fs_rear_seat_bkhd_bottom: float = 107.0  # derived: side x 103 - 18.0
    fs_rear_seat_bkhd_top: float = 118.5  # derived: side x 59.75 + 36.75 = 96.5
    side_panel_length: float = 103.0  # book plans-1980:p36
    side_panel_top_wl: float = 23.0  # book plans-1980:p36
    side_panel_thickness: float = 0.8
    # (x from front, depth down from the top edge)
    side_panel_heights: Tuple[Tuple[float, float], ...] = (
        (0, 19.8),
        (10, 20.3),
        (20, 20.5),
        (30, 20.5),
        (40, 20.5),
        (50, 20.5),
        (60, 20.5),
        (70, 20.4),
        (80, 19.8),
        (90, 18.4),
        (100, 16.6),
        (103, 16.0),
    )
    side_spar_cutout: Tuple[float, float] = (
        6.5,
        8.5,
    )  # (width at aft end, depth from top)
    side_sight_gauge: Tuple[float, float, float, float, float] = (
        82.0,
        9.15,
        2.5,
        1.0,
        0.2,
    )
    side_dish: Tuple[float, float, float, float] = (
        24.75,
        7.0,
        8.0,
        0.5,
    )  # (x, down, dia, depth)
    front_seat_bkhd_length: float = 28.3
    front_seat_bkhd_width: float = 23.0
    front_seat_bkhd_thickness: float = 0.8
    front_seat_bkhd_taper: float = 0.7
    front_seat_bkhd_notch_top: Tuple[float, float] = (0.7, 1.5)
    front_seat_bkhd_notch_bottom: Tuple[float, float] = (0.7, 0.7)
    rear_seat_bkhd_bottom_width: float = 20.6
    rear_seat_bkhd_top_width: float = 18.7
    rear_seat_bkhd_length: float = 16.1  # slant height
    rear_seat_bkhd_thickness: float = 0.8
    rear_seat_bkhd_side_taper: float = 0.95
    rear_seat_bkhd_bevel_top_deg: float = 45.0
    rear_seat_bkhd_bevel_bottom_deg: float = 35.0
    rear_seat_bkhd_notch: Tuple[float, float] = (0.7, 1.4)
    rear_seat_bkhd_access_dia: float = 7.0
    rear_seat_bkhd_foam_circle_dia: float = 8.0
    # (FS, inner width between the sides)
    fuselage_inner_width_stations: Tuple[Tuple[float, float], ...] = (
        (63.55, 23.0),
        (81.75, 23.0),
        (107.0, 20.6),
        (118.5, 18.7),
    )
    fuselage_inner_width_fwd: float = (
        23.0  # unsourced: forward of the front seat bulkhead
    )
    bottom_foam_thickness: float = 1.6
    bottom_trim_outboard: float = 0.7
    bottom_aft_trim: float = 0.25

    # === EXTERIOR, ROLL-OVER AND MAIN GEAR (chapters 7-9, plans-1980:p46-p53, p171) ===
    fs_spar_aft_face: float = 125.5  # book: p50 aft face of the center section spar
    bl_gear_datum: float = 26.75  # book: p50 straight-board datum at the spar aft face
    main_axle_fwd_of_spar: float = 15.0  # book: p50
    wl_main_axle: float = -22.0  # book: p171
    fs_nose_wheel: float = (
        17.0  # conflict: p171 prints 17, the Owner's Manual says about 20
    )
    wl_nose_wheel: float = -22.0  # cp-corrected: CP25 LPC 24
    ng50_travel_deg: float = 156.0  # book: p73 NG50 arms travel 156 deg
    nose_crank_turns: float = 10.8  # book: p73 full travel
    nose_crank_seconds_min: float = 5.0  # book: p73 five to seven seconds
    nose_crank_seconds_max: float = 7.0
    wl_fuselage_bottom_3view: float = (
        0.9  # book, medium: p171 side view label at the fuselage bottom line
    )
    gear_tip_back_deg: float = 12.0  # book: p171 line from the main contact
    gear_toe_in_b_minus_a: Tuple[float, float] = (
        0.2,
        0.45,
    )  # book: p52, over gear_toe_in_square_in
    gear_toe_in_square_in: float = 24.0
    # skins and belt insert
    skin_third_ply_fs_range: Tuple[float, float] = (60.0, 110.0)  # derived: p46
    skin_strip_width: float = 3.0
    skin_strip_lengths: Tuple[float, float, float] = (52.0, 50.0, 48.0)
    skin_firewall_lap: float = 0.5
    skin_bottom_overlap: float = 2.0
    skin_ply_angle_deg: float = 30.0
    belt_insert_fs_range: Tuple[float, float] = (49.7, 54.7)  # derived: p46, medium
    # roll-over box (p47, p48)
    rollover_width: float = 23.0
    rollover_base_height: float = 4.0
    rollover_shoulder: float = 7.3
    rollover_peak_base: float = 8.4
    rollover_peak_height: float = 12.6
    rollover_notch: Tuple[float, float] = (0.7, 1.4)
    rollover_side_length: float = 13.0  # cp-corrected: CP26 LPC 37 (printed 12.7)
    rollover_side_ends: Tuple[float, float] = (3.0, 4.5)
    rollover_back_triangle: Tuple[float, float] = (8.1, 12.7)
    rollover_shoulder_top: Tuple[float, float] = (6.9, 2.7)
    rollover_foam_thickness: float = 0.35
    rollover_insert: Tuple[float, float, float] = (1.25, 1.25, 0.25)
    rollover_harness_insert_spacing: float = (
        4.0  # cp-corrected: CP27 LPC 52 (printed 4.5)
    )
    rollover_harness_insert_from_end: float = 1.25
    rollover_canopy_insert_from_peak: Tuple[float, float] = (1.5, 1.25)
    rollover_map_slot: Tuple[float, float] = (1.8, 8.0)  # right side only
    rollover_baggage_hole_dia: float = 3.75
    # belts and step (p49)
    belt_front_fwd_of_front_seat_bkhd: float = 5.0  # hand sketch
    belt_rear_fwd_of_rear_seat_bkhd: float = 8.0  # hand sketch
    step_size: Tuple[float, float, float] = (1.8, 4.5, 4.5)
    step_thickness: float = 0.125
    step_min_bend_radius: float = 0.5
    # gear jig and hardware (p50-p53)
    gear_jig_block: Tuple[float, float, float, float, float, float] = (
        2.0,
        1.0,
        0.625,
        0.7,
        0.8,
        0.25,
    )
    # (width, top radius, hole dia, below hole, bevel, thickness)
    gear_tube: Tuple[float, float, float] = (
        0.625,
        0.049,
        6.75,
    )  # (OD, wall, length), 4130N
    gear_tube_showing: float = 0.65
    gear_tab_pads: Tuple[Tuple[float, float], ...] = (
        (2.5, 12.0),
        (2.5, 3.5),
        (2.5, 2.5),
    )
    gear_extrusion: Tuple[float, float, float] = (0.25, 2.0, 2.0)  # 6061-T6

    # === NOSE, NOSE GEAR BOX AND ROUND-NOSE ELEVATORS (chapters 11-13) ===
    # nose box and nose gear (plans-1980 pdf pages p73-p82). No strut rake, NG6 position, fork offset or trail:
    # they live on the A6/A7 sheets the owner does not hold.
    fs_nose_wheel_manual: float = 20.0  # conflict: om-1980:p35 nose arm "about 20" (sample 19.6); pair with fs_nose_wheel
    ng6_width_in: float = 2.75  # book: p73
    ng6_bore_height_in: float = 1.25  # book: p73
    ng7_length_in: float = 2.75  # book: p73
    ng30_thickness_in: float = 0.2  # book: p77
    ng30_gap_in: float = 3.0  # book: p77 inside gap between the plates
    ng3_to_ng7_in: float = 6.71  # book: p78 (tolerance 0.05)
    nose_strut_pivot_to_pivot_in: float = 25.5  # book, medium: p81
    floor_block_length_in: float = 20.9  # book, medium: p79
    floor_block_width_in: float = (
        8.2  # book, medium: p79 (which end is 8.2 vs 1.6 is a reading)
    )
    floor_block_thickness_in: float = 1.6  # book, medium: p79
    side_block_length_in: float = 21.9  # book, medium: p79
    side_block_height_f22_in: float = 15.6  # book, medium: p79
    side_block_height_ng31_above_in: float = 5.5  # book, medium: p79
    side_block_height_ng31_below_in: float = 2.8  # book, medium: p79
    top_block_length_in: float = 19.3  # book, medium: p82
    top_block_width_aft_in: float = 19.6  # book, medium: p82
    top_block_width_fwd_in: float = 7.0  # book, medium: p82
    pedal_block_from_ng30_in: float = 6.1  # book: p79
    static_port_fwd_of_panel_in: float = (
        8.0  # book: p82; static port is on the LEFT side
    )
    wl_static_port: float = 13.0  # book: p82 (10 below the top longerons)
    # Roncz elevators (cobelu ch30 text and figures; the owner holds no scan of them)
    elevator_length_right_in: float = 55.7  # cobelu fig C-1
    elevator_length_left_in: float = 72.7  # cobelu fig C-1
    elevator_travel_up_target_deg: float = 15.0  # cobelu ch30
    elevator_travel_up_floor_deg: float = 12.5  # cobelu ch30, absolute floor
    elevator_travel_down_deg: float = 30.0  # cobelu ch30
    elevator_outboard_end_bl_in: float = 65.0  # cobelu fig C-1 plan dimension from B.L. 0; both elevators end here (left on -B.L.)
    elevator_hinge_bl_in: Tuple[float, float, float] = (
        9.2,
        34.1,
        59.0,
    )  # positioned-from-text, low
    elevator_hinge_bl_right_first_drawn_in: float = (
        7.8  # the right side draws the first hinge here
    )
    elevator_slot_gap_in: float = 0.2
    elevator_hinge_offset_in: float = 0.55
    elevator_tube_od_in: float = 1.0
    elevator_pin_right_in: float = 36.0
    elevator_pin_left_in: float = 61.0
    cs11_lead_dims: Tuple[float, float, float] = (2.0, 0.6, 0.8)
    cs10_inboard_from_end_in: float = 7.5
    balance_pocket_clearance_in: float = 0.06
    elevator_fuselage_gap_in: float = 0.0625  # 1/16 to the fuselage side
    elevator_fuselage_round_tube_gap_in: float = (
        0.1  # clearance round the tubes at full travel
    )
    # check bounds from the Owner's Manual, NOT masses of any part
    elevator_weight_ceiling_left_lb: float = 3.9
    elevator_weight_ceiling_right_lb: float = 3.6

    # === CENTRE-SECTION SPAR, FIREWALL, CONTROLS, TRIM (chapters 14-17, M2.5) ===
    # plans-1980 pdf pages p84-p107; Roncz trim values from cobelu ch30. The attach-bolt station is NOT printed
    # (it comes with chapter 19), and spar-cap trough outlines, the firewall outline, console and stick fore-aft
    # positions beyond the two pivot planes, master-cylinder stations and belcrank height live on A-sheets.
    spar_fwd_face_fs: float = 118.5  # book: p88 forward face, BL 0 to 23
    spar_aft_face_fs_centre: float = (
        125.0  # book: p88 centreline aft face = the firewall line
    )
    spar_kink_bl: float = 23.0  # book: p88
    spar_outboard_sweep_deg: float = 8.57  # book: p88
    spar_half_span_bl: float = 56.46  # book: p88
    spar_chord_centreline_in: float = 6.50  # book: p88 fore-aft depth of the spar
    spar_face_length_fwd_outboard_in: float = (
        33.834  # book: p88 forward face outboard of the kink
    )
    spar_face_length_aft_outboard_in: float = (
        32.865  # book: p88 aft face outboard of the kink
    )
    spar_hard_point_spacing_aft_in: float = 28.82  # book: p88 along the aft face
    spar_depth_in: float = 8.50  # book: p88
    spar_top_wl: float = 22.0  # book: p88
    spar_bottom_wl: float = 13.5  # book: p88
    spar_bottom_flat_to_bl: float = 9.0  # book, medium: p88 "about"
    spar_bottom_wl_outboard: float = 15.15  # book: p88 at BL 56.46
    spar_top_flat_to_bl: float = 25.0  # book: p88
    spar_top_wl_outboard: float = 21.7  # book, medium: p88 label at the outboard end
    spar_hp_inboard_bl_in: float = 25.0  # book: p88 one bolt per wing
    spar_hp_inboard_wl_in: float = 20.25  # book: p88
    spar_hp_outboard_bl_in: float = 53.5  # book: p88 two bolts per wing
    spar_hp_outboard_wl_in: Tuple[float, float] = (20.5, 16.3)  # book: p88
    spar_end_bulkhead_width_in: float = 6.30  # book: p90 CS5/CS8
    spar_end_bulkhead_height_in: float = 6.83  # book: p90 CS5/CS8
    spar_foam_height_centre_in: float = 8.41  # book: p90 CS1
    spar_foam_height_kink_in: float = 7.94  # book: p90 CS1 at BL 23
    spar_foam_height_end_in: float = 6.83  # book: p90 CS1 at the ends
    spar_cap_tape_width_in: float = 3.0  # book: p85
    spar_ply_thickness_laid_in: float = 0.0375  # book: p85 text, as laid
    spar_ply_thickness_stock_in: float = 0.035  # book: p85 text, stock tape
    # ply strip lengths, full-span strips first then partials short-to-long order of the book table (p86)
    spar_top_cap_strips_in: Tuple[float, ...] = (
        113,
        113,
        113,
        113,
        100,
        90,
        80,
        70,
        60,
        50,
        40,
        30,
    )
    spar_bottom_cap_strips_in: Tuple[float, ...] = (
        113,
        113,
        113,
        96,
        82,
        68,
        54,
        40,
        26,
    )
    spar_top_cap_partial_end_bl: Tuple[float, ...] = (
        15,
        20,
        25,
        30,
        35,
        40,
        45,
        50,
    )  # p86, strips 30 to 100
    spar_bottom_cap_partial_end_bl: Tuple[float, ...] = (
        13,
        20,
        27,
        34,
        41,
        48,
    )  # p86, strips 26 to 96
    spar_full_ply_end_bl: float = 55.5  # book: p86
    spar_spruce_block_in: Tuple[float, float, float] = (1.0, 1.0, 3.0)  # book: p86
    spar_spruce_block_bl: float = 7.5  # book: p86 at BL +/-7.5, top and bottom
    spar_em12_length_in: float = 8.0  # book: p87 1x1x1/8 angle, four off
    spar_em12_count: int = 4  # book: p87
    # LWA (name, height, thickness, width, quantity), 2024-T3; LWA4/LWA5 heights are the CP43 corrected sizes
    spar_lwa_sizes: Tuple[Tuple[str, float, float, float, int], ...] = (
        ("LWA1", 1.5, 0.125, 2.0, 6),
        ("LWA2", 2.5, 0.125, 2.0, 4),
        ("LWA3", 6.4, 0.125, 2.0, 4),
        ("LWA4", 1.75, 0.25, 2.0, 8),
        ("LWA5", 2.25, 0.25, 2.0, 2),
    )
    spar_lwa1_outboard_setback_in: float = (
        0.75  # cp-corrected: CP25 LPC 28 (p85 printed 1.0)
    )
    spar_baggage_hole_in: Tuple[float, float] = (
        14.0,
        5.0,
    )  # book: p87/p88 forward face, centred
    spar_nut_access_hole_dia_in: float = (
        2.25  # book: p87/p92 at BL 53.5 through the bottom
    )
    ctl_torque_tube_hole_dia_in: float = 1.0  # book: p98/p101 through the firewall
    ctl_torque_tube_hole_bl_in: float = 6.2  # book: p98 text, right of centre
    ctl_torque_tube_hole_wl_in: float = 12.3  # book: p101
    ctl_rudder_conduit_wl_in: float = 8.0  # book: p103
    ctl_rudder_conduit_length_in: float = 82.0  # book: p103
    ctl_stick_pivot_fs_front: float = 45.5  # book, medium: p100 CS108/109 plane
    ctl_stick_pivot_fs_rear: float = 89.7  # book, medium: p100 CS117/118 plane
    ctl_stick_cant_inboard_deg: float = 5.0  # book: p97/p98/p102 at neutral aileron
    ctl_stick_cant_forward_deg: float = 5.0  # book: p97/p98/p102 at neutral elevator
    ctl_roll_travel_deg: float = 20.0  # book: p97/p102 each way from the 5 deg cant
    ctl_cs103_length_in: float = 6.1  # book: p98
    ctl_cs110_length_in: float = 39.2  # book: p99 trim to length
    ctl_cs105_length_in: float = 42.9  # book: p99 trim to fit
    ctl_cs106_length_in: float = 3.8  # book: p99
    ctl_cs115_length_in: float = 4.2  # book: p102
    ctl_cs116_length_in: float = 4.4  # book: p102
    ctl_cs121_length_in: float = 29.5  # book: p102 trim to fit
    ctl_cs119_length_in: float = 4.1  # cp-corrected: CP26 LPC 29 (printed 3.1)
    ctl_elevator_arm_gu_in: float = (
        1.9  # book, medium: GU CS12 only; not the Roncz elevator
    )
    ctl_elevator_arm_fit_in: float = (
        1.9  # fitted: GU arm 1.9 is a size hint only, Roncz arm not printed
    )
    ctl_stick_lever_fit_in: float = (
        5.0  # fitted: stick rod-end lever, representational, not printed
    )
    trim_panel_face_fs_in: float = (
        40.0  # book: p106 (fs_panel carries 39.75, unchanged)
    )
    trim_pth_dim_from_panel_in: float = 9.5  # book: p106 leftmost end of the PTH
    trim_pth_leftmost_fs_label: float = (
        49.8  # conflict: p106 label, against the 49.5 derived property
    )
    trim_handle_pivot_wl_in: float = 8.6  # book: p106
    trim_friction_bolt_wl_in: float = 7.1  # book: p106 lower friction bolt
    trim_swage_from_sleeve_in: Tuple[float, float] = (5.6, 6.2)  # book: p106
    trim_sleeve_bl_in: float = 9.5  # cp-corrected: CP25 addendum
    trim_sleeve_wl_in: Tuple[float, float] = (9.6, 8.3)  # cp-corrected: CP25 addendum
    trim_spring_pts_in: Tuple[float, float] = (6.0, 9.0)  # book: p105 free, installed
    trim_spring_rts_in: Tuple[float, float] = (2.0, 3.0)  # book: p105 free, installed
    trim_spring_cs_in: Tuple[float, float] = (0.5, 0.25)  # book: p105 as listed
    trim_nc5a_belcrank_bl_left_in: float = (
        9.2  # positioned-from-text: cobelu fig C-1, inboard end of the left tube
    )
    trim_cs202_extra_spacer_in: float = (
        0.4  # book, medium: Roncz spacer at the elevator-end rod end
    )

    # === CANOPY (chapter 18, M2.6) ===
    # plans-1980 pdf pages p108-p117. The bubble contour is a vendor part with no printed section, so the loft is
    # representational (core.canopy_book); only the stations below are printed.
    canopy_plexi_length_in: float = 68.0  # book: p108 trimmed plexiglass length
    canopy_rear_cut_fs: float = (
        117.0  # book: p111 rear cut at the longeron (CP27 LPC 43)
    )
    canopy_pad_length_in: float = 2.5  # book: p112 each of the eight pads
    canopy_pad_aft_edge_left_in: Tuple[float, float, float, float] = (
        11.0,
        41.0,
        59.0,
        71.0,
    )  # book: p112 forward of the rear cut; 59 is the safety-catch pad
    canopy_pad_aft_edge_right_in: Tuple[float, float, float, float] = (
        20.0,
        25.5,
        48.0,
        53.5,
    )  # book: p112 hinge pads
    canopy_safety_catch_fs: float = 56.75  # book: p116 SC-1 bolt station
    canopy_door_size_in: Tuple[float, float] = (
        4.3,
        3.7,
    )  # book: p116 left door, long by high
    canopy_check_a_min_in: float = (
        13.5  # book: p109 canopy top above the longerons, at least
    )
    canopy_check_b_in: float = 12.3  # book: p109 at 15 in forward of the firewall
    canopy_check_datum_wl: float = 23.0  # book: p109 top of the longerons, as WL
    canopy_front_cut_fs: float = (
        41.65  # conflict: p111 14.0 aft of an unnamed vertical; F28 reading carried
    )
    canopy_latch_labels_fs: Tuple[float, float, float] = (
        104.0,
        74.0,
        44.0,
    )  # conflict: p117 printed labels, against the derived centres
    canopy_open_past_vertical_deg: float = 15.0  # book: p115 text

    # === WING BOOK (chapter 19, M2.7) ===
    # plans-1980 pdf pages p118 to p134; the plan view is p126 (scale 1/10, right wing, the left is the mirror). The analysis planform
    # (wing_span, wing_root_bl, wing_washout, wing_root_chord) is NOT moved here: see the notes in GEOMETRY_PROVENANCE.
    # Rib stations: BL 23 is the root rib (inboard core FC1 starts there), 55.5 the foam joint, 106.25 the second joint, 157 the tip rib.
    wing_book_rib_bl: Tuple[float, float, float, float] = (
        23.0,
        55.5,
        106.25,
        157.0,
    )  # book: p126 and p127
    wing_book_le_fs_bl_55_5: float = 112.9  # book: p126 LE label at the BL 55.5 joint
    wing_book_le_fs_tip: float = 156.0  # book: p126 and p171 tip LE
    wing_book_le_fs_bl_106_25_printed: float = (
        134.95  # conflict: p126 LE label; the chord and the line give 134.45
    )
    wing_book_te_fs: Tuple[float, float, float] = (
        155.6,
        165.8,
        176.0,
    )  # book: p126 TE at BL 55.5, 106.25, 157
    wing_book_te_fs_bl_23: float = 148.4  # book: p126 inboard TE at the root rib
    wing_book_chord: Tuple[float, float, float] = (
        42.7,
        31.35,
        20.0,
    )  # book: p126 chords at BL 55.5, 106.25, 157
    wing_book_thickness_pct: Tuple[float, float, float] = (
        16.2,
        15.7,
        15.0,
    )  # book: p126 thickness at BL 55.5, 106.25, 157 (16.2 medium)
    wing_book_washout_deg: Tuple[float, float, float] = (
        -0.6,
        0.96,
        2.7,
    )  # book: p126 twist at BL 55.5, 106.25, 157; positive washout (LE down going outboard), -0.6 is the printed washin
    wing_book_te_sweep_deg: float = 11.36  # book: p126 outer TE sweep
    wing_book_te_sweep_inboard_deg: float = 12.49  # book: p126 TE kink BL 23 to 55.5
    wing_book_chord_line_wl: float = (
        17.4  # book: p126 and p128 all chord lines at WL 17.4 (LE flat), model z 0
    )
    wing_book_te_wl: Tuple[float, float] = (
        16.95,
        18.35,
    )  # book: p126 TE height at BL 55.5 and BL 157 (the section's thickness and twist)
    wing_book_shear_web_fwd_fs: Tuple[float, float, float, float] = (
        125.6,
        130.5,
        147.35,
        164.2,
    )  # book: p126 shear web forward face (foam edge) at BL 23, 55.5, 106.25, 157
    wing_book_shear_web_sweep_deg: float = 18.42  # book: p126
    wing_book_spar_cap_width_in: float = 3.0  # book: p126 and p122 (3 in UND tape)
    wing_book_foam_blocks: Tuple[int, int] = (
        5,
        2,
    )  # book: p118 five 7x14x64 and two 7x14x41 blocks per wing
    wing_book_core_angle_deg: Tuple[float, float] = (
        78.64,
        77.51,
    )  # book: p118 and p127 centre/outboard and inboard core cut angles
    wing_book_fc1_le_length_in: float = 32.87  # book: p118 and p127 FC1 LE length
    wing_shear_web_zones: Tuple[
        Tuple[float, float, int], Tuple[float, float, int], Tuple[float, float, int]
    ] = (
        (23.0, 70.0, 6),
        (70.0, 120.0, 4),
        (120.0, 157.0, 2),
    )  # cp-corrected: p121 plies by BL zone; the outboard zone prints 3, CP26 LPC 31 makes it 2
    wing_shear_web_outboard_plies_printed: int = (
        3  # book as printed, superseded by the cp-corrected zone above
    )
    wing_cap_bottom_plies_in: Tuple[float, float, float, float, float] = (
        142.0,
        135.0,
        84.0,
        52.0,
        19.5,
    )  # book: p122 bottom cap ply lengths, 3 in UND tape, base schedule (the fifth digit medium)
    wing_cap_bottom_offsets_in: Tuple[float, float, float, float] = (
        5.0,
        12.0,
        19.0,
        26.0,
    )  # book: p122 inboard offsets of plies 2 to 5 from the root end
    wing_cap_top_plies_in: Tuple[float, float, float, float, float, float, float] = (
        142.0,
        142.0,
        119.0,
        90.0,
        61.0,
        39.0,
        20.0,
    )  # book: p123 top cap ply lengths, seven plies
    wing_cap_top_offsets_in: Tuple[float, float, float, float] = (
        6.0,
        12.0,
        18.0,
        24.0,
    )  # book: p123 inboard offsets (plies 3 to 6; the model continues the same step for ply 7)
    wing_skin_plies: Tuple[int, int] = (
        2,
        3,
    )  # book: p122 and p123 bottom 2 UND, top 2 UND plus a third UND forward of the hinge line (p128 prints 3 top)
    wing_skin_le_lap_in: float = 2.0  # book: p122 LE lap onto the bottom skin
    wing_skin_te_lap_min_in: float = (
        0.5  # cp-corrected: CP32 TE lap minimum (0.6 printed)
    )
    wing_aileron_outboard_bl: float = 118.1  # book: p126, p119 and p171 agree
    wing_aileron_inboard_bl: float = (
        55.5  # conflict: p124 cuts at the BL 55.5 foam joint
    )
    wing_aileron_inboard_bl_p171: float = 54.3  # conflict: p171 prints BL 54.3
    wing_aileron_skin_cut_top_in: Tuple[float, float] = (
        5.9,
        4.35,
    )  # book: p124 and p130 hinge-line cut forward of the TE at BL 55.5 and 106.25 (4.35 digit medium)
    wing_aileron_skin_cut_bottom_in: Tuple[float, float] = (
        7.6,
        5.65,
    )  # book: p124 and p130 bottom skin cut at BL 55.5 and 106.25
    wing_aileron_rod_length_in: float = 65.0  # book: p133 A13 3/8 steel rod
    wing_aileron_torque_tube_length_in: float = 9.0  # book: p133 A10 3/4 x .058 tube
    wing_aileron_hinge_lengths_in: Tuple[float, float, float] = (
        8.0,
        6.0,
        6.0,
    )  # book: p133 A3 inboard, A4 mid and outboard
    wing_aileron_max_up_deg: float = (
        20.0  # book: p125 and p131 stop bolt for 20 deg up aileron
    )
    wing_spar_join_bolt_spacing_in: float = (
        28.85  # conflict: p134 drawing; the text note prints 28.83
    )
    wing_spar_join_bolt_spacing_text_in: float = 28.83  # conflict: p134 text note
    wing_spar_join_bolts: Tuple[int, int] = (
        2,
        1,
    )  # book: p134 2 x AN8-21A and 1 x AN8-23A per wing
    wing_spar_join_bushings_per_wing: int = 6  # book: p134 LWA9, 12 in all

    # === WINGLET BOOK (chapter 20, M2.7) ===
    # plans-1980 pdf pages p135 to p140. The fin airfoils, the lower fin outline, block A and the tip cap are on A-sheets the owner does
    # not hold: the build model draws them as fitted shapes (core.winglet_book). Cant and toe are not printed.
    winglet_book_root_wl: float = (
        18.4  # book: p135 root level line (rudder, root template, lower fin joint)
    )
    winglet_book_top_wl: float = 65.4  # book: p135 top of the skin
    winglet_book_cap_in: float = (
        1.0  # book: p135 and p136 urethane cap, WL 66.4 with it
    )
    winglet_book_bottom_wl: float = 9.8  # book: p135 and p171 lower fin bottom
    winglet_book_root_le_fs: float = (
        159.7  # book: p135 the straight LE line meets WL 18.4
    )
    winglet_book_root_le_fs_wing_top: float = (
        160.5  # book: p135 and p136 LE at the wing top surface
    )
    winglet_book_root_te_fs: float = 186.8  # book: p135 root TE at WL 18.4
    winglet_book_top_te_fs: float = 196.6  # book: p135 and p171 top TE corner
    winglet_book_tip_chord_in: float = 11.4  # derived-medium: captain pixel read scaled by the printed rudder widths; not crew C's 28.9
    winglet_book_rudder_hinge_fs: float = 176.8  # book: p135
    winglet_book_rudder_widths_in: Tuple[float, float, float] = (
        10.0,
        12.14,
        11.5,
    )  # book: p135 and p138 hinge to TE at WL 18.4, at the top, at the bottom
    winglet_book_rudder_height_in: Tuple[float, float] = (
        10.5,
        4.0,
    )  # book: p135 rudder 10.5 above WL 18.4 and 4 below (14.5 in all)
    winglet_book_rudder_max_deg: float = 30.0  # book: p139 maximum travel
    winglet_book_hinge_length_in: float = 7.5  # book: p138 piano hinge from WL 18.4 up
    winglet_book_core_angle_deg: Tuple[float, float] = (
        78.64,
        101.36,
    )  # book: p135 upper fin core end angles
    winglet_book_core_length_in: float = 48.0  # book: p135 upper fin core block length
    winglet_book_jig_wprp: Tuple[float, float] = (
        149.6,
        55.5,
    )  # book: p136 WPRP (FS, BL), inboard front corner of the aileron cut-out
    winglet_book_jig_abc_in: Tuple[float, float, float] = (
        102.15,
        108.35,
        118.35,
    )  # book: p136 CP25 LPC 6, A to the LE mark, B to the root TE, C to the tip TE
    winglet_book_jig_tol_in: Tuple[float, float, float] = (
        0.05,
        0.05,
        1.0,
    )  # book: p136 tolerance on A, B and C
    winglet_book_bid_patch_in: Tuple[float, float] = (
        18.0,
        14.0,
    )  # cp-corrected: p136 third BID ply on the upper winglet root, 18 up by 14 wide (CP34 LPC 104; the 14 is medium)
    winglet_book_und_table_in: Tuple[
        Tuple[float, float],
        Tuple[float, float],
        Tuple[float, float],
        Tuple[float, float],
        Tuple[float, float],
        Tuple[float, float],
        Tuple[float, float],
    ] = (
        (24.0, 12.0),
        (22.0, 11.0),
        (20.0, 10.0),
        (18.0, 9.0),
        (16.0, 8.0),
        (14.0, 7.0),
        (12.0, 6.0),
    )  # book: p138 corner layups 3 and 4 UND plies, A in and B in
    winglet_book_conduit_from_te_in: float = (
        13.2  # book: p137 rudder conduit from the winglet TE
    )

    # === STRAKE AND FUEL BOOK (chapter 21, M2.8) ===
    # plans-1980 pdf pages p141 to p148 (printed 21-1 to 21-8). The R23 and R45 rib outlines (A14), the OD outline and the jig board use are on
    # sheets the owner does not hold: the build model draws them as fitted shapes (core.strake_book).
    # The prefix is stk_ because tests/test_nose_elevator_stations.py bans any field name containing 'rake' (gear rake) and 'strake' does.
    stk_book_le_fs_fuselage: float = 50.0  # book: plans-1980:p147: strake LE at the fuselage side, F.S. 50 (p171 agrees)
    stk_book_le_fs_bl_23: float = 73.3  # book: plans-1980:p147: TLE and BLE kink at BL 23, F.S. 73.3 (p171 agrees)
    stk_book_le_fs_bl_45: float = (
        99.5  # book: plans-1980:p147: LE at BL 45 where R45 meets the TLE, F.S. 99.5
    )
    stk_book_spar_fwd_fs_bl_23: float = (
        118.5  # book: plans-1980:p147: spar forward face at BL 23, F.S. 118.5
    )
    stk_book_spar_slope_deg: float = 8.57  # derived: plans-1980:p118: spar face sweeps aft 8.57 deg per BL out (4.9 over 32.5 on p118)
    stk_book_bab_fuselage_fs: float = 103.5  # book: plans-1980:p147: BAB meets the fuselage side at F.S. 103.5 (the aft edge of the baggage cutout)
    stk_book_sump_fs: Tuple[float, float] = (
        103.5,
        125.0,
    )  # derived: plans-1980:p144: sump blister runs F.S. 103.5 to 125, flush with the firewall (p144 note, p171 FS 125)
    stk_book_fuselage_side_bl: Tuple[float, float] = (
        12.1,
        11.3,
    )  # derived-unsourced: plans-1980:p147: fuselage side BL at F.S. 50 and at F.S. 103.5, scaled off the p147 image (plus or minus 0.
    stk_book_foam_thickness_in: float = 0.35  # book: plans-1980:p141: type 45 PV core, 0.35 in thick, for every strake part and skin
    stk_book_tle_in: Tuple[float, float] = (
        33.5,
        2.55,
    )  # book: plans-1980:p141: TLE fuel tank leading edge, 33.5 long by 2.55 wide, 90 deg corners
    stk_book_ble_in: Tuple[float, float] = (
        25.5,
        2.55,
    )  # book: plans-1980:p141: BLE baggage leading edge, 25.5 long by 2.55 wide
    stk_book_b23_in: Tuple[float, float] = (
        21.3,
        7.3,
    )  # book: plans-1980:p141: B23 baffle, 21.3 long by 7.3 high
    stk_book_bab_in: Tuple[float, float, float] = (
        13.4,
        7.3,
        7.75,
    )  # book: plans-1980:p141: BAB baffle, 13.4 long, 7.3 high outboard and 7.75 high inboard (the 7.75 is medium)
    stk_book_db_in: Tuple[float, float, float] = (
        28.5,
        7.3,
        6.5,
    )  # book: plans-1980:p141: DB diagonal baffle, 28.5 long, 7.3 high at the fore end and 6.5 at the aft end (the 6.5 is
    stk_book_b23_hole_in: Tuple[float, float] = (
        5.0,
        3.0,
    )  # book: plans-1980:p141: B23 oval hole 5 long by 3 high, 3 in from the right end and 3 in clear of the bottom edge
    stk_book_notch_radius_in: Tuple[float, float] = (
        0.8,
        1.3,
    )  # book: plans-1980:p141: B23 and DB corner notch radii, 0.8 on top and 1.3 on the bottom, centres 2 in from each en
    stk_book_skin_top_in: Tuple[float, float, float, float] = (
        23.9,
        44.3,
        44.3,
        67.2,
    )  # book: plans-1980:p142: top skin foam edges A, B, C and D (outboard skin A, B and C
    stk_book_skin_bottom_in: Tuple[float, float, float, float] = (
        23.7,
        44.1,
        44.1,
        67.0,
    )  # book: plans-1980:p142: bottom skin foam edges A, B, C and D
    stk_book_skin_spar_edge_in: Tuple[float, float] = (
        32.0,
        4.9,
    )  # book: plans-1980:p142: outboard skin spar edge 32.0 long along the bevel, offset aft 4.9, square at the aft corne
    stk_book_cutout_fwd_in: Tuple[Tuple[float, float, float], ...] = (
        (65.8, 4.0, 6.55),
        (63.0, 2.9, 7.35),
        (60.0, 2.15, 7.9),
        (56.0, 1.7, 8.45),
        (52.0, 1.55, 8.8),
        (47.0, 1.45, 9.05),
        (42.0, 1.40, 9.1),
    )  # book: plans-1980:p142: baggage cutout in the fuselage side: station forward of the spar face, top-edge depth and
    stk_book_cutout_aft_in: Tuple[float, float, float, float] = (
        30.0,
        15.0,
        1.40,
        9.15,
    )  # book: plans-1980:p142: tank cutout in the fuselage side: round forward end begins 30.0 forward of the spar face,
    stk_book_cutout_aft_top_alt_in: float = 1.90  # conflict: plans-1980:p142: the tank cutout top depth reads 1.90 near the aft end and 1.40 at mid length in the same d
    stk_book_jig_rib_height_in: Tuple[float, float] = (
        2.65,
        3.45,
    )  # book: plans-1980:p143: the WL 17.4 mark on R45 is 2.65 above the jig table and on R23 3.45 above (the strake bott
    stk_book_sump_blister_in: Tuple[float, float, float] = (
        21.0,
        2.75,
        0.5,
    )  # book: plans-1980:p144: sump blister 21 long, 2.75 deep, 0.5 flange all round
    stk_book_baggage_limit_lb: float = 100.0  # book: om-1980:p4: each strake baggage floor is structurally good for 100 lb (OM weights page)
    fuel_book_lb_per_gal: float = (
        6.0  # book: om-1980:p25: 6.0 lb per gal (40 gal = 240 lb, om-1980:p26)
    )
    fuel_book_arm_fs: float = 104.5  # book: om-1980:p26: fuel arm F.S. 104.5 (rows 240 lb moment 25080 and 150 lb moment 15675 both close)
    fuel_book_capacity_plans_gal: float = (
        25.5  # conflict: plans-1980:p141: plans: two tanks of 25.5 gal each (51 total)
    )
    fuel_book_capacity_om_gal: float = 28.0  # conflict: om-1980:p8: OM: two 28 gal tanks (56) but also a 52 gal total (also cp-text CP24 p13)
    fuel_book_capacity_om_total_gal: float = 52.0  # book: om-1980:p8: OM: 52 gal total capacity (cp-text CP24 p13 spec table agrees)

    # === ELECTRICAL BOOK (chapter 22, M2.8) ===
    # plans-1980 pdf pages p149 to p155. No fuselage station or weight is printed in the chapter; the battery station is on A6 (not held).
    elec_book_battery_v: float = 12.0  # book: plans-1980:p150: 12 V system
    elec_book_battery_ah: float = 25.0  # book: plans-1980:p150: 25 Ah in the nose in both systems 'to provide the correct CG' (p149)
    elec_book_battery_fs_range: Tuple[float, float] = (
        0.0,
        22.0,
    )  # positioned-from-text: plans-1980:p155: the battery sits on a nose shelf bonded to NG30 and F6 (p155)
    elec_book_battery_model_fs: float = 11.0  # unsourced: no page: the model draws the battery at the middle of the F.S. 0 to 22 range for illustration only
    elec_book_battery_added_lb: float = 19.0  # derived: cp-text:p27: the 25 Ah nose battery 'accepts a 19 lb increase' over the small battery (CP27 p4): a prin
    elec_book_shelf_in: Tuple[float, float] = (
        0.6,
        0.4,
    )  # book: plans-1980:p155: battery shelf 0.6 above the floor mark and cover wrap gap 0.4 (small hand digits)
    elec_book_starter_fs_min: float = 150.0  # positioned-from-text: cp-text:p27: starter, ring gear and alternator 'way back at station 150+' (CP27 p4): a lower bound, not
    elec_book_relay_fs: float = 22.0  # positioned-from-text: plans-1980:p149: mount the start relay and over-voltage unit on the front of F22 (p149)
    elec_book_nav_strip_in: float = 22.8  # cp-corrected: cp-text:p30: nav antenna copper strips are 22.8 in, not 24 (CP30 LPC 78)
    elec_book_comm_strip_in: float = 20.3  # cp-corrected: cp-text:p26: comm antenna in the winglet: two foil strips 20.3 in, three balums (CP26 p8)

    # === ENGINE BOOK (chapter 23, M2.8) ===
    # plans-1980 pdf pages p156 to p158: a three-page delta; the installation lives in Sections IIA, IIC and IIL (not held).
    eng_book_engine_max_lb: float = 246.0  # book: plans-1980:p156: engine with accessories at most 246 lb (a limit, not a weight)
    eng_book_vibrating_max_lb: float = 286.0  # book: plans-1980:p156: vibrating mass (engine, accessories, exhaust, prop, extensions, oil) at most 286 lb
    eng_book_oil_lb: float = 8.0  # book: om-1980:p25: oil 8 lb
    eng_book_oil_fs: float = (
        140.0  # book: om-1980:p25: oil station F.S. 140.0 (moment 1120)
    )
    eng_book_down_thrust_deg: float = 2.0  # cp-corrected: cp-text:p32: 2 deg down thrust, plus or minus 1, prop flange higher than the magneto end
    eng_book_crank_bl: float = (
        0.0  # cp-corrected: cp-text:p32: crankshaft on BL 0 in plan (CP32 p5)
    )
    eng_book_block_in: Tuple[float, float, float] = (
        30.0,
        32.0,
        20.0,
    )  # unsourced: no page: O-235-sized block, length (along the crank), width and height
    eng_book_block_fwd_fs: float = 127.0  # unsourced: no page: front of the engine block, aft of the firewall (F.S. 125) and the mount
    eng_book_block_wl: float = 23.0  # unsourced: no page: WL of the block centre
    eng_book_prop_dia_in: float = 60.0  # conflict: plans-1980:p171: back cover 'max dia 60' (the inch mark is smudged)
    eng_book_cowl_trim_in: float = 9.0  # book: plans-1980:p157: trim about 9 in off each outboard end of the VariEze cowl
    eng_book_cowl_reinf_in: Tuple[int, float] = (
        4,
        2.0,
    )  # book: plans-1980:p157: 4 plies BID at 45 deg, 2 in wide, in 4 places just inboard of the 9 in trim line (the band
    eng_book_cowl_aft_shift_in: float = 0.7  # cp-corrected: cp-text:p27: the Lycoming cowl moves aft 0.7 in against the VariEze and the engine moves aft with the d
    eng_book_rib_in: Tuple[float, float, float, float, float] = (
        0.020,
        20.0,
        24.0,
        1.2,
        0.5,
    )  # book: plans-1980:p158: wing-root metal rib: 6061-0 sheet 0.020 thick (p157 text prints 0.20, a typo), 20 by 24 sh
    eng_book_bracket_plate_in: Tuple[float, float, float] = (
        6.5,
        2.5,
        0.063,
    )  # book: plans-1980:p156: throttle and mixture bracket plate seen from below, 6.5 long by 2.5 wide, 0.063 2024-T3 (f
    eng_book_bracket_holes_in: Tuple[float, float, float, float] = (
        2.0,
        3.6,
        1.8,
        1.25,
    )  # book: plans-1980:p156: oil-drain hole dia 2.0 centred 3.6 from the carb hole centre, carb hole dia 1.8 (hand '1-8
    eng_book_bracket_angle_in: Tuple[float, float, float] = (
        2.0,
        2.0,
        0.063,
    )  # book: plans-1980:p156: upright 2 by 2 formed angle, 0.063, eight rivets (the rivet prefix is smudged)

    # === DATUM OFFSET (internal -> published coordinate translation) ===
    datum_offset_in: float = 0.0  # stations are in the published frame
    # Was 45.5, fitted so the computed NP matched published FS 108 (retired 2026-09-29).
    # internal_fs - datum_offset_in = published_fs

    # === OPENVSP GEOMETRY (positions for 3D model) ===
    wing_le_wl: float = (
        0.0  # model zero = book W.L. 17.4, the wing plane (plans-1980:p134)
    )
    canard_le_wl: float = (
        1.5  # above the wing plane: p171 W.L. 18.9 - 17.4; see GEOMETRY_PROVENANCE
    )
    winglet_height: float = (
        47.0  # Winglet vertical span, WL 18.4 to 65.4 (plans-1980:p135)
    )
    winglet_root_chord: float = (
        27.1  # Winglet root chord, derived from p135 FS 159.7 and 186.8
    )
    winglet_tip_chord: float = (
        11.4  # Winglet tip chord, derived-unsourced (scaled off the 1/5 drawing)
    )

    # === CANARD DOWNWASH ===
    canard_vertical_offset_in: float = (
        1.5  # Vertical separation canard AC to wing plane (see GEOMETRY_PROVENANCE)
    )

    # === ERGONOMICS ===
    cockpit_width: float = 23.0  # F-22 interior width
    pilot_height_max: float = 77.0  # Max pilot height (inches)

    @property
    def fs_main_axle(self) -> float:
        """Derived: spar aft face minus 15 in (p50). A property so it cannot drift."""
        return self.fs_spar_aft_face - self.main_axle_fwd_of_spar

    @property
    def fs_static_port(self) -> float:
        """Derived: instrument panel station minus 8 in (p82)."""
        return self.fs_panel - self.static_port_fwd_of_panel_in

    @property
    def elevator_inboard_bl_right_in(self) -> float:
        """Derived: right elevator FOAM inboard end (drawn stock end), B.L. +(65.0 - 55.7) = +9.3 (C-1 labels 9.3)."""
        return self.elevator_outboard_end_bl_in - self.elevator_length_right_in

    @property
    def elevator_inboard_bl_left_in(self) -> float:
        """Derived: left elevator FOAM inboard end, the mirror of the right, B.L. -(65.0 - 55.7) = -9.3 (C-1 labels 9.2 (left); 0.1 in apart)."""
        return -(self.elevator_outboard_end_bl_in - self.elevator_length_right_in)

    @property
    def elevator_tube_end_bl_left_in(self) -> float:
        """Derived: left elevator TUBE end, B.L. +(72.7 - 65.0) = +7.7 (C-1): the bare 1 in tube crosses the fuselage and the centreline."""
        return self.elevator_length_left_in - self.elevator_outboard_end_bl_in

    @property
    def fs_ng31_min(self) -> float:
        """Derived: F22 minus the side block length (p79); with fs_ng31_max a range, not a point."""
        return self.fs_f22 - self.side_block_length_in

    @property
    def fs_ng31_max(self) -> float:
        """Derived: F22 minus the floor block length (p79)."""
        return self.fs_f22 - self.floor_block_length_in

    @property
    def spar_chord_square_outboard_in(self) -> float:
        """Derived: centreline chord times cos(outboard sweep), square to the outboard face (p88)."""
        return self.spar_chord_centreline_in * math.cos(
            math.radians(self.spar_outboard_sweep_deg)
        )

    @property
    def spar_fwd_face_fs_tip(self) -> float:
        """Derived: forward face station at the half span from the kink and the sweep (p88)."""
        return self.spar_fwd_face_fs + (
            self.spar_half_span_bl - self.spar_kink_bl
        ) * math.tan(math.radians(self.spar_outboard_sweep_deg))

    @property
    def spar_aft_face_fs_bl_55_5(self) -> float:
        """Derived: aft face station at BL 55.5 from the kink and the sweep (p88 prints 129.9)."""
        return self.spar_aft_face_fs_centre + (55.5 - self.spar_kink_bl) * math.tan(
            math.radians(self.spar_outboard_sweep_deg)
        )

    @property
    def trim_pth_leftmost_fs(self) -> float:
        """Derived: panel face FS 40 plus the 9.5 dimension (p106); the p106 label reads 49.8."""
        return self.trim_panel_face_fs_in + self.trim_pth_dim_from_panel_in

    @property
    def canopy_latch_pad_centres_fs(self) -> Tuple[float, float, float]:
        """Derived: rear cut less the left pad aft edge (11, 41, 71) less half the 2.5 pad (p112); the p117 labels read 104, 74, 44."""
        a = self.canopy_pad_aft_edge_left_in
        half = self.canopy_pad_length_in / 2
        c = self.canopy_rear_cut_fs
        return (c - a[0] - half, c - a[1] - half, c - a[3] - half)

    @property
    def canopy_hinge_spans_fs(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Derived: aft and forward hinge, each the span of its two right pads (p112, p114): FS 89 to 97 and 61 to 69."""
        r, ln = self.canopy_pad_aft_edge_right_in, self.canopy_pad_length_in
        c = self.canopy_rear_cut_fs
        return ((c - r[1] - ln, c - r[0]), (c - r[3] - ln, c - r[2]))

    @property
    def canopy_check_a_wl(self) -> float:
        """Derived: top of the longerons (WL 23) plus 13.5 (p109), at least; measured 6 in forward of the headrest."""
        return self.canopy_check_datum_wl + self.canopy_check_a_min_in

    @property
    def canopy_check_b_wl(self) -> float:
        """Derived: WL 23 plus 12.3 (p109)."""
        return self.canopy_check_datum_wl + self.canopy_check_b_in

    @property
    def canopy_check_b_fs(self) -> float:
        """Derived: 15 in forward of the firewall line (p109)."""
        return self.fs_firewall - 15.0

    # --- chapter 19 and 20 derived values (M2.7) ---
    @property
    def wing_le_fs_bl_58(self) -> float:
        """Derived: LE at BL 58 from the p126 LE at BL 55.5 and the 22.98 deg line (113.96); CP25 LPC 7 prints 113.9."""
        return self.wing_book_le_fs_bl_55_5 + (
            58.0 - self.wing_book_rib_bl[1]
        ) * math.tan(math.radians(self.wing_sweep_le))

    @property
    def wing_le_fs_bl_106_25_derived(self) -> float:
        """Derived: p126 TE 165.8 less the printed chord 31.35 (134.45); the p126 LE label prints 134.95 and the 22.98 deg line gives 134.42."""
        return self.wing_book_te_fs[1] - self.wing_book_chord[1]

    @property
    def wing_le_fs_bl_106_25_line(self) -> float:
        """Derived: the straight 22.98 deg LE line from FS 112.9 at BL 55.5 to BL 106.25 (134.42)."""
        return self.wing_book_le_fs_bl_55_5 + (
            self.wing_book_rib_bl[2] - self.wing_book_rib_bl[1]
        ) * math.tan(math.radians(self.wing_sweep_le))

    @property
    def wing_aileron_hinge_fs(self) -> Tuple[float, float]:
        """Derived: top-skin hinge line FS at BL 55.5 and 106.25, the p126 TE less the p124 top cut (149.7, 161.45)."""
        te = self.wing_book_te_fs
        cut = self.wing_aileron_skin_cut_top_in
        return (te[0] - cut[0], te[1] - cut[1])

    @property
    def winglet_height_book_in(self) -> float:
        """Derived: WL 65.4 less WL 18.4 (p135), the upper fin without its cap."""
        return self.winglet_book_top_wl - self.winglet_book_root_wl

    @property
    def winglet_lower_height_book_in(self) -> float:
        """Derived: WL 18.4 less WL 9.8 (p135)."""
        return self.winglet_book_root_wl - self.winglet_book_bottom_wl

    @property
    def winglet_root_chord_book_in(self) -> float:
        """Derived: root TE FS 186.8 less the straight LE line at WL 18.4, FS 159.7 (p135): 27.1."""
        return self.winglet_book_root_te_fs - self.winglet_book_root_le_fs

    @property
    def winglet_top_le_fs(self) -> float:
        """Derived-medium: top TE FS 196.6 less the 11.4 tip chord (185.2)."""
        return self.winglet_book_top_te_fs - self.winglet_book_tip_chord_in

    @property
    def winglet_cant_in(self) -> float:
        """Derived-low: inward lean of the tip over the fin height that closes the p136 C dimension (about 3.6)."""
        wprp_fs, wprp_bl = self.winglet_book_jig_wprp
        lateral = self.wing_book_rib_bl[3] - wprp_bl
        dx = self.winglet_book_top_te_fs - wprp_fs
        dz = self.winglet_height_book_in
        c = self.winglet_book_jig_abc_in[2]
        return lateral - math.sqrt(c * c - dx * dx - dz * dz)

    @property
    def stk_book_spar_fwd_fs_bl_45(self) -> float:
        """Derived: spar forward face at BL 45, 118.5 + (45 - 23) tan 8.57 deg (121.8)."""
        return self.stk_book_spar_fwd_fs_bl_23 + (45.0 - 23.0) * math.tan(
            math.radians(self.stk_book_spar_slope_deg)
        )

    @property
    def stk_book_junction_fs(self) -> float:
        """Derived: where R23, B23, BAB and DB meet on BL 23, the spar face less the printed B23 length (97.2; p147 derives 97.3)."""
        return self.stk_book_spar_fwd_fs_bl_23 - self.stk_book_b23_in[0]

    @property
    def stk_book_db_far_fs(self) -> float:
        """Derived: where DB meets R45, the junction plus the DB run along FS that closes its printed length over 22 in of BL (115.3)."""
        return self.stk_book_junction_fs + math.sqrt(
            self.stk_book_db_in[0] ** 2 - (45.0 - 23.0) ** 2
        )

    @property
    def eng_book_vibrating_allowance_lb(self) -> float:
        """Derived: 286 lb vibrating mass less the 246 lb engine, the 40 lb left for prop, exhaust, extensions and oil."""
        return self.eng_book_vibrating_max_lb - self.eng_book_engine_max_lb

    # === DERIVED DIMENSIONS (computed at runtime) ===
    @property
    def canard_root_chord(self) -> float:
        return self.canard_chord

    @property
    def canard_tip_chord(self) -> float:
        return self.canard_chord

    @property
    def fs_wing_le(self) -> float:
        """Wing root LE station, derived from the book anchor via the (unverified) wing sweep."""
        fs, bl = self.wing_le_anchor
        return fs - (bl - self.wing_root_bl) * math.tan(
            math.radians(self.wing_sweep_le)
        )

    @property
    def canard_arm(self) -> float:
        """Distance from wing AC to canard AC (critical for stability).

        Uses MAC-based quarter chord with sweep offset for both surfaces. The wing is the
        gross reference trapezoid (centreline chord to tip), the planform of wing_area_sqft
        and of PhysicsEngine.calculate_mac (ledger C2).
        """

        # Wing AC: MAC quarter-chord of the reference trapezoid, with sweep offset
        tan_le = math.tan(math.radians(self.wing_sweep_le))
        c0 = self.wing_centerline_chord
        taper_w = self.wing_tip_chord / c0
        mac_w = (2 / 3) * c0 * (1 + taper_w + taper_w**2) / (1 + taper_w)
        y_mac_w = (self.wing_span / 6) * (1 + 2 * taper_w) / (1 + taper_w)
        wing_ac = (
            self.fs_wing_le
            - self.wing_root_bl * tan_le
            + y_mac_w * tan_le
            + 0.25 * mac_w
        )

        # Canard AC: MAC quarter-chord with sweep offset
        taper_c = self.canard_tip_chord / self.canard_root_chord
        mac_c = (
            (2 / 3)
            * self.canard_root_chord
            * (1 + taper_c + taper_c**2)
            / (1 + taper_c)
        )
        y_mac_c = (self.canard_span / 2 / 3) * (1 + 2 * taper_c) / (1 + taper_c)
        canard_ac = (
            self.fs_canard_le
            + y_mac_c * math.tan(math.radians(self.canard_sweep_le))
            + 0.25 * mac_c
        )

        return wing_ac - canard_ac

    @property
    def wing_tip_bl(self) -> float:
        """Butt line of the wing tip (wing_span / 2); the tip chord is specified here."""
        return self.wing_span / 2

    @property
    def wing_panel_span(self) -> float:
        """Length of one wing panel, root BL (wing_root_bl) to tip BL (wing_span / 2)."""
        return self.wing_span / 2 - self.wing_root_bl

    @property
    def fuselage_length(self) -> float:
        """Fuselage length, fs_tail - fs_nose (single basis; provenance status is conflict)."""
        return self.fs_tail - self.fs_nose

    @property
    def wing_centerline_chord(self) -> float:
        """Wing chord at BL 0: the straight root-to-tip taper extended to the centreline."""
        slope = (self.wing_root_chord - self.wing_tip_chord) / self.wing_panel_span
        return self.wing_root_chord + self.wing_root_bl * slope

    @property
    def wing_exposed_area_sqft(self) -> float:
        """Exposed wing panel area in sq ft: both panels, trapezoid from root BL to tip BL.

        Excludes the centre section between the two root BLs (strakes/fuselage).
        """
        avg_chord = (self.wing_root_chord + self.wing_tip_chord) / 2
        return 2 * self.wing_panel_span * avg_chord / 144  # sq in to sq ft

    @property
    def wing_area_sqft(self) -> float:
        """Wing REFERENCE area in sq ft: gross trapezoid, LE/TE extended to the centreline.

        Both halves, BL 0 (wing_centerline_chord) to the tip BL (wing_tip_chord). This is the
        standard reference-area convention; it matches the manual's 81.99 sq ft (om-1980:p3)
        to 0.4%. The exposed panels alone are wing_exposed_area_sqft.
        """
        avg_chord = (self.wing_centerline_chord + self.wing_tip_chord) / 2
        return self.wing_span * avg_chord / 144  # sq in to sq ft

    @property
    def wing_area(self) -> float:
        """Wing reference area in square feet (alias of wing_area_sqft)."""
        return self.wing_area_sqft

    @property
    def canard_area(self) -> float:
        """Canard planform area in square feet."""
        avg_chord = (self.canard_root_chord + self.canard_tip_chord) / 2
        return (avg_chord * self.canard_span) / 144

    @property
    def wing_aspect_ratio(self) -> float:
        """Aspect ratio of the reference wing: span^2 / reference area.

        Span and area come from the SAME planform, the gross trapezoid tip to tip
        (wing_area_sqft extends the panels to the centreline).
        """
        span_ft = self.wing_span / 12
        return (span_ft**2) / self.wing_area_sqft

    @property
    def wing_le_fs(self) -> float:
        """Wing LE fuselage station (alias for fs_wing_le, used by OpenVSP geometry builder)."""
        return self.fs_wing_le

    @property
    def canard_le_fs(self) -> float:
        """Canard LE fuselage station (alias for fs_canard_le, used by OpenVSP geometry builder)."""
        return self.fs_canard_le

    def to_published_datum(self, internal_fs: float) -> float:
        """Convert a code fuselage station to the published Long-EZ datum.

        Since the 2026-09-29 planform correction, code stations are already in
        the published frame (datum_offset_in = 0), so this is the identity. It
        is kept so existing callers don't break.

        Args:
            internal_fs: Fuselage station in internal coordinates (inches)

        Returns:
            Fuselage station in published Long-EZ datum (inches)
        """
        return internal_fs - self.datum_offset_in


PROVENANCE_STATUSES = frozenset(
    {
        "book",
        "cp-corrected",
        "derived",
        "derived-unsourced",
        "converted-unsourced",
        "unsourced",
        "conflict",
        "positioned-from-text",
    }
)


def _p(status: str, source: str = "", confidence: str = "n/a", note: str = "") -> dict:
    return {"status": status, "source": source, "confidence": confidence, "note": note}


# Where each planform/station value comes from. Statuses: book (plans page), cp-corrected (a
# Canard Pusher correction), derived (computed from book/cp-corrected values; the formula is in the
# note and the source cites the input pages), derived-unsourced (computed from an unverified input),
# converted-unsourced (shifted between frames, never checked), unsourced, conflict, positioned-from-text
# (a value the text places but no page dimensions on its own; always low confidence).
# tests/test_geometry_provenance.py fails if a matching GeometricParams field lacks an entry.
GEOMETRY_PROVENANCE: dict[str, dict] = {
    "canard_span": _p(
        "conflict",
        "om-1980:p3 canard span 11.8 ft",
        "medium",
        "GU planform (om-1980 p3); Roncz planform unconfirmed. Roncz elevator tip-to-tip 130 (cp-43:p1); cobelu ch30 Roncz core jig blocks 126 apart (cobelu:p13); plans GU span 142 (plans-1980:p54, B.L. 71 at p171)",
    ),
    "canard_chord": _p(
        CHORD_STATUS,
        CHORD_SOURCE,
        "medium",
        "GU planform (om-1980 p3); Roncz planform unconfirmed; chord = 12.8*144/141.6",
    ),
    "canard_sweep_le": _p(
        "book",
        "plans-1980:p71",
        "high",
        "zero sweep (ch12 canard installation); p.171 planform agrees",
    ),
    "canard_incidence": _p(
        "unsourced",
        note="set by incidence blocks; value not in the book; CP 47 gives the method (level against top longeron), no angle",
    ),
    "canard_oswald_e": _p("unsourced", note="aero estimate, not a plans value"),
    "canard_le_wl": _p(
        "conflict",
        "plans-1980:p171 W.L. 18.9 at canard",
        "medium",
        "model z is relative to the wing plane (wing_le_wl 0 = book W.L. 17.4, plans-1980:p126/p134). p171 3-view W.L. 18.9 at the canard lower surface (GU, first edition) gives 18.9-17.4 = 1.5; GU template level line W.L. 19.4 (plans-1980:p55) and Roncz template level line W.L. 19.8 (cobelu C-3) are different references; none is labelled as the LE",
    ),
    "canard_vertical_offset_in": _p(
        "conflict",
        "plans-1980:p171 W.L. 18.9 at canard",
        "medium",
        "downwash separation, canard to wing plane; same evidence as canard_le_wl (18.9-17.4 = 1.5); the book drawings put the canard 1.5-2.4 in above the wing plane, 12 had no source",
    ),
    "wing_span": _p(
        "derived",
        "plans-1980:p126 tip rib at B.L. 157 (also p171)",
        "high",
        "2 x 157 = 314.0 (was 313.2, om-1980:p3 26.1 ft). The OM figure is not a rounding of 314 (26.17 ft rounds to 26.2), so it stays a noted conflict and the plans govern geometry. Moved in M2.8 with a ledger row; the analysis NP moves with it",
    ),
    "wing_root_chord": _p(
        "derived",
        "plans-1980:p126 chords 42.7 at BL 55.5, 20.0 at BL 157",
        "medium",
        "linear taper through the printed chords, extrapolated to root BL 23.0: 42.7 + (55.5-23.0)*(42.7-20.0)/(157-55.5) = 49.97 (was 49.90 at BL 23.3, moved with wing_root_bl in M2.8); taper is straight (31.35 printed at BL 106.25 matches)",
    ),
    "wing_tip_chord": _p(
        "book",
        "plans-1980:p126 chord 20.0 at B.L. 157",
        "high",
        "wing tip section chord",
    ),
    "wing_sweep_le": _p(
        "book",
        "plans-1980:p126 22.98 deg LE sweep",
        "high",
        "CP25 LE 113.9 at BL 58 and tip LE F.S. 156 at BL 157 give 23.0 deg, consistent",
    ),
    "wing_dihedral": _p(
        "book",
        "plans-1980:p134 wing flat at 17.4 waterline plane",
        "medium",
        "LE flat at W.L. 17.4 (p126); TE rises with thickness taper; no dihedral angle printed",
    ),
    "fs_nose": _p(
        "book",
        "plans-1980:p171 nose tip F.S. -6.8",
        "medium",
        "nose tip callout on the back-cover 3-view; the datum F.S. 0.0 (om-1980:p25) lies 6.8 in aft of the nose tip; "
        "p171 label read at 500 dpi; first digit closer to 6 than 4, not crisp",
    ),
    "fs_canard_le": _p(
        "book",
        "plans-1980:p171 F.S. 18.7 at B.L. 71",
        "high",
        "back-cover 3-view, canard tip LE; owner check (2026-09-29 by-eye read, recorded in docs/geometry-correction-ledger.md); zero sweep makes the tip LE station the LE station everywhere",
    ),
    "fs_pilot_seat": _p(
        "book",
        "om-1980:p25 pilot moment = weight x 59",
        "high",
        "the pilot's CG station; the model uses this field as the pilot arm (core/analysis.py) and as a loft station; the old F-22 label was wrong (F22 is a forward bulkhead)",
    ),
    "fs_rear_seat": _p(
        "book",
        "om-1980:p25 passenger moment = weight x 103",
        "high",
        "passenger CG station; used as loft station and turtleback start; the old F-28 label was wrong (F28 is a forward bulkhead)",
    ),
    "fs_firewall": _p(
        "book",
        "plans-1980:p101 firewall line at F.S. 125",
        "high",
        "spar aft face F.S. 125 (plans-1980:p88) agrees; p171 side view line at 125",
    ),
    "fs_tail": _p(
        "converted-unsourced",
        note="internal 214.0 shifted by -45.5; no fuselage aft-end station printed in Section I",
    ),
    "fuselage_length": _p(
        "conflict",
        note="fs_tail - fs_nose (175.3); fs_tail unsourced; manual overall length 201.4 (om-1980:p3) includes more than the fuselage; conflict kept",
    ),
    "wing_le_anchor": _p(
        "cp-corrected",
        "cp-text:p25 LPC 7 wing root LE 113.9",
        "high",
        "plans p.171 prints 113.4; CP25 LPC 7 (MEO) corrects to 113.9; the station is the strake/wing LE junction at BL 58 and agrees with p126 (112.9 + 2.5 tan 22.98 = 113.96). The retired 125.61 is a different point: p126 prints FS 125.6 at BL 23 for the FC1 foam edge (the shear web face), not a wing LE, and 125.61 itself was a fitted value in an old frame with no book meaning (M2.7 ruling, docs/geometry-correction-ledger.md). fs_wing_le is derived from this anchor (derived-unsourced via wing sweep)",
    ),
    "wing_centerline_chord": _p(
        "derived",
        "plans-1980:p126 chords 42.7 at BL 55.5, 20.0 at BL 157",
        "medium",
        "straight taper extended to BL 0: wing_root_chord + wing_root_bl*(wing_root_chord - wing_tip_chord)/wing_panel_span = 55.11; sets the reference area span*(c0 + ct)/2 = 81.68 sq ft, cross-check om-1980:p3 wing area 81.99 (0.4%)",
    ),
    "wing_root_bl": _p(
        "book",
        "plans-1980:p126 prints BL 23",
        "high",
        "23.0 (was 23.3, which appears on no page). p118, p119 and p147 print the same BL 23. Moved in M2.8 with a ledger row. wing_root_chord moves 49.90 to 49.97 with it (the same straight taper evaluated at BL 23.0)",
    ),
    "fs_f22": _p(
        "derived",
        "plans-1980:p36 side x 0 is F22",
        "medium",
        "fs_firewall 125 (p101) minus side length 103 (p36); matches the bulkhead name",
    ),
    "fs_f28": _p(
        "derived",
        "plans-1980:p36 F28 at side x 5.65",
        "medium",
        "p41 gives 5.9 from F22's forward face (0.25 difference, F22 thickness/flange)",
    ),
    "fs_panel": _p(
        "derived",
        "plans-1980:p36 panel at side x 17.75",
        "medium",
        "conflict: om-1980:p34 panel reference FS 40 (0.25 in)",
    ),
    "fs_front_seat_bkhd_bottom": _p(
        "derived",
        "plans-1980:p36 front seat bulkhead bottom at side x 41.55",
        "medium",
        "22 + 41.55",
    ),
    "fs_front_seat_bkhd_top": _p(
        "derived",
        "plans-1980:p36 front seat bulkhead top at side x 59.75",
        "medium",
        "22 + 59.75",
    ),
    "fs_rear_seat_bkhd_bottom": _p(
        "derived",
        "plans-1980:p36 rear seat bulkhead bottom 18.0 from aft end",
        "medium",
        "22 + (103 - 18.0) = 107.0",
    ),
    "fs_rear_seat_bkhd_top": _p(
        "derived",
        "plans-1980:p36 rear seat bulkhead top at side x 59.75 + 36.75",
        "medium",
        "22 + 96.5 = 118.5; this is the spar forward face (plans-1980:p88); the top meets the spar cutout's lower forward corner (p38, p39)",
    ),
    "side_panel_length": _p(
        "book", "plans-1980:p36 overall side length 103", "high", "overall side length"
    ),
    "side_panel_top_wl": _p(
        "book",
        "plans-1980:p36 top edge at W.L. 23",
        "high",
        "top edge straight, both top corners square",
    ),
    "side_panel_thickness": _p(
        "book", "plans-1980:p36 side foam 0.8 thick", "high", "side foam thickness"
    ),
    "side_panel_heights": _p(
        "book",
        "plans-1980:p36 depth table at x 0..100 and 103",
        "high",
        "depth below the top edge at side x; spacing per cp-text:p25 LPC 5 (10 in, aft dimension 3 in)",
    ),
    "side_spar_cutout": _p(
        "book",
        "plans-1980:p38 spar cutout 6.5 by 8.5",
        "high",
        "width at the aft end, depth from the top",
    ),
    "side_sight_gauge": _p(
        "book",
        "plans-1980:p36 sight gauge 82 from front, 9.15 down",
        "high",
        "x from front, extent down from top, half-width each way, flat width, foam left",
    ),
    "side_dish": _p(
        "conflict",
        "plans-1980:p36 dish 8 in dia at panel line + 7, 7 down",
        "medium",
        "text p36/p37 says 0.5 deep, section C-C shows 0.3; centre x = panel 17.75 + 7; right side only",
    ),
    "front_seat_bkhd_length": _p(
        "book",
        "plans-1980:p33 front seat bulkhead dimensions",
        "high",
        "28.3 x 23 x 0.8; 0.7 taper both ends; corner notches top 0.7 x 1.5, bottom 0.7 x 0.7",
    ),
    "front_seat_bkhd_width": _p(
        "book",
        "plans-1980:p33 front seat bulkhead dimensions",
        "high",
        "28.3 x 23 x 0.8; 0.7 taper both ends; corner notches top 0.7 x 1.5, bottom 0.7 x 0.7",
    ),
    "front_seat_bkhd_thickness": _p(
        "book",
        "plans-1980:p33 front seat bulkhead dimensions",
        "high",
        "28.3 x 23 x 0.8; 0.7 taper both ends; corner notches top 0.7 x 1.5, bottom 0.7 x 0.7",
    ),
    "front_seat_bkhd_taper": _p(
        "book",
        "plans-1980:p33 front seat bulkhead dimensions",
        "high",
        "28.3 x 23 x 0.8; 0.7 taper both ends; corner notches top 0.7 x 1.5, bottom 0.7 x 0.7",
    ),
    "front_seat_bkhd_notch_top": _p(
        "book",
        "plans-1980:p33 front seat bulkhead dimensions",
        "high",
        "28.3 x 23 x 0.8; 0.7 taper both ends; corner notches top 0.7 x 1.5, bottom 0.7 x 0.7",
    ),
    "front_seat_bkhd_notch_bottom": _p(
        "book",
        "plans-1980:p33 front seat bulkhead dimensions",
        "high",
        "28.3 x 23 x 0.8; 0.7 taper both ends; corner notches top 0.7 x 1.5, bottom 0.7 x 0.7",
    ),
    "rear_seat_bkhd_bottom_width": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "medium",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "rear_seat_bkhd_top_width": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "medium",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "rear_seat_bkhd_length": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "medium",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length; slant from (x 85, side bottom) to (x 96.5, 8.5 down) computes 15.6 vs printed 16.1",
    ),
    "rear_seat_bkhd_thickness": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "high",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "rear_seat_bkhd_side_taper": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "high",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length; taper on both sides per cp-text:p29 clarification",
    ),
    "rear_seat_bkhd_bevel_top_deg": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "high",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "rear_seat_bkhd_bevel_bottom_deg": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "high",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "rear_seat_bkhd_notch": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "high",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "rear_seat_bkhd_access_dia": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "high",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "rear_seat_bkhd_foam_circle_dia": _p(
        "book",
        "plans-1980:p34 rear seat bulkhead dimensions",
        "high",
        "rear seat bulkhead; captain reading: 20.6 bottom width, 18.7 top width, 16.1 slant length",
    ),
    "fuselage_inner_width_stations": _p(
        "derived",
        "plans-1980:p33 width 23; plans-1980:p34 widths 20.6/18.7",
        "medium",
        "inner width between the sides at FS, from the seat bulkhead widths at their stations; aft of 118.5 extrapolate the last segment",
    ),
    "fuselage_inner_width_fwd": _p(
        "unsourced",
        note="forward of the front seat bulkhead the width is not printed; held at 23; p40 top sketch narrows, undimensioned (not measured)",
    ),
    "bottom_foam_thickness": _p(
        "book", "plans-1980:p42 bottom block", "high", "bottom foam block thickness"
    ),
    "bottom_trim_outboard": _p(
        "book", "plans-1980:p42 bottom block", "high", "trim outboard of the side marks"
    ),
    "bottom_aft_trim": _p(
        "book", "plans-1980:p42 bottom block", "high", "trim aft of the rear seat mark"
    ),
    "fs_spar_aft_face": _p(
        "book",
        "plans-1980:p50 aft face of center section spar at B.L. 26.75, F.S. 125.5",
        "high",
        "swept aft face at BL 26.75: 125 + (26.75-23) tan 8.57 = 125.57, so 125.5; the spar is 6.50 deep fore-aft and its centreline aft face is FS 125.0, the firewall line (p101); no conflict",
    ),
    "bl_gear_datum": _p(
        "book",
        "plans-1980:p50 straight-board datum at the spar aft face, B.L. 26.75",
        "high",
    ),
    "main_axle_fwd_of_spar": _p(
        "book",
        "plans-1980:p50 axle centre line 15 in forward of the datum edge",
        "high",
    ),
    "fs_main_axle": _p(
        "derived",
        "plans-1980:p50 figure 1A prints F.S. 110.5",
        "high",
        "fs_spar_aft_face 125.5 minus 15; p171 back cover prints F.S. 110.5 too; Owner's Manual says 110.5 +/-1 (om-1980 p34 per research); property, cannot drift",
    ),
    "wl_main_axle": _p("book", "plans-1980:p171 main axle W.L. -22", "high"),
    "fs_nose_wheel": _p(
        "conflict",
        "plans-1980:p171 back cover prints nose wheel F.S. 17",
        "medium",
        "Owner's Manual says about 20 (sample 19.6); conflict kept; nose gear is chapter 13",
    ),
    "ng50_travel_deg": _p(
        "book",
        "plans-1980:p73 NG50 arms travel 156 deg between the NG14 spacers",
        "high",
    ),
    "nose_crank_turns": _p(
        "book",
        "plans-1980:p73 the pilot's crank uses 10.8 turns for full travel",
        "high",
    ),
    "nose_crank_seconds_min": _p(
        "book", "plans-1980:p73 retraction takes five to seven seconds", "high"
    ),
    "nose_crank_seconds_max": _p(
        "book", "plans-1980:p73 retraction takes five to seven seconds", "high"
    ),
    "wl_fuselage_bottom_3view": _p(
        "book",
        "plans-1980:p171 back-cover side view W.L. 0.9 at the fuselage bottom",
        "medium",
        "captain read of the label on the 200 dpi page; the model's own bottom_z is a fitted outline, this is the printed height",
    ),
    "wl_nose_wheel": _p(
        "cp-corrected",
        "cp-text:p25 LPC 24 nose gear CL at W.L. -22 not -23",
        "medium",
        "printed label struck through on p171, struck digit unclear at 400 dpi (-23 or -25); the owner's note and CP25 LPC 24 say -22",
    ),
    "gear_tip_back_deg": _p(
        "book",
        "plans-1980:p171 12 deg line from the main contact",
        "high",
        "ground-handling note only; CG height is unsourced so no tip-back verdict",
    ),
    "gear_toe_in_b_minus_a": _p(
        "book",
        "plans-1980:p52 toe-in B minus A 0.2 to 0.45",
        "high",
        "total over gear_toe_in_square_in",
    ),
    "gear_toe_in_square_in": _p("book", "plans-1980:p52 toe-in squares 24 in", "high"),
    "skin_third_ply_fs_range": _p(
        "derived",
        "plans-1980:p46 strip 50 long ending 15 forward of F.S. 125",
        "high",
        "labelled F.S. 60 to 110; 125 - 15 = 110, 110 - 50 = 60",
    ),
    "skin_strip_width": _p("book", "plans-1980:p46 3 in wide strip", "high"),
    "skin_strip_lengths": _p("book", "plans-1980:p46 strip lengths 52/50/48", "high"),
    "skin_firewall_lap": _p(
        "book", "plans-1980:p46 skin laps 1/2 in onto firewall", "high"
    ),
    "skin_bottom_overlap": _p(
        "book", "plans-1980:p46 2 in overlap at bottom centre line", "high"
    ),
    "skin_ply_angle_deg": _p(
        "book", "plans-1980:p46 two plies crossed at 30 deg", "high"
    ),
    "belt_insert_fs_range": _p(
        "derived",
        "plans-1980:p46 insert 5 in long, 32.7 from the F.S. 22 edge",
        "medium",
        "32.7 from the FS 22 edge read as reaching the insert's aft end: 22 + 27.7 = 49.7, 22 + 32.7 = 54.7; left side only",
    ),
    "rollover_width": _p("book", "plans-1980:p47 roll-over 23 wide", "high"),
    "rollover_base_height": _p(
        "book", "plans-1980:p47 roll-over 4 high at base", "high"
    ),
    "rollover_shoulder": _p(
        "book", "plans-1980:p47 roll-over 7.3 each shoulder", "high"
    ),
    "rollover_peak_base": _p("book", "plans-1980:p47 roll-over 8.4 peak base", "high"),
    "rollover_peak_height": _p(
        "book", "plans-1980:p47 roll-over 12.6 peak height", "high"
    ),
    "rollover_notch": _p("book", "plans-1980:p47 roll-over 0.7 by 1.4 notches", "high"),
    "rollover_side_ends": _p(
        "book", "plans-1980:p47 roll-over side ends 3 and 4.5", "high"
    ),
    "rollover_back_triangle": _p(
        "book", "plans-1980:p47 roll-over triangle 8.1 by 12.7", "high"
    ),
    "rollover_shoulder_top": _p(
        "book", "plans-1980:p47 roll-over small piece 6.9 by 2.7", "high"
    ),
    "rollover_foam_thickness": _p("book", "plans-1980:p47 roll-over 0.35 foam", "high"),
    "rollover_side_length": _p(
        "cp-corrected",
        "cp-text:p26 LPC 37 roll-over sides 13",
        "high",
        "printed 12.7 on p47; CP26 LPC 37 makes it 13",
    ),
    "rollover_insert": _p(
        "book", "plans-1980:p48 inserts 1.25 by 1.25 by 1/4 ply", "high"
    ),
    "rollover_harness_insert_spacing": _p(
        "cp-corrected",
        "cp-text:p27 LPC 52 harness insert spacing 4.0",
        "high",
        "printed 4.5 on p47; CP27 LPC 52 makes it 4.0 and moves the insert outboard 1/2 in",
    ),
    "rollover_harness_insert_from_end": _p(
        "book", "plans-1980:p47 harness insert 1.25 from the shoulder end", "high"
    ),
    "rollover_canopy_insert_from_peak": _p(
        "book", "plans-1980:p47 canopy insert 1.5 and 1.25 below the peak", "high"
    ),
    "rollover_map_slot": _p(
        "book", "plans-1980:p48 map slot 1.8 by 8, right side only", "high"
    ),
    "rollover_baggage_hole_dia": _p(
        "book",
        "plans-1980:p48 rear access hole 3 3/4 dia",
        "medium",
        "the research read 3/4; the page reads 3 3/4 at 400 dpi",
    ),
    "belt_front_fwd_of_front_seat_bkhd": _p(
        "book",
        "plans-1980:p49 front belt 5 forward of front seat bulkhead",
        "medium",
        "hand sketch, not to scale",
    ),
    "belt_rear_fwd_of_rear_seat_bkhd": _p(
        "book",
        "plans-1980:p49 rear belt 8 forward of rear seat bulkhead",
        "medium",
        "hand sketch, not to scale; the research said 8 between",
    ),
    "step_size": _p("book", "plans-1980:p49 step 1.8 by 4.5 by 4.5", "high"),
    "step_thickness": _p("book", "plans-1980:p49 step 1/8 2024-T3", "high"),
    "step_min_bend_radius": _p(
        "book", "plans-1980:p49 step min bend radius 0.5", "high"
    ),
    "gear_jig_block": _p(
        "book",
        "plans-1980:p53 jig block 1/4 ply, 1 in radius, 5/8 hole; p51 2 in wide",
        "high",
        "(width 2, radius 1, hole 0.625, below hole 0.7, bevel 0.8, thickness 0.25)",
    ),
    "gear_tube": _p(
        "book", "plans-1980:p53 4130N tube 5/8 OD, 0.049 wall, 6.75 long", "high"
    ),
    "gear_tube_showing": _p(
        "book", "plans-1980:p50 about 0.65 of tube shows each side", "high", "also p53"
    ),
    "gear_tab_pads": _p(
        "book", "plans-1980:p53 pads 2.5 by 12, 2.5 by 3.5, 2.5 by 2.5", "high"
    ),
    "gear_extrusion": _p(
        "book", "plans-1980:p52 extrusion 1/4 by 2 by 2, 6061-T6", "high"
    ),
    "fs_nose_wheel_manual": _p(
        "conflict",
        "om-1980:p35 nose arm about 20.0 (sample table 19.6)",
        "medium",
        "pair with fs_nose_wheel 17 (p171); sample table prints 19.6; the manual's figure comes from an owner weigh-in method, not a build dimension; unresolved without the A6/A7 side view",
    ),
    "ng6_width_in": _p(
        "book",
        "plans-1980:p73 NG6 assembly width 2.75",
        "high",
        "CP11 hint and CP10 LPC agree",
    ),
    "ng6_bore_height_in": _p(
        "book", "plans-1980:p73 NG6 bore centre 1.25 above the base", "high"
    ),
    "ng7_length_in": _p("book", "plans-1980:p73 NG7 spacer 2.75 long", "high"),
    "ng30_thickness_in": _p("book", "plans-1980:p77 NG30 foam 0.2 thick", "high"),
    "ng30_gap_in": _p(
        "book", "plans-1980:p77 3.0 inside between the NG30 plates", "high"
    ),
    "ng3_to_ng7_in": _p(
        "book",
        "plans-1980:p78 NG3 bolt to NG7 centre 6.71",
        "high",
        "tolerance 0.05 in",
    ),
    "nose_strut_pivot_to_pivot_in": _p(
        "book",
        "plans-1980:p81 strut pivot to pivot 25.5",
        "medium",
        "thin decimal in the retracted sketch",
    ),
    "floor_block_length_in": _p(
        "book", "plans-1980:p79 floor block length 20.9", "medium", "hand-dimensioned"
    ),
    "floor_block_width_in": _p(
        "book",
        "plans-1980:p79 floor block 8.2 at one end",
        "medium",
        "which end is 1.6 and which is 8.2 is the captain's reading of the page",
    ),
    "floor_block_thickness_in": _p(
        "book",
        "plans-1980:p79 floor block 1.6 at the shallow end",
        "medium",
        "which end is 1.6 and which is 8.2 is the captain's reading of the page",
    ),
    "side_block_length_in": _p(
        "book", "plans-1980:p79 side block length 21.9", "medium", "hand digits"
    ),
    "side_block_height_f22_in": _p(
        "book", "plans-1980:p79 side block 15.6 high at F22", "medium", "hand digits"
    ),
    "side_block_height_ng31_above_in": _p(
        "book",
        "plans-1980:p79 side block 5.5 above the NG31 end",
        "medium",
        "hand digits",
    ),
    "side_block_height_ng31_below_in": _p(
        "book",
        "plans-1980:p79 side block 2.8 below the NG31 end",
        "medium",
        "hand digits",
    ),
    "top_block_length_in": _p(
        "book",
        "plans-1980:p82 top block length 19.3",
        "medium",
        "top view; orientation is a reading",
    ),
    "top_block_width_aft_in": _p(
        "book",
        "plans-1980:p82 top block 19.6 on the aft edge",
        "medium",
        "top view; orientation is a reading",
    ),
    "top_block_width_fwd_in": _p(
        "book",
        "plans-1980:p82 top block 7.0 on the forward edge",
        "medium",
        "top view; orientation is a reading",
    ),
    "pedal_block_from_ng30_in": _p(
        "book", "plans-1980:p79 pedal pivot block 6.1 from NG30", "high"
    ),
    "static_port_fwd_of_panel_in": _p(
        "book",
        "plans-1980:p82 static port 8 forward of the panel",
        "high",
        "static port is on the left side",
    ),
    "fs_static_port": _p(
        "derived",
        "plans-1980:p82 static port 8 forward of the panel",
        "medium",
        "fs_panel minus static_port_fwd_of_panel_in (8.0); left side; fs_panel itself is 39.75 against the manual's 40; property, cannot drift",
    ),
    "wl_static_port": _p(
        "book",
        "plans-1980:p82 static port 10 below the top longerons, W.L. 13",
        "high",
        "left side",
    ),
    "fs_ng31_min": _p(
        "derived",
        "plans-1980:p79 side block length 21.9 back from F22",
        "medium",
        "fs_f22 minus side_block_length_in; block lengths hand-dimensioned, may not share a line, so a range with fs_ng31_max, never one value",
    ),
    "fs_ng31_max": _p(
        "derived",
        "plans-1980:p79 floor block length 20.9 back from F22",
        "medium",
        "fs_f22 minus floor_block_length_in; block lengths hand-dimensioned, may not share a line, so a range with fs_ng31_min, never one value",
    ),
    "elevator_outboard_end_bl_in": _p(
        "book",
        "cobelu:pC-1 ch30 figure C-1 plan dimension 65 from B.L. 0 to the elevators' outer ends",
        "medium",
        "captain read of the rotated figure; both elevators end at this |B.L.|; 65.0 - 55.7 = 9.3 and 72.7 - 65.0 = 7.7 match the inboard labels on the figure",
    ),
    "elevator_inboard_bl_right_in": _p(
        "conflict",
        "cobelu:pC-1 outboard end 65.0 minus right length 55.7",
        "medium",
        "foam inboard end; figure labels B.L. 9.3; property, cannot drift. drawn stock end; the figure says trim to fit the fuselage and the 1/16 in clearance puts the trimmed end at the fuselage side (about +/-11.5): span vs fuselage sides unresolved; do not move",
    ),
    "elevator_inboard_bl_left_in": _p(
        "conflict",
        "cobelu:pC-1 mirror of the right foam end, -(65.0 - 55.7)",
        "medium",
        "left foam inboard end, derived as the mirror of the right (figure labels 9.2 (left); 0.1 in difference noted); property, cannot drift. drawn stock end; the figure says trim to fit the fuselage and the 1/16 in clearance puts the trimmed end at the fuselage side (about +/-11.5): span vs fuselage sides unresolved; do not move",
    ),
    "elevator_tube_end_bl_left_in": _p(
        "derived",
        "cobelu:pC-1 left length 72.7 minus outboard end 65.0",
        "medium",
        "figure labels B.L. 7.7 at the left TUBE end: the bare 1 in tube (16.9 in dimension, NC-5A trim belcrank at B.L. 0, CS-11/NC-12A at this end) "
        "crosses the fuselage and the centreline; the foam does not; property, cannot drift",
    ),
    "elevator_length_right_in": _p(
        "book",
        "cobelu:pC-1 ch30 figure C-1 right elevator 55.7",
        "medium",
        "stock tube 57; trim 1.3 agrees with the left side; owner holds no scan of this figure",
    ),
    "elevator_length_left_in": _p(
        "book",
        "cobelu:pC-1 ch30 figure C-1 left elevator 72.7",
        "medium",
        "stock tube 74; trim 1.3 agrees with the right side; owner holds no scan of this figure",
    ),
    "elevator_travel_up_target_deg": _p(
        "book",
        "cobelu:pch30 ch30 text up-travel at least 15 deg",
        "medium",
        "Roncz elevator; the GU 20/22 deg and the manual's 22 +/-2 are different airplanes' numbers and must not be used",
    ),
    "elevator_travel_up_floor_deg": _p(
        "book",
        "cobelu:pch30 ch30 text 12.5 deg up is the absolute floor",
        "medium",
        "Roncz elevator; the GU 20/22 deg and the manual's 22 +/-2 are different airplanes' numbers and must not be used",
    ),
    "elevator_travel_down_deg": _p(
        "book",
        "cobelu:pch30 ch30 text 30 deg trailing edge down",
        "medium",
        "Roncz elevator; the GU 20/22 deg and the manual's 22 +/-2 are different airplanes' numbers and must not be used",
    ),
    "elevator_hinge_bl_in": _p(
        "positioned-from-text",
        "cobelu:pch30 ch30 figure 30-33 hinge stations",
        "low",
        "BL 9.2, 34.1, 59 as the text places them; fig C-1 shows 57.0 near the outer CS-10, so 59 vs 57.0 is unverified; the right side draws the first as 7.8",
    ),
    "elevator_hinge_bl_right_first_drawn_in": _p(
        "positioned-from-text",
        "cobelu:pch30 ch30 figure 30-33 right first hinge as drawn",
        "low",
        "right side draws 7.8 where the left reads 9.2; unresolved",
    ),
    "elevator_slot_gap_in": _p(
        "book", "cobelu:pch30 ch30 text hinge slot gap about 0.2", "medium"
    ),
    "elevator_hinge_offset_in": _p(
        "book",
        "cobelu:pch30 ch30 figure 30-46 hinge pivot 0.55 aft of tube leading edge",
        "medium",
    ),
    "elevator_tube_od_in": _p(
        "book", "cobelu:pch30 ch30 text 1 in OD torque tube", "medium"
    ),
    "elevator_pin_right_in": _p(
        "book",
        "cobelu:pch30 ch30 text right hinge pin trimmed to 36",
        "medium",
        "the parts list shows two 61 in pins; the trim step is followed",
    ),
    "elevator_pin_left_in": _p(
        "book", "cobelu:pch30 ch30 text left hinge pin trimmed to 61", "medium"
    ),
    "cs11_lead_dims": _p(
        "book",
        "cobelu:pch30 ch30 figure 30-59 CS-11 lead block 2 x 0.6 x 0.8",
        "medium",
        "which edge is which is not page-read; no mass is sourced, lead density is not from a plans source",
    ),
    "cs10_inboard_from_end_in": _p(
        "book",
        "cobelu:pch30 ch30 figure 30-53 CS-10 inboard side 7.5 from the elevator end",
        "medium",
        "the CS-10 profile is not dimensioned",
    ),
    "balance_pocket_clearance_in": _p(
        "book",
        "cobelu:pch30 ch30 text balance weight clears the pocket by 0.06",
        "medium",
    ),
    "elevator_fuselage_gap_in": _p(
        "book",
        "plans-1980:p72 elevator 1/16 from the fuselage side",
        "medium",
        "cobelu ch30 agrees; this is a fit gap, not a travel value",
    ),
    "elevator_fuselage_round_tube_gap_in": _p(
        "book",
        "cobelu:pch30 ch30 text 0.1 clearance round the tubes at 15 up and 30 down",
        "medium",
        "plans-1980:p72 gives the same 0.1 for round tubes",
    ),
    "elevator_weight_ceiling_left_lb": _p(
        "book",
        "om-1980:p30 left elevator ceiling with balance installed 3.9",
        "high",
        "check bound, not a mass of any part",
    ),
    "elevator_weight_ceiling_right_lb": _p(
        "book",
        "om-1980:p30 right elevator ceiling with balance installed 3.6",
        "high",
        "check bound, not a mass of any part",
    ),
    # --- chapters 14-17 (M2.5): centre-section spar, firewall, controls, trim ---
    **{
        k: _p("book", "plans-1980:p88 spar planform and elevations", "high", n)
        for k, n in {
            "spar_fwd_face_fs": "forward face FS 118.5 from BL 0 to the kink",
            "spar_aft_face_fs_centre": "centreline aft face = firewall line FS 125.0; the swept aft face reaches 125.5 at BL 26.75",
            "spar_kink_bl": "faces turn outboard at BL 23.0",
            "spar_outboard_sweep_deg": "outboard faces swept 8.57 deg aft",
            "spar_half_span_bl": "half span BL 56.46",
            "spar_chord_centreline_in": "6.50 fore-aft at the centreline",
            "spar_face_length_fwd_outboard_in": "forward face outboard of the kink, 33.834 = 33.46/cos 8.57",
            "spar_face_length_aft_outboard_in": "aft face outboard of the kink, 32.865 = 32.5/cos 8.57",
            "spar_hard_point_spacing_aft_in": "hard-point spacing along the aft face",
            "spar_depth_in": "8.50 deep, WL 22.0 to 13.5",
            "spar_top_wl": "top at WL 22.0",
            "spar_bottom_wl": "bottom at WL 13.5",
            "spar_bottom_wl_outboard": "bottom rises to WL 15.15 at BL 56.46",
            "spar_top_flat_to_bl": "top flat to BL 25, then tapers aft",
            "spar_hp_inboard_bl_in": "inboard hard point BL 25.0, one bolt per wing; attach-bolt FS is not printed (comes with ch19)",
            "spar_hp_inboard_wl_in": "inboard hard point WL 20.25",
            "spar_hp_outboard_bl_in": "outboard hard points BL 53.5, two bolts per wing; nut access hole centred here (p87, p92)",
            "spar_hp_outboard_wl_in": "outboard hard points at WL 20.5 and WL 16.3",
        }.items()
    },
    "spar_bottom_flat_to_bl": _p(
        "book",
        "plans-1980:p88 bottom flat to about BL 9",
        "medium",
        "the word about is in the page; the rise to WL 15.15 is straight",
    ),
    "spar_top_wl_outboard": _p(
        "book",
        "plans-1980:p88 WL 21.7 label at outboard end",
        "medium",
        "hand digits; not cross-checked",
    ),
    "spar_chord_square_outboard_in": _p(
        "derived",
        "plans-1980:p88 centreline chord and 8.57 deg sweep",
        "high",
        "6.50 cos 8.57 = 6.43, the chord square to the outboard face; property, cannot drift",
    ),
    "spar_fwd_face_fs_tip": _p(
        "derived",
        "plans-1980:p88 forward face 118.5, kink BL 23, sweep 8.57 deg",
        "high",
        "118.5 + (56.46-23) tan 8.57 = 123.54; property, cannot drift",
    ),
    "spar_aft_face_fs_bl_55_5": _p(
        "derived",
        "plans-1980:p88 aft face 125.0, kink BL 23, sweep 8.57 deg",
        "medium",
        "125 + 32.5 tan 8.57 = 129.89; p88 prints 129.9 at BL 55.5 in hand digits, medium-high, and agrees; property",
    ),
    **{
        k: _p("book", "plans-1980:p90 parts sheet", "high", n)
        for k, n in {
            "spar_end_bulkhead_width_in": "CS5 and CS8 end bulkheads 6.30 wide",
            "spar_end_bulkhead_height_in": "CS5 and CS8 end bulkheads 6.83 tall",
            "spar_foam_height_centre_in": "CS1 foam 8.41 high at the centreline",
            "spar_foam_height_kink_in": "CS1 foam 7.94 high at BL 23",
            "spar_foam_height_end_in": "CS1 foam 6.83 high at the ends",
        }.items()
    },
    "spar_cap_tape_width_in": _p("book", "plans-1980:p85 cap tape 3 wide", "high"),
    "spar_ply_thickness_laid_in": _p(
        "book", "plans-1980:p85 text, ply as laid 0.0375", "high", "stock tape is 0.035"
    ),
    "spar_ply_thickness_stock_in": _p(
        "book", "plans-1980:p85 text, stock tape 0.035", "high"
    ),
    "spar_top_cap_strips_in": _p(
        "book",
        "plans-1980:p86 top cap, 12 plies",
        "high",
        "four full 113 strips then 100 down to 30; sums to 972",
    ),
    "spar_bottom_cap_strips_in": _p(
        "book",
        "plans-1980:p86 bottom cap, 9 plies",
        "high",
        "three full 113 strips then 96 down to 26; sums to 705, total 1677. Cobelu's four full bottom strips is rejected: scan p85 prints three and only three makes 1677",
    ),
    "spar_top_cap_partial_end_bl": _p(
        "book",
        "plans-1980:p86 top cap ply end stations",
        "high",
        "BL 15 to 50, strip length is twice the end BL",
    ),
    "spar_bottom_cap_partial_end_bl": _p(
        "book",
        "plans-1980:p86 bottom cap ply end stations",
        "high",
        "BL 13 to 48, strip length is twice the end BL",
    ),
    "spar_full_ply_end_bl": _p(
        "book",
        "plans-1980:p86 full plies end at BL 55.5",
        "high",
        "p85 shows an unresolved hand figure 29.84 (29.84 - 28.82 = 1.02, near the 1.0 setback, unproven); not used",
    ),
    "spar_spruce_block_in": _p(
        "book", "plans-1980:p86 spruce blocks 1 by 1 by 3", "high"
    ),
    "spar_spruce_block_bl": _p(
        "book", "plans-1980:p86 spruce blocks at BL +/-7.5, top and bottom", "high"
    ),
    "spar_em12_length_in": _p(
        "book", "plans-1980:p87 EM12 angle 8.0 long", "high", "1x1x1/8 angle"
    ),
    "spar_em12_count": _p("book", "plans-1980:p87 EM12 four off", "high"),
    "spar_lwa_sizes": _p(
        "cp-corrected",
        "cp-text:p43 CP43 LPC 119 LWA4 and LWA5 heights",
        "high",
        "p90 prints LWA4 1.5x1/4 and LWA5 2x1/4; CP43 corrects the heights to 1.75 and 2.25, the model values. "
        "LWA1 1.5x1/8 x6, LWA2 2.5x1/8 x4, LWA3 6.4x1/8 x4 as printed (plans-1980:p90); all 2 wide, 2024-T3",
    ),
    "spar_lwa1_outboard_setback_in": _p(
        "cp-corrected",
        "cp-text:p25 CP25 LPC 28 LWA1 setback 0.75",
        "high",
        "p85 printed 1.0 outside CS5/CS8; corrected to 0.75",
    ),
    "spar_baggage_hole_in": _p(
        "book",
        "plans-1980:p87 baggage hole 14 long by 5 high",
        "medium",
        "forward face, centred; the top near WL 20 is a hand tick, medium",
    ),
    "spar_nut_access_hole_dia_in": _p(
        "book",
        "plans-1980:p87 nut access hole 2.25 diameter",
        "high",
        "at BL 53.5 through the bottom (p92 agrees)",
    ),
    "ctl_torque_tube_hole_dia_in": _p(
        "book", "plans-1980:p101 torque-tube hole 1 in diameter", "high"
    ),
    "ctl_torque_tube_hole_bl_in": _p(
        "book",
        "plans-1980:p98 text, hole at BL 6.2 right",
        "medium",
        "p101 BL ticks 4.8 and 9.2 are low-confidence hand reads and are not used",
    ),
    "ctl_torque_tube_hole_wl_in": _p("book", "plans-1980:p101 hole at WL 12.3", "high"),
    "ctl_rudder_conduit_wl_in": _p(
        "book", "plans-1980:p103 rudder conduits at WL 8", "high"
    ),
    "ctl_rudder_conduit_length_in": _p(
        "book", "plans-1980:p103 conduits 82 long", "high"
    ),
    "ctl_stick_pivot_fs_front": _p(
        "book",
        "plans-1980:p100 front stick pivot plane FS 45.5",
        "medium",
        "CS108 and CS109 plane; hand digits",
    ),
    "ctl_stick_pivot_fs_rear": _p(
        "book",
        "plans-1980:p100 rear stick pivot plane FS 89.7",
        "medium",
        "CS117 and CS118 plane; hand digits",
    ),
    "ctl_stick_cant_inboard_deg": _p(
        "book",
        "plans-1980:p97 stick tilts 5 deg inboard",
        "high",
        "at neutral aileron; also p98, p102",
    ),
    "ctl_stick_cant_forward_deg": _p(
        "book",
        "plans-1980:p98 stick tilts 5 deg forward",
        "high",
        "at neutral elevator; no pitch stop is printed anywhere, so stops are representational and carry no number",
    ),
    "ctl_roll_travel_deg": _p(
        "book",
        "plans-1980:p102 roll 20 deg each way from the cant",
        "high",
        "also p97, p98",
    ),
    "ctl_cs103_length_in": _p("book", "plans-1980:p98 CS103 6.1 long", "high"),
    "ctl_cs110_length_in": _p(
        "book", "plans-1980:p99 CS110 39.2, trim to length", "high"
    ),
    "ctl_cs105_length_in": _p("book", "plans-1980:p99 CS105 42.9, trim to fit", "high"),
    "ctl_cs106_length_in": _p("book", "plans-1980:p99 CS106 3.8", "high"),
    "ctl_cs115_length_in": _p("book", "plans-1980:p102 CS115 4.2", "high"),
    "ctl_cs116_length_in": _p("book", "plans-1980:p102 CS116 4.4", "high"),
    "ctl_cs121_length_in": _p(
        "book", "plans-1980:p102 CS121 29.5, trim to fit", "high"
    ),
    "ctl_cs119_length_in": _p(
        "cp-corrected", "cp-text:p26 CP26 LPC 29 CS119 4.1", "high", "plans printed 3.1"
    ),
    "ctl_elevator_arm_gu_in": _p(
        "book",
        "plans-1980:p102 GU CS12 elevator arm 1.9",
        "medium",
        "GU schematic only; not the Roncz elevator. GU travel values 20 and 22 are different-airplane numbers and are not carried",
    ),
    "ctl_elevator_arm_fit_in": _p(
        "unsourced",
        "",
        "low",
        "fitted: GU arm 1.9 is a size hint only, Roncz arm not printed; representational, drives the pushrod kinematics sketch only",
    ),
    "ctl_stick_lever_fit_in": _p(
        "unsourced",
        "",
        "low",
        "fitted: stick rod-end lever not printed; representational, drives the pushrod kinematics sketch only",
    ),
    "trim_panel_face_fs_in": _p(
        "book",
        "plans-1980:p106 panel face FS 40",
        "high",
        "fs_panel carries 39.75 unchanged; reference only",
    ),
    "trim_pth_dim_from_panel_in": _p(
        "book", "plans-1980:p106 PTH left end 9.5 from the panel", "high"
    ),
    "trim_pth_leftmost_fs": _p(
        "conflict",
        "plans-1980:p106 panel face 40 plus 9.5",
        "high",
        "derived 49.5; the p106 label reads 49.8 (trim_pth_leftmost_fs_label), 0.3 in apart; nothing moves to 49.8; property",
    ),
    "trim_pth_leftmost_fs_label": _p(
        "conflict",
        "plans-1980:p106 label FS 49.8",
        "medium",
        "pair with trim_pth_leftmost_fs 49.5 derived; unresolved",
    ),
    "trim_handle_pivot_wl_in": _p(
        "book", "plans-1980:p106 trim handle pivot WL 8.6", "high"
    ),
    "trim_friction_bolt_wl_in": _p(
        "book", "plans-1980:p106 lower friction bolt WL 7.1", "high"
    ),
    "trim_swage_from_sleeve_in": _p(
        "book", "plans-1980:p106 swages 5.6 and 6.2 from the panel sleeve", "high"
    ),
    "trim_sleeve_bl_in": _p(
        "cp-corrected",
        "cp-text:p25 CP25 addendum sleeve BL 9.5",
        "medium",
        "not on the scan",
    ),
    "trim_sleeve_wl_in": _p(
        "cp-corrected",
        "cp-text:p25 CP25 addendum sleeve WL 9.6 and 8.3",
        "medium",
        "not on the scan",
    ),
    "trim_spring_pts_in": _p(
        "book", "plans-1980:p105 PTS spring 6.0 free, 9.0 installed", "high"
    ),
    "trim_spring_rts_in": _p(
        "book", "plans-1980:p105 RTS spring 2.0 free, 3.0 installed", "high"
    ),
    "trim_spring_cs_in": _p(
        "book",
        "plans-1980:p105 CS spring 0.5 and 0.25",
        "high",
        "pair order as listed; not re-read as free and installed",
    ),
    "trim_nc5a_belcrank_bl_left_in": _p(
        "positioned-from-text",
        "cobelu:pC-1 ch30 figure C-1 NC-5A at the left tube inboard end, BL 9.2",
        "low",
        "medium at best; the earlier BL 0 claim is unsupported (BL 0 is the dimension datum); p101 ticks 4.8 and 9.2 are a separate low read",
    ),
    "trim_cs202_extra_spacer_in": _p(
        "book",
        "cobelu:pch30 ch30 extra 0.4 CS-202 spacer at the elevator-end rod end",
        "medium",
        "GU plans list two CS202, the Roncz parts list three",
    ),
    # --- chapter 18 (M2.6): canopy ---
    "canopy_plexi_length_in": _p(
        "book", "plans-1980:p108 plexiglass 68 long", "high", "printed twice, identical"
    ),
    "canopy_rear_cut_fs": _p(
        "cp-corrected",
        "cp-text:p27 CP27 LPC 43 rear cut FS 117",
        "high",
        "p111 prints FS 117 and 8 in to the firewall (125 - 8); LPC 43 corrects the hinge dimensions on p114 to run from FS 117; 117 - 59 - 1.25 = 56.75 agrees with SC-1",
    ),
    "canopy_pad_length_in": _p("book", "plans-1980:p112 pads 2.5 long", "high"),
    "canopy_pad_aft_edge_left_in": _p(
        "book",
        "plans-1980:p112 left pads 11, 41, 59, 71 forward of FS 117",
        "high",
        "distance to each pad's aft edge; the 59 pad is the safety catch",
    ),
    "canopy_pad_aft_edge_right_in": _p(
        "book",
        "plans-1980:p112 right pads 20, 25.5, 48, 53.5 forward of FS 117",
        "high",
        "distance to each pad's aft edge; these are the four hinge pads (p113)",
    ),
    "canopy_safety_catch_fs": _p(
        "book",
        "plans-1980:p116 SC-1 at F.S. 56.75",
        "high",
        "CP25 p3 says 57; compatible",
    ),
    "canopy_door_size_in": _p(
        "book",
        "plans-1980:p116 door 4.3 by 3.7",
        "high",
        "left side; position is not dimensioned to a station",
    ),
    "canopy_check_a_min_in": _p(
        "book",
        "plans-1980:p109 check A at least 13.5",
        "high",
        "CP26 p7 repeats it; measured 6 in forward of the headrest",
    ),
    "canopy_check_b_in": _p(
        "book",
        "plans-1980:p109 check B 12.3",
        "high",
        "at 15 in forward of the firewall; CP26 p7 allows trimming the aft flange",
    ),
    "canopy_check_datum_wl": _p(
        "book", "plans-1980:p109 checks A and B above the longerons, WL 23", "high"
    ),
    "canopy_front_cut_fs": _p(
        "conflict",
        "plans-1980:p111 14.0 aft of an unnamed vertical",
        "low",
        "two readings, no page names the datum: the F28 notch (FS 27.65) gives 41.65, carried; the panel (FS 39.75, step 6 text warns against cutting it) gives 53.75, which plans-1980:p112 contradicts (front left pad FS 43.5 to 46 lies forward of it); unresolved, drawn representational",
    ),
    "canopy_latch_labels_fs": _p(
        "conflict",
        "plans-1980:p117 latch labels FS 104, 74, 44",
        "medium",
        "pair with canopy_latch_pad_centres_fs 104.75, 74.75, 44.75 derived; 0.75 in apart, unresolved (labels may mark a pad forward edge)",
    ),
    "canopy_open_past_vertical_deg": _p(
        "book",
        "plans-1980:p115 canopy opens about 15 degrees past vertical",
        "high",
        "text",
    ),
    "canopy_latch_pad_centres_fs": _p(
        "conflict",
        "plans-1980:p112 rear cut 117, left pad aft edges 11, 41, 71, pad 2.5",
        "high",
        "derived 104.75, 74.75, 44.75; the p117 labels read 104, 74, 44 (canopy_latch_labels_fs); property",
    ),
    "canopy_hinge_spans_fs": _p(
        "derived",
        "plans-1980:p112 right pad stations, p114 hinge",
        "medium",
        "FS 89 to 97 and 61 to 69, each the span of two 2.5 in pads; the hinge length itself is not printed; property",
    ),
    "canopy_check_a_wl": _p(
        "derived",
        "plans-1980:p109 WL 23 plus 13.5",
        "high",
        "WL 36.5 at least; property",
    ),
    "canopy_check_b_wl": _p(
        "derived", "plans-1980:p109 WL 23 plus 12.3", "high", "WL 35.3; property"
    ),
    "canopy_check_b_fs": _p(
        "derived",
        "plans-1980:p109 15 in forward of the firewall FS 125",
        "high",
        "FS 110; property",
    ),
    # --- chapter 19 (M2.7): wings ---
    "wing_book_rib_bl": _p(
        "book",
        "plans-1980:p126 rib stations BL 55.5, 106.25, 157; p127 adds the BL 23 root rib",
        "high",
        "BL 23 is the inboard core FC1 root rib, not the analysis root_bl 23.3 (wing_root_bl)",
    ),
    "wing_book_le_fs_bl_55_5": _p(
        "book",
        "plans-1980:p126 LE FS 112.9 at BL 55.5",
        "high",
        "re-read on the page image; chord 155.6 - 112.9 = 42.7 agrees",
    ),
    "wing_book_le_fs_tip": _p(
        "book",
        "plans-1980:p126 LE FS 156 at BL 157",
        "high",
        "p171 prints 156 too",
    ),
    "wing_book_le_fs_bl_106_25_printed": _p(
        "conflict",
        "plans-1980:p126 LE label FS 134.95 at BL 106.25",
        "low",
        "pair with wing_le_fs_bl_106_25_derived 134.45 (TE 165.8 less chord 31.35) and the 22.98 deg line 134.42; the page's hand renders 4 like 9 elsewhere; the model uses the straight line and is unaffected",
    ),
    "wing_le_fs_bl_106_25_derived": _p(
        "conflict",
        "plans-1980:p126 TE 165.8 and chord 31.35 at BL 106.25",
        "medium",
        "derived 134.45; the printed LE label reads 134.95 (wing_book_le_fs_bl_106_25_printed), 0.5 in apart, carried as a pair; property",
    ),
    "wing_le_fs_bl_106_25_line": _p(
        "derived",
        "plans-1980:p126 LE FS 112.9 at BL 55.5, 22.98 deg",
        "high",
        "112.9 + 50.75 tan 22.98 = 134.42; property",
    ),
    "wing_le_fs_bl_58": _p(
        "derived",
        "plans-1980:p126 LE FS 112.9 at BL 55.5, 22.98 deg",
        "high",
        "112.9 + 2.5 tan 22.98 = 113.96, agrees with CP25 LPC 7 (cp-text:p25) 113.9 within 0.1; property",
    ),
    "wing_book_te_fs": _p(
        "book",
        "plans-1980:p126 TE FS 155.6, 165.8, 176 at BL 55.5, 106.25, 157",
        "high",
        "11.36 deg outer TE; 165.8 = 155.6 + 50.75 tan 11.36",
    ),
    "wing_book_te_fs_bl_23": _p(
        "book",
        "plans-1980:p126 TE FS 148.4 at BL 23",
        "medium",
        "hand 4 reads like 9; 155.6 - 32.5 tan 12.49 = 148.4 settles it",
    ),
    "wing_book_chord": _p(
        "book",
        "plans-1980:p126 chords 42.7, 31.35, 20.0",
        "high",
        "each equals TE minus LE at its station, except that the BL 106.25 LE label conflicts (wing_book_le_fs_bl_106_25_printed)",
    ),
    "wing_book_thickness_pct": _p(
        "book",
        "plans-1980:p126 thickness 16.2, 15.7, 15.0 per cent",
        "medium",
        "the 16.2 trailing glyph is smeared; the others are clear",
    ),
    "wing_book_washout_deg": _p(
        "book",
        "plans-1980:p126 twist 0.6 washin, 0.96 washout, 2.7 washout",
        "high",
        "sign: positive is washout; the reference datum of these angles is not printed; the analysis wing_washout (1.0 tip) matches none of them",
    ),
    "wing_book_te_sweep_deg": _p(
        "book",
        "plans-1980:p126 TE sweep 11.36 deg",
        "high",
        "20.4 / 101.5 gives 11.37",
    ),
    "wing_book_te_sweep_inboard_deg": _p(
        "book",
        "plans-1980:p126 inboard TE kink 12.49 deg",
        "high",
        "7.2 / 32.5 gives 12.49",
    ),
    "wing_book_chord_line_wl": _p(
        "book",
        "plans-1980:p126 chord lines at W.L. 17.40",
        "medium",
        "p128 section A-A prints 17.4 twice and p134 names the 17.4 waterline plane; the digit 4 reads like 9 on p126; model z 0 (wing_le_wl)",
    ),
    "wing_book_te_wl": _p(
        "book",
        "plans-1980:p126 TE height WL 16.95 at BL 55.5, 18.35 at BL 157",
        "high",
        "the TE rises with the thickness taper and the twist",
    ),
    "wing_book_shear_web_fwd_fs": _p(
        "book",
        "plans-1980:p126 shear web forward face FS 125.6, 130.5, 147.35, 164.2",
        "high",
        "18.42 deg line; FS 125.6 at BL 23 is the FC1 foam edge, NOT a wing LE (see wing_le_anchor and the correction ledger)",
    ),
    "wing_book_shear_web_sweep_deg": _p(
        "book",
        "plans-1980:p126 shear web sweep 18.42 deg",
        "high",
        "atan(0.3320) = 18.37, the print rounds differently by 0.05",
    ),
    "wing_book_spar_cap_width_in": _p(
        "book",
        "plans-1980:p126 spar cap 3.0; p122 3 in tape",
        "high",
        "",
    ),
    "wing_book_foam_blocks": _p(
        "book",
        "plans-1980:p118 five 7x14x64 and two 7x14x41 blocks per wing",
        "high",
        "p127 lays them out",
    ),
    "wing_book_core_angle_deg": _p(
        "book",
        "plans-1980:p118 core cut angles 78.64 centre and outboard, 77.51 inboard",
        "high",
        "90 - 11.36 and 90 - 12.49",
    ),
    "wing_book_fc1_le_length_in": _p(
        "book",
        "plans-1980:p118 FC1 LE length 32.87",
        "high",
        "sqrt(32.5^2 + 4.9^2) = 32.87 from the shear-web edge stations",
    ),
    "wing_shear_web_zones": _p(
        "cp-corrected",
        "cp-text:p26 CP26 LPC 31 outboard shear web 2 plies",
        "high",
        "p121 prints 6 plies BL 23-70, 4 plies BL 70-120 and 3 plies BL 120-157; LPC 31 corrects the 3 to 2; plans-1980:p121",
    ),
    "wing_shear_web_outboard_plies_printed": _p(
        "book",
        "plans-1980:p121 3 plies BL 120 to 157 as printed",
        "high",
        "superseded by CP26 LPC 31 (wing_shear_web_zones); kept so the correction is visible",
    ),
    "wing_cap_bottom_plies_in": _p(
        "book",
        "plans-1980:p122 bottom cap 142, 135, 84, 52, 19.5 long",
        "medium",
        "fifth digit medium (19.5 or 17.5); base schedule only: the CP25 thin-tape box adds plies when the 5-ply test reads thin (CP28 LPC 56 makes it mandatory then) and the model says so",
    ),
    "wing_cap_bottom_offsets_in": _p(
        "book",
        "plans-1980:p122 offsets 5, 12, 19, 26",
        "high",
        "the drawing is not to scale along the span; the model reads them as inboard-end offsets of plies 2 to 5",
    ),
    "wing_cap_top_plies_in": _p(
        "book",
        "plans-1980:p123 top cap 142, 142, 119, 90, 61, 39, 20 long",
        "high",
        "142 tape is about 134 / cos 18.4 = 141.3 along the web line; base schedule, the CP25 box adds plies on thin tape",
    ),
    "wing_cap_top_offsets_in": _p(
        "book",
        "plans-1980:p123 offsets 6, 12, 18, 24",
        "medium",
        "four offsets for seven plies; the model puts plies 1 and 2 flush and carries the 6 in step on to ply 7 (representational)",
    ),
    "wing_skin_plies": _p(
        "book",
        "plans-1980:p122 bottom 2 UND; p123 and p128 top 3 UND",
        "high",
        "the third top ply is forward of the hinge line only; the bottom third ply is BID at the tip",
    ),
    "wing_skin_le_lap_in": _p(
        "book",
        "plans-1980:p122 2 in LE lap onto the bottom skin",
        "high",
        "p123 adds a 4 in lap down the FC1 face",
    ),
    "wing_skin_te_lap_min_in": _p(
        "cp-corrected",
        "cp-text:p32 CP32 wing TE lap minimum 0.5",
        "high",
        "the plans print 0.6; plans-1980:p128",
    ),
    "wing_aileron_outboard_bl": _p(
        "book",
        "plans-1980:p126 aileron outboard end BL 118.1",
        "high",
        "p119 and p171 agree",
    ),
    "wing_aileron_inboard_bl": _p(
        "conflict",
        "plans-1980:p124 aileron skin cut at the BL 55.5 foam joint",
        "medium",
        "pair with wing_aileron_inboard_bl_p171 (54.3); the A10 torque tube overhangs 1 in inboard (p125); no page says which dimension p171 means",
    ),
    "wing_aileron_inboard_bl_p171": _p(
        "conflict",
        "plans-1980:p171 aileron inner end BL 54.3",
        "high",
        "pair with wing_aileron_inboard_bl (55.5); digits clear, meaning unresolved",
    ),
    "wing_aileron_skin_cut_top_in": _p(
        "book",
        "plans-1980:p124 top cut 5.9 at BL 55.5, 4.35 at BL 106.25",
        "medium",
        "the 4.35 third digit is 3 or 5 on the image; 5.9 repeats on CP34 LPC 107 (cp-text:p34); measured forward of the TE",
    ),
    "wing_aileron_skin_cut_bottom_in": _p(
        "book",
        "plans-1980:p124 bottom cut 7.6 at BL 55.5, 5.65 at BL 106.25",
        "high",
        "7.6 repeats on CP34 LPC 107; the root cut is a vertical plane (cp-text:p34)",
    ),
    "wing_aileron_rod_length_in": _p(
        "book",
        "plans-1980:p133 A13 balance rod 3/8 steel 65 long",
        "high",
        "hinge line is about 63.9 in, so 65 fits within 1.1 in; the p130 section labels the same rod A11",
    ),
    "wing_aileron_torque_tube_length_in": _p(
        "book",
        "plans-1980:p133 A10 tube 3/4 x .058, 9 in",
        "high",
        "overhangs 1 in inboard of the aileron (p125)",
    ),
    "wing_aileron_hinge_lengths_in": _p(
        "book",
        "plans-1980:p133 A3 8 in, A4 6 in twice",
        "high",
        "hinge stock MS20001-P6",
    ),
    "wing_aileron_max_up_deg": _p(
        "book",
        "plans-1980:p125 stop bolt for 20 deg up aileron; p131 20 deg of belcrank travel",
        "high",
        "",
    ),
    "wing_spar_join_bolt_spacing_in": _p(
        "conflict",
        "plans-1980:p134 drawing 28.85",
        "high",
        "pair with wing_spar_join_bolt_spacing_text_in 28.83 (text note on the same page); unresolved",
    ),
    "wing_spar_join_bolt_spacing_text_in": _p(
        "conflict",
        "plans-1980:p134 text note 28.83",
        "high",
        "pair with wing_spar_join_bolt_spacing_in 28.85",
    ),
    "wing_spar_join_bolts": _p(
        "book",
        "plans-1980:p134 2 x AN8-21A and 1 x AN8-23A per wing",
        "high",
        "p128 and p129 show the same",
    ),
    "wing_spar_join_bushings_per_wing": _p(
        "book",
        "plans-1980:p134 LWA9 bushing, 12 in all",
        "high",
        "6 per wing",
    ),
    "wing_aileron_hinge_fs": _p(
        "derived",
        "plans-1980:p126 TE and p124 top cut",
        "medium",
        "FS 149.7 at BL 55.5 and 161.45 at BL 106.25; the hinge line sits at the top skin; property",
    ),
    # --- chapter 20 (M2.7): winglets and rudders ---
    "winglet_book_root_wl": _p(
        "book",
        "plans-1980:p135 root level line WL 18.4",
        "high",
        "printed five times",
    ),
    "winglet_book_top_wl": _p(
        "book",
        "plans-1980:p135 top of skin WL 65.4",
        "high",
        "WL 66.4 with the 1 in cap; read twice",
    ),
    "winglet_book_cap_in": _p(
        "book",
        "plans-1980:p135 1 in urethane cap, p136 skinned 1 ply BID",
        "high",
        "",
    ),
    "winglet_book_bottom_wl": _p(
        "book",
        "plans-1980:p135 lower fin bottom WL 9.8",
        "high",
        "p171 prints 9.8 too",
    ),
    "winglet_book_root_le_fs": _p(
        "book",
        "plans-1980:p135 straight LE line meets WL 18.4 at FS 159.7",
        "high",
        "p135 label read twice; the LE at the wing top surface is FS 160.5 (winglet_book_root_le_fs_wing_top)",
    ),
    "winglet_book_root_le_fs_wing_top": _p(
        "book",
        "plans-1980:p136 side view FS 160.5 at the wing top",
        "high",
        "4.5 in aft of the wingtip LE FS 156",
    ),
    "winglet_book_root_te_fs": _p(
        "book",
        "plans-1980:p135 root TE FS 186.8",
        "high",
        "rudder hinge 176.8 plus 10",
    ),
    "winglet_book_top_te_fs": _p(
        "book",
        "plans-1980:p135 top TE corner FS 196.6",
        "high",
        "p171 prints 196.6 too",
    ),
    "winglet_book_tip_chord_in": _p(
        "derived-unsourced",
        "plans-1980:p135 planform at 1/5 scale, pixel read scaled by the printed 10 and 12.14 rudder widths",
        "medium",
        "about 11.4, tip LE about FS 185.2; the page prints no tip chord. Crew C read 28.9, which is wrong (the fin tapers); not used",
    ),
    "winglet_book_rudder_hinge_fs": _p(
        "book",
        "plans-1980:p135 rudder hinge FS 176.8",
        "high",
        "",
    ),
    "winglet_book_rudder_widths_in": _p(
        "book",
        "plans-1980:p135 and p138 rudder 10 at WL 18.4, 12.14 at the top, 11.5 at the bottom",
        "high",
        "186.8 - 176.8 = 10",
    ),
    "winglet_book_rudder_height_in": _p(
        "book",
        "plans-1980:p135 rudder 14.5 tall, 10.5 above WL 18.4 and 4 below",
        "high",
        "",
    ),
    "winglet_book_rudder_max_deg": _p(
        "book",
        "plans-1980:p139 rudder travel 30 deg maximum",
        "high",
        "the brake master cylinder is the stop; the swage keeps at least 0.7 in travel",
    ),
    "winglet_book_hinge_length_in": _p(
        "book",
        "plans-1980:p138 piano hinge 7.5 in from WL 18.4 up",
        "high",
        "the p135 hatched strip agrees",
    ),
    "winglet_book_core_angle_deg": _p(
        "book",
        "plans-1980:p135 upper fin core end angles 78.64 and 101.36",
        "high",
        "same as the wing",
    ),
    "winglet_book_core_length_in": _p(
        "book",
        "plans-1980:p135 upper fin core 48 in long",
        "high",
        "cut from the wing outboard TE block",
    ),
    "winglet_book_jig_wprp": _p(
        "book",
        "plans-1980:p136 WPRP FS 149.6, BL 55.5",
        "high",
        "inboard front corner of the aileron cut-out; the p124 top hinge line gives FS 149.7 at BL 55.5 (wing_aileron_hinge_fs)",
    ),
    "winglet_book_jig_abc_in": _p(
        "book",
        "plans-1980:p136 A 102.15, B 108.35, C 118.35 (CP25 LPC 6, cp-text:p25)",
        "high",
        "handwritten on the page; the plan arithmetic closes A within 0.1, B within 0.25 and C only with a lean (winglet_cant_in)",
    ),
    "winglet_book_jig_tol_in": _p(
        "book",
        "plans-1980:p136 A and B within 0.05, C within 1",
        "high",
        "",
    ),
    "winglet_book_bid_patch_in": _p(
        "cp-corrected",
        "plans-1980:p136 third BID ply 18 in up by 14 wide; CP34 LPC 104 (cp-text:p34) upper winglet only",
        "medium",
        "the 14 label is handwritten",
    ),
    "winglet_book_und_table_in": _p(
        "book",
        "plans-1980:p138 UND plies 24/12, 22/11, 20/10, 18/9, 16/8, 14/7, 12/6",
        "high",
        "A in and B in, layups 3 and 4",
    ),
    "winglet_book_conduit_from_te_in": _p(
        "book",
        "plans-1980:p137 rudder conduit 13.2 from the winglet TE",
        "high",
        "cobelu agrees",
    ),
    "winglet_height_book_in": _p(
        "derived",
        "plans-1980:p135 WL 65.4 less WL 18.4",
        "high",
        "47.0 (48.0 with the cap); property",
    ),
    "winglet_lower_height_book_in": _p(
        "derived",
        "plans-1980:p135 WL 18.4 less WL 9.8",
        "high",
        "8.6; property",
    ),
    "winglet_root_chord_book_in": _p(
        "derived",
        "plans-1980:p135 root TE 186.8 less LE line 159.7",
        "medium",
        "27.1; the page prints no chord; property",
    ),
    "winglet_top_le_fs": _p(
        "derived-unsourced",
        "plans-1980:p135 top TE 196.6 less the 11.4 tip chord",
        "medium",
        "185.2 (LE sweep about 28 deg); inherits the tip chord's pixel read; property",
    ),
    "winglet_cant_in": _p(
        "derived-unsourced",
        "plans-1980:p136 jig C 118.35 from the WPRP",
        "low",
        "about 3.6 in inward over 47 in closes C; no cant or toe angle is printed, so it is representational; A and B close without it; property",
    ),
    # --- analysis fields with no page behind them (M2.7 rulings; values unchanged) ---
    "wing_washout": _p(
        "unsourced",
        "",
        "n/a",
        "tip washout 1.0 deg matches no page. The book twist is 0.6 washin at BL 55.5, 0.96 washout at 106.25 and 2.7 washout at the tip (wing_book_washout_deg, plans-1980:p126); not moved here because it changes the NP (Block 3)",
    ),
    "winglet_height": _p(
        "book",
        "plans-1980:p135 WL 65.4 less WL 18.4",
        "high",
        "47.0 (was 16.0, which matched no page); same value as winglet_height_book_in. The 8.6 lower fin is not in the analysis winglet. Moved in M2.8 with a ledger row",
    ),
    "winglet_root_chord": _p(
        "derived",
        "plans-1980:p135 root TE 186.8 less LE line 159.7",
        "medium",
        "27.1 (was 20.0, which matched no page); same value as winglet_root_chord_book_in. Moved in M2.8 with a ledger row",
    ),
    "winglet_tip_chord": _p(
        "derived-unsourced",
        "plans-1980:p135 1/5 drawing scaled by the printed rudder widths",
        "low",
        "11.4 (was 12.0, which matched no page); same value as winglet_book_tip_chord_in. A scaled drawing read, not a source. Moved in M2.8 with a ledger row",
    ),
    # --- chapters 21 to 23 (M2.8): strakes and fuel, electrical, engine ---
    "stk_book_le_fs_fuselage": _p(
        "book",
        "plans-1980:p147",
        "high",
        "strake LE at the fuselage side, F.S. 50 (p171 agrees); the LE is a polyline, not a line: 73.3 at BL 23, 99.5 at BL 45, the wing LE at BL 58",
    ),
    "stk_book_le_fs_bl_23": _p(
        "book",
        "plans-1980:p147",
        "high",
        "TLE and BLE kink at BL 23, F.S. 73.3 (p171 agrees)",
    ),
    "stk_book_le_fs_bl_45": _p(
        "book",
        "plans-1980:p147",
        "high",
        "LE at BL 45 where R45 meets the TLE, F.S. 99.5; StrakeConfig.fs_trailing_edge 99.5 is this number, not a strake trailing edge",
    ),
    "stk_book_spar_fwd_fs_bl_23": _p(
        "book",
        "plans-1980:p147",
        "high",
        "spar forward face at BL 23, F.S. 118.5; this, not 99.5, is the strake aft boundary",
    ),
    "stk_book_spar_slope_deg": _p(
        "derived",
        "plans-1980:p118",
        "medium",
        "spar face sweeps aft 8.57 deg per BL out (4.9 over 32.5 on p118); p142 prints 4.9 over 32.0 = 8.71, the 0.14 deg gap is print tolerance",
    ),
    "stk_book_bab_fuselage_fs": _p(
        "book",
        "plans-1980:p147",
        "high",
        "BAB meets the fuselage side at F.S. 103.5 (the aft edge of the baggage cutout)",
    ),
    "stk_book_sump_fs": _p(
        "derived",
        "plans-1980:p144",
        "medium",
        "sump blister runs F.S. 103.5 to 125, flush with the firewall (p144 note, p171 FS 125); the 21 in blister from 103.5 reaches 124.5, within 0.5",
    ),
    "stk_book_fuselage_side_bl": _p(
        "derived-unsourced",
        "plans-1980:p147",
        "low",
        "fuselage side BL at F.S. 50 and at F.S. 103.5, scaled off the p147 image (plus or minus 0.7 in); not dimensioned on the page, so representational; the baggage and tank outlines depend on it",
    ),
    "stk_book_foam_thickness_in": _p(
        "book",
        "plans-1980:p141",
        "high",
        "type 45 PV core, 0.35 in thick, for every strake part and skin",
    ),
    "stk_book_tle_in": _p(
        "book",
        "plans-1980:p141",
        "high",
        "TLE fuel tank leading edge, 33.5 long by 2.55 wide, 90 deg corners",
    ),
    "stk_book_ble_in": _p(
        "book",
        "plans-1980:p141",
        "high",
        "BLE baggage leading edge, 25.5 long by 2.55 wide",
    ),
    "stk_book_b23_in": _p(
        "book",
        "plans-1980:p141",
        "high",
        "B23 baffle, 21.3 long by 7.3 high; p147 derives 21.2 (spar face 118.5 less the DB junction)",
    ),
    "stk_book_bab_in": _p(
        "book",
        "plans-1980:p141",
        "medium",
        "BAB baffle, 13.4 long, 7.3 high outboard and 7.75 high inboard (the 7.75 is medium); p147 derives 13.2",
    ),
    "stk_book_db_in": _p(
        "book",
        "plans-1980:p141",
        "medium",
        "DB diagonal baffle, 28.5 long, 7.3 high at the fore end and 6.5 at the aft end (the 6.5 is medium); p147 derives 28.3",
    ),
    "stk_book_b23_hole_in": _p(
        "book",
        "plans-1980:p141",
        "medium",
        "B23 oval hole 5 long by 3 high, 3 in from the right end and 3 in clear of the bottom edge (hand digits)",
    ),
    "stk_book_notch_radius_in": _p(
        "book",
        "plans-1980:p141",
        "medium",
        "B23 and DB corner notch radii, 0.8 on top and 1.3 on the bottom, centres 2 in from each end (small print)",
    ),
    "stk_book_skin_top_in": _p(
        "book",
        "plans-1980:p142",
        "high",
        "top skin foam edges A, B, C and D (outboard skin A, B and C; inboard skin D along the fuselage)",
    ),
    "stk_book_skin_bottom_in": _p(
        "book",
        "plans-1980:p142",
        "high",
        "bottom skin foam edges A, B, C and D; the 0.2 difference from the top is the 1 in bevel offset",
    ),
    "stk_book_skin_spar_edge_in": _p(
        "book",
        "plans-1980:p142",
        "high",
        "outboard skin spar edge 32.0 long along the bevel, offset aft 4.9, square at the aft corner",
    ),
    "stk_book_cutout_fwd_in": _p(
        "book",
        "plans-1980:p142",
        "medium",
        "baggage cutout in the fuselage side: station forward of the spar face, top-edge depth and bottom-edge depth below WL 23 (top of the longeron); the 4.0 and 1.40 reads are medium",
    ),
    "stk_book_cutout_aft_in": _p(
        "book",
        "plans-1980:p142",
        "medium",
        "tank cutout in the fuselage side: round forward end begins 30.0 forward of the spar face, aft edge 15.0, top depth 1.40, bottom depth 9.15 below WL 23",
    ),
    "stk_book_cutout_aft_top_alt_in": _p(
        "conflict",
        "plans-1980:p142",
        "low",
        "the tank cutout top depth reads 1.90 near the aft end and 1.40 at mid length in the same drawing; whether 1.90 is a sight-gauge notch or a misprint is not settled, both are carried",
    ),
    "stk_book_jig_rib_height_in": _p(
        "book",
        "plans-1980:p143",
        "high",
        "the WL 17.4 mark on R45 is 2.65 above the jig table and on R23 3.45 above (the strake bottom follows the spar bottom, about 2.1 deg)",
    ),
    "stk_book_sump_blister_in": _p(
        "book",
        "plans-1980:p144",
        "high",
        "sump blister 21 long, 2.75 deep, 0.5 flange all round; the 5 in dimension and the exact outline are not unambiguous (prefab SB is 3 ply BID)",
    ),
    "stk_book_baggage_limit_lb": _p(
        "book",
        "om-1980:p4",
        "high",
        "each strake baggage floor is structurally good for 100 lb (OM weights page)",
    ),
    "fuel_book_lb_per_gal": _p(
        "book",
        "om-1980:p25",
        "high",
        "6.0 lb per gal (40 gal = 240 lb, om-1980:p26); the analysis fuel_density_lb_per_gal 6.01 is the avgas figure and is not moved",
    ),
    "fuel_book_arm_fs": _p(
        "book",
        "om-1980:p26",
        "high",
        "fuel arm F.S. 104.5 (rows 240 lb moment 25080 and 150 lb moment 15675 both close); the derived plan centroid of the tank is 103.85",
    ),
    "fuel_book_capacity_plans_gal": _p(
        "conflict",
        "plans-1980:p141",
        "high",
        "plans: two tanks of 25.5 gal each (51 total); the OM prints 28 each and 52 total, so the sources disagree; the model keeps 26 per side (StrakeConfig.tank_volume_gal) and carries both",
    ),
    "fuel_book_capacity_om_gal": _p(
        "conflict",
        "om-1980:p8",
        "high",
        "OM: two 28 gal tanks (56) but also a 52 gal total (also cp-text CP24 p13); 52 total is 26 per side, which fits neither 25.5 nor 28",
    ),
    "fuel_book_capacity_om_total_gal": _p(
        "book",
        "om-1980:p8",
        "high",
        "OM: 52 gal total capacity (cp-text CP24 p13 spec table agrees)",
    ),
    "elec_book_battery_v": _p(
        "book",
        "plans-1980:p150",
        "high",
        "12 V system; the battery is a Gill PSG-9, 25 Ah (p150 and p151, om-1980:p10 agrees on 12 V 25 Ah)",
    ),
    "elec_book_battery_ah": _p(
        "book",
        "plans-1980:p150",
        "high",
        "25 Ah in the nose in both systems 'to provide the correct CG' (p149)",
    ),
    "elec_book_battery_fs_range": _p(
        "positioned-from-text",
        "plans-1980:p155",
        "low",
        "the battery sits on a nose shelf bonded to NG30 and F6 (p155); its station is on A6 only, not held, so only the nose box range F.S. 0 (NG31, about) to 22 (F22, derived in M2.4) is known; representational",
    ),
    "elec_book_battery_model_fs": _p(
        "unsourced",
        "",
        "low",
        "the model draws the battery at the middle of the F.S. 0 to 22 range for illustration only; no source gives a station",
    ),
    "elec_book_battery_added_lb": _p(
        "derived",
        "cp-text:p27",
        "medium",
        "the 25 Ah nose battery 'accepts a 19 lb increase' over the small battery (CP27 p4): a printed delta, not an absolute battery weight",
    ),
    "elec_book_shelf_in": _p(
        "book",
        "plans-1980:p155",
        "medium",
        "battery shelf 0.6 above the floor mark and cover wrap gap 0.4 (small hand digits)",
    ),
    "elec_book_starter_fs_min": _p(
        "positioned-from-text",
        "cp-text:p27",
        "low",
        "starter, ring gear and alternator 'way back at station 150+' (CP27 p4): a lower bound, not an arm",
    ),
    "elec_book_relay_fs": _p(
        "positioned-from-text",
        "plans-1980:p149",
        "low",
        "mount the start relay and over-voltage unit on the front of F22 (p149); F22 is F.S. 22 (fs_f22, derived)",
    ),
    "elec_book_nav_strip_in": _p(
        "cp-corrected",
        "cp-text:p30",
        "high",
        "nav antenna copper strips are 22.8 in, not 24 (CP30 LPC 78); two strips under the canard",
    ),
    "elec_book_comm_strip_in": _p(
        "cp-corrected",
        "cp-text:p26",
        "high",
        "comm antenna in the winglet: two foil strips 20.3 in, three balums (CP26 p8)",
    ),
    "eng_book_engine_max_lb": _p(
        "book",
        "plans-1980:p156",
        "high",
        "engine with accessories at most 246 lb (a limit, not a weight); O-200 or O-235 only",
    ),
    "eng_book_vibrating_max_lb": _p(
        "book",
        "plans-1980:p156",
        "high",
        "vibrating mass (engine, accessories, exhaust, prop, extensions, oil) at most 286 lb; 286 less 246 leaves a 40 lb allowance (derived)",
    ),
    "eng_book_oil_lb": _p(
        "book",
        "om-1980:p25",
        "high",
        "oil 8 lb",
    ),
    "eng_book_oil_fs": _p(
        "book",
        "om-1980:p25",
        "high",
        "oil station F.S. 140.0 (moment 1120); the only printed engine-side arm",
    ),
    "eng_book_down_thrust_deg": _p(
        "cp-corrected",
        "cp-text:p32",
        "high",
        "2 deg down thrust, plus or minus 1, prop flange higher than the magneto end (CP32 p5; CP38 p5 agrees); crank axis on BL 0 in plan",
    ),
    "eng_book_crank_bl": _p(
        "cp-corrected",
        "cp-text:p32",
        "high",
        "crankshaft on BL 0 in plan (CP32 p5)",
    ),
    "eng_book_block_in": _p(
        "unsourced",
        "",
        "low",
        "O-235-sized block, length (along the crank), width and height; no engine dimension is printed in any held source (Sections IIA, IIC and IIL are not held); striped representational in the lab",
    ),
    "eng_book_block_fwd_fs": _p(
        "unsourced",
        "",
        "low",
        "front of the engine block, aft of the firewall (F.S. 125) and the mount; with the block length it puts oil (140) inside and the starter end (150+) at the aft face; no source gives it",
    ),
    "eng_book_block_wl": _p(
        "unsourced",
        "",
        "low",
        "WL of the block centre; the book prints no prop or crank height (the fuselage top is about WL 32.8 at the firewall, p171, medium)",
    ),
    "eng_book_prop_dia_in": _p(
        "conflict",
        "plans-1980:p171",
        "medium",
        "back cover 'max dia 60' (the inch mark is smudged); om-1980:p5 prints a 58 in disc and cp-text CP42 p5 lists 62 in props; all three are carried, the config uses 60",
    ),
    "eng_book_cowl_trim_in": _p(
        "book",
        "plans-1980:p157",
        "high",
        "trim about 9 in off each outboard end of the VariEze cowl",
    ),
    "eng_book_cowl_reinf_in": _p(
        "book",
        "plans-1980:p157",
        "high",
        "4 plies BID at 45 deg, 2 in wide, in 4 places just inboard of the 9 in trim line (the band position, 9 to 11 in, is medium)",
    ),
    "eng_book_cowl_aft_shift_in": _p(
        "cp-corrected",
        "cp-text:p27",
        "high",
        "the Lycoming cowl moves aft 0.7 in against the VariEze and the engine moves aft with the dynafocal mount (CP27 p5)",
    ),
    "eng_book_rib_in": _p(
        "book",
        "plans-1980:p158",
        "high",
        "wing-root metal rib: 6061-0 sheet 0.020 thick (p157 text prints 0.20, a typo), 20 by 24 sheet, two 1.2 flanges, 0.5 edge offset; the outline is a hand drawing with no coordinates",
    ),
    "eng_book_bracket_plate_in": _p(
        "book",
        "plans-1980:p156",
        "high",
        "throttle and mixture bracket plate seen from below, 6.5 long by 2.5 wide, 0.063 2024-T3 (figure 23-1)",
    ),
    "eng_book_bracket_holes_in": _p(
        "book",
        "plans-1980:p156",
        "medium",
        "oil-drain hole dia 2.0 centred 3.6 from the carb hole centre, carb hole dia 1.8 (hand '1-8', could be 1.6) centred 1.25 from the forward end",
    ),
    "eng_book_bracket_angle_in": _p(
        "book",
        "plans-1980:p156",
        "medium",
        "upright 2 by 2 formed angle, 0.063, eight rivets (the rivet prefix is smudged)",
    ),
    "stk_book_spar_fwd_fs_bl_45": _p(
        "derived",
        "plans-1980:p147",
        "medium",
        "118.5 + 22 tan 8.57 = 121.8; property (the OD and R45 end here; the slope is a two-page average)",
    ),
    "stk_book_junction_fs": _p(
        "derived",
        "plans-1980:p147",
        "medium",
        "118.5 less the printed B23 length 21.3 = 97.2; p147 scaling gives 97.3 (B23 21.2); property",
    ),
    "stk_book_db_far_fs": _p(
        "derived",
        "plans-1980:p141",
        "medium",
        "97.2 + sqrt(28.5^2 - 22^2) = 115.3; p147 shows about 115 at the R45 and spar corner; the printed 28.5 and the derived 28.3 differ by 0.2; property",
    ),
    "eng_book_vibrating_allowance_lb": _p(
        "derived",
        "plans-1980:p156",
        "high",
        "286 - 246 = 40 lb for prop, exhaust, extensions and oil; derived, not printed; property",
    ),
    "datum_offset_in": _p(
        "book",
        "om-1980:p25 datum F.S. 0.0",
        "high",
        "published frame by definition (offset 0); was 45.5, fitted to NP; retired",
    ),
}


# Provenance flags for the analysis weight, arm and engine fields that are not geometry (M2.8; values unchanged).
# Same shape and statuses as GEOMETRY_PROVENANCE; tests/test_m28_weight_flags.py reads it. Fixing the values is
# ledger closure (milestone 2.n), not M2.8.
WEIGHT_PROVENANCE: dict[str, dict] = {
    "wing_weight_lb": _p(
        "conflict",
        "cp-text:p26 64 lb per wing with winglets and rudder",
        "low",
        "85.0 lb for both wings is unsourced. CP26 p3 gives 64 lb per wing complete with winglets and rudder (60 lb painted without rudder and aileron, CP26 p16), so 2 x 64 = 128 lb, but that is one builder's airplane (N26MS). Both values are kept; ledger closure decides",
    ),
    "engine_cg_arm_in": _p(
        "conflict",
        "plans-1980:p171 firewall FS 125; om-1980:p25 oil FS 140",
        "high",
        "8.0 in, commented 'forward of firewall', contradicts every held source: the engine is aft of the firewall (FS 125), oil is at FS 140 (om-1980:p25) and the starter and alternator are at station 150+ (cp-text:p27). No engine arm is printed in any held source. The value is unchanged; ledger closure replaces it",
    ),
    "engine_mass_kg": _p(
        "conflict",
        "plans-1980:p156 engine with accessories at most 246 lb",
        "medium",
        "113 kg is 249.1 lb (commented '250 lb dry'), over the 246 lb book limit and 6 lb over engine_dry_weight_lb 243. The two fields disagree; the value is unchanged and ledger closure picks one",
    ),
    "engine_dry_weight_lb": _p(
        "unsourced",
        "plans-1980:p156 limit 246 lb is a limit, not a weight",
        "low",
        "243 lb matches no page. The book prints only the limits: engine with accessories at most 246 lb and vibrating mass at most 286 lb (plans-1980:p156). Disagrees with engine_mass_kg (249.1 lb)",
    ),
    "electrical_weight_lb": _p(
        "conflict",
        "cp-text:p27 CP27 page 4",
        "medium",
        "25 lb as one row at FS 119.5 is the wrong shape. The 25 Ah battery sits in the nose (plans-1980:p149, p155; about +19 lb over the small battery) and the starter, ring gear and alternator are at station 150+ (cp-text:p27); the plans print 'electric start adds over 25 lb' (plans-1980:p149). Unsourced as a row; the ledger closure splits it",
    ),
    "tank_volume_gal": _p(
        "conflict",
        "plans-1980:p141 25.5 gal per tank; om-1980:p8 28 gal per tank and 52 total",
        "high",
        "26 gal per side is half the OM 52 gal total and matches neither the plans (25.5) nor the OM per-tank figure (28). Both source values are in fuel_book_capacity_plans_gal and fuel_book_capacity_om_gal; the model keeps 26 and says so (M2.8)",
    ),
    "electrical_arm_in": _p(
        "conflict",
        "cp-text:p27 CP27 page 4",
        "medium",
        "119.5 in is converted-unsourced and sits where neither the battery (nose, about FS 0 to 22, A6 only) nor the starter and alternator (FS 150+) are. Unchanged; ledger closure replaces it",
    ),
}


@dataclass
class MaterialParams:
    """Composite layup and foam specifications."""

    # === FIBERGLASS PLY THICKNESSES (inches) ===
    bid_ply_thickness: float = 0.013  # Bi-directional cloth (per ply)
    uni_ply_thickness: float = 0.009  # Unidirectional tape (per ply)

    # === SPAR CAP LAYUP (Long-EZ specific) ===
    spar_cap_plies: int = 17  # UNI plies for main spar cap
    spar_cap_width: float = 3.0  # Spar cap width (inches)
    spar_modulus_psi: float = 2.8e6  # Typical UNI glass modulus in bending

    # === D-BOX SECTION (LE to spar) ===
    dbox_chord_fraction: float = 0.25  # D-box extends from LE to this fraction of chord
    dbox_skin_plies: int = 2  # BID plies per skin (upper + lower)
    dbox_web_foam_thickness_in: float = 0.25  # Shear web foam core thickness
    dbox_web_bid_plies: int = 1  # BID plies per face of web sandwich
    spar_cap_ply_schedule: List[int] = field(
        default_factory=lambda: [17, 17, 14, 11, 8]
    )
    # 5-station schedule: root to tip (root-root, 25%, 50%, 75%, tip)

    # === FOAM CORE ===
    wing_core_foam: FoamType = FoamType.STYROFOAM_BLUE
    fuselage_foam: FoamType = FoamType.URETHANE_2LB
    foam_core_thickness: float = 0.5  # PVC foam shell thickness

    # === LAMINATE SCHEDULES ===
    laminates: Dict[str, LaminateDefinition] = field(
        default_factory=lambda: {
            "wing_skin": LaminateDefinition(
                name="wing_skin",
                plies=[
                    Ply(material="bid", orientation=45.0),
                    Ply(material="bid", orientation=-45.0),
                    Ply(material="uni", orientation=0.0),
                    Ply(material="bid", orientation=45.0),
                ],
                notes="Baseline Long-EZ wing skin schedule",
            ),
            "canard_skin": LaminateDefinition(
                name="canard_skin",
                plies=[
                    Ply(material="bid", orientation=30.0),
                    Ply(material="bid", orientation=-30.0),
                    Ply(material="bid", orientation=45.0),
                ],
                notes="Roncz canard surface layup",
            ),
        }
    )

    @property
    def spar_trough_depth(self) -> float:
        """Spar cap trough depth = plies × thickness."""
        return self.spar_cap_plies * self.uni_ply_thickness

    @property
    def ply_thickness_lookup(self) -> Dict[str, float]:
        """Map laminate material names to nominal ply thickness."""
        return {
            "bid": self.bid_ply_thickness,
            "uni": self.uni_ply_thickness,
        }


@dataclass
class ManufacturingIntent:
    """Describes a manufacturing artifact and its expected fidelity."""

    artifact: str
    format: str
    tolerance: float
    description: str = ""


@dataclass
class ComponentManufacturingIntent:
    """Per-component manufacturing outputs for CAM and templates."""

    printable_jigs: ManufacturingIntent
    cnc_foam: ManufacturingIntent
    sheet_templates: ManufacturingIntent


@dataclass
class ManufacturingParams:
    """CNC and hot-wire cutting parameters."""

    # === HOT-WIRE CUTTING ===
    wire_diameter: float = 0.032  # NiChrome wire diameter (inches)
    wire_temp_styrofoam: float = 400  # Cutting temp for Styrofoam (°F)
    wire_temp_urethane: float = 500  # Cutting temp for urethane (°F)
    feed_rate_default: float = 4.0  # Default feed rate (in/min)

    # === KERF COMPENSATION ===
    kerf_styrofoam: float = 0.045  # Material removed (inches)
    kerf_urethane: float = 0.035  # Material removed (inches)

    # === NESTING / SHEET STOCK ===
    stock_sheets: List[Tuple[float, float]] = field(
        default_factory=lambda: [
            (24.0, 48.0),  # Typical foam block face
            (48.0, 96.0),  # Full plywood sheet
        ]
    )
    default_dogbone_radius: float = 0.0625
    default_fillet_radius: float = 0.125
    engraving_depth: float = 0.02

    # === FABRICATION INTENT ===
    component_intents: Dict[str, ComponentManufacturingIntent] = field(
        default_factory=lambda: {
            "wing": ComponentManufacturingIntent(
                printable_jigs=ManufacturingIntent(
                    artifact="wing_alignment_jig",
                    format="STL",
                    tolerance=0.01,
                    description="3D printed tip/rib fixtures to hold foam cores",
                ),
                cnc_foam=ManufacturingIntent(
                    artifact="wing_foam_core",
                    format="GCODE",
                    tolerance=0.02,
                    description="4-axis hot-wire toolpath with kerf offsets",
                ),
                sheet_templates=ManufacturingIntent(
                    artifact="wing_root_tip_templates",
                    format="DXF",
                    tolerance=0.01,
                    description="Laser or waterjet templates for foam blanks",
                ),
            ),
            "canard": ComponentManufacturingIntent(
                printable_jigs=ManufacturingIntent(
                    artifact="canard_alignment_jig",
                    format="STL",
                    tolerance=0.01,
                    description="Roncz canard washout and alignment fixtures",
                ),
                cnc_foam=ManufacturingIntent(
                    artifact="canard_foam_core",
                    format="GCODE",
                    tolerance=0.02,
                    description="Hot-wire toolpath honoring Roncz airfoil",
                ),
                sheet_templates=ManufacturingIntent(
                    artifact="canard_root_tip_templates",
                    format="DXF",
                    tolerance=0.01,
                    description="Templates for canard foam blocks",
                ),
            ),
            "bulkhead": ComponentManufacturingIntent(
                printable_jigs=ManufacturingIntent(
                    artifact="bulkhead_jig",
                    format="STL",
                    tolerance=0.01,
                    description="Bonding jigs to hold bulkheads square",
                ),
                cnc_foam=ManufacturingIntent(
                    artifact="bulkhead_blank",
                    format="DXF",
                    tolerance=0.02,
                    description="Router-ready outlines for foam or plywood blanks",
                ),
                sheet_templates=ManufacturingIntent(
                    artifact="bulkhead_templates",
                    format="DXF",
                    tolerance=0.01,
                    description="Full-size bulkhead profiles for tracing",
                ),
            ),
            "fuselage": ComponentManufacturingIntent(
                printable_jigs=ManufacturingIntent(
                    artifact="fuselage_assembly_jig",
                    format="STL",
                    tolerance=0.02,
                    description="3D printed pads/locators for longerons and bulkheads",
                ),
                cnc_foam=ManufacturingIntent(
                    artifact="fuselage_shell",
                    format="DXF",
                    tolerance=0.03,
                    description="Panel nest files for CNC-routed side and bottom panels",
                ),
                sheet_templates=ManufacturingIntent(
                    artifact="fuselage_panel_templates",
                    format="DXF",
                    tolerance=0.02,
                    description="Printable side/bottom templates for manual cutting",
                ),
            ),
        }
    )

    @property
    def kerf_compensation(self) -> Dict[FoamType, float]:
        """Kerf offset by foam type."""
        return {
            FoamType.STYROFOAM_BLUE: self.kerf_styrofoam,
            FoamType.URETHANE_2LB: self.kerf_urethane,
            FoamType.DIVINYCELL_H45: 0.030,
        }

    # === SKIN DEDUCTION ===
    skin_thickness_deduction: bool = True  # Offset foam core for skin thickness
    wire_tension_lbf: float = 5.0  # Hot-wire tension for bow correction
    wire_bow_correction: bool = True  # Enable geometric wire bow compensation

    # === FUSELAGE BUILD SETTINGS ===
    fuselage_build_method: BuildMethod = BuildMethod.BOW_FOAM
    max_cnc_block_length: float = 48.0  # Max CNC machine width (inches)
    auto_segment_wings: bool = True  # Auto-segment wings for CNC

    # === STRONGBACK / JIG SETTINGS ===
    strongback_table_width: float = 36.0  # Work table width (inches)
    strongback_table_length: float = 240.0  # Work table length (inches)


@dataclass
class StrakeConfig:
    """Strake geometry for wing-fuselage integration."""

    # === GEOMETRY ===
    fs_leading_edge: float = 50.0  # book: plans-1980:p147 strake LE at fuselage side F.S. 50 (p171 agrees; LE is swept: 73.3 at BL 23, 99.5 at BL 45)
    fs_trailing_edge: float = 99.5  # converted-unsourced (internal 145.0 shifted); NOT a strake TE: 99.5 is the book LE at BL 45 (stk_book_le_fs_bl_45); the book aft boundary is the spar face, F.S. 118.5 at BL 23 (stk_book_spar_fwd_fs_bl_23)
    inboard_width: float = 8.0  # At fuselage junction (inches)
    outboard_taper: float = 0.6  # Width reduction ratio at BL 23.3

    # === TANKAGE ===
    tank_volume_gal: float = 26.0  # Per side (fuel mode); conflict: plans 25.5, OM 28 (fuel_book_capacity_*), 52 total kept as 26 per side
    baffle_spacing: float = 6.0  # Anti-slosh baffle spacing (inches)

    # === E-Z BATTERY CONVERSION ===
    battery_cell_pitch: float = 2.625  # LiFePO4 prismatic spacing (inches)
    battery_module_count: int = 8  # Modules per strake (16 total)
    battery_cell_capacity_ah: float = 100.0  # Cell capacity
    battery_cells_series: int = 16  # 16S = 48V nominal
    battery_cells_parallel: int = 4  # 4P for capacity


@dataclass
class PropulsionConfig:
    """Powerplant configuration for CG and firewall generation."""

    propulsion_type: PropulsionType = PropulsionType.LYCOMING_O235

    # === IC ENGINE DEFAULTS (O-235) ===
    engine_mass_kg: float = 113.0  # 250 lb dry
    engine_cg_arm_in: float = 8.0  # Forward of firewall
    fuel_capacity_gal: float = 52.0  # Total fuel (26 gal per strake)
    fuel_consumption_gph: float = 6.5  # Cruise consumption

    # === IC ENGINE SPECS (Lycoming O-235-L2C) ===
    engine_dry_weight_lb: float = 243.0  # Dry weight with accessories
    engine_displacement_ci: float = 235.0
    engine_rated_hp: float = 115.0
    engine_rated_rpm: int = 2700
    engine_prop_diameter_in: float = 60.0

    # === ELECTRIC DEFAULTS (LiFePO4) ===
    motor_mass_kg: float = 35.0  # EMRAX 228 MV
    motor_power_kw: float = 100.0  # 134 hp continuous
    battery_capacity_kwh: float = 25.6  # 16S4P configuration
    battery_voltage_v: float = 51.2  # 16S nominal

    @property
    def is_electric(self) -> bool:
        """Check if propulsion is electric."""
        return self.propulsion_type in (
            PropulsionType.ELECTRIC_LIFEPO4,
            PropulsionType.ELECTRIC_NMC,
        )

    @property
    def battery_energy_density_wh_kg(self) -> float:
        """Energy density based on battery chemistry."""
        if self.propulsion_type == PropulsionType.ELECTRIC_LIFEPO4:
            return 150.0  # LiFePO4
        elif self.propulsion_type == PropulsionType.ELECTRIC_NMC:
            return 250.0  # NMC
        return 0.0

    @property
    def battery_mass_kg(self) -> float:
        """Computed battery mass from capacity and density."""
        if not self.is_electric:
            return 0.0
        return (self.battery_capacity_kwh * 1000) / self.battery_energy_density_wh_kg


@dataclass
class AirfoilSelection:
    """Airfoil assignments for each lifting surface."""

    # SAFETY: Roncz is NON-NEGOTIABLE for the canard
    canard: AirfoilType = AirfoilType.RONCZ_R1145MS

    # Main wing uses modified Eppler with trailing-edge reflex
    wing_root: AirfoilType = AirfoilType.EPPLER_1230_MOD
    wing_tip: AirfoilType = AirfoilType.EPPLER_1230_MOD

    # Reflex percentage for pitch stability
    wing_reflex_percent: float = 2.5


@dataclass
class FlightConditionParams:
    """Design flight conditions for aerodynamic analysis."""

    design_altitude_ft: float = 8000.0  # Primary design altitude
    v_ne_ktas: float = 200.0  # Never-exceed speed (KTAS)
    approach_speed_ktas: float = 60.0  # Estimated approach speed for stall check
    gross_weight_lb: float = 1325.0  # om-1980:p4 normal max takeoff gross; 1425 is the takeoff-only band (data/mass_ledger.yaml envelope, om-1980:p28)

    # === PILOT / PAYLOAD RANGES (for CG envelope) ===
    pilot_weight_min_lb: float = 150.0
    pilot_weight_max_lb: float = 250.0
    fuel_reserve_gal: float = 5.0  # Minimum fuel reserve


@dataclass
class StructuralWeightParams:
    """Measured structural component weights (from builder records)."""

    wing_weight_lb: float = 85.0
    wing_arm_in: float = (
        94.5  # unsourced (internal 140.0 shifted by -45.5); Block 2 replaces
    )
    canard_weight_lb: float = 25.0
    canard_arm_in: float = field(
        default_factory=lambda: GeometricParams().fs_canard_le
        + 0.25 * GeometricParams().canard_chord
    )  # canard structural weight at the canard (quarter chord), Block 1
    fuselage_weight_lb: float = 120.0
    fuselage_arm_in: float = (
        54.5  # unsourced (internal 100.0 shifted by -45.5); Block 2 replaces
    )
    # landing gear: no free constants; decomposed rows in data/mass_ledger.yaml `gear:` (core.ledger.gear_rows)
    electrical_weight_lb: float = 25.0
    electrical_arm_in: float = (
        119.5  # unsourced (internal 165.0 shifted by -45.5); Block 2 replaces
    )
    instruments_weight_lb: float = 15.0
    instruments_arm_in: float = (
        29.5  # unsourced (internal 75.0 shifted by -45.5); Block 2 replaces
    )
    interior_weight_lb: float = 20.0
    interior_arm_in: float = (
        49.5  # unsourced (internal 95.0 shifted by -45.5); Block 2 replaces
    )
    fuel_density_lb_per_gal: float = 6.01  # 100LL avgas
    fuel_arm_in: float = 104.5  # book: om-1980:p26 fuel station 104.5


@dataclass
class AeroLimitsParams:
    """Aerodynamic limits for stall and stability analysis."""

    # === CANARD STALL PRIORITY (safety critical) ===
    canard_clmax: float = 1.35  # Roncz R1145MS (wind tunnel data)
    wing_clmax: float = 1.45  # Eppler 1230 Modified
    canard_alpha_0L: float = -3.0  # Zero-lift AoA (degrees)
    wing_alpha_0L: float = -2.0  # Zero-lift AoA (degrees)
    min_stall_margin_deg: float = 2.0  # Minimum canard-first stall margin
    clmax_reference_re: float = 3.0e6  # Re at which CLmax values were measured


@dataclass
class FlutterParams:
    """Parameters for torsional stiffness and flutter analysis."""

    # === TORSION (D-box section) ===
    shear_modulus_psi: float = 1.0e6  # G for glass/epoxy BID
    skin_thickness_in: float = 0.048  # Effective skin thickness for D-box

    # === FLUTTER (14 CFR 23.629) ===
    flutter_safety_factor: float = 1.2  # V_flutter must exceed V_ne * this

    # === CONTROL SURFACE MASS BALANCE ===
    elevon_mass_balance_pct: float = 100.0  # 100% = CG on hinge line (minimum safe)
    aileron_mass_balance_pct: float = 100.0


@dataclass
class ComplianceParams:
    """FAA 14 CFR 21.191(g) compliance tracking."""

    strict_compliance: bool = False  # Block G-code export if < 51%

    # Task credit weights (percentage of 51% rule)
    task_credits: Dict[str, float] = field(
        default_factory=lambda: {
            "wing_cores_cnc": 0.08,  # Builder-operated CNC foam cutting
            "wing_skins_layup": 0.12,  # Manual fiberglass layup
            "fuselage_assembly": 0.15,  # Bulkhead installation & bonding
            "canard_fabrication": 0.10,  # Canard core + skins
            "control_system": 0.08,  # Linkages, cables, torque tubes
            "landing_gear": 0.06,  # Main gear bow, nose gear
            "engine_install": 0.05,  # Engine mount, baffles, cowl
            "electrical": 0.04,  # Wiring harness
            "finishing": 0.06,  # Fill, sand, paint
            "final_assembly": 0.10,  # Systems integration
        }
    )

    @property
    def total_builder_credit(self) -> float:
        """Sum of all builder credits - must exceed 0.50."""
        return sum(self.task_credits.values())


@dataclass
class AircraftConfig:
    """
    Master configuration singleton.

    ALL downstream modules import this. Changes here propagate through:
    - CadQuery geometry scripts
    - OpenVSP aerodynamic models
    - G-code manufacturing output
    - Markdown documentation injection
    """

    geometry: GeometricParams = field(default_factory=GeometricParams)
    materials: MaterialParams = field(default_factory=MaterialParams)
    manufacturing: ManufacturingParams = field(default_factory=ManufacturingParams)
    airfoils: AirfoilSelection = field(default_factory=AirfoilSelection)
    compliance: ComplianceParams = field(default_factory=ComplianceParams)
    strakes: StrakeConfig = field(default_factory=StrakeConfig)
    propulsion: PropulsionConfig = field(default_factory=PropulsionConfig)
    flight_condition: FlightConditionParams = field(
        default_factory=FlightConditionParams
    )
    structural_weights: StructuralWeightParams = field(
        default_factory=StructuralWeightParams
    )
    aero_limits: AeroLimitsParams = field(default_factory=AeroLimitsParams)
    flutter: FlutterParams = field(default_factory=FlutterParams)

    # Project metadata
    project_name: str = "Open-EZ PDE"
    version: str = "0.1.0"
    baseline: str = "Long-EZ Model 61"

    def validate(self) -> List[str]:
        """Validate configuration for safety and regulatory compliance."""
        errors = []

        # SAFETY CHECK: Roncz canard is mandatory
        if self.airfoils.canard != AirfoilType.RONCZ_R1145MS:
            errors.append(
                "SAFETY VIOLATION: Canard must use RONCZ_R1145MS. "
                "GU25-5(11)8 causes dangerous lift loss in rain."
            )

        # COMPLIANCE CHECK: Builder credits must exceed 51%
        if self.compliance.total_builder_credit < 0.51:
            errors.append(
                f"COMPLIANCE VIOLATION: Builder credits ({self.compliance.total_builder_credit:.1%}) "
                "below FAA 51% requirement."
            )

        # STABILITY CHECK: Canard must stall before wing
        # Simplified thin-airfoil lift curve slope: a0 = 2*pi per radian
        a0_per_deg = 2.0 * math.pi / 180.0  # ~0.1097 per degree
        # Stall AoA in aircraft frame = alpha_0L + CLmax/a0 - incidence
        canard_stall_aoa = (
            self.aero_limits.canard_alpha_0L
            + self.aero_limits.canard_clmax / a0_per_deg
            - self.geometry.canard_incidence
        )
        wing_stall_aoa = (
            self.aero_limits.wing_alpha_0L + self.aero_limits.wing_clmax / a0_per_deg
        )
        stall_margin = wing_stall_aoa - canard_stall_aoa
        if stall_margin < self.aero_limits.min_stall_margin_deg:
            errors.append(
                f"STABILITY WARNING: Canard-first stall margin is {stall_margin:.1f} deg, "
                f"below minimum {self.aero_limits.min_stall_margin_deg:.1f} deg. "
                "Run OpenVSP analysis to verify."
            )

        return errors

    def summary(self) -> str:
        """Generate human-readable configuration summary."""
        return f"""
Open-EZ PDE Configuration Summary
=================================
Baseline: {self.baseline}
Version: {self.version}

GEOMETRY
--------
Wing Span: {self.geometry.wing_span / 12:.1f} ft
Wing Area: {self.geometry.wing_area:.1f} sq ft
Wing AR: {self.geometry.wing_aspect_ratio:.2f}
Canard Span: {self.geometry.canard_span / 12:.1f} ft
Canard Area: {self.geometry.canard_area:.1f} sq ft
Canard Arm: {self.geometry.canard_arm:.1f} in

AIRFOILS
--------
Canard: {self.airfoils.canard.value} (SAFETY CRITICAL)
Wing: {self.airfoils.wing_root.value}
Wing Reflex: {self.airfoils.wing_reflex_percent}%

MATERIALS
---------
Spar Cap Plies: {self.materials.spar_cap_plies}
Spar Trough Depth: {self.materials.spar_trough_depth:.3f} in

COMPLIANCE
----------
Builder Credits: {self.compliance.total_builder_credit:.1%}
FAA 51% Status: {"PASS" if self.compliance.total_builder_credit >= 0.51 else "FAIL"}
"""


# Singleton instance - import this throughout the project
config = AircraftConfig()

# Validate on import
_errors = config.validate()
if _errors:
    import warnings

    for err in _errors:
        warnings.warn(err, UserWarning)
