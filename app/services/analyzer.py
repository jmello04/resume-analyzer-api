"""Módulo responsável pela análise estruturada de currículos em texto."""

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

_REQUIRED_FIELDS: frozenset[str] = frozenset({
    "score",
    "level",
    "strong_points",
    "weak_points",
    "suggestions",
    "detected_skills",
})

_LIST_FIELDS: frozenset[str] = frozenset({
    "strong_points",
    "weak_points",
    "suggestions",
    "detected_skills",
})


def _validate_analysis_payload(payload: dict[str, Any]) -> None:
    """Valida os campos obrigatórios e tipos do payload retornado pela API de análise.

    Args:
        payload: Dicionário desserializado com os campos da análise.

    Raises:
        AnalysisProcessingError: Se algum campo obrigatório estiver ausente ou com tipo inválido.
    """
    missing_fields = _REQUIRED_FIELDS - payload.keys()
    if missing_fields:
        raise AnalysisProcessingError(
            f"Resposta de análise incompleta. Campos ausentes: {', '.join(sorted(missing_fields))}"
        )

    try:
        payload["score"] = max(0, min(100, int(payload["score"])))
    except (ValueError, TypeError) as exc:
        raise AnalysisProcessingError(
            "Campo 'score' deve ser um número inteiro entre 0 e 100."
        ) from exc

    if not isinstance(payload.get("level"), str) or not payload["level"].strip():
        raise AnalysisProcessingError("Campo 'level' deve ser uma string não vazia.")

    for field in _LIST_FIELDS:
        if not isinstance(payload.get(field), list):
            raise AnalysisProcessingError(
                f"Campo '{field}' deve ser uma lista de strings."
            )


def analyze_resume(resume_text: str) -> dict[str, Any]:
    """Envia o texto de um currículo para a API de análise e retorna a avaliação estruturada.

    Args:
        resume_text: Conteúdo textual extraído do currículo em PDF.

    Returns:
        Dicionário com os campos: score, level, strong_points, weak_points,
        suggestions e detected_skills.

    Raises:
        AnalysisProcessingError: Se a API retornar erro, resposta malformada ou
            se ocorrer falha de conexão ou limite de requisições.
    """
    try:
        client = anthropic.Anthropic(api_key=settings.ANALYSIS_API_KEY)

        api_response = client.messages.create(
            model=settings.ANALYSIS_MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": _PROMPT_TEMPLATE.format(resume_text=resume_text),
                }
            ],
        )

        raw_content = api_response.content[0].text.strip()

        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            raw_content = "\n".join(lines[1:-1]).strip()

        analysis_payload: dict[str, Any] = json.loads(raw_content)

        _validate_analysis_payload(analysis_payload)

        return analysis_payload

    except AnalysisProcessingError:
        raise
    except json.JSONDecodeError as exc:
        raise AnalysisProcessingError(
            "Não foi possível interpretar o resultado da análise."
        ) from exc
    except anthropic.APIConnectionError as exc:
        raise AnalysisProcessingError(
            "Falha na conexão com o serviço de análise. Tente novamente."
        ) from exc
    except anthropic.RateLimitError as exc:
        raise AnalysisProcessingError(
            "Limite de requisições atingido. Aguarde alguns instantes e tente novamente."
        ) from exc
    except anthropic.APIStatusError as exc:
        raise AnalysisProcessingError(f"Erro no serviço de análise: {exc.message}") from exc
    except Exception as exc:
        raise AnalysisProcessingError(f"Erro inesperado durante a análise: {str(exc)}") from exc
