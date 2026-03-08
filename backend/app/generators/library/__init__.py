from __future__ import annotations

import importlib
import inspect
import pkgutil

from app.generators.core.base import BaseGenerator
from app.generators.core.registry import registry


def register_all_generators() -> None:
    package_name = __name__
    package_path = __path__  # type: ignore[name-defined]

    for module_info in pkgutil.iter_modules(package_path):
        if module_info.name in {'common'}:
            continue

        module = importlib.import_module(f'{package_name}.{module_info.name}')
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if not issubclass(cls, BaseGenerator) or cls is BaseGenerator:
                continue

            instance = cls()
            key = instance.metadata().key
            if key not in registry.keys():
                registry.register(instance)
