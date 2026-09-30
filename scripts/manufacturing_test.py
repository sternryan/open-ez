from pathlib import Path
from core.structures import CanardGenerator
from core.manufacturing import GCodeEngine, JigFactory
from config import config


def test_manufacturing_pipeline(tmp_path):
    """Run the canard manufacturing chain; write everything under tmp_path.

    Under pytest, tmp_path is a throwaway directory so the suite never rewrites
    tracked files. Run as a script, it writes to output/test_mfg (gitignored).
    """
    out_root = Path(tmp_path)
    print("🚀 Starting Manufacturing Pipeline Test...")

    # 1. Initialize Canard (Safety Critical)
    print("   Creating Canard core...")
    canard = CanardGenerator()
    canard.generate_geometry()

    # 2. Add Spar Troughs
    print("   Cutting spar troughs...")
    canard.cut_spar_trough()

    # 3. Use GCodeEngine to generate manufacturing output
    print("   Generating G-Code via GCodeEngine...")
    engine = GCodeEngine(output_root=out_root)
    gcode_path = engine.generate_component_gcode(canard, foam_name="styrofoam_blue")
    print(f"   ✅ G-Code generated: {gcode_path}")

    # 4. Generate Jigs
    print("   Generating assembly jigs...")
    jig_dir = out_root / "jigs"
    jig_dir.mkdir(parents=True, exist_ok=True)

    # Root cradle
    cradle = JigFactory.generate_incidence_cradle(
        canard, station_bl=0.0, incidence_angle=config.geometry.canard_incidence
    )
    import cadquery as cq

    cq.exporters.export(cradle, str(jig_dir / "canard_root_jig.stl"))
    print(f"   ✅ Jig generated: {jig_dir / 'canard_root_jig.stl'}")

    # 5. Export DXF
    print("   Exporting DXF templates...")
    dxf_path = canard.export_dxf(out_root / "dxf")
    print(f"   ✅ DXF templates exported: {dxf_path}")

    print("\n🎉 Manufacturing Pipeline Test Completed Successfully!")


if __name__ == "__main__":
    test_manufacturing_pipeline(Path("output/test_mfg"))
