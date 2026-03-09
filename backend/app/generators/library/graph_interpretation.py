from __future__ import annotations

import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution
from app.services.asset_service import asset_service


class GraphInterpretationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='graph_interpretation',
            name='Graf-tolkning',
            description='Tolking av funksjonsgraf med nullpunkter.',
            tema='Funksjoner',
            part='del2',
            answer_type='solution_set',
            difficulty=3,
            default_weight=1.0,
        )

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        r1 = rng.choice([-5, -4, -3, -2, -1])
        r2 = rng.choice([1, 2, 3, 4, 5])
        a = rng.choice([1, 2, 3])

        x = np.linspace(-7, 7, 400)
        y = a * (x - r1) * (x - r2)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y, color='#0B4F8C', linewidth=2)
        ax.axhline(0, color='black', linewidth=0.9)
        ax.axvline(0, color='black', linewidth=0.9)
        ax.set_xticks(np.arange(-6, 7, 1))
        ax.grid(alpha=0.25)
        ax.set_title('Graf for en andregradsfunksjon')
        asset = asset_service.save_figure(fig, 'graph_interp')
        plt.close(fig)

        prompt = 'Les av nullpunktene til grafen. Oppgi løsningsmengden for f(x)=0.'

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='solution_set',
            correct_answer=[r1, r2],
            solution_short=f'Nullpunktene er x={r1} og x={r2}.',
            solution_steps=[
                'Nullpunkter er der grafen krysser x-aksen.',
                f'Grafen krysser ved x={r1} og x={r2}.',
                f'Svar: {{{r1}, {r2}}}.',
            ],
            metadata={'tema': 'graf', 'difficulty': 3, 'latex': False},
            assets=[asset],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
