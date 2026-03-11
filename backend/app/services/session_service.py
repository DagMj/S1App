from __future__ import annotations

from dataclasses import dataclass
import random

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.generators.core.registry import registry
from app.generators.core.types import ProblemData
from app.models.generator import GeneratorConfig
from app.models.session import PracticeSession, SessionItem, Submission
from app.models.task import ProblemInstance
from app.services.generator_registry_service import registry_service
from app.services.progress_service import progress_service
from app.utils.weighted import weighted_choice, weighted_sample_without_replacement


@dataclass
class GeneratedItem:
    session_item: SessionItem
    problem: ProblemInstance


class SessionService:
    def start_exam(self, db: Session, user_id: str) -> tuple[PracticeSession, list[GeneratedItem]]:
        registry_service.ensure_registered_in_db(db)

        del1_enabled = registry_service.enabled_for_part(db, "del1")
        del2_enabled = registry_service.enabled_for_part(db, "del2")

        del1_keys_pool, del1_weights = self._build_exam_pool(
            del1_enabled,
            required_count=6,
            min_difficulty=2,
        )
        del2_keys_pool, del2_weights = self._build_exam_pool(
            del2_enabled,
            required_count=4,
            min_difficulty=2,
        )

        if len(del1_keys_pool) < 6 or len(del2_keys_pool) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For faa aktive generatorer for eksamensmodus (minst 6 del1 og 4 del2).",
            )

        seed = random.randint(1, 10**9)
        del1_keys = weighted_sample_without_replacement(del1_keys_pool, del1_weights, 6, seed=seed)
        del2_keys = weighted_sample_without_replacement(del2_keys_pool, del2_weights, 4, seed=seed + 1)

        session = PracticeSession(
            mode="exam",
            status="active",
            config_json={"del1_keys": del1_keys, "del2_keys": del2_keys, "seed": seed},
        )
        db.add(session)
        db.flush()

        items: list[GeneratedItem] = []
        ordered = [("del1", key) for key in del1_keys] + [("del2", key) for key in del2_keys]

        for idx, (part, key) in enumerate(ordered, start=1):
            generated = self._generate_problem(key=key, forced_part=part)
            problem = self._persist_problem(db, generated)
            session_item = SessionItem(
                session_id=session.id,
                problem_id=problem.id,
                order_index=idx,
                generator_key=key,
                part=part,
                max_points=generated.max_points,
                is_answered=False,
            )
            db.add(session_item)
            db.flush()
            problem.session_item_id = session_item.id
            items.append(GeneratedItem(session_item=session_item, problem=problem))

        db.commit()
        return session, items

    def start_training(
        self, db: Session, user_id: str, mode: str, generator_keys: list[str]
    ) -> PracticeSession:
        registry_service.ensure_registered_in_db(db)

        if mode not in {"training_single", "training_multi"}:
            raise HTTPException(status_code=400, detail="Ugyldig treningsmodus")

        if mode == "training_single" and len(generator_keys) != 1:
            raise HTTPException(status_code=400, detail="training_single krever noeyaktig 1 generator")

        if not generator_keys:
            raise HTTPException(status_code=400, detail="Velg minst en generator")

        cfg_map = registry_service.get_config_map(db, generator_keys)
        for key in generator_keys:
            cfg = cfg_map.get(key)
            if cfg is None:
                raise HTTPException(status_code=404, detail=f"Generator ikke funnet: {key}")
            if not cfg.is_enabled:
                raise HTTPException(status_code=400, detail=f"Generator er deaktivert: {key}")

        session = PracticeSession(
            mode=mode,
            status="active",
            config_json={"generator_keys": generator_keys},
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def next_training_problem(self, db: Session, session_id: str, user_id: str) -> GeneratedItem:
        session = db.get(PracticeSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Oekt ikke funnet")
        if session.mode not in {"training_single", "training_multi"}:
            raise HTTPException(status_code=400, detail="Neste oppgave er kun tilgjengelig i treningsmodus")

        keys = list(session.config_json.get("generator_keys", []))
        if not keys:
            raise HTTPException(status_code=400, detail="Ingen generatorer i oekten")

        cfg_map = registry_service.get_config_map(db, keys)
        weights = {k: cfg_map[k].weight for k in keys if k in cfg_map}

        if session.mode == "training_single":
            key = keys[0]
        else:
            key = weighted_choice(keys, weights)

        generated = self._generate_problem(key=key)
        problem = self._persist_problem(db, generated)

        order_index = (
            db.execute(
                select(func.coalesce(func.max(SessionItem.order_index), 0)).where(
                    SessionItem.session_id == session.id
                )
            ).scalar_one()
            + 1
        )

        item = SessionItem(
            session_id=session.id,
            problem_id=problem.id,
            order_index=order_index,
            generator_key=generated.generator_key,
            part=generated.part,
            max_points=generated.max_points,
            is_answered=False,
        )
        db.add(item)
        db.flush()
        problem.session_item_id = item.id
        db.commit()
        db.refresh(problem)
        return GeneratedItem(session_item=item, problem=problem)

    def submit_answer(
        self,
        db: Session,
        *,
        user_id: str,
        session_id: str,
        session_item_id: str,
        answer: str,
    ) -> tuple[Submission, ProblemData]:
        session = db.get(PracticeSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Oekt ikke funnet")

        item = db.get(SessionItem, session_item_id)
        if not item or item.session_id != session.id:
            raise HTTPException(status_code=404, detail="Oppgave i oekten finnes ikke")

        if item.is_answered:
            if session.mode == "exam":
                raise HTTPException(status_code=400, detail="Oppgaven er allerede besvart i eksamensmodus")
            raise HTTPException(status_code=400, detail="Oppgaven er allerede besvart")

        problem = db.get(ProblemInstance, item.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem ikke funnet")

        problem_data = ProblemData(
            generator_key=problem.generator_key,
            part=problem.part,
            prompt=problem.prompt,
            answer_type=problem.answer_type,
            correct_answer=problem.correct_answer,
            solution_short=problem.solution_short,
            solution_steps=list(problem.solution_steps or []),
            metadata=dict(problem.metadata_json or {}),
            assets=list(problem.assets or []),
            max_points=float(problem.max_points),
            seed=int(problem.seed),
        )

        generator = registry.get(problem.generator_key)
        eval_result = generator.evaluate(answer, problem_data)

        submission = Submission(
            session_id=session.id,
            session_item_id=item.id,
            problem_id=problem.id,
            raw_answer=answer,
            normalized_answer=eval_result.normalized_answer,
            is_correct=eval_result.is_correct,
            score=eval_result.score,
            max_points=eval_result.max_points,
            confidence=eval_result.confidence,
            uncertain=eval_result.uncertain,
            feedback=eval_result.feedback,
            evaluation_json=eval_result.details,
        )
        db.add(submission)

        item.is_answered = True

        progress_service.register_submission(
            db,
            user_id=user_id,
            generator_key=problem.generator_key,
            part=problem.part,
            score=eval_result.score,
            is_correct=eval_result.is_correct,
        )

        db.commit()
        db.refresh(submission)

        return submission, problem_data

    def session_summary(self, db: Session, session_id: str, user_id: str) -> dict:
        session = db.get(PracticeSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Oekt ikke funnet")

        solved = int(
            db.execute(select(func.count(Submission.id)).where(Submission.session_id == session_id)).scalar_one()
        )
        correct = int(
            db.execute(
                select(func.count(Submission.id)).where(
                    Submission.session_id == session_id,
                    Submission.is_correct.is_(True),
                )
            ).scalar_one()
        )
        score = float(
            db.execute(
                select(func.coalesce(func.sum(Submission.score), 0.0)).where(
                    Submission.session_id == session_id
                )
            ).scalar_one()
        )

        return {
            "session_id": session.id,
            "mode": session.mode,
            "status": session.status,
            "started_at": session.started_at,
            "solved": solved,
            "correct": correct,
            "score": score,
        }

    def _difficulty_for_key(self, key: str, fallback: int = 1) -> int:
        try:
            return registry.get(key).metadata().difficulty
        except KeyError:
            return fallback

    def _build_exam_pool(
        self,
        configs: list[GeneratorConfig],
        *,
        required_count: int,
        min_difficulty: int,
    ) -> tuple[list[str], dict[str, float]]:
        if not configs:
            return [], {}

        difficult = [
            cfg
            for cfg in configs
            if self._difficulty_for_key(cfg.key, cfg.difficulty) >= min_difficulty
        ]
        selected = difficult if len(difficult) >= required_count else configs

        keys = [cfg.key for cfg in selected]
        weights: dict[str, float] = {}

        for cfg in selected:
            difficulty = self._difficulty_for_key(cfg.key, cfg.difficulty)
            bonus = 1.0 + max(0, difficulty - min_difficulty) * 0.35
            weights[cfg.key] = max(cfg.weight, 0.01) * bonus

        return keys, weights

    def _generate_problem(self, key: str, forced_part: str | None = None) -> ProblemData:
        generator = registry.get(key)
        generated = generator.generate(seed=random.randint(1, 10**9))
        if forced_part is not None:
            generated.part = forced_part
        return generated

    def _persist_problem(self, db: Session, generated: ProblemData) -> ProblemInstance:
        row = ProblemInstance(
            generator_key=generated.generator_key,
            part=generated.part,
            prompt=generated.prompt,
            answer_type=generated.answer_type,
            correct_answer=generated.correct_answer,
            solution_short=generated.solution_short,
            solution_steps=generated.solution_steps,
            metadata_json=generated.metadata,
            assets=generated.assets,
            max_points=int(generated.max_points),
            seed=int(generated.seed),
        )
        db.add(row)
        db.flush()
        return row


session_service = SessionService()
