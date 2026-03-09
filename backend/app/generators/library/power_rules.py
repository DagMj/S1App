from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class PowerRulesGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='power_rules',
            name='Potensregning',
            description='Forenkling av potensuttrykk med flere variabler og røtter.',
            tema='Potenser',
            part='del1',
            answer_type='expression',
            difficulty=3,
            default_weight=1.0,
        )

    @staticmethod
    def _format_answer(exp_a: int, exp_b: int) -> str:
        factors: list[str] = []
        if exp_a > 0:
            factors.append('a' if exp_a == 1 else f'a**{exp_a}')
        if exp_b > 0:
            factors.append('b' if exp_b == 1 else f'b**{exp_b}')
        return '*'.join(factors) if factors else '1'

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choice(['fraction', 'nested', 'root'])

        if subtype == 'fraction':
            a_top = rng.choice([5, 6, 7, 8])
            a_bottom = rng.choice([2, 3, 4])
            b_top = rng.choice([4, 5, 6, 7])
            b_bottom = rng.choice([1, 2, 3])

            exp_a = a_top - a_bottom
            exp_b = b_top - b_bottom

            prompt = f'Forenkle uttrykket $$\\frac{{a^{{{a_top}}}b^{{{b_top}}}}}{{a^{{{a_bottom}}}b^{{{b_bottom}}}}}$$'
            answer = self._format_answer(exp_a, exp_b)
            steps = [
                'Bruk regelen $a^m/a^n=a^{m-n}$ på hver variabel.',
                f'For $a$: $a^{{{a_top}}}/a^{{{a_bottom}}}=a^{{{exp_a}}}$.',
                f'For $b$: $b^{{{b_top}}}/b^{{{b_bottom}}}=b^{{{exp_b}}}$.',
                f'Svar: ${answer}$.',
            ]

        elif subtype == 'nested':
            p = rng.choice([2, 3, 4])
            q = rng.choice([1, 2, 3])
            k = rng.choice([2, 3])
            # Clamp r and s so exponents stay positive (avoid silently dropping factors)
            r = rng.randint(1, p * k - 1)
            s = rng.randint(1, q * k - 1)

            exp_a = p * k - r
            exp_b = q * k - s

            prompt = (
                f'Forenkle uttrykket $$\\frac{{(a^{{{p}}}b^{{{q}}})^{{{k}}}}}{{a^{{{r}}}b^{{{s}}}}}$$'
            )
            answer = self._format_answer(exp_a, exp_b)
            steps = [
                'Bruk regelen $(xy)^n=x^ny^n$ og $(x^m)^n=x^{mn}$.',
                f'Telleren blir $a^{{{p * k}}}b^{{{q * k}}}$.',
                f'Trekk fra eksponentene i nevneren: $a^{{{p * k}-{r}}}b^{{{q * k}-{s}}}=a^{{{exp_a}}}b^{{{exp_b}}}$.',
                f'Svar: ${answer}$.',
            ]

        else:
            root_a = rng.choice([3, 4, 5])
            root_b = rng.choice([2, 3, 4])
            reduce_a = rng.choice([1, 2])
            reduce_b = rng.choice([1, 2])

            exp_a = root_a - reduce_a
            exp_b = root_b - reduce_b
            answer = self._format_answer(exp_a, exp_b)

            prompt = (
                'Anta at $a>0$ og $b>0$. '
                f'Forenkle uttrykket $$\\frac{{\\sqrt{{a^{{{2 * root_a}}}b^{{{2 * root_b}}}}}}}{{a^{{{reduce_a}}}b^{{{reduce_b}}}}}$$'
            )
            steps = [
                'Bruk regelen $\\sqrt{a^{2n}}=a^n$ når $a>0$.',
                f'Nevneren i roten gir $\\sqrt{{a^{{{2 * root_a}}}b^{{{2 * root_b}}}}}=a^{{{root_a}}}b^{{{root_b}}}$.',
                f'Deretter $a^{{{root_a}}}/a^{{{reduce_a}}}=a^{{{exp_a}}}$ og $b^{{{root_b}}}/b^{{{reduce_b}}}=b^{{{exp_b}}}$.',
                f'Svar: ${answer}$.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=answer,
            solution_short=f'Svar: {answer}.',
            solution_steps=steps,
            metadata={'tema': 'potensregning', 'difficulty': 3, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
