"""Block 3 M3.4: canard equivalence report gates (plan T12; captain-written tests, script by a crew).

Contract for `scripts/equivalence_report.py` (the crew implements it to these tests):

  gate(passed, flagged=(), reasons=(), test_required=None)
      -> {"state", "reasons", "flagged_inputs", "test_required_inputs", "closing_coupons", "label"}
      state is "pass", "fail", "blocked" or "open". Any reason, any flagged input, or passed=None
      blocks. A flagged input adds the reason "inputs_unsourced". test_required maps
      "<material>.<property>" -> coupon id for inputs flagged requires_original_test (ledger row 77);
      any entry adds the reason "requires_original_test", lists the inputs in test_required_inputs
      and the sorted unique coupon ids in closing_coupons (both lists always present). That reason
      cannot be passed in reasons (ValueError): it must carry its inputs and coupons. The state is
      "open" when requires_original_test is the only reason and no input is flagged unsourced; with
      any other reason it is "blocked". Neither can ever be "pass". reasons are sorted and
      de-duplicated; label is "pass", "fail", "blocked: <reasons joined by ', '>" or
      "open: requires_original_test".
  REASONS = {"inputs_unsourced", "glass_unvalidated", "criterion_unavailable", "not_applicable",
             "requires_original_test"}
  STATES = ("pass", "fail", "blocked", "open")
  LOAD_CASES = ("+M", "-M", "+T", "-T")
  strength_ratio_min(carbon, book) -> float
      carbon, book: {(load_case, f12_star): first-ply-failure capacity under that unit load}. The
      minimum over every key of carbon/book. Raises ValueError unless both hold all four load cases
      at the same two or more f12 values (the cited value and 0).
  strength_gate(carbon, book, flagged=(), reasons=()) -> gate dict; passed iff the minimum >= 1.0.
  mass_placement_gate(offset_carbon, offset_book, flagged=(), reasons=()) -> gate dict;
      passed iff the carbon mass-centroid offset aft of the shear centre <= the book's.
  f_consistency(F_carbon, F_book) -> gate dict with "kind": "consistency_check";
      passed iff F_carbon <= F_book (F is a flexibility: smaller is stiffer).
  stiffness_deltas(book, carbon, threshold) -> {name: {"book", "carbon", "delta_fraction", "flag"}}
      for every name in book (EI, GJ, ...); flag iff delta_fraction > threshold.
  flagged_inputs(schedule, materials, material_ids) -> sorted list of "<material>.<property>" for
      every property flagged unsourced in the named materials, plus "<ply id>.count" etc. for every
      flagged ply. Properties flagged requires_original_test are NOT in this list.
  test_required_inputs(materials, material_ids) -> {"<material>.<property>": closing coupon id} for
      every property flagged requires_original_test in the named materials.
  station_capacities(schedule, materials, section, bl, f12_star) -> {load_case: capacity}
      First-ply-failure capacity (minimum Tsai-Wu strength ratio over the plies) under a unit moment
      and a unit torque, both signs, at span station bl, through core.kernels.
  build_report() -> dict; render(report) -> str (canonical JSON, sorted keys, indent 2, final newline);
  main(out: Path) writes render(build_report()) to out.
"""

import copy
import json
from pathlib import Path

import pytest

eq = pytest.importorskip(
    "scripts.equivalence_report",
    reason="M3.4 report script pending (plan T12, crew lane)",
)

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "data/validation/equivalence_canard.json"
F12 = (-0.5, 0.0)


def caps(value):
    return {(lc, f): value for lc in eq.LOAD_CASES for f in F12}


# ---- gate states ----------------------------------------------------------------------------


def test_gate_pass_and_fail():
    assert eq.gate(True)["state"] == "pass"
    assert eq.gate(True)["label"] == "pass"
    assert eq.gate(False)["state"] == "fail"


def test_gate_with_unknown_result_is_blocked():
    g = eq.gate(None)
    assert g["state"] == "blocked"
    assert g["label"].startswith("blocked: ")


@pytest.mark.parametrize(
    "name",
    ["bid_7725_wet.E1", "carbon3k_mgs418_wet.F6", "cap_top_all.count", "cell.web_xc"],
)
def test_flagging_any_single_input_turns_pass_into_blocked(name):
    assert eq.gate(True)["state"] == "pass"
    g = eq.gate(True, flagged=[name])
    assert g["state"] == "blocked"
    assert "inputs_unsourced" in g["reasons"]
    assert g["flagged_inputs"] == [name]


def test_flagging_turns_fail_into_blocked_too():
    assert eq.gate(False, flagged=["x.E1"])["state"] == "blocked"


BLOCKING = {
    "inputs_unsourced",
    "glass_unvalidated",
    "criterion_unavailable",
    "not_applicable",
}


@pytest.mark.parametrize("reason", sorted(BLOCKING))
def test_every_reason_blocks(reason):
    assert reason in eq.REASONS
    g = eq.gate(True, reasons=[reason])
    assert g["state"] == "blocked" and g["label"] == f"blocked: {reason}"


def test_reasons_are_sorted_and_unique():
    g = eq.gate(
        True, flagged=["a.E1"], reasons=["glass_unvalidated", "inputs_unsourced"]
    )
    assert g["reasons"] == ["glass_unvalidated", "inputs_unsourced"]
    assert g["label"] == "blocked: glass_unvalidated, inputs_unsourced"


def test_unknown_reason_is_rejected():
    with pytest.raises(ValueError):
        eq.gate(True, reasons=["looks_fine"])


# ---- requires_original_test (ledger row 77) -------------------------------------------------

NEEDS_TEST = {"c.E1": "B5-CPW-T0", "c.F1c": "B5-CPW-C0", "c.F1t": "B5-CPW-T0"}


def test_reasons_and_states_are_the_registered_sets():
    assert eq.REASONS == BLOCKING | {"requires_original_test"}
    assert tuple(eq.STATES) == ("pass", "fail", "blocked", "open")


@pytest.mark.parametrize("passed", [True, False, None])
def test_requires_original_test_alone_reads_open_never_pass(passed):
    g = eq.gate(passed, test_required=NEEDS_TEST)
    assert g["state"] == "open"
    assert g["label"] == "open: requires_original_test"
    assert g["reasons"] == ["requires_original_test"]
    assert g["test_required_inputs"] == ["c.E1", "c.F1c", "c.F1t"]
    assert g["closing_coupons"] == ["B5-CPW-C0", "B5-CPW-T0"]
    assert g["flagged_inputs"] == []


def test_one_test_required_input_turns_pass_into_open():
    assert eq.gate(True)["state"] == "pass"
    assert eq.gate(True, test_required={"c.E1": "B5-CPW-T0"})["state"] == "open"


def test_requires_original_test_with_another_reason_is_blocked_and_keeps_both():
    g = eq.gate(True, flagged=["b.E1"], test_required=NEEDS_TEST)
    assert g["state"] == "blocked"
    assert g["reasons"] == ["inputs_unsourced", "requires_original_test"]
    assert g["label"] == "blocked: inputs_unsourced, requires_original_test"
    assert g["closing_coupons"] == ["B5-CPW-C0", "B5-CPW-T0"]
    g = eq.gate(True, reasons=["glass_unvalidated"], test_required=NEEDS_TEST)
    assert g["state"] == "blocked"


def test_requires_original_test_cannot_be_asserted_without_inputs_and_coupons():
    with pytest.raises(ValueError):
        eq.gate(True, reasons=["requires_original_test"])


def test_plain_gates_carry_empty_test_lists():
    g = eq.gate(True)
    assert g["test_required_inputs"] == [] and g["closing_coupons"] == []


def test_test_required_inputs_reads_the_flag_and_flagged_inputs_ignores_it():
    mats = {
        "m": {
            "use": "design-proxy",
            "properties": {
                "E1": {
                    "value": None,
                    "units": "psi",
                    "flag": "requires_original_test",
                    "search": "s",
                    "closing_test": {
                        "method": "ASTM D3039/D3039M",
                        "coupon": "B5-M-T0",
                    },
                    "test_plan": "plan.md",
                },
                "E2": {"value": None, "units": "psi", "flag": "unsourced"},
            },
        }
    }
    sched = {"plies": []}
    assert eq.test_required_inputs(mats, ["m"]) == {"m.E1": "B5-M-T0"}
    assert eq.flagged_inputs(sched, mats, ["m"]) == ["m.E2"]


# ---- strength ratio -------------------------------------------------------------------------


def test_strength_ratio_is_the_minimum_over_every_case():
    book = caps(2.0)
    carbon = caps(3.0)
    carbon[("-T", 0.0)] = 1.9  # one case only, at f12 = 0
    assert eq.strength_ratio_min(carbon, book) == pytest.approx(0.95)
    assert eq.strength_gate(carbon, book)["state"] == "fail"


def test_strength_gate_passes_at_equal_capacity():
    assert eq.strength_gate(caps(2.0), caps(2.0))["state"] == "pass"


def test_strength_ratio_needs_both_signs_of_both_loads():
    book, carbon = caps(1.0), caps(1.0)
    del carbon[("-M", F12[0])]
    with pytest.raises(ValueError):
        eq.strength_ratio_min(carbon, book)


def test_strength_ratio_needs_two_f12_values():
    one = {(lc, -0.5): 1.0 for lc in eq.LOAD_CASES}
    with pytest.raises(ValueError):
        eq.strength_ratio_min(one, one)


# ---- mass placement, F consistency, stiffness deltas ------------------------------------------


def test_mass_placement_gate():
    assert eq.mass_placement_gate(0.5, 0.6)["state"] == "pass"
    assert eq.mass_placement_gate(0.6, 0.6)["state"] == "pass"
    assert (
        eq.mass_placement_gate(0.7, 0.6)["state"] == "fail"
    )  # broken input: centroid moved aft


def test_doubled_f_carbon_fails_the_relative_comparison():
    g = eq.f_consistency(1.0e-4, 1.0e-4)
    assert g["state"] == "pass" and g["kind"] == "consistency_check"
    assert eq.f_consistency(2.0e-4, 1.0e-4)["state"] == "fail"


def test_stiffness_deltas_present_and_flagged_past_threshold():
    d = eq.stiffness_deltas({"EI": 100.0, "GJ": 50.0}, {"EI": 105.0, "GJ": 60.0}, 0.10)
    assert d["EI"]["delta_fraction"] == pytest.approx(0.05)
    assert d["EI"]["flag"] is False
    assert d["GJ"]["delta_fraction"] == pytest.approx(0.20)
    assert d["GJ"]["flag"] is True


# ---- flagged-input collection on the real files ---------------------------------------------


def test_flagged_inputs_finds_single_flags():
    mats = {
        "m": {
            "use": "design-proxy",
            "properties": {
                "E1": {"value": 1.0, "units": "psi", "cite": "om-1980:p1"},
                "E2": {"value": 1.0, "units": "psi", "cite": "om-1980:p1"},
            },
        }
    }
    sched = {
        "plies": [
            {"id": "p", "material": "m", "count": 1, "cite": "om-1980:p1", "flag": None}
        ]
    }
    assert eq.flagged_inputs(sched, mats, ["m"]) == []
    broken = copy.deepcopy(mats)
    broken["m"]["properties"]["E2"] = {
        "value": None,
        "units": "psi",
        "flag": "unsourced",
    }
    assert eq.flagged_inputs(sched, broken, ["m"]) == ["m.E2"]
    sched2 = copy.deepcopy(sched)
    sched2["plies"][0].update(count=None, cite=None, flag="unsourced")
    assert eq.flagged_inputs(sched2, mats, ["m"]) == ["p.count"]


# ---- the report on the real data ------------------------------------------------------------


@pytest.fixture(scope="module")
def report():
    return eq.build_report()


def test_report_regenerates_byte_for_byte(tmp_path, report):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    eq.main(a)
    eq.main(b)
    assert a.read_bytes() == b.read_bytes()
    assert a.read_text() == eq.render(report)
    assert COMMITTED.read_text() == a.read_text(), (
        "committed report is stale: regenerate it"
    )


def test_every_gate_has_a_state_and_reasons(report):
    gates = report["gates"]
    for name in ("strength", "mass_placement", "elevator_balance"):
        g = gates[name]
        assert g["state"] in set(eq.STATES), name
        assert set(g["reasons"]) <= eq.REASONS, name
        assert (g["state"] in {"blocked", "open"}) == bool(g["reasons"]), name


def test_today_the_strength_gate_is_blocked_for_the_known_reasons(report):
    g = report["gates"]["strength"]
    assert g["state"] == "blocked"
    assert (
        "inputs_unsourced" in g["reasons"]
    )  # book and carbon lamina values are flagged
    assert "glass_unvalidated" not in g["reasons"]  # M3.1 glass closed, ledger row 80
    assert "bid_7725_wet.E1" in g["flagged_inputs"]
    # the carbon warp values need an original test (row 77): listed apart, with their coupons
    assert "requires_original_test" in g["reasons"]
    assert "carbon3k_mgs418_wet.E1" in g["test_required_inputs"]
    assert "carbon3k_mgs418_wet.E1" not in g["flagged_inputs"]
    assert {"B5-CPW-T0", "B5-CPW-C0"} <= set(g["closing_coupons"])


def test_today_the_mass_placement_gate_is_blocked(report):
    g = report["gates"]["mass_placement"]
    assert g["state"] == "blocked" and "inputs_unsourced" in g["reasons"]


def test_elevator_balance_waits_for_report_45(report):
    g = report["gates"]["elevator_balance"]
    assert g["state"] == "blocked" and "criterion_unavailable" in g["reasons"]
    assert g.get("by_analogy") is True


def test_reported_only_items_are_present(report):
    rep = report["reported"]
    assert rep["f_relative"]["kind"] == "consistency_check"
    for name in ("EI", "GJ", "torsional_inertia", "mass_per_length"):
        assert name in rep["stiffness_and_mass_deltas"], name
    assert "book_canard_mass_vs_closure" in rep
    assert rep["stiffness_flag_fraction"] == pytest.approx(0.10)
    assert report["inputs_sha256"]  # the row-74 freeze hashes travel with the report


def test_committed_json_is_valid():
    json.loads(COMMITTED.read_text())


# ---- discriminating strength check through the kernels (cap ply removed) --------------------

FIXTURE_LAMINA = {  # TEST FIXTURE ONLY, not data: round numbers so the pipeline can run before sourcing
    "use": "design-proxy",
    "properties": {
        k: {"value": v, "units": u, "cite": "om-1980:p1"}
        for k, v, u in [
            ("E1", 5.0e6, "psi"),
            ("E2", 1.5e6, "psi"),
            ("G12", 0.6e6, "psi"),
            ("nu12", 0.28, "1"),
            ("F1t", 100e3, "psi"),
            ("F1c", 80e3, "psi"),
            ("F2t", 5e3, "psi"),
            ("F2c", 20e3, "psi"),
            ("F6", 8e3, "psi"),
            ("t_ply", 0.01, "in"),
            ("areal_mass", 0.05, "lb/ft2"),
        ]
    },
}
FIXTURE_SECTION = {"width": 10.0, "height": 1.5, "web_x": 3.0, "cap_width": 3.0}


def fixture_schedule(cap_count):
    def ply(pid, region, angle, count):
        return {
            "id": pid,
            "region": region,
            "material": "fx",
            "angle_deg": angle,
            "count": count,
            "bl_from": -54,
            "bl_to": 54,
            "cite": "om-1980:p1",
            "flag": None,
        }

    return {
        "plies": [
            ply("web", "shear_web", [45, -45], 2),
            ply("capb", "spar_cap_bottom", 0, cap_count),
            ply("capt", "spar_cap_top", 0, cap_count),
            ply("skb0", "skin_bottom", 0, 1),
            ply("skb45", "skin_bottom", [45, -45], 1),
            ply("skt0", "skin_top", 0, 1),
            ply("skt45", "skin_top", [45, -45], 1),
        ]
    }


def test_removing_one_cap_ply_fails_the_strength_gate():
    pytest.importorskip(
        "core.kernels.laminate", reason="needs the M3.1 kernel (plan T4)"
    )
    pytest.importorskip(
        "core.kernels.thinwall", reason="needs the M3.2 kernel (plan T7)"
    )
    mats = {"fx": FIXTURE_LAMINA}

    def capacities(schedule):
        out = {}
        for f in F12:
            for lc, v in eq.station_capacities(
                schedule, mats, FIXTURE_SECTION, 5.0, f
            ).items():
                out[(lc, f)] = v
        return out

    book = capacities(fixture_schedule(6))
    assert eq.strength_gate(capacities(fixture_schedule(6)), book)["state"] == "pass"
    broken = fixture_schedule(6)
    broken["plies"][1]["count"] = 5  # one bottom cap ply removed
    assert eq.strength_gate(capacities(broken), book)["state"] == "fail"
