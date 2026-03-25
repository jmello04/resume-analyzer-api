# Resume Analyzer API

![CI](https://github.com/jmello04/resume-analyzer-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![License](https://img.shields.io/badge/Licença-MIT-green)

API REST para análise automatizada de currículos em PDF. O sistema extrai o conteúdo textual dos documentos enviados e retorna uma avaliação estruturada com pontuação, nível profissional, pontos fortes, fracos, sugestões de melhoria e habilidades detectadas.

---

## Sumário

- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Como executar](#como-executar)
- [Endpoints](#endpoints)
- [Exemplos de uso](#exemplos-de-uso)
- [Testes](#testes)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Códigos de resposta](#códigos-de-resposta)

---

## Tecnologias

| Tecnologia | Versão | Finalidade |
|---|---|---|
| **FastAPI** | 0.115 | Framework web assíncrono de alta performance |
| **pdfplumber** | 0.11 | Extração de texto de arquivos PDF |
| **SQLAlchemy** | 2.0 | ORM para persistência dos dados |
| **PostgreSQL** | 16 | Banco de dados relacional |
| **Pydantic** | 2.10 | Validação e serialização de dados |
| **Docker Compose** | — | Orquestração dos serviços |

---

## Arquitetura

O projeto segue **Clean Architecture**, com separação rigorosa entre as camadas. Cada camada tem uma única responsabilidade e depende apenas das camadas internas.

```
resume-analyzer-api/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── analyze.py       # POST /api/v1/analyze
│   │       └── history.py       # GET  /api/v1/history[/{id}]
│   │
│   ├── core/
│   │   ├── config.py            # Configurações via variáveis de ambiente
│   │   ├── exceptions.py        # Exceções HTTP customizadas
│   │   └── logging.py           # Configuração de logging estruturado
│   │
│   ├── domain/
│   │   ├── interfaces.py        # Contratos abstratos (Repository Pattern)
│   │   └── schemas.py           # Modelos Pydantic de entrada e saída
│   │
│   ├── infra/
│   │   └── database/
│   │       ├── connection.py    # Engine e sessão do SQLAlchemy
│   │       ├── models.py        # Modelos ORM das tabelas
│   │       └── repository.py    # Implementação concreta do repositório
│   │
│   ├── services/
│   │   ├── analyzer.py          # Processamento e avaliação semântica de currículos
│   │   ├── history_service.py   # Casos de uso do histórico
│   │   └── pdf_extractor.py     # Extração de texto via pdfplumber
│   │
│   └── main.py                  # Bootstrap, middlewares e exception handlers
│
├── tests/
│   ├── conftest.py              # Fixtures e banco SQLite de testes
│   └── test_analyze.py          # 25+ testes automatizados
│
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de CI/CD (GitHub Actions)
│
├── Dockerfile                   # Multi-stage build com usuário não-root
├── docker-compose.yml           # API + PostgreSQL com health check
├── Makefile                     # Atalhos de desenvolvimento
└── requirements.txt
```

### Fluxo de uma requisição

```
Cliente
  │
  ▼
[Middleware] request_logging (gera Request-ID, mede latência)
  │
  ▼
[Route] POST /api/v1/analyze
  │
  ├─► [Service] pdf_extractor.py  — extrai texto do PDF
  ├─► [Service] analyzer.py       — processa e retorna avaliação estruturada
  └─► [Repository] AnalysisRepository.create() — persiste no PostgreSQL
        │
        ▼
     Resposta JSON (201 Created)
```

---

## Como executar

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)
- Chave de API do serviço de análise

### 1. Clonar o repositório

```bash
git clone https://github.com/jmello04/resume-analyzer-api.git
cd resume-analyzer-api
```

### 2. Configurar as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env`:

```env
ANALYSIS_API_KEY=sua-chave-aqui
DATABASE_URL=postgresql://postgres:postgres@db:5432/resume_analyzer
DEBUG=false
```

### 3. Subir os serviços

```bash
# Com Makefile
make up

# Ou diretamente
docker-compose up --build
```

A API estará disponível em `http://localhost:8000`

### 4. Acessar a documentação

| Interface | URL |
|---|---|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |

---

## Endpoints

### `POST /api/v1/analyze`

Recebe um currículo em PDF e retorna a análise completa.

| Campo | Tipo | Descrição |
|---|---|---|
| `file` | `File` | Arquivo PDF (obrigatório, máx. 10 MB) |

**Resposta — 201 Created**

```json
{
  "id": 1,
  "filename": "curriculo.pdf",
  "score": 74,
  "level": "Pleno",
  "strong_points": [
    "Experiência sólida em desenvolvimento backend com Python",
    "Domínio de tecnologias modernas como FastAPI e Docker"
  ],
  "weak_points": [
    "Ausência de certificações formais na área"
  ],
  "suggestions": [
    "Incluir links para perfil no LinkedIn e GitHub",
    "Adicionar métricas quantitativas de resultados alcançados"
  ],
  "detected_skills": [
    "Python", "FastAPI", "PostgreSQL", "Docker", "SQLAlchemy"
  ],
  "created_at": "2024-06-15T14:30:00Z"
}
```

---

### `GET /api/v1/history`

Lista todas as análises realizadas, da mais recente para a mais antiga.

**Parâmetros de query**

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `skip` | `int` | `0` | Registros a ignorar |
| `limit` | `int` | `100` | Máximo de registros (até 500) |

**Resposta — 200 OK**

```json
{
  "total": 5,
  "analyses": [...]
}
```

---

### `GET /api/v1/history/{id}`

Retorna uma análise específica pelo ID.

**Resposta — 200 OK** — mesmo formato do `POST /api/v1/analyze`

**Resposta — 404 Not Found**

```json
{
  "detail": "Análise com ID 42 não encontrada"
}
```

---

## Exemplos de uso

### cURL

```bash
# Analisar currículo
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "accept: application/json" \
  -F "file=@curriculo.pdf"

# Listar histórico
curl http://localhost:8000/api/v1/history

# Buscar análise por ID
curl http://localhost:8000/api/v1/history/1
```

### Python (httpx)

```python
import httpx

with open("curriculo.pdf", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/api/v1/analyze",
        files={"file": ("curriculo.pdf", f, "application/pdf")},
    )

print(response.json())
```

---

## Testes

### Com Makefile (dentro do contêiner)

```bash
make test
```

### Localmente

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
pytest
```

### Com cobertura de código

```bash
make test-cov
```

A suíte de testes cobre:

- Validação de arquivo PDF (formato, tamanho, conteúdo vazio)
- Estrutura e tipos dos campos da resposta
- Paginação do histórico
- Busca por ID (existente e inexistente)
- Integração entre `POST /analyze` e `GET /history/{id}`
- Incremento do total ao salvar nova análise
- Endpoints de status (`/` e `/health`)
- Header `X-Request-ID` em todas as respostas
- Tratamento de erros (422, 500, 413)

---

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `ANALYSIS_API_KEY` | **Sim** | — | Chave de autenticação do serviço de análise |
| `DATABASE_URL` | **Sim** | — | String de conexão PostgreSQL |
| `ANALYSIS_MODEL` | Não | ver `.env.example` | Modelo de análise utilizado |
| `ALLOWED_ORIGINS` | Não | `["*"]` | Origens permitidas pelo CORS |
| `DEBUG` | Não | `false` | Ativa logs detalhados |

---

## Códigos de resposta

| Código | Descrição |
|---|---|
| `200 OK` | Requisição bem-sucedida |
| `201 Created` | Análise criada com sucesso |
| `400 Bad Request` | Arquivo inválido, vazio ou formato incorreto |
| `404 Not Found` | Análise não encontrada |
| `413 Request Entity Too Large` | Arquivo excede 10 MB |
| `422 Unprocessable Entity` | Não foi possível extrair texto do PDF |
| `500 Internal Server Error` | Erro interno inesperado |

---

## Makefile — Referência rápida

```bash
make up          # Sobe os serviços (build + start)
make up-d        # Sobe em segundo plano
make down        # Para os serviços
make logs        # Exibe logs da API em tempo real
make test        # Roda os testes dentro do contêiner
make test-local  # Roda os testes localmente
make test-cov    # Testes com relatório de cobertura
make clean       # Remove contêineres, volumes e cache
```

---

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
