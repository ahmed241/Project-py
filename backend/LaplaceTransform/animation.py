# backend/LaplaceTransform/animation.py
from manim import *
import json
import os

class LaplaceTransformScene(Scene):
    def construct(self):
        # Load data from JSON file
        json_path = os.path.join(os.path.dirname(__file__), "data.json")
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.add(Text("Error: data.json not found.").scale(0.7))
            return

        input_latex = data.get("inputLatex", "f(t)")
        output_latex = data.get("outputLatex", "F(s)")
        show_steps = data.get("showSteps", False)
        steps = data.get("steps", [])

        # Display input function
        input_text = MathTex(f"f(t) = {input_latex}").to_edge(UP + LEFT)
        self.play(Write(input_text))
        self.wait(1)

        # Display Laplace Transform operator
        transform_op = MathTex("\\mathcal{L}\\{f(t)\\} = F(s)").next_to(input_text, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(transform_op))
        self.wait(1)

        # Display the result
        result_text = MathTex(f"F(s) = {output_latex}").next_to(transform_op, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(result_text))
        self.wait(2)

        if show_steps and steps:
            self.play(FadeOut(input_text, transform_op, result_text))
            step_mobjects = VGroup(*[MathTex(step).to_edge(UP if i == 0 else LEFT).shift(DOWN * i * 0.8) for i, step in enumerate(steps)])
            self.play(LaggedStart(*[Write(step) for step in step_mobjects], lag_ratio=0.7))
            self.wait(3)

        self.wait(1)

