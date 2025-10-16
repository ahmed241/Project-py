import os
import time
import argparse
import sys
from manim import *
from helper_funcs import AnimationHelpers 
from PSG_data_EOT import *

# --- 1. Accept Command-Line Arguments ---
parser = argparse.ArgumentParser(description="Generate EOT Crane Design Animation.")
parser.add_argument("--load", type=float, required=True, help="Load in kN")
parser.add_argument("--speed", type=float, required=True, help="Hoisting speed in m/s")
parser.add_argument("--lift", type=float, required=True, help="Lift height in meters")

args = parser.parse_args()


class DesignScene(Scene):
    """
    A scene to animate the design and calculation steps for the EOT crane.
    """
    def construct(self):
        # Instantiate our helper class
        Title = Tex("Design Of EOT Crane", font_size=48)
        self.play(Write(Title))
        self.wait(0.5)
        self.play(Title.animate.scale(0.75))
        self.play(Title.animate.to_edge(UP))
        
        # Title for the section
        title1 = Tex("Step 1: Selection of Wire Rope").next_to(Title, DOWN, buff=0.25)
        self.play(Write(title1))

        # --- Section 1: Rope Design ---
        breaking_load_tonnes = AnimationHelpers.animate_rope_design(self, args.load, title1)
        self.wait(2)
        self.next_section(skip_animations=True)
        # --- Section 2: Rope Selection ---
        selected_rope_dia, selected_load = AnimationHelpers.animate_rope_selection_from_table(
            self, breaking_load_tonnes, psg_data_ropedia, title1
        )
        
        # --- Section 3: Pulley Selection ---
        self.play(FadeOut(title1))
        title3 = Tex("Step 3: Pulley Selection").next_to(Title, DOWN, buff=0.25)
        selected_pulley = AnimationHelpers.animate_pulley_selection(
            self, selected_rope_dia, pulley_data, title3
        )
        self.wait(1)


if __name__ == "__main__":
    # Generate a unique filename to avoid conflicts
    timestamp = int(time.time())
    file_name = f"eot_crane_{timestamp}.mp4"
    
    # IMPORTANT: Set the output directory to the public folder
    # Get the project root (where this script is run from)
    project_root = os.getcwd()
    output_dir = os.path.join(project_root, "public", "videos")
    
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Configure Manim
    config.media_dir = output_dir
    config.output_file = file_name
    config.quality = "high_quality"  # Options: low_quality, medium_quality, high_quality
    config.preview = False  # Don't open preview window
    
    # This renders the scene
    scene = DesignScene()
    scene.render()
    
    # IMPORTANT: Print ONLY the filename to stdout (this is read by Node.js)
    # Make sure this is the last print statement
    print(file_name, flush=True)