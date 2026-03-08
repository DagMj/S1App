from __future__ import annotations

import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_solution
from app.services.asset_service import asset_service
from app.services.evaluation_engine import evaluation_engine


class RegressionGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='regression',
            name='Lineær regresjon',
            description='Lineær regresjon med tydelig verditabell og graf.',
            tema='Regresjon',
            part='del2',
            answer_type='number',
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
        slope = rng.choice([1.4, 1.8, 2.2, 2.6])
        intercept = rng.choice([1.5, 2.0, 2.5, 3.0])

        x = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
        noise = np.array([rng.choice([-0.2, -0.1, 0.0, 0.1, 0.2]) for _ in x])
        y = slope * x + intercept + noise

        fit = np.polyfit(x, y, 1)
        est_slope = round(float(fit[0]), 2)
        est_intercept = round(float(fit[1]), 2)

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

        prompt = (
            f'{self._format_table(x, y)}\n'
            'Bruk lineær regresjon på datasettet. '
            'Oppgi stigningstallet a i modellen y = ax + b (to desimaler).'
        )

        return ProblemData(
            generator_key=self.metadata().key,
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=est_slope,
            solution_short=f'a ≈ {est_slope}, b ≈ {est_intercept}.',
            solution_steps=[
                'Kjør lineær regresjon på verditabellen.',
                f'Regresjonslinjen blir omtrent y = {est_slope}x + {est_intercept}.',
                f'Svar: a ≈ {est_slope}.',
            ],
            metadata={'tema': 'regresjon', 'difficulty': 3, 'latex': False},
            assets=[asset],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        base = evaluation_engine.evaluate(answer, problem)
        if base.is_correct:
            return base

        try:
            user = float(answer.strip().replace(',', '.'))
            expected = float(problem.correct_answer)
            if abs(user - expected) <= 0.2:
                return EvalResult(
                    is_correct=True,
                    score=problem.max_points,
                    max_points=problem.max_points,
                    confidence=0.9,
                    uncertain=False,
                    feedback='Riktig innenfor regresjonstoleranse.',
                    normalized_answer=str(user),
                    details={'layer': 'generator_specific', 'tolerance': 0.2},
                )
        except Exception:
            pass
        return base

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
