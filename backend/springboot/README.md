# Spring Boot gateway

Java 17 / Spring Boot 3.5 REST service. Persists questions and attachments
(JPA/PostgreSQL) and orchestrates the two Python services via REST.

## Endpoints

| Endpoint | Description |
|---|---|
| `POST /api/questions` (multipart) | Save question + attachments; parse JSON attachments into `tracked_data`, forward with optional `visionAnalysis` to the LLM service `/query` |
| `GET /api/questions/dashboard/stats` | Totals + 5 most recent questions |
| `POST /api/llm/query` | RAG query via `LLMService` (stores the Q&A pair) |
| `POST /api/questions/vision/analyze` (multipart) | First image → vision `/classify_screen` + `/analyze`, merged response |
| `POST /api/questions/premium-auto/analyze` | Demo-mode analysis (hardcoded scores, persisted as `analyses` rows) |
| `POST /api/questions/test-upload` | Debug: logs/echoes a multipart upload |

`test.http` contains a ready-made sample request for IDE HTTP clients.

## Configuration

`application.properties` holds local defaults (Postgres
`localhost:5432/ux_beta`, `myuser`/`mypassword`); everything is overridable:

| Env var | Purpose |
|---|---|
| `DB_URL` / `DB_USERNAME` / `DB_PASSWORD` | Datasource |
| `APP_LLM_BASE_URL` | LLM service base URL (default `http://localhost:8000`) |
| `APP_VISION_BASE_URL` | Vision service base URL (default `http://localhost:8001`) |
| `APP_CORS_ALLOWED_ORIGINS` | Allowed origins (default `http://localhost:4200`) |

Schema is managed by Hibernate (`ddl-auto=update`) — no SQL migration files.

## Build & run

```bash
./mvnw spring-boot:run     # local (needs Postgres running)
./mvnw package             # jar → target/
docker build -t ux-insight-gateway .   # multi-stage: builds with Maven inside
```

The root `docker-compose.yml` builds this directory and wires `DB_*` and
`APP_*` variables to the other containers.

## Tests

`UxBetaApplicationTests` is a Spring context-load test — it requires a live
PostgreSQL at the configured datasource. A real test suite is a roadmap item.
