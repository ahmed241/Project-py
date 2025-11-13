import argparse
import sys
import json
import numpy as np
import subprocess  # Used to call Manim
import os          # Used to get file paths
import shutil      # Used to move the final video file

# --- Import the solver logic ---
# We assume assignment_solver.py is in the same directory
try:
    from assignment_solver import AssignmentSolver
except ImportError:
    print(f"[ERROR] Could not import 'AssignmentSolver' from assignment_solver.py.", file=sys.stderr)
    sys.exit(1)

# --- Manim Helper Function ---
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
    
    # Manim saves to: media/videos/<script_name_no_ext>/<quality>/<scene_name>.mp4
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
    """Solves the problem directly using assignment_solver.py and writes a JSON output."""
    print("Solving Assignment problem (direct)...")
    
    output_payload = {}
    
    try:
        cost_matrix = np.array(input_data['tableData'])
        problem_type = input_data['problemType']
        
        # Call your solver
        solver = AssignmentSolver(cost_matrix, problem_type)
        solution = solver.solve()
        
        print(f"[SUCCESS] Solver finished.")
        # The 'solution' dict already has 'assignments', 'total_cost', etc.
        # We just add a top-level 'status' for the frontend.
        output_payload = {
            'status': 'success',
            'solution': solution
        }

    except Exception as e:
        print(f"[ERROR] An error occurred during calculation: {str(e)}", file=sys.stderr)
        output_payload['status'] = 'error'
        output_payload['message'] = str(e)
    
    finally:
        # Write the results or error to the output JSON file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_payload, f, indent=2)
                
            print(f"Results written to {output_file}")
            if output_payload.get('status') == 'error':
                 sys.exit(1) # Exit with error code if design failed
        except Exception as e:
            print(f"[CRITICAL-ERROR] Failed to write output JSON to {output_file}: {e}", file=sys.stderr)
            sys.exit(1)


def generate_video(input_data, output_video_path):
    """Generates a Manim video."""
    print("Starting Manim video generation process for Assignment Problem...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. --- Prepare Manim Input File (assignment_problem.json) ---
    # This is the file your animation.py will read
    manim_input_json = os.path.join(script_dir, "assignment_problem.json")
    
    # Format the data exactly as animation.py expects
    manim_data = {
        "matrix": input_data['tableData'],
        "type": input_data['problemType'],
        "restrictions": [] # You can add this to your frontend/model later
    }
    
    try:
        with open(manim_input_json, 'w', encoding='utf-8') as f:
            json.dump(manim_data, f, indent=2)
        print(f"Wrote user input to {manim_input_json}")
    except Exception as e:
        print(f"Error writing Manim input JSON: {e}", file=sys.stderr)
        raise

    # 2. --- Run the Manim Scene ---
    # Your animation.py has class MyScene
    video_path = _run_manim_scene("animation.py", "MyScene", script_dir)
    
    # 3. --- Move the final video ---
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
    """Main entry point for all Assignment Problem requests."""
    parser = argparse.ArgumentParser(description='Assignment Problem Solver')
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