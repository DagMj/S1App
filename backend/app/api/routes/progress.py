from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.progress import ProgressOverview, ProgressPerGenerator, ProgressTimelinePoint
from app.services.progress_service import progress_service

router = APIRouter()


@router.get('/me/overview', response_model=ProgressOverview)
def overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressOverview:
    return ProgressOverview(**progress_service.overview(db, current_user.id))


@router.get('/me/per-generator', response_model=list[ProgressPerGenerator])
def per_generator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProgressPerGenerator]:
    return [ProgressPerGenerator(**row) for row in progress_service.per_generator(db, current_user.id)]


@router.get('/me/timeline', response_model=list[ProgressTimelinePoint])
def timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProgressTimelinePoint]:
    return [ProgressTimelinePoint(**row) for row in progress_service.timeline(db, current_user.id)]
