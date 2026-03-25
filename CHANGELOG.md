# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adota [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [1.0.0] — 2026-03-24

### Adicionado
- `POST /api/v1/analyze` — recebe currículo em PDF e retorna análise estruturada
- `GET /api/v1/history` — lista histórico de análises com paginação
- `GET /api/v1/history/{id}` — retorna análise específica por ID
- Extração de texto de PDFs com `pdfplumber`
- Serviço de análise semântica de currículos configurável via variáveis de ambiente
- Persistência de histórico com SQLAlchemy e PostgreSQL
- Containerização com Docker multi-stage build e usuário não-root
- Pipeline de CI/CD com GitHub Actions
- Suite de 25+ testes automatizados com pytest
- Logging estruturado com Request-ID rastreável por requisição
- Middleware de logging com medição de latência
- Makefile com atalhos de desenvolvimento
- Documentação interativa automática via Swagger UI e ReDoc
