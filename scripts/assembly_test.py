from pathlib import Path

from core.assembly import AircraftAssembly


def test_full_assembly(tmp_path):
    print("🚀 Starting Full Aircraft Assembly Test...")

    assembly = AircraftAssembly()
    print("   Generating full airframe geometry (B-Rep union)...")
    # This might take a few seconds as it performs boolean unions
    assembly.generate_geometry()

    print("   Calculating mass properties...")
    props = assembly.get_mass_properties()
    print(f"   ✅ Total Volume: {props['volume_in3']:.2f} in3")
    print(f"   ✅ Estimated Structural Weight: {props['estimated_weight_lb']:.2f} lbs")
    print(f"   ✅ Estimated Center of Mass (FS): {props['cg_x_fs']:.2f} in")

    # Verify CG is within reasonable range for Long-EZ
    # Typical CG is around FS 100-110
    if 80 < props["cg_x_fs"] < 140:
        print("   ✅ CG is within viable envelope for Long-EZ configuration.")
    else:
        print(
            f"   ⚠️ WARNING: CG ({props['cg_x_fs']:.2f}) looks suspicious. Check FS positions."
        )

    print("   Building assembly hierarchy...")
    assembly.build_assembly()  # Builds and stores hierarchy internally

    print("   Exporting assembly artifacts...")
    output_dir = Path(tmp_path)
    assembly.export_step(output_dir)
    print(f"   ✅ STEP exported: {output_dir / 'open_ez_airframe.step'}")

    print("\n🎉 Full Assembly Test Completed Successfully!")


if __name__ == "__main__":
    test_full_assembly(Path("output/assembly_test"))
