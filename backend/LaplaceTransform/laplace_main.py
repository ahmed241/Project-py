import argparse
import sys
import json
import numpy as np
import pandas as pd
import subprocess
import os
import shutil
import re

# --- FIX 1: Import the new, correct solver function ---
try:
    from laplace_solver import solve_step_by_step
except ImportError:
    print(f"[ERROR] Could not import 'solve_laplace' from laplace_solver.py.", file=sys.stderr)
    sys.exit(1)


# --- JSON Helper Function (Unchanged) ---
def to_native_types(obj):
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

# --- Manim Helper Function (Unchanged) ---
def _run_manim_scene(script_name, scene_name, cwd_dir):
    animation_script_path = os.path.join(cwd_dir, script_name)
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

# --- Helper to parse LaTeX (Unchanged, but I'm renaming it) ---
def parse_latex_input(latex_full: str) -> str:
    try:
        parts = latex_full.split('=')
        if len(parts) > 1:
            return parts[1].strip()
        else:
            return latex_full.strip()
    except Exception as e:
        print(f"Warning: Could not parse LaTeX input '{latex_full}'. Using as-is. Error: {e}")
        return latex_full

# --- Main Generation Functions ---

def generate_direct_solution(input_data, output_file):
    """Solves the problem directly using laplace_solver.py and writes a JSON output."""
    print("Solving Laplace problem (direct)...")
    
    output_payload = {}
    
    try:
        latex_input_full = input_data['latex']
        operation = input_data['operation']
        
        # Parse the input to get just the function
        # (This uses the sympify parser, not the regex one)
        # We don't need to parse, the new solver does it!
        
        # --- FIX 2: Call the new 'solve_laplace' function ---
        result_dict = solve_step_by_step(latex_input_full)

        # --- FIX 3: Check for 'status' == 'success' ---
        if result_dict["status"] == "success":
            print(f"[SUCCESS] Solver finished.")
            # The result_dict already has the correct format
            output_payload = result_dict 
        else:
            print(f"[ERROR] Solver returned an error.")
            output_payload['status'] = 'error'
            output_payload['message'] = result_dict['message']

    except Exception as e:
        print(f"[ERROR] An error occurred during calculation: {str(e)}", file=sys.stderr)
        output_payload['status'] = 'error'
        output_payload['message'] = str(e)
    
    finally:
        try:
            final_payload = to_native_types(output_payload)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_payload, f, indent=2)
            print(f"Results written to {output_file}")
            if final_payload.get('status') == 'error':
                 sys.exit(1)
        except Exception as e:
            print(f"[CRITICAL-ERROR] Failed to write output JSON to {output_file}: {e}", file=sys.stderr)
            sys.exit(1)


def generate_video(input_data, output_video_path):
    """Generates a Manim video by first solving, then animating."""
    print("Starting Manim video generation process for Laplace...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # --- Step 1: Solve the problem to get data for Manim ---
    latex_input_full = input_data['latex']
    operation = input_data['operation']
    
    if operation == 'inverse':
        print("Warning: Inverse Laplace animation may not be fully supported by animation.py.")
    
    # --- FIX 4: Call the new 'solve_laplace' function ---
    result_dict = solve_step_by_step(latex_input_full)

    # --- FIX 5: Check for 'status' == 'success' ---
    if result_dict["status"] != "success":
        raise Exception(f"Solver failed: {result_dict['message']}")

    # --- Step 2: Prepare Manim Input File (data.json) ---
    # Your animation.py expects 'inputLatex', 'outputLatex', etc.
    manim_data = {
        "inputLatex": latex_input_full,    # Pass the full f(t) = ...
        "outputLatex": result_dict['result'], # The final answer, e.g., "\frac{2}{s^3}"
        "showSteps": True,
        "steps": result_dict['steps']       # The list of steps
    }
    
    manim_input_json = os.path.join(script_dir, "data.json")
    
    try:
        with open(manim_input_json, 'w', encoding='utf-8') as f:
            json.dump(manim_data, f, indent=2)
        print(f"Wrote solver data to {manim_input_json} for Manim")
    except Exception as e:
        print(f"Error writing Manim input JSON: {e}", file=sys.stderr)
        raise

    # --- Step 3: Run the Manim Scene ---
    video_path = _run_manim_scene("animation.py", "LaplaceTransformScene", script_dir)
    
    # --- Step 4: Move the final video ---
    shutil.move(video_path, output_video_path)
    print(f"Manim video moved to {output_video_path}")


def generate_pdf_report(input_data, output_file):
    # (Unchanged)
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


# --- Main Execution (Unchanged) ---
def main():
    parser = argparse.ArgumentParser(description='Laplace Transform Solver')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--type', required=True, choices=['video', 'pdf', 'direct'], help='Output type')
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
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
        error_output_path = os.path.splitext(args.output)[0] + ".json"
        error_message = f"Python script failed: {str(e)}"
        try:
            safe_message = str(e).encode('utf-8', 'ignore').decode('utf-8')
            error_message = f"Python script failed: {safe_message}"
            if len(error_message) > 1000:
                 error_message = error_message[:1000] + "... (error truncated)"
        except Exception:
            pass
        try:
            with open(error_output_path, 'w', encoding='utf-8') as f:
                json.dump({'status': 'error', 'message': error_message}, f, indent=2)
            print(f"Error JSON written to {error_output_path}")
        except Exception as e2:
            print(f"[CRITICAL-ERROR] Failed to write error JSON: {e2}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()