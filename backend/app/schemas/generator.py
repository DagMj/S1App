from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GeneratorConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    name: str
    description: str
    tema: str
    part: str
    answer_type: str
    difficulty: int
    weight: float
    is_enabled: bool
    updated_at: datetime


class GeneratorConfigUpdate(BaseModel):
    part: str | None = Field(default=None, pattern='^(del1|del2)$')
    weight: float | None = Field(default=None, ge=0.0, le=100.0)
    is_enabled: bool | None = None


class GeneratorSampleResponse(BaseModel):
    generator_key: str
    prompt: str
    answer_type: str
    metadata: dict
    assets: list[str]
    solution_short: str
    solution_steps: list[str]
