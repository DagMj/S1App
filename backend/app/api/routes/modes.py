from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.generators.core.registry import registry
from app.schemas.session import (
    ProblemRead,
    SessionSummary,
    StartExamResponse,
    StartTrainingRequest,
    StartTrainingResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.session_service import GeneratedItem, session_service

router = APIRouter()

ANONYMOUS_USER_ID = 'anonymous'


def _to_problem_read(session_id: str, item: GeneratedItem) -> ProblemRead:
    try:
        generator_name = registry.get(item.problem.generator_key).metadata().name
    except KeyError:
        generator_name = item.problem.generator_key

    steps = list(item.problem.solution_steps or [])
    hint = steps[0] if steps else None

    return ProblemRead(
        session_id=session_id,
        session_item_id=item.session_item.id,
        order_index=item.session_item.order_index,
        generator_key=item.problem.generator_key,
        generator_name=generator_name,
        part=item.problem.part,
        prompt=item.problem.prompt,
        answer_type=item.problem.answer_type,
        metadata=item.problem.metadata_json or {},
        assets=item.problem.assets or [],
        max_points=float(item.session_item.max_points),
        hint=hint,
    )


@router.post('/exam/start', response_model=StartExamResponse)
def start_exam(
    db: Session = Depends(get_db),
) -> StartExamResponse:
    session, items = session_service.start_exam(db, ANONYMOUS_USER_ID)
    payload_items = [_to_problem_read(session.id, item) for item in items]
    return StartExamResponse(session_id=session.id, mode=session.mode, items=payload_items)


@router.post('/training/start', response_model=StartTrainingResponse)
def start_training(
    payload: StartTrainingRequest,
    db: Session = Depends(get_db),
) -> StartTrainingResponse:
    session = session_service.start_training(db, ANONYMOUS_USER_ID, payload.mode, payload.generator_keys)
    return StartTrainingResponse(session_id=session.id, mode=session.mode)


@router.post('/training/{session_id}/next', response_model=ProblemRead)
def next_training_problem(
    session_id: str,
    db: Session = Depends(get_db),
) -> ProblemRead:
    item = session_service.next_training_problem(db, session_id, ANONYMOUS_USER_ID)
    return _to_problem_read(session_id, item)


@router.post('/sessions/{session_id}/submit', response_model=SubmitAnswerResponse)
def submit_answer(
    session_id: str,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
) -> SubmitAnswerResponse:
    submission, problem_data = session_service.submit_answer(
        db,
        user_id=ANONYMOUS_USER_ID,
        session_id=session_id,
        session_item_id=payload.session_item_id,
        answer=payload.answer,
    )

    return SubmitAnswerResponse(
        is_correct=submission.is_correct,
        score=float(submission.score),
        max_points=float(submission.max_points),
        confidence=float(submission.confidence),
        uncertain=submission.uncertain,
        feedback=submission.feedback,
        normalized_answer=submission.normalized_answer,
        details=submission.evaluation_json or {},
        solution_short=problem_data.solution_short,
        solution_steps=problem_data.solution_steps,
    )


@router.get('/sessions/{session_id}/summary', response_model=SessionSummary)
def session_summary(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionSummary:
    try:
        summary = session_service.session_summary(db, session_id, ANONYMOUS_USER_ID)
    except HTTPException:
        raise
    return SessionSummary(**summary)
