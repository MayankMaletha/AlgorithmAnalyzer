"""
Algorithm Visualizer - FastAPI Backend
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routes.algorithms import router as algo_router
from routes.ai import router as ai_router
from routes.websocket import router as ws_router

app = FastAPI(
    title="Algorithm Visualizer API",
    description="Step-by-step DSA visualization backend with AI explanations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow Next.js frontend (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(algo_router, tags=["Algorithms"])
app.include_router(ai_router, tags=["AI"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "docs": "/docs",
        "websocket": "ws://localhost:8000/ws/algorithm",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}