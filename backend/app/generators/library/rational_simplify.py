from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class RationalSimplifyGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='rational_simplify',
            name='Forkorte rasjonale uttrykk',
            description='Forkorter rasjonale uttrykk med faktorisering og forkorting.',
            tema='Algebra',
            part='del1',
            answer_type='expression',
            difficulty=2,
            default_weight=1.2,
        )

    @staticmethod
    def _coeff_x_term(coeff: int, power: int = 1) -> str:
        if power == 1:
            return 'x' if coeff == 1 else f'{coeff}x'
        return f'x^{power}' if coeff == 1 else f'{coeff}x^{power}'

    @staticmethod
    def _linear_display(coeff: int, constant: int) -> str:
        x_term = RationalSimplifyGenerator._coeff_x_term(coeff)
        sign = '+' if constant >= 0 else '-'
        return f'{x_term} {sign} {abs(constant)}'

    @staticmethod
    def _linear_answer_expr(coeff: int, constant: int) -> str:
        x_term = 'x' if coeff == 1 else f'{coeff}*x'
        if constant == 0:
            return x_term
        sign = '+' if constant > 0 else '-'
        return f'{x_term}{sign}{abs(constant)}'

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choice(['difference_of_squares', 'common_factor'])

        if subtype == 'difference_of_squares':
            a = rng.choice([1, 2, 3])
            b = rng.choice([2, 3, 4, 5])
            leading = self._coeff_x_term(a, 2)
            constant = a * (b**2)
            prompt = f'Forkort uttrykket (for $x \\neq {b}$)\n$$\\frac{{{leading} - {constant}}}{{x - {b}}}$$'
            answer = f'{a}*(x+{b})' if a != 1 else f'x+{b}'
            factor_prefix = '' if a == 1 else str(a)
            steps = [
                f'Bruk kvadratsetningen: {leading} - {constant} = {factor_prefix}(x^2-{b**2}).' if a != 1 else f'Bruk kvadratsetningen: {leading} - {constant} = x^2-{b**2}.',
                f'Faktoriser: {factor_prefix}(x-{b})(x+{b}).' if a != 1 else f'Faktoriser: (x-{b})(x+{b}).',
                f'Forkort med (x-{b}).',
                f'Svar: {answer}.',
            ]
        else:
            k = rng.choice([2, 3, 4, 5])
            m = rng.choice([1, 2, 3, 4])
            n = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
            linear_display = self._linear_display(m, n)
            prompt = f'Forkort uttrykket (for $x \\neq 0$)\n$$\\frac{{{k}x({linear_display})}}{{{k}x}}$$'
            answer = self._linear_answer_expr(m, n)
            steps = [
                f'Telleren er et produkt: {k}x({linear_display}).',
                f'Forkort med {k}x i teller og nevner.',
                f'Svar: {linear_display}.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=answer,
            solution_short=f'Uttrykket blir {answer}.',
            solution_steps=steps,
            metadata={'tema': 'algebra', 'difficulty': 2, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
