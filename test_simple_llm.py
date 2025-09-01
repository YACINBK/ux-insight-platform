#!/usr/bin/env python3
"""
Simple test for LLM API with ChromaDB context
"""
import requests
import json
import time

def test_simple_llm():
    print("🧪 Testing LLM API with ChromaDB context...")
    
    # Simple test question
    test_data = {
        "question": "What are the best practices for user interface design?",
        "tracked_data": None,
        "attachments": None,
        "vision": None
    }
    
    try:
        print("📤 Sending request to LLM API...")
        response = requests.post(
            "http://localhost:8000/query",
            json=test_data,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM API test PASSED!")
            print(f"📝 Question: {result['question']}")
            print(f"📚 ChromaDB Context Found: {len(result['relevant_context'])} documents")
            print(f"🔗 Sources: {result['sources']}")
            print(f"💬 Answer length: {len(result['answer'])} characters")
            
            # Show the ChromaDB context that was used
            print("\n📄 ChromaDB Context Used:")
            for i, context in enumerate(result['relevant_context']):
                print(f"  {i+1}. {context[:150]}...")
            
            print(f"\n💬 Answer Preview:")
            print(f"{result['answer'][:300]}...")
            
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
    test_simple_llm() 