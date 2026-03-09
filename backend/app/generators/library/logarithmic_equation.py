from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _ax_display(a: int) -> str:
    return 'x' if a == 1 else f'{a}x'


class LogarithmicEquationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='logarithmic_equation',
            name='Logaritmelikninger',
            description='Logaritmelikninger med lineært uttrykk eller log-regler.',
            tema='Logaritmer',
            part='del1',
            answer_type='number',
            difficulty=3,
            default_weight=0.9,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choice(['shifted', 'sum_logs'])

        if subtype == 'shifted':
            base = rng.choice([2, 3, 5, 10])
            exp = rng.choice([1, 2, 3])
            rhs = base**exp
            a = rng.choice([1, 2, 3, 4])
            x = rng.choice([1, 2, 3, 4, 5, 6, 7])
            c = rhs - a * x
            while abs(c) > 12:
                x = rng.choice([1, 2, 3, 4, 5, 6, 7])
                c = rhs - a * x

            c_sign = '+' if c >= 0 else '-'
            c_abs = abs(c)
            ax = _ax_display(a)
            prompt = f'Løs likningen $$\\log_{{{base}}}({ax} {c_sign} {c_abs}) = {exp}$$'
            steps = [
                f'Skriv om til eksponentialform: ${ax} {c_sign} {c_abs} = {base}^{{{exp}}} = {rhs}$.',
                f'Løs den lineære likningen: $x = {x}$.',
                f'Svar: $x = {x}$.',
            ]
        else:
            base = rng.choice([2, 3, 5, 10])
            m = rng.choice([1, 2, 3, 4])
            x = rng.choice([m + 2, m + 3, m + 4, m + 5])
            rhs = x * (x - m)
            prompt = (
                f'Løs likningen $$\\log_{{{base}}}(x) + \\log_{{{base}}}(x-{m}) '
                f'= \\log_{{{base}}}({rhs})$$'
            )
            steps = [
                f'Domene: $x > {m}$.',
                f'Bruk log-regel: $\\log_{{{base}}}(x) + \\log_{{{base}}}(x-{m}) = \\log_{{{base}}}(x(x-{m}))$.',
                f'Da får vi $x(x-{m}) = {rhs}$, som gir $x = {x}$ i domenet.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=x,
            solution_short=f'$x = {x}$',
            solution_steps=steps,
            metadata={'tema': 'logaritmer', 'difficulty': 3, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
