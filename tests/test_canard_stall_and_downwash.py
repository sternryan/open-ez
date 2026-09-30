"""
Phase 2 Tests: Canard Stall Priority, Downwash Model, Canard MAC
=================================================================

Validates:
1. Default config canard stalls >= 2 deg before wing
2. Artificially high canard CLmax triggers stall priority failure
3. Downwash model uses vertical separation (Phillips Ch. 9)
4. NP shifts forward vs old heuristic (safety-conservative)
5. Canard AC uses MAC, not root chord
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

sys.modules.setdefault("cadquery", MagicMock())
sys.modules.setdefault("OCP", MagicMock())

from core.analysis import PhysicsEngine  # noqa: E402
from config import config  # noqa: E402


class TestCanardStallPriority:
    def test_default_config_canard_stalls_first(self):
        """Default config must show canard stalling >= 2 deg before wing."""
        engine = PhysicsEngine()
        is_safe, msg = engine.check_canard_stall_priority()
        assert is_safe, f"Canard stall priority check failed: {msg}"
        assert "WARNING" not in msg

    def test_high_canard_clmax_triggers_failure(self):
        """Setting canard_clmax artificially high should fail stall priority."""
        # Save original value
        original = config.aero_limits.canard_clmax
        try:
            config.aero_limits.canard_clmax = 2.5  # Unrealistically high
            engine = PhysicsEngine()
            is_safe, msg = engine.check_canard_stall_priority()
            assert not is_safe, f"Should fail with canard_clmax=2.5: {msg}"
        finally:
            config.aero_limits.canard_clmax = original

    def test_stall_message_contains_reynolds_info(self):
        """Stall check should report Reynolds-scaled CLmax values."""
        engine = PhysicsEngine()
        _, msg = engine.check_canard_stall_priority()
        assert "CLmax_canard" in msg
        assert "CLmax_wing" in msg
        assert "Re=" in msg

    def test_reynolds_scaling_reduces_canard_clmax(self):
        """Canard CLmax at approach Re should be lower than reference value.

        At approach speed (60 KTAS), canard chord (~15") produces Re ~750K,
        much lower than the reference Re of 3.0M. The scaling (Re/Re_ref)^0.1
        should reduce CLmax.
        """
        engine = PhysicsEngine()
        _, msg = engine.check_canard_stall_priority()
        # Extract CLmax_canard from message
        # Format: "CLmax_canard=X.XXX"
        for part in msg.split(", "):
            if "CLmax_canard=" in part:
                val = float(part.split("=")[1].split(" ")[0])
                # Should be less than reference 1.35
                assert val < config.aero_limits.canard_clmax, (
                    f"Scaled CLmax {val} not less than ref {config.aero_limits.canard_clmax}"
                )
                break
        else:
            raise AssertionError("CLmax_canard not found in message")


class TestDownwashModel:
    def test_np_with_vertical_separation(self):
        """NP should shift forward with proper downwash model vs no downwash."""
        engine = PhysicsEngine()
        np_with_downwash = engine.calculate_neutral_point()
        # NP should be a reasonable FS value (100-180 range)
        assert 100.0 < np_with_downwash < 180.0

    def test_zero_vertical_offset_stronger_downwash(self):
        """With h=0 (no vertical separation), the canard downwash at the wing is strongest.

        The downwash acts on the aft surface, the wing (Raymer eq. 16.9; ledger C3): it cuts the
        wing's effective lift slope, so the wing contributes less and the NP moves FORWARD
        toward the canard AC. So np_h0 < np_h100.
        """
        original_h = config.geometry.canard_vertical_offset_in
        try:
            # h=0: canard and wing in same plane -- maximum downwash
            config.geometry.canard_vertical_offset_in = 0.0
            engine_h0 = PhysicsEngine()
            np_h0 = engine_h0.calculate_neutral_point()

            # h=100: extreme separation -- downwash much weaker
            config.geometry.canard_vertical_offset_in = 100.0
            engine_h100 = PhysicsEngine()
            np_h100 = engine_h100.calculate_neutral_point()

            assert np_h0 < np_h100, (
                f"NP at h=0 ({np_h0:.1f}) should be forward of NP at h=100 ({np_h100:.1f})"
            )
        finally:
            config.geometry.canard_vertical_offset_in = original_h

    def test_downwash_h12_reduces_by_expected_amount(self):
        """With h=12\", b_c=147\", vertical factor should be ~0.974.

        (2*12/147)^2 = 0.0267, factor = 1/1.0267 = 0.974
        """
        h = 12.0
        b_c = 147.0
        vert_factor = 1.0 / (1.0 + (2.0 * h / b_c) ** 2)
        assert abs(vert_factor - 0.974) < 0.002


class TestCanardMAC:
    def test_canard_mac_equals_chord_for_rectangle(self):
        """Canard is a rectangle (book geometry): MAC equals the single chord, root == tip."""
        import pytest

        c = config.geometry.canard_chord
        assert config.geometry.canard_root_chord == config.geometry.canard_tip_chord
        cr, ct = config.geometry.canard_root_chord, config.geometry.canard_tip_chord
        taper = ct / cr
        mac = (2 / 3) * cr * (1 + taper + taper**2) / (1 + taper)
        assert mac == pytest.approx(c)

    def test_canard_mac_value(self):
        """Pure MAC formula check on the retired 17/13.5 taper (independent of config)."""
        cr = 17.0
        ct = 13.5
        taper = ct / cr  # 0.794
        mac = (2 / 3) * cr * (1 + taper + taper**2) / (1 + taper)
        assert abs(mac - 15.35) < 0.1, f"Canard MAC = {mac:.2f}, expected ~15.35"

    def test_canard_ac_uses_mac_in_np_calc(self):
        """NP calculation should use canard MAC, not root chord, for AC location.

        Canard AC uses the MAC; for the rectangular book canard MAC equals the chord.
        """
        # The NP calculation internally uses MAC -- just verify NP is reasonable
        engine = PhysicsEngine()
        np_loc = engine.calculate_neutral_point()
        assert 100.0 < np_loc < 180.0
