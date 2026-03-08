from __future__ import annotations

from abc import ABC, abstractmethod
import random

from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData


class BaseGenerator(ABC):
    @abstractmethod
    def metadata(self) -> GeneratorMeta:
        raise NotImplementedError

    @abstractmethod
    def generate(self, seed: int | None = None) -> ProblemData:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, answer: str, problem: ProblemData) -> EvalResult:
        raise NotImplementedError

    @abstractmethod
    def solution(self, problem: ProblemData) -> dict:
        raise NotImplementedError

    @staticmethod
    def rng(seed: int | None = None) -> random.Random:
        return random.Random(seed)
