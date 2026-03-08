from app.generators.core.registry import registry
from app.generators.library import register_all_generators


def test_generators_registered_and_valid():
    register_all_generators()
    keys = registry.keys()
    assert len(keys) >= 10

    for key in keys:
        gen = registry.get(key)
        meta = gen.metadata()
        assert meta.key
        assert meta.part in {'del1', 'del2'}
        assert meta.answer_type


def test_generators_generate_and_accept_correct_answer():
    register_all_generators()

    for key in registry.keys():
        gen = registry.get(key)
        problem = gen.generate(seed=12345)
        assert problem.prompt
        assert problem.solution_short
        assert isinstance(problem.solution_steps, list)
        result = gen.evaluate(str(problem.correct_answer), problem)
        assert result.uncertain or result.is_correct
