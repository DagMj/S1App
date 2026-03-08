from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _linear_factor(coeff: int, const: int) -> str:
    coeff_part = 'x' if coeff == 1 else f'{coeff}x'
    if const > 0:
        return f'({coeff_part}+{const})'
    return f'({coeff_part}{const})'


class FactorizationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='factorization',
            name='Faktorisering',
            description='Faktorisering av andregradsuttrykk med koeffisienter.',
            tema='Algebra',
            part='del1',
            answer_type='expression',
            difficulty=3,
            default_weight=1.0,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')

        m = rng.choice([1, 2, 3])
        p = rng.choice([1, 2, 3])
        n = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
        q = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])

        expr = sp.expand((m * x + n) * (p * x + q))
        factored = sp.factor(expr)

        factor_left = _linear_factor(m, n)
        factor_right = _linear_factor(p, q)

        prompt = f'Faktoriser uttrykket $$ {sp.latex(expr)} $$'

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=sp.sstr(factored),
            solution_short=f'Faktorisert form er {factor_left}{factor_right}.',
            solution_steps=[
                'Se etter to faktorer som gir riktig andregradsledd og konstantledd.',
                f'Et passende produkt er {factor_left}{factor_right}.',
                f'Svar: {factor_left}{factor_right}.',
            ],
            metadata={'tema': 'algebra', 'difficulty': 3, 'latex': True},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
