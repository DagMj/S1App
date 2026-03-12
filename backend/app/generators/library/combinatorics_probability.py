from __future__ import annotations

import math
import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution

# Norwegian color names (adjective form used with "kuler")
_COLORS = ['røde', 'blå', 'grønne', 'gule', 'hvite', 'svarte']


def _color_desc(counts: dict[str, int]) -> str:
    parts = [f'{n} {color}' for color, n in counts.items()]
    if len(parts) == 1:
        return parts[0] + ' kuler'
    return ', '.join(parts[:-1]) + ' og ' + parts[-1] + ' kuler'


class CombinatoricsProbabilityGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='combinatorics_probability',
            name='Kombinatorikk og sannsynlighet',
            description='Trekking av kuler fra pose – fire varianter (ordnet/uordnet, med/uten tilbakelegging).',
            tema='Sannsynlighet',
            part='del2',
            answer_type='number',
            difficulty=3,
            default_weight=0.9,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)

        # --- Build the bag of balls ---
        num_colors = rng.choice([2, 3])
        color_names = rng.sample(_COLORS, num_colors)
        counts: dict[str, int] = {c: rng.randint(3, 7) for c in color_names}
        n = sum(counts.values())

        # k must be < n for non-replacement variants, and small enough for combinatorics
        k = rng.choice([2, 3])
        while k >= n:
            k += 1

        color_desc = _color_desc(counts)
        bag_intro = f'I en pose er det {color_desc} ({n} kuler totalt).'

        subtype = rng.choice([
            'ordered_no_replace',
            'ordered_replace',
            'unordered_no_replace',
            'unordered_replace',
        ])

        if subtype == 'ordered_no_replace':
            ans = math.perm(n, k)
            prompt = (
                f'{bag_intro} '
                f'Du trekker {k} kuler etter hverandre uten tilbakelegging, '
                'og rekkefølgen du trekker dem i betyr noe. '
                f'På hvor mange ulike måter kan dette gjøres?'
            )
            steps = [
                'Rekkefølgen betyr noe og vi legger ikke tilbake → permutasjon uten tilbakelegging.',
                'Formel: $P(n, k) = \\dfrac{n!}{(n-k)!}$',
                f'$P({n}, {k}) = \\dfrac{{{n}!}}{{{n-k}!}} = {ans}$',
            ]

        elif subtype == 'ordered_replace':
            ans = n ** k
            prompt = (
                f'{bag_intro} '
                f'Du trekker {k} kuler etter hverandre med tilbakelegging '
                '(kula legges tilbake og posen ristes mellom hver trekking), '
                'og rekkefølgen betyr noe. '
                f'På hvor mange ulike måter kan dette gjøres?'
            )
            steps = [
                'Rekkefølgen betyr noe og vi legger tilbake → multiplikasjonsprinsippet.',
                f'For hvert av {k} trekk er det {n} mulige kuler.',
                f'Totalt: ${n}^{{{k}}} = {ans}$',
            ]

        elif subtype == 'unordered_no_replace':
            ans = math.comb(n, k)
            prompt = (
                f'{bag_intro} '
                f'Du trekker {k} kuler på én gang uten tilbakelegging. '
                'Vi bryr oss ikke om rekkefølgen. '
                f'Hvor mange ulike utvalg på {k} kuler er mulig?'
            )
            steps = [
                'Vi bryr oss ikke om rekkefølgen og legger ikke tilbake → kombinasjon.',
                'Formel: $C(n, k) = \\dbinom{n}{k} = \\dfrac{n!}{k!\\,(n-k)!}$',
                f'$C({n}, {k}) = \\dfrac{{{n}!}}{{{k}!\\cdot {n-k}!}} = {ans}$',
            ]

        else:  # unordered_replace
            ans = math.comb(n + k - 1, k)
            prompt = (
                f'{bag_intro} '
                f'Du trekker {k} kuler med tilbakelegging, '
                'men vi bryr oss ikke om i hvilken rekkefølge de ble trukket. '
                f'Hvor mange ulike utvalg av {k} kuler er mulig?'
            )
            steps = [
                'Vi bryr oss ikke om rekkefølgen, men legger tilbake → kombinasjon med tilbakelegging.',
                'Formel: $C(n + k - 1,\\, k) = \\dbinom{n+k-1}{k}$',
                f'$C({n}+{k}-1,\\, {k}) = C({n+k-1},\\, {k}) = {ans}$',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=ans,
            solution_short=f'Svar: {ans}',
            solution_steps=steps,
            metadata={
                'tema': 'sannsynlighet',
                'difficulty': 3,
                'latex': True,
                'subtype': subtype,
                'n': n,
                'k': k,
            },
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
