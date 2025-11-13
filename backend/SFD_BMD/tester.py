#!/usr/bin/env python3
"""
Quick CLI test runner for sfd_bmd_solver.solve_sfd_bmd.

Usage:
    python test_runner.py
"""
import json
import sys
from pprint import pprint

# Import your solver (assumes test_runner.py sits next to sfd_bmd_solver.py)
from sfd_bmd_solver import solve_sfd_bmd

# ------------- 1) Raw data exactly as you posted -------------
raw_data = {
    "beamLength": 10.0,
    "supports": [
        {"id": "support-1762958934939", "type": "pin", "position": 0},
        {"id": "support-1762958939645", "type": "pin", "position": 10}
    ],
    "loads": [
        {"id": "load-1762958817467", "type": "point", "position": 5, "magnitude": 10, "angle": 270}
    ],
    "outputType": "direct"
}

# ------------- 2) Corrected data (one pin + one roller) -------------
corrected_data = {
    "beamLength": raw_data["beamLength"],
    "supports": [
        {"id": "support-1762958934939", "type": "pin", "position": 0},
        # change the second support type to roller so your current solver can handle it
        {"id": "support-1762958939645", "type": "roller", "position": 10}
    ],
    "loads": raw_data["loads"],
    "outputType": "direct"
}

def run_case(case_name: str, data: dict):
    print("\n" + "="*60)
    print(f"Running case: {case_name}")
    print("="*60)
    try:
        results = solve_sfd_bmd(
            beam_length = float(data["beamLength"]),
            supports = data["supports"],
            loads = data["loads"]
        )
        print("\nSolver returned results (top-level keys):")
        pprint(list(results.keys()))
        # print a short summary
        print("\nSummary:")
        print(f"  max_moment: {results.get('max_moment')}")
        print(f"  min_moment: {results.get('min_moment')}")
        print(f"  max_shear: {results.get('max_shear')}")
        print(f"  min_shear: {results.get('min_shear')}")
        print("\nReactions:")
        pprint(results.get("reactions"))
        # Optionally write the SFD/BMD arrays to files for inspection
        with open(f"sfd_{case_name}.json", "w") as f:
            json.dump(results.get("sfd_points", []), f, indent=2)
        with open(f"bmd_{case_name}.json", "w") as f:
            json.dump(results.get("bmd_points", []), f, indent=2)
        print(f"\nWrote sfd_{case_name}.json and bmd_{case_name}.json")
    except Exception as e:
        print(f"[ERROR] Solver raised an exception for case '{case_name}':\n  {e}", file=sys.stderr)

if __name__ == "__main__":
    # 1) Run raw (original) data
    # run_case("original_raw", raw_data)

    # 2) Run corrected (pin+roller)
    run_case("corrected_pin_roller", corrected_data)

    print("\nAll done.")
