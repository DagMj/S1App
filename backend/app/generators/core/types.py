from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GeneratorMeta(BaseModel):
    key: str
    name: str
    description: str
    tema: str
    part: str = Field(pattern='^(del1|del2)$')
    answer_type: str
    difficulty: int = 1
    default_weight: float = 1.0


class ProblemData(BaseModel):
    generator_key: str
    part: str
    prompt: str
    answer_type: str
    correct_answer: Any
    solution_short: str
    solution_steps: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
    assets: list[str] = []
    max_points: float = 1.0
    seed: int


class EvalResult(BaseModel):
    is_correct: bool
    score: float
    max_points: float
    confidence: float
    uncertain: bool
    feedback: str
    normalized_answer: str
    details: dict[str, Any] = {}
