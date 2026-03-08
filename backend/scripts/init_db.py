from app.db.base import Base
from app.db.session import engine
from app.generators.library import register_all_generators
from app.services.generator_registry_service import registry_service
from app.db.session import SessionLocal


def main() -> None:
    register_all_generators()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        registry_service.ensure_registered_in_db(db)
    finally:
        db.close()
    print('Database initialized.')


if __name__ == '__main__':
    main()
