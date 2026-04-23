"""
Chatbot Routes
POST /chat/message     — send a message, get AI response + algorithm suggestions
GET  /chat/history     — retrieve conversation history for current user
DELETE /chat/history   — clear conversation history
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import User, ChatHistory, get_db
from models.schemas import ChatMessage, ChatResponse, ChatHistoryItem
from services.auth_service import get_current_user, get_current_user_optional
from services.chatbot_service import process_chat

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    req: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    # Load conversation history for context (last 20 messages)
    history = []
    if current_user:
        rows = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == current_user.id)
            .order_by(ChatHistory.created_at.asc())
            .limit(20)
            .all()
        )
        history = [{"role": r.role, "content": r.content} for r in rows]

    # Get AI response
    result = await process_chat(req.message, history)

    # Persist to DB if authenticated
    if current_user:
        db.add(ChatHistory(user_id=current_user.id, role="user",      content=req.message))
        db.add(ChatHistory(user_id=current_user.id, role="assistant", content=result["reply"]))
        db.commit()

    return ChatResponse(**result)


@router.get("/history", response_model=list[ChatHistoryItem])
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.asc())
        .limit(limit)
        .all()
    )
    return rows


@router.delete("/history")
def clear_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared"}