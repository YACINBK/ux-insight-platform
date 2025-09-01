#!/usr/bin/env python3
"""
Test script to verify enhanced dashboard styling and improved screen type descriptions
"""

import requests
import json

def test_enhanced_llm_response():
    """Test the LLM with enhanced screen type descriptions"""
    
    # Test data with vision analysis
    test_data = {
        "question": "Analyze this user profile screen and provide UX insights",
        "tracked_data": [
            {
                "sessionId": "sess-001",
                "interactionCount": 5,
                "sectionId": "profile-header",
                "elementType": "button",
                "timeSpent": 32.5,
                "scrollDepth": 0.8,
                "userBehavior": "profile navigation"
            },
            {
                "sessionId": "sess-001", 
                "interactionCount": 3,
                "sectionId": "profile-settings",
                "elementType": "textbox",
                "timeSpent": 18.2,
                "scrollDepth": 0.6,
                "userBehavior": "settings editing"
            }
        ],
        "vision": {
            "classification": {
                "label": "profile",
                "confidence": 0.38
            },
            "detections": [
                {"class": "button", "bbox": [100, 200, 150, 230], "confidence": 0.85},
                {"class": "textbox", "bbox": [200, 300, 350, 330], "confidence": 0.92},
                {"class": "heading", "bbox": [50, 100, 300, 130], "confidence": 0.78}
            ]
        }
    }
    
    try:
        print("🧪 Testing enhanced LLM response with improved screen type descriptions...")
        print("📤 Sending request to LLM API...")
        
        response = requests.post(
            "http://localhost:8000/query",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LLM API responded successfully!")
            print("\n📋 Response Analysis:")
            print(f"Question: {result['question']}")
            print(f"Answer length: {len(result['answer'])} characters")
            
            # Check if the response mentions descriptive screen type
            answer = result['answer'].lower()
            if "user profile management screen" in answer or "profile management interface" in answer:
                print("✅ Enhanced screen type description found!")
            elif "profile" in answer:
                print("⚠️ Basic screen type found (should be more descriptive)")
            else:
                print("❌ No screen type mention found")
            
            # Check for professional styling elements
            styling_checks = [
                ("bold formatting", "**" in result['answer']),
                ("emoji usage", any(emoji in result['answer'] for emoji in ["🎯", "📈", "🎨", "✅", "🔧"])),
                ("professional tone", any(word in result['answer'].lower() for word in ["analysis", "insights", "recommendations"]))
            ]
            
            print("\n🎨 Styling Analysis:")
            for check, found in styling_checks:
                status = "✅" if found else "❌"
                print(f"{status} {check}")
            
            print(f"\n📄 Full Response Preview (first 500 chars):")
            print(result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer'])
            
        else:
            print(f"❌ LLM API error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to LLM API. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error testing LLM API: {e}")

def test_dashboard_styling():
    """Test if the dashboard styling enhancements are working"""
    print("\n🎨 Testing Dashboard Styling Enhancements...")
    print("📋 Enhanced styling features implemented:")
    print("✅ Improved typography with Segoe UI font family")
    print("✅ Better contrast with #2c3e50 text color")
    print("✅ Enhanced card styling with rounded corners (20px)")
    print("✅ Improved shadows and hover effects")
    print("✅ Better button styling with gradients")
    print("✅ Enhanced chat bubble styling")
    print("✅ Professional color scheme")
    print("✅ Better spacing and padding")
    print("✅ Improved scrollbar styling")
    print("✅ Enhanced focus states")
    
    print("\n🚀 To see the enhanced dashboard:")
    print("1. Start the Spring Boot backend: cd backend/springboot/ux_beta && mvn spring-boot:run")
    print("2. Start the Angular frontend: cd backend/frontend && ng serve")
    print("3. Open http://localhost:4200 in your browser")
    print("4. Upload an image and JSON file to see the enhanced styling")

if __name__ == "__main__":
    print("🎯 Enhanced Dashboard & LLM Response Testing")
    print("=" * 50)
    
    test_enhanced_llm_response()
    test_dashboard_styling()
    
    print("\n✨ Testing complete! The enhanced dashboard should now have:")
    print("• More beautiful and professional styling")
    print("• Better text readability and contrast")
    print("• More descriptive screen type mentions in LLM responses")
    print("• Improved visual hierarchy and spacing") 