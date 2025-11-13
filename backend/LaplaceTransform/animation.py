from manim import *
from helper_funcs import *
class DemoInputOnly(Scene):
    def construct(self):
        # a simple LaTeX inner expression (use raw string)
        inner = r"e^{2 t} \sin\left(3 t\right)"   # clean LaTeX for inside of L{ ... }
        title = Tex("Laplace Transform", font_size = 72).to_edge(UP)
        self.play(Write(title))
        # call the helper to display title + equation
        eq = display_input_equation(self, inner, title)

        # now `eq` is available for later actions (highlight, transform, etc.)
        # example: briefly highlight the equation
        box = SurroundingRectangle(eq, color=YELLOW, buff=0.12)
        self.play(Create(box))
        self.wait(0.8)
        self.play(FadeOut(box))
        self.wait(0.5)
