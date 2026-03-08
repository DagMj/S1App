from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.generators.core.registry import registry
from app.models.generator import GeneratorConfig


class GeneratorRegistryService:
    def ensure_registered_in_db(self, db: Session) -> None:
        for generator in registry.all():
            meta = generator.metadata()
            existing = db.execute(
                select(GeneratorConfig).where(GeneratorConfig.key == meta.key)
            ).scalar_one_or_none()

            if existing is None:
                db.add(
                    GeneratorConfig(
                        key=meta.key,
                        name=meta.name,
                        description=meta.description,
                        tema=meta.tema,
                        part=meta.part,
                        answer_type=meta.answer_type,
                        difficulty=meta.difficulty,
                        weight=meta.default_weight,
                        is_enabled=True,
                    )
                )
                continue

            # Keep admin-controlled fields (`part`, `weight`, `is_enabled`) untouched,
            # but sync display/metadata fields from generator code.
            existing.name = meta.name
            existing.description = meta.description
            existing.tema = meta.tema
            existing.answer_type = meta.answer_type
            existing.difficulty = meta.difficulty

        db.commit()

    def enabled_for_part(self, db: Session, part: str) -> list[GeneratorConfig]:
        return list(
            db.execute(
                select(GeneratorConfig).where(
                    GeneratorConfig.is_enabled.is_(True),
                    GeneratorConfig.part == part,
                )
            ).scalars()
        )

    def get_config_map(self, db: Session, keys: list[str]) -> dict[str, GeneratorConfig]:
        rows = db.execute(select(GeneratorConfig).where(GeneratorConfig.key.in_(keys))).scalars().all()
        return {r.key: r for r in rows}


registry_service = GeneratorRegistryService()
