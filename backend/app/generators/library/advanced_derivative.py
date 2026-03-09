from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class AdvancedDerivativeGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='advanced_derivative',
            name='Derivasjon (produkt, kjede, brøk)',
            description='Derivasjonsoppgaver med produktregel, kjerneregel og brøkregel.',
            tema='Derivasjon',
            part='del2',
            answer_type='function',
            difficulty=4,
            default_weight=0.8,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')
        subtype = rng.choice(['product', 'chain', 'quotient'])

        if subtype == 'product':
            a = rng.choice([1, 2, 3, 4])
            b = rng.choice([-4, -3, -2, 2, 3, 4])
            c = rng.choice([1, 2, 3])
            d = rng.choice([1, 2, 3, 4, 5])
            expr = (a * x + b) * (c * x**2 + d)
            derivative = sp.expand(sp.diff(expr, x))
            steps = [
                "Bruk produktregelen: (uv)' = u'v + uv'.",
                f'Sett u={sp.latex(a * x + b)} og v={sp.latex(c * x**2 + d)}.',
                f'Da blir f\'(x)={sp.latex(derivative)}.',
            ]

        elif subtype == 'chain':
            a = rng.choice([2, 3, 4])
            b = rng.choice([-3, -2, -1, 1, 2, 3])
            n = rng.choice([3, 4, 5])
            expr = (a * x + b) ** n
            # Keep factored form — more readable and matches hand-written chain-rule answer
            derivative = sp.diff(expr, x)
            steps = [
                "Bruk kjerneregel: (g(x)^n)' = n·g(x)^{n-1}·g'(x).",
                f'Her er g(x)={sp.latex(a * x + b)} og g\'(x)={a}.',
                f'Da blir f\'(x)={sp.latex(derivative)}.',
            ]

        else:
            a = rng.choice([2, 3, 4, 5])
            b = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            c = rng.choice([1, 2, 3])
            d = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
            while a * d - b * c == 0:
                d = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])

            expr = (a * x + b) / (c * x + d)
            derivative = sp.simplify(sp.diff(expr, x))
            steps = [
                "Bruk brøkregelen: (u/v)' = (u'v - uv')/v^2.",
                f'Sett u={sp.latex(a * x + b)} og v={sp.latex(c * x + d)}.',
                f'Da blir f\'(x)={sp.latex(derivative)}.',
            ]

        expr_latex = sp.latex(expr)
        derivative_latex = sp.latex(derivative)

        prompt = (
            'Deriver funksjonen\n'
            f'$$f(x)={expr_latex}$$\n'
            'Oppgi svaret som $f\'(x)$. '
            'Du kan bruke produktregel, kjerneregel eller brøkregel der det passer.'
        )

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='function',
            correct_answer=sp.sstr(derivative),
            solution_short=f"f'(x) = {derivative_latex}",
            solution_steps=steps,
            metadata={'tema': 'derivasjon', 'difficulty': 4, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
