from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class AssignmentConfig:
    assignment_id: str
    number_of_days: int
    number_of_notes: int
    summary_line_count: int
    source: List[str]
    flag: bool
    no_limit: bool
