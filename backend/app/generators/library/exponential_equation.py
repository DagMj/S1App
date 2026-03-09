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


def _signed_term(coeff: int, var_latex: str) -> str:
    """Format ' + c·var' or ' - c·var' or '' for coeff==0 (var_latex='' → plain number)."""
    if coeff == 0:
        return ''
    abs_c = abs(coeff)
    sign = '+' if coeff > 0 else '-'
    if not var_latex:
        return f' {sign} {abs_c}'
    if abs_c == 1:
        return f' {sign} {var_latex}'
    return f' {sign} {abs_c} \\cdot {var_latex}'


class ExponentialEquationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='exponential_equation',
            name='Eksponentiallikninger',
            description='Eksponentiallikninger inkl. andregradslikninger i forkledning.',
            tema='Eksponentialfunksjoner',
            part='del2',
            answer_type='number',
            difficulty=3,
            default_weight=1.0,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choice(['same_base', 'base_rewrite', 'quadratic_disguise'])

        if subtype == 'same_base':
            base = rng.choice([2, 3, 5])
            shift = rng.choice([-3, -2, -1, 0, 1, 2, 3])
            x = rng.choice([1, 2, 3, 4, 5, 6])
            exponent = x - shift
            rhs = base**exponent
            shifted_x = format_x_shift_latex(shift)
            prompt = f'Løs likningen $$ {base}^{{{shifted_x}}} = {rhs} $$'
            steps = [
                f'Skriv {rhs} som ${base}^{{{exponent}}}$.',
                f'Sett eksponentene like: ${shifted_x} = {exponent}$.',
                f'Løs for $x$: $x = {x}$.',
            ]
            answer_type = 'number'
            correct_answer = x

        elif subtype == 'base_rewrite':
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
                f'Skriv venstresiden med samme grunntall: ${left_base} = {base}^{{{k}}}$.',
                f'Da får vi: ${k}({p_latex}) = {right_exponent}$.',
                f'Løs for $x$: $x = {x}$.',
            ]
            answer_type = 'number'
            correct_answer = x

        else:  # quadratic_disguise
            variant = rng.choice(['exp_2', 'exp_3', 'exp_10', 'exp_e', 'log_lg'])

            if variant in ('exp_2', 'exp_3', 'exp_10'):
                base_map = {'exp_2': 2, 'exp_3': 3, 'exp_10': 10}
                base = base_map[variant]
                exp_choices = {2: [1, 2, 3], 3: [1, 2], 10: [1, 2]}
                x1 = rng.choice(exp_choices[base])
                u1 = base ** x1
                k = rng.choice([1, 2, 3, 4])
                while k == u1:  # avoid B=0 (trivial, no linear term)
                    k = rng.choice([1, 2, 3, 4])
                B = k - u1   # coefficient of base^x (negative if k < u1)
                C = -k * u1  # constant term (always negative)
                b_str = str(base)
                b_x = f'{b_str}^x'
                eq = f'{b_str}^{{2x}}{_signed_term(B, b_x)}{_signed_term(C, "")} = 0'
                u_eq = f'u^2{_signed_term(B, "u")}{_signed_term(C, "")} = 0'
                correct_answer = x1
                answer_type = 'number'
                x_step = f'${b_x} = {u1} = {b_str}^{{{x1}}}$, så $x = {x1}$.'
                steps = [
                    f'La $u = {b_x}$. Da er ${b_str}^{{2x}} = u^2$.',
                    f'Likningen blir $${u_eq}$$',
                    f'Faktoriser: $(u - {u1})(u + {k}) = 0$ → $u = {u1}$ eller $u = -{k}$.',
                    f'$u = -{k}$ er ugyldig siden ${b_x} > 0$ alltid.',
                    x_step,
                ]

            elif variant == 'exp_e':
                # e^(2x) + (k-1)·e^x - k = 0, roots u=1 (x=0) and u=-k (invalid)
                k = rng.choice([2, 3, 4, 5])
                B = k - 1
                C = -k
                eq = f'e^{{2x}}{_signed_term(B, "e^x")}{_signed_term(C, "")} = 0'
                u_eq = f'u^2{_signed_term(B, "u")}{_signed_term(C, "")} = 0'
                correct_answer = 0
                answer_type = 'number'
                steps = [
                    r'La $u = e^x$. Da er $e^{2x} = u^2$.',
                    f'Likningen blir $${u_eq}$$',
                    f'Faktoriser: $(u - 1)(u + {k}) = 0$ → $u = 1$ eller $u = -{k}$.',
                    f'$u = -{k}$ er ugyldig siden $e^x > 0$ alltid.',
                    r'$e^x = 1 = e^0$, så $x = 0$.',
                ]

            else:  # log_lg
                # (lg x)^2 + B·lg(x) + C = 0, roots u1, u2 ∈ {0,1,2}
                pair = rng.choice([(0, 1), (0, 2), (1, 2)])
                u1, u2 = pair
                B = -(u1 + u2)
                C = u1 * u2
                x1, x2 = 10**u1, 10**u2
                lg_var = r'\lg(x)'
                eq = f'(\\lg x)^2{_signed_term(B, lg_var)}{_signed_term(C, "")} = 0'
                u_eq = f'u^2{_signed_term(B, "u")}{_signed_term(C, "")} = 0'
                correct_answer = sorted([x1, x2])
                answer_type = 'solution_set'
                x1_expr = f'$x = 10^{{{u1}}} = {x1}$' if u1 > 0 else f'$x = 10^0 = 1$'
                x2_expr = f'$x = 10^{{{u2}}} = {x2}$'
                steps = [
                    r'La $u = \lg(x)$.',
                    f'Likningen blir $${u_eq}$$',
                    f'Røtter: $u = {u1}$ og $u = {u2}$.',
                    f'{x1_expr} og {x2_expr}.',
                ]

            if variant == 'log_lg':
                prompt = (
                    f'Løs likningen $$ {eq} $$\n'
                    r'Tips: la $u = \lg(x)$ og løs andregradslikningen for $u$.'
                )
            elif variant == 'exp_e':
                prompt = (
                    f'Løs likningen $$ {eq} $$\n'
                    r'Tips: la $u = e^x$ og løs andregradslikningen for $u$.'
                )
            else:
                b_str = str(base_map[variant])
                prompt = (
                    f'Løs likningen $$ {eq} $$\n'
                    f'Tips: la $u = {b_str}^x$ og løs andregradslikningen for $u$.'
                )

            if answer_type == 'solution_set':
                solution_short = f'Løsningsmengde: {{{x1}, {x2}}}'
            else:
                solution_short = f'$x = {correct_answer}$'

            return ProblemData(
                generator_key=self.metadata().key,
                part='del2',
                prompt=prompt,
                answer_type=answer_type,
                correct_answer=correct_answer,
                solution_short=solution_short,
                solution_steps=steps,
                metadata={
                    'tema': 'eksponentiallikning',
                    'difficulty': 4,
                    'latex': True,
                    'subtype': subtype,
                    'variant': variant,
                },
                assets=[],
                seed=seed or rng.randint(1, 10**9),
            )

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type=answer_type,
            correct_answer=correct_answer,
            solution_short=f'$x = {correct_answer}$',
            solution_steps=steps,
            metadata={'tema': 'eksponentiallikning', 'difficulty': 3, 'latex': True, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
