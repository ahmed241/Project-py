import argparse
import sys
import json
import numpy as np
import pandas as pd
import subprocess  # Used to call Manim
import os          # Used to get file paths
import shutil      # Used to move the final video file
import math

# Import the solver logic
from EOT_solver import design_eot_crane

# --- JSON Helper Function ---
def to_native_types(obj):
    # (Your to_native_types function is unchanged)
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Series):
        return to_native_types(obj.to_dict())
    if isinstance(obj, dict):
        return {key: to_native_types(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [to_native_types(item) for item in obj]
    return obj

# --- Manim Helper Function ---
def _run_manim_scene(script_name, scene_name, cwd_dir):
    # (Your _run_manim_scene function is unchanged)
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

# --- Main Generation Functions ---

def generate_direct_solution(input_data, output_file):
    # (This function is unchanged)
    print("Solving EOT Crane problem (direct)...")
    output_payload = {}
    try:
        load_val = float(input_data['load'])
        load_unit = input_data.get('loadUnit', 'tonnes').lower()
        if load_unit == 'tonnes': load_for_function = load_val
        elif load_unit == 'kg': load_for_function = load_val / 1000.0
        else: raise ValueError(f"Unsupported load unit: {load_unit}")
        
        speed_val = float(input_data['speed'])
        speed_unit = input_data.get('speedUnit', 'm/min').lower()
        if speed_unit == 'm/min': speed_for_function = speed_val
        elif speed_unit == 'm/s': speed_for_function = speed_val * 60.0
        else: raise ValueError(f"Unsupported speed unit: {speed_unit}")

        height_for_function = float(input_data['liftHeight'])
        if height_for_function <= 0: raise ValueError("liftHeight must be a positive value")
            
        design_results = design_eot_crane(
            load_tonnes=load_for_function,
            lift_height=height_for_function,
            hoist_speed=speed_for_function
        )
        
        if design_results:
            print("[SUCCESS] Design completed successfully.")
            output_payload['status'] = 'success'
            output_payload['results'] = to_native_types(design_results)
        else:
            print("[ERROR] Design failed.")
            output_payload['status'] = 'error'
            output_payload['message'] = 'Failed to find suitable components. Check console logs.'

    except Exception as e:
        print(f"[ERROR] An error occurred during calculation: {str(e)}", file=sys.stderr)
        output_payload['status'] = 'error'
        output_payload['message'] = str(e)
    
    finally:
        # This function ALWAYS writes its output JSON
        try:
            with open(output_file, 'w') as f:
                json.dump(output_payload, f, indent=2)
            print(f"Results written to {output_file}")
            if output_payload.get('status') == 'error':
                 sys.exit(1) 
        except Exception as e:
            print(f"[CRITICAL-ERROR] Failed to write output JSON to {output_file}: {e}", file=sys.stderr)
            sys.exit(1)


def generate_video(input_data, output_video_path):
    # (This function is unchanged)
    print("Starting Manim video generation process for EOT Crane...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manim_input_json = os.path.join(script_dir, "data.json")
    
    manim_data = {
        "load": input_data.get('load'),
        "speed": input_data.get('speed'),
        "lift": input_data.get('liftHeight')
    }
    
    try:
        with open(manim_input_json, 'w') as f:
            json.dump(manim_data, f, indent=2)
        print(f"Wrote user input to {manim_input_json}")
    except Exception as e:
        print(f"Error writing Manim input JSON: {e}", file=sys.stderr)
        raise

    video_path = _run_manim_scene("animation.py", "DesignScene", script_dir)
    shutil.move(video_path, output_video_path)
    print(f"Manim video moved to {output_video_path}")


def generate_pdf_report(input_data, output_file):
    # (This function is unchanged)
    print(f"PDF generation logic for {output_file} goes here.")
    with open(output_file, 'w') as f:
        f.write(json.dumps({
            'status': 'error',
            'message': 'PDF generation not yet implemented.'
        }))
    print("Placeholder PDF report generated.")


# --- Main Execution ---

def main():
    """Main entry point for all EOT Crane requests."""
    parser = argparse.ArgumentParser(description='EOT Crane Problem Solver')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--type', required=True, choices=['video', 'pdf', 'direct'], help='Output type')
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as f:
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
        print(f"Error: {str(e)}", file=sys.stderr)
        
        # --- ROBUST ERROR-WRITING BLOCK ---
        
        # 1. Define the error file path
        error_output_path = os.path.splitext(args.output)[0] + ".json"
        
        # 2. Create a default, safe error message
        error_message = "Python script failed. Check server logs (stderr) for the full traceback."
        
        try:
            # 3. Try to create a safe, truncated message from the real error
            safe_message = str(e).encode('utf-8', 'ignore').decode('utf-8')
            error_message = f"Python script failed: {safe_message}"
            if len(error_message) > 1000: # Truncate long Manim errors
                 error_message = error_message[:1000] + "... (error truncated)"
        except Exception:
            pass # If this fails, we'll just use the default message

        try:
            # 4. Write the safe message to the error JSON
            with open(error_output_path, 'w', encoding='utf-8') as f:
                json.dump({'status': 'error', 'message': error_message}, f, indent=2)
            print(f"Error JSON written to {error_output_path}")
            
        except Exception as e2:
            # If this STILL fails (e.g., permissions), we can't do much else
            print(f"[CRITICAL-ERROR] Failed to write error JSON: {e2}", file=sys.stderr)
            
        sys.exit(1) # Ensure we exit with a failure code

if __name__ == '__main__':
    main()