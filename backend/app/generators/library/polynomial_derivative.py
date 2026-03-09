from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import (
    default_evaluate,
    default_solution,
    format_polynomial_latex,
)


class PolynomialDerivativeGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='polynomial_derivative',
            name='Derivasjon av polynom',
            description='Deriverer polynomfunksjoner.',
            tema='Derivasjon',
            part='del1',
            answer_type='function',
            difficulty=2,
            default_weight=1.0,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        a = rng.choice([1, 2, 3, 4])
        b = rng.choice([1, 2, 3, 4, 5])
        c = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        d = rng.choice([-6, -4, -2, 0, 2, 4, 6])

        poly_latex = format_polynomial_latex(
            [(a, 'x^3'), (b, 'x^2'), (c, 'x'), (d, '')]
        )
        derivative_latex = format_polynomial_latex([(3 * a, 'x^2'), (2 * b, 'x'), (c, '')])

        prompt = (
            f'Gitt funksjonen\n$$f(x)={poly_latex}$$\n'
            'Finn den deriverte funksjonen\n'
            '$$f^{\\prime}(x)$$'
        )
        answer = f'{3 * a}*x**2 + {2 * b}*x + {c}'

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='function',
            correct_answer=answer,
            solution_short=f"$f'(x) = {derivative_latex}$",
            solution_steps=[
                f'Gitt $f(x) = {poly_latex}$.',
                r'Deriver ledd for ledd: $x^n \to n\cdot x^{n-1}$.',
                f"Svar: $f'(x) = {derivative_latex}$.",
            ],
            metadata={'tema': 'derivasjon', 'difficulty': 2, 'latex': True},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
