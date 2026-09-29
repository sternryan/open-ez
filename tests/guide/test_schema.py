from pathlib import Path
import textwrap
import pytest
from guide.schema import load_graph, validate, topo_order, authored_texts, SchemaError

def write(d: Path, name: str, body: str):
    (d / name).write_text(textwrap.dedent(body))

@pytest.fixture
def gdir(tmp_path):
    write(tmp_path, "components.yaml", """
        - {id: canard.core, label: Canard foam core, fidelity: unvalidated}
        - {id: canard.spar_cap_bottom, label: Bottom spar cap, fidelity: no-geometry}
    """)
    write(tmp_path, "pages.yaml", """
        58: "10-5"
        59: "10-6"
    """)
    write(tmp_path, "annotations.yaml", """
        - {scan_pp: 58, cp: 25, lpc: 16, class: MEO, text: "WL 19.4 not centerline", confirmed: true}
    """)
    write(tmp_path, "ch10.yaml", """
        - id: c03.layup-skills
          chapter: 3
          title: Composite layup skills
          stub: true
        - id: c10.cores
          chapter: 10
          title: Cut the foam cores
          summary: Hot-wire the four canard cores from the templates.
          variants: [gu]
          requires: [c03.layup-skills]
          components: [canard.core]
          geometry_visible: true
          sources: [{doc: scan-1980, scan_pp: 58}]
          changes:
            - {cp: 25, lpc: 16, class: MEO, status: verified, kind: official, note: Shear web line moves to WL 19.4., annotation_pp: 58}
          completion: [Four cores cut and labeled]
        - id: c10.twist-check
          chapter: 10
          title: Check for twist
          summary: Level the jigged cores and confirm zero twist before skinning.
          variants: [gu]
          requires: [c10.cores]
          components: []
          geometry_visible: false
          inspection: true
          sources: [{doc: scan-1980, scan_pp: 59}]
          completion: [Incidence matches at both ends]
    """)
    return tmp_path

def test_valid_graph_has_no_errors(gdir):
    g = load_graph(gdir)
    assert validate(g) == []
    assert topo_order(g) == ["c03.layup-skills", "c10.cores", "c10.twist-check"]

def test_unknown_requires_and_component(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("requires: [c10.cores]", "requires: [c10.nope]").replace("components: [canard.core]", "components: [canard.ghost]"))
    errs = validate(load_graph(gdir))
    assert any("c10.twist-check" in e and "c10.nope" in e for e in errs)
    assert any("canard.ghost" in e for e in errs)

def test_cycle_detected(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("requires: [c03.layup-skills]", "requires: [c10.twist-check]"))
    assert any("cycle" in e for e in validate(load_graph(gdir)))

def test_duplicate_id_raises(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text() + "\n- {id: c10.cores, chapter: 10, title: dup, stub: true}\n")
    with pytest.raises(SchemaError, match="duplicate"):
        load_graph(gdir)

def test_scan_page_must_be_mapped(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("scan_pp: 59", "scan_pp: 99"))
    assert any("scan_pp 99" in e for e in validate(load_graph(gdir)))

def test_confirmed_annotation_must_be_linked(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("lpc: 16, class: MEO, status: verified", "lpc: 99, class: MEO, status: verified"))
    assert any("annotation" in e and "LPC 16" in e for e in validate(load_graph(gdir)))

def test_bad_enums(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("variants: [gu]\n  requires: [c03", "variants: [vari]\n  requires: [c03").replace("status: verified", "status: maybe"))
    errs = validate(load_graph(gdir))
    assert any("vari" in e for e in errs) and any("maybe" in e for e in errs)

def test_non_stub_needs_summary_source_completion(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("completion: [Four cores cut and labeled]", "completion: []"))
    assert any("c10.cores" in e and "completion" in e for e in validate(load_graph(gdir)))

def test_authored_texts_excludes_annotations(gdir):
    locs = [loc for loc, _ in authored_texts(load_graph(gdir))]
    assert "c10.cores.summary" in locs and "c10.cores.changes[0].note" in locs
    assert not any(loc.startswith("annotation") for loc in locs)
