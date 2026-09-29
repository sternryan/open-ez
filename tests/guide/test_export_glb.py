"""Test glb export with component-ID node names."""
import cadquery as cq
from guide.export_glb import export_components, read_glb_node_names


def test_node_names_are_component_ids(tmp_path):
    out = export_components(
        {
            "canard.core": cq.Workplane().box(10, 2, 1),
            "canard.spar_cap_top": cq.Workplane().box(10, 1, 0.1),
        },
        tmp_path / "t.glb",
    )
    names = read_glb_node_names(out)
    assert "canard.core" in names and "canard.spar_cap_top" in names
    assert out.read_bytes()[:4] == b"glTF"
