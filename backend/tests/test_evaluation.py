from app.generators.core.types import ProblemData
from app.services.evaluation_engine import evaluation_engine


def test_number_accepts_x_equals_value():
    problem = ProblemData(
        generator_key='t',
        part='del1',
        prompt='x?',
        answer_type='number',
        correct_answer=3,
        solution_short='3',
        solution_steps=[''],
        metadata={},
        assets=[],
        seed=1,
    )
    result = evaluation_engine.evaluate('x=3', problem)
    assert result.is_correct


def test_decimal_comma_supported():
    problem = ProblemData(
        generator_key='t',
        part='del1',
        prompt='x?',
        answer_type='number',
        correct_answer=2.5,
        solution_short='2.5',
        solution_steps=[''],
        metadata={},
        assets=[],
        seed=1,
    )
    result = evaluation_engine.evaluate('2,5', problem)
    assert result.is_correct


def test_expression_equivalence():
    problem = ProblemData(
        generator_key='t',
        part='del1',
        prompt='forenkle',
        answer_type='expression',
        correct_answer='x+2',
        solution_short='x+2',
        solution_steps=[''],
        metadata={},
        assets=[],
        seed=1,
    )
    result = evaluation_engine.evaluate('2+x', problem)
    assert result.is_correct


def test_expression_accepts_implicit_parenthesis_multiplication():
    problem = ProblemData(
        generator_key='t',
        part='del1',
        prompt='faktoriser',
        answer_type='expression',
        correct_answer='(x+4)*(x+5)',
        solution_short='(x+4)(x+5)',
        solution_steps=[''],
        metadata={},
        assets=[],
        seed=1,
    )
    assert evaluation_engine.evaluate('(x+4)(x+5)', problem).is_correct


def test_solution_set_accepts_braces_and_text_form():
    problem = ProblemData(
        generator_key='t',
        part='del1',
        prompt='los',
        answer_type='solution_set',
        correct_answer=[-2, 2],
        solution_short='{-2,2}',
        solution_steps=[''],
        metadata={},
        assets=[],
        seed=1,
    )

    assert evaluation_engine.evaluate('{-2, 2}', problem).is_correct
    assert evaluation_engine.evaluate('Nullpunktene er x=-2 og x=2', problem).is_correct


def test_model_choice_accepts_letter_and_model_name():
    problem = ProblemData(
        generator_key='t',
        part='del2',
        prompt='velg modell',
        answer_type='model_choice',
        correct_answer='A',
        solution_short='A',
        solution_steps=[''],
        metadata={},
        assets=[],
        seed=1,
    )

    assert evaluation_engine.evaluate('A', problem).is_correct
    assert evaluation_engine.evaluate('lineær', problem).is_correct

def test_expression_accepts_equivalent_factored_form_with_scaling():
    problem = ProblemData(
        generator_key='t',
        part='del1',
        prompt='faktoriser',
        answer_type='expression',
        correct_answer='6*(x-2/3)*(x+5/2)',
        solution_short='6(x-2/3)(x+5/2)',
        solution_steps=[''],
        metadata={},
        assets=[],
        seed=1,
    )
    assert evaluation_engine.evaluate('(3x-2)(2x+5)', problem).is_correct
