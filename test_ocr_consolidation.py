#!/usr/bin/env python3
"""
Test script for OCR enhancement and data consolidation workflow
Demonstrates the complete pipeline from multiple images to unified analysis
"""

import requests
import json
import time

def test_ocr_enhancement():
    """Test OCR enhancement on a single image"""
    print("🧪 Testing OCR Enhancement...")
    
    # Test with a sample image (you would use actual images in practice)
    test_image_path = "test_image.png"  # Replace with actual image path
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:8001/analyze', files=files)
            
        if response.status_code == 200:
            result = response.json()
            print("✅ OCR enhancement successful!")
            print(f"📊 Enhanced {len(result.get('detections', []))} detections")
            
            # Show enhanced detections
            for i, detection in enumerate(result.get('detections', [])):
                original_class = detection.get('original_class', 'Unknown')
                enhanced_class = detection.get('class', 'Unknown')
                extracted_text = detection.get('extracted_text', '')
                
                print(f"  {i+1}. {original_class} → {enhanced_class}")
                if extracted_text:
                    print(f"     Text: '{extracted_text}'")
            
            return result
        else:
            print(f"❌ OCR enhancement failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return None

def test_consolidation():
    """Test data consolidation with sample data"""
    print("\n🧪 Testing Data Consolidation...")
    
    # Sample vision results (simulating multiple image analysis)
    sample_vision_results = [
        {
            "imageName": "screenshot_1.png",
            "imageIndex": 0,
            "classification": {
                "label": "login",
                "confidence": 0.85
            },
            "detections": [
                {
                    "class": "submit_button",
                    "bbox": [100, 200, 150, 230],
                    "confidence": 0.92,
                    "extracted_text": "Login",
                    "has_text": True
                },
                {
                    "class": "email_input",
                    "bbox": [200, 300, 350, 330],
                    "confidence": 0.88,
                    "extracted_text": "Email",
                    "has_text": True
                }
            ]
        },
        {
            "imageName": "screenshot_2.png",
            "imageIndex": 1,
            "classification": {
                "label": "dashboard",
                "confidence": 0.72
            },
            "detections": [
                {
                    "class": "navigation_link",
                    "bbox": [50, 100, 120, 120],
                    "confidence": 0.95,
                    "extracted_text": "Home",
                    "has_text": True
                },
                {
                    "class": "welcome_heading",
                    "bbox": [100, 50, 300, 80],
                    "confidence": 0.89,
                    "extracted_text": "Welcome Back",
                    "has_text": True
                }
            ]
        }
    ]
    
    # Sample tracked data
    sample_tracked_data = [
        {
            "interactionType": "click",
            "elementType": "submit_button",
            "bbox": [100, 200, 150, 230],
            "interactionCount": 1,
            "imageName": "screenshot_1.png"
        },
        {
            "interactionType": "type",
            "elementType": "email_input",
            "bbox": [200, 300, 350, 330],
            "interactionCount": 1,
            "imageName": "screenshot_1.png"
        },
        {
            "interactionType": "click",
            "elementType": "navigation_link",
            "bbox": [50, 100, 120, 120],
            "interactionCount": 1,
            "imageName": "screenshot_2.png"
        }
    ]
    
    # Test consolidation
    try:
        from consolidator import get_consolidator
        
        consolidator = get_consolidator()
        
        # Consolidate vision data
        consolidated_vision = consolidator.consolidate_vision_data(sample_vision_results)
        print("✅ Vision data consolidation successful!")
        print(f"📊 Total detections: {consolidated_vision['summary']['total_detections']}")
        print(f"🖼️ Screen types: {dict(consolidated_vision['summary']['screen_types'])}")
        
        # Consolidate tracked data
        consolidated_tracked = consolidator.consolidate_tracked_data(sample_tracked_data)
        print("✅ Tracked data consolidation successful!")
        print(f"📈 Total interactions: {consolidated_tracked['summary']['total_interactions']}")
        print(f"🖱️ Interaction types: {dict(consolidated_tracked['summary']['interaction_types'])}")
        
        # Create unified payload
        unified_payload = consolidator.create_unified_analysis_payload(
            sample_vision_results, sample_tracked_data
        )
        print("✅ Unified payload creation successful!")
        print(f"🔗 Element-interaction matches: {unified_payload['element_interaction_mapping']['mapping_statistics']['total_matches']}")
        
        return unified_payload
        
    except Exception as e:
        print(f"❌ Consolidation test failed: {e}")
        return None

def test_complete_pipeline():
    """Test the complete pipeline from multiple images to LLM analysis"""
    print("\n🧪 Testing Complete Pipeline...")
    
    # Step 1: Process multiple images through Vision API with OCR
    vision_results = []
    
    # Simulate processing multiple images
    sample_images = ["screenshot_1.png", "screenshot_2.png"]  # Replace with actual image paths
    
    for i, image_path in enumerate(sample_images):
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                
                # Get detections
                detections_response = requests.post('http://localhost:8001/analyze', files=files)
                if detections_response.status_code == 200:
                    detections_result = detections_response.json()
                
                # Get classification
                f.seek(0)  # Reset file pointer
                classification_response = requests.post('http://localhost:8001/classify_screen', files=files)
                if classification_response.status_code == 200:
                    classification_result = classification_response.json()
                
                # Combine results
                vision_result = {
                    "imageName": image_path,
                    "imageIndex": i,
                    "classification": classification_result,
                    "detections": detections_result.get('detections', [])
                }
                vision_results.append(vision_result)
                print(f"✅ Processed {image_path}")
                
        except Exception as e:
            print(f"⚠️ Failed to process {image_path}: {e}")
    
    # Step 2: Consolidate data
    if vision_results:
        from consolidator import get_consolidator
        consolidator = get_consolidator()
        
        # Sample tracked data (in practice, this would come from JSON files)
        tracked_data = [
            {
                "interactionType": "click",
                "elementType": "submit_button",
                "bbox": [100, 200, 150, 230],
                "interactionCount": 1
            }
        ]
        
        unified_payload = consolidator.create_unified_analysis_payload(vision_results, tracked_data)
        
        # Step 3: Send to LLM API
        llm_payload = {
            "question": "Analyze the user interface and provide insights about the user experience",
            "tracked_data": unified_payload['tracked_data']['all_interactions'],
            "vision": unified_payload['vision']
        }
        
        try:
            llm_response = requests.post('http://localhost:8000/query', json=llm_payload)
            if llm_response.status_code == 200:
                result = llm_response.json()
                print("✅ Complete pipeline successful!")
                print(f"📝 LLM response length: {len(result.get('answer', ''))} characters")
                return result
            else:
                print(f"❌ LLM API failed: {llm_response.status_code}")
                
        except Exception as e:
            print(f"❌ LLM API error: {e}")
    
    return None

def main():
    """Run all tests"""
    print("🚀 Starting OCR and Consolidation Tests...")
    print("=" * 60)
    
    # Test 1: OCR Enhancement
    ocr_result = test_ocr_enhancement()
    
    # Test 2: Data Consolidation
    consolidation_result = test_consolidation()
    
    # Test 3: Complete Pipeline
    pipeline_result = test_complete_pipeline()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"OCR Enhancement: {'✅ PASS' if ocr_result else '❌ FAIL'}")
    print(f"Data Consolidation: {'✅ PASS' if consolidation_result else '❌ FAIL'}")
    print(f"Complete Pipeline: {'✅ PASS' if pipeline_result else '❌ FAIL'}")
    
    if pipeline_result:
        print("\n🎉 All tests passed! The OCR + Consolidation workflow is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 