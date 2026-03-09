from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _ln_latex(expr: sp.Expr) -> str:
    """SymPy renders natural log as \\log; replace with \\ln for display."""
    return sp.latex(expr).replace(r'\log', r'\ln')


class AdvancedDerivativeGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='advanced_derivative',
            name='Derivasjon (produkt, kjede, brøk)',
            description='Derivasjonsoppgaver med produktregel, kjerneregel og brøkregel – inkl. e^x og ln(x).',
            tema='Derivasjon',
            part='del2',
            answer_type='function',
            difficulty=4,
            default_weight=0.8,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x', positive=True)  # positive=True helps ln domain
        subtype = rng.choice(['product', 'chain', 'quotient'])

        if subtype == 'product':
            # One factor must be a transcendental function (e^x or ln x)
            variant = rng.choice(['poly_exp', 'poly2_exp', 'poly_ln'])

            if variant == 'poly_exp':
                # f(x) = (ax + b) · e^x
                a = rng.choice([1, 2, 3])
                b = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
                u = a * x + b
                v = sp.exp(x)
                expr = u * v
                derivative = sp.factor(sp.diff(expr, x))   # (ax+a+b)·e^x
                steps = [
                    "Bruk produktregelen: $(uv)' = u'v + uv'$.",
                    f"Sett $u = {sp.latex(u)}$ og $v = e^x$.",
                    f"$u' = {a}$ og $v' = e^x$.",
                    f"$f'(x) = {a} \\cdot e^x + {sp.latex(u)} \\cdot e^x = {_ln_latex(derivative)}$.",
                ]

            elif variant == 'poly2_exp':
                # f(x) = (ax² + b) · e^x
                a = rng.choice([1, 2, 3])
                b = rng.choice([1, 2, 3, 4, 5])
                u = a * x**2 + b
                v = sp.exp(x)
                expr = u * v
                derivative = sp.factor(sp.diff(expr, x))   # (ax²+2ax+b)·e^x
                steps = [
                    "Bruk produktregelen: $(uv)' = u'v + uv'$.",
                    f"Sett $u = {sp.latex(u)}$ og $v = e^x$.",
                    f"$u' = {sp.latex(sp.diff(u, x))}$ og $v' = e^x$.",
                    f"$f'(x) = {_ln_latex(derivative)}$.",
                ]

            else:  # poly_ln
                # f(x) = (ax + b) · ln(x),  b > 0 so f defined near x>0
                a = rng.choice([1, 2, 3])
                b = rng.choice([1, 2, 3, 4, 5])
                u = a * x + b
                v = sp.log(x)
                expr = u * v
                derivative = sp.simplify(sp.diff(expr, x))
                steps = [
                    "Bruk produktregelen: $(uv)' = u'v + uv'$.",
                    f"Sett $u = {sp.latex(u)}$ og $v = \\ln x$.",
                    f"$u' = {a}$ og $v' = \\dfrac{{1}}{{x}}$.",
                    f"$f'(x) = {a} \\cdot \\ln x + {sp.latex(u)} \\cdot \\dfrac{{1}}{{x}} = {_ln_latex(derivative)}$.",
                ]

        elif subtype == 'chain':
            # Inner function can be (ax+b)^n, e^(ax+b), or ln(ax+b)
            variant = rng.choice(['power', 'exp_linear', 'ln_linear'])

            if variant == 'power':
                a = rng.choice([2, 3, 4])
                b = rng.choice([-3, -2, -1, 1, 2, 3])
                n = rng.choice([3, 4, 5])
                expr = (a * x + b) ** n
                derivative = sp.diff(expr, x)   # keep factored: n·a·(ax+b)^(n-1)
                steps = [
                    r"Bruk kjerneregel: $(g(x)^n)' = n \cdot g(x)^{n-1} \cdot g'(x)$.",
                    f"Her $g(x) = {sp.latex(a * x + b)}$ og $g'(x) = {a}$.",
                    f"$f'(x) = {sp.latex(derivative)}$.",
                ]

            elif variant == 'exp_linear':
                # f(x) = e^(ax+b),  derivative = a·e^(ax+b)
                a = rng.choice([2, 3, 4])
                b = rng.choice([-3, -2, -1, 0, 1, 2, 3])
                inner = a * x + b
                expr = sp.exp(inner)
                derivative = sp.diff(expr, x)   # a·exp(ax+b)
                steps = [
                    r"Bruk kjerneregel: $(e^{g(x)})' = g'(x) \cdot e^{g(x)}$.",
                    f"Her $g(x) = {sp.latex(inner)}$ og $g'(x) = {a}$.",
                    f"$f'(x) = {_ln_latex(derivative)}$.",
                ]

            else:  # ln_linear
                # f(x) = ln(ax+b), a > 0, b > 0 → always positive for x > 0
                a = rng.choice([2, 3, 4])
                b = rng.choice([1, 2, 3, 4, 5])
                inner = a * x + b
                expr = sp.log(inner)
                derivative = sp.diff(expr, x)   # a/(ax+b)
                steps = [
                    r"Bruk kjerneregel: $(\ln(g(x)))' = \dfrac{g'(x)}{g(x)}$.",
                    f"Her $g(x) = {sp.latex(inner)}$ og $g'(x) = {a}$.",
                    f"$f'(x) = {_ln_latex(derivative)}$.",
                ]

        else:  # quotient  (polynomial/polynomial — brøkregel)
            a = rng.choice([2, 3, 4, 5])
            b = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            c = rng.choice([1, 2, 3])
            d = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
            while a * d - b * c == 0:
                d = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])

            u = a * x + b
            v = c * x + d
            expr = u / v
            derivative = sp.simplify(sp.diff(expr, x))
            steps = [
                r"Bruk brøkregelen: $\left(\dfrac{u}{v}\right)' = \dfrac{u'v - uv'}{v^2}$.",
                f"Sett $u = {sp.latex(u)}$ og $v = {sp.latex(v)}$.",
                f"$u' = {a}$ og $v' = {c}$.",
                f"$f'(x) = {_ln_latex(derivative)}$.",
            ]

        expr_latex = _ln_latex(expr)
        derivative_latex = _ln_latex(derivative)

        prompt = (
            'Deriver funksjonen\n'
            f'$$f(x) = {expr_latex}$$\n'
            "Oppgi svaret som $f'(x)$."
        )

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='function',
            correct_answer=sp.sstr(derivative),
            solution_short=f"$f'(x) = {derivative_latex}$",
            solution_steps=steps,
            metadata={
                'tema': 'derivasjon',
                'difficulty': 4,
                'latex': True,
                'subtype': subtype,
                'variant': variant if subtype in ('product', 'chain') else 'quotient',
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
