from __future__ import annotations

from datetime import date
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.progress import ProgressDaily
from app.models.session import Submission


class ProgressService:
    def register_submission(
        self,
        db: Session,
        *,
        user_id: str,
        generator_key: str,
        part: str,
        score: float,
        is_correct: bool,
    ) -> None:
        today = date.today()
        row = db.execute(
            select(ProgressDaily).where(
                and_(
                    ProgressDaily.user_id == user_id,
                    ProgressDaily.date == today,
                    ProgressDaily.generator_key == generator_key,
                    ProgressDaily.part == part,
                )
            )
        ).scalar_one_or_none()

        if row is None:
            row = ProgressDaily(
                user_id=user_id,
                date=today,
                generator_key=generator_key,
                part=part,
                solved_count=0,
                correct_count=0,
                score_sum=0.0,
            )
            db.add(row)

        row.solved_count += 1
        row.correct_count += 1 if is_correct else 0
        row.score_sum += score

    def overview(self, db: Session, user_id: str) -> dict:
        solved = db.execute(
            select(func.count(Submission.id)).where(Submission.user_id == user_id)
        ).scalar_one()
        correct = db.execute(
            select(func.count(Submission.id)).where(
                and_(Submission.user_id == user_id, Submission.is_correct.is_(True))
            )
        ).scalar_one()

        del1 = db.execute(
            select(func.coalesce(func.sum(ProgressDaily.solved_count), 0)).where(
                and_(ProgressDaily.user_id == user_id, ProgressDaily.part == 'del1')
            )
        ).scalar_one()
        del2 = db.execute(
            select(func.coalesce(func.sum(ProgressDaily.solved_count), 0)).where(
                and_(ProgressDaily.user_id == user_id, ProgressDaily.part == 'del2')
            )
        ).scalar_one()

        acc = (correct / solved) if solved else 0.0
        return {
            'solved_total': int(solved),
            'correct_total': int(correct),
            'accuracy': float(round(acc, 4)),
            'del1_solved': int(del1),
            'del2_solved': int(del2),
        }

    def per_generator(self, db: Session, user_id: str) -> list[dict]:
        rows = db.execute(
            select(
                ProgressDaily.generator_key,
                func.sum(ProgressDaily.solved_count),
                func.sum(ProgressDaily.correct_count),
            )
            .where(ProgressDaily.user_id == user_id)
            .group_by(ProgressDaily.generator_key)
            .order_by(ProgressDaily.generator_key)
        ).all()

        out = []
        for generator_key, solved, correct in rows:
            solved_i = int(solved or 0)
            correct_i = int(correct or 0)
            out.append(
                {
                    'generator_key': generator_key,
                    'solved': solved_i,
                    'correct': correct_i,
                    'accuracy': round((correct_i / solved_i), 4) if solved_i else 0.0,
                }
            )
        return out

    def timeline(self, db: Session, user_id: str) -> list[dict]:
        rows = db.execute(
            select(
                ProgressDaily.date,
                func.sum(ProgressDaily.solved_count),
                func.sum(ProgressDaily.correct_count),
            )
            .where(ProgressDaily.user_id == user_id)
            .group_by(ProgressDaily.date)
            .order_by(ProgressDaily.date)
        ).all()

        out = []
        for day, solved, correct in rows:
            solved_i = int(solved or 0)
            correct_i = int(correct or 0)
            out.append(
                {
                    'date': str(day),
                    'solved': solved_i,
                    'correct': correct_i,
                    'accuracy': round((correct_i / solved_i), 4) if solved_i else 0.0,
                }
            )
        return out


progress_service = ProgressService()
