from __future__ import annotations

import random
from fractions import Fraction

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _frac_latex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return rf'\dfrac{{{f.numerator}}}{{{f.denominator}}}'


class ProbabilityConditionalGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='probability_conditional',
            name='Betinget sannsynlighet',
            description='Betinget sannsynlighet P(A|B) fra frekvenstabeller og kontekstoppgaver.',
            tema='Sannsynlighet',
            part='del2',
            answer_type='number',
            difficulty=3,
            default_weight=1.0,
        )

    def generate(self, seed: int) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choices(
            ['table_school', 'table_health', 'table_sports', 'formula'],
            weights=[30, 25, 25, 20],
        )[0]

        if subtype == 'table_school':
            return self._table_school(rng, seed)
        elif subtype == 'table_health':
            return self._table_health(rng, seed)
        elif subtype == 'table_sports':
            return self._table_sports(rng, seed)
        else:
            return self._formula(rng, seed)

    # ── school survey table ───────────────────────────────────────────────────

    def _table_school(self, rng: random.Random, seed: int) -> ProblemData:
        # 2×2 table: rows=Jenter/Gutter, cols=Liker mat / Liker ikke mat
        g_yes = rng.randint(8, 18)
        g_no = rng.randint(4, 12)
        b_yes = rng.randint(6, 16)
        b_no = rng.randint(5, 14)
        total = g_yes + g_no + b_yes + b_no

        question = rng.choice([
            'jente_given_likes',
            'likes_given_girl',
            'boy_given_dislikes',
            'dislikes_given_boy',
        ])

        if question == 'likes_given_girl':
            n_b = g_yes + g_no  # total jenter
            n_ab = g_yes
            prob = Fraction(n_ab, n_b)
            given_txt = 'jente'
            event_txt = 'liker matematikk'
            cond_sym = 'L \\mid J'
        elif question == 'jente_given_likes':
            n_b = g_yes + b_yes  # total som liker
            n_ab = g_yes
            prob = Fraction(n_ab, n_b)
            given_txt = 'liker matematikk'
            event_txt = 'jente'
            cond_sym = 'J \\mid L'
        elif question == 'boy_given_dislikes':
            n_b = g_no + b_no
            n_ab = b_no
            prob = Fraction(n_ab, n_b)
            given_txt = 'ikke liker matematikk'
            event_txt = 'gutt'
            cond_sym = 'G \\mid L^c'
        else:  # dislikes_given_boy
            n_b = b_yes + b_no
            n_ab = b_no
            prob = Fraction(n_ab, n_b)
            given_txt = 'gutt'
            event_txt = 'ikke liker matematikk'
            cond_sym = 'L^c \\mid G'

        prompt = (
            f'I en klasse ble det gjennomført en undersøkelse om hvem som liker matematikk.\n'
            f'Resultatene er vist i tabellen:\n\n'
            f'| | Liker mat | Liker ikke | Totalt |\n'
            f'|---|---|---|---|\n'
            f'| Jenter | {g_yes} | {g_no} | {g_yes + g_no} |\n'
            f'| Gutter | {b_yes} | {b_no} | {b_yes + b_no} |\n'
            f'| Totalt | {g_yes + b_yes} | {g_no + b_no} | {total} |\n\n'
            f'En elev velges tilfeldig.\n'
            f'Hva er sannsynligheten for at eleven {event_txt}, gitt at eleven er {given_txt}?'
        )
        steps = [
            f'Betinget sannsynlighet: $P(A \\mid B) = \\dfrac{{n(A \\cap B)}}{{n(B)}}$.',
            f'$n(B) = {n_b}$ (antall som er {given_txt}).',
            f'$n(A \\cap B) = {n_ab}$ (antall som er {event_txt} OG {given_txt}).',
            f'$P({cond_sym}) = {_frac_latex(prob)}$',
        ]
        short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_conditional',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── health study table ────────────────────────────────────────────────────

    def _table_health(self, rng: random.Random, seed: int) -> ProblemData:
        # rows=Trener/Trener ikke, cols=Forkjølet/Ikke forkjølet
        t_sick = rng.randint(5, 15)
        t_well = rng.randint(20, 40)
        n_sick = rng.randint(15, 30)
        n_well = rng.randint(10, 25)
        total = t_sick + t_well + n_sick + n_well

        question = rng.choice(['sick_given_trains', 'trains_given_sick', 'well_given_no_train'])

        if question == 'sick_given_trains':
            n_b = t_sick + t_well
            n_ab = t_sick
            prob = Fraction(n_ab, n_b)
            prompt = (
                f'En helseundersøkelse av {total} elever ga følgende resultater:\n\n'
                f'| | Forkjølet | Ikke forkjølet | Totalt |\n'
                f'|---|---|---|---|\n'
                f'| Trener regelmessig | {t_sick} | {t_well} | {t_sick+t_well} |\n'
                f'| Trener ikke | {n_sick} | {n_well} | {n_sick+n_well} |\n'
                f'| Totalt | {t_sick+n_sick} | {t_well+n_well} | {total} |\n\n'
                f'Hva er sannsynligheten for at en tilfeldig elev er forkjølet, gitt at eleven trener regelmessig?'
            )
            steps = [
                f'$P(\\text{{forkjølet}} \\mid \\text{{trener}}) = \\dfrac{{{n_ab}}}{{{n_b}}} = {_frac_latex(prob)}$',
            ]

        elif question == 'trains_given_sick':
            n_b = t_sick + n_sick
            n_ab = t_sick
            prob = Fraction(n_ab, n_b)
            prompt = (
                f'En helseundersøkelse av {total} elever ga følgende resultater:\n\n'
                f'| | Forkjølet | Ikke forkjølet | Totalt |\n'
                f'|---|---|---|---|\n'
                f'| Trener regelmessig | {t_sick} | {t_well} | {t_sick+t_well} |\n'
                f'| Trener ikke | {n_sick} | {n_well} | {n_sick+n_well} |\n'
                f'| Totalt | {t_sick+n_sick} | {t_well+n_well} | {total} |\n\n'
                f'Hva er sannsynligheten for at en tilfeldig forkjølet elev trener regelmessig?'
            )
            steps = [
                f'$P(\\text{{trener}} \\mid \\text{{forkjølet}}) = \\dfrac{{{n_ab}}}{{{n_b}}} = {_frac_latex(prob)}$',
            ]

        else:
            n_b = n_sick + n_well
            n_ab = n_well
            prob = Fraction(n_ab, n_b)
            prompt = (
                f'En helseundersøkelse av {total} elever ga følgende resultater:\n\n'
                f'| | Forkjølet | Ikke forkjølet | Totalt |\n'
                f'|---|---|---|---|\n'
                f'| Trener regelmessig | {t_sick} | {t_well} | {t_sick+t_well} |\n'
                f'| Trener ikke | {n_sick} | {n_well} | {n_sick+n_well} |\n'
                f'| Totalt | {t_sick+n_sick} | {t_well+n_well} | {total} |\n\n'
                f'Hva er sannsynligheten for at en elev ikke er forkjølet, gitt at eleven ikke trener?'
            )
            steps = [
                f'$P(\\text{{ikke forkjølet}} \\mid \\text{{trener ikke}}) = \\dfrac{{{n_ab}}}{{{n_b}}} = {_frac_latex(prob)}$',
            ]

        full_steps = [
            'Betinget sannsynlighet: $P(A \\mid B) = \\dfrac{n(A \\cap B)}{n(B)}$.',
        ] + steps
        short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_conditional',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=full_steps,
            seed=seed,
        )

    # ── sports table ──────────────────────────────────────────────────────────

    def _table_sports(self, rng: random.Random, seed: int) -> ProblemData:
        sport1, sport2 = rng.choice([
            ('fotball', 'basketball'),
            ('svømming', 'løping'),
            ('ski', 'fotball'),
        ])
        a_both = rng.randint(5, 12)
        a_only = rng.randint(8, 20)
        b_only = rng.randint(8, 20)
        neither = rng.randint(5, 15)
        total = a_both + a_only + b_only + neither

        question = rng.choice(['s1_given_s2', 's2_given_s1'])

        if question == 's1_given_s2':
            n_b = a_both + b_only
            n_ab = a_both
            prob = Fraction(n_ab, n_b)
            prompt = (
                f'{total} elever ble spurt om de spiller {sport1} og/eller {sport2}.\n'
                f'- Begge: {a_both}\n'
                f'- Kun {sport1}: {a_only}\n'
                f'- Kun {sport2}: {b_only}\n'
                f'- Ingen: {neither}\n\n'
                f'Hva er sannsynligheten for at en tilfeldig elev spiller {sport1}, '
                f'gitt at eleven spiller {sport2}?'
            )
            steps = [
                f'Elever som spiller {sport2}: {a_both} + {b_only} = {n_b}.',
                f'Av disse spiller {a_both} også {sport1}.',
                f'$P({sport1} \\mid {sport2}) = \\dfrac{{{n_ab}}}{{{n_b}}} = {_frac_latex(prob)}$',
            ]
        else:
            n_b = a_both + a_only
            n_ab = a_both
            prob = Fraction(n_ab, n_b)
            prompt = (
                f'{total} elever ble spurt om de spiller {sport1} og/eller {sport2}.\n'
                f'- Begge: {a_both}\n'
                f'- Kun {sport1}: {a_only}\n'
                f'- Kun {sport2}: {b_only}\n'
                f'- Ingen: {neither}\n\n'
                f'Hva er sannsynligheten for at en tilfeldig elev spiller {sport2}, '
                f'gitt at eleven spiller {sport1}?'
            )
            steps = [
                f'Elever som spiller {sport1}: {a_both} + {a_only} = {n_b}.',
                f'Av disse spiller {a_both} også {sport2}.',
                f'$P({sport2} \\mid {sport1}) = \\dfrac{{{n_ab}}}{{{n_b}}} = {_frac_latex(prob)}$',
            ]

        short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_conditional',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── formula-based ─────────────────────────────────────────────────────────

    def _formula(self, rng: random.Random, seed: int) -> ProblemData:
        # P(A) = a/n, P(B) = b/n, P(A∩B) = c/n  — ask P(A|B) or P(B|A)
        n = rng.choice([10, 12, 15, 20])
        # ensure c < a, b
        c = rng.randint(2, n // 3)
        a = rng.randint(c + 1, n * 2 // 3)
        b = rng.randint(c + 1, n * 2 // 3)
        # keep a + b - c <= n
        while a + b - c > n:
            a = rng.randint(c + 1, n * 2 // 3)
            b = rng.randint(c + 1, n * 2 // 3)

        pA = Fraction(a, n)
        pB = Fraction(b, n)
        pAB = Fraction(c, n)

        variant = rng.choice(['a_given_b', 'b_given_a'])
        if variant == 'a_given_b':
            prob = pAB / pB  # = c/b
            prompt = (
                f'For to hendelser A og B gjelder:\n'
                f'$P(A) = {_frac_latex(pA)}$, '
                f'$P(B) = {_frac_latex(pB)}$, '
                f'$P(A \\cap B) = {_frac_latex(pAB)}$.\n\n'
                f'Finn $P(A \\mid B)$.'
            )
            steps = [
                r'$P(A \mid B) = \dfrac{P(A \cap B)}{P(B)}$',
                f'$= \\dfrac{{{_frac_latex(pAB)}}}{{{_frac_latex(pB)}}} = {_frac_latex(prob)}$',
            ]
            short = f'$P(A \\mid B) = {_frac_latex(prob)}$'
        else:
            prob = pAB / pA  # = c/a
            prompt = (
                f'For to hendelser A og B gjelder:\n'
                f'$P(A) = {_frac_latex(pA)}$, '
                f'$P(B) = {_frac_latex(pB)}$, '
                f'$P(A \\cap B) = {_frac_latex(pAB)}$.\n\n'
                f'Finn $P(B \\mid A)$.'
            )
            steps = [
                r'$P(B \mid A) = \dfrac{P(A \cap B)}{P(A)}$',
                f'$= \\dfrac{{{_frac_latex(pAB)}}}{{{_frac_latex(pA)}}} = {_frac_latex(prob)}$',
            ]
            short = f'$P(B \\mid A) = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_conditional',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    def evaluate(self, problem: ProblemData, user_answer: str) -> EvalResult:
        return default_evaluate(problem, user_answer)

    def solution(self, problem: ProblemData) -> ProblemData:
        return default_solution(problem)
