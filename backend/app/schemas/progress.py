from pydantic import BaseModel


class ProgressOverview(BaseModel):
    solved_total: int
    correct_total: int
    accuracy: float
    del1_solved: int
    del2_solved: int


class ProgressPerGenerator(BaseModel):
    generator_key: str
    solved: int
    correct: int
    accuracy: float


class ProgressTimelinePoint(BaseModel):
    date: str
    solved: int
    correct: int
    accuracy: float
