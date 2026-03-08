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
            description='Velg modelltype som passer data i verditabell.',
            tema='Modellering',
            part='del2',
            answer_type='model_choice',
            difficulty=3,
            default_weight=0.9,
        )

    def _build_dataset(self, model: str) -> list[tuple[int, float]]:
        x_vals = [0, 1, 2, 3, 4, 5, 6]
        if model == 'A':  # lineær
            return [(x, 2.4 * x + 3.2) for x in x_vals]
        if model == 'B':  # eksponentiell
            return [(x, 1.7 * (1.62**x)) for x in x_vals]
        if model == 'C':  # logistisk
            return [(x, 18 / (1 + 10 * (0.58**x))) for x in x_vals]
        # trigonometrisk
        return [(x, 5 + 2.6 * math.sin((math.pi / 3) * x)) for x in x_vals]

    @staticmethod
    def _format_table(rows: list[tuple[int, float]]) -> str:
        x_row = ', '.join(str(x) for x, _ in rows)
        y_row = ', '.join(f'{y:.2f}' for _, y in rows)
        return f'Verditabell:\nx: {x_row}\ny: {y_row}'

    def generate(self, seed: int | None = None) -> ProblemData:
        rng = random.Random(seed)
        model = rng.choice(['A', 'B', 'C', 'D'])
        rows = self._build_dataset(model)

        prompt = (
            'Velg modellen som passer best til datasettet.\n'
            f'{self._format_table(rows)}\n'
            'A) lineær  B) eksponentiell  C) logistisk  D) trigonometrisk'
        )

        model_name = {'A': 'lineær', 'B': 'eksponentiell', 'C': 'logistisk', 'D': 'trigonometrisk'}[model]

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
