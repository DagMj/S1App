from __future__ import annotations

from app.generators.core.types import EvalResult, ProblemData
from app.services.evaluation_engine import evaluation_engine


def default_evaluate(answer: str, problem: ProblemData) -> EvalResult:
    return evaluation_engine.evaluate(answer, problem)


def default_solution(problem: ProblemData) -> dict:
    return {'short': problem.solution_short, 'steps': problem.solution_steps}


def _term_body(coeff: int, symbol: str) -> str:
    abs_coeff = abs(coeff)
    coeff_part = '' if abs_coeff == 1 and symbol else str(abs_coeff)
    return f'{coeff_part}{symbol}'


def format_polynomial_latex(terms: list[tuple[int, str]]) -> str:
    parts: list[str] = []
    for coeff, symbol in terms:
        if coeff == 0:
            continue

        body = _term_body(coeff, symbol)
        if not parts:
            parts.append(body if coeff > 0 else f'-{body}')
        else:
            sign = '+' if coeff > 0 else '-'
            parts.append(f'{sign} {body}')

    return ' '.join(parts) if parts else '0'


def format_x_shift_latex(shift: int) -> str:
    if shift == 0:
        return 'x'
    if shift > 0:
        return f'x - {shift}'
    return f'x + {abs(shift)}'
