from pydantic import BaseModel

class SubmissionDTO(BaseModel):
    code: str
    problem_id: int
    language: str
    submission_id: int
    is_pretest_run: bool