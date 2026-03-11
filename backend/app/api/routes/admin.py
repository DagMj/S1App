import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.generators.core.registry import registry
from app.models.generator import GeneratorConfig
from app.schemas.generator import GeneratorConfigRead, GeneratorConfigUpdate, GeneratorSampleResponse
from app.services.generator_registry_service import registry_service

router = APIRouter()


@router.get('/generators', response_model=list[GeneratorConfigRead])
def admin_list_generators(
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
) -> list[GeneratorConfigRead]:
    registry_service.ensure_registered_in_db(db)
    rows = db.execute(select(GeneratorConfig).order_by(GeneratorConfig.key)).scalars().all()
    return [GeneratorConfigRead.model_validate(row) for row in rows]


@router.patch('/generators/{key}', response_model=GeneratorConfigRead)
def update_generator(
    key: str,
    payload: GeneratorConfigUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
) -> GeneratorConfigRead:
    row = db.execute(select(GeneratorConfig).where(GeneratorConfig.key == key)).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail='Generator ikke funnet')

    update = payload.model_dump(exclude_none=True)
    for field, value in update.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return GeneratorConfigRead.model_validate(row)


@router.get('/generators/{key}/sample', response_model=GeneratorSampleResponse)
def generator_sample(
    key: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
) -> GeneratorSampleResponse:
    registry_service.ensure_registered_in_db(db)
    config = db.execute(select(GeneratorConfig).where(GeneratorConfig.key == key)).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail='Generator ikke funnet')

    generator = registry.get(key)
    problem = generator.generate(seed=random.randint(1, 10**9))

    return GeneratorSampleResponse(
        generator_key=key,
        prompt=problem.prompt,
        answer_type=problem.answer_type,
        metadata=problem.metadata,
        assets=problem.assets,
        solution_short=problem.solution_short,
        solution_steps=problem.solution_steps,
    )


@router.post('/generators/{key}/stress')
def stress_generator(
    key: str,
    count: int = Query(default=1000, ge=10, le=10000),
    _=Depends(get_current_admin),
) -> dict:
    if key not in registry.keys():
        raise HTTPException(status_code=404, detail='Generator ikke funnet i register')

    gen = registry.get(key)
    failures: list[str] = []

    for idx in range(count):
        try:
            problem = gen.generate(seed=random.randint(1, 10**9))
            eval_result = gen.evaluate(str(problem.correct_answer), problem)
            if not eval_result.is_correct:
                failures.append(f'#{idx}: korrekt svar ble ikke godkjent')
                if len(failures) >= 20:
                    break
        except Exception as exc:  # noqa: BLE001
            failures.append(f'#{idx}: {exc}')
            if len(failures) >= 20:
                break

    return {
        'generator_key': key,
        'count': count,
        'ok': len(failures) == 0,
        'failures': failures,
    }
