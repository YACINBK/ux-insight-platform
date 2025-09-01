#!/usr/bin/env python3
"""
Test script to verify LLM API with ChromaDB RAG
"""
import requests
import json

def test_llm_api():
    print("Testing LLM API with ChromaDB RAG...")
    
    # Test data
    test_data = {
        "question": "How can I improve user experience on a login page?",
        "tracked_data": None,
        "attachments": None,
        "vision": None
    }
    
    try:
        # Test the API
        response = requests.post(
            "http://localhost:8000/query",
            json=test_data,
            timeout=180  # 3 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM API test PASSED!")
            print(f"📝 Question: {result['question']}")
            print(f"📚 Relevant Context: {len(result['relevant_context'])} documents found")
            print(f"🔗 Sources: {result['sources']}")
            print(f"💬 Answer length: {len(result['answer'])} characters")
            print(f"\n📄 Answer preview: {result['answer'][:200]}...")
            return True
        else:
            print(f"❌ LLM API test FAILED: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ LLM API test FAILED: Cannot connect to server")
        print("Make sure the LLM FastAPI is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ LLM API test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_llm_api() 