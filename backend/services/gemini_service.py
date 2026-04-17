"""
Gemini AI Service
- Explain algorithms
- Explain individual steps
- Generate code in multiple languages
"""

import os
import google.generativeai as genai
from typing import Any


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def explain_algorithm(self, algorithm: str, language: str = "en") -> dict:
        prompt = f"""
You are an expert computer science educator. Explain the '{algorithm}' algorithm clearly.

Structure your response as JSON with these fields:
{{
  "name": "Full Algorithm Name",
  "overview": "2-3 sentence plain English overview",
  "how_it_works": "Step-by-step explanation in 4-6 bullets",
  "time_complexity": {{ "best": "O(?)", "average": "O(?)", "worst": "O(?)" }},
  "space_complexity": "O(?)",
  "use_cases": ["use case 1", "use case 2", "use case 3"],
  "pros": ["pro 1", "pro 2"],
  "cons": ["con 1", "con 2"],
  "fun_fact": "One interesting fact about this algorithm"
}}

Return ONLY valid JSON, no markdown fences.
"""
        response = self.model.generate_content(prompt)
        import json
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            return {"overview": response.text, "name": algorithm}

    async def explain_step(self, algorithm: str, step: dict[str, Any],
                            step_index: int, total_steps: int) -> dict:
        prompt = f"""
You are helping a student understand algorithm visualization.

Algorithm: {algorithm}
Current step {step_index + 1} of {total_steps}:
{step}

Explain in simple terms:
1. What is happening in this specific step?
2. Why is this step necessary?
3. What changes occurred compared to the previous state?

Keep it under 80 words, friendly and educational.
Return JSON: {{"explanation": "...", "key_action": "one phrase summary", "tip": "optional tip"}}
Return ONLY valid JSON, no markdown fences.
"""
        response = self.model.generate_content(prompt)
        import json
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            return {"explanation": response.text}

    async def generate_code(self, algorithm: str, language: str) -> dict:
        prompt = f"""
Write a clean, well-commented implementation of '{algorithm}' in {language}.

Requirements:
- Production-quality code
- Inline comments explaining key steps
- Include example usage at the bottom
- Handle edge cases

Return JSON:
{{
  "language": "{language}",
  "algorithm": "{algorithm}",
  "code": "full code as string with \\n for newlines",
  "explanation": "2-3 sentence summary of the implementation"
}}
Return ONLY valid JSON, no markdown fences.
"""
        response = self.model.generate_content(prompt)
        import json
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            return {"code": response.text, "language": language, "algorithm": algorithm}


# Singleton — instantiate only when needed (avoids crash if no API key at import time)
_gemini_service = None

def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service