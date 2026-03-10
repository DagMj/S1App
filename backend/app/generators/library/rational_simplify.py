from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class RationalSimplifyGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='rational_simplify',
            name='Forkorte rasjonale uttrykk',
            description='Forkorter rasjonale uttrykk med faktorisering, fellesnevner og forkorting.',
            tema='Algebra',
            part='del1',
            answer_type='expression',
            difficulty=2,
            default_weight=1.2,
        )

    @staticmethod
    def _format_forbidden(values: list[int]) -> str:
        latex_vals = ', '.join(sp.latex(v) for v in values)
        return f'x \\neq {latex_vals}'

    @staticmethod
    def _random_linear_expr(rng: random.Random, x: sp.Symbol) -> sp.Expr:
        coeff = rng.choice([1, 1, 1, 2, 3])
        constant = rng.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4])
        return coeff * x + constant

    @staticmethod
    def _simplified_expr(expr: sp.Expr) -> sp.Expr:
        return sp.cancel(sp.together(sp.simplify(expr)))

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')
        subtype = rng.choice(
            [
                'difference_of_squares',
                'common_factor',
                'sum_two_fractions_linear_numerators',
                'sum_three_fractions_composed_denominator',
            ]
        )

        if subtype == 'difference_of_squares':
            a = rng.choice([1, 2, 3])
            b = rng.choice([2, 3, 4, 5])
            numerator = a * x**2 - a * (b**2)
            denominator = x - b
            expr = numerator / denominator
            simplified = self._simplified_expr(expr)
            answer = sp.sstr(simplified)

            factor_prefix = '' if a == 1 else str(a)
            prompt = (
                f'Forkort uttrykket (for ${self._format_forbidden([b])}$)\n'
                f'$$\\frac{{{sp.latex(numerator)}}}{{{sp.latex(denominator)}}}$$'
            )
            steps = [
                f'Bruk kvadratsetningen: ${sp.latex(numerator)} = {factor_prefix}(x-{b})(x+{b})$.' if a != 1 else f'Bruk kvadratsetningen: ${sp.latex(numerator)} = (x-{b})(x+{b})$.',
                f'Forkort med (x-{b}).',
                f'Svar: ${sp.latex(simplified)}$.',
            ]
            solution_short = f'Uttrykket blir ${sp.latex(simplified)}$.'

        elif subtype == 'common_factor':
            k = rng.choice([2, 3, 4, 5])
            m = rng.choice([1, 2, 3, 4])
            n = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
            linear_expr = m * x + n
            numerator = k * x * linear_expr
            denominator = k * x
            expr = numerator / denominator
            simplified = self._simplified_expr(expr)
            answer = sp.sstr(simplified)

            prompt = (
                f'Forkort uttrykket (for ${self._format_forbidden([0])}$)\n'
                f'$$\\frac{{{sp.latex(numerator)}}}{{{sp.latex(denominator)}}}$$'
            )
            steps = [
                f'Telleren er et produkt: ${sp.latex(numerator)}$.',
                f'Forkort med {k}x i teller og nevner.',
                f'Svar: ${sp.latex(simplified)}$.',
            ]
            solution_short = f'Uttrykket blir ${sp.latex(simplified)}$.'

        elif subtype == 'sum_two_fractions_linear_numerators':
            p = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            q_candidates = [v for v in [-4, -3, -2, -1, 1, 2, 3, 4] if v != p]
            q = rng.choice(q_candidates)

            den1 = x - p
            den2 = x - q
            num1 = self._random_linear_expr(rng, x)
            num2 = self._random_linear_expr(rng, x)
            op2 = rng.choice([1, -1])
            sign2 = '+' if op2 == 1 else '-'

            expr = num1 / den1 + op2 * num2 / den2
            simplified = self._simplified_expr(expr)
            answer = sp.sstr(simplified)

            prompt = (
                f'Regn ut og forkort uttrykket (for ${self._format_forbidden([p, q])}$)\n'
                f'$$\\frac{{{sp.latex(num1)}}}{{{sp.latex(den1)}}} {sign2} \\frac{{{sp.latex(num2)}}}{{{sp.latex(den2)}}}$$'
            )
            steps = [
                f'Fellesnevner er ${sp.latex(sp.expand(den1 * den2))} = ({sp.latex(den1)})({sp.latex(den2)})$.',
                'Utvid brøkene til fellesnevner og slå sammen tellerne.',
                f'Forkort uttrykket dersom mulig. Svar: ${sp.latex(simplified)}$.',
            ]
            solution_short = f'Svar: ${sp.latex(simplified)}$.'

        else:
            p = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            q_candidates = [v for v in [-4, -3, -2, -1, 1, 2, 3, 4] if v != p]
            q = rng.choice(q_candidates)

            den1 = x - p
            den2 = x - q
            den3 = den1 * den2
            num1 = self._random_linear_expr(rng, x)
            num2 = self._random_linear_expr(rng, x)
            num3 = self._random_linear_expr(rng, x)
            op2 = rng.choice([1, -1])
            op3 = rng.choice([1, 1, -1])
            sign2 = '+' if op2 == 1 else '-'
            sign3 = '+' if op3 == 1 else '-'

            expr = num1 / den1 + op2 * num2 / den2 + op3 * num3 / den3
            simplified = self._simplified_expr(expr)
            answer = sp.sstr(simplified)

            prompt = (
                f'Regn ut og forkort uttrykket (for ${self._format_forbidden([p, q])}$)\n'
                f'$$\\frac{{{sp.latex(num1)}}}{{{sp.latex(den1)}}} '
                f'{sign2} \\frac{{{sp.latex(num2)}}}{{{sp.latex(den2)}}} '
                f'{sign3} \\frac{{{sp.latex(num3)}}}{{{sp.latex(den3)}}}$$'
            )
            steps = [
                f'En av nevnerne er et produkt av de to andre: ${sp.latex(den3)} = ({sp.latex(den1)})({sp.latex(den2)})$.',
                'Bruk fellesnevner og kombiner tellerleddene.',
                f'Forkort uttrykket dersom mulig. Svar: ${sp.latex(simplified)}$.',
            ]
            solution_short = f'Svar: ${sp.latex(simplified)}$.'

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=answer,
            solution_short=solution_short,
            solution_steps=steps,
            metadata={'tema': 'algebra', 'difficulty': 2, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
