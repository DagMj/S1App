from __future__ import annotations

import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


# ── LaTeX helpers ─────────────────────────────────────────────────────────────

def _lead(a: int, var: str) -> str:
    """Leading term: 2x, -x, x, -3y …"""
    if a == 1:
        return var
    if a == -1:
        return f'-{var}'
    return f'{a}{var}'


def _follow(a: int, var: str) -> str:
    """Subsequent term with explicit sign: +2x, -3y, +y, -x …"""
    if a == 1:
        return f' + {var}'
    if a == -1:
        return f' - {var}'
    if a > 0:
        return f' + {a}{var}'
    return f' - {abs(a)}{var}'


def _eq(a: int, b: int, c: int) -> str:
    """Format ax + by = c."""
    return f'{_lead(a, "x")}{_follow(b, "y")} = {c}'


def _cases(eq1: str, eq2: str) -> str:
    return f'$$\\begin{{cases}} {eq1} \\\\ {eq2} \\end{{cases}}$$'


def _signed(n: int) -> str:
    """Format integer with explicit sign for display in steps: -3, +5 …"""
    return str(n) if n < 0 else f'+{n}'


# ── Scenario pool for word problems ──────────────────────────────────────────

_SCENARIOS = [
    {
        'item_a': 'epler',
        'item_b': 'bananer',
        'unit': 'kr per kg',
        'q_unit': 'kg',
        'template': (
            '{q1a} kg {item_a} og {q1b} kg {item_b} koster til sammen {T1} kr.\n'
            '{q2a} kg {item_a} og {q2b} kg {item_b} koster til sammen {T2} kr.\n'
            'Hva koster {item_a} per kg?'
        ),
    },
    {
        'item_a': 'voksenbilletter',
        'item_b': 'barnebilletter',
        'unit': 'kr per billett',
        'q_unit': 'billetter',
        'template': (
            '{q1a} {item_a} og {q1b} {item_b} kostet til sammen {T1} kr.\n'
            '{q2a} {item_a} og {q2b} {item_b} kostet til sammen {T2} kr.\n'
            'Hva koster en voksenbillett?'
        ),
    },
    {
        'item_a': 'kaffe',
        'item_b': 'te',
        'unit': 'kr per kopp',
        'q_unit': 'kopper',
        'template': (
            '{q1a} kopper {item_a} og {q1b} kopper {item_b} koster til sammen {T1} kr.\n'
            '{q2a} kopper {item_a} og {q2b} kopper {item_b} koster til sammen {T2} kr.\n'
            'Hva koster én kopp {item_a}?'
        ),
    },
    {
        'item_a': 'bøker',
        'item_b': 'hefter',
        'unit': 'kr per stk',
        'q_unit': 'stk',
        'template': (
            '{q1a} {item_a} og {q1b} {item_b} koster til sammen {T1} kr.\n'
            '{q2a} {item_a} og {q2b} {item_b} koster til sammen {T2} kr.\n'
            'Hva koster én bok?'
        ),
    },
]


class LinearSystemGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='linear_system',
            name='Lineære likningssystemer',
            description='Løs et system av to lineære likninger med to ukjente.',
            tema='Likninger',
            part='del1',
            answer_type='number',
            difficulty=3,
            default_weight=1.0,
        )

    # ── Subtype generators ────────────────────────────────────────────────────

    def _gen_substitution(self, rng: random.Random, seed) -> ProblemData:
        """Eq1 is already solved for y: y = ax + b. Eq2 is cx + dy = e."""
        x_val = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        y_val = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])

        a = rng.choice([1, 2, 3])
        b = y_val - a * x_val          # y = ax + b
        c = rng.choice([2, 3, 4])
        d = rng.choice([1, 2, 3])
        e = c * x_val + d * y_val

        # Format eq1 as "y = ax + b"
        b_str = (f' + {b}' if b > 0 else (f' - {abs(b)}' if b < 0 else ''))
        if a == 1:
            eq1_display = f'y = x{b_str}'
        else:
            eq1_display = f'y = {a}x{b_str}'
        eq2_display = _eq(c, d, e)

        prompt = (
            'Løs likningssystemet\n'
            + _cases(eq1_display, eq2_display)
            + '\nOppgi verdien av $x$.'
        )

        # Substitution: cx + d(ax+b) = e → (c + da)x = e - db
        coeff_x = c + d * a
        rhs = e - d * b          # = coeff_x * x_val

        # Build step showing the substituted expression
        if d == 1:
            sub_expr = f'{c}x + ({a}x{b_str})'
        else:
            sub_expr = f'{c}x + {d}({a}x{b_str})'

        steps = [
            f'Sett inn $y = {a}x{b_str}$ i likning 2: ${sub_expr} = {e}$.',
            f'Utvid og samle $x$-ledd: ${coeff_x}x = {rhs}$.',
            f'$x = \\dfrac{{{rhs}}}{{{coeff_x}}} = {x_val}$.',
            f'Sett inn $x = {x_val}$ i likning 1: $y = {a} \\cdot {x_val}{b_str} = {y_val}$.',
            f'Svar: $x = {x_val}$, $y = {y_val}$.',
        ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=x_val,
            solution_short=f'$x = {x_val}$, $y = {y_val}$',
            solution_steps=steps,
            metadata={
                'tema': 'likninger',
                'difficulty': 3,
                'latex': True,
                'subtype': 'substitution',
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def _gen_elimination(self, rng: random.Random, seed) -> ProblemData:
        """Multiply one equation to eliminate a variable, then back-substitute."""
        x_val = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        y_val = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])

        a1 = rng.choice([1, 2, 3])
        b1 = rng.choice([1, 2, 3])

        # Choose which variable to eliminate and the multiplier
        eliminate = rng.choice(['x', 'y'])
        k = rng.choice([2, 3])

        if eliminate == 'x':
            a2 = k * a1
            # Choose b2 < k*b1 so that k*b1 - b2 > 0 (positive coefficient after elimination)
            pool = [v for v in range(1, k * b1) if v != k * b1]
            if not pool:
                pool = [v for v in [1, 2, 3, 4, 5, 6] if v != k * b1]
            b2 = rng.choice(pool)
        else:
            b2 = k * b1
            pool = [v for v in range(1, k * a1) if v != k * a1]
            if not pool:
                pool = [v for v in [1, 2, 3, 4, 5, 6] if v != k * a1]
            a2 = rng.choice(pool)

        c1 = a1 * x_val + b1 * y_val
        c2 = a2 * x_val + b2 * y_val

        eq1_display = _eq(a1, b1, c1)
        eq2_display = _eq(a2, b2, c2)

        prompt = (
            'Løs likningssystemet\n'
            + _cases(eq1_display, eq2_display)
            + '\nOppgi verdien av $x + y$.'
        )

        # Steps: multiply eq1 by k, then subtract eq2
        if eliminate == 'x':
            elim_coeff = k * b1 - b2           # > 0 by construction
            elim_rhs = k * c1 - c2             # = elim_coeff * y_val
            solved_val, solved_var = y_val, 'y'
            # Back-substitute y_val into eq1 to find x
            inter = c1 - b1 * solved_val       # = a1 * x_val
            if a1 == 1:
                back_expr = f'x = {c1} - {b1} \\cdot {solved_val} = {x_val}'
            else:
                back_expr = (
                    f'{a1}x = {c1} - {b1} \\cdot {solved_val} = {inter}'
                    f' \\Rightarrow x = {x_val}'
                )
        else:
            elim_coeff = k * a1 - a2           # > 0 by construction
            elim_rhs = k * c1 - c2             # = elim_coeff * x_val
            solved_val, solved_var = x_val, 'x'
            # Back-substitute x_val into eq1 to find y
            inter = c1 - a1 * solved_val       # = b1 * y_val
            if b1 == 1:
                back_expr = f'y = {c1} - {a1} \\cdot {solved_val} = {y_val}'
            else:
                back_expr = (
                    f'{b1}y = {c1} - {a1} \\cdot {solved_val} = {inter}'
                    f' \\Rightarrow y = {y_val}'
                )

        steps = [
            f'Multipliser likning 1 med ${k}$: '
            f'${_eq(k * a1, k * b1, k * c1)}$.',
            f'Trekk likning 2 fra: eliminerer ${eliminate}$, gir '
            f'${elim_coeff}{solved_var} = {elim_rhs}$.',
            f'${solved_var} = \\dfrac{{{elim_rhs}}}{{{elim_coeff}}} = {solved_val}$.',
            f'Sett inn ${solved_var} = {solved_val}$ i likning 1: ${back_expr}$.',
            f'Svar: $x = {x_val}$, $y = {y_val}$, og $x + y = {x_val + y_val}$.',
        ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=x_val + y_val,
            solution_short=f'$x = {x_val}$, $y = {y_val}$ (sum: ${x_val + y_val}$)',
            solution_steps=steps,
            metadata={
                'tema': 'likninger',
                'difficulty': 3,
                'latex': True,
                'subtype': 'elimination',
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def _gen_word_problem(self, rng: random.Random, seed) -> ProblemData:
        """Real-world context: two items, two purchase totals → find unit price."""
        scenario = rng.choice(_SCENARIOS)

        # Prices in multiples of 5 to keep totals clean
        x_val = rng.choice([5, 10, 15, 20, 25, 30])  # price of item_a
        y_val = rng.choice([5, 10, 15, 20, 25, 30])  # price of item_b

        # Quantities — ensure non-degenerate system (q1a/q2a ≠ q1b/q2b)
        for _ in range(30):
            q1a = rng.choice([2, 3, 4])
            q1b = rng.choice([1, 2, 3])
            q2a = rng.choice([1, 2, 3])
            q2b = rng.choice([3, 4, 5])
            if q1a * q2b != q2a * q1b:  # non-degenerate check
                break

        T1 = q1a * x_val + q1b * y_val
        T2 = q2a * x_val + q2b * y_val

        desc = scenario['template'].format(
            q1a=q1a, q1b=q1b, T1=T1,
            q2a=q2a, q2b=q2b, T2=T2,
            item_a=scenario['item_a'],
            item_b=scenario['item_b'],
        )
        prompt = (
            f'{desc}\n\n'
            f'La $x$ = pris per enhet av {scenario["item_a"]} '
            f'og $y$ = pris per enhet av {scenario["item_b"]}.'
        )

        eq1_display = _eq(q1a, q1b, T1)
        eq2_display = _eq(q2a, q2b, T2)

        # Solve by elimination: multiply eq1 by q2a, eq2 by q1a, subtract to get y
        # Then back-substitute.  (Use multiplier on the larger coeff for cleaner display.)
        mult1, mult2 = q2a, q1a
        elim_b = mult1 * q1b - mult2 * q2b
        elim_rhs = mult1 * T1 - mult2 * T2   # = elim_b * y_val

        back_rhs = T1 - q1b * y_val           # = q1a * x_val

        steps = [
            f'Sett opp systemet:\n$\\begin{{cases}} {eq1_display} \\\\ {eq2_display} \\end{{cases}}$',
            f'Multipliser likning 1 med ${mult1}$ og likning 2 med ${mult2}$, '
            f'og trekk fra hverandre for å eliminere $x$.',
            f'${elim_b}y = {elim_rhs} \\Rightarrow y = {y_val}$.',
            f'Sett inn $y = {y_val}$ i likning 1: '
            f'${q1a}x = {back_rhs} \\Rightarrow x = {x_val}$.',
            f'Svar: {scenario["item_a"]} koster ${x_val}$ kr per enhet.',
        ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=x_val,
            solution_short=f'${scenario["item_a"]}$: ${x_val}$ kr, '
                           f'${scenario["item_b"]}$: ${y_val}$ kr.',
            solution_steps=steps,
            metadata={
                'tema': 'likninger',
                'difficulty': 3,
                'latex': True,
                'subtype': 'word_problem',
                'scenario': scenario['item_a'],
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    # ── Public interface ──────────────────────────────────────────────────────

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choices(
            ['substitution', 'elimination', 'word_problem'],
            weights=[35, 35, 30],
        )[0]

        gen = {
            'substitution': self._gen_substitution,
            'elimination': self._gen_elimination,
            'word_problem': self._gen_word_problem,
        }[subtype]
        return gen(rng, seed)

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
