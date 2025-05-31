from pydantic import BaseModel
from typing import Optional


class Analysis(BaseModel):
    id: str
    job_id: str
    score: float
    name: str
    status: str
    skills: Optional[list] = []
    education: Optional[list] = []
    languages: Optional[list] = []
    salary_expectation: Optional[str] = None