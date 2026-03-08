from datetime import datetime

from pydantic import BaseModel, Field


class ProblemRead(BaseModel):
    session_id: str
    session_item_id: str
    order_index: int
    generator_key: str
    generator_name: str | None = None
    part: str
    prompt: str
    answer_type: str
    metadata: dict
    assets: list[str]
    max_points: float
    hint: str | None = None


class StartExamResponse(BaseModel):
    session_id: str
    mode: str
    items: list[ProblemRead]


class StartTrainingRequest(BaseModel):
    mode: str = Field(pattern='^(training_single|training_multi)$')
    generator_keys: list[str]


class StartTrainingResponse(BaseModel):
    session_id: str
    mode: str


class SubmitAnswerRequest(BaseModel):
    session_item_id: str
    answer: str


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    score: float
    max_points: float
    confidence: float
    uncertain: bool
    feedback: str
    normalized_answer: str
    details: dict
    solution_short: str
    solution_steps: list[str]


class SessionSummary(BaseModel):
    session_id: str
    mode: str
    status: str
    started_at: datetime
    solved: int
    correct: int
    score: float
