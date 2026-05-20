# Observable Microservice Template

A FastAPI-based microservice template focused on **observability** with structured logging, Prometheus metrics, and OpenTelemetry tracing. The project is containerized with Docker and can be run locally with Docker Compose alongside Prometheus and Jaeger for a complete local monitoring stack.

## Overview

This project demonstrates how to build a small Python microservice that is easier to operate and debug in real environments. It includes:

- FastAPI for API development
- Docker and Docker Compose for containerized local development
- Structured JSON logging for readable and searchable logs
- Prometheus metrics exposed at `/metrics`
- OpenTelemetry tracing exported to Jaeger
- Health endpoints for liveness and readiness checks
- Basic automated tests and CI workflow support

## Features

- Health check endpoints: `/health/live` and `/health/ready`
- Item endpoints for simple CRUD-style interaction
- Swagger UI docs at `/docs`
- Prometheus metrics scraping support
- Jaeger trace visualization support
- Request ID middleware for correlating logs across a request lifecycle

## Tech Stack

- Python 3.10
- FastAPI
- Uvicorn
- Pydantic
- Prometheus
- OpenTelemetry
- Jaeger
- Docker / Docker Compose
- Pytest
- GitHub Actions

## Quick Start

### Prerequisites

Make sure the following tools are installed:

- Docker
- Docker Compose
- Git

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd observable_microservice_template
```

### 2. Build the application image

```bash
docker build -t observable-microservice:latest .
```

### 3. Start the full stack

```bash
docker compose up
```

This starts:

- `app` on port `8000`
- `prometheus` on port `9090`
- `jaeger` on port `16686`

### 4. Open the local UIs

- App docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Jaeger: [http://localhost:16686](http://localhost:16686)

## API Endpoints

### Health Endpoints

#### `GET /health/live`
Checks whether the application process is alive.

Example response:

```json
{
  "status": "ok",
  "detail": "live"
}
```

#### `GET /health/ready`
Checks whether the application is ready to serve traffic.

Example response:

```json
{
  "status": "ok",
  "detail": "ready"
}
```

### Metrics Endpoint

#### `GET /metrics`
Exposes Prometheus-formatted metrics for scraping.

This endpoint is used by Prometheus to collect request counts, durations, and other service metrics.

### Item Endpoints

#### `POST /items`
Creates a new item.

Example request:

```json
{
  "name": "Test",
  "description": "Sample item"
}
```

Example response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Test",
  "description": "Sample item",
  "created_at": "2026-05-20T07:00:00+00:00"
}
```

#### `GET /items`
Returns all stored items.

Example response:

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Test",
    "description": "Sample item",
    "created_at": "2026-05-20T07:00:00+00:00"
  }
]
```

> Update the example payloads above if your actual schema differs.

## Observability

### Logging

The application uses structured JSON logging so logs are easier to filter and correlate in local development and production-style environments.

Typical log fields include:

- `asctime`
- `levelname`
- `name`
- `message`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

### Metrics

Prometheus scrapes the application at:

```text
http://app:8000/metrics
```

The scrape interval is configured in `prometheus.yml` to run every 15 seconds.

### Tracing

OpenTelemetry tracing is configured in the app and exported to Jaeger over OTLP.

In Docker Compose, the application should export traces to:

```text
http://jaeger:4317
```

After generating requests, traces can be viewed in the Jaeger UI.

## Project Structure

```text
observable_microservice_template/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── store.py
│   ├── metrics.py
│   ├── tracing.py
│   └── logging_config.py
├── tests/
│   └── test_basics.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
└── README.md
```

## What Each Core File Does

- `main.py` - creates the FastAPI app, registers middleware, and defines API routes.
- `models.py` - defines Pydantic request and response schemas.
- `store.py` - contains in-memory item storage logic.
- `metrics.py` - configures Prometheus metrics and request timing instrumentation.
- `tracing.py` - configures OpenTelemetry tracing and exporters.
- `logging_config.py` - sets up structured logging.
- `test_basics.py` - contains basic tests for health and item endpoints.

## Testing

Run tests locally with:

```bash
pytest
```

Typical tests include:

- health endpoint checks
- item creation and retrieval
- API response validation

If dependencies are not installed locally, install them first:

```bash
pip install -r requirements.txt
```

## CI

The repository can include a GitHub Actions workflow at `.github/workflows/ci.yml`.

A typical CI pipeline will:

- run on `push` and `pull_request`
- install Python dependencies
- run tests with `pytest`
- optionally validate the Docker build

Example commands CI is expected to run:

```bash
pip install -r requirements.txt
pytest
```

## Local Demo Checklist

To verify the project end-to-end locally:

1. Run the stack:

```bash
docker compose up --build
```

2. Verify the app docs page opens:

```text
http://localhost:8000/docs
```

3. Verify Prometheus is running and scraping metrics:

```text
http://localhost:9090
```

Check the `Targets` page and confirm the app target is **UP**.

4. Verify Jaeger is receiving traces:

```text
http://localhost:16686
```

Send a few requests to the app, then search for traces in Jaeger.

## Example cURL Commands

### Check liveness

```bash
curl http://localhost:8000/health/live
```

### Check readiness

```bash
curl http://localhost:8000/health/ready
```

### Create an item

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "Created from curl"}'
```

### List items

```bash
curl http://localhost:8000/items
```

### View raw metrics

```bash
curl http://localhost:8000/metrics
```

## Code Quality Notes

Before submission or publishing, it is a good idea to:

- add docstrings to modules, classes, and functions
- organize imports consistently
- remove unused imports and dead code
- ensure there are no runtime warnings in the local stack
- keep dependency versions explicit in `requirements.txt`

## Demo Evidence

For assignment submission or portfolio use, include either:

- screenshots of `/docs`, Prometheus, and Jaeger, or
- a short screen recording showing the stack working

Suggested evidence files:

- `docs-screenshot.png`
- `prometheus-targets.png`
- `jaeger-trace.png`

## Repository Description

**Observable FastAPI microservice template with Docker, health checks, structured logging, Prometheus metrics, and OpenTelemetry tracing.**

## Future Improvements

- Add persistent storage instead of in-memory storage
- Add more complete CRUD endpoints
- Add custom Prometheus metrics for business events
- Add linting and formatting checks in CI
- Add OpenAPI request examples directly in route definitions

## License

Add a license section here if you plan to publish the repository publicly.
