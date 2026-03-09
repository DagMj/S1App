from __future__ import annotations

import math
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution
from app.services.asset_service import asset_service


class ModelVisualizationGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='model_visualization',
            name='Modellvisualisering',
            description='Grafisk modelltolkning med tydelige modellformer.',
            tema='Modellering',
            part='del2',
            answer_type='model_choice',
            difficulty=3,
            default_weight=0.8,
        )

    def _build_curve(self, model: str, x: np.ndarray, rng: random.Random) -> tuple[np.ndarray, str]:
        if model == 'A':
            m = rng.choice([0.8, 1.2, 1.6, 2.0])
            c = rng.choice([1.0, 2.0, 3.0, 4.0])
            return m * x + c, 'Lineær modell'

        if model == 'B':
            a = rng.choice([1.2, 1.6, 2.0])
            b = rng.choice([1.25, 1.35, 1.5])
            return a * (b**x), 'Eksponentiell modell'

        if model == 'C':
            L = rng.choice([10.0, 12.0, 15.0])
            A = rng.choice([6.0, 8.0, 10.0])
            k = rng.choice([0.7, 0.9, 1.1])
            return L / (1 + A * np.exp(-k * x)), 'Logistisk modell'

        amp = rng.choice([2.0, 2.5, 3.0])
        c0 = rng.choice([4.0, 5.0, 6.0])
        return c0 + amp * np.sin((math.pi / 3) * x), 'Trigonometrisk modell'

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        model = rng.choice(['A', 'B', 'C', 'D'])
        x = np.linspace(0, 6, 220)
        y, title = self._build_curve(model, x, rng)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, y, color='#0B4F8C', linewidth=2.2)
        ax.grid(alpha=0.3)
        ax.set_title(title)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        asset = asset_service.save_figure(fig, 'model_visual')
        plt.close(fig)

        prompt = (
            'Hvilken modelltype passer grafen best?\n'
            'A) lineær  B) eksponentiell  C) logistisk  D) trigonometrisk'
        )

        model_name = {
            'A': 'lineær',
            'B': 'eksponentiell',
            'C': 'logistisk',
            'D': 'trigonometrisk',
        }[model]

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='model_choice',
            correct_answer=model,
            solution_short=f'Riktig modell er {model} ({model_name}).',
            solution_steps=[
                'Se på kurvens form og vekstmønster.',
                f'Denne grafen passer best med {model_name} modell.',
                f'Riktig valg: {model}.',
            ],
            metadata={'tema': 'modellvisualisering', 'difficulty': 3, 'latex': False},
            assets=[asset],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)

