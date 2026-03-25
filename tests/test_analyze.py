from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

MOCK_RESULT = {
    "score": 74,
    "level": "Pleno",
    "strong_points": [
        "Experiência sólida em desenvolvimento backend com Python",
        "Domínio de tecnologias modernas como FastAPI e Docker",
        "Histórico consistente de entregas em projetos reais",
    ],
    "weak_points": [
        "Ausência de certificações formais na área",
        "Pouca menção a trabalho colaborativo em equipe",
    ],
    "suggestions": [
        "Incluir links para perfil no LinkedIn e repositórios no GitHub",
        "Adicionar métricas e resultados quantitativos das entregas",
        "Detalhar projetos pessoais ou contribuições open source",
    ],
    "detected_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "SQLAlchemy"],
}

MOCK_RESUME_TEXT = (
    "João Silva\n"
    "Desenvolvedor Backend Python | 4 anos de experiência\n\n"
    "Habilidades: Python, FastAPI, PostgreSQL, Docker, SQLAlchemy, REST APIs\n\n"
    "Experiência:\n"
    "- Empresa XYZ (2021–2024): Desenvolvimento de APIs REST com FastAPI e PostgreSQL\n"
    "- Empresa ABC (2020–2021): Manutenção de sistemas legados em Python\n\n"
    "Formação: Bacharelado em Ciência da Computação – Universidade Federal (2019)"
)

VALID_PDF_BYTES = b"%PDF-1.4 mock content for testing"


class TestStatusEndpoints:
    def test_health_check_retorna_200(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_retorna_info_da_api(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
        assert "service" in data
        assert "docs" in data

    def test_resposta_contem_request_id_no_header(self, client: TestClient):
        response = client.get("/health")
        assert "x-request-id" in response.headers


class TestAnalyzeEndpoint:
    def test_analise_retorna_201_com_pdf_valido(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        assert response.status_code == 201

    def test_campos_obrigatorios_presentes_na_resposta(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        data = response.json()
        campos = ["id", "filename", "score", "level", "strong_points",
                  "weak_points", "suggestions", "detected_skills", "created_at"]
        for campo in campos:
            assert campo in data, f"Campo obrigatório ausente: {campo}"

    def test_filename_salvo_corretamente(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("meu_curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        assert response.json()["filename"] == "meu_curriculo.pdf"

    def test_score_dentro_do_intervalo_valido(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        score = response.json()["score"]
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_level_com_valor_valido(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        assert response.json()["level"] in ("Júnior", "Pleno", "Sênior")

    def test_listas_sao_do_tipo_correto(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        data = response.json()
        for campo in ("strong_points", "weak_points", "suggestions", "detected_skills"):
            assert isinstance(data[campo], list), f"'{campo}' deveria ser uma lista"

    def test_rejeita_arquivo_nao_pdf(self, client: TestClient):
        response = client.post(
            "/api/v1/analyze",
            files={"file": ("curriculo.docx", b"conteudo qualquer", "application/msword")},
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_rejeita_arquivo_com_extensao_txt(self, client: TestClient):
        response = client.post(
            "/api/v1/analyze",
            files={"file": ("curriculo.txt", b"texto puro", "text/plain")},
        )
        assert response.status_code == 400

    def test_rejeita_arquivo_vazio(self, client: TestClient):
        response = client.post(
            "/api/v1/analyze",
            files={"file": ("vazio.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400
        assert "vazio" in response.json()["detail"].lower()

    def test_rejeita_arquivo_maior_que_10mb(self, client: TestClient):
        conteudo_grande = b"A" * (10 * 1024 * 1024 + 1)
        response = client.post(
            "/api/v1/analyze",
            files={"file": ("grande.pdf", conteudo_grande, "application/pdf")},
        )
        assert response.status_code == 413

    def test_erro_na_extracao_do_pdf_retorna_422(self, client: TestClient):
        from app.core.exceptions import PDFExtractionError

        with patch(
            "app.api.routes.analyze.extract_text_from_pdf",
            side_effect=PDFExtractionError("PDF ilegível"),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("corrompido.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        assert response.status_code == 422
        assert "PDF ilegível" in response.json()["detail"]

    def test_erro_no_servico_de_analise_retorna_500(self, client: TestClient):
        from app.core.exceptions import AnalysisProcessingError

        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch(
                "app.api.routes.analyze.analyze_resume",
                side_effect=AnalysisProcessingError("Serviço indisponível"),
            ),
        ):
            response = client.post(
                "/api/v1/analyze",
                files={"file": ("curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        assert response.status_code == 500


class TestHistoryEndpoints:
    def test_historico_retorna_200(self, client: TestClient):
        response = client.get("/api/v1/history")
        assert response.status_code == 200

    def test_historico_possui_campos_obrigatorios(self, client: TestClient):
        response = client.get("/api/v1/history")
        data = response.json()
        assert "total" in data
        assert "analyses" in data

    def test_historico_analyses_e_lista(self, client: TestClient):
        response = client.get("/api/v1/history")
        assert isinstance(response.json()["analyses"], list)

    def test_historico_total_e_inteiro(self, client: TestClient):
        response = client.get("/api/v1/history")
        assert isinstance(response.json()["total"], int)

    def test_historico_paginacao_skip_e_limit(self, client: TestClient):
        response = client.get("/api/v1/history?skip=0&limit=10")
        assert response.status_code == 200

    def test_historico_limit_invalido_retorna_422(self, client: TestClient):
        response = client.get("/api/v1/history?limit=0")
        assert response.status_code == 422

    def test_historico_retorna_404_para_id_inexistente(self, client: TestClient):
        response = client.get("/api/v1/history/999999")
        assert response.status_code == 404

    def test_historico_mensagem_404_contem_id(self, client: TestClient):
        response = client.get("/api/v1/history/999999")
        assert "999999" in response.json()["detail"]

    def test_analise_salva_aparece_no_historico(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            post_response = client.post(
                "/api/v1/analyze",
                files={"file": ("novo_curriculo.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        assert post_response.status_code == 201
        analysis_id = post_response.json()["id"]

        get_response = client.get(f"/api/v1/history/{analysis_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == analysis_id
        assert get_response.json()["filename"] == "novo_curriculo.pdf"

    def test_historico_total_incrementa_apos_analise(self, client: TestClient):
        total_inicial = client.get("/api/v1/history").json()["total"]

        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            client.post(
                "/api/v1/analyze",
                files={"file": ("mais_um.pdf", VALID_PDF_BYTES, "application/pdf")},
            )

        total_atualizado = client.get("/api/v1/history").json()["total"]
        assert total_atualizado == total_inicial + 1

    def test_historico_ordenado_por_mais_recente(self, client: TestClient):
        with (
            patch("app.api.routes.analyze.extract_text_from_pdf", return_value=MOCK_RESUME_TEXT),
            patch("app.api.routes.analyze.analyze_resume", return_value=MOCK_RESULT),
        ):
            for nome in ("primeiro.pdf", "segundo.pdf", "terceiro.pdf"):
                client.post(
                    "/api/v1/analyze",
                    files={"file": (nome, VALID_PDF_BYTES, "application/pdf")},
                )

        analyses = client.get("/api/v1/history?limit=3").json()["analyses"]
        if len(analyses) >= 2:
            from datetime import datetime
            datas = [datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")) for a in analyses]
            assert datas == sorted(datas, reverse=True)
