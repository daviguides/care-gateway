# 🩺 Care Gateway: All-in-One Portfolio Project

<p align="center">
  <a href="./SECURITY.md"><img src="https://img.shields.io/badge/security-zero%20trust-blue"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="http://daviguides.github.io"><img src="https://img.shields.io/badge/built%20with-%E2%9D%A4%EF%B8%8F%20by%20Davi%20Guides-orange"></a>
  <a href="https://daviguides.github.io/articles/devsecops/2025/04/25/zero-trust-manifest.html"><img src="https://img.shields.io/badge/read-architecture%20article-blueviolet"></a>
  <a href="https://daviguides.github.io/keysentinel/"><img src="https://img.shields.io/badge/docs-online-blue"></a>
  <img src="https://img.shields.io/badge/tests-passing-brightgreen">
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen">
</p>

**Care Gateway** is a modular, full-stack healthcare backend system designed to showcase real-world engineering skills across REST APIs, gRPC services, ETL pipelines, and messaging systems. This project reflects hands-on experience with scalable backend systems, domain modeling, and cloud-native design patterns using **PostgreSQL**, **Kafka**, **PySpark**, and multiple Python web frameworks.

This repository simulates a healthcare claim submission platform — suitable as a demonstration for engineering roles requiring strong expertise in **Python**, **gRPC**, **API design**, and **data processing**.

---

## ⭐ Related Projects

- 🔗 [sftp2s3](https://github.com/daviguides/sftp2s3): Syncs files from SFTP to S3 — ideal for the upstream flow of EDI files.
- 🔗 [eks-terraform-ansible-gitops](https://github.com/daviguides/eks-terraform-ansible-gitops): AWS EKS with EC2 nodes using CDK + Terraform — useful for deploying these services.

---

## 🔧 Components Overview

### 1. FastAPI Application

- Async REST API using **FastAPI** + **SQLModel**
- Designed for high performance and modern async use cases
- Fully covered with `pytest-asyncio`

**Entry Point:** `care_gateway/api_fastapi/app.py`

**Example Endpoints:**

```http
GET /claims/
GET /claim_events/
GET /claim_events/by-claim/{claim_id}
```

---

### 2. Flask Application

- Synchronous REST API with **Flask** + **SQLAlchemy**
- Uses **Marshmallow** for serialization
- Communicates with the gRPC service for deeper logic
- Great for demonstrating traditional Flask-based workflows

**Entry Point:** `care_gateway/api_flask/app.py`

**Example Endpoints:**

```http
GET /claims/
POST /claim_events/
POST /claim_events/submit
```

---

### 3. gRPC Service

- Built using **grpcio** and **grpcio-tools**
- Provides backend logic for claim submission
- Decoupled architecture simulating modern backend patterns

**Protos:** `care_gateway/service_grpc/proto/claims/`

**To Run:**

```bash
python scripts/run_service_grpc.py
```

---

### 4. ETL Worker (Kafka + Spark)

- Event-driven ETL pipeline using **Kafka** and **PySpark**
- Processes **EDI 837** healthcare claim files via [`databricksx12`](https://github.com/databricks-industry-solutions/x12-edi-parser)
- Transforms and flattens data into PostgreSQL-ready format

**Entry Point:** `care_gateway/worker_kafka/app.py`

**Flow:**

1. An `.edi` or `.txt` file lands in S3 (via `sftp2s3`)
2. A Kafka event is emitted
3. Worker consumes the event, parses the EDI file, and prepares DB records

---

## 📦 Directory Structure

```
care_gateway/
├── api_fastapi/            # FastAPI app (SQLModel + async)
├── api_flask/              # Flask app (SQLAlchemy + Marshmallow)
├── db/                     # Shared DB models
├── service_grpc/           # gRPC server and services
├── worker_kafka/           # Kafka + Spark ETL worker
├── utils/                  # Utilities (e.g., test DB setup)
├── logging_config.py       # Logging setup
scripts/                    # Execution helpers
data/                       # EDI inbox/outbox folders
alembic/                    # Alembic migrations
```

---

## 📥 Installation & Setup

### ✅ Requirements

- Python 3.12+
- PostgreSQL running locally (`claims_test_db`, `claims_test_db_test`)
- Kafka broker (for ETL)

---

### 1. Create Environment & Install

```bash
uv venv
uv pip install -e .[dev,api-fastapi,worker-kafka-spark,grpcio-server]
```

---

### 2. Create Databases and Run Migrations

```bash
createdb claims_test_db
createdb claims_test_db_test
make upgrade
```

---

### 3. Run Applications

```bash
# Terminal 1: gRPC Service
python scripts/run_service_grpc.py

# Terminal 2: Flask API
python scripts/run_api_flask.py

# Terminal 3: FastAPI
bash scripts/run_api_fastapi.zsh

# Terminal 4: Kafka Worker
python scripts/run_kafka_scheduler.py
```

---

### 4. Run Tests

```bash
pytest --cov=care_gateway --cov-report=term-missing
```

Or test manually with `tests/requests.http`.

---

## 🧪 Test Coverage

- ✅ Full test coverage for Flask and FastAPI APIs
- ✅ DB model validation
- ✅ gRPC call simulation
- ✅ Kafka + ETL test structure (expandable)

---

## ⚠️ Disclaimer

This project was built with a focus on demonstrating **integration of multiple technologies**. As such:

- Data models are intentionally **simplified**
- EDI 837 ingestion **does not parse every segment**
- Certain flows (e.g., full S3 sync + Kafka trigger) are **simulated**
- The primary goal is **showcasing architecture, backend versatility, and tech integration**, not production-readiness

---

## 📄 License

[MIT License](LICENSE)
