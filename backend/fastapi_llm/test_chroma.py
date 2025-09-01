#!/usr/bin/env python3
"""
Test script to verify ChromaDB RAG functionality
"""
import chromadb
from sentence_transformers import SentenceTransformer
import json

def test_chroma_rag():
    print("Testing ChromaDB RAG functionality...")
    
    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("ux_heuristics")
        embedder = SentenceTransformer('BAAI/bge-small-en-v1.5')
        
        print("✅ ChromaDB client initialized")
        print("✅ Collection 'ux_heuristics' loaded")
        print("✅ Embedding model loaded")
        
        # Test query
        test_question = "How can I improve user experience on a login page?"
        print(f"\n🔍 Testing query: '{test_question}'")
        
        # Generate embedding
        question_embedding = embedder.encode([test_question]).tolist()
        print("✅ Question embedded successfully")
        
        # Vector search
        results = collection.query(
            query_embeddings=question_embedding,
            n_results=3
        )
        
        docs = results["documents"][0]
        metadata = results["metadatas"][0]
        
        print(f"✅ Found {len(docs)} relevant documents")
        print("\n📄 Retrieved documents:")
        for i, (doc, meta) in enumerate(zip(docs, metadata)):
            print(f"  {i+1}. {doc[:100]}... (Source: {meta.get('source', 'Unknown')})")
        
        print("\n🎉 ChromaDB RAG test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB RAG test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chroma_rag() 