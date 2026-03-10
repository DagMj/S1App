from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import (
    default_evaluate,
    default_solution,
    format_polynomial_latex,
)

_PROMPT_TEMPLATES = [
    'Gitt funksjonen\n$$f(x)={poly}$$\nFinn den deriverte funksjonen\n$$f^{{\\prime}}(x)$$',
    'Deriver funksjonen\n$$f(x)={poly}$$',
    'En funksjon er gitt ved\n$$f(x)={poly}$$\nBestem $f\'(x)$.',
    'Finn den deriverte av\n$$f(x)={poly}$$',
]


class PolynomialDerivativeGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='polynomial_derivative',
            name='Derivasjon av polynom',
            description='Deriverer polynomfunksjoner av grad 2 og 3.',
            tema='Derivasjon',
            part='del1',
            answer_type='function',
            difficulty=2,
            default_weight=1.0,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        # cubic: vekt 2, quadratic: vekt 2, mixed (ax³+bx+c): vekt 1
        subtype = rng.choices(
            ['cubic', 'quadratic', 'mixed'],
            weights=[2, 2, 1],
        )[0]

        prompt_template = rng.choice(_PROMPT_TEMPLATES)

        if subtype == 'cubic':
            a = rng.choice([1, 2, 3, 4])
            b = rng.choice([1, 2, 3, 4, 5])
            c = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            d = rng.choice([-6, -4, -2, 0, 2, 4, 6])

            poly_latex = format_polynomial_latex(
                [(a, 'x^3'), (b, 'x^2'), (c, 'x'), (d, '')]
            )
            derivative_latex = format_polynomial_latex(
                [(3 * a, 'x^2'), (2 * b, 'x'), (c, '')]
            )
            answer = f'{3 * a}*x**2 + {2 * b}*x + {c}'
            steps = [
                f'Gitt $f(x) = {poly_latex}$.',
                r'Deriver ledd for ledd: $x^n \to n\cdot x^{n-1}$.',
                f"$3 \\cdot {a}x^2 + 2 \\cdot {b}x + {c}$.",
                f"Svar: $f'(x) = {derivative_latex}$.",
            ]

        elif subtype == 'quadratic':
            a = rng.choice([1, 2, 3, 4, 5])
            b = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            c = rng.choice([-8, -6, -4, -2, 0, 2, 4, 6, 8])

            poly_latex = format_polynomial_latex(
                [(a, 'x^2'), (b, 'x'), (c, '')]
            )
            derivative_latex = format_polynomial_latex(
                [(2 * a, 'x'), (b, '')]
            )
            answer = f'{2 * a}*x + {b}'
            steps = [
                f'Gitt $f(x) = {poly_latex}$.',
                r'Deriver ledd for ledd: $x^2 \to 2x$, $x \to 1$, konstant $\to 0$.',
                f"Svar: $f'(x) = {derivative_latex}$.",
            ]

        else:  # mixed: ax³ + bx + c (ingen x²-ledd)
            a = rng.choice([1, 2, 3])
            b = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            c = rng.choice([-6, -4, -2, 0, 2, 4, 6])

            poly_latex = format_polynomial_latex(
                [(a, 'x^3'), (b, 'x'), (c, '')]
            )
            derivative_latex = format_polynomial_latex(
                [(3 * a, 'x^2'), (b, '')]
            )
            answer = f'{3 * a}*x**2 + {b}'
            steps = [
                f'Gitt $f(x) = {poly_latex}$.',
                r'Deriver ledd for ledd: $x^3 \to 3x^2$, $x \to 1$.',
                f"Svar: $f'(x) = {derivative_latex}$.",
            ]

        prompt = prompt_template.format(poly=poly_latex)

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='function',
            correct_answer=answer,
            solution_short=f"$f'(x) = {derivative_latex}$",
            solution_steps=steps,
            metadata={
                'tema': 'derivasjon',
                'difficulty': 2,
                'latex': True,
                'subtype': subtype,
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
