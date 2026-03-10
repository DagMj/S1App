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
            description='Logaritmelikninger: lineært uttrykk, log-regler, potensregel og differanse.',
            tema='Logaritmer',
            part='del1',
            answer_type='number',
            difficulty=3,
            default_weight=0.9,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choices(
            ['shifted', 'sum_logs', 'power_log', 'log_difference'],
            weights=[25, 25, 25, 25],
        )[0]

        if subtype == 'shifted':
            # log_b(ax + c) = exp
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

        elif subtype == 'sum_logs':
            # log_b(x) + log_b(x-m) = log_b(rhs)
            base = rng.choice([2, 3, 5, 10])
            m = rng.choice([1, 2, 3, 4])
            x = rng.choice([m + 2, m + 3, m + 4, m + 5])
            rhs = x * (x - m)
            prompt = (
                f'Løs likningen $$\\log_{{{base}}}(x) + \\log_{{{base}}}(x-{m}) '
                f'= \\log_{{{base}}}({rhs})$$'
            )
            steps = [
                f'Domene: $x > {m}$ (begge logaritmer må være definert).',
                f'Bruk log-regel: $\\log_{{{base}}}(x) + \\log_{{{base}}}(x-{m}) = \\log_{{{base}}}(x(x-{m}))$.',
                f'Da får vi $x(x-{m}) = {rhs}$, dvs. $x^2 - {m}x - {rhs} = 0$.',
                f'Løsningene er $x = {x}$ og $x = {-(x - m)}$. Siden $x > {m}$ beholdes bare $x = {x}$.',
            ]

        elif subtype == 'power_log':
            # n * log_b(x) = n*exp  →  log_b(x) = exp  →  x = b^exp
            base = rng.choice([2, 3, 10])
            n = rng.choice([2, 3])
            exp = rng.choice([1, 2])
            x = base**exp
            rhs = n * exp  # n * log_b(x) = n*exp (høyresiden som tall)
            prompt = (
                f'Løs likningen $${n} \\cdot \\log_{{{base}}}(x) = {rhs}$$'
            )
            steps = [
                f'Del begge sider på ${n}$: $\\log_{{{base}}}(x) = {exp}$.',
                f'Skriv om til eksponentialform: $x = {base}^{{{exp}}}$.',
                f'Svar: $x = {x}$.',
            ]

        else:  # log_difference
            # log_b(x) - log_b(x-m) = 1  →  x/(x-m) = b  →  x = b*m/(b-1)
            base = rng.choice([2, 3])
            if base == 2:
                m = rng.choice([1, 2, 3, 4])
            else:  # base == 3
                m = rng.choice([2, 4])  # gir heltallsverdi for x = 3m/2
            x = base * m // (base - 1)
            prompt = (
                f'Løs likningen $$\\log_{{{base}}}(x) - \\log_{{{base}}}(x-{m}) = 1$$'
            )
            steps = [
                f'Domene: $x > {m}$.',
                f'Bruk log-regel: $\\log_{{{base}}}(x) - \\log_{{{base}}}(x-{m}) = \\log_{{{base}}}\\!\\left(\\dfrac{{x}}{{x-{m}}}\\right)$.',
                f'Da: $\\dfrac{{x}}{{x-{m}}} = {base}^1 = {base}$.',
                f'Løs: $x = {base}(x-{m}) \\Rightarrow x(1-{base}) = -{base} \\cdot {m} \\Rightarrow x = {x}$.',
                f'Kontroll: $x = {x} > {m}$ ✓',
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
