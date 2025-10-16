import subprocess
import json

def solve_lines(grid):
    """
    This function acts as a bridge to your trusted Ruby script.
    1. Saves the grid data to a file.
    2. Runs the Ruby script as a subprocess.
    3. Reads the JSON output from the Ruby script.
    4. Formats the output for the Manim animation.
    """
    # 1. Save the current matrix data for the Ruby script to read
    with open("E:/manimations/Project/Assignment/data_for_ruby.json", "w") as f:
        json.dump(grid, f)
        
    try:
        # 2. Run the Ruby script. This requires 'ruby' to be in your system's PATH.
        command = ["ruby", "E:/manimations/Project/Assignment/line_finder.rb"]
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True # This will raise an error if the script fails
        )
        while True:
            
            # 3. Read the JSON output from the completed Ruby script
            lines = json.loads(result.stdout)
            
            # 4. Format the data for the Manim functions
            rows_to_cover = [index for type, index in lines if type == "row"]
            cols_to_cover = [index for type, index in lines if type == "column"]
            
            return rows_to_cover, cols_to_cover

    except FileNotFoundError:
        print("ERROR: 'ruby' command not found. Is Ruby installed and in your system's PATH?")
        return [], []
    except subprocess.CalledProcessError as e:
        print("ERROR: The Ruby script failed to execute.")
        print("--- Ruby Script Output ---")
        print(e.stdout)
        print(e.stderr)
        print([],[])
        return [], []
