from __future__ import annotations

import math
import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class CombinatoricsProbabilityGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='combinatorics_probability',
            name='Kombinatorikk og sannsynlighet',
            description='Kombinatorikk- og sannsynlighetsoppgaver for S1.',
            tema='Sannsynlighet',
            part='del2',
            answer_type='number',
            difficulty=3,
            default_weight=0.9,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choice(['comb', 'perm', 'prob'])

        if subtype == 'comb':
            n = rng.choice([9, 10, 11, 12, 13, 14])
            k = rng.choice([3, 4, 5])
            ans = math.comb(n, k)
            prompt = f'Hvor mange ulike grupper på {k} elever kan lages fra {n} elever?'
            steps = [
                'Når rekkefølgen ikke betyr noe, bruker vi kombinasjoner.',
                f'Formel: C(n,k)=n!/(k!(n-k)!). Her: C({n},{k})={n}!/({k}!({n-k})!).',
                f'Beregning gir C({n},{k})={ans}.',
            ]

        elif subtype == 'perm':
            n = rng.choice([7, 8, 9, 10])
            k = rng.choice([3, 4])
            ans = math.perm(n, k)
            prompt = f'På hvor mange måter kan {k} ulike verv fordeles blant {n} elever?'
            steps = [
                'Når rekkefølgen betyr noe, bruker vi permutasjoner.',
                f'Formel: P(n,k)=n!/(n-k)!. Her: P({n},{k})={n}!/({n-k})!.',
                f'Beregning gir P({n},{k})={ans}.',
            ]

        else:
            total = rng.choice([8, 10, 12, 15])
            good = rng.choice([2, 3, 4, 5, 6])
            if good >= total:
                good = total - 1
            ans = round(good / total, 4)
            prompt = (
                f'I en pose er det {good} røde og {total-good} blå kuler. '
                'En kule trekkes tilfeldig. Hva er sannsynligheten for rød kule?'
            )
            steps = [
                f'Formel: P(A)=antall gunstige / antall mulige = {good}/{total}.',
                f'P(rød) = {ans}.',
            ]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=ans,
            solution_short=f'Svar: {ans}',
            solution_steps=steps,
            metadata={'tema': 'sannsynlighet', 'difficulty': 3, 'latex': False, 'subtype': subtype},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
