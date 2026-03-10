from __future__ import annotations

import math
import random

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


class ModelChoiceGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='model_choice',
            name='Modellvalg',
            description='Velg modellen som passer best til data i verditabell.',
            tema='Modellering',
            part='del2',
            answer_type='model_choice',
            difficulty=3,
            default_weight=0.9,
        )

    def _build_dataset(self, model: str, rng: random.Random) -> list[tuple[int, float]]:
        x_vals = [0, 1, 2, 3, 4, 5, 6]
        if model == 'A':  # lineær
            m = rng.choice([1.5, 2.0, 2.4, 3.0, 3.5])
            c = rng.choice([1.0, 2.0, 3.0, 4.0, 5.0])
            return [(x, m * x + c) for x in x_vals]
        if model == 'B':  # eksponentiell
            a = rng.choice([1.5, 2.0, 2.5, 3.0])
            b = rng.choice([1.4, 1.5, 1.6, 1.8])
            return [(x, a * (b**x)) for x in x_vals]
        if model == 'C':  # logistisk
            L = rng.choice([15.0, 18.0, 20.0, 25.0])
            A = rng.choice([8.0, 10.0, 12.0])
            k = rng.choice([0.5, 0.6, 0.7, 0.8])
            return [(x, L / (1 + A * (k**x))) for x in x_vals]
        # trigonometrisk
        amp = rng.choice([2.0, 2.5, 3.0, 3.5])
        center = rng.choice([4.0, 5.0, 6.0])
        period_factor = rng.choice([math.pi / 3, math.pi / 4])
        return [(x, center + amp * math.sin(period_factor * x)) for x in x_vals]

    @staticmethod
    def _format_table(rows: list[tuple[int, float]]) -> str:
        x_row = ', '.join(str(x) for x, _ in rows)
        y_row = ', '.join(f'{y:.2f}' for _, y in rows)
        return f'Verditabell:\nx: {x_row}\ny: {y_row}'

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        model = rng.choice(['A', 'B', 'C', 'D'])
        rows = self._build_dataset(model, rng)

        prompt = (
            'Velg modellen som passer best til datasettet.\n'
            f'{self._format_table(rows)}\n'
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
            solution_short=f'Riktig modellvalg er {model} ({model_name}).',
            solution_steps=[
                'Se på vekstmønsteret i verditabellen.',
                f'Mønsteret passer best med {model_name} modell.',
                f'Svar: {model}.',
            ],
            metadata={'tema': 'modellering', 'difficulty': 3, 'latex': False},
            assets=[],
            seed=seed or rng.randint(1, 10**9),
        )

    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        return default_evaluate(answer, problem)

    def solution(self, problem: ProblemData) -> dict:
        return default_solution(problem)
