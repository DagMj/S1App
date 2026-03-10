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


def _cases3(eq1: str, eq2: str, eq3: str) -> str:
    return f'$$\\begin{{cases}} {eq1} \\\\ {eq2} \\\\ {eq3} \\end{{cases}}$$'


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
            name='Likningssystemer',
            description=(
                'Lineære og ikke-lineære likningssystemer med to eller tre ukjente. '
                'Subtyper: innsetting, addisjon, tekstoppgave, sum/produkt, '
                'andregradssystem, kvadratdifferanse, tre ukjente.'
            ),
            tema='Likninger',
            part='del1',
            answer_type='number',
            difficulty=3,
            default_weight=1.0,
        )

    # ── Linear 2×2 ────────────────────────────────────────────────────────────

    def _gen_substitution(self, rng: random.Random, seed) -> ProblemData:
        """Eq1 is already solved for y: y = ax + b. Eq2 is cx + dy = e."""
        x_val = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        y_val = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])

        a = rng.choice([1, 2, 3])
        b = y_val - a * x_val
        c = rng.choice([2, 3, 4])
        d = rng.choice([1, 2, 3])
        e = c * x_val + d * y_val

        b_str = (f' + {b}' if b > 0 else (f' - {abs(b)}' if b < 0 else ''))
        eq1_display = f'y = x{b_str}' if a == 1 else f'y = {a}x{b_str}'
        eq2_display = _eq(c, d, e)

        prompt = (
            'Løs likningssystemet\n'
            + _cases(eq1_display, eq2_display)
            + '\nOppgi verdien av $x$.'
        )

        coeff_x = c + d * a
        rhs = e - d * b

        sub_expr = (
            f'{c}x + ({a}x{b_str})' if d == 1
            else f'{c}x + {d}({a}x{b_str})'
        )

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
            metadata={'tema': 'likninger', 'difficulty': 3, 'latex': True, 'subtype': 'substitution'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def _gen_elimination(self, rng: random.Random, seed) -> ProblemData:
        """Multiply one equation to eliminate a variable, then back-substitute."""
        x_val = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        y_val = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])

        a1 = rng.choice([1, 2, 3])
        b1 = rng.choice([1, 2, 3])
        eliminate = rng.choice(['x', 'y'])
        k = rng.choice([2, 3])

        if eliminate == 'x':
            a2 = k * a1
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

        if eliminate == 'x':
            elim_coeff = k * b1 - b2
            elim_rhs = k * c1 - c2
            solved_val, solved_var = y_val, 'y'
            inter = c1 - b1 * solved_val
            if a1 == 1:
                back_expr = f'x = {c1} - {b1} \\cdot {solved_val} = {x_val}'
            else:
                back_expr = (
                    f'{a1}x = {c1} - {b1} \\cdot {solved_val} = {inter}'
                    f' \\Rightarrow x = {x_val}'
                )
        else:
            elim_coeff = k * a1 - a2
            elim_rhs = k * c1 - c2
            solved_val, solved_var = x_val, 'x'
            inter = c1 - a1 * solved_val
            if b1 == 1:
                back_expr = f'y = {c1} - {a1} \\cdot {solved_val} = {y_val}'
            else:
                back_expr = (
                    f'{b1}y = {c1} - {a1} \\cdot {solved_val} = {inter}'
                    f' \\Rightarrow y = {y_val}'
                )

        steps = [
            f'Multipliser likning 1 med ${k}$: ${_eq(k * a1, k * b1, k * c1)}$.',
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
            metadata={'tema': 'likninger', 'difficulty': 3, 'latex': True, 'subtype': 'elimination'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def _gen_word_problem(self, rng: random.Random, seed) -> ProblemData:
        """Real-world context: two items, two purchase totals → find unit price."""
        scenario = rng.choice(_SCENARIOS)
        x_val = rng.choice([5, 10, 15, 20, 25, 30])
        y_val = rng.choice([5, 10, 15, 20, 25, 30])

        for _ in range(30):
            q1a = rng.choice([2, 3, 4])
            q1b = rng.choice([1, 2, 3])
            q2a = rng.choice([1, 2, 3])
            q2b = rng.choice([3, 4, 5])
            if q1a * q2b != q2a * q1b:
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
        mult1, mult2 = q2a, q1a
        elim_b = mult1 * q1b - mult2 * q2b
        elim_rhs = mult1 * T1 - mult2 * T2
        back_rhs = T1 - q1b * y_val

        steps = [
            f'Sett opp systemet: $\\begin{{cases}} {eq1_display} \\\\ {eq2_display} \\end{{cases}}$',
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
            solution_short=(
                f'${scenario["item_a"]}$: ${x_val}$ kr, '
                f'${scenario["item_b"]}$: ${y_val}$ kr.'
            ),
            solution_steps=steps,
            metadata={
                'tema': 'likninger', 'difficulty': 3, 'latex': True,
                'subtype': 'word_problem', 'scenario': scenario['item_a'],
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    # ── Non-linear 2×2 ────────────────────────────────────────────────────────

    def _gen_sum_product(self, rng: random.Random, seed) -> ProblemData:
        """x + y = s, xy = p  →  quadratic t² - st + p = 0."""
        r1 = rng.choice([2, 3, 4, 5, 6, 7])
        r2 = rng.choice([1, 2, 3, 4, 5, 6])
        while r2 == r1:
            r2 = rng.choice([1, 2, 3, 4, 5, 6])
        lo, hi = min(r1, r2), max(r1, r2)
        s, p = lo + hi, lo * hi

        # Vary the framing
        frame = rng.choice(['tall', 'sidelengder', 'alder'])
        if frame == 'tall':
            prompt = (
                f'To positive tall har sum ${s}$ og produkt ${p}$.\n'
                'Finn de to tallene og oppgi dem som en løsningsmengde.'
            )
        elif frame == 'sidelengder':
            prompt = (
                f'Et rektangel har omkretstillegg $\\frac{{O}}{{2}} = {s}$ '
                f'og areal $A = {p}$.\n'
                'Finn sidelengdene og oppgi dem som en løsningsmengde.'
            )
        else:  # alder
            prompt = (
                f'To søskens alder summeres til ${s}$ og produktet av aldrene er ${p}$.\n'
                'Finn aldrene og oppgi dem som en løsningsmengde.'
            )

        steps = [
            f'La $x$ og $y$ være de to tallene: $x + y = {s}$, $xy = {p}$.',
            f'Fra $x + y = {s}$: $y = {s} - x$.',
            f'Sett inn: $x({s} - x) = {p} \\Rightarrow x^2 - {s}x + {p} = 0$.',
            f'Faktoriser: $(x - {lo})(x - {hi}) = 0$.',
            f'Svar: $\\{{{lo}, {hi}\\}}$.',
        ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='solution_set',
            correct_answer=[lo, hi],
            solution_short=f'$\\{{{lo}, {hi}\\}}$',
            solution_steps=steps,
            metadata={'tema': 'likninger', 'difficulty': 3, 'latex': True, 'subtype': 'sum_product'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def _gen_quadratic_linear(self, rng: random.Random, seed) -> ProblemData:
        """y = x²  and  x + y = n(n+1)  →  two integer x-solutions: n and -(n+1)."""
        n = rng.choice([1, 2, 3, 4])
        k = n * (n + 1)          # sum on RHS
        x1, x2 = n, -(n + 1)    # x-solutions
        y1, y2 = n**2, (n + 1)**2

        prompt = (
            'Løs likningssystemet\n'
            + _cases(f'y = x^2', f'x + y = {k}')
            + '\nOppgi løsningsmengden for $x$.'
        )

        steps = [
            f'Sett inn $y = x^2$ i likning 2: $x + x^2 = {k}$.',
            f'Skriv om: $x^2 + x - {k} = 0$.',
            f'Faktoriser: $(x - {x1})(x + {n + 1}) = 0$.',
            f'$x = {x1}$: $y = {x1}^2 = {y1}$.',
            f'$x = {x2}$: $y = ({x2})^2 = {y2}$.',
            f'Svar: $x \\in \\{{{x2}, {x1}\\}}$ med løsningspar '
            f'$({x1}, {y1})$ og $({x2}, {y2})$.',
        ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='solution_set',
            correct_answer=sorted([x1, x2]),
            solution_short=f'$x \\in \\{{{x2}, {x1}\\}}$',
            solution_steps=steps,
            metadata={'tema': 'likninger', 'difficulty': 4, 'latex': True, 'subtype': 'quadratic_linear'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def _gen_difference_squares(self, rng: random.Random, seed) -> ProblemData:
        """x + y = a,  x² − y² = c  →  factor as (x+y)(x−y) = c  →  linear system."""
        r1 = rng.choice([3, 4, 5, 6, 7])        # larger value (= x)
        r2 = rng.choice(list(range(1, r1)))      # smaller value (= y)
        a = r1 + r2                              # sum
        d = r1 - r2                              # difference
        c = a * d                                # = r1² - r2²

        prompt = (
            'Løs likningssystemet\n'
            + _cases(f'x + y = {a}', f'x^2 - y^2 = {c}')
            + '\nLa $x > y > 0$. Oppgi verdien av $x$.'
        )

        steps = [
            f'Faktoriser: $x^2 - y^2 = (x + y)(x - y) = {a}(x - y) = {c}$.',
            f'Dermed: $x - y = \\dfrac{{{c}}}{{{a}}} = {d}$.',
            f'Vi har nå: $x + y = {a}$ og $x - y = {d}$.',
            f'Legg sammen: $2x = {a + d} \\Rightarrow x = {r1}$.',
            f'Trekk fra: $2y = {a - d} \\Rightarrow y = {r2}$.',
            f'Svar: $x = {r1}$, $y = {r2}$.',
        ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=r1,
            solution_short=f'$x = {r1}$, $y = {r2}$',
            solution_steps=steps,
            metadata={'tema': 'likninger', 'difficulty': 3, 'latex': True, 'subtype': 'difference_squares'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    # ── Linear 3×3 ────────────────────────────────────────────────────────────

    def _gen_three_vars(self, rng: random.Random, seed) -> ProblemData:
        """x+y=a, y+z=b, x+z=c  →  add all, divide by 2, subtract each eq."""
        x_val = rng.choice([1, 2, 3, 4, 5])
        y_val = rng.choice([1, 2, 3, 4, 5])
        z_val = rng.choice([1, 2, 3, 4, 5])

        a = x_val + y_val
        b = y_val + z_val
        c = x_val + z_val
        S = a + b + c            # = 2(x + y + z), always even

        prompt = (
            'Løs likningssystemet\n'
            + _cases3(f'x + y = {a}', f'y + z = {b}', f'x + z = {c}')
            + '\nOppgi verdien av $x + y + z$.'
        )

        steps = [
            f'Legg sammen alle tre likningene: $2(x + y + z) = {a} + {b} + {c} = {S}$.',
            f'$x + y + z = {S // 2}$.',
            f'Trekk likning 2 ($y + z = {b}$) fra summen: $x = {S // 2} - {b} = {x_val}$.',
            f'Trekk likning 3 ($x + z = {c}$) fra summen: $y = {S // 2} - {c} = {y_val}$.',
            f'Trekk likning 1 ($x + y = {a}$) fra summen: $z = {S // 2} - {a} = {z_val}$.',
            f'Svar: $x = {x_val}$, $y = {y_val}$, $z = {z_val}$.',
        ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=S // 2,
            solution_short=(
                f'$x + y + z = {S // 2}$ '
                f'($x = {x_val}$, $y = {y_val}$, $z = {z_val}$)'
            ),
            solution_steps=steps,
            metadata={'tema': 'likninger', 'difficulty': 3, 'latex': True, 'subtype': 'three_vars_pairwise'},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    # ── Public interface ──────────────────────────────────────────────────────

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choices(
            [
                'substitution',
                'elimination',
                'word_problem',
                'sum_product',
                'quadratic_linear',
                'difference_squares',
                'three_vars_pairwise',
            ],
            weights=[20, 20, 15, 15, 12, 10, 8],
        )[0]

        gen = {
            'substitution': self._gen_substitution,
            'elimination': self._gen_elimination,
            'word_problem': self._gen_word_problem,
            'sum_product': self._gen_sum_product,
            'quadratic_linear': self._gen_quadratic_linear,
            'difference_squares': self._gen_difference_squares,
            'three_vars_pairwise': self._gen_three_vars,
        }[subtype]
        return gen(rng, seed)

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
