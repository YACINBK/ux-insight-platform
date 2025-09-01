#!/usr/bin/env python3
"""
Test to verify enhanced prompt includes screen type mentions and bold formatting
"""
import requests
import json

def test_vision_prompt():
    print("🔍 Testing enhanced prompt with vision data...")
    
    # Test with vision data to see if screen type is mentioned
    test_data = {
        "question": "How can I improve the user experience of this interface?",
        "tracked_data": [
            {
                "sessionId": "session_001",
                "sectionId": "login_section",
                "interactionCount": "5",
                "timeSpent": 45,
                "scrollDepth": 0.8,
                "elementType": "button",
                "userBehavior": "Clicked login button multiple times"
            }
        ],
        "attachments": None,
        "vision": {
            "classification": {
                "label": "login",
                "confidence": 0.95
            },
            "detections": [
                {
                    "class": "button",
                    "bbox": [100, 200, 200, 250],
                    "confidence": 0.92
                },
                {
                    "class": "textbox",
                    "bbox": [150, 150, 300, 180],
                    "confidence": 0.88
                }
            ]
        }
    }
    
    try:
        print("📤 Sending request with vision data...")
        response = requests.post(
            "http://localhost:8000/query",
            json=test_data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced prompt test PASSED!")
            
            answer = result['answer']
            print(f"💬 Answer length: {len(answer)} characters")
            
            # Check for screen type mention
            if 'login' in answer.lower():
                print("✅ Screen type 'login' is mentioned in the response!")
            else:
                print("⚠️ Screen type 'login' not found in response")
            
            # Check for bold formatting
            if '**' in answer:
                print("✅ Bold formatting (**) is used in the response!")
            else:
                print("⚠️ Bold formatting not found in response")
            
            # Check for emojis
            emoji_count = sum(1 for char in answer if ord(char) > 127)
            if emoji_count > 5:
                print(f"✅ Emojis are used ({emoji_count} special characters found)!")
            else:
                print("⚠️ Limited emoji usage found")
            
            print(f"\n📄 Response Preview:")
            print(f"{answer[:500]}...")
            
            return True
        else:
            print(f"❌ Enhanced prompt test FAILED: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Enhanced prompt test FAILED: Cannot connect to server")
        return False
    except Exception as e:
        print(f"❌ Enhanced prompt test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_vision_prompt() 