# models/study_models.py
from pydantic import BaseModel

class Task(BaseModel):
    name: str
    type: str  # exam, project, assignment, reading, quiz
    deadline: str | None  # Format: YYYY-MM-DD
    estimatedHours: float | None
    priority: str  # critical, high, medium, low
    quadrant: str  # q1, q2, q3, q4
    description: str | None

class SyllabusAnalysisResponse(BaseModel):
    tasks: list[Task]
