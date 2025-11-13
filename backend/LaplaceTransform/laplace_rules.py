"""
laplace_rules.py
----------------
Defines the base Laplace Transform rules and properties.

This version:
 - Robustly detects exponentials in forms exp(a*t) and E**(a*t)/e**(a*t)
 - Extracts numeric/symbolic coefficients of t in sin/cos/sinh/cosh
 - Handles constant multiples reliably
"""

import sympy as sp

# Smart symbols (imported / reused by solver)
t = sp.Symbol('t', real=True, positive=True)
s = sp.Symbol('s', real=True)
a = sp.Symbol('a', real=True)
b = sp.Symbol('b', real=True)


# ---------- Helpers ----------
def _extract_coeff_of_t(expr):
    """
    If expr is b*t (or t*b), return b.
    If expr is just t, return 1.
    If expr is numeric multiple of t, return that numeric coefficient.
    Otherwise return the original expr (fallback).
    """
    e = sp.simplify(expr)
    if e == t:
        return sp.Integer(1)
    # Use .coeff for linear coefficient of t
    try:
        coeff = sp.expand(e).coeff(t, 1)
        if coeff != 0:
            return sp.simplify(coeff)
    except Exception:
        pass
    return e


def _get_exp_argument(e):
    """
    Return the exponent argument if e is an exponential:
      - exp(arg) -> returns arg
      - E**arg  -> returns arg
      - e**arg  -> returns arg (if base name is 'e' or 'E')
    Otherwise returns None.
    """
    # case: exp(...)
    if e.func == sp.exp:
        return e.args[0]

    # case: pow with base E or base named 'E'/'e'
    if isinstance(e, sp.Pow):
        base = e.base
        # direct sympy.E
        if base == sp.E:
            return e.exp
        # sometimes base can be a Symbol named 'e' or 'E' from parsing
        if getattr(base, "name", None) in ("e", "E"):
            return e.exp

    return None


# -------------------------------------------------------------------
# BASE FUNCTION RULES
# -------------------------------------------------------------------
def get_base_rules(expr):
    """Return (result_expr, description) if expr matches a base function, else None."""

    e = sp.simplify(expr)

    # Constant (number)
    if e.is_Number:
        return (e / s, "L{C} = C / s")

    # t^n (power)
    if e.is_Pow and e.base == t:
        n = e.exp
        try:
            n_int = int(n)
            if n_int >= 0 and n_int == n:
                return (sp.factorial(n_int) / s**(n_int + 1), "L{t^n} = n! / s^{n+1}")
        except Exception:
            pass

    # Exponential: handle exp(arg) and E**arg / e**arg
    exp_arg = _get_exp_argument(e)
    if exp_arg is not None:
        # If arg contains t, extract coefficient of t
        if exp_arg.has(t):
            a_coeff = sp.simplify(sp.expand(exp_arg).coeff(t, 1))
            # if .coeff returned 0 (unexpected), fallback to whole arg
            if a_coeff == 0:
                a_coeff = exp_arg
            return (1 / (s - a_coeff), f"L{{e^{{{a_coeff} t}}}} = 1 / (s - {a_coeff})")
        else:
            # exp(constant) is a constant function value independent of t => treat as constant
            return (sp.exp(exp_arg) / s, "L{e^{c}} (treated as constant) = e^{c} / s")

    # Sine: sin(b t)
    if e.func == sp.sin:
        arg = e.args[0]
        b_val = _extract_coeff_of_t(arg)
        return (sp.simplify(b_val / (s**2 + sp.simplify(b_val)**2)), "L{sin(bt)} = b / (s^2 + b^2)")

    # Cosine: cos(b t)
    if e.func == sp.cos:
        arg = e.args[0]
        b_val = _extract_coeff_of_t(arg)
        return (sp.simplify(s / (s**2 + sp.simplify(b_val)**2)), "L{cos(bt)} = s / (s^2 + b^2)")

    # Sinh
    if e.func == sp.sinh:
        arg = e.args[0]
        b_val = _extract_coeff_of_t(arg)
        return (sp.simplify(b_val / (s**2 - sp.simplify(b_val)**2)), "L{sinh(bt)} = b / (s^2 - b^2)")

    # Cosh
    if e.func == sp.cosh:
        arg = e.args[0]
        b_val = _extract_coeff_of_t(arg)
        return (sp.simplify(s / (s**2 - sp.simplify(b_val)**2)), "L{cosh(bt)} = s / (s^2 - b^2)")

    # Dirac delta δ(t - a) -> exp(-a s)
    if e.func == sp.DiracDelta:
        arg = e.args[0]
        # common case DiracDelta(t - a)
        if arg.is_Add:
            const_part = sp.expand(arg - t)
            shift = -const_part
            return (sp.exp(-shift * s), "L{δ(t - a)} = e^{-a s}")
        else:
            if arg == t:
                return (sp.Integer(1), "L{δ(t)} = 1")

    # Heaviside step (unit step)
    if e.func == sp.Heaviside:
        arg = e.args[0]
        if arg == t:
            return (1 / s, "L{u(t)} = 1 / s")
        return None

    # Fallback
    return None


# -------------------------------------------------------------------
# PROPERTY RULES
# -------------------------------------------------------------------
def get_property_rules(expr, recursive_solver):
    """
    Check and apply property-based rules.
    Calls recursive_solver() on sub-expressions as needed.
    Returns (result_expr, description) or None
    """

    e = sp.simplify(expr)

    # Linearity: sum of terms
    if isinstance(e, sp.Add):
        results = []
        for term in e.args:
            sub = recursive_solver(term)
            results.append(sp.simplify(sub))
        return (sp.simplify(sum(results)), r"Linearity: $L{f + g} = L{f} + L{g}$")

    # -----------------------
    # Time Shifting: f(t - a) * u(t - a)
    # -----------------------
    # Detect Heaviside/Unit step factor with argument (t - a)
    # Handles patterns:
    #   Heaviside(t - a) * g(...)     OR    g(...) * Heaviside(t - a)
    # where g(...) is typically expressed in terms of (t - a)
    if isinstance(e, sp.Mul):
        # find Heaviside factor
        heaviside_factors = [arg for arg in e.args if arg.func == sp.Heaviside]
        if heaviside_factors:
            H = heaviside_factors[0]
            H_arg = H.args[0]  # e.g., t - a
            # attempt to extract shift value 'a' from H_arg
            # common pattern: t - a  -> shift = a
            shift_val = None
            if H_arg.is_Add:
                # try to get constant part such that H_arg == t - a
                # compute (H_arg - t) and take negative
                const_part = sp.simplify(H_arg - t)
                shift_val = -const_part
            elif H_arg.is_Mul or H_arg.is_Symbol or H_arg.is_Number:
                # rare/other forms: try solving for shift: H_arg.subs(t, 0) = -a? fallback
                # if H_arg == t - 2, this is handled above; else try H_arg.coeff(t,1)
                try:
                    coeff_t = sp.expand(H_arg).coeff(t, 1)
                    if coeff_t == 1:
                        # then constant part = H_arg - t
                        const_part = sp.simplify(H_arg - t)
                        shift_val = -const_part
                except Exception:
                    shift_val = None
            else:
                # direct equality check: if H_arg == t - a_sym
                try:
                    if H_arg.has(t):
                        const_part = sp.simplify(H_arg - t)
                        shift_val = -const_part
                except Exception:
                    shift_val = None

            # If shift_val found, try to reconstruct f(t)
            if shift_val is not None:
                # remaining factor(s) (product of args excluding H)
                remaining_args = [arg for arg in e.args if arg != H]
                if not remaining_args:
                    # pure Heaviside(t-a) -> treat as time-shifted unit-step
                    # L{u(t-a)} = e^{-a s}/s  but standard is L{u(t-a)} = e^{-a s}/s
                    result = sp.exp(-shift_val * s) / s
                    return (result, f"Time Shifting: L{{u(t - {shift_val})}} = e^(-{shift_val} s)/s")
                remaining = sp.Mul(*remaining_args)
                # Check if remaining explicitly uses (t - a) pattern
                # We will attempt to rebuild unshifted f(t) by substituting t -> t + a in the remaining expression.
                try:
                    f_of_t = sp.simplify(remaining.subs(t, t + shift_val))
                    # compute F(s) = Laplace{ f(t) }
                    F_s = recursive_solver(f_of_t)
                    # final result = e^{-a s} * F(s)
                    result = sp.simplify(sp.exp(-shift_val * s) * F_s)
                    return (result, f"Time Shifting: L{{f(t - {shift_val}) u(t - {shift_val})}} = e^(-{shift_val} s) F(s)")
                except Exception:
                    # fallback: cannot reconstruct f(t), skip to other rules
                    pass

    # Frequency Shift: e^{a t} * f(t)
    if isinstance(e, sp.Mul):
        exp_factor = None
        for arg in e.args:
            if arg.func == sp.exp:
                exp_factor = arg
                break
            if isinstance(arg, sp.Pow) and (arg.base == sp.E or getattr(arg.base, "name", None) in ("e", "E")):
                exp_factor = arg
                break
        if exp_factor is not None:
            # get exponent of exp_factor
            if exp_factor.func == sp.exp:
                exp_arg = exp_factor.args[0]
            else:
                exp_arg = exp_factor.exp
            if exp_arg.has(t):
                a_coeff = sp.simplify(sp.expand(exp_arg).coeff(t, 1))
            else:
                a_coeff = exp_arg
            remaining = sp.Mul(*[arg for arg in e.args if arg != exp_factor])
            F_s = recursive_solver(remaining)
            shifted = sp.simplify(F_s.subs(s, s - a_coeff))
            return (shifted, r"Frequency Shifting: $L{e^{a t} f(t)} = F(s - a)$")

    # Multiplication by t^n: t^n * f(t)
    if isinstance(e, sp.Mul):
        pow_terms = [arg for arg in e.args if arg.is_Pow and arg.base == t]
        if pow_terms:
            pow_term = pow_terms[0]
            n_val = pow_term.exp
            rest = sp.Mul(*[arg for arg in e.args if arg != pow_term])
            F_s = recursive_solver(rest)
            try:
                n_int = int(n_val)
                derivative = sp.diff(F_s, s, n_int)
                result = sp.simplify(((-1)**n_int) * derivative)
                return (result, r"Multiplication by $t^n$: $\mathcal{L}\{t^n f(t)\} = (-1)^n F^{(n)}(s)$")

            except Exception:
                pass

    # Differentiation in time: derivative of f(t)
    if e.is_Derivative:
        f = e.args[0]
        F_s = recursive_solver(f)
        try:
            f0 = sp.limit(f, t, 0)
        except Exception:
            f0 = None
        if f0 is None:
            f0 = f.subs(t, 0)
        result = sp.simplify(s * F_s - f0)
        return (result, r"Differentiation in Time: $L{f'(t)} = sF(s) - f(0)$")

    # Scaling property: limited support; skip here
    return None
