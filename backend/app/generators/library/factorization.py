from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class FactorizationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='factorization',
            name='Faktorisering',
            description=(
                'Faktorisering av andregradsuttrykk: enkle (a=1), kvadratsetningene '
                'og vanskeligere uttrykk (a>1).'
            ),
            tema='Algebra',
            part='del1',
            answer_type='expression',
            difficulty=3,
            default_weight=1.0,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')

        # Weights: simple 20, sq1 15, sq2 15, diff_sq 20, hard 30
        subtype = rng.choices(
            ['simple', 'sq1', 'sq2', 'diff_sq', 'hard'],
            weights=[20, 15, 15, 20, 30],
        )[0]

        if subtype == 'simple':
            # (x+p)(x+q), p≠q, a=1
            p = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            q = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            while q == p:
                q = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            expr = sp.expand((x + p) * (x + q))
            factored = (x + p) * (x + q)
            f1 = _shift_factor(p)
            f2 = _shift_factor(q)
            prompt = f'Faktoriser uttrykket $$ {sp.latex(expr)} $$'
            solution_steps = [
                f'Finn to tall som multiplisert gir ${p * q}$ og addert gir ${p + q}$.',
                f'Tallene er ${p}$ og ${q}$.',
                f'Svar: ${f1}{f2}$.',
            ]

        elif subtype == 'sq1':
            # 1. kvadratsetning: (x+n)² = x² + 2nx + n²
            n = rng.choice([2, 3, 4, 5, 6])
            expr = sp.expand((x + n) ** 2)
            factored = (x + n) ** 2
            f1 = _shift_factor(n)
            prompt = f'Faktoriser uttrykket $$ {sp.latex(expr)} $$'
            solution_steps = [
                'Gjenkjenn 1. kvadratsetning: $a^2 + 2ab + b^2 = (a+b)^2$.',
                f'Her er $a=x$ og $b={n}$, siden $2 \\cdot x \\cdot {n} = {2*n}x$ og ${n}^2 = {n**2}$.',
                f'Svar: $(x+{n})^2$.',
            ]

        elif subtype == 'sq2':
            # 2. kvadratsetning: (x−n)² = x² − 2nx + n²
            n = rng.choice([2, 3, 4, 5, 6])
            expr = sp.expand((x - n) ** 2)
            factored = (x - n) ** 2
            prompt = f'Faktoriser uttrykket $$ {sp.latex(expr)} $$'
            solution_steps = [
                'Gjenkjenn 2. kvadratsetning: $a^2 - 2ab + b^2 = (a-b)^2$.',
                f'Her er $a=x$ og $b={n}$, siden $2 \\cdot x \\cdot {n} = {2*n}x$ og ${n}^2 = {n**2}$.',
                f'Svar: $(x-{n})^2$.',
            ]

        elif subtype == 'diff_sq':
            # 3. kvadratsetning: (x+n)(x−n) = x² − n²
            n = rng.choice([2, 3, 4, 5, 6, 7])
            expr = sp.expand((x + n) * (x - n))
            factored = (x + n) * (x - n)
            prompt = f'Faktoriser uttrykket $$ {sp.latex(expr)} $$'
            solution_steps = [
                'Gjenkjenn 3. kvadratsetning (konjugatsetningen): $a^2 - b^2 = (a+b)(a-b)$.',
                f'Her er $a=x$ og $b={n}$, siden $x^2 - {n}^2 = x^2 - {n**2}$.',
                f'Svar: $(x+{n})(x-{n})$.',
            ]

        else:
            # hard: (mx+p)(nx+q), m,n > 0, at least one > 1
            m = rng.choice([2, 3])
            nv = rng.choice([1, 2, 3])
            p = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            q = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            expr = sp.expand((m * x + p) * (nv * x + q))
            factored = sp.factor(expr)
            f1 = _linear_factor(m, p)
            f2 = _linear_factor(nv, q)
            prompt = f'Faktoriser uttrykket $$ {sp.latex(expr)} $$'
            lead = m * nv
            solution_steps = [
                f'Finn to faktorer av formen $({_coeff_str(m)}x+p)({_coeff_str(nv)}x+q)$.',
                f'Andregradsleddet er ${lead}x^2$ og konstantleddet er ${p * q}$.',
                f'Svar: ${f1}{f2}$.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=sp.sstr(factored),
            solution_short=f'${sp.latex(factored)}$',
            solution_steps=solution_steps,
            metadata={'tema': 'algebra', 'difficulty': 3, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)


def _shift_factor(n: int) -> str:
    """Format (x+n) or (x-n)."""
    if n >= 0:
        return f'(x+{n})'
    return f'(x-{abs(n)})'


def _linear_factor(coeff: int, const: int) -> str:
    """Format (coeff*x + const)."""
    c = '' if coeff == 1 else str(coeff)
    if const > 0:
        return f'({c}x+{const})'
    if const < 0:
        return f'({c}x-{abs(const)})'
    return f'({c}x)'


def _coeff_str(n: int) -> str:
    return '' if n == 1 else str(n)
