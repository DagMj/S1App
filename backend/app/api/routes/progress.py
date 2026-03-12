from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.modes import ANONYMOUS_USER_ID
from app.db.session import get_db
from app.schemas.progress import ProgressOverview, ProgressPerGenerator, ProgressTimelinePoint
from app.services.progress_service import progress_service

router = APIRouter()


@router.get('/overview', response_model=ProgressOverview)
def get_overview(db: Session = Depends(get_db)) -> ProgressOverview:
    data = progress_service.overview(db, ANONYMOUS_USER_ID)
    return ProgressOverview(**data)


@router.get('/generators', response_model=list[ProgressPerGenerator])
def get_per_generator(db: Session = Depends(get_db)) -> list[ProgressPerGenerator]:
    rows = progress_service.per_generator(db, ANONYMOUS_USER_ID)
    return [ProgressPerGenerator(**row) for row in rows]


@router.get('/timeline', response_model=list[ProgressTimelinePoint])
def get_timeline(db: Session = Depends(get_db)) -> list[ProgressTimelinePoint]:
    rows = progress_service.timeline(db, ANONYMOUS_USER_ID)
    return [ProgressTimelinePoint(**row) for row in rows]
