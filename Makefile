DB_URL=postgresql+psycopg://admin:admin@localhost:5432/claims_db
PROTO_BASE=eligibility_checker/service_grpc/proto
PROTO_NAME ?= eligibility

.PHONY: help proto run-server run-api

help:
	@echo "Comandos disponíveis:"
	@echo "  make proto        - Compila os arquivos .proto"
	@echo "  make run-server   - Inicia o servidor gRPC"
	@echo "  make run-api      - Inicia o servidor Flask"

install:
	uv sync --all-groups

proto:
	@python -m grpc_tools.protoc -I $(PROTO_BASE) \
		--python_out=$(PROTO_BASE) \
		--grpc_python_out=$(PROTO_BASE) \
		$(PROTO_BASE)/$(PROTO_NAME)/$(PROTO_NAME).proto

run-server:
	python run_grpc.py

run-flask:
	python run_flask.py

migrate:
	alembic revision --autogenerate -m "auto migration"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

db-create:
	createdb claims_db

db-drop:
	dropdb claims_db --if-exists

db-reset:
	dropdb claims_db --if-exists
	createdb claims_db

test:
	export ENVIRONMENT=test && pytest -c ./config/pytest.ini --cov-config= ./config/pytest.ini

cov:
	export ENVIRONMENT=test && pytest -c ./config/pytest.ini --cov app --cov-report=xml:config/cov/converage.xml --cov-report=html:config/cov/htmlcov/
	open ./config/cov/htmlcov/index.html
	@echo "Coverage report generated!"
