#!/usr/bin/env python3
"""
Test to verify ChromaDB is working and being used in LLM prompts
"""
import requests
import json

def test_chroma_verification():
    print("🔍 Testing ChromaDB integration with LLM API...")
    
    # Test with a question that should definitely use ChromaDB context
    test_data = {
        "question": "What are the key principles for designing accessible user interfaces?",
        "tracked_data": None,
        "attachments": None,
        "vision": None
    }
    
    try:
        print("📤 Sending request to LLM API...")
        response = requests.post(
            "http://localhost:8000/query",
            json=test_data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM API test PASSED!")
            
            # Check if ChromaDB context was used
            if result['relevant_context'] and len(result['relevant_context']) > 0:
                print("✅ ChromaDB context IS being used!")
                print(f"📚 Found {len(result['relevant_context'])} relevant documents")
                print(f"🔗 Sources: {result['sources']}")
                
                print("\n📄 ChromaDB Context Used:")
                for i, context in enumerate(result['relevant_context']):
                    print(f"  {i+1}. {context[:150]}...")
                
                # Check if the answer mentions accessibility (should be in ChromaDB context)
                answer_lower = result['answer'].lower()
                if 'accessibility' in answer_lower or 'accessible' in answer_lower:
                    print("✅ Answer contains accessibility content from ChromaDB!")
                else:
                    print("⚠️ Answer doesn't seem to contain accessibility content")
                
                print(f"\n💬 Answer Preview:")
                print(f"{result['answer'][:300]}...")
                
                return True
            else:
                print("❌ ChromaDB context NOT found in response!")
                print(f"Relevant context: {result['relevant_context']}")
                return False
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
    test_chroma_verification() 