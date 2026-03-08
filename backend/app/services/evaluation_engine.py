from __future__ import annotations

import math
import re
from typing import Any, Callable

from rapidfuzz import fuzz
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.core.config import get_settings
from app.generators.core.types import EvalResult, ProblemData


GeneratorSpecific = Callable[[str, ProblemData, EvalResult], EvalResult | None]


class EvaluationEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.x = sp.Symbol('x')
        self._parser_transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )

    def evaluate(
        self,
        answer: str,
        problem: ProblemData,
        generator_specific: GeneratorSpecific | None = None,
    ) -> EvalResult:
        deterministic = self._evaluate_deterministic(answer, problem)
        if deterministic.is_correct:
            return deterministic

        if generator_specific is not None:
            custom = generator_specific(answer, problem, deterministic)
            if custom is not None:
                return custom

        if self.settings.ai_fallback_enabled:
            fallback = self._evaluate_ai_like(answer, problem)
            if fallback is not None:
                return fallback

        return deterministic

    def _normalize_common(self, answer: str) -> str:
        normalized = (answer or '').strip().lower()
        normalized = normalized.replace(',', '.')
        normalized = normalized.replace(' ', '')
        if re.fullmatch(r'[0-9o.\-+=x{};\[\]\(\),u]+', normalized):
            normalized = normalized.replace('o', '0')
        return normalized

    @staticmethod
    def _fold_letters(text: str) -> str:
        return text.lower().replace('æ', 'ae').replace('ø', 'o').replace('å', 'a')

    def _extract_numeric(self, answer: str) -> str:
        val = self._normalize_common(answer)
        if '=' in val:
            _, rhs = val.split('=', maxsplit=1)
            return rhs
        return val

    def _parse_number(self, value: str) -> float | None:
        try:
            return float(sp.N(sp.sympify(value)))
        except Exception:
            return None

    def _compare_numbers(self, user: str, expected: Any, tol: float = 1e-6) -> tuple[bool, str, float]:
        candidate = self._extract_numeric(user)
        parsed_user = self._parse_number(candidate)
        parsed_expected = self._parse_number(str(expected))
        if parsed_user is None or parsed_expected is None:
            return False, candidate, 0.0
        is_correct = math.isclose(parsed_user, parsed_expected, rel_tol=tol, abs_tol=tol)
        return is_correct, str(parsed_user), 1.0 if is_correct else 0.0

    def _parse_solution_set(self, answer: str) -> list[float] | None:
        raw = (answer or '').strip().lower()
        normalized = raw.replace(' ', '')
        normalized = normalized.replace('{', '').replace('}', '')
        normalized = normalized.replace('[', '').replace(']', '')
        normalized = normalized.replace('eller', ';').replace('og', ';')
        normalized = normalized.replace('x=', '')
        normalized = normalized.replace(',', ';')

        parts = re.split(r'[;]+', normalized)
        values: list[float] = []
        for part in parts:
            if not part:
                continue
            num = self._parse_number(part)
            if num is None:
                values = []
                break
            values.append(float(num))

        if values:
            return sorted(set(values))

        # Fallback: hent ut tall fra fritekst, f.eks. "nullpunktene er x=-2 og x=2".
        matches = re.findall(r'[-+]?\d+(?:[.,]\d+)?(?:/\d+)?', raw)
        if not matches:
            return None

        parsed_values: list[float] = []
        for token in matches:
            num = self._parse_number(token.replace(',', '.'))
            if num is None:
                continue
            parsed_values.append(float(num))

        if not parsed_values:
            return None

        return sorted(set(parsed_values))

    def _compare_solution_sets(self, user: str, expected: Any, tol: float = 1e-6) -> tuple[bool, str, float]:
        user_set = self._parse_solution_set(user)
        exp_list = expected if isinstance(expected, list) else [expected]
        parsed = []
        for val in exp_list:
            parsed_val = self._parse_number(str(val))
            if parsed_val is None:
                return False, self._normalize_common(user), 0.0
            parsed.append(float(parsed_val))
        exp_set = sorted(set(parsed))

        if user_set is None or len(user_set) != len(exp_set):
            return False, self._normalize_common(user), 0.0

        for a, b in zip(user_set, exp_set):
            if not math.isclose(a, b, abs_tol=tol, rel_tol=tol):
                return False, self._normalize_common(user), 0.0
        return True, str(user_set), 1.0

    def _to_expr(self, expression: str) -> sp.Expr | None:
        try:
            cleaned = expression.strip().lower()
            cleaned = cleaned.replace('\u2212', '-')
            cleaned = cleaned.replace('f\u2032(x)', "f'(x)")

            if cleaned.startswith("f'(x)"):
                cleaned = cleaned[len("f'(x)"):].lstrip(':')

            if cleaned.startswith('y='):
                cleaned = cleaned[2:]

            if '=' in cleaned:
                cleaned = cleaned.split('=', maxsplit=1)[1]

            cleaned = cleaned.strip()
            return parse_expr(
                cleaned,
                transformations=self._parser_transformations,
                local_dict={'x': self.x},
                evaluate=True,
            )
        except Exception:
            return None

    def _compare_expressions(self, user: str, expected: Any) -> tuple[bool, str, float]:
        user_expr = self._to_expr(user)
        exp_expr = self._to_expr(str(expected))
        if user_expr is None or exp_expr is None:
            return False, self._normalize_common(user), 0.0
        try:
            if sp.simplify(user_expr - exp_expr) == 0:
                return True, str(user_expr), 1.0
        except Exception:
            return False, str(user_expr), 0.0
        return False, str(user_expr), 0.0

    def _compare_functions(self, user: str, expected: Any) -> tuple[bool, str, float]:
        user_expr = self._to_expr(user)
        exp_expr = self._to_expr(str(expected))
        if user_expr is None or exp_expr is None:
            return False, self._normalize_common(user), 0.0

        try:
            if sp.simplify(user_expr - exp_expr) == 0:
                return True, str(user_expr), 1.0
        except Exception:
            pass

        test_points = [-3, -2, -1, 0, 1, 2, 3]
        matches = 0
        total = 0

        for point in test_points:
            try:
                uv = float(user_expr.subs(self.x, point))
                ev = float(exp_expr.subs(self.x, point))
                total += 1
                if math.isclose(uv, ev, rel_tol=1e-6, abs_tol=1e-6):
                    matches += 1
            except Exception:
                continue

        if total > 0 and matches == total:
            return True, str(user_expr), 0.95
        return False, str(user_expr), 0.0

    def _parse_interval_token(self, token: str) -> tuple[float, float, bool, bool] | None:
        m = re.match(r'^([\[(])\s*([^,]+)\s*,\s*([^\])]+)\s*([\])])$', token)
        if not m:
            return None
        left_closed = m.group(1) == '['
        right_closed = m.group(4) == ']'

        a = self._parse_number(m.group(2))
        b = self._parse_number(m.group(3))
        if a is None or b is None:
            return None
        return float(a), float(b), left_closed, right_closed

    def _parse_intervals(self, text: str) -> list[tuple[float, float, bool, bool]] | None:
        norm = self._normalize_common(text)
        norm = norm.replace('union', 'u')
        parts = [p for p in norm.split('u') if p]
        parsed: list[tuple[float, float, bool, bool]] = []
        for part in parts:
            token = self._parse_interval_token(part)
            if token is None:
                return None
            parsed.append(token)
        parsed.sort(key=lambda t: t[0])
        return parsed

    def _compare_intervals(self, user: str, expected: Any) -> tuple[bool, str, float]:
        user_parsed = self._parse_intervals(user)
        if user_parsed is None:
            return False, self._normalize_common(user), 0.0

        expected_text = expected if isinstance(expected, str) else str(expected)
        exp_parsed = self._parse_intervals(expected_text)
        if exp_parsed is None:
            return False, self._normalize_common(user), 0.0

        if len(user_parsed) != len(exp_parsed):
            return False, self._normalize_common(user), 0.0

        for u, e in zip(user_parsed, exp_parsed):
            if not (
                math.isclose(u[0], e[0], abs_tol=1e-6)
                and math.isclose(u[1], e[1], abs_tol=1e-6)
                and u[2] == e[2]
                and u[3] == e[3]
            ):
                return False, self._normalize_common(user), 0.0

        return True, str(user_parsed), 1.0

    def _compare_choice(self, user: str, expected: Any) -> tuple[bool, str, float]:
        normalized = self._normalize_common(user)
        expected_n = self._normalize_common(str(expected))
        if normalized == expected_n:
            return True, normalized, 1.0

        if expected_n in {'a', 'b', 'c', 'd'}:
            tokens = re.findall(r'[a-zæøå]+', (user or '').lower())
            folded_tokens = {self._fold_letters(token) for token in tokens}

            if expected_n in folded_tokens:
                return True, normalized, 1.0

            model_synonyms = {
                'a': {'lineaer', 'linear', 'linearmodell', 'lineaermodell'},
                'b': {'eksponentiell', 'eksponential', 'exponential', 'eksponentiellmodell'},
                'c': {'logistisk', 'logistic', 'logistiskmodell'},
                'd': {'trigonometrisk', 'trig', 'sinus', 'sinusformet'},
            }
            if folded_tokens.intersection(model_synonyms[expected_n]):
                return True, normalized, 0.95

        return False, normalized, 0.0

    def _evaluate_deterministic(self, answer: str, problem: ProblemData) -> EvalResult:
        answer_type = problem.answer_type
        expected = problem.correct_answer

        is_correct = False
        normalized_answer = self._normalize_common(answer)
        confidence = 0.0

        if answer_type == 'number':
            is_correct, normalized_answer, confidence = self._compare_numbers(answer, expected)
        elif answer_type in {'expression', 'algebra'}:
            is_correct, normalized_answer, confidence = self._compare_expressions(answer, expected)
        elif answer_type == 'solution_set':
            is_correct, normalized_answer, confidence = self._compare_solution_sets(answer, expected)
        elif answer_type == 'function':
            is_correct, normalized_answer, confidence = self._compare_functions(answer, expected)
        elif answer_type == 'interval':
            is_correct, normalized_answer, confidence = self._compare_intervals(answer, expected)
        elif answer_type in {'multiple_choice', 'model_choice'}:
            is_correct, normalized_answer, confidence = self._compare_choice(answer, expected)
        else:
            is_correct, normalized_answer, confidence = self._compare_choice(answer, expected)

        score = problem.max_points if is_correct else 0.0
        feedback = 'Riktig.' if is_correct else 'Ikke riktig svar.'
        return EvalResult(
            is_correct=is_correct,
            score=score,
            max_points=problem.max_points,
            confidence=confidence,
            uncertain=False,
            feedback=feedback,
            normalized_answer=normalized_answer,
            details={'layer': 'deterministic', 'answer_type': answer_type},
        )

    def _evaluate_ai_like(self, answer: str, problem: ProblemData) -> EvalResult | None:
        normalized = self._normalize_common(answer)
        expected = self._normalize_common(str(problem.correct_answer))
        similarity = fuzz.ratio(normalized, expected)

        if similarity >= 92:
            return EvalResult(
                is_correct=True,
                score=problem.max_points,
                max_points=problem.max_points,
                confidence=0.65,
                uncertain=True,
                feedback='Svar tolket som sannsynlig riktig (AI-fallback).',
                normalized_answer=normalized,
                details={'layer': 'ai_fallback', 'similarity': similarity},
            )

        if similarity >= 80:
            return EvalResult(
                is_correct=False,
                score=0.0,
                max_points=problem.max_points,
                confidence=0.4,
                uncertain=True,
                feedback='Svar er uklart. Flagget som usikkert.',
                normalized_answer=normalized,
                details={'layer': 'ai_fallback', 'similarity': similarity},
            )

        return None


evaluation_engine = EvaluationEngine()


