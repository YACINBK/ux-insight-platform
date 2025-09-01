#!/usr/bin/env python3
"""
Test script for multi-image handling in the LLM API
"""

import requests
import json

def test_multi_image_llm():
    """Test the LLM API with multiple vision analysis results"""
    
    # Simulate multiple vision analysis results (like what the frontend would send)
    multi_vision_data = [
        {
            "imageName": "screenshot_1.png",
            "imageIndex": 0,
            "classification": {
                "label": "profile",
                "confidence": 0.85
            },
            "detections": [
                {
                    "class": "button",
                    "bbox": [100, 200, 150, 230],
                    "confidence": 0.92
                },
                {
                    "class": "textbox",
                    "bbox": [200, 300, 350, 330],
                    "confidence": 0.88
                }
            ]
        },
        {
            "imageName": "screenshot_2.png", 
            "imageIndex": 1,
            "classification": {
                "label": "menu",
                "confidence": 0.72
            },
            "detections": [
                {
                    "class": "link",
                    "bbox": [50, 100, 120, 120],
                    "confidence": 0.95
                },
                {
                    "class": "heading",
                    "bbox": [100, 50, 300, 80],
                    "confidence": 0.89
                }
            ]
        }
    ]
    
    # Sample tracked data
    tracked_data = [
        {
            "interactionType": "click",
            "elementType": "button",
            "bbox": [100, 200, 150, 230],
            "interactionCount": 3
        },
        {
            "interactionType": "type",
            "elementType": "textbox", 
            "bbox": [200, 300, 350, 330],
            "interactionCount": 1
        }
    ]
    
    # Prepare the request payload
    payload = {
        "question": "Analyze the user interface and provide insights about the user experience across these screenshots",
        "tracked_data": tracked_data,
        "vision": multi_vision_data
    }
    
    print("🧪 Testing multi-image handling...")
    print(f"📊 Sending {len(multi_vision_data)} vision analysis results")
    print(f"📈 Including {len(tracked_data)} tracked data points")
    
    try:
        # Send request to LLM API
        response = requests.post(
            "http://localhost:8000/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Multi-image test successful!")
            print(f"📝 Response length: {len(result.get('answer', ''))} characters")
            print("\n" + "="*50)
            print("LLM RESPONSE:")
            print("="*50)
            print(result.get('answer', 'No answer received'))
            print("="*50)
        else:
            print(f"❌ Test failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    test_multi_image_llm() 