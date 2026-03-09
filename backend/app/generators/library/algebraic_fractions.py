from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class AlgebraicFractionsGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='algebraic_fractions',
            name='Algebraiske brøker',
            description='Regning med algebraiske brøker med ulik nevner.',
            tema='Algebra',
            part='del1',
            answer_type='expression',
            difficulty=3,
            default_weight=1.1,
        )

    @staticmethod
    def _fmt(v: int) -> str:
        return f'x+{v}' if v >= 0 else f'x-{abs(v)}'

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')

        subtype = rng.choice(['two_frac', 'three_frac'])

        if subtype == 'two_frac':
            a = rng.choice([1, 2, 3, 4, 5])
            c = rng.choice([1, 2, 3, 4, 5])
            b = rng.choice([1, 2, 3, 4])
            op = rng.choice(['+', '-'])

            left = sp.Rational(a, 1) / (x + b)
            right = sp.Rational(c, 1) / (x - b)

            if op == '+':
                expr = left + right
                prompt = f'Regn ut og forkort uttrykket\n$$\\frac{{{a}}}{{x+{b}}}+\\frac{{{c}}}{{x-{b}}}$$'
                step_join = 'Legg sammen tellerne etter utviding til fellesnevner.'
            else:
                expr = left - right
                prompt = f'Regn ut og forkort uttrykket\n$$\\frac{{{a}}}{{x+{b}}}-\\frac{{{c}}}{{x-{b}}}$$'
                step_join = 'Trekk fra tellerne etter utviding til fellesnevner.'

            simplified = sp.together(sp.simplify(expr))
            answer = sp.sstr(simplified)

            return ProblemData(
                generator_key=self.metadata().key,
                part='del1',
                prompt=prompt,
                answer_type='expression',
                correct_answer=answer,
                solution_short=f'Svar: {sp.latex(simplified)}',
                solution_steps=[
                    f'Fellesnevner er (x+{b})(x-{b}) = x^2-{b**2}.',
                    step_join,
                    f'Forkort uttrykket til: {sp.latex(simplified)}.',
                ],
                metadata={'tema': 'algebra', 'difficulty': 3, 'latex': True, 'subtype': 'two_frac'},
                assets=[],
                seed=seed or rng.randint(1, 10**9),
            )

        # three_frac: a/(x+p) OP b/(x+q) OP c/((x+p)(x+q))
        p = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        q_pool = [v for v in [-4, -3, -2, -1, 1, 2, 3, 4] if v != p]
        q = rng.choice(q_pool)

        a = rng.choice([1, 2, 3, 4, 5])
        b = rng.choice([1, 2, 3, 4, 5])
        c = rng.choice([1, 2, 3, 4, 5, 6, 8, 10])
        op1 = rng.choice(['+', '-'])
        op2 = rng.choice(['+', '-'])

        s2 = 1 if op1 == '+' else -1
        s3 = 1 if op2 == '+' else -1

        expr = (
            sp.Rational(a) / (x + p)
            + s2 * sp.Rational(b) / (x + q)
            + s3 * sp.Rational(c) / ((x + p) * (x + q))
        )
        simplified = sp.together(sp.simplify(expr))
        answer = sp.sstr(simplified)

        fp, fq = self._fmt(p), self._fmt(q)
        frac1 = f'\\frac{{{a}}}{{{fp}}}'
        frac2 = f'\\frac{{{b}}}{{{fq}}}'
        frac3 = f'\\frac{{{c}}}{{({fp})({fq})}}'
        prompt = f'Regn ut og forkort uttrykket\n$${frac1}{op1}{frac2}{op2}{frac3}$$'

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=answer,
            solution_short=f'Svar: {sp.latex(simplified)}',
            solution_steps=[
                f'Fellesnevner er ({fp})({fq}).',
                'Utvid de to første brøkene til fellesnevner.',
                f'Legg sammen alle tellerne og forkort: {sp.latex(simplified)}.',
            ],
            metadata={'tema': 'algebra', 'difficulty': 3, 'latex': True, 'subtype': 'three_frac'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)

