# UX Insight Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A containerized UX analysis platform. An Angular dashboard submits questions, UI
screenshots, and interaction data to a Spring Boot gateway, which orchestrates two
Python services — a RAG-backed LLM consultant (provider-agnostic) and a
computer-vision UI analyzer — with everything persisted in PostgreSQL.

## What it does

**Manual Mode** — the core workflow, fully working end to end:

1. Ask a UX question and attach UI screenshots and/or JSON interaction data
2. Each screenshot is analyzed by the vision service (UI-element detection,
   screen classification, OCR-enhanced labels)
3. The LLM service runs a two-pass RAG query grounded in 13 Nielsen-style UX
   heuristics stored in ChromaDB (draft answer, then a validation/refinement pass)
4. The answer is rendered in the dashboard chat panel; the question and all
   attachments are stored in PostgreSQL

**Dashboard stats** — total questions, total attachments, and the five most
recent questions.

**Premium Auto Mode** — currently returns **demo data** (clearly labeled as
such in the UI). The real headless-crawler collector lives in
[`tools/automation`](tools/automation/README.md); wiring its output into the
gateway is on the roadmap.

## Architecture

```
Browser (Angular 20 + Material, :4200)
   │   window.API_BASE_URL  (set in frontend/public/env.js, default http://localhost:8080/api)
   ▼
Spring Boot gateway (:8080) ──────────────► PostgreSQL (:5432)
   │ APP_LLM_BASE_URL                │ APP_VISION_BASE_URL
   ▼                                  ▼
FastAPI LLM service (:5000)     FastAPI Vision service (:5001)
  • ChromaDB RAG over 13           • TorchScript UI-element detection
    UX heuristics                  • TorchScript screen classification (ENRICO)
  • two-pass prompting             • EasyOCR text extraction
  • OpenAI / Mistral / DeepSeek /
    OpenRouter / local Ollama
```

| Service | Directory | Stack | Port |
|---|---|---|---|
| Frontend | `frontend/` | Angular 20, Angular Material, nginx | 4200 |
| API gateway | `backend/springboot/` | Java 17, Spring Boot 3.5, JPA | 8080 |
| LLM service | `backend/fastapi_llm/` | Python 3.11, FastAPI, ChromaDB, sentence-transformers | 5000 |
| Vision service | `backend/fastapi_vision/` | Python 3.11, FastAPI, PyTorch, EasyOCR | 5001 |
| Database | `docker-compose.yml` | PostgreSQL 15 | 5432 |

## Quick start

Prerequisites: Docker + Docker Compose, ~10 GB free disk, an API key for one
LLM provider (or [Ollama](https://ollama.com) for a fully local setup).

**1. Configure the environment**

```bash
cp .env.example .env   # then edit: set POSTGRES_PASSWORD and one API key
```

**2. Seed the RAG store** (required — the LLM service exits at startup
without it)

```bash
# Option A: with a local Python environment
cd backend/fastapi_llm
pip install chromadb sentence-transformers
python populate_chroma.py          # writes data/chroma_db (repo-relative, CWD-independent)

# Option B: entirely inside Docker (uses the service image)
cd <repo root>
docker compose build fastapi-llm
docker compose run --rm \
  -v "$(pwd)/datasets:/datasets:ro" \
  -e HEURISTICS_PATH=/datasets/heuristics/ux_heuristics.json \
  fastapi-llm python populate_chroma.py
```

**3. (Optional, for vision analysis) download the model checkpoints**

The two TorchScript checkpoints are not bundled in this repository. Fetch them
from the [WebUI project releases (biglab, CMU)](https://huggingface.co/biglab)
and place them here:

```
backend/fastapi_vision/webui-main/downloads/checkpoints/screenrecognition-web7k.torchscript
backend/fastapi_vision/webui-main/downloads/checkpoints/screenclassification-resnet-noisystudent+web350k.torchscript
```

The label/class maps they need are already committed under
`backend/fastapi_vision/webui-main/metadata/`. Without the checkpoints the
vision container fails its model load at startup; the rest of the platform
works, but screenshot analysis endpoints will fail.

**4. Start everything**

```bash
docker compose up -d
```

The app is served at http://localhost:4200. Other endpoints: gateway
http://localhost:8080, LLM http://localhost:5000, vision http://localhost:5001,
PostgreSQL on 5432.

> The browser talks to the gateway directly via `window.API_BASE_URL`, which is
> set in `frontend/public/env.js` (default `http://localhost:8080/api`). To
> deploy the frontend against a different gateway host, edit that file before
> building the image.

## Configuration

All configuration is environment-driven (see `.env.example`):

| Variable | Default | Used by |
|---|---|---|
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | `uxdb` / `uxuser` / — | PostgreSQL container; also fed to the gateway as `DB_*` |
| `FRONTEND_ORIGIN` | `http://localhost:4200` | Gateway CORS (`APP_CORS_ALLOWED_ORIGINS`) |
| `LLM_API_URL` / `VISION_API_URL` | `http://fastapi-llm:5000` / `http://fastapi-vision:5001` | Gateway → Python services |
| `LLM_PROVIDER` | `openai` | LLM service (`openai`, `mistral`, `deepseek`, `openrouter`, `ollama`) |
| `OPENAI_API_KEY` / `MISTRAL_API_KEY` / `DEEPSEEK_API_KEY` / `OPENROUTER_API_KEY` | — | LLM service |
| `OPENAI_MODEL` / `MISTRAL_MODEL` / `DEEPSEEK_MODEL` / `OPENROUTER_MODEL` | sensible per-provider defaults | LLM service (optional overrides) |
| `OLLAMA_ENDPOINT` / `OLLAMA_MODEL` | `http://ollama:11434` / `llama3.1:8b` | LLM service in `ollama` mode |

The gateway also honors `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `APP_LLM_BASE_URL`,
`APP_VISION_BASE_URL`, and `APP_CORS_ALLOWED_ORIGINS` directly; its local
(non-Docker) defaults (`localhost:5432/ux_beta`, `myuser`/`mypassword`) live in
`backend/springboot/src/main/resources/application.properties`.

## API

### Spring Boot gateway (:8080)

| Endpoint | Description |
|---|---|
| `POST /api/questions` (multipart) | Submit question + attachments + optional `visionAnalysis` JSON; proxies to the LLM service |
| `GET /api/questions/dashboard/stats` | Totals + 5 most recent questions |
| `POST /api/llm/query` | Direct LLM/RAG query (`{question, tracked_data?}`) |
| `POST /api/questions/vision/analyze` (multipart) | Screenshot → classification + detections |
| `POST /api/questions/premium-auto/analyze` | **Demo data** (see above) |
| `POST /api/questions/test-upload` (multipart) | Debug endpoint — logs and echoes what it received |

### FastAPI LLM service (:5000)

- `GET /` — service status
- `POST /query` — RAG query; returns `{question, relevant_context, metadata, answer, sources}`

### FastAPI Vision service (:5001)

- `POST /analyze` — UI-element detections for a screenshot
- `POST /classify_screen` — ENRICO screen classification (`{label, confidence}`)

## The RAG knowledge base

`datasets/heuristics/ux_heuristics.json` contains 13 Nielsen-style UX
heuristics that ground every LLM answer. They are embedded with
`BAAI/bge-small-en-v1.5` (downloaded on first use, ~130 MB) into a ChromaDB
collection by `backend/fastapi_llm/populate_chroma.py`;
`test_chroma.py` is a smoke check for the seeded store.

## Premium Auto Mode and the automation tool

The UI's Premium Auto Mode returns demo scores today. The real collector — a
Puppeteer stealth crawler that records interaction telemetry, takes
screenshots, and computes page metrics — lives in
[`tools/automation`](tools/automation/README.md) and works standalone. Feeding
its results into the gateway is the main roadmap item.

## First build expectations

The Python images install PyTorch, torchvision, EasyOCR, and OpenCV. Expect a
**2–3 GB download and a 15–30 minute first build** (subsequent builds reuse
Docker layer cache). EasyOCR and the embedding model download on first run.
8 GB RAM recommended. This is why the RAG store seeding and model downloads are
separate, cacheable steps.

## Development without Docker

```bash
# Frontend                     # Gateway                        # Python services
cd frontend                    cd backend/springboot            cd backend/fastapi_llm
npm install                    ./mvnw spring-boot:run           uvicorn main:app --port 8000
npm start                      (needs Postgres on               cd ../fastapi_vision
                               localhost:5432/ux_beta)          uvicorn main:app --port 8001
```

Note the local port defaults: the gateway looks for the LLM/vision services at
`:8000`/`:8001` unless `APP_LLM_BASE_URL`/`APP_VISION_BASE_URL` say otherwise.

## Testing

Honest answer: the suite is minimal. There is one Angular smoke spec
(`ng test`), a Spring context-load test that requires a live database, and a
Python smoke script for the RAG store. A real test suite is a stated roadmap
goal — PRs welcome.

## Current limitations & roadmap

- **Premium Auto Mode is demo data** — wire `tools/automation` output into the
  gateway (receiving endpoint planned: `/api/questions/premium-auto/automation-results`)
- Vision model checkpoints are a manual download (licensing/size — see step 3)
- No authentication anywhere; this is an internal/demo tool as-is
- No CI pipeline yet
- Question history UI (list/get/delete) — the backend currently only stores
- Minimal test coverage (see above)

## Project structure

```
ux-insight-platform/
├── frontend/                  # Angular 20 dashboard (nginx-served)
├── backend/
│   ├── springboot/            # Spring Boot 3.5 gateway (controllers, JPA, RestTemplate)
│   ├── fastapi_llm/           # RAG + multi-provider LLM service
│   ├── fastapi_vision/        # UI detection/classification + OCR service
│   └── (postgres runs from the official image; schema via JPA)
├── datasets/heuristics/       # 13 UX heuristics (RAG knowledge base)
├── tools/automation/          # standalone Puppeteer website analyzer
├── docker-compose.yml         # all five services
├── .env.example               # environment template
└── README.md
```

## Attribution

- The vision models and label maps come from the **WebUI** project —
  *WebUI: A Dataset for Enhancing Visual UI Understanding with Web Semantics*
  (CHI 2023, best-paper honorable mention), by the biglab team at CMU. The
  TorchScript checkpoints are published by the project on
  [HuggingFace (biglab)](https://huggingface.co/biglab).
- The RAG knowledge base is a set of Nielsen-style heuristics
  (`datasets/heuristics/ux_heuristics.json`).
- UI built with Angular Material; automation with Puppeteer.

```
@inproceedings{wu2023webui,
  title={WebUI: A Dataset for Enhancing Visual UI Understanding with Web Semantics},
  author={Wu, Jason and Wang, Siyan and Shen, Siman and Peng, Yi-Hao and Nichols, Jeffrey and Bigham, Jeffrey P},
  booktitle={Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems},
  year={2023}
}
```

## License

[MIT](LICENSE)
