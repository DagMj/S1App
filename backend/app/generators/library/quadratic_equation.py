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
            description='Andregradslikninger med heltallsrøtter – faktorisering og abc-formelen.',
            tema='Likninger',
            part='del1',
            answer_type='solution_set',
            difficulty=3,
            default_weight=1.1,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')

        # factoring_a1: a=1, vis fremgangsmåte uten å avsløre faktorene direkte
        # abc_formula: vis abc-formelen steg for steg
        subtype = rng.choices(
            ['factoring_a1', 'factoring_lead', 'abc_formula'],
            weights=[35, 25, 40],
        )[0]

        r1 = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
        r2 = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
        while r2 == r1:
            r2 = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
        roots = sorted([r1, r2])

        if subtype == 'factoring_a1':
            # x² + bx + c = 0  (lead = 1)
            b_coeff = -(r1 + r2)
            c_coeff = r1 * r2
            expr = sp.expand((x - r1) * (x - r2))
            prompt = f'Løs likningen $$ {sp.latex(expr)} = 0 $$'
            p, q = -r1, -r2  # tall med sum=b_coeff, produkt=c_coeff
            steps = [
                f'Vi søker to tall $p$ og $q$ slik at $p + q = {b_coeff}$ og $p \\cdot q = {c_coeff}$.',
                f'Tallene er $p = {p}$ og $q = {q}$.',
                f'Likningen faktoriserer til $(x + {p})(x + {q}) = 0$.',
                f'Nullproduktregelen gir $x = {r1}$ eller $x = {r2}$.',
            ]

        elif subtype == 'factoring_lead':
            # lead*(x-r1)*(x-r2) = 0  (lead = 2 eller 3)
            lead = rng.choice([2, 3])
            expr = sp.expand(lead * (x - r1) * (x - r2))
            prompt = f'Løs likningen $$ {sp.latex(expr)} = 0 $$'
            b_coeff = int(expr.coeff(x, 1))
            c_coeff = int(expr.coeff(x, 0))
            steps = [
                f'Del likningen på ${lead}$: $x^2 {sp.latex(sp.expand((x - r1) * (x - r2)))} = 0$.',
                f'Finn to tall med sum $= {-(r1 + r2)}$ og produkt $= {r1 * r2}$.',
                f'Faktoriser: $(x - {r1})(x - {r2}) = 0$.',
                f'Nullproduktregelen gir $x = {r1}$ eller $x = {r2}$.',
            ]

        else:  # abc_formula
            lead = rng.choice([1, 2, 3])
            expr = sp.expand(lead * (x - r1) * (x - r2))
            a_val = int(expr.coeff(x, 2))
            b_val = int(expr.coeff(x, 1))
            c_val = int(expr.coeff(x, 0))
            disc = b_val**2 - 4 * a_val * c_val  # = lead²*(r1-r2)²
            sqrt_disc = int(disc**0.5)
            prompt = f'Løs likningen $$ {sp.latex(expr)} = 0 $$'
            x1_num = -b_val + sqrt_disc
            x2_num = -b_val - sqrt_disc
            denom = 2 * a_val
            steps = [
                r'Bruk abc-formelen: $x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.',
                f'Her er $a = {a_val}$, $b = {b_val}$, $c = {c_val}$.',
                f'Diskriminanten: $D = {b_val}^2 - 4 \\cdot {a_val} \\cdot {c_val} = {disc}$.',
                f'$x = \\dfrac{{{-b_val} \\pm {sqrt_disc}}}{{{denom}}}$',
                f'Svar: $x = {roots[0]}$ eller $x = {roots[1]}$.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='solution_set',
            correct_answer=roots,
            solution_short=f'Løsningsmengde: $\\{{{roots[0]}, {roots[1]}\\}}$',
            solution_steps=steps,
            metadata={
                'tema': 'likninger',
                'difficulty': 3,
                'latex': True,
                'subtype': subtype,
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
