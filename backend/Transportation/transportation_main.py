import argparse
import sys
import json
import numpy as np
import subprocess  # Used to call Manim
import os          # Used to get file paths
import shutil      # Used to move the final video file

# Import the solver logic from your other files
from VAM_solver import solve_vam, max_to_min, balance_problem
from MODI_solver import solve_MODI, calculate_final_cost, check_degeneracy, find_min_cost_unallocated, add_epsilon_allocations, u_v_calculation, calculate_opportunity_costs, check_optimality, find_loop, adjust_allocations

# --- Manim Helper Functions ---

def _run_manim_scene(script_name, scene_name, cwd_dir):
    """
    Runs a specific Manim scene and handles errors.
    """
    animation_script_path = os.path.join(cwd_dir, script_name)
    
    # Command: manim -pql <script_name> <scene_name>
    # -q (quality) l (low).
    manim_command = ["manim", "-ql", animation_script_path, scene_name, "--disable_caching"]
    
    print(f"Running command: {' '.join(manim_command)}")
    
    # Run from the `backend/Transportation` directory
    result = subprocess.run(manim_command, cwd=cwd_dir, capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        print("--- MANIM FAILED ---", file=sys.stderr)
        print("STDOUT:", result.stdout, file=sys.stdout)
        print("STDERR:", result.stderr, file=sys.stderr)
        raise Exception(f"Manim rendering for {script_name} failed. See stderr.")
    
    print(f"Manim render complete for {scene_name}")
    
    # --- Find Rendered File ---
    script_name_no_ext = os.path.splitext(script_name)[0]
    
    # Manim saves to: media/videos/<script_name_no_ext>/<quality>/<scene_name>.mp4
    rendered_file_path = os.path.join(cwd_dir, "media", "videos", script_name_no_ext, "480p15", f"{scene_name}.mp4")

    if not os.path.exists(rendered_file_path):
        # Fallback for 720p
        print(f"Warning: Could not find 480p file. Trying 720p30...", file=sys.stderr)
        rendered_file_path = os.path.join(cwd_dir, "media", "videos", script_name_no_ext, "720p30", f"{scene_name}.mp4")
        if not os.path.exists(rendered_file_path):
            print(f"Error: Could not find rendered file at {rendered_file_path}", file=sys.stderr)
            raise Exception("Manim rendered, but output file not found.")
            
    return rendered_file_path

def _stitch_videos(video_paths, output_path, cwd_dir):
    """
    Uses ffmpeg to concatenate multiple video files into one.
    """
    print(f"Stitching {len(video_paths)} videos into {output_path}...")
    
    # Create a temporary file list for ffmpeg
    file_list_path = os.path.join(cwd_dir, "file_list.txt")
    
    with open(file_list_path, 'w', encoding='utf-8') as f:
        for path in video_paths:
            # ffmpeg requires forward slashes, even on Windows
            ffmpeg_path = path.replace(os.sep, '/')
            f.write(f"file '{ffmpeg_path}'\n")
            
    # Run ffmpeg command
    ffmpeg_command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", file_list_path,
        "-c", "copy", # Fast stitching, no re-encoding
        output_path
    ]
    
    print(f"Running command: {' '.join(ffmpeg_command)}")
    result = subprocess.run(ffmpeg_command, cwd=cwd_dir, capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        print("--- FFMPEG STITCHING FAILED ---", file=sys.stderr)
        print("STDOUT:", result.stdout, file=sys.stdout)
        print("STDERR:", result.stderr, file=sys.stderr)
        raise Exception("Failed to stitch videos.")
        
    # Clean up temporary files
    os.remove(file_list_path)
    for path in video_paths:
        os.remove(path)
        
    print("Stitching complete.")

# --- Main Generation Functions ---

def generate_video(input_data, output_video_path, solution_type):
    """
    Generates a Manim video by:
    1. Writing the user's data to 'transportation_problem.json'.
    2. Dynamically selecting the correct Manim script(s) to run.
    3. Stitching videos if 'both' is requested.
    4. Moving the final video to the public/outputs path.
    """
    print("Starting Manim video generation process...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. --- Prepare Manim Input File ---
    manim_input_json = os.path.join(script_dir, "transportation_problem.json")
    
    manim_data = {
        "costs": input_data['costMatrix'],
        "supply": input_data['supply'],
        "demand": input_data['demand'],
        "problemType": input_data['problemType'],
        "solutionType": solution_type 
    }
    
    try:
        with open(manim_input_json, 'w') as f:
            json.dump(manim_data, f, indent=2)
        print(f"Wrote user input to {manim_input_json}")
    except Exception as e:
        print(f"Error writing Manim input JSON: {e}", file=sys.stderr)
        raise

    # 2. --- Run the correct animation(s) using match/case ---
    
    videos_to_stitch = []
    
    match solution_type:
        case 'initial':
            print("Rendering VAM-only video...")
            vam_video_path = _run_manim_scene("VAM_animation.py", "VAM_Transportation", script_dir)
            # Move the single video to the final output path
            shutil.move(vam_video_path, output_video_path)
            print(f"VAM video moved to {output_video_path}")
            
        case 'final':
            print("Rendering MODI-only video...")
            modi_video_path = _run_manim_scene("MODI_animation.py", "MODI_Transportation", script_dir)
            # Move the single video to the final output path
            shutil.move(modi_video_path, output_video_path)
            print(f"MODI video moved to {output_video_path}")

        case 'both':
            print("Rendering 'both' videos (VAM then MODI)...")
            # Step A: Run VAM
            vam_video_path = _run_manim_scene("VAM_animation.py", "VAM_Transportation", script_dir)
            videos_to_stitch.append(vam_video_path)
            
            # Step B: Run MODI
            modi_video_path = _run_manim_scene("MODI_animation.py", "MODI_Transportation", script_dir)
            videos_to_stitch.append(modi_video_path)
            
            # Step C: Stitch them
            _stitch_videos(videos_to_stitch, output_video_path, script_dir)
            print(f"Combined VAM+MODI video saved to {output_video_path}")
        
        case _:
            raise ValueError(f"Unknown solution type for video: {solution_type}")

def generate_direct_solution(input_data, output_file):
    """Solves the problem directly and writes a JSON output."""
    print("Solving transportation problem (direct)...")
    
    costs = np.array(input_data['costMatrix'])
    supply = np.array(input_data['supply'])
    demand = np.array(input_data['demand'])
    problem_type = input_data['problemType']
    solution_type = input_data['solutionType']
    
    # 1. Run VAM
    (initial_allocation, initial_cost, 
     original_costs, costs_to_solve, 
     _, _) = solve_vam(supply.copy(), demand.copy(), costs.copy(), problem_type)
    
    solution = {}
    
    # --- Use match/case for solution type ---
    match solution_type:
        case 'initial':
            solution = {
                'assignments': np.array(initial_allocation).tolist(),
                'total_cost': float(initial_cost),
                'problem_type': problem_type
            }
            
        case 'final':
            final_allocation, total_cost = solve_MODI(costs_to_solve, original_costs, initial_allocation)
            solution = {
                'assignments': np.array(final_allocation).tolist(),
                'total_cost': float(total_cost),
                'problem_type': problem_type
            }

        case 'both':
            final_allocation, total_cost = solve_MODI(costs_to_solve, original_costs, initial_allocation)
            solution = {
                'initial': {
                    'assignments': np.array(initial_allocation).tolist(),
                    'total_cost': float(initial_cost), 
                    'problem_type': problem_type
                },
                'final': {
                    'assignments': np.array(final_allocation).tolist(),
                    'total_cost': float(total_cost), 
                    'problem_type': problem_type
                }
            }
        
        case _:
            raise ValueError(f"Unknown solution type: {solution_type}")

    # Write the solution to the output JSON file
    with open(output_file, 'w') as f:
        json.dump(solution, f, indent=2)
    
    print("Direct solution generated successfully!")
    
    if 'initial' in solution:
         print(f"Initial Cost: {solution['initial']['total_cost']}")
         print(f"Final Cost: {solution['final']['total_cost']}")
    else:
        print(f"Total Cost: {solution['total_cost']}")

def generate_pdf_report(input_data, output_file):
    """Generates a PDF report (placeholder)."""
    # TODO: Implement PDF logic
    print(f"PDF generation logic for {output_file} goes here.")
    # For now, just create an empty file as a placeholder
    with open(output_file, 'w') as f:
        f.write("PDF generation not yet implemented.")

# --- Main Execution ---

def main():
    """Main entry point for all Transportation problem requests."""
    parser = argparse.ArgumentParser(description='Transportation Problem Solver')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--type', required=True, choices=['video', 'pdf', 'direct'], help='Output type')
    
    args = parser.parse_args()
    
    try:
        # Read the user's temporary input file
        with open(args.input, 'r') as f:
            input_data = json.load(f)
        
        # --- Use match case for output type ---
        match args.type:
            case 'direct':
                generate_direct_solution(input_data, args.output)
            
            case 'video':
                generate_video(input_data, args.output, input_data.get('solutionType', 'both'))
                print(f"Video process complete. Final file at: {args.output}")

            case 'pdf':
                generate_pdf_report(input_data, args.output)
            
            case _:
                # This case is redundant thanks to argparse 'choices', but is good practice
                print(f"Error: Unknown output type '{args.type}'", file=sys.stderr)
                sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()