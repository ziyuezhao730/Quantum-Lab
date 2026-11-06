from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Literal

class PlanRequest(BaseModel):
    budget_minutes: int = Field(ge = 0, le = 180, strict = True)
    proficiency: dict[str, Annotated[float, Field(ge=0, le=1, allow_inf_nan=False, strict=True)]]
    requested_solver : Literal["exact", "qaoa"]

    @field_validator("proficiency")
    @classmethod
    def check_topic_keys(cls, value):
        expected = {"T1", "T2", "T3"}
        if set(value) != expected:
            raise ValueError("proficiency must contain exactly T1, T2, and T3")
        return value


class QuantumMetrics(BaseModel):
    qubits: int = Field(gt=0, strict=True)
    p: int = Field(gt=0, strict=True)
    shots: int = Field(gt=0, strict=True)
    seed: int = Field(ge=0, strict=True)
    feasible_shot_rate: float = Field(ge=0, le=1, allow_inf_nan=False, strict=True)
    raw_best_utility: float | None = Field(default=None, ge=0, allow_inf_nan=False, strict=True)

class PlanResult(BaseModel):
    allocations: dict[str, Literal[0, 30, 60]]
    used_minutes: int = Field(ge=0, strict=True)
    unused_minutes: int = Field(ge=0, strict=True)
    utility: float = Field(ge=0, allow_inf_nan=False, strict=True)
    feasible: bool = Field(strict=True)
    actual_solver: Literal["exact", "qaoa"]
    execution_mode: Literal["live", "cached_replay"]
    elapsed_ms: float = Field(ge=0, allow_inf_nan=False, strict=True)
    warnings: list[str] = Field(default_factory=list)
    quantum_metrics: QuantumMetrics | None = None
    
    @field_validator("allocations")
    @classmethod
    def check_allocation_keys(cls, value):
        if set(value) != {"T1", "T2", "T3"}:
            raise ValueError("allocations must contain exactly T1, T2, and T3")
        return value



    @field_validator("allocations")
    @classmethod
    def check_allocation_keys(cls, value):
        if set(value) != {"T1", "T2", "T3"}:
            raise ValueError("allocations must contain exactly T1, T2, and T3")
        return value

class Evidence(BaseModel):
    source_id: str = Field(min_length=1)
    page: int = Field(ge=1, strict=True)
    excerpt: str = Field(min_length=1)


class Source(BaseModel):
    source_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    provenance: str = Field(min_length=1)
    label: str | None = None
    filename: str | None = None


class Topic(BaseModel):
    topic_id: Literal["T1", "T2", "T3"]
    name: str = Field(min_length=1)
    importance: float = Field(
        ge=0,
        le=1,
        allow_inf_nan=False,
        strict=True,
    )
    evidence: list[Evidence]


class Question(BaseModel):
    question_id: str = Field(min_length=1)
    topic_id: Literal["T1", "T2", "T3"]
    text: str = Field(min_length=1)
    difficulty: Literal[1, 2, 3]
    purpose: Literal["diagnostic", "practice"]
    source_id: str = Field(min_length=1)
    page: int = Field(ge=1, strict=True)
    review_status: Literal["pending", "approved"]
    answer: str | None = None
    choices: dict[str, str] | None = None
    correct_choice: str | None = None


class CourseData(BaseModel):
    schema_version: Literal[1]
    topics: list[Topic]
    questions: list[Question]
    sources: list[Source]
    assessment_count: int = Field(ge=0, strict=True)
    topic_counts: dict[
        str,
        Annotated[int, Field(ge=0, strict=True)],
    ]

class DiagnosticResult(BaseModel):
    submitted_choices: dict[str, str]
    proficiency: dict[
        str,
        Annotated[
            float,
            Field(ge=0, le=1, allow_inf_nan=False, strict=True),
        ],
    ]

    @field_validator("proficiency")
    @classmethod
    def check_proficiency_keys(cls, value):
        if set(value) != {"T1", "T2", "T3"}:
            raise ValueError(
                "proficiency must contain exactly T1, T2, and T3"
            )

        return value

class ProfileSnapshot(BaseModel):
    schema_version: Literal[1]
    profile_source: Literal["diagnostic"]
    request: PlanRequest
    topic_weights: dict[
        str,
        Annotated[
            float,
            Field(ge=0.5, le=1, allow_inf_nan=False, strict=True),
        ],
    ]

    @field_validator("topic_weights")
    @classmethod
    def check_topic_weight_keys(cls, value):
        if set(value) != {"T1", "T2", "T3"}:
            raise ValueError(
                "topic_weights must contain exactly T1, T2, and T3"
            )

        return value
