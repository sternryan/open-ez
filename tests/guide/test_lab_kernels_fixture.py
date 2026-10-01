"""The lab's TypeScript kinematics (guide/lab/src/logic/kin.ts) are a re-implementation of core.elevators_kin and core.nose_gear_kin.
guide/lab/tests/fixtures/kernels.json holds numbers the Python kernels computed; guide/lab/tests/kin.test.ts checks the TypeScript
against them, and this test checks the fixture against the kernels, so neither side can drift alone.

Regenerate after a deliberate kernel change:  .venv/bin/python -m tests.guide.test_lab_kernels_fixture
"""
import json
from pathlib import Path

import numpy as np

FIXTURE = Path(__file__).resolve().parents[2] / "guide" / "lab" / "tests" / "fixtures" / "kernels.json"


def build() -> dict:
    from core import elevators_book as eb
    from core import elevators_kin as ek
    from core import landing_gear_book as lgb
    from core import nose_gear_kin as ngk
    from guide import fuselage_export as fe

    ex = fe.extras_section()
    hinge = list(eb.hinge_axis_xz())
    pts_in = [[3.0, 0.5], [12.0, -0.4], [9.664, 0.2245], [-1.0, 2.0]]
    rot = [{"pt": p, "deg": d, "out": list(ek.rotate_about_hinge(tuple(p), tuple(hinge), d))} for p in pts_in for d in (-15.0, 0.0, 12.5, 30.0)]
    hang = [{"dx": dx, "dz": dz, "pitch": ek.hang_pitch_deg(dx, dz), "nose_down": ek.hangs_nose_down(dx, dz)}
            for dx, dz in ((-1.5, 0.1), (-1.5, -0.1), (-2.0, 0.0), (1.0, 0.3), (0.2, -1.0))]
    classes = [{"deg": d, "cls": ek.classify_up_travel(d)} for d in (10.0, 12.4, 12.5, 14.99, 15.0, 20.0)]
    poses = [{"side": s, "deg": d, "m": eb.elevator_pose(s, d).tolist()} for s in ("right", "left") for d in (-15.0, 30.0)]
    ng = ex["nose_gear"]
    nose = []
    for cand in ("plans", "manual"):
        pts = lgb.nose_gear_points(cand)
        up = lgb.nose_retracted_theta_deg(cand)
        rows = []
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            m = lgb.nose_gear_pose(t, cand)
            axle = m @ np.array([*pts["axle"], 1.0])
            rows.append({"t": t, "theta": ngk.retraction_theta_deg(t, pts["theta_down_deg"], up), "crank": ngk.crank_turns(t),
                         "rot": [m[0, 0], m[0, 2], m[2, 0], m[2, 2]], "trans": [m[0, 3], m[2, 3]], "axle_xz": [axle[0], axle[2]]})
        nose.append({"cand": cand, "pivot": [pts["pivot"][0], pts["pivot"][2]], "axle": [pts["axle"][0], pts["axle"][2]],
                     "theta_down": pts["theta_down_deg"], "theta_up": up, "rows": rows})
    return {"elevators": {"hinge": hinge, "rotate": rot, "hang": hang, "classify": classes, "poses": poses},
            "nose": nose, "extras": {"elevators": ex["elevators"], "nose_gear": ng}}


def _round(x, n=9):
    if isinstance(x, dict):
        return {k: _round(v, n) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_round(v, n) for v in x]
    if isinstance(x, float):
        return round(x, n)
    return x


def test_the_kernel_fixture_is_what_the_python_kernels_compute_today():
    assert json.loads(FIXTURE.read_text()) == json.loads(json.dumps(_round(build())))


def test_the_elevator_hang_pitch_matches_the_pose_convention():
    """pitch positive = nose (leading edge) down; the TE-down pose angle is its negative and puts the CG below the hinge."""
    from core import elevators_kin as ek

    dx, dz = -1.5, 0.1
    pitch = ek.hang_pitch_deg(dx, dz)
    assert 0 < pitch < 180 and ek.hangs_nose_down(dx, dz)
    x, z = ek.rotate_about_hinge((dx, dz), (0.0, 0.0), -pitch)
    assert z < -1.0 and abs(x) < 0.3  # the CG hangs straight under the hinge line


if __name__ == "__main__":
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(_round(build()), indent=1))
    print("wrote", FIXTURE)
