from __future__ import annotations

import argparse
import random
import sys

from app.generators.core.registry import registry
from app.generators.library import register_all_generators


def run_stress(generator_key: str, count: int) -> int:
    register_all_generators()
    if generator_key not in registry.keys():
        print(f'Ukjent generator: {generator_key}')
        return 2

    gen = registry.get(generator_key)
    failures: list[str] = []

    for idx in range(count):
        try:
            problem = gen.generate(seed=random.randint(1, 10**9))
            result = gen.evaluate(str(problem.correct_answer), problem)
            if not result.is_correct:
                failures.append(f'[{idx}] correct answer rejected: {problem.correct_answer}')
        except Exception as exc:  # noqa: BLE001
            failures.append(f'[{idx}] exception: {exc}')

        if len(failures) >= 20:
            break

    if failures:
        print('Stress test feilet:')
        for failure in failures:
            print(f' - {failure}')
        print(f'Antall feil: {len(failures)} av {count}')
        return 1

    print(f'OK: {generator_key} genererte {count} oppgaver uten edge-case feil')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Stress-test av S1-generator')
    parser.add_argument('--generator', required=True, help='Generator key')
    parser.add_argument('--count', type=int, default=1000, help='Antall genereringer')
    args = parser.parse_args()

    return run_stress(args.generator, args.count)


if __name__ == '__main__':
    sys.exit(main())
