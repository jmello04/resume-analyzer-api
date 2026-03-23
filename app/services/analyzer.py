import json
import re

from anthropic import Anthropic

from app.core.config import settings
from app.domain.models import AnalysisResult

_PROMPT_TEMPLATE = """Analyze the following resume and return a structured evaluation as a JSON object.

The JSON must contain exactly these fields:
- "score": integer between 0 and 100 representing overall resume quality
- "level": one of "Júnior", "Pleno", or "Sênior"
- "strong_points": list of strings describing strengths
- "weak_points": list of strings describing weaknesses
- "suggestions": list of strings with concrete improvement suggestions
- "detected_skills": list of technical and soft skills identified in the resume

Resume content:
{resume_text}

Return only valid JSON. Do not include markdown, code blocks, or any text outside the JSON object."""


class ResumeAnalyzerService:
    def __init__(self) -> None:
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def analyze(self, resume_text: str) -> AnalysisResult:
        message = self.client.messages.create(
            model=settings.analysis_model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": _PROMPT_TEMPLATE.format(resume_text=resume_text),
                }
            ],
        )

        raw = message.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)
        return AnalysisResult(**data)
