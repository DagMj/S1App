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


class ProbabilityClassicalGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='probability_classical',
            name='Klassisk sannsynlighet',
            description='Grunnleggende sannsynlighetsoppgaver med terning, mynter og komplementregelen.',
            tema='Sannsynlighet',
            part='del1',
            answer_type='number',
            difficulty=2,
            default_weight=1.0,
        )

    def generate(self, seed: int) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choices(
            ['single_die', 'two_dice', 'coins', 'complement'],
            weights=[25, 30, 25, 20],
        )[0]

        if subtype == 'single_die':
            return self._single_die(rng, seed)
        elif subtype == 'two_dice':
            return self._two_dice(rng, seed)
        elif subtype == 'coins':
            return self._coins(rng, seed)
        else:
            return self._complement(rng, seed)

    # ── single die ────────────────────────────────────────────────────────────

    def _single_die(self, rng: random.Random, seed: int) -> ProblemData:
        die_sides = rng.choice([6, 8, 10, 12])
        variant = rng.choice(['exact', 'leq', 'geq', 'even', 'odd'])

        if variant == 'exact':
            target = rng.randint(1, die_sides)
            prob = Fraction(1, die_sides)
            prompt = (
                f'Du kaster en {die_sides}-sidet terning.\n'
                f'Hva er sannsynligheten for å få tallet {target}?'
            )
            steps = [
                f'Terningen har {die_sides} like sannsynlige utfall.',
                f'Gunstige utfall: {{{target}}} → 1 utfall.',
                f'$P = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'leq':
            k = rng.randint(2, die_sides - 1)
            prob = Fraction(k, die_sides)
            prompt = (
                f'Du kaster en {die_sides}-sidet terning.\n'
                f'Hva er sannsynligheten for å få {k} eller lavere?'
            )
            steps = [
                f'Gunstige utfall: {{1, 2, …, {k}}} → {k} utfall.',
                f'Totalt: {die_sides} utfall.',
                f'$P = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'geq':
            k = rng.randint(2, die_sides - 1)
            fav = die_sides - k + 1
            prob = Fraction(fav, die_sides)
            prompt = (
                f'Du kaster en {die_sides}-sidet terning.\n'
                f'Hva er sannsynligheten for å få {k} eller høyere?'
            )
            steps = [
                f'Gunstige utfall: {{{k}, {k+1}, …, {die_sides}}} → {fav} utfall.',
                f'Totalt: {die_sides} utfall.',
                f'$P = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'even':
            fav = die_sides // 2
            prob = Fraction(fav, die_sides)
            prompt = (
                f'Du kaster en {die_sides}-sidet terning.\n'
                f'Hva er sannsynligheten for å få et partall?'
            )
            steps = [
                f'Partall på 1–{die_sides}: {fav} utfall.',
                f'Totalt: {die_sides} utfall.',
                f'$P(\\text{{partall}}) = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        else:  # odd
            fav = (die_sides + 1) // 2
            prob = Fraction(fav, die_sides)
            prompt = (
                f'Du kaster en {die_sides}-sidet terning.\n'
                f'Hva er sannsynligheten for å få et oddetall?'
            )
            steps = [
                f'Oddetall på 1–{die_sides}: {fav} utfall.',
                f'Totalt: {die_sides} utfall.',
                f'$P(\\text{{oddetall}}) = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_classical',
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── two dice ──────────────────────────────────────────────────────────────

    def _two_dice(self, rng: random.Random, seed: int) -> ProblemData:
        variant = rng.choice(['exact_sum', 'sum_geq', 'both_same', 'at_least_one'])

        if variant == 'exact_sum':
            target = rng.randint(4, 10)
            fav = sum(
                1
                for a in range(1, 7)
                for b in range(1, 7)
                if a + b == target
            )
            prob = Fraction(fav, 36)
            prompt = (
                f'Du kaster to vanlige terninger.\n'
                f'Hva er sannsynligheten for at summen blir {target}?'
            )
            steps = [
                f'Totalt antall utfall: $6 \\times 6 = 36$.',
                f'Gunstige summer lik {target}: {fav} utfall.',
                f'$P(\\text{{sum}} = {target}) = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'sum_geq':
            k = rng.randint(9, 11)
            fav = sum(
                1
                for a in range(1, 7)
                for b in range(1, 7)
                if a + b >= k
            )
            prob = Fraction(fav, 36)
            prompt = (
                f'Du kaster to vanlige terninger.\n'
                f'Hva er sannsynligheten for at summen er minst {k}?'
            )
            steps = [
                f'Totalt: 36 utfall.',
                f'Utfall med sum ≥ {k}: {fav} stykker.',
                f'$P(\\text{{sum}} \\geq {k}) = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'both_same':
            prob = Fraction(6, 36)
            prompt = (
                'Du kaster to vanlige terninger.\n'
                'Hva er sannsynligheten for at begge terningene viser det samme tallet?'
            )
            steps = [
                'Gunstige utfall: (1,1),(2,2),(3,3),(4,4),(5,5),(6,6) → 6 utfall.',
                'Totalt: 36 utfall.',
                f'$P(\\text{{like}}) = {_frac_latex(prob)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        else:  # at_least_one
            k = rng.randint(1, 4)
            none_fav = (6 - 1) ** 2  # neither shows k: 5*5=25
            prob = Fraction(36 - none_fav, 36)
            prompt = (
                f'Du kaster to vanlige terninger.\n'
                f'Hva er sannsynligheten for at minst én av terningene viser {k}?'
            )
            steps = [
                f'Komplementet: ingen terning viser {k}.',
                f'$P(\\text{{ingen {k}}}) = {_frac_latex(Fraction(5,6))}^2 = {_frac_latex(Fraction(25,36))}$',
                f'$P(\\text{{minst én {k}}}) = 1 - {_frac_latex(Fraction(25,36))} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_classical',
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── coins ─────────────────────────────────────────────────────────────────

    def _coins(self, rng: random.Random, seed: int) -> ProblemData:
        n_coins = rng.choice([2, 3, 4])
        total = 2 ** n_coins
        variant = rng.choice(['exactly_k', 'at_least_k', 'all_heads'])

        from math import comb

        if variant == 'exactly_k':
            k = rng.randint(1, n_coins - 1)
            fav = comb(n_coins, k)
            prob = Fraction(fav, total)
            prompt = (
                f'Du kaster {n_coins} mynter.\n'
                f'Hva er sannsynligheten for å få nøyaktig {k} kron?'
            )
            steps = [
                f'Totalt: $2^{{{n_coins}}} = {total}$ utfall.',
                rf'Antall måter å velge {k} av {n_coins}: $\binom{{{n_coins}}}{{{k}}} = {fav}$.',
                f'$P = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'at_least_k':
            k = rng.randint(1, n_coins - 1)
            fav = sum(comb(n_coins, i) for i in range(k, n_coins + 1))
            prob = Fraction(fav, total)
            prompt = (
                f'Du kaster {n_coins} mynter.\n'
                f'Hva er sannsynligheten for å få minst {k} kron?'
            )
            steps = [
                f'Totalt: {total} utfall.',
                f'Gunstige (≥ {k} kron): {fav} utfall.',
                f'$P = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        else:  # all_heads
            prob = Fraction(1, total)
            prompt = (
                f'Du kaster {n_coins} mynter.\n'
                f'Hva er sannsynligheten for å få kron på alle?'
            )
            steps = [
                f'Totalt: {total} utfall.',
                f'Gunstig utfall: kun 1 (alle kron).',
                f'$P = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_classical',
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── complement ────────────────────────────────────────────────────────────

    def _complement(self, rng: random.Random, seed: int) -> ProblemData:
        contexts = [
            {
                'setup': lambda: (
                    rng.randint(1, 5),  # num
                    rng.randint(6, 12),  # den
                ),
                'template': (
                    'I en klasse er sannsynligheten for at en tilfeldig valgt elev {verb} $P = {frac}$.\n'
                    'Hva er sannsynligheten for at eleven {neg_verb}?'
                ),
                'verbs': [
                    ('liker matematikk', 'ikke liker matematikk'),
                    ('har bestått eksamen', 'ikke har bestått eksamen'),
                    ('sykler til skolen', 'ikke sykler til skolen'),
                ],
            },
        ]

        num = rng.randint(1, 5)
        den = rng.randint(6, 12)
        p = Fraction(num, den)
        comp = 1 - p
        verb, neg_verb = rng.choice([
            ('liker matematikk', 'ikke liker matematikk'),
            ('har bestått eksamen', 'ikke har bestått eksamen'),
            ('sykler til skolen', 'ikke sykler til skolen'),
            ('spiller fotball', 'ikke spiller fotball'),
        ])

        prompt = (
            f'Sannsynligheten for at en tilfeldig elev {verb} er $P = {_frac_latex(p)}$.\n'
            f'Hva er sannsynligheten for at eleven {neg_verb}?'
        )
        steps = [
            'Komplementregelen: $P(A^c) = 1 - P(A)$.',
            f'$P = 1 - {_frac_latex(p)} = {_frac_latex(comp)}$',
        ]
        short = f'$P = {_frac_latex(comp)}$'

        return ProblemData(
            generator_key='probability_classical',
            part='del1',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(comp), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    def evaluate(self, problem: ProblemData, user_answer: str) -> EvalResult:
        return default_evaluate(problem, user_answer)

    def solution(self, problem: ProblemData) -> ProblemData:
        return default_solution(problem)
