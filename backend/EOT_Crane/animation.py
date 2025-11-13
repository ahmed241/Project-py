import os
import time
import json
from manim import *
from helper_funcs import AnimationHelpers 
from PSG_data_EOT import *

class DesignScene(Scene):
    """
    A scene to animate the design and calculation steps for the EOT crane.
    """
    def construct(self):
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, "data.json")
            with open(json_path, "r") as f:
                saved_data = json.load(f)
                load_value = saved_data["load"]
                speed = saved_data["speed"]
                lift_height = saved_data["lift"]

            # Instantiate our helper class
            self.next_section(skip_animations=True)
            Title = Tex("Design Of EOT Crane", font_size=48)
            self.play(Write(Title))
            self.wait(0.5)
            self.play(Title.animate.scale(0.75))
            self.play(Title.animate.to_edge(UP))
            
            # Title for the section
            title1 = Tex("Step 1: Selection of Wire Rope").next_to(Title, DOWN, buff=0.25)
            self.play(Write(title1))

            # --- Section 1: Rope Design ---
            breaking_load_tonnes, load_per_fall_kgf = AnimationHelpers.animate_rope_design(self, load_value, title1)
            self.wait(2)
            
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

            # --- NEW: Section 4: Axle Design ---
            self.play(FadeOut(title3)) # Fade out previous title
            title4 = Tex("Step 4: Design of Axle").next_to(Title, DOWN, buff=0.25)
            # Call the new function
            self.next_section()
            axle_diagram = AnimationHelpers.animate_axle_design(
                self, selected_pulley, load_per_fall_kgf, title4
            )
            self.wait(1)