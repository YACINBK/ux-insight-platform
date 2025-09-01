#!/usr/bin/env python3
"""
OCR Enhancer for UI Element Classification
Extracts text from detected UI elements to provide more specific classifications
"""

import easyocr
import cv2
import numpy as np
from PIL import Image
import io
from typing import List, Dict, Any, Tuple
import logging

class OCREnhancer:
    def __init__(self):
        """Initialize EasyOCR reader"""
        try:
            self.reader = easyocr.Reader(['en'])  # English only for now
            logging.info("✅ EasyOCR initialized successfully")
        except Exception as e:
            logging.error(f"❌ Failed to initialize EasyOCR: {e}")
            self.reader = None
    
    def extract_text_from_bbox(self, image: np.ndarray, bbox: List[float]) -> str:
        """
        Extract text from a specific bounding box in the image
        
        Args:
            image: numpy array of the image
            bbox: [x1, y1, x2, y2] coordinates
            
        Returns:
            Extracted text string
        """
        if self.reader is None:
            return ""
        
        try:
            # Convert bbox to integers
            x1, y1, x2, y2 = map(int, bbox)
            
            # Ensure coordinates are within image bounds
            height, width = image.shape[:2]
            x1 = max(0, min(x1, width))
            y1 = max(0, min(y1, height))
            x2 = max(0, min(x2, width))
            y2 = max(0, min(y2, height))
            
            # Extract the region
            roi = image[y1:y2, x1:x2]
            
            if roi.size == 0:
                return ""
            
            # Perform OCR on the region
            results = self.reader.readtext(roi)
            
            # Combine all detected text
            text = " ".join([result[1] for result in results])
            return text.strip()
            
        except Exception as e:
            logging.warning(f"OCR extraction failed for bbox {bbox}: {e}")
            return ""
    
    def enhance_element_classification(self, element_class: str, text: str, bbox: List[float]) -> str:
        """
        Enhance element classification based on extracted text and context
        
        Args:
            element_class: Original class from Vision API
            text: Extracted text from OCR
            bbox: Bounding box coordinates
            
        Returns:
            Enhanced, specific classification
        """
        text_lower = text.lower().strip()
        
        # Button classifications
        if element_class == "button":
            if any(word in text_lower for word in ["submit", "login", "sign in", "log in"]):
                return "submit_button"
            elif any(word in text_lower for word in ["cancel", "close", "exit"]):
                return "cancel_button"
            elif any(word in text_lower for word in ["save", "update", "edit"]):
                return "save_button"
            elif any(word in text_lower for word in ["delete", "remove", "trash"]):
                return "delete_button"
            elif any(word in text_lower for word in ["next", "continue", "proceed"]):
                return "next_button"
            elif any(word in text_lower for word in ["back", "previous", "return"]):
                return "back_button"
            elif any(word in text_lower for word in ["search", "find", "lookup"]):
                return "search_button"
            elif any(word in text_lower for word in ["menu", "hamburger", "☰"]):
                return "menu_button"
            elif any(word in text_lower for word in ["home", "main", "dashboard"]):
                return "home_button"
            elif text_lower:
                return f"button_{text_lower.replace(' ', '_')}"
            else:
                return "generic_button"
        
        # Input field classifications
        elif element_class == "textbox" or element_class == "input":
            if any(word in text_lower for word in ["email", "e-mail", "@"]):
                return "email_input"
            elif any(word in text_lower for word in ["password", "pass", "pwd"]):
                return "password_input"
            elif any(word in text_lower for word in ["username", "user", "login"]):
                return "username_input"
            elif any(word in text_lower for word in ["search", "find", "query"]):
                return "search_input"
            elif any(word in text_lower for word in ["name", "full name"]):
                return "name_input"
            elif any(word in text_lower for word in ["phone", "tel", "mobile"]):
                return "phone_input"
            elif any(word in text_lower for word in ["address", "street", "city"]):
                return "address_input"
            elif text_lower:
                return f"input_{text_lower.replace(' ', '_')}"
            else:
                return "generic_input"
        
        # Link classifications
        elif element_class == "link":
            if any(word in text_lower for word in ["home", "main", "dashboard"]):
                return "home_link"
            elif any(word in text_lower for word in ["about", "info", "help"]):
                return "info_link"
            elif any(word in text_lower for word in ["contact", "support", "help"]):
                return "contact_link"
            elif any(word in text_lower for word in ["login", "sign in"]):
                return "login_link"
            elif any(word in text_lower for word in ["register", "sign up", "join"]):
                return "register_link"
            elif any(word in text_lower for word in ["profile", "account", "settings"]):
                return "profile_link"
            elif text_lower:
                return f"link_{text_lower.replace(' ', '_')}"
            else:
                return "generic_link"
        
        # Heading classifications
        elif element_class == "heading":
            if any(word in text_lower for word in ["welcome", "hello", "hi"]):
                return "welcome_heading"
            elif any(word in text_lower for word in ["login", "sign in"]):
                return "login_heading"
            elif any(word in text_lower for word in ["register", "sign up"]):
                return "register_heading"
            elif any(word in text_lower for word in ["profile", "account"]):
                return "profile_heading"
            elif any(word in text_lower for word in ["settings", "preferences"]):
                return "settings_heading"
            elif text_lower:
                return f"heading_{text_lower.replace(' ', '_')}"
            else:
                return "generic_heading"
        
        # Default: return original class if no enhancement possible
        return element_class
    
    def enhance_detections(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance all detections with OCR and improved classifications
        
        Args:
            image: numpy array of the image
            detections: List of detection dictionaries from Vision API
            
        Returns:
            Enhanced detections with specific classifications and extracted text
        """
        enhanced_detections = []
        
        for detection in detections:
            if not isinstance(detection, dict):
                continue
                
            bbox = detection.get('bbox', [])
            original_class = detection.get('class', 'Unknown')
            
            # Extract text from the bounding box
            extracted_text = self.extract_text_from_bbox(image, bbox)
            
            # Enhance classification based on text
            enhanced_class = self.enhance_element_classification(original_class, extracted_text, bbox)
            
            # Create enhanced detection
            enhanced_detection = {
                **detection,
                'class': enhanced_class,
                'original_class': original_class,
                'extracted_text': extracted_text,
                'has_text': bool(extracted_text)
            }
            
            enhanced_detections.append(enhanced_detection)
        
        return enhanced_detections

# Global OCR enhancer instance
ocr_enhancer = None

def get_ocr_enhancer() -> OCREnhancer:
    """Get or create global OCR enhancer instance"""
    global ocr_enhancer
    if ocr_enhancer is None:
        ocr_enhancer = OCREnhancer()
    return ocr_enhancer 