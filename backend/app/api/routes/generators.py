from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.generator import GeneratorConfig
from app.models.user import User
from app.schemas.generator import GeneratorConfigRead
from app.services.generator_registry_service import registry_service

router = APIRouter()


@router.get('', response_model=list[GeneratorConfigRead])
def list_generators(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[GeneratorConfigRead]:
    registry_service.ensure_registered_in_db(db)
    rows = db.execute(select(GeneratorConfig).order_by(GeneratorConfig.part, GeneratorConfig.key)).scalars().all()
    return [GeneratorConfigRead.model_validate(row) for row in rows]
