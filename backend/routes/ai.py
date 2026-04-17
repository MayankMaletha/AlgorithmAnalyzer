"""
AI Routes - Gemini-powered explanation and code generation endpoints.
"""

from fastapi import APIRouter, HTTPException
from models.requests import AIExplainRequest, AIStepExplainRequest, AICodeRequest
from services.gemini_service import get_gemini_service

router = APIRouter(prefix="/ai")

SUPPORTED_LANGUAGES = ["python", "javascript", "java", "c++", "go", "rust", "typescript"]


@router.post("/explain")
async def explain_algorithm(req: AIExplainRequest):
    """Get a full AI explanation of an algorithm including complexity, use cases, pros/cons."""
    try:
        service = get_gemini_service()
        result = await service.explain_algorithm(req.algorithm, req.language)
        return {"algorithm": req.algorithm, "explanation": result}
    except ValueError as e:
        raise HTTPException(503, f"AI service unavailable: {e}")
    except Exception as e:
        raise HTTPException(500, f"AI explanation failed: {e}")


@router.post("/step-explain")
async def explain_step(req: AIStepExplainRequest):
    """Get AI explanation for a specific step in the algorithm execution."""
    try:
        service = get_gemini_service()
        result = await service.explain_step(
            req.algorithm, req.step, req.step_index, req.total_steps
        )
        return {"step_index": req.step_index, "explanation": result}
    except ValueError as e:
        raise HTTPException(503, f"AI service unavailable: {e}")
    except Exception as e:
        raise HTTPException(500, f"Step explanation failed: {e}")


@router.post("/code")
async def generate_code(req: AICodeRequest):
    """Generate algorithm implementation in any supported programming language."""
    if req.language.lower() not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, f"Language '{req.language}' not supported. "
                                 f"Choose from: {SUPPORTED_LANGUAGES}")
    try:
        service = get_gemini_service()
        result = await service.generate_code(req.algorithm, req.language)
        return result
    except ValueError as e:
        raise HTTPException(503, f"AI service unavailable: {e}")
    except Exception as e:
        raise HTTPException(500, f"Code generation failed: {e}")


@router.get("/languages")
def list_languages():
    return {"supported_languages": SUPPORTED_LANGUAGES}