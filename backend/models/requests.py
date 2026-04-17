"""
Pydantic models for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional


# ─────────────────────── SORTING / SEARCHING ────────────────────────

class SortRequest(BaseModel):
    algorithm: str = Field(..., examples=["bubble_sort", "merge_sort", "quick_sort"])
    array: list[int] = Field(..., min_length=1, max_length=500)

    model_config = {"json_schema_extra": {
        "example": {"algorithm": "bubble_sort", "array": [64, 34, 25, 12, 22, 11, 90]}
    }}


class SearchRequest(BaseModel):
    algorithm: str = Field(..., examples=["linear_search", "binary_search"])
    array: list[int]
    target: int

    model_config = {"json_schema_extra": {
        "example": {"algorithm": "binary_search", "array": [1,3,5,7,9,11], "target": 7}
    }}


# ─────────────────────────── GRAPH ──────────────────────────────────

class GraphRequest(BaseModel):
    algorithm: str = Field(..., examples=["bfs", "dfs", "dijkstra", "prim"])
    graph: Optional[dict[str, list]] = None       # adjacency list
    edges: Optional[list[list]] = None            # edge list for kruskal / bellman_ford
    num_vertices: Optional[int] = None
    start: Optional[str] = "0"

    model_config = {"json_schema_extra": {
        "example": {
            "algorithm": "dijkstra",
            "graph": {"0": [["1", 4], ["2", 1]], "1": [["3", 1]], "2": [["1", 2], ["3", 5]], "3": []},
            "start": "0"
        }
    }}


# ─────────────────────────── DP ─────────────────────────────────────

class DPRequest(BaseModel):
    algorithm: str = Field(..., examples=["fibonacci", "knapsack_01", "lcs", "lis"])
    # fibonacci
    n: Optional[int] = None
    # knapsack
    weights: Optional[list[int]] = None
    values: Optional[list[int]] = None
    capacity: Optional[int] = None
    # lcs
    s1: Optional[str] = None
    s2: Optional[str] = None
    # lis
    array: Optional[list[int]] = None


# ─────────────────────────── AI ─────────────────────────────────────

class AIExplainRequest(BaseModel):
    algorithm: str
    language: str = "en"

class AIStepExplainRequest(BaseModel):
    algorithm: str
    step: dict[str, Any]
    step_index: int
    total_steps: int

class AICodeRequest(BaseModel):
    algorithm: str
    language: str = Field(..., examples=["python", "javascript", "java", "c++", "go"])


# ─────────────────────────── COMMON RESPONSE ────────────────────────

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None