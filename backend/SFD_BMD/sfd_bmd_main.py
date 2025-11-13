import argparse
import sys
import json
import numpy as np
import subprocess  # Used to call Manim
import os          # Used to get file paths
import shutil      # Used to move the final video file
import pandas as pd
from typing import List, Dict, Any

# --- Import your actual solver function ---
try:
    # We assume this file is in the same directory (SFD_BMD/)
    from sfd_bmd_solver import solve_beam_by_stiffness
except ImportError:
    print(f"[ERROR] Could not import 'solve_beam_by_stiffness' from sfd_bmd_solver.py.", file=sys.stderr)
    print("Please make sure sfd_bmd_solver.py is in the same directory.", file=sys.stderr)
    sys.exit(1)

# --- JSON Helper Function (for numpy/pandas types) ---
def to_native_types(obj):
    """
    Recursively converts numpy/pandas types to native Python types for JSON.
    """
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Series):
        return to_native_types(obj.to_dict())
    
    try:
        import sympy
        if isinstance(obj, sympy.Basic):
            return str(obj)
    except ImportError:
        pass 

    if isinstance(obj, dict):
        return {key: to_native_types(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [to_native_types(item) for item in obj]
    return obj

# --- Manim Helper Function (copied from your reference) ---
def _run_manim_scene(script_name, scene_name, cwd_dir):
    """
    Runs a specific Manim scene and handles errors.
    """
    animation_script_path = os.path.join(cwd_dir, script_name)
    
    # Command: manim -ql <script_name> <scene_name>
    manim_command = ["manim", "-ql", animation_script_path, scene_name, "--disable_caching"]
    
    print(f"Running command: {' '.join(manim_command)}")
    
    result = subprocess.run(manim_command, cwd=cwd_dir, capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        print("--- MANIM FAILED ---", file=sys.stderr)
        print("STDOUT:", result.stdout, file=sys.stdout)
        print("STDERR:", result.stderr, file=sys.stderr)
        raise Exception(f"Manim rendering for {script_name} failed. See stderr.")
    
    print(f"Manim render complete for {scene_name}")
    
    script_name_no_ext = os.path.splitext(script_name)[0]
    
    rendered_file_path = os.path.join(cwd_dir, "media", "videos", script_name_no_ext, "480p15", f"{scene_name}.mp4")

    if not os.path.exists(rendered_file_path):
        print(f"Warning: Could not find 480p file. Trying 720p30...", file=sys.stderr)
        rendered_file_path = os.path.join(cwd_dir, "media", "videos", script_name_no_ext, "720p30", f"{scene_name}.mp4")
        if not os.path.exists(rendered_file_path):
            print(f"Error: Could not find rendered file at {rendered_file_path}", file=sys.stderr)
            raise Exception("Manim rendered, but output file not found.")
            
    return rendered_file_path

# --- Solver Wrapper ---
def _call_solver(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the solver with default E and I values.
    Returns a combined dictionary of results.
    """
    # Get default E and I from your solver's test case
    # In the future, these can come from input_data
    E = input_data.get('E', 210e9) # Default 210 GPa
    I = input_data.get('I', 8.333e-6) # Default I
    
    # Call your solver
    solution_res, solution_forces = solve_beam_by_stiffness(
        beam_length=input_data['beamLength'],
        supports=input_data['supports'],
        loads=input_data['loads'],
        E=E,
        I=I
    )
    
    # Combine results into one dictionary
    solution_data = {
        "analysis_results": solution_res,
        "element_forces": solution_forces
    }
    return solution_data

# --- Main Generation Functions ---

def generate_direct_solution(input_data, output_file):
    """Solves the problem directly using sfd_bmd_solver.py and writes a JSON output."""
    print("Solving SFD/BMD problem (direct)...")
    
    output_payload = {}
    
    try:
        solution_data = _call_solver(input_data)
        
        print(f"[SUCCESS] Solver finished.")
        output_payload = {
            'status': 'success',
            'solution': solution_data
        }

    except Exception as e:
        print(f"[ERROR] An error occurred during calculation: {str(e)}", file=sys.stderr)
        output_payload['status'] = 'error',
        output_payload['message'] = str(e)
    
    finally:
        # Write the results or error to the output JSON file
        try:
            # Clean the payload of any NumPy/SymPy types
            final_payload = to_native_types(output_payload)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_payload, f, indent=2)
                
            print(f"Results written to {output_file}")
            if final_payload.get('status') == 'error':
                 sys.exit(1) # Exit with error code if design failed
        except Exception as e:
            print(f"[CRITICAL-ERROR] Failed to write output JSON to {output_file}: {e}", file=sys.stderr)
            sys.exit(1)


def generate_video(input_data, output_video_path):
    """Generates a Manim video by first solving, then animating."""
    print("Starting Manim video generation process for SFD/BMD...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # --- Step 1: Solve the problem to get data for Manim ---
    try:
        solution_data = _call_solver(input_data)
    except Exception as e:
        print(f"[ERROR] Solver failed, cannot generate video: {str(e)}", file=sys.stderr)
        raise # Re-raise exception to be caught by main()
    
    # --- Step 2: Prepare Manim Input File (sfd_bmd_data.json) ---
    # This file will be read by your sfd_bmd_animation.py
    manim_input_json = os.path.join(script_dir, "sfd_bmd_data.json")
    
    # This payload includes the inputs AND the solution data
    manim_data = {
        "inputs": input_data,
        "solution": solution_data
    }
    
    try:
        # Clean data for JSON
        manim_data_clean = to_native_types(manim_data)
        with open(manim_input_json, 'w', encoding='utf-8') as f:
            json.dump(manim_data_clean, f, indent=2)
        print(f"Wrote solver data to {manim_input_json} for Manim")
    except Exception as e:
        print(f"Error writing Manim input JSON: {e}", file=sys.stderr)
        raise

    # --- Step 3: Run the Manim Scene ---
    # We assume your animation file is 'sfd_bmd_animation.py'
    # and the scene class is 'SFDBMDScene'
    video_path = _run_manim_scene("sfd_bmd_animation.py", "SFDBMDScene", script_dir)
    
    # --- Step 4: Move the final video ---
    shutil.move(video_path, output_video_path)
    print(f"Manim video moved to {output_video_path}")


def generate_pdf_report(input_data, output_file):
    """Generates a PDF report (placeholder)."""
    print(f"PDF generation logic for {output_file} goes here.")
    output_payload = {
        'status': 'error',
        'message': 'PDF generation not yet implemented.'
    }
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_payload, f, indent=2)
    except Exception as e:
        print(f"[CRITICAL-ERROR] Failed to write PDF placeholder: {e}", file=sys.stderr)
    print("Placeholder PDF report generated.")


# --- Main Execution ---
def main():
    """Main entry point for all SFD/BMD requests."""
    parser = argparse.ArgumentParser(description='SFD/BMD Solver')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--type', required=True, choices=['video', 'pdf', 'direct'], help='Output type')
    
    args = parser.parse_args()
    
    try:
        # Read the user's temporary input file
        with open(args.input, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # --- Use match case for output type ---
        match args.type:
            case 'direct':
                generate_direct_solution(input_data, args.output)
            
            case 'video':
                generate_video(input_data, args.output)
                print(f"Video process complete. Final file at: {args.output}")

            case 'pdf':
                generate_pdf_report(input_data, args.output)
            
            case _:
                print(f"Error: Unknown output type '{args.type}'", file=sys.stderr)
                sys.exit(1)

    except Exception as e:
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        
        # --- ROBUST ERROR-WRITING BLOCK ---
        error_output_path = os.path.splitext(args.output)[0] + ".json"
        
        error_message = f"Python script failed: {str(e)}"
        try:
            safe_message = str(e).encode('utf-8', 'ignore').decode('utf-8')
            error_message = f"Python script failed: {safe_message}"
            if len(error_message) > 1000:
                 error_message = error_message[:1000] + "... (error truncated)"
        except Exception:
            pass # Use the default message

        try:
            with open(error_output_path, 'w', encoding='utf-8') as f:
                json.dump({'status': 'error', 'message': error_message}, f, indent=2)
            print(f"Error JSON written to {error_output_path}")
        except Exception as e2:
            print(f"[CRITICAL-ERROR] Failed to write error JSON: {e2}", file=sys.stderr)
            
        sys.exit(1) # Ensure we exit with a failure code

if __name__ == '__main__':
    main()