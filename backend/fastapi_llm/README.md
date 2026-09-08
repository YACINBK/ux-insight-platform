# FastAPI LLM service

RAG-backed UX consultant. Answers are grounded in 13 Nielsen-style UX
heuristics stored in ChromaDB and generated in **two passes** (draft answer,
then a validation/enhancement pass) through whichever provider is selected.

## Endpoints

- `GET /` — status
- `POST /query` — `{question, tracked_data?, attachments?, vision?}` →
  `{question, relevant_context, metadata, answer, sources}`

## Providers

Selected by `LLM_PROVIDER` (`openai` | `mistral` | `deepseek` | `openrouter`
| `ollama`), each authenticated by its `*_API_KEY` env var; optional
`*_MODEL` overrides exist per provider. Ollama mode is fully local
(`OLLAMA_ENDPOINT`, `OLLAMA_MODEL`).

## The vector store (required setup)

The service **exits at startup** if the `ux_heuristics` collection is missing.
Seed it once:

```bash
pip install chromadb sentence-transformers
python populate_chroma.py     # reads datasets/heuristics/ux_heuristics.json
                              # (repo-relative; override with HEURISTICS_PATH)
                              # writes data/chroma_db (override DATA_DIR)
python test_chroma.py         # smoke check
```

In Docker, `docker-compose.yml` mounts `./backend/fastapi_llm/data` into the
container at `/app/data`, so a host-seeded store (or a
`docker compose run fastapi-llm python populate_chroma.py` with
`HEURISTICS_PATH` pointed at a mounted `datasets/`) is picked up by the
service.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --port 8000          # local
docker build -t ux-insight-llm .      # container (port 5000 in compose)
```

Embeddings use `BAAI/bge-small-en-v1.5` (~130 MB, downloaded on first run).
