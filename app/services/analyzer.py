import json
from typing import Any

import anthropic

from app.core.config import settings
from app.core.exceptions import AnalysisProcessingError

_PROMPT_TEMPLATE = """Você é um especialista em recrutamento e avaliação de perfis profissionais. \
Analise o currículo abaixo com atenção e retorne uma avaliação técnica objetiva.

CURRÍCULO:
{resume_text}

Retorne EXCLUSIVAMENTE um objeto JSON válido, sem texto adicional, com a seguinte estrutura:
{{
    "score": <inteiro de 0 a 100>,
    "level": "<Júnior|Pleno|Sênior>",
    "strong_points": ["<ponto forte 1>", "<ponto forte 2>", ...],
    "weak_points": ["<ponto fraco 1>", "<ponto fraco 2>", ...],
    "suggestions": ["<sugestão 1>", "<sugestão 2>", ...],
    "detected_skills": ["<habilidade 1>", "<habilidade 2>", ...]
}}

Diretrizes de pontuação:
- 0 a 30: Perfil com pouca ou nenhuma experiência relevante
- 31 a 50: Perfil em desenvolvimento inicial da carreira
- 51 a 70: Perfil intermediário com boa base técnica
- 71 a 85: Perfil sólido, bem estruturado e consistente
- 86 a 100: Perfil excepcional e altamente qualificado

Diretrizes de nível:
- Júnior: até 2 anos de experiência prática ou início de carreira
- Pleno: de 3 a 5 anos com domínio das principais responsabilidades
- Sênior: 6 ou mais anos com liderança técnica e autonomia comprovada

Forneça entre 3 e 6 itens em cada lista. Baseie-se exclusivamente no conteúdo do currículo."""

_REQUIRED_FIELDS = {
    "score",
    "level",
    "strong_points",
    "weak_points",
    "suggestions",
    "detected_skills",
}

_LIST_FIELDS = {"strong_points", "weak_points", "suggestions", "detected_skills"}


def _validate_result(result: dict[str, Any]) -> None:
    missing = _REQUIRED_FIELDS - result.keys()
    if missing:
        raise AnalysisProcessingError(
            f"Resposta de análise incompleta. Campos ausentes: {', '.join(sorted(missing))}"
        )

    try:
        result["score"] = max(0, min(100, int(result["score"])))
    except (ValueError, TypeError):
        raise AnalysisProcessingError(
            "Campo 'score' deve ser um número inteiro entre 0 e 100."
        )

    if not isinstance(result.get("level"), str) or not result["level"].strip():
        raise AnalysisProcessingError("Campo 'level' deve ser uma string não vazia.")

    for field in _LIST_FIELDS:
        if not isinstance(result.get(field), list):
            raise AnalysisProcessingError(
                f"Campo '{field}' deve ser uma lista de strings."
            )


def analyze_resume(resume_text: str) -> dict[str, Any]:
    try:
        client = anthropic.Anthropic(api_key=settings.ANALYSIS_API_KEY)

        message = client.messages.create(
            model=settings.ANALYSIS_MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": _PROMPT_TEMPLATE.format(resume_text=resume_text),
                }
            ],
        )

        raw = message.content[0].text.strip()

        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        result: dict[str, Any] = json.loads(raw)

        _validate_result(result)

        return result

    except AnalysisProcessingError:
        raise
    except json.JSONDecodeError:
        raise AnalysisProcessingError(
            "Não foi possível interpretar o resultado da análise."
        )
    except anthropic.APIConnectionError:
        raise AnalysisProcessingError(
            "Falha na conexão com o serviço de análise. Tente novamente."
        )
    except anthropic.RateLimitError:
        raise AnalysisProcessingError(
            "Limite de requisições atingido. Aguarde alguns instantes e tente novamente."
        )
    except anthropic.APIStatusError as exc:
        raise AnalysisProcessingError(f"Erro no serviço de análise: {exc.message}")
    except Exception as exc:
        raise AnalysisProcessingError(f"Erro inesperado durante a análise: {str(exc)}")
