.PHONY: help install install-pip install-frontend dev-up dev-down migrate upgrade downgrade run-backend run-celery run-frontend run-agent test clean

help:
	@echo "Available commands:"
	@echo "  make install         - Install Python dependencies using uv (installs uv if needed)"
	@echo "  make install-pip     - Install Python dependencies using pip (fallback)"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo "  make dev-up          - Start PostgreSQL and Redis containers"
	@echo "  make dev-down        - Stop containers"
	@echo "  make migrate         - Create new Alembic migration"
	@echo "  make upgrade         - Run database migrations"
	@echo "  make downgrade       - Rollback last migration"
	@echo "  make run-backend     - Start FastAPI backend server"
	@echo "  make run-celery      - Start Celery worker"
	@echo "  make run-frontend    - Start Vite frontend dev server"
	@echo "  make run-agent       - Run Agno agent example"
	@echo "  make test            - Run tests"
	@echo "  make clean           - Clean generated files"

install:
	@if ! command -v uv > /dev/null 2>&1; then \
		echo "📦 Installing uv..."; \
		if [ "$$(uname -s)" = "Linux" ] || [ "$$(uname -s)" = "Darwin" ]; then \
			curl -LsSf https://astral.sh/uv/install.sh | sh; \
			export PATH="$$HOME/.cargo/bin:$$PATH"; \
		else \
			echo "Please install uv manually: https://github.com/astral-sh/uv#installation"; \
			exit 1; \
		fi; \
	fi
	@uv pip install -e .

install-pip:
	pip install -e .

install-frontend:
	cd frontend && npm install

dev-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5

dev-down:
	docker-compose down

migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

run-backend:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-celery:
	celery -A app.tasks worker --loglevel=info

run-frontend:
	cd frontend && npm run dev

run-agent:
	python agents/agno_app.py

test:
	pytest

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf *.egg-info
	rm -rf uploads/* artifacts/* generated/* previews/* bundles/*
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

