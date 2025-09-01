#!/usr/bin/env python3
"""
Data Consolidator for Multi-Image Analysis
Merges multiple vision analysis results and tracked data into unified JSON structures
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
import json
import logging

class DataConsolidator:
    def __init__(self):
        """Initialize the data consolidator"""
        self.logger = logging.getLogger(__name__)
    
    def consolidate_vision_data(self, vision_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate multiple vision analysis results into a unified structure
        
        Args:
            vision_results: List of vision analysis results from multiple images
            
        Returns:
            Consolidated vision data with statistics and unified detections
        """
        if not vision_results:
            return {"error": "No vision results provided"}
        
        consolidated = {
            "summary": {
                "total_images": len(vision_results),
                "total_detections": 0,
                "detection_types": Counter(),
                "screen_types": Counter()
            },
            "overall_classification": {
                "primary_screen": None,
                "confidence": 0.0,
                "secondary_screens": [],
                "screen_distribution": {}
            },
            "all_detections": [],
            "detections_by_type": defaultdict(list),
            "detections_by_image": {},
            "enhanced_elements": {
                "buttons": [],
                "inputs": [],
                "links": [],
                "headings": [],
                "other": []
            }
        }
        
        # Process each vision result
        for i, vision_result in enumerate(vision_results):
            image_name = vision_result.get('imageName', f'Image_{i+1}')
            image_index = vision_result.get('imageIndex', i)
            
            # Track screen classifications
            if 'classification' in vision_result:
                classification = vision_result['classification']
                screen_type = classification.get('label', 'Unknown')
                confidence = classification.get('confidence', 0.0)
                
                consolidated['summary']['screen_types'][screen_type] += 1
                
                # Update overall classification
                if confidence > consolidated['overall_classification']['confidence']:
                    consolidated['overall_classification']['primary_screen'] = screen_type
                    consolidated['overall_classification']['confidence'] = confidence
            
            # Process detections
            if 'detections' in vision_result:
                image_detections = []
                
                for detection in vision_result['detections']:
                    if not isinstance(detection, dict):
                        continue
                    
                    # Add image context to detection
                    enhanced_detection = {
                        **detection,
                        'image_name': image_name,
                        'image_index': image_index
                    }
                    
                    # Track statistics
                    element_class = detection.get('class', 'Unknown')
                    consolidated['summary']['detection_types'][element_class] += 1
                    consolidated['summary']['total_detections'] += 1
                    
                    # Add to various collections
                    consolidated['all_detections'].append(enhanced_detection)
                    consolidated['detections_by_type'][element_class].append(enhanced_detection)
                    image_detections.append(enhanced_detection)
                    
                    # Categorize by enhanced element type
                    self._categorize_element(enhanced_detection, consolidated['enhanced_elements'])
                
                consolidated['detections_by_image'][image_name] = image_detections
        
        # Finalize screen distribution
        total_images = len(vision_results)
        consolidated['overall_classification']['screen_distribution'] = {
            screen_type: count / total_images 
            for screen_type, count in consolidated['summary']['screen_types'].items()
        }
        
        # Get secondary screens (screens with >20% presence)
        secondary_screens = [
            screen_type for screen_type, ratio in consolidated['overall_classification']['screen_distribution'].items()
            if ratio > 0.2 and screen_type != consolidated['overall_classification']['primary_screen']
        ]
        consolidated['overall_classification']['secondary_screens'] = secondary_screens
        
        # Convert defaultdict to regular dict for JSON serialization
        consolidated['detections_by_type'] = dict(consolidated['detections_by_type'])
        
        return consolidated
    
    def consolidate_tracked_data(self, tracked_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate multiple tracked data JSON files into a unified structure
        
        Args:
            tracked_data_list: List of tracked data from multiple JSON files
            
        Returns:
            Consolidated tracked data with statistics and unified interactions
        """
        if not tracked_data_list:
            return {"error": "No tracked data provided"}
        
        consolidated = {
            "summary": {
                "total_interactions": 0,
                "interaction_types": Counter(),
                "element_types": Counter(),
                "sessions": len(tracked_data_list)
            },
            "interactions_by_type": defaultdict(list),
            "interactions_by_element": defaultdict(list),
            "interactions_by_image": defaultdict(list),
            "user_behavior_patterns": {
                "most_clicked_elements": [],
                "interaction_sequences": [],
                "time_spent_patterns": []
            },
            "all_interactions": []
        }
        
        # Process each tracked data entry
        for i, tracked_data in enumerate(tracked_data_list):
            if isinstance(tracked_data, dict):
                # Single interaction
                self._process_single_interaction(tracked_data, consolidated, f"session_{i}")
            elif isinstance(tracked_data, list):
                # Multiple interactions
                for j, interaction in enumerate(tracked_data):
                    if isinstance(interaction, dict):
                        self._process_single_interaction(interaction, consolidated, f"session_{i}_interaction_{j}")
        
        # Calculate statistics
        consolidated['summary']['total_interactions'] = len(consolidated['all_interactions'])
        
        # Find most clicked elements
        element_counts = Counter()
        for interaction in consolidated['all_interactions']:
            element_type = interaction.get('elementType', 'Unknown')
            element_counts[element_type] += interaction.get('interactionCount', 1)
        
        consolidated['user_behavior_patterns']['most_clicked_elements'] = [
            {"element": element, "count": count} 
            for element, count in element_counts.most_common(10)
        ]
        
        # Convert defaultdict to regular dict for JSON serialization
        consolidated['interactions_by_type'] = dict(consolidated['interactions_by_type'])
        consolidated['interactions_by_element'] = dict(consolidated['interactions_by_element'])
        consolidated['interactions_by_image'] = dict(consolidated['interactions_by_image'])
        
        return consolidated
    
    def _process_single_interaction(self, interaction: Dict[str, Any], consolidated: Dict[str, Any], session_id: str):
        """Process a single interaction and add it to the consolidated data"""
        # Add session context
        enhanced_interaction = {
            **interaction,
            'session_id': session_id
        }
        
        # Track statistics
        interaction_type = interaction.get('interactionType', 'Unknown')
        element_type = interaction.get('elementType', 'Unknown')
        image_name = interaction.get('imageName', 'Unknown')
        
        consolidated['summary']['interaction_types'][interaction_type] += 1
        consolidated['summary']['element_types'][element_type] += 1
        
        # Add to collections
        consolidated['all_interactions'].append(enhanced_interaction)
        consolidated['interactions_by_type'][interaction_type].append(enhanced_interaction)
        consolidated['interactions_by_element'][element_type].append(enhanced_interaction)
        consolidated['interactions_by_image'][image_name].append(enhanced_interaction)
    
    def _categorize_element(self, detection: Dict[str, Any], enhanced_elements: Dict[str, List]):
        """Categorize detected element into enhanced categories"""
        element_class = detection.get('class', '').lower()
        
        if 'button' in element_class:
            enhanced_elements['buttons'].append(detection)
        elif any(word in element_class for word in ['input', 'textbox', 'field']):
            enhanced_elements['inputs'].append(detection)
        elif 'link' in element_class:
            enhanced_elements['links'].append(detection)
        elif 'heading' in element_class:
            enhanced_elements['headings'].append(detection)
        else:
            enhanced_elements['other'].append(detection)
    
    def create_unified_analysis_payload(self, 
                                      vision_results: List[Dict[str, Any]], 
                                      tracked_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a unified payload combining vision and tracked data for LLM analysis
        
        Args:
            vision_results: List of vision analysis results
            tracked_data_list: List of tracked data
            
        Returns:
            Unified payload for LLM analysis
        """
        consolidated_vision = self.consolidate_vision_data(vision_results)
        consolidated_tracked = self.consolidate_tracked_data(tracked_data_list)
        
        # Create mapping between detected elements and tracked interactions
        element_interaction_mapping = self._create_element_interaction_mapping(
            consolidated_vision, consolidated_tracked
        )
        
        unified_payload = {
            "vision": consolidated_vision,
            "tracked_data": consolidated_tracked,
            "element_interaction_mapping": element_interaction_mapping,
            "analysis_summary": {
                "total_screenshots": len(vision_results),
                "total_detected_elements": consolidated_vision['summary']['total_detections'],
                "total_user_interactions": consolidated_tracked['summary']['total_interactions'],
                "primary_screen_type": consolidated_vision['overall_classification']['primary_screen'],
                "most_interactive_elements": consolidated_tracked['user_behavior_patterns']['most_clicked_elements'][:5]
            }
        }
        
        return unified_payload
    
    def _create_element_interaction_mapping(self, 
                                          consolidated_vision: Dict[str, Any], 
                                          consolidated_tracked: Dict[str, Any]) -> Dict[str, Any]:
        """Create mapping between detected elements and tracked interactions"""
        mapping = {
            "matched_elements": [],
            "unmatched_detections": [],
            "unmatched_interactions": [],
            "mapping_statistics": {
                "total_matches": 0,
                "match_rate": 0.0
            }
        }
        
        # Simple IoU-based matching (can be enhanced with more sophisticated algorithms)
        for detection in consolidated_vision['all_detections']:
            detection_bbox = detection.get('bbox', [])
            detection_class = detection.get('class', '')
            
            best_match = None
            best_iou = 0.0
            
            for interaction in consolidated_tracked['all_interactions']:
                interaction_bbox = interaction.get('bbox', [])
                interaction_element = interaction.get('elementType', '')
                
                # Calculate IoU if bboxes are available
                if len(detection_bbox) == 4 and len(interaction_bbox) == 4:
                    iou = self._calculate_iou(detection_bbox, interaction_bbox)
                    
                    # Check if classes are compatible
                    if self._classes_compatible(detection_class, interaction_element) and iou > best_iou:
                        best_iou = iou
                        best_match = interaction
            
            if best_match and best_iou > 0.3:  # IoU threshold
                mapping['matched_elements'].append({
                    'detection': detection,
                    'interaction': best_match,
                    'iou_score': best_iou
                })
                mapping['mapping_statistics']['total_matches'] += 1
            else:
                mapping['unmatched_detections'].append(detection)
        
        # Find unmatched interactions
        matched_interaction_ids = {match['interaction'].get('session_id', '') + str(match['interaction'].get('bbox', [])) 
                                 for match in mapping['matched_elements']}
        
        for interaction in consolidated_tracked['all_interactions']:
            interaction_id = interaction.get('session_id', '') + str(interaction.get('bbox', []))
            if interaction_id not in matched_interaction_ids:
                mapping['unmatched_interactions'].append(interaction)
        
        # Calculate match rate
        total_possible_matches = len(consolidated_vision['all_detections'])
        if total_possible_matches > 0:
            mapping['mapping_statistics']['match_rate'] = mapping['mapping_statistics']['total_matches'] / total_possible_matches
        
        return mapping
    
    def _calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Calculate Intersection over Union between two bounding boxes"""
        if len(bbox1) != 4 or len(bbox2) != 4:
            return 0.0
        
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _classes_compatible(self, detection_class: str, interaction_element: str) -> bool:
        """Check if detection class and interaction element type are compatible"""
        detection_lower = detection_class.lower()
        interaction_lower = interaction_element.lower()
        
        # Direct matches
        if detection_lower == interaction_lower:
            return True
        
        # Button variations
        if 'button' in detection_lower and 'button' in interaction_lower:
            return True
        
        # Input variations
        if any(word in detection_lower for word in ['input', 'textbox', 'field']) and \
           any(word in interaction_lower for word in ['input', 'textbox', 'field']):
            return True
        
        # Link variations
        if 'link' in detection_lower and 'link' in interaction_lower:
            return True
        
        return False

# Global consolidator instance
consolidator = None

def get_consolidator() -> DataConsolidator:
    """Get or create global consolidator instance"""
    global consolidator
    if consolidator is None:
        consolidator = DataConsolidator()
    return consolidator 