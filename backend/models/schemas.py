"""
Pydantic schemas — request validation and response serialization.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Any, Optional
from datetime import datetime


# ─────────────── AUTH ────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────── CHATBOT ─────────────────────────────────────────────
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    reply: str
    suggestions: list[dict] = []   # [{id, name, category}]
    is_algo_related: bool = False

class ChatHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────── ALGORITHMS ──────────────────────────────────────────
class SortRequest(BaseModel):
    algorithm: str
    array: list[int] = Field(..., min_length=1, max_length=500)

class SearchRequest(BaseModel):
    algorithm: str
    array: list[int]
    target: int

class GraphRequest(BaseModel):
    algorithm: str
    graph: Optional[dict[str, list]] = None
    edges: Optional[list[list]] = None
    num_vertices: Optional[int] = None
    start: Optional[str] = "0"

class DPRequest(BaseModel):
    algorithm: str
    n: Optional[int] = None
    weights: Optional[list[int]] = None
    values: Optional[list[int]] = None
    capacity: Optional[int] = None
    s1: Optional[str] = None
    s2: Optional[str] = None
    array: Optional[list[int]] = None

class TreeRequest(BaseModel):
    algorithm: str
    tree: list
    insert_val: Optional[int] = None
    p: Optional[int] = None
    q: Optional[int] = None

class StringRequest(BaseModel):
    algorithm: str
    text: str
    pattern: str

class WindowRequest(BaseModel):
    algorithm: str
    array: Optional[list] = None
    string: Optional[str] = None
    k: Optional[int] = None
    queries: Optional[list] = None