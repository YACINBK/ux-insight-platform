# Datasets

## heuristics/ux_heuristics.json

The RAG knowledge base for the LLM service: 13 Nielsen-style UX heuristics
(`id`, `text`, `source`), embedded into the ChromaDB `ux_heuristics`
collection by `backend/fastapi_llm/populate_chroma.py`. Every LLM answer in
the platform is grounded in these documents.
