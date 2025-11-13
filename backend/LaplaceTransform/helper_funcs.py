from manim import *

def display_input_equation(scene: Scene, inner_latex: str, title):
    """
    Display the page title and the input Laplace expression: \\mathcal{L}{ ... }.

    Args:
      scene: the Manim Scene (self inside your Scene methods).
      inner_latex: the LaTeX string for the thing inside L{ ... }, e.g. r"e^{2 t} \sin(3 t)".
                   NOTE: pass raw strings (r"...") to avoid Python escape issues.

    Returns:
      (equation_mobj)
      - equation_mobj is the MathTex containing "\mathcal{L}\{ inner_latex \}"
    """


    # 1) Build the MathTex for \mathcal{L}{ ... }
    # Put the inner latex directly inside. Use raw string when calling this function.
    full_tex = r"\mathcal{L}\{ " + inner_latex + r" \}"
    equation = MathTex(full_tex, font_size=52)
    # position it a little below the title
    equation.next_to(title, DOWN)

    # 3) Animate it to the screen
    scene.play(Write(equation))
    scene.wait(0.6)

    return equation
