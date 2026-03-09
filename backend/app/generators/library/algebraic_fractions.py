from __future__ import annotations

import random
from math import gcd
from typing import Optional

import sympy as sp

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(abs(a), abs(b)) if a and b else max(abs(a), abs(b))


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

    # ── LaTeX / SymPy helpers ─────────────────────────────────────────────────

    @staticmethod
    def _fmt_shift(v: int) -> str:
        """x+v as a string without outer parens, e.g. x+3 or x-2."""
        if v > 0:
            return f'x+{v}'
        if v == 0:
            return 'x'
        return f'x-{abs(v)}'

    @staticmethod
    def _latex_num(a: int, b: Optional[int] = None) -> str:
        """
        Numerator LaTeX.
        b=None → constant integer a
        b=int  → linear ax+b (a≥1)
        """
        if b is None:
            return str(a)
        coeff = '' if a == 1 else str(a)
        if b == 0:
            return f'{coeff}x'
        if b > 0:
            return f'{coeff}x+{b}'
        return f'{coeff}x-{abs(b)}'

    @staticmethod
    def _negate_num_str(num_str: str, is_const: bool) -> str:
        """Return LaTeX for the negation of a numerator string."""
        if is_const:
            return f'-{num_str}'
        return f'-({num_str})'

    @staticmethod
    def _sympy_num(a: int, b: Optional[int], x: sp.Symbol) -> sp.Expr:
        return sp.Integer(a) if b is None else a * x + b

    @staticmethod
    def _latex_simple_denom(k: int, v: int) -> str:
        """Format denominator: k(x+v), e.g. 2(x+3) or (x-1)."""
        inner = AlgebraicFractionsGenerator._fmt_shift(v)
        return f'({inner})' if k == 1 else f'{k}({inner})'

    @staticmethod
    def _latex_product_denom(p: int, q: int, expand: bool = False) -> str:
        """(x+p)(x+q), optionally written as expanded polynomial."""
        if expand:
            s, prod = p + q, p * q
            res = 'x^2'
            if s == 1:
                res += '+x'
            elif s == -1:
                res += '-x'
            elif s > 1:
                res += f'+{s}x'
            elif s < -1:
                res += f'{s}x'
            if prod > 0:
                res += f'+{prod}'
            elif prod < 0:
                res += str(prod)
            return res
        fp = AlgebraicFractionsGenerator._fmt_shift(p)
        fq = AlgebraicFractionsGenerator._fmt_shift(q)
        return f'({fp})({fq})'

    @staticmethod
    def _latex_ans(expr: sp.Expr) -> str:
        """Wrap a SymPy expression in display-math LaTeX delimiters."""
        return f'$${sp.latex(expr)}$$'

    # ── Numerator picker ──────────────────────────────────────────────────────

    def _pick_numerator(
        self, rng: random.Random, allow_linear: bool = True
    ) -> tuple[int, Optional[int]]:
        """
        Returns (a, b).
        b=None → constant a
        b=int  → linear ax+b
        """
        if allow_linear and rng.random() < 0.45:
            a = rng.choice([1, 2])
            b = rng.choice([-3, -2, -1, 1, 2, 3])
            return a, b
        return rng.choice([1, 2, 3, 4, 5]), None

    def _pick_shifts(self, rng: random.Random) -> tuple[int, int]:
        pool = [-4, -3, -2, -1, 1, 2, 3, 4]
        p = rng.choice(pool)
        q = rng.choice([v for v in pool if v != p])
        return p, q

    # ── Top-level generate ────────────────────────────────────────────────────

    @staticmethod
    def _is_clean(expr: sp.Expr, x: sp.Symbol) -> bool:
        """Return True if the simplified result has numerator degree ≤ 1."""
        try:
            num, _ = sp.fraction(expr)
            deg = sp.Poly(sp.expand(num), x).degree()
            return deg <= 1  # type: ignore[operator]
        except Exception:
            return True

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        x = sp.Symbol('x')
        # Weight three_frac 3:1 — richer and more representative of exam problems
        subtype = rng.choices(['two_frac', 'three_frac'], weights=[1, 3])[0]
        gen = self._gen_two_frac if subtype == 'two_frac' else self._gen_three_frac
        # Retry until the simplified answer is clean (deg-1 numerator)
        last: ProblemData | None = None
        for _ in range(20):
            attempt_rng = random.Random(rng.randint(1, 10**9))
            result = gen(attempt_rng, x, seed)
            last = result
            if self._is_clean(sp.sympify(result.correct_answer), x):
                return result
        return last  # type: ignore[return-value]

    # ── two_frac: a/(d1) OP b/(d2) ───────────────────────────────────────────

    def _gen_two_frac(self, rng: random.Random, x: sp.Symbol, seed) -> ProblemData:
        p, q = self._pick_shifts(rng)

        # Optional extra integer factor outside one denominator (prob 30%)
        k1, k2 = 1, 1
        if rng.random() < 0.40:
            if rng.random() < 0.5:
                k1 = rng.choice([2, 3])
            else:
                k2 = rng.choice([2, 3])

        # Numerators — at most one linear to keep things readable
        na, nb = self._pick_numerator(rng)
        ca, cb = self._pick_numerator(rng, allow_linear=(nb is None))

        op = rng.choice(['+', '-'])
        sign = 1 if op == '+' else -1

        # SymPy
        num1 = self._sympy_num(na, nb, x)
        num2 = self._sympy_num(ca, cb, x)
        expr = num1 / (k1 * (x + p)) + sign * num2 / (k2 * (x + q))
        simplified = sp.together(sp.simplify(expr))

        # LaTeX prompt — randomly swap display order for + (can't swap - without sign change)
        lat_d1 = self._latex_simple_denom(k1, p)
        lat_d2 = self._latex_simple_denom(k2, q)
        num1_str = self._latex_num(na, nb)
        num2_str = self._latex_num(ca, cb)
        f1 = f'\\frac{{{num1_str}}}{{{lat_d1}}}'
        f2 = f'\\frac{{{num2_str}}}{{{lat_d2}}}'

        if op == '+' and rng.random() < 0.5:
            display = f'{f2}+{f1}'
        else:
            display = f'{f1}{op}{f2}'

        prompt = f'Regn ut og forkort uttrykket\n$${display}$$'

        # LCD description
        k_lcm = _lcm(k1, k2)
        fp, fq = self._fmt_shift(p), self._fmt_shift(q)
        lcd = f'$({fp})({fq})$' if k_lcm == 1 else f'${k_lcm}({fp})({fq})$'

        # Intermediate step: combined fraction before final simplification
        combined_frac = sp.together(expr)
        numer_combined, denom_combined = sp.fraction(combined_frac)
        numer_exp_lat = sp.latex(sp.expand(numer_combined))
        denom_lat = sp.latex(sp.factor(denom_combined))
        intermediate_step = (
            f'Felles nevner gir: $\\dfrac{{{numer_exp_lat}}}{{{denom_lat}}}$'
        )

        ans_lat = self._latex_ans(simplified)
        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=sp.sstr(simplified),
            solution_short=ans_lat,
            solution_steps=[
                f'Fellesnevner er {lcd}.',
                intermediate_step,
                f'Forkortet svar: {ans_lat}',
            ],
            metadata={'tema': 'algebra', 'difficulty': 3, 'latex': True, 'subtype': 'two_frac'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    # ── three_frac: a/(d1) OP b/(d2) OP c/((x+p)(x+q)) ──────────────────────

    def _gen_three_frac(self, rng: random.Random, x: sp.Symbol, seed) -> ProblemData:
        p, q = self._pick_shifts(rng)

        # Optional extra factor on one simple denominator (prob 30%)
        k1, k2 = 1, 1
        if rng.random() < 0.40:
            if rng.random() < 0.5:
                k1 = rng.choice([2, 3])
            else:
                k2 = rng.choice([2, 3])

        # Numerators
        na, nb = self._pick_numerator(rng)
        ca, cb = self._pick_numerator(rng, allow_linear=(nb is None))
        c = rng.choice([1, 2, 3, 4, 5, 6])

        # Sometimes write the product denominator as an expanded polynomial
        expand_quad = rng.random() < 0.45

        op1 = rng.choice(['+', '-'])
        op2 = rng.choice(['+', '-'])
        s1 = 1 if op1 == '+' else -1
        s2 = 1 if op2 == '+' else -1

        # SymPy
        num_a = self._sympy_num(na, nb, x)
        num_b = self._sympy_num(ca, cb, x)
        expr = (
            num_a / (k1 * (x + p))
            + s1 * num_b / (k2 * (x + q))
            + s2 * sp.Integer(c) / ((x + p) * (x + q))
        )
        simplified = sp.together(sp.simplify(expr))

        # Build the three fraction LaTeX strings with their sign flags
        lat_d1 = self._latex_simple_denom(k1, p)
        lat_d2 = self._latex_simple_denom(k2, q)
        lat_dprod = self._latex_product_denom(p, q, expand=expand_quad)

        num1_str = self._latex_num(na, nb)
        num2_str = self._latex_num(ca, cb)

        fracs = [
            {
                'num': num1_str,
                'denom': lat_d1,
                'lat': f'\\frac{{{num1_str}}}{{{lat_d1}}}',
                'neg': False,
                'is_const': (nb is None),
            },
            {
                'num': num2_str,
                'denom': lat_d2,
                'lat': f'\\frac{{{num2_str}}}{{{lat_d2}}}',
                'neg': (op1 == '-'),
                'is_const': (cb is None),
            },
            {
                'num': str(c),
                'denom': lat_dprod,
                'lat': f'\\frac{{{c}}}{{{lat_dprod}}}',
                'neg': (op2 == '-'),
                'is_const': True,
            },
        ]

        # Shuffle position of all three fractions randomly
        rng.shuffle(fracs)

        # For the first fraction: if negative, randomly put minus in numerator
        if fracs[0]['neg'] and rng.random() < 0.5:
            neg_num = self._negate_num_str(fracs[0]['num'], fracs[0]['is_const'])
            fracs[0] = {
                **fracs[0],
                'lat': f'\\frac{{{neg_num}}}{{{fracs[0]["denom"]}}}',
                'neg': False,
            }

        # Build the display expression
        parts: list[str] = []
        for i, f in enumerate(fracs):
            if i == 0:
                parts.append(f'-{f["lat"]}' if f['neg'] else f['lat'])
            else:
                parts.append(f'-{f["lat"]}' if f['neg'] else f'+{f["lat"]}')

        prompt = f'Regn ut og forkort uttrykket\n$${"".join(parts)}$$'

        # Solution steps
        k_lcm = _lcm(k1, k2)
        fp, fq = self._fmt_shift(p), self._fmt_shift(q)
        lcd = f'$({fp})({fq})$' if k_lcm == 1 else f'${k_lcm}({fp})({fq})$'

        steps = [f'Fellesnevner er {lcd}.']
        if expand_quad:
            expanded_str = self._latex_product_denom(p, q, expand=True)
            factored_str = self._latex_product_denom(p, q, expand=False)
            steps.append(
                f'Nevneren ${expanded_str}$ faktoriserer til ${factored_str}$.'
            )

        # Intermediate step: combined fraction before final simplification
        combined_frac = sp.together(expr)
        numer_combined, denom_combined = sp.fraction(combined_frac)
        numer_exp_lat = sp.latex(sp.expand(numer_combined))
        denom_lat = sp.latex(sp.factor(denom_combined))
        steps.append(
            f'Felles nevner gir: $\\dfrac{{{numer_exp_lat}}}{{{denom_lat}}}$'
        )

        ans_lat = self._latex_ans(simplified)
        steps.append(f'Forkortet svar: {ans_lat}')

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='expression',
            correct_answer=sp.sstr(simplified),
            solution_short=ans_lat,
            solution_steps=steps,
            metadata={'tema': 'algebra', 'difficulty': 3, 'latex': True, 'subtype': 'three_frac'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
