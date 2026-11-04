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
