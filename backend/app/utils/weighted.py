from __future__ import annotations

import math
import random
from typing import Iterable


def weighted_sample_without_replacement(
    items: Iterable[str], weights: dict[str, float], k: int, seed: int | None = None
) -> list[str]:
    pool = list(items)
    if k > len(pool):
        raise ValueError('k kan ikke være større enn antall elementer')

    rng = random.Random(seed)
    keys: list[tuple[float, str]] = []

    for item in pool:
        w = max(weights.get(item, 0.0), 1e-9)
        u = rng.random()
        key = math.log(u) / w
        keys.append((key, item))

    # Høyest key først gir vektet trekning uten tilbakelegging.
    selected = [item for _, item in sorted(keys, key=lambda t: t[0], reverse=True)[:k]]
    return selected


def weighted_choice(items: list[str], weights: dict[str, float], seed: int | None = None) -> str:
    rng = random.Random(seed)
    cumulative = []
    total = 0.0
    for item in items:
        total += max(weights.get(item, 0.0), 0.0)
        cumulative.append(total)

    if total <= 0:
        return rng.choice(items)

    pick = rng.random() * total
    for idx, edge in enumerate(cumulative):
        if pick <= edge:
            return items[idx]
    return items[-1]
