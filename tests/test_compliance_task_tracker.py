"""Unit tests for core.compliance.tracker (ComplianceTaskTracker, ChecklistEntry, TaskRole)."""

from pathlib import Path
from typing import Tuple

import pytest

from core.compliance import ComplianceTracker, ManufacturingMethod
from core.compliance.tracker import ChecklistEntry, ComplianceTaskTracker, TaskRole


@pytest.fixture
def trackers() -> Tuple[ComplianceTracker, ComplianceTaskTracker]:
    """Build a fresh ComplianceTracker and ComplianceTaskTracker for each test."""
    tracker = ComplianceTracker()
    task_tracker = ComplianceTaskTracker(tracker)
    return tracker, task_tracker


def test_task_role_enum_values() -> None:
    """TaskRole enum exposes exact builder and helper string values."""
    assert TaskRole.BUILDER.value == "builder"
    assert TaskRole.HELPER.value == "helper"


def test_artifact_task_map_keys_and_wing_cad_bindings() -> None:
    """ARTIFACT_TASK_MAP has the 4 expected keys and maps wing/cad to both wing cores with BUILDER_CNC."""
    expected_keys = {
        ("canard", "cad"),
        ("canard", "layup_schedule"),
        ("wing", "cad"),
        ("wing", "layup_schedule"),
    }
    assert set(ComplianceTaskTracker.ARTIFACT_TASK_MAP.keys()) == expected_keys
    assert len(ComplianceTaskTracker.ARTIFACT_TASK_MAP) == 4
    assert ComplianceTaskTracker.ARTIFACT_TASK_MAP[("wing", "cad")] == [
        ("wing_cores_left", ManufacturingMethod.BUILDER_CNC),
        ("wing_cores_right", ManufacturingMethod.BUILDER_CNC),
    ]
    assert ComplianceTaskTracker.ARTIFACT_TASK_MAP[("canard", "cad")] == [
        ("canard_cores", ManufacturingMethod.BUILDER_CNC),
    ]
    assert ComplianceTaskTracker.ARTIFACT_TASK_MAP[("canard", "layup_schedule")] == [
        ("canard_skins", ManufacturingMethod.BUILDER_MANUAL),
    ]
    assert ComplianceTaskTracker.ARTIFACT_TASK_MAP[("wing", "layup_schedule")] == [
        ("wing_skins_left", ManufacturingMethod.BUILDER_MANUAL),
        ("wing_skins_right", ManufacturingMethod.BUILDER_MANUAL),
    ]


def test_fresh_tracker_initial_task_state(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """Tracked tasks on a fresh tracker have exact descriptions, base credits, and completed == False."""
    tracker, task_tracker = trackers
    expected = {
        "canard_cores": ("Fabricate canard foam cores (Roncz R1145MS)", 0.05),
        "canard_skins": ("Layup canard fiberglass skins", 0.05),
        "wing_cores_left": ("Fabricate left wing foam cores", 0.08),
        "wing_cores_right": ("Fabricate right wing foam cores", 0.08),
        "wing_skins_left": ("Layup left wing fiberglass skins", 0.12),
        "wing_skins_right": ("Layup right wing fiberglass skins", 0.12),
    }
    for task_id, (description, base_credit) in expected.items():
        task = tracker.get_task(task_id)
        assert task.description == description
        assert task.base_credit == pytest.approx(base_credit)
        assert task.completed is False
    assert task_tracker.checklist == []


def test_record_generation_canard_cad_default_builder(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """Recording canard/cad with default BUILDER role awards full CNC credit and default notes."""
    tracker, task_tracker = trackers
    entries = task_tracker.record_generation("canard", "cad")

    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, ChecklistEntry)
    assert entry.task_id == "canard_cores"
    assert entry.description == "Fabricate canard foam cores (Roncz R1145MS)"
    assert entry.component == "canard"
    assert entry.artifact == "cad"
    assert entry.role == TaskRole.BUILDER
    assert entry.method == ManufacturingMethod.BUILDER_CNC
    assert entry.credit_awarded == pytest.approx(0.05)
    assert entry.note == ""
    assert entry.completed is True

    task = tracker.get_task("canard_cores")
    assert task.completed is True
    assert task.method == ManufacturingMethod.BUILDER_CNC
    assert task.notes == "cad generated for canard"


def test_record_generation_wing_layup_schedule_helper(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """Recording wing/layup_schedule as HELPER halves credit to 0.06 across both wing skin tasks."""
    tracker, task_tracker = trackers
    entries = task_tracker.record_generation(
        "wing", "layup_schedule", TaskRole.HELPER, "note1"
    )

    assert [e.task_id for e in entries] == ["wing_skins_left", "wing_skins_right"]
    for entry in entries:
        assert entry.role == TaskRole.HELPER
        assert entry.method == ManufacturingMethod.BUILDER_HELPER
        assert entry.credit_awarded == pytest.approx(0.12 / 2)
        assert entry.credit_awarded == pytest.approx(0.06)
        assert entry.note == "note1"
        assert entry.completed is True

    for task_id in ("wing_skins_left", "wing_skins_right"):
        task = tracker.get_task(task_id)
        assert task.completed is True
        assert task.method == ManufacturingMethod.BUILDER_HELPER
        assert task.notes == "note1"
        assert task.builder_credit == pytest.approx(0.06)


def test_record_generation_unmapped_artifact_returns_empty(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """Unmapped component/artifact pairs return an empty list and leave checklist unchanged."""
    _, task_tracker = trackers
    entries = task_tracker.record_generation("fuselage", "cad")

    assert entries == []
    assert task_tracker.checklist == []


def test_record_generation_repeat_as_helper_updates_method_and_keeps_note(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """Re-recording canard/cad as HELPER without a note halves credit and preserves initial task notes."""
    tracker, task_tracker = trackers
    task_tracker.record_generation("canard", "cad", TaskRole.BUILDER)
    second_entries = task_tracker.record_generation("canard", "cad", TaskRole.HELPER)

    assert len(second_entries) == 1
    second = second_entries[0]
    assert second.method == ManufacturingMethod.BUILDER_HELPER
    assert second.credit_awarded == pytest.approx(0.05 / 2)
    assert second.credit_awarded == pytest.approx(0.025)

    task = tracker.get_task("canard_cores")
    assert task.method == ManufacturingMethod.BUILDER_HELPER
    assert task.notes == "cad generated for canard"
    assert len(task_tracker.checklist) == 2


def test_checklist_property_returns_defensive_copy(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """Mutating the list returned by checklist does not mutate the tracker's internal checklist."""
    _, task_tracker = trackers
    task_tracker.record_generation("canard", "cad")
    returned = task_tracker.checklist
    assert len(returned) == 1

    returned.append(returned[0])
    assert len(task_tracker.checklist) == 1


def test_render_running_checklist_fresh_tracker(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """Fresh tracker renders header metadata and 6 PENDING rows with em-dash artifacts."""
    _, task_tracker = trackers
    rendered = task_tracker.render_running_checklist()
    lines = rendered.splitlines()

    assert "# FAA 8000-38 Running Checklist" in lines
    assert "Project: Open-EZ PDE (Long-EZ Model 61)" in lines
    assert "Baseline Canard Airfoil: roncz_r1145ms" in lines
    assert "| Task | Artifact | Role | Method | Status | Credit |" in lines

    pending_rows = [
        line for line in lines if line.startswith("| ") and "PENDING" in line
    ]
    assert len(pending_rows) == 6
    assert (
        "| Layup canard fiberglass skins | — | builder | builder_manual | PENDING | 5.0% |"
        in lines
    )


def test_render_running_checklist_after_canard_cad(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """After recording canard/cad, the canard cores row shows DONE with builder_cnc and 5.0%."""
    _, task_tracker = trackers
    task_tracker.record_generation("canard", "cad")
    lines = task_tracker.render_running_checklist().splitlines()

    assert (
        "| Fabricate canard foam cores (Roncz R1145MS) | cad | builder | builder_cnc | DONE | 5.0% |"
        in lines
    )


def test_render_running_checklist_after_helper_wing_layup(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
) -> None:
    """After recording wing/layup_schedule as HELPER, left wing skins row shows helper, builder_helper, 6.0%."""
    _, task_tracker = trackers
    task_tracker.record_generation("wing", "layup_schedule", TaskRole.HELPER, "note1")
    lines = task_tracker.render_running_checklist().splitlines()

    assert (
        "| Layup left wing fiberglass skins | layup_schedule | helper | builder_helper | DONE | 6.0% |"
        in lines
    )


def test_write_checklist_creates_dir_and_matches_rendered_text(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
    tmp_path: Path,
) -> None:
    """write_checklist creates the target directory and writes compliance_checklist.md matching render output."""
    _, task_tracker = trackers
    task_tracker.record_generation("canard", "cad")
    out_dir = tmp_path / "out"

    checklist_path = task_tracker.write_checklist(out_dir)

    assert out_dir.is_dir()
    assert checklist_path == out_dir / "compliance_checklist.md"
    file_lines = [
        line
        for line in checklist_path.read_text().splitlines()
        if not line.startswith("Generated:")
    ]
    rendered_lines = [
        line
        for line in task_tracker.render_running_checklist().splitlines()
        if not line.startswith("Generated:")
    ]
    assert file_lines == rendered_lines


def test_write_layup_schedule_canard(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
    tmp_path: Path,
) -> None:
    """write_layup_schedule for canard writes header, 4 step rows, exact step 1, and trailing newline."""
    _, task_tracker = trackers
    out_dir = tmp_path / "schedules"
    schedule_path = task_tracker.write_layup_schedule("canard", out_dir)

    assert schedule_path == out_dir / "canard_layup_schedule.md"
    content = schedule_path.read_text()
    lines = content.splitlines()

    assert lines[0] == "# Roncz R1145MS Canard Layup"
    step_rows = [
        line
        for line in lines
        if any(line.startswith(f"| {idx} |") for idx in range(1, 5))
    ]
    assert len(step_rows) == 4
    assert (
        step_rows[0]
        == "| 1 | Surface prep: Sand/clean foam cores, apply micro slurry. | BUILDER | Layup canard fiberglass skins (5.0%) |"
    )
    assert (
        lines[-1]
        == "- Attach photos of peel-ply removal and cured surfaces to the compliance package."
    )
    assert content.endswith(
        "- Attach photos of peel-ply removal and cured surfaces to the compliance package.\n"
    )
    assert not content.endswith("\n\n")


def test_write_layup_schedule_wing(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
    tmp_path: Path,
) -> None:
    """write_layup_schedule for wing writes wing_layup_schedule.md with Main Wing header and 17-ply step 1."""
    _, task_tracker = trackers
    out_dir = tmp_path / "schedules"
    schedule_path = task_tracker.write_layup_schedule("wing", out_dir)

    assert schedule_path == out_dir / "wing_layup_schedule.md"
    assert schedule_path.name == "wing_layup_schedule.md"
    lines = schedule_path.read_text().splitlines()

    assert lines[0] == "# Main Wing Layup"
    step_rows = [
        line
        for line in lines
        if any(line.startswith(f"| {idx} |") for idx in range(1, 5))
    ]
    assert len(step_rows) == 4
    assert (
        step_rows[0]
        == '| 1 | Spar cap build: Lay 17 UNI plies in trough, maintaining 0.153" depth. | BUILDER | Layup left wing fiberglass skins (12.0%) |'
    )


def test_write_layup_schedule_unsupported_component_raises(
    trackers: Tuple[ComplianceTracker, ComplianceTaskTracker],
    tmp_path: Path,
) -> None:
    """write_layup_schedule raises ValueError mentioning 'canard and wing' for unsupported components."""
    _, task_tracker = trackers
    with pytest.raises(ValueError, match="canard and wing"):
        task_tracker.write_layup_schedule("fuselage", tmp_path / "schedules")


# --- added after mutation review (survivors: note overwrite, row order, latest-entry-wins, layup prose) ---

def test_repeat_record_with_a_note_overwrites_the_task_note(trackers) -> None:
    tracker, tt = trackers
    tt.record_generation("canard", "cad")
    tt.record_generation("canard", "cad", TaskRole.HELPER, "n2")
    assert tracker.get_task("canard_cores").notes == "n2"


def test_checklist_rows_are_sorted_by_task_id(trackers) -> None:
    _, tt = trackers
    rows = [ln for ln in tt.render_running_checklist().splitlines() if ln.startswith("| ") and "PENDING" in ln]
    assert [r.split(" | ")[0][2:] for r in rows] == [
        "Fabricate canard foam cores (Roncz R1145MS)",
        "Layup canard fiberglass skins",
        "Fabricate left wing foam cores",
        "Fabricate right wing foam cores",
        "Layup left wing fiberglass skins",
        "Layup right wing fiberglass skins",
    ]


def test_latest_entry_wins_in_the_rendered_row(trackers) -> None:
    _, tt = trackers
    tt.record_generation("canard", "cad", TaskRole.BUILDER)
    tt.record_generation("canard", "cad", TaskRole.HELPER)
    lines = tt.render_running_checklist().splitlines()
    assert "| Fabricate canard foam cores (Roncz R1145MS) | cad | helper | builder_helper | DONE | 2.5% |" in lines


def test_completed_task_without_an_entry_shows_the_tasks_own_method(trackers) -> None:
    tracker, tt = trackers
    tracker.complete_task("canard_cores", ManufacturingMethod.BUILDER_CNC)
    lines = tt.render_running_checklist().splitlines()
    row = next(ln for ln in lines if ln.startswith("| Fabricate canard foam cores"))
    assert "| — | builder | builder_cnc | DONE |" in row


def test_render_ends_with_newline_and_has_the_separator_row(trackers) -> None:
    _, tt = trackers
    text = tt.render_running_checklist()
    assert text.endswith("\n")
    assert "|------|----------|------|--------|--------|--------|" in text.splitlines()


def test_canard_layup_prose_is_exact(tmp_path: Path, trackers) -> None:
    _, tt = trackers
    content = tt.write_layup_schedule("canard", tmp_path).read_text()
    lines = content.splitlines()
    assert "| Step | Action | Operator | Credit Task |" in lines
    assert "Builder of record must perform the following layups to retain FAA builder credit." in lines
    assert "Repeat 2 plies BID at ±45°; peel-ply hinge line and spar cap step." in content
    assert "Install peel-ply and allow full cure before trimming trailing edge." in content
    assert "- Ensure builder name appears on shop traveler for each layup." in lines
    assert "- Helper-assisted work must be documented; credit is reduced automatically." in lines


def test_wing_layup_prose_is_exact(tmp_path: Path, trackers) -> None:
    _, tt = trackers
    content = tt.write_layup_schedule("wing", tmp_path).read_text()
    assert "BID at ±45° across panel; stagger overlaps by at least 1 in." in content
    assert "Mirror upper skin schedule; peel-ply control surface seams." in content
    assert "Maintain 140°F post-cure per epoxy data sheet before cutting control surfaces." in content
