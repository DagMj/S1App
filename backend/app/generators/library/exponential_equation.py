from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution, format_x_shift_latex


def _linear_latex(coeff: int, constant: int) -> str:
    coeff_part = 'x' if coeff == 1 else f'{coeff}x'
    if constant == 0:
        return coeff_part
    sign = '+' if constant > 0 else '-'
    return f'{coeff_part}{sign}{abs(constant)}'


class ExponentialEquationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='exponential_equation',
            name='Eksponentiallikninger',
            description='Eksponentiallikninger med omskriving av baser.',
            tema='Eksponentialfunksjoner',
            part='del2',
            answer_type='number',
            difficulty=3,
            default_weight=1.0,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choice(['same_base', 'base_rewrite'])

        if subtype == 'same_base':
            base = rng.choice([2, 3, 5])
            shift = rng.choice([-3, -2, -1, 0, 1, 2, 3])
            x = rng.choice([1, 2, 3, 4, 5, 6])
            exponent = x - shift
            rhs = base**exponent
            shifted_x = format_x_shift_latex(shift)
            prompt = f'Løs likningen $$ {base}^{{{shifted_x}}} = {rhs} $$'
            steps = [
                f'Skriv {rhs} som {base}^{exponent}.',
                f'Sett eksponentene like: {shifted_x} = {exponent}.',
                f'Løs for x: x = {x}.',
            ]
        else:
            base = rng.choice([2, 3])
            k = rng.choice([2, 3])
            p = rng.choice([-2, -1, 0, 1, 2])
            q = rng.choice([1, 2, 3, 4, 5])
            while q == k:
                q = rng.choice([1, 2, 3, 4, 5])

            x = rng.choice([-2, -1, 0, 1, 2, 3, 4, 5])
            r = k * (x + p) - q * x

            left_base = base**k
            p_latex = format_x_shift_latex(-p)
            right_exponent = _linear_latex(q, r)
            prompt = f'Løs likningen $$ {left_base}^{{{p_latex}}} = {base}^{{{right_exponent}}} $$'
            steps = [
                f'Skriv venstresiden med samme grunntall: {left_base}= {base}^{k}.',
                f'Da får vi eksponentlikning: {k}({p_latex}) = {right_exponent}.',
                f'Løs for x: x = {x}.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=x,
            solution_short=f'x = {x}',
            solution_steps=steps,
            metadata={'tema': 'eksponentiallikning', 'difficulty': 3, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
