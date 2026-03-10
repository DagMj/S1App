from __future__ import annotations

import random
from fractions import Fraction

from app.generators.core.base import BaseGenerator
from app.generators.core.types import EvalResult, GeneratorMeta, ProblemData
from app.generators.library.common import default_evaluate, default_solution


def _frac_latex(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return rf'\dfrac{{{f.numerator}}}{{{f.denominator}}}'


class ProbabilityTwoStepGenerator(BaseGenerator):
    def metadata(self) -> GeneratorMeta:
        return GeneratorMeta(
            key='probability_two_step',
            name='Sammensatt sannsynlighet',
            description='Sekvensielle trekk uten tilbakelegging – multiplikasjonsregelen P(A∩B) = P(A)·P(B|A).',
            tema='Sannsynlighet',
            part='del2',
            answer_type='number',
            difficulty=3,
            default_weight=1.0,
        )

    def generate(self, seed: int) -> ProblemData:
        rng = random.Random(seed)
        subtype = rng.choices(
            ['balls', 'socks', 'students', 'cards'],
            weights=[30, 25, 25, 20],
        )[0]

        if subtype == 'balls':
            return self._balls(rng, seed)
        elif subtype == 'socks':
            return self._socks(rng, seed)
        elif subtype == 'students':
            return self._students(rng, seed)
        else:
            return self._cards(rng, seed)

    # ── balls ─────────────────────────────────────────────────────────────────

    def _balls(self, rng: random.Random, seed: int) -> ProblemData:
        total = rng.randint(8, 15)
        red = rng.randint(2, total - 3)
        blue = total - red
        variant = rng.choice(['both_red', 'both_blue', 'one_each'])

        if variant == 'both_red':
            p1 = Fraction(red, total)
            p2 = Fraction(red - 1, total - 1)
            prob = p1 * p2
            prompt = (
                f'En pose inneholder {red} røde og {blue} blå kuler.\n'
                f'Du trekker to kuler uten tilbakelegging.\n'
                f'Hva er sannsynligheten for at begge kulene er røde?'
            )
            steps = [
                f'Første trekk: $P(\\text{{rød}}) = {_frac_latex(p1)}$.',
                f'Andre trekk (gitt første var rød): $P(\\text{{rød}}) = {_frac_latex(p2)}$.',
                f'$P(\\text{{begge røde}}) = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'both_blue':
            p1 = Fraction(blue, total)
            p2 = Fraction(blue - 1, total - 1)
            prob = p1 * p2
            prompt = (
                f'En pose inneholder {red} røde og {blue} blå kuler.\n'
                f'Du trekker to kuler uten tilbakelegging.\n'
                f'Hva er sannsynligheten for at begge kulene er blå?'
            )
            steps = [
                f'Første trekk: $P(\\text{{blå}}) = {_frac_latex(p1)}$.',
                f'Andre trekk (gitt første var blå): $P(\\text{{blå}}) = {_frac_latex(p2)}$.',
                f'$P(\\text{{begge blå}}) = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        else:  # one_each (rød, deretter blå)
            p1 = Fraction(red, total)
            p2 = Fraction(blue, total - 1)
            p_rb = p1 * p2
            p1b = Fraction(blue, total)
            p2r = Fraction(red, total - 1)
            p_br = p1b * p2r
            prob = p_rb + p_br
            prompt = (
                f'En pose inneholder {red} røde og {blue} blå kuler.\n'
                f'Du trekker to kuler uten tilbakelegging.\n'
                f'Hva er sannsynligheten for å få én rød og én blå kule?'
            )
            steps = [
                f'Alternativ 1 (rød–blå): ${_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(p_rb)}$.',
                f'Alternativ 2 (blå–rød): ${_frac_latex(p1b)} \\cdot {_frac_latex(p2r)} = {_frac_latex(p_br)}$.',
                f'$P = {_frac_latex(p_rb)} + {_frac_latex(p_br)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_two_step',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── socks ─────────────────────────────────────────────────────────────────

    def _socks(self, rng: random.Random, seed: int) -> ProblemData:
        black = rng.randint(3, 7)
        white = rng.randint(3, 7)
        total = black + white
        variant = rng.choice(['matching_pair', 'black_then_white'])

        if variant == 'matching_pair':
            p_bb = Fraction(black, total) * Fraction(black - 1, total - 1)
            p_ww = Fraction(white, total) * Fraction(white - 1, total - 1)
            prob = p_bb + p_ww
            prompt = (
                f'I en skuff ligger {black} svarte og {white} hvite sokker.\n'
                f'Du trekker to sokker tilfeldig uten å se.\n'
                f'Hva er sannsynligheten for å få et matchende par?'
            )
            steps = [
                f'P(begge svarte) = ${_frac_latex(Fraction(black, total))} \\cdot {_frac_latex(Fraction(black-1, total-1))} = {_frac_latex(p_bb)}$.',
                f'P(begge hvite) = ${_frac_latex(Fraction(white, total))} \\cdot {_frac_latex(Fraction(white-1, total-1))} = {_frac_latex(p_ww)}$.',
                f'$P(\\text{{par}}) = {_frac_latex(p_bb)} + {_frac_latex(p_ww)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        else:
            p1 = Fraction(black, total)
            p2 = Fraction(white, total - 1)
            prob = p1 * p2
            prompt = (
                f'I en skuff ligger {black} svarte og {white} hvite sokker.\n'
                f'Du trekker én sokk, og deretter en til uten tilbakelegging.\n'
                f'Hva er sannsynligheten for at den første er svart og den andre er hvit?'
            )
            steps = [
                f'$P(\\text{{svart}}) = {_frac_latex(p1)}$.',
                f'$P(\\text{{hvit}} \\mid \\text{{svart}}) = {_frac_latex(p2)}$.',
                f'$P = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_two_step',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── students ──────────────────────────────────────────────────────────────

    def _students(self, rng: random.Random, seed: int) -> ProblemData:
        total = rng.randint(15, 25)
        girls = rng.randint(6, total - 4)
        boys = total - girls
        k = rng.choice([2, 3])

        if k == 2:
            p1 = Fraction(girls, total)
            p2 = Fraction(girls - 1, total - 1)
            prob = p1 * p2
            prompt = (
                f'I en klasse er det {girls} jenter og {boys} gutter ({total} elever totalt).\n'
                f'To elever velges tilfeldig uten tilbakelegging.\n'
                f'Hva er sannsynligheten for at begge er jenter?'
            )
            steps = [
                f'$P(\\text{{jente}}_1) = {_frac_latex(p1)}$.',
                f'$P(\\text{{jente}}_2 \\mid \\text{{jente}}_1) = {_frac_latex(p2)}$.',
                f'$P = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'
        else:
            p1 = Fraction(girls, total)
            p2 = Fraction(girls - 1, total - 1)
            p3 = Fraction(girls - 2, total - 2)
            prob = p1 * p2 * p3
            prompt = (
                f'I en klasse er det {girls} jenter og {boys} gutter ({total} elever totalt).\n'
                f'Tre elever velges tilfeldig uten tilbakelegging.\n'
                f'Hva er sannsynligheten for at alle tre er jenter?'
            )
            steps = [
                f'$P(\\text{{jente}}_1) = {_frac_latex(p1)}$.',
                f'$P(\\text{{jente}}_2 \\mid \\ldots) = {_frac_latex(p2)}$.',
                f'$P(\\text{{jente}}_3 \\mid \\ldots) = {_frac_latex(p3)}$.',
                f'$P = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} \\cdot {_frac_latex(p3)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_two_step',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    # ── cards ─────────────────────────────────────────────────────────────────

    def _cards(self, rng: random.Random, seed: int) -> ProblemData:
        variant = rng.choice(['both_hearts', 'both_face', 'ace_then_ace'])

        if variant == 'both_hearts':
            p1 = Fraction(13, 52)
            p2 = Fraction(12, 51)
            prob = p1 * p2
            prompt = (
                'Du trekker to kort fra en vanlig kortstokk (52 kort) uten tilbakelegging.\n'
                'Hva er sannsynligheten for at begge kortene er hjerter?'
            )
            steps = [
                f'$P(\\text{{hjerte}}_1) = {_frac_latex(p1)}$.',
                f'$P(\\text{{hjerte}}_2 \\mid \\text{{hjerte}}_1) = {_frac_latex(p2)}$.',
                f'$P = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        elif variant == 'both_face':
            # J, Q, K = 12 face cards
            p1 = Fraction(12, 52)
            p2 = Fraction(11, 51)
            prob = p1 * p2
            prompt = (
                'Du trekker to kort fra en vanlig kortstokk (52 kort) uten tilbakelegging.\n'
                'Hva er sannsynligheten for at begge kortene er bildekort (J, Q eller K)?'
            )
            steps = [
                f'Bildekort: $4 \\times 3 = 12$ stykker.',
                f'$P(\\text{{bildekort}}_1) = {_frac_latex(p1)}$.',
                f'$P(\\text{{bildekort}}_2 \\mid \\text{{bildekort}}_1) = {_frac_latex(p2)}$.',
                f'$P = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        else:  # ace_then_ace
            p1 = Fraction(4, 52)
            p2 = Fraction(3, 51)
            prob = p1 * p2
            prompt = (
                'Du trekker to kort fra en vanlig kortstokk (52 kort) uten tilbakelegging.\n'
                'Hva er sannsynligheten for at begge kortene er ess?'
            )
            steps = [
                f'$P(\\text{{ess}}_1) = {_frac_latex(p1)}$.',
                f'$P(\\text{{ess}}_2 \\mid \\text{{ess}}_1) = {_frac_latex(p2)}$.',
                f'$P = {_frac_latex(p1)} \\cdot {_frac_latex(p2)} = {_frac_latex(prob)}$',
            ]
            short = f'$P = {_frac_latex(prob)}$'

        return ProblemData(
            generator_key='probability_two_step',
            part='del2',
            prompt=prompt,
            answer_type='number',
            correct_answer=round(float(prob), 6),
            solution_short=short,
            solution_steps=steps,
            seed=seed,
        )

    def evaluate(self, problem: ProblemData, user_answer: str) -> EvalResult:
        return default_evaluate(problem, user_answer)

    def solution(self, problem: ProblemData) -> ProblemData:
        return default_solution(problem)
