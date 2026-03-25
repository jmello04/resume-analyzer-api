# Guia de Contribuição

Obrigado pelo interesse em contribuir com o **Resume Analyzer API**!
Este guia explica como configurar o ambiente, as convenções adotadas e o fluxo de trabalho esperado.

---

## Configuração do ambiente

### Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Git

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/jmello04/resume-analyzer-api.git
cd resume-analyzer-api

# 2. Crie o ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 5. Suba o banco de dados
docker-compose up db -d

# 6. Execute os testes para validar o ambiente
pytest
```

---

## Fluxo de trabalho

1. Crie uma branch a partir de `main` com nome descritivo:
   ```bash
   git checkout -b feat/nome-da-funcionalidade
   git checkout -b fix/nome-do-bug
   ```

2. Implemente as alterações seguindo as convenções abaixo.

3. Certifique-se de que todos os testes passam:
   ```bash
   pytest
   ```

4. Abra um Pull Request descrevendo claramente o que foi alterado e por quê.

---

## Convenções de commit

Este projeto adota [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

| Prefixo | Uso |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Alterações na documentação |
| `test:` | Adição ou modificação de testes |
| `refactor:` | Refatoração sem alteração de comportamento |
| `chore:` | Tarefas de manutenção (CI, dependências, config) |
| `perf:` | Melhoria de performance |

**Exemplos:**
```
feat: adicionar suporte a análise de currículos em DOCX
fix: corrigir paginação retornando total incorreto
docs: atualizar exemplos de uso no README
test: adicionar testes para erro de conexão com o banco
```

---

## Estrutura do projeto

```
app/
├── api/routes/      # Endpoints HTTP (somente lógica de roteamento)
├── core/            # Config, logging e exceções globais
├── domain/          # Schemas Pydantic e interfaces abstratas
├── infra/database/  # ORM, conexão e repositório
└── services/        # Lógica de negócio e casos de uso
```

Regras de dependência entre camadas:
- `api` → `services` e `domain`
- `services` → `infra` e `domain`
- `infra` → `domain`
- `domain` → nada (camada mais interna)

---

## Padrões de código

- Type hints em todas as funções públicas
- Nomes em português para variáveis de domínio, inglês para infraestrutura
- Máximo de 100 caracteres por linha
- Sem comentários óbvios — o código deve ser autoexplicativo

---

## Reportar bugs

Use o template de issue disponível em `.github/ISSUE_TEMPLATE/bug_report.yml`.
Inclua sempre: versão do Python, sistema operacional, mensagem de erro completa e passos para reproduzir.
