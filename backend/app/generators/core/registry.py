from __future__ import annotations

from app.generators.core.base import BaseGenerator


class GeneratorRegistry:
    def __init__(self) -> None:
        self._generators: dict[str, BaseGenerator] = {}

    def register(self, generator: BaseGenerator) -> None:
        key = generator.metadata().key
        if key in self._generators:
            raise ValueError(f'Generator med key {key} er allerede registrert')
        self._generators[key] = generator

    def get(self, key: str) -> BaseGenerator:
        if key not in self._generators:
            raise KeyError(f'Ukjent generator: {key}')
        return self._generators[key]

    def keys(self) -> list[str]:
        return sorted(self._generators.keys())

    def all(self) -> list[BaseGenerator]:
        return list(self._generators.values())


registry = GeneratorRegistry()
