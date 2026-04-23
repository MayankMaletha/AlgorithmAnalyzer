"""
Analytics Routes
GET /analytics/dashboard   — summary stats for current user
GET /analytics/runs        — paginated algorithm run history
POST /analytics/track      — record an algorithm run (called by frontend)
GET /analytics/leaderboard — most popular algorithms across all users (public)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional

from models.database import User, AlgorithmRun, ChatHistory, get_db
from services.auth_service import get_current_user, get_current_user_optional
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class TrackRunRequest(BaseModel):
    algorithm: str
    category: str
    input_snapshot: Optional[str] = None


@router.post("/track")
def track_run(
    req: TrackRunRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Record that a user ran an algorithm. Called by frontend on each Run click."""
    if not current_user:
        return {"tracked": False}
    run = AlgorithmRun(
        user_id=current_user.id,
        algorithm=req.algorithm,
        category=req.category,
        input_snapshot=req.input_snapshot,
    )
    db.add(run)
    db.commit()
    return {"tracked": True}


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return summary stats for the authenticated user's dashboard."""
    user_id = current_user.id

    # Total runs
    total_runs = db.query(func.count(AlgorithmRun.id))\
        .filter(AlgorithmRun.user_id == user_id).scalar() or 0

    # Runs last 7 days
    since = datetime.utcnow() - timedelta(days=7)
    recent_runs = db.query(func.count(AlgorithmRun.id))\
        .filter(AlgorithmRun.user_id == user_id, AlgorithmRun.created_at >= since).scalar() or 0

    # Favourite algorithm (most run)
    fav_row = db.query(AlgorithmRun.algorithm, func.count(AlgorithmRun.id).label("cnt"))\
        .filter(AlgorithmRun.user_id == user_id)\
        .group_by(AlgorithmRun.algorithm)\
        .order_by(desc("cnt"))\
        .first()
    favourite = fav_row[0] if fav_row else None

    # Category breakdown
    cat_rows = db.query(AlgorithmRun.category, func.count(AlgorithmRun.id).label("cnt"))\
        .filter(AlgorithmRun.user_id == user_id)\
        .group_by(AlgorithmRun.category)\
        .order_by(desc("cnt"))\
        .all()
    categories = [{"category": r[0], "count": r[1]} for r in cat_rows]

    # Top 5 algorithms
    top_rows = db.query(AlgorithmRun.algorithm, func.count(AlgorithmRun.id).label("cnt"))\
        .filter(AlgorithmRun.user_id == user_id)\
        .group_by(AlgorithmRun.algorithm)\
        .order_by(desc("cnt"))\
        .limit(5).all()
    top_algos = [{"algorithm": r[0], "count": r[1]} for r in top_rows]

    # Total chat messages
    chat_count = db.query(func.count(ChatHistory.id))\
        .filter(ChatHistory.user_id == user_id, ChatHistory.role == "user").scalar() or 0

    # Daily run counts last 7 days for sparkline
    daily = []
    for i in range(6, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end   = day_start + timedelta(days=1)
        cnt = db.query(func.count(AlgorithmRun.id))\
            .filter(AlgorithmRun.user_id == user_id,
                    AlgorithmRun.created_at >= day_start,
                    AlgorithmRun.created_at < day_end).scalar() or 0
        daily.append({"date": day_start.strftime("%a"), "count": cnt})

    return {
        "total_runs":   total_runs,
        "recent_runs":  recent_runs,
        "favourite":    favourite,
        "chat_messages": chat_count,
        "categories":   categories,
        "top_algos":    top_algos,
        "daily_runs":   daily,
        "member_since": current_user.created_at.strftime("%B %Y"),
    }


@router.get("/runs")
def run_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Paginated list of the user's algorithm runs."""
    q = db.query(AlgorithmRun).filter(AlgorithmRun.user_id == current_user.id)
    if category:
        q = q.filter(AlgorithmRun.category == category)
    total = q.count()
    runs  = q.order_by(desc(AlgorithmRun.created_at)).offset((page-1)*limit).limit(limit).all()
    return {
        "total": total, "page": page, "limit": limit,
        "runs": [
            {"id": r.id, "algorithm": r.algorithm, "category": r.category,
             "created_at": r.created_at.isoformat()}
            for r in runs
        ],
    }


@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    """Most popular algorithms across ALL users — public endpoint."""
    rows = db.query(
        AlgorithmRun.algorithm,
        AlgorithmRun.category,
        func.count(AlgorithmRun.id).label("total_runs"),
    ).group_by(AlgorithmRun.algorithm, AlgorithmRun.category)\
     .order_by(desc("total_runs"))\
     .limit(10).all()
    return [{"algorithm": r[0], "category": r[1], "total_runs": r[2]} for r in rows]