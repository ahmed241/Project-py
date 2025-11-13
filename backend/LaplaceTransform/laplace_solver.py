"""
laplace_solver.py
-----------------
Laplace Transform Solver with LaTeX output
------------------------------------------
Now returns LaTeX equations ready for Manim animations.
"""

import sympy as sp
import json
import re
from sympy.parsing.latex import parse_latex
from laplace_rules import get_base_rules, get_property_rules  # make sure it's in same directory

# Smart symbols
t = sp.Symbol('t', real=True, positive=True)
s = sp.Symbol('s', real=True)
a = sp.Symbol('a', real=True)
b = sp.Symbol('b', real=True)


# -----------------------------------------------------------------
# HELPER: LaTeX → SymPy Parser
# -----------------------------------------------------------------
def parse_to_sympy(latex_input: str):
    """
    Convert a LaTeX string into a SymPy expression.
    """
    parts = re.split(r'\s*=\s*', latex_input.strip(), maxsplit=1)
    latex_clean = parts[-1]
    expr_raw = parse_latex(latex_clean)
    subs = {sym: {'t': t, 's': s, 'a': a, 'b': b}.get(sym.name, sym)
            for sym in expr_raw.free_symbols}
    return expr_raw.subs(subs)


# -----------------------------------------------------------------
# MAIN SOLVER CLASS
# -----------------------------------------------------------------
class LaplaceSolver:
    def __init__(self, expr: sp.Expr):
        self.expr = sp.simplify(sp.expand(expr))
        self.steps = []

    def solve(self):
        """
        Solve the Laplace transform step by step.
        Returns JSON with both plain text and LaTeX outputs.
        """
        self.steps = []
        result = self._solve_recursive(self.expr)
        result_simplified = sp.simplify(result) if result is not None else None

        # Create final pretty LaTeX equation
        final_equation = self._make_laplace_equation(self.expr, result_simplified)

        return {
            "input": str(self.expr),
            "input_latex": sp.latex(self.expr),
            "result": str(result_simplified),
            "result_latex": sp.latex(result_simplified) if result_simplified is not None else None,
            "final_latex_equation": final_equation,
            "steps": self.steps
        }

    # -----------------------------------------------------------------
    # Core recursive solver
    # -----------------------------------------------------------------
    def _solve_recursive(self, expr):
        expr = sp.simplify(expr)

        # 1️⃣ Property-based rules
        prop = get_property_rules(expr, self._solve_recursive)
        if prop is not None:
            result_expr, desc = prop
            self._add_step("Property Applied", desc, expr, result_expr)
            return result_expr

        # 2️⃣ Base rules
        base = get_base_rules(expr)
        if base is not None:
            result_expr, desc = base
            self._add_step("Base Rule Applied", desc, expr, result_expr)
            return result_expr

        # 3️⃣ Constant multiple
        if expr.is_Mul:
            consts = [a for a in expr.args if a.is_Number]
            non_consts = [a for a in expr.args if not a.is_Number]
            if consts and non_consts:
                c = sp.Mul(*consts)
                f = sp.Mul(*non_consts)
                F_s = self._solve_recursive(f)
                result_expr = sp.simplify(c * F_s)
                self._add_step("Constant Multiple", "L{c·f(t)} = c·F(s)", expr, result_expr)
                return result_expr

        # 4️⃣ Fallback for sums
        if isinstance(expr, sp.Add):
            parts = [self._solve_recursive(p) for p in expr.args]
            combined = sp.simplify(sum(parts))
            self._add_step("Linearity (combine)", "Sum of sub-transforms", expr, combined)
            return combined

        # 5️⃣ Unknown
        self._add_step("Unknown", f"No matching rule for {expr}", expr, None)
        return sp.Symbol(f"L{{{expr}}}")

    # -----------------------------------------------------------------
    # Step logger with LaTeX equation
    # -----------------------------------------------------------------
    def _add_step(self, step_name: str, desc: str, expr, result):
        expr_latex = sp.latex(expr)
        result_latex = sp.latex(result) if result is not None else "?"
        equation = self._make_laplace_equation(expr, result)

        self.steps.append({
            "step": step_name,
            "description": desc,
            "expression": str(expr),
            "expression_latex": expr_latex,
            "result": str(result) if result is not None else None,
            "result_latex": result_latex,
            "latex_equation": equation  # ✅ ready for MathTex / Manim
        })

    # -----------------------------------------------------------------
    # Helper: format full Laplace equation
    # -----------------------------------------------------------------
    def _make_laplace_equation(self, expr, result):
        """
        Create a LaTeX equation like:
            \mathcal{L}\{ e^{2t}\sin(3t) \} = \frac{3}{(s-2)^2 + 9}
        """
        expr_tex = sp.latex(expr)
        if result is None:
            return rf"\mathcal{{L}}\{{ {expr_tex} \}}"
        result_tex = sp.latex(result)
        return rf"\mathcal{{L}}\{{ {expr_tex} \}} = {result_tex}"


# -----------------------------------------------------------------
# DEMO / TEST
# -----------------------------------------------------------------
if __name__ == "__main__":
    tests = [
        r"e^{2t}\sin(3t)",
        r"e^{t} + 4t^2 + \sin(3t)",
        r"t^2",
        r"5t^3 + \cos(4t)",
    ]

    for latex in tests:
        expr = parse_to_sympy(latex)
        solver = LaplaceSolver(expr)
        result = solver.solve()

        print(f"\n=== f(t) = {latex} ===")
        print(json.dumps(result, indent=2))
