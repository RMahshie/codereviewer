from pydantic import BaseModel


class Issue(BaseModel):
    category: str
    file: str
    line: int
    issue: str
    impact: str
    recommendation: str

class ReviewOutput(BaseModel):
    issues: list[Issue]

class SummaryOutput(BaseModel):
    summary: str
    number_of_changes: int