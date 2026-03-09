from __future__ import annotations

import random

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution

_INEQ_LAT = {'<': '<', '<=': r'\leq', '>': '>', '>=': r'\geq'}
_INEQ_FLIP = {'<': '>', '<=': '>=', '>': '<', '>=': '<='}


def _x_shift(value: int) -> str:
    if value >= 0:
        return f'x+{value}'
    return f'x-{abs(value)}'


def _interval(boundary: int, ineq: str) -> str:
    """Correct answer string in interval notation for x [ineq] boundary."""
    if ineq == '<':
        return f'(-oo, {boundary})'
    if ineq == '<=':
        return f'(-oo, {boundary}]'
    if ineq == '>':
        return f'({boundary}, oo)'
    return f'[{boundary}, oo)'


def _interval_lat(boundary: int, ineq: str) -> str:
    """LaTeX interval string."""
    if ineq == '<':
        return f'$(-\\infty, {boundary})$'
    if ineq == '<=':
        return f'$(-\\infty, {boundary}]$'
    if ineq == '>':
        return f'$({boundary}, \\infty)$'
    return f'$[{boundary}, \\infty)$'


_INEQ_PROMPT_SUFFIX = (
    '\nSkriv svaret som et intervall, f.eks. $(-\\infty, 3)$ eller $[5, \\infty)$.'
)


class LinearEquationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='linear_equation',
            name='Lineære likninger og ulikheter',
            description='Lineære ligninger og ulikheter med varierende kompleksitet, inkl. parentesuttrykk.',
            tema='Likninger',
            part='del1',
            answer_type='number',
            difficulty=2,
            default_weight=1.3,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        # 15% one_side, 15% two_side, 25% ineq_simple, 20% ineq_paren, 25% advanced_eq
        subtype = rng.choices(
            ['one_side', 'two_side', 'ineq_simple', 'ineq_paren', 'advanced_eq'],
            weights=[15, 15, 25, 20, 25],
        )[0]

        if subtype == 'one_side':
            x = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            a = rng.choice([2, 3, 4, 5, 6, 7])
            b = rng.choice([-12, -10, -8, -6, -4, -2, 2, 4, 6, 8, 10, 12])
            c = a * x + b

            abs_b = abs(b)
            b_sign = '+' if b >= 0 else '-'
            prompt = f'Løs likningen $$ {a}x {b_sign} {abs_b} = {c} $$'
            step_1 = (
                f'Trekk fra ${abs_b}$ på begge sider.'
                if b >= 0
                else f'Legg til ${abs_b}$ på begge sider.'
            )
            steps = [
                step_1,
                f'Da får vi ${a}x = {c - b}$.',
                f'Del på ${a}$: $x = {x}$.',
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

        elif subtype == 'two_side':
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

        elif subtype == 'ineq_simple':
            # ax + b [ineq] c, solution x [ineq] x_val (a always positive → no flip)
            x_val = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            a = rng.choice([2, 3, 4, 5, 6])
            b = rng.choice([-12, -10, -8, -6, -4, -2, 2, 4, 6, 8, 10, 12])
            c = a * x_val + b
            ineq = rng.choice(['<', '<=', '>', '>='])
            il = _INEQ_LAT[ineq]

            abs_b, b_sign = abs(b), ('+' if b >= 0 else '-')
            prompt = f'Løs ulikheten $$ {a}x {b_sign} {abs_b} {il} {c} $$' + _INEQ_PROMPT_SUFFIX
            step1 = (
                f'Trekk fra ${abs_b}$ på begge sider.'
                if b >= 0
                else f'Legg til ${abs_b}$ på begge sider.'
            )
            steps = [
                step1,
                f'Da får vi ${a}x {il} {c - b}$.',
                f'Del på ${a}$: $x {il} {x_val}$.',
                f'Svar: {_interval_lat(x_val, ineq)}.',
            ]
            return ProblemData(
                generator_key=self.metadata().key,
                part='del1',
                prompt=prompt,
                answer_type='interval',
                correct_answer=_interval(x_val, ineq),
                solution_short=_interval_lat(x_val, ineq),
                solution_steps=steps,
                metadata={'tema': 'ulikheter', 'difficulty': 2, 'latex': True, 'subtype': subtype},
                assets=[],
                seed=seed or rng.randint(1, 10**9),
            )

        elif subtype == 'ineq_paren':
            # a(x+b) [ineq] c(x+d) + e, with a > c so no flip when collecting x-terms
            x_val = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            a = rng.choice([3, 4, 5, 6])
            c = rng.choice([1, 2])          # a > c always
            b = rng.choice([-3, -2, -1, 1, 2, 3])
            d = rng.choice([-3, -2, -1, 1, 2, 3])
            e = a * (x_val + b) - c * (x_val + d)
            ineq = rng.choice(['<', '<=', '>', '>='])
            il = _INEQ_LAT[ineq]

            e_str = '' if e == 0 else (f' + {e}' if e > 0 else f' - {abs(e)}')
            prompt = (
                f'Løs ulikheten $$ {a}({_x_shift(b)}) {il} {c}({_x_shift(d)}){e_str} $$'
                + _INEQ_PROMPT_SUFFIX
            )

            xs = sp.Symbol('x')
            lhs_exp = sp.latex(sp.expand(a * (xs + b)))
            rhs_exp = sp.latex(sp.expand(c * (xs + d) + e))
            coeff = a - c
            rhs_num = (a - c) * x_val  # = e - a*b + c*d simplified

            steps = [
                f'Utvid parentesene: ${lhs_exp} {il} {rhs_exp}$.',
                f'Samle $x$-ledd: ${coeff}x {il} {rhs_num}$.',
                f'Del på ${coeff}$: $x {il} {x_val}$.',
                f'Svar: {_interval_lat(x_val, ineq)}.',
            ]
            return ProblemData(
                generator_key=self.metadata().key,
                part='del1',
                prompt=prompt,
                answer_type='interval',
                correct_answer=_interval(x_val, ineq),
                solution_short=_interval_lat(x_val, ineq),
                solution_steps=steps,
                metadata={'tema': 'ulikheter', 'difficulty': 3, 'latex': True, 'subtype': subtype},
                assets=[],
                seed=seed or rng.randint(1, 10**9),
            )

        else:  # advanced_eq
            # a(x+b) + c(x+d) = e — two parentheses, solve for x
            x_val = rng.choice([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6])
            a = rng.choice([2, 3, 4, 5])
            b = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            c = rng.choice([1, 2, 3, 4])
            d = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            e = a * (x_val + b) + c * (x_val + d)

            prompt = f'Løs likningen $$ {a}({_x_shift(b)}) + {c}({_x_shift(d)}) = {e} $$'

            xs = sp.Symbol('x')
            lhs_exp = sp.latex(sp.expand(a * (xs + b) + c * (xs + d)))
            coeff = a + c
            rhs_collected = coeff * x_val  # e - a*b - c*d

            steps = [
                f'Utvid parentesene: ${lhs_exp} = {e}$.',
                f'Samle $x$-ledd: ${coeff}x = {rhs_collected}$.',
                f'Del på ${coeff}$: $x = {x_val}$.',
            ]
            return ProblemData(
                generator_key=self.metadata().key,
                part='del1',
                prompt=prompt,
                answer_type='number',
                correct_answer=x_val,
                solution_short=f'$x = {x_val}$',
                solution_steps=steps,
                metadata={'tema': 'likninger', 'difficulty': 3, 'latex': True, 'subtype': subtype},
                assets=[],
                seed=seed or rng.randint(1, 10**9),
            )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
