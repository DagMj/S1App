from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _x_shift(value: int) -> str:
    if value >= 0:
        return f'x+{value}'
    return f'x-{abs(value)}'


class LinearEquationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='linear_equation',
            name='Lineære likninger',
            description='Lineære likninger på eksamensnivå med pene tall.',
            tema='Likninger',
            part='del1',
            answer_type='number',
            difficulty=2,
            default_weight=1.3,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choice(['one_side', 'two_side'])

        if subtype == 'one_side':
            x = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            a = rng.choice([2, 3, 4, 5, 6, 7])
            b = rng.choice([-12, -10, -8, -6, -4, -2, 2, 4, 6, 8, 10, 12])
            c = a * x + b

            abs_b = abs(b)
            b_sign = '+' if b >= 0 else '-'
            prompt = f'Løs likningen $$ {a}x {b_sign} {abs_b} = {c} $$'
            step_1 = (
                f'Trekk fra {abs_b} på begge sider.'
                if b >= 0
                else f'Legg til {abs_b} på begge sider.'
            )
            steps = [
                step_1,
                f'Da får vi ${a}x = {c - b}$.',
                f'Del på ${a}$: $x = {x}$.',
            ]
        else:
            x = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            a = rng.choice([2, 3, 4, 5])
            c = rng.choice([1, 2, 3, 4])
            while c == a:
                c = rng.choice([1, 2, 3, 4])

            b = rng.choice([-6, -4, -2, 2, 4, 6])
            d = rng.choice([-5, -3, -1, 1, 3, 5])
            e = a * (x + b) - c * (x + d)

            prompt = f'Løs likningen $$ {a}({_x_shift(b)}) = {c}({_x_shift(d)}) + {e} $$'
            steps = [
                f'Utvid parentesene: ${a}({_x_shift(b)}) = {c}({_x_shift(d)}) + {e}$.',
                'Flytt ledd med $x$ til venstre og tall til høyre.',
                f'Da får vi $x = {x}$.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=x,
            solution_short=f'$x = {x}$',
            solution_steps=steps,
            metadata={'tema': 'likninger', 'difficulty': 2, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
