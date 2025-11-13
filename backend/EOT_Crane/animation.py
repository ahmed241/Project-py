import os
import time
import json
from manim import *
from helper_funcs import AnimationHelpers
from PSG_data_EOT import *

# narration imports
from manim_narration import NarrationScene
from manim_narration.speech import KokoroService

class DesignScene(NarrationScene):
    """
    A scene to animate the design and calculation steps for the EOT crane.
    Added narration using KokoroService (speech_service_id="en").
    """
    def construct(self):
            # setup TTS service
            self.set_speech_services(
                en=KokoroService(voice="af_jessica", lang_code="en-us")
            )

            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, "data.json")
            with open(json_path, "r") as f:
                saved_data = json.load(f)
                load_value = saved_data["load"]
                speed = saved_data["speed"]
                lift_height = saved_data["lift"]

            # Instantiate our helper class
            self.next_section(skip_animations=True)

            # Title with narration
            Title = Tex("Design Of EOT Crane", font_size=48)
            with self.narration(speech_service_id="en", text="Design of E O T crane. We will step through rope selection, pulley selection and axle design.") as narration:
                self.play(Write(Title), run_time=narration.duration)
                self.wait(0.2)
                self.play(Title.animate.scale(0.75), run_time=0.6)
                self.play(Title.animate.to_edge(UP), run_time=0.6)

            # Title for the section with narration
            title1 = Tex("Step 1: Selection of Wire Rope").next_to(Title, DOWN, buff=0.25)
            with self.narration(speech_service_id="en", text="Step one: selection of wire rope.") as narration:
                self.play(Write(title1), run_time=narration.duration)

            # --- Section 1: Rope Design ---
            # animate_rope_design includes its own narration blocks
            breaking_load_tonnes, load_per_fall_kgf = AnimationHelpers.animate_rope_design(self, load_value, title1)
            self.wait(2)

            # --- Section 2: Rope Selection ---
            # animate_rope_selection_from_table includes narration internally
            selected_rope_dia, selected_load = AnimationHelpers.animate_rope_selection_from_table(
                self, breaking_load_tonnes, psg_data_ropedia, title1
            )

            # --- Section 3: Pulley Selection ---
            with self.narration(speech_service_id="en", text="Now we select a suitable pulley for the chosen rope diameter.") as narration:
                self.play(FadeOut(title1), run_time=min(0.4, narration.duration))
                title3 = Tex("Step 3: Pulley Selection").next_to(Title, DOWN, buff=0.25)
                self.play(Write(title3), run_time=narration.duration)

            selected_pulley = AnimationHelpers.animate_pulley_selection(
                self, selected_rope_dia, pulley_data, title3
            )
            self.wait(1)

            # --- Section 4: Axle Design ---
            with self.narration(speech_service_id="en", text="Finally, we design the axle for the pulley and compute dimensions.") as narration:
                self.play(FadeOut(title3), run_time=min(0.4, narration.duration))
                title4 = Tex("Step 4: Design of Axle").next_to(Title, DOWN, buff=0.25)
                self.play(Write(title4), run_time=narration.duration)

            self.next_section()
            axle_diagram = AnimationHelpers.animate_axle_design(
                self, selected_pulley, load_per_fall_kgf, title4
            )
            self.wait(1)
