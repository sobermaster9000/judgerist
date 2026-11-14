from datetime import datetime, timezone

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# stores metadata about problem, actual statement and formats in JSON files
class ProblemBase(SQLModel):
    name: str = Field(max_length=64)
    time_limit: float = Field(ge=0.5, le=10)
    memory_limit: int = Field(ge=4, le=512)
    test_cases: int = Field(ge=1, le=256)

    created_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc),
                                        sa_column_kwargs={ 'onupdate': lambda: datetime.now(timezone.utc) })

class Problem(ProblemBase, table=True):
    __tablename__: str = 'problems'

    id: int | None = Field(default=None, primary_key=True)

class ProblemTags(SQLModel, table=True):
    __tablename__: str = 'problem_tags'

    problem_id: int = Field(index=True)
    tag: str = Field(max_length=32)

class ProblemExampleTests(SQLModel, table=True):
    __tablename__: str = 'problem_example_tests'

    problem_id: int = Field(index=True)
    test_no: int

class ProblemVisibleTests(SQLModel, table=True):
    __tablename__: str = 'problem_visible_tests'

    problem_id: str = Field(index=True)
    test_no: int

class ProblemPublic(ProblemBase):
    id: int
    tags: list[str]
    example_tests: list[int]
    visible_tests: list[int]

class ProblemResponse(BaseModel):
    detail: str
    data: ProblemPublic

class ProblemListResponse(BaseModel):
    detail: str
    data: list[ProblemPublic]
