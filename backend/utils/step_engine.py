"""
Step Engine - Universal step format for all algorithms.
Every algorithm returns a list of Step objects so the frontend
can reuse the same animation logic regardless of algorithm type.
"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class StepType(str, Enum):
    COMPARE = "compare"
    SWAP = "swap"
    VISIT = "visit"
    UPDATE = "update"
    SELECT = "select"
    INSERT = "insert"
    DELETE = "delete"
    FOUND = "found"
    NOT_FOUND = "not_found"
    HIGHLIGHT = "highlight"
    COMPLETE = "complete"


class Step(BaseModel):
    """Universal step format for all algorithms."""
    type: StepType
    description: str                      # Human-readable explanation of this step
    indices: list[int] = []               # Active indices (for arrays)
    array: list[Any] = []                 # Current array/list state
    extra: dict[str, Any] = {}            # Algorithm-specific data (dp table, graph state, etc.)

    @classmethod
    def compare(cls, i: int, j: int, array: list, desc: str = "", **extra):
        return cls(type=StepType.COMPARE, indices=[i, j], array=list(array),
                   description=desc or f"Comparing indices {i} and {j}", extra=extra)

    @classmethod
    def swap(cls, i: int, j: int, array: list, desc: str = "", **extra):
        return cls(type=StepType.SWAP, indices=[i, j], array=list(array),
                   description=desc or f"Swapping indices {i} and {j}", extra=extra)

    @classmethod
    def visit(cls, i: int, array: list, desc: str = "", **extra):
        return cls(type=StepType.VISIT, indices=[i], array=list(array),
                   description=desc or f"Visiting index {i}", extra=extra)

    @classmethod
    def update(cls, indices: list[int], array: list, desc: str = "", **extra):
        return cls(type=StepType.UPDATE, indices=indices, array=list(array),
                   description=desc or f"Updating indices {indices}", extra=extra)

    @classmethod
    def found(cls, i: int, array: list, desc: str = "", **extra):
        return cls(type=StepType.FOUND, indices=[i], array=list(array),
                   description=desc or f"Found at index {i}", extra=extra)

    @classmethod
    def not_found(cls, array: list, desc: str = "", **extra):
        return cls(type=StepType.NOT_FOUND, indices=[], array=list(array),
                   description=desc or "Element not found", extra=extra)

    @classmethod
    def complete(cls, array: list, desc: str = "Algorithm complete", **extra):
        return cls(type=StepType.COMPLETE, indices=[], array=list(array),
                   description=desc, extra=extra)


class AlgorithmResult(BaseModel):
    """Wrapper returned by every algorithm endpoint."""
    algorithm: str
    steps: list[Step]
    total_steps: int
    complexity: dict[str, str]   # {"time": "O(n²)", "space": "O(1)"}
    input_data: dict[str, Any]