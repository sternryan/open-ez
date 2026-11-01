"""Build groups: file order, required files, and the stub / GU exemptions."""

import shutil
import textwrap
from pathlib import Path

import pytest

from guide.schema import SchemaError, load_graph, validate
from tests.guide.test_schema import gdir as _schema_gdir
from tests.guide.test_schema import write

gdir = pytest.fixture(_schema_gdir.__wrapped__)

ROOT = Path(__file__).resolve().parents[2]


def test_groups_keep_file_order(gdir):
    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: bulkheads-firewall, label: "Seat bulkheads and firewall"}
          - {id: fuselage-sides, label: "Fuselage sides"}
        required_files: [ch04.yaml, ch05.yaml]
        """,
    )
    text = (gdir / "ch10.yaml").read_text()
    text = text.replace(
        "  title: Cut the foam cores\n",
        "  title: Cut the foam cores\n  group: fuselage-sides\n",
        1,
    )
    (gdir / "ch10.yaml").write_text(text)
    g = load_graph(gdir)
    assert [(grp.id, grp.label) for grp in g.groups] == [
        ("bulkheads-firewall", "Seat bulkheads and firewall"),
        ("fuselage-sides", "Fuselage sides"),
    ]
    assert g.groups_required == {"ch04.yaml", "ch05.yaml"}
    assert g.ops["c10.cores"].group == "fuselage-sides"
    assert g.ops["c10.cores"].file == "ch10.yaml"
    assert validate(g) == []


def test_required_op_missing_group(gdir):
    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: canard, label: Canard}
        required_files: [ch10.yaml]
        """,
    )
    (gdir / "ch10.yaml").write_text(
        (gdir / "ch10.yaml").read_text()
        + textwrap.dedent(
            """
            - id: c10.roncz-skin
              chapter: 10
              title: Skin the canard
              summary: Skin the Roncz canard.
              variants: [roncz]
              sources: [{doc: scan-1980, scan_pp: 58}]
              completion: [Skinned]
            """
        )
    )
    errs = validate(load_graph(gdir))
    assert "c10.roncz-skin: missing group" in errs


def test_unknown_group(gdir):
    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: canard, label: Canard}
        required_files: []
        """,
    )
    text = (
        (gdir / "ch10.yaml")
        .read_text()
        .replace(
            "  title: Cut the foam cores\n",
            "  title: Cut the foam cores\n  group: nope\n",
            1,
        )
    )
    (gdir / "ch10.yaml").write_text(text)
    errs = validate(load_graph(gdir))
    assert "c10.cores: group 'nope' not in groups.yaml" in errs


def test_duplicate_group(gdir):
    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: canard, label: Canard}
          - {id: canard, label: Canard again}
        required_files: []
        """,
    )
    errs = validate(load_graph(gdir))
    assert "groups.yaml: duplicate group canard" in errs


def test_stub_and_gu_only_are_exempt(gdir):
    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: canard, label: Canard}
        required_files: [ch10.yaml]
        """,
    )
    (gdir / "ch10.yaml").write_text(
        (gdir / "ch10.yaml").read_text()
        + textwrap.dedent(
            """
            - id: c10.mixed
              chapter: 10
              title: Mixed variants
              summary: Not a single-variant GU step.
              variants: [gu, roncz]
              sources: [{doc: scan-1980, scan_pp: 58}]
              completion: [Noted]
            - id: c10.roncz-skin
              chapter: 10
              title: Skin the canard
              summary: Skin the Roncz canard.
              variants: [both]
              sources: [{doc: scan-1980, scan_pp: 58}]
              completion: [Skinned]
            """
        )
    )
    errs = validate(load_graph(gdir))
    assert "c03.layup-skills: missing group" not in errs
    assert "c10.cores: missing group" not in errs
    assert "c10.twist-check: missing group" not in errs
    assert "c10.mixed: missing group" in errs
    assert "c10.roncz-skin: missing group" in errs


def test_unknown_group_on_a_stub_still_fails(gdir):
    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: canard, label: Canard}
        required_files: [ch10.yaml]
        """,
    )
    text = (
        (gdir / "ch10.yaml")
        .read_text()
        .replace(
            "  title: Composite layup skills\n  stub: true\n",
            "  title: Composite layup skills\n  stub: true\n  group: nope\n",
            1,
        )
    )
    (gdir / "ch10.yaml").write_text(text)
    errs = validate(load_graph(gdir))
    assert "c03.layup-skills: group 'nope' not in groups.yaml" in errs
    assert "c03.layup-skills: missing group" not in errs


def test_fixture_without_groups_loads_empty(gdir):
    g = load_graph(gdir)
    assert g.groups == []
    assert g.groups_required == set()
    assert validate(g) == []
    assert all(op.group is None and op.plan is None for op in g.ops.values())
    assert {op.file for op in g.ops.values()} == {"ch10.yaml"}


def test_scripts_yaml_is_not_an_op_file(gdir):
    (gdir / "scripts.yaml").write_text("scripts: {}\n")
    g = load_graph(gdir)
    assert validate(g) == []
    assert all(op.file != "scripts.yaml" for op in g.ops.values())


def test_groups_yaml_unknown_key_raises(gdir):
    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: canard, label: Canard, order: 1}
        required_files: []
        """,
    )
    with pytest.raises(SchemaError, match="unknown key"):
        load_graph(gdir)


def _real_graph(tmp_path):
    dest = tmp_path / "graph"
    shutil.copytree(ROOT / "guide" / "graph", dest)
    return load_graph(dest)


def _needs_group(op) -> bool:
    """Player steps. Stubs and GU-only ops are exempt from the one-group rule."""
    return not op.stub and op.variants != ("gu",)


def test_every_roncz_step_grouped_once(tmp_path):
    g = _real_graph(tmp_path)
    chapters = {p.name for p in (ROOT / "guide" / "graph").glob("ch*.yaml")}
    assert g.groups_required == chapters
    for op in g.ops.values():
        if not _needs_group(op):
            continue
        assert sum(grp.id == op.group for grp in g.groups) == 1, op.id


def test_groups_respect_dag(tmp_path):
    g = _real_graph(tmp_path)
    rank = {grp.id: i for i, grp in enumerate(g.groups)}

    def grouped(op) -> bool:
        return op.group in rank

    for op in g.ops.values():
        for req_id in op.requires:
            req = g.ops[req_id]
            if not grouped(req):
                continue
            assert grouped(op), f"{op.id} requires grouped {req.id} but has no group"
            assert (
                rank[req.group] <= rank[op.group]
            ), f"{op.id} ({op.group}) requires {req.id} ({req.group})"


def test_real_graph_assigns_first_stretch_groups(tmp_path):
    g = _real_graph(tmp_path)
    # P3-A: "g00.* IDs in ground-school, first group"
    assert [(grp.id, grp.label) for grp in g.groups][:2] == [
        ("ground-school", "Ground school"),
        ("bulkheads-firewall", "Seat bulkheads and firewall"),
    ]
    assert {"ch04.yaml", "ch05.yaml"} <= g.groups_required
    ch04 = [op for op in g.ops.values() if op.file == "ch04.yaml"]
    ch05 = [op for op in g.ops.values() if op.file == "ch05.yaml"]
    assert len(ch04) == 8 and {op.group for op in ch04} == {"bulkheads-firewall"}
    assert len(ch05) == 9 and {op.group for op in ch05} == {"fuselage-sides"}
    assert all(op.plan is not None for op in ch04 + ch05)
    assert validate(g) == []
