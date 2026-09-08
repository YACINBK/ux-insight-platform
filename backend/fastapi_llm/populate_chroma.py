"""
Populate Chroma vector database with UX heuristics from JSON.

Requirements:
    pip install chromadb sentence-transformers

Embedding model options:
    - 'all-MiniLM-L6-v2' (default, small, fast, good for prototyping)
    - 'paraphrase-MiniLM-L6-v2' (alternative, similar size)
    - 'BAAI/bge-small-en-v1.5' (very strong, slightly larger)
    - For multilingual: 'distiluse-base-multilingual-cased-v2'
    - For production, consider OpenAI or other API-based models (requires API key)
"""
import json
import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
# Heuristics dataset: repo-relative default, overridable via HEURISTICS_PATH
DEFAULT_JSON_PATH = Path(__file__).resolve().parents[2] / "datasets" / "heuristics" / "ux_heuristics.json"
JSON_PATH = Path(os.getenv("HEURISTICS_PATH", str(DEFAULT_JSON_PATH)))

# ChromaDB location: same DATA_DIR convention as main.py
DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).parent / "data"))
CHROMA_COLLECTION = "ux_heuristics"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # Change as needed

# --- LOAD HEURISTICS ---
with open(JSON_PATH, "r", encoding="utf-8") as f:
    heuristics = json.load(f)

texts = [h["text"] for h in heuristics]
ids = [h["id"] for h in heuristics]
metadatas = [{"source": h["source"]} for h in heuristics]

# --- GENERATE EMBEDDINGS ---
print(f"Loading embedding model: {EMBEDDING_MODEL}")
embedder = SentenceTransformer(EMBEDDING_MODEL)
embeddings = embedder.encode(texts).tolist()

# --- POPULATE CHROMA ---
client = chromadb.PersistentClient(path=os.path.join(DATA_DIR, "chroma_db"))
# Remove collection if it exists (for idempotency)
try:
    client.delete_collection(CHROMA_COLLECTION)
except Exception:
    pass
collection = client.create_collection(CHROMA_COLLECTION)

collection.add(
    documents=texts,
    embeddings=embeddings,
    ids=ids,
    metadatas=metadatas
)

print(f"Inserted {len(texts)} heuristics into Chroma collection '{CHROMA_COLLECTION}' at {os.path.join(DATA_DIR, 'chroma_db')}")
