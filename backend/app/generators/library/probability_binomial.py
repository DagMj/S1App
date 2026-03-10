from __future__ import annotations

import random
from fractions import Fraction
from math import comb

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _frac_latex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return rf'\dfrac{{{f.numerator}}}{{{f.denominator}}}'


def _binom_prob(n: int, k: int, p: Fraction) -> Fraction:
    return Fraction(comb(n, k)) * (p ** k) * ((1 - p) ** (n - k))


class ProbabilityBinomialGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='probability_binomial',
            name='Binomisk sannsynlighet',
            description='Binomisk fordeling P(X=k) = C(n,k)·p^k·(1-p)^(n-k) med ulike kontekster.',
            tema='Sannsynlighet',
            part='del2',
            answer_type='number',
            difficulty=4,
            default_weight=1.0,
        )

    def generate(self, seed: int) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choices(
            ['coin', 'die', 'freeThrow', 'multipleChoice', 'medicine'],
            weights=[20, 20, 20, 20, 20],
        )[0]

        if subtype == 'coin':
            return self._coin(rng, seed)
        elif subtype == 'die':
            return self._die(rng, seed)
        elif subtype == 'freeThrow':
            return self._free_throw(rng, seed)
        elif subtype == 'multipleChoice':
            return self._multiple_choice(rng, seed)
        else:
            return self._medicine(rng, seed)

    # ── shared builder ────────────────────────────────────────────────────────

    def _build_problem(
        self,
        seed: int,
        prompt: str,
        n: int,
        k: int,
        p: Fraction,
        context_name: str,
        question_type: str,  # 'exactly', 'at_least', 'at_most'
        extra_steps: list[str] | None = None,
    ) -> ProblemData:
        q = 1 - p

        if question_type == 'exactly':
            prob = _binom_prob(n, k, p)
            binom_line = (
                rf'$P(X = {k}) = \binom{{{n}}}{{{k}}} \cdot '
                rf'{_frac_latex(p)}^{{{k}}} \cdot {_frac_latex(q)}^{{{n-k}}}$'
            )
            steps = [
                f'$X \\sim B(n={n},\\, p={_frac_latex(p)})$',
                r'Binomisk formel: $P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}$',
                binom_line,
                f'$= {comb(n,k)} \\cdot {_frac_latex(p**k)} \\cdot {_frac_latex(q**(n-k))}$',
                f'$= {_frac_latex(prob)}$',
            ]
            short = f'$P(X={k}) = {_frac_latex(prob)}$'

        elif question_type == 'at_least':
            prob = sum(_binom_prob(n, i, p) for i in range(k, n + 1))
            complement = 1 - prob
            steps = [
                f'$X \\sim B(n={n},\\, p={_frac_latex(p)})$',
                f'$P(X \\geq {k}) = 1 - P(X \\leq {k-1})$',
            ]
            for i in range(k):
                pi = _binom_prob(n, i, p)
                steps.append(
                    rf'$P(X={i}) = \binom{{{n}}}{{{i}}} \cdot {_frac_latex(p)}^{i} \cdot {_frac_latex(q)}^{{{n-i}}} = {_frac_latex(pi)}$'
                )
            steps.append(f'$P(X \\leq {k-1}) = {_frac_latex(complement)}$')
            steps.append(f'$P(X \\geq {k}) = 1 - {_frac_latex(complement)} = {_frac_latex(prob)}$')
            short = f'$P(X \\geq {k}) = {_frac_latex(prob)}$'

        else:  # at_most
            prob = sum(_binom_prob(n, i, p) for i in range(0, k + 1))
            steps = [
                f'$X \\sim B(n={n},\\, p={_frac_latex(p)})$',
                f'$P(X \\leq {k}) = \\sum_{{i=0}}^{{{k}}} P(X=i)$',
            ]
            for i in range(k + 1):
                pi = _binom_prob(n, i, p)
                steps.append(
                    rf'$P(X={i}) = \binom{{{n}}}{{{i}}} \cdot {_frac_latex(p)}^{i} \cdot {_frac_latex(q)}^{{{n-i}}} = {_frac_latex(pi)}$'
                )
            steps.append(f'$P(X \\leq {k}) = {_frac_latex(prob)}$')
            short = f'$P(X \\leq {k}) = {_frac_latex(prob)}$'

        if extra_steps:
            steps = extra_steps + steps

        return ProblemData(
            generator_key='probability_binomial',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── coin ──────────────────────────────────────────────────────────────────

    def _coin(self, rng: random.Random, seed: int) -> ProblemData:
        n = rng.randint(4, 8)
        k = rng.randint(1, n - 1)
        p = Fraction(1, 2)
        q_type = rng.choice(['exactly', 'at_least', 'at_most'])

        if q_type == 'exactly':
            prompt = (
                f'Du kaster en rettferdig mynt {n} ganger.\n'
                f'Hva er sannsynligheten for å få nøyaktig {k} kron?'
            )
        elif q_type == 'at_least':
            prompt = (
                f'Du kaster en rettferdig mynt {n} ganger.\n'
                f'Hva er sannsynligheten for å få minst {k} kron?'
            )
        else:
            prompt = (
                f'Du kaster en rettferdig mynt {n} ganger.\n'
                f'Hva er sannsynligheten for å få høyst {k} kron?'
            )

        return self._build_problem(seed, prompt, n, k, p, 'mynt', q_type)

    # ── die ───────────────────────────────────────────────────────────────────

    def _die(self, rng: random.Random, seed: int) -> ProblemData:
        n = rng.randint(4, 7)
        target = rng.randint(1, 6)
        k = rng.randint(1, min(3, n - 1))
        p = Fraction(1, 6)
        q_type = rng.choice(['exactly', 'at_least'])

        if q_type == 'exactly':
            prompt = (
                f'Du kaster en terning {n} ganger.\n'
                f'Hva er sannsynligheten for å få {target}-er nøyaktig {k} gang{"er" if k > 1 else ""}?'
            )
        else:
            prompt = (
                f'Du kaster en terning {n} ganger.\n'
                f'Hva er sannsynligheten for å få {target}-er minst {k} gang{"er" if k > 1 else ""}?'
            )

        return self._build_problem(seed, prompt, n, k, p, 'terning', q_type)

    # ── free throw ────────────────────────────────────────────────────────────

    def _free_throw(self, rng: random.Random, seed: int) -> ProblemData:
        sport = rng.choice([
            ('basketballspiller', 'frikastvinger', 'frikast'),
            ('håndballspiller', 'straffekast', 'straffekast'),
            ('fotballspiller', 'straffespark', 'straffespark'),
        ])
        name = rng.choice(['Ola', 'Kari', 'Jonas', 'Emma', 'Lars'])
        p_num = rng.choice([3, 4])
        p = Fraction(p_num, 5)  # 60% or 80%
        n = rng.randint(4, 7)
        k = rng.randint(2, min(4, n - 1))
        q_type = rng.choice(['exactly', 'at_least'])
        context, action_pl, action_sg = sport

        if q_type == 'exactly':
            prompt = (
                f'{name} er en dyktig {context} som scorer på {_frac_latex(p)} av sine {action_pl}.\n'
                f'{name} tar {n} {action_pl}.\n'
                f'Hva er sannsynligheten for å score nøyaktig {k} ganger?'
            )
        else:
            prompt = (
                f'{name} er en dyktig {context} som scorer på {_frac_latex(p)} av sine {action_pl}.\n'
                f'{name} tar {n} {action_pl}.\n'
                f'Hva er sannsynligheten for å score minst {k} ganger?'
            )

        return self._build_problem(seed, prompt, n, k, p, context, q_type)

    # ── multiple choice ───────────────────────────────────────────────────────

    def _multiple_choice(self, rng: random.Random, seed: int) -> ProblemData:
        choices = rng.choice([4, 5])
        p = Fraction(1, choices)
        n = rng.randint(5, 8)
        k = rng.randint(2, min(4, n - 1))
        q_type = rng.choice(['exactly', 'at_least'])

        if q_type == 'exactly':
            prompt = (
                f'En flervalgstest har {n} spørsmål, hvert med {choices} svaralternativer.\n'
                f'En elev gjetter tilfeldig på alle spørsmålene.\n'
                f'Hva er sannsynligheten for å svare riktig på nøyaktig {k} spørsmål?'
            )
        else:
            prompt = (
                f'En flervalgstest har {n} spørsmål, hvert med {choices} svaralternativer.\n'
                f'En elev gjetter tilfeldig på alle spørsmålene.\n'
                f'Hva er sannsynligheten for å svare riktig på minst {k} spørsmål?'
            )

        extra = [f'Sannsynligheten for riktig svar på ett spørsmål: $p = {_frac_latex(p)}$.']
        return self._build_problem(seed, prompt, n, k, p, 'flervalg', q_type, extra)

    # ── medicine / defect ─────────────────────────────────────────────────────

    def _medicine(self, rng: random.Random, seed: int) -> ProblemData:
        context = rng.choice([
            {
                'setup': 'En medisin virker på {pct}% av pasientene.',
                'actor': 'pasienter',
                'success': 'virker',
            },
            {
                'setup': 'En fabrikk produserer produkter der {pct}% er defekte.',
                'actor': 'produkter',
                'success': 'er defekte',
            },
            {
                'setup': '{pct}% av frøene spirer.',
                'actor': 'frø',
                'success': 'spirer',
            },
        ])
        pct = rng.choice([20, 25, 30, 40])
        p = Fraction(pct, 100)
        n = rng.randint(5, 8)
        k = rng.randint(1, min(3, n - 1))
        q_type = rng.choice(['exactly', 'at_most'])

        setup = context['setup'].format(pct=pct)
        actor = context['actor']
        success = context['success']

        if q_type == 'exactly':
            prompt = (
                f'{setup}\n'
                f'Man velger tilfeldig {n} {actor}.\n'
                f'Hva er sannsynligheten for at nøyaktig {k} {success}?'
            )
        else:
            prompt = (
                f'{setup}\n'
                f'Man velger tilfeldig {n} {actor}.\n'
                f'Hva er sannsynligheten for at høyst {k} {success}?'
            )

        extra = [f'$p = {_frac_latex(p)}$ ({pct}%), $n = {n}$, binomisk fordeling.']
        return self._build_problem(seed, prompt, n, k, p, actor, q_type, extra)

    def evaluate(self, problem: ProblemData, user_answer: str) -> EvalResult:
        return default_evaluate(problem, user_answer)

    def solution(self, problem: ProblemData) -> ProblemData:
        return default_solution(problem)
