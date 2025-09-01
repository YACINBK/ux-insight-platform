"""
Test script to verify Chroma population and retrieval.
"""
import chromadb
from sentence_transformers import SentenceTransformer

# Load the same embedding model used for population
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
embedder = SentenceTransformer(EMBEDDING_MODEL)

# Connect to Chroma
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("ux_heuristics")

# Test queries
test_queries = [
    "How should I design error messages?",
    "What makes a good list interface?",
    "How to ensure accessibility?",
    "What feedback should users get?"
]

print("=== Testing Chroma Retrieval ===\n")

for query in test_queries:
    print(f"Query: {query}")
    
    # Generate embedding for the query
    query_embedding = embedder.encode([query]).tolist()
    
    # Search for similar documents
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )
    
    print("Top matches:")
    for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"  {i+1}. {doc[:100]}... (Source: {metadata['source']})")
    print("-" * 80)

# Show collection info
print(f"\nCollection contains {collection.count()} documents") 