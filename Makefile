.DEFAULT_GOAL := help

.PHONY: help build up up-d down logs test test-local test-cov clean

help: ## Exibe esta mensagem de ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Constrói as imagens Docker
	docker-compose build

up: ## Sobe os serviços (API + banco de dados)
	docker-compose up --build

up-d: ## Sobe os serviços em segundo plano
	docker-compose up --build -d

down: ## Para e remove os contêineres
	docker-compose down

logs: ## Exibe os logs da API em tempo real
	docker-compose logs -f api

test: ## Executa os testes dentro do contêiner
	docker-compose exec api pytest

test-local: ## Executa os testes localmente (requer .venv ativo)
	pytest

test-cov: ## Executa os testes com relatório de cobertura
	pytest --cov=app --cov-report=term-missing

clean: ## Remove contêineres, volumes e arquivos temporários
	docker-compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.db" -delete 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
