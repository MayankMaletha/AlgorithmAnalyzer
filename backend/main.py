"""
AlgoViz Backend v2
==================
Run:  uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from models.database import init_db
from routes.auth      import router as auth_router
from routes.chatbot   import router as chat_router
from routes.analytics import router as analytics_router
from routes.algorithms import router as algo_router
from routes.websocket  import router as ws_router
from routes.ai         import router as ai_router

app = FastAPI(
    title="AlgoViz API",
    description="JWT auth · AI chatbot · 30+ algorithms · real-time WebSocket streaming · analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(algo_router,  tags=["Algorithms"])
app.include_router(ws_router,    tags=["WebSocket"])
app.include_router(ai_router,    tags=["AI"])


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running", "version": "2.0.0", "docs": "/docs",
        "endpoints": {
            "auth":      ["/auth/register", "/auth/login", "/auth/me", "/auth/logout"],
            "chat":      ["/chat/message", "/chat/history"],
            "analytics": ["/analytics/dashboard", "/analytics/runs",
                          "/analytics/track", "/analytics/leaderboard"],
            "algorithms":["/algorithm/list", "/algorithm/run", "/search/run",
                          "/graph/run", "/dp/run", "/tree/run", "/string/run", "/window/run"],
            "ai":        ["/ai/explain", "/ai/step-explain", "/ai/code"],
            "websocket": "ws://localhost:8000/ws/algorithm",
        },
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "2.0.0"}