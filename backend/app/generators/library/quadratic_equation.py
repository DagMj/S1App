from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class QuadraticEquationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='quadratic_equation',
            name='Andregradslikninger',
            description='Andregradslikninger med heltallsrøtter og varierende ledende koeffisient.',
            tema='Likninger',
            part='del1',
            answer_type='solution_set',
            difficulty=3,
            default_weight=1.1,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')

        r1 = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
        r2 = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
        while r2 == r1:
            r2 = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])

        lead = rng.choice([1, 2, 3])
        expr = sp.expand(lead * (x - r1) * (x - r2))

        prompt = f'Løs likningen $$ {sp.latex(expr)} = 0 $$'
        roots = sorted([r1, r2])

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='solution_set',
            correct_answer=roots,
            solution_short=f'Løsningsmengde: $\\{{{roots[0]}, {roots[1]}\\}}$',
            solution_steps=[
                f'Likningen kan skrives som ${lead}(x-{r1})(x-{r2})=0$.',
                'Bruk nullproduktregelen: et produkt er null når minst én faktor er null.',
                f'Svar: $x={r1}$ eller $x={r2}$.',
            ],
            metadata={'tema': 'likninger', 'difficulty': 3, 'latex': True},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
