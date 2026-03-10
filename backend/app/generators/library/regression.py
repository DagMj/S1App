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


class RegressionGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='regression',
            name='Lineær regresjon',
            description='Lineær regresjon – velg riktig stigningstall blant fem alternativer.',
            tema='Regresjon',
            part='del2',
            answer_type='multiple_choice',
            difficulty=3,
            default_weight=0.8,
        )

    @staticmethod
    def _format_table(x: np.ndarray, y: np.ndarray) -> str:
        rows = ['Verditabell:']
        for x_val, y_val in zip(x, y, strict=True):
            rows.append(f'x={int(x_val)}, y={y_val:.2f}')
        return '\n'.join(rows)

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        slope = rng.choice([1.4, 1.8, 2.2, 2.6, -1.4, -1.8, -2.2, -2.6])
        intercept = rng.choice([1.5, 2.0, 2.5, 3.0, 8.0, 10.0, 12.0])

        x = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
        noise = np.array([rng.choice([-0.2, -0.1, 0.0, 0.1, 0.2]) for _ in x])
        y = slope * x + intercept + noise

        fit = np.polyfit(x, y, 1)
        est_slope = round(float(fit[0]), 2)
        est_intercept = round(float(fit[1]), 2)

        # Build 5 options spaced 0.8 apart, with est_slope at position 2 (middle).
        deltas = [-1.6, -0.8, 0.0, 0.8, 1.6]
        options = [round(est_slope + d, 2) for d in deltas]
        correct_idx = 2  # middle element is always the correct slope

        order = list(range(5))
        rng.shuffle(order)
        letters = ['A', 'B', 'C', 'D', 'E']
        choices = {letters[i]: f'{options[order[i]]:.2f}' for i in range(5)}
        correct_letter = letters[order.index(correct_idx)]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(x, y, color='#0B4F8C', s=45, label='Datapunkter', zorder=3)
        xs = np.linspace(min(x), max(x), 200)
        ax.plot(xs, fit[0] * xs + fit[1], color='#D13B2F', linewidth=2, label='Regresjonslinje', zorder=2)
        ax.set_xticks(x)
        ax.grid(alpha=0.35)
        ax.legend()
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Lineær regresjon')
        asset = asset_service.save_figure(fig, 'regression')
        plt.close(fig)

        prompt = (
            f'{self._format_table(x, y)}\n'
            'Bruk lineær regresjon på datasettet. '
            'Hvilket alternativ gir best estimat for stigningstallet $a$ i modellen $y = ax + b$?'
        )

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='multiple_choice',
            correct_answer=correct_letter,
            solution_short=f'Alternativ {correct_letter}: $a \\approx {est_slope}$, $b \\approx {est_intercept}$.',
            solution_steps=[
                'Kjør lineær regresjon på verditabellen.',
                f'Regresjonslinjen blir omtrent $y = {est_slope}x + {est_intercept}$.',
                f'Stigningstallet er $a \\approx {est_slope}$, dvs. alternativ {correct_letter}.',
            ],
            metadata={
                'tema': 'regresjon',
                'difficulty': 3,
                'latex': True,
                'choices': choices,
            },
            assets=[asset],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
