from pydantic import BaseModel

class ProblemConstraint(BaseModel):
    language_name: str
    language_id: int
    memory_limit: int
    time_limit: int

class ProblemTestCase(BaseModel):
    input: str
    output: str
    points: int
    is_pretest: bool
    number: int

class ProblemConfig(BaseModel):
    id: int
    config_version_number: int
    constraints: list[ProblemConstraint]
    test_cases: list[ProblemTestCase]