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
    has_critical_issues: bool

class SummaryOutput(BaseModel):
    summary: str
    has_critical_issues: bool
    number_of_changes: int