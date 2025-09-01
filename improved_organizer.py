#!/usr/bin/env python3
"""
Improved Dataset Organization Script for YOLOv8 UI Element Detection
Addresses class imbalance and annotation quality issues
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import random
from collections import defaultdict
from PIL import Image
import numpy as np

class ImprovedUIElementDetector:
    """Improved class to handle UI element detection with better classification"""
    
    def __init__(self):
        # Reduced and more focused UI element classes
        self.ui_classes = {
            'button': 0,
            'text': 1, 
            'input': 2,
            'image': 3,
            'container': 4,
            'navigation': 5,
            'checkbox': 6,
            'radio': 7,
            'slider': 8,
            'progress': 9,
            'toolbar': 10,
            'card': 11,
            'list_item': 12,
            'webview': 13,
            'ad': 14
        }
        
        # Improved mapping with more specific classification
        self.class_mapping = {
            # Buttons - more specific
            'android.widget.Button': 'button',
            'android.widget.ImageButton': 'button',
            'android.support.v7.widget.AppCompatButton': 'button',
            'android.support.v7.widget.AppCompatImageButton': 'button',
            'android.support.design.widget.FloatingActionButton': 'button',
            'com.google.android.gms.plus.PlusOneButton': 'button',
            'com.kakao.usermgmt.LoginButton': 'button',
            'com.path.base.views.widget.PartlyRoundedButton': 'button',
            'android.widget.ActionMenuPresenter$OverflowMenuButton': 'button',
            
            # Text elements - more specific
            'android.widget.TextView': 'text',
            'android.support.v7.widget.AppCompatTextView': 'text',
            'com.global.foodpanda.android.custom.views.FoodPandaTextView': 'text',
            'com.twoergo.foxbusinessnews.widget.FBNTextView': 'text',
            'com.google.android.finsky.layout.LinkTextView': 'text',
            'com.bbva.compassBuzz.commons.ui.widget.CustomTextView': 'text',
            
            # Input fields
            'android.widget.EditText': 'input',
            'android.support.v7.widget.AppCompatEditText': 'input',
            'android.widget.AutoCompleteTextView': 'input',
            'android.widget.MultiAutoCompleteTextView': 'input',
            
            # Images - more specific
            'android.widget.ImageView': 'image',
            'android.support.v7.widget.AppCompatImageView': 'image',
            
            # Containers - more restrictive
            'android.widget.FrameLayout': 'container',
            'android.widget.LinearLayout': 'container',
            'android.widget.RelativeLayout': 'container',
            'android.widget.ScrollView': 'container',
            'android.widget.HorizontalScrollView': 'container',
            'android.widget.GridView': 'container',
            'android.widget.GridLayout': 'container',
            'android.widget.TableLayout': 'container',
            'android.widget.TableRow': 'container',
            
            # Navigation - more specific
            'android.widget.TabHost': 'navigation',
            'android.support.design.widget.BottomNavigationView': 'navigation',
            'android.support.design.widget.NavigationView': 'navigation',
            
            # Toolbars
            'android.support.v7.widget.Toolbar': 'toolbar',
            'android.widget.ActionMenuView': 'toolbar',
            
            # Interactive elements
            'android.widget.CheckBox': 'checkbox',
            'android.widget.RadioButton': 'radio',
            'android.widget.RadioGroup': 'radio',
            'android.widget.SeekBar': 'slider',
            'android.widget.ProgressBar': 'progress',
            'android.widget.Switch': 'checkbox',
            'android.widget.ToggleButton': 'checkbox',
            
            # Cards and lists
            'android.support.v7.widget.CardView': 'card',
            'android.widget.ListView': 'list_item',
            'android.widget.RecyclerView': 'list_item',
            'android.support.v7.widget.RecyclerView': 'list_item',
            'android.widget.ExpandableListView': 'list_item',
            
            # Web and media
            'android.webkit.WebView': 'webview',
            'org.apache.cordova.engine.SystemWebView': 'webview',
            
            # Ads
            'com.google.android.gms.ads.AdView': 'ad',
            'com.facebook.ads.AdView': 'ad',
        }
    
    def get_image_dimensions(self, image_path: str) -> Tuple[int, int]:
        """Get actual image dimensions using PIL"""
        try:
            with Image.open(image_path) as img:
                return img.size  # Returns (width, height)
        except Exception as e:
            print(f"Warning: Could not get dimensions for {image_path}: {e}")
            # Fallback to common Android resolution
            return 1440, 2560
    
    def convert_bounds_to_yolo(self, bounds: List[int], img_width: int, img_height: int) -> Tuple[float, float, float, float]:
        """Convert Android bounds [x1, y1, x2, y2] to YOLO format [x_center, y_center, width, height] (normalized)"""
        x1, y1, x2, y2 = bounds
        
        # Calculate center and dimensions
        x_center = (x1 + x2) / 2.0
        y_center = (y1 + y2) / 2.0
        width = x2 - x1
        height = y2 - y1
        
        # Normalize to [0, 1]
        x_center_norm = x_center / img_width
        y_center_norm = y_center / img_height
        width_norm = width / img_width
        height_norm = height / img_height
        
        # Validate bounds
        if (x_center_norm < 0 or x_center_norm > 1 or 
            y_center_norm < 0 or y_center_norm > 1 or
            width_norm <= 0 or height_norm <= 0):
            return None
        
        return x_center_norm, y_center_norm, width_norm, height_norm
    
    def is_meaningful_element(self, node: Dict, bounds: List[int], img_width: int, img_height: int) -> bool:
        """Check if element is meaningful for training"""
        if not bounds or len(bounds) != 4:
            return False
        
        # Calculate area
        area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
        total_area = img_width * img_height
        area_ratio = area / total_area
        
        # Filter out elements that are too small or too large
        if area_ratio < 0.0001:  # Too small (less than 0.01% of image)
            return False
        
        if area_ratio > 0.8:  # Too large (more than 80% of image)
            return False
        
        # Check element properties
        is_clickable = node.get('clickable', False)
        is_focusable = node.get('focusable', False)
        has_text = bool(node.get('text', '').strip())
        has_content_desc = bool(node.get('content-desc', [None])[0])
        is_visible = node.get('visible-to-user', True)
        
        # Keep elements that are interactive or have content
        if is_clickable or is_focusable or has_text or has_content_desc:
            return True
        
        # Keep visible elements that are not just background
        if is_visible and area_ratio < 0.5:
            return True
        
        return False
    
    def classify_element(self, node: Dict) -> Optional[str]:
        """Enhanced element classification based on class and properties"""
        if 'class' not in node:
            return None
        
        android_class = node['class']
        
        # Direct mapping
        if android_class in self.class_mapping:
            return self.class_mapping[android_class]
        
        # Enhanced classification based on properties
        is_clickable = node.get('clickable', False)
        is_focusable = node.get('focusable', False)
        has_text = bool(node.get('text', '').strip())
        has_content_desc = bool(node.get('content-desc', [None])[0])
        
        # Classify based on properties
        if is_clickable and (has_text or has_content_desc):
            return 'button'
        elif has_text or has_content_desc:
            return 'text'
        elif is_clickable:
            return 'button'
        elif android_class.endswith('View') and not android_class.endswith('ImageView'):
            return 'container'
        
        return None
    
    def extract_ui_elements(self, json_data: Dict, img_width: int, img_height: int) -> List[Tuple[str, List[int], Dict]]:
        """Extract UI elements with improved filtering"""
        elements = []
        
        def traverse_node(node, depth=0):
            if isinstance(node, dict):
                # Check if this is a UI element
                if 'bounds' in node and len(node['bounds']) == 4:
                    bounds = node['bounds']
                    
                    # Check if element is meaningful
                    if self.is_meaningful_element(node, bounds, img_width, img_height):
                        ui_class = self.classify_element(node)
                        if ui_class:
                            elements.append((ui_class, bounds, node))
                
                # Traverse children (limit depth to avoid too many nested elements)
                if 'children' in node and depth < 8:  # Reduced depth limit
                    for child in node['children']:
                        traverse_node(child, depth + 1)
        
        # Start traversal from root
        if 'activity' in json_data and 'root' in json_data['activity']:
            traverse_node(json_data['activity']['root'])
        
        return elements
    
    def filter_overlapping_elements(self, elements: List[Tuple[str, List[int], Dict]], overlap_threshold: float = 0.7) -> List[Tuple[str, List[int], Dict]]:
        """Filter out overlapping elements with stricter threshold"""
        if not elements:
            return elements
        
        # Sort by area (largest first)
        def get_area(bounds):
            return (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
        
        sorted_elements = sorted(elements, key=lambda x: get_area(x[1]), reverse=True)
        filtered_elements = []
        
        for element in sorted_elements:
            ui_class, bounds, node = element
            
            # Check overlap with already selected elements
            is_overlapping = False
            for existing_element in filtered_elements:
                existing_bounds = existing_element[1]
                
                # Calculate intersection
                x1 = max(bounds[0], existing_bounds[0])
                y1 = max(bounds[1], existing_bounds[1])
                x2 = min(bounds[2], existing_bounds[2])
                y2 = min(bounds[3], existing_bounds[3])
                
                if x1 < x2 and y1 < y2:
                    intersection = (x2 - x1) * (y2 - y1)
                    area1 = get_area(bounds)
                    area2 = get_area(existing_bounds)
                    smaller_area = min(area1, area2)
                    
                    if intersection / smaller_area > overlap_threshold:
                        is_overlapping = True
                        break
            
            if not is_overlapping:
                filtered_elements.append(element)
        
        return filtered_elements
    
    def create_yolo_annotation(self, elements: List[Tuple[str, List[int], Dict]], img_width: int, img_height: int) -> List[str]:
        """Create YOLO format annotation lines with improved filtering"""
        yolo_lines = []
        
        # Filter overlapping elements
        filtered_elements = self.filter_overlapping_elements(elements)
        
        for ui_class, bounds, node in filtered_elements:
            if ui_class in self.ui_classes:
                class_id = self.ui_classes[ui_class]
                yolo_coords = self.convert_bounds_to_yolo(bounds, img_width, img_height)
                
                if yolo_coords:
                    x_center, y_center, width, height = yolo_coords
                    
                    # Additional validation
                    if width > 0.9 or height > 0.9:  # Skip very large elements
                        continue
                    
                    if width < 0.01 or height < 0.01:  # Skip very small elements
                        continue
                    
                    # Format: class_id x_center y_center width height
                    yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                    yolo_lines.append(yolo_line)
        
        return yolo_lines

def create_yolo_structure(base_path: str):
    """Create YOLO directory structure"""
    yolo_dirs = [
        'improved_yolo_dataset',
        'improved_yolo_dataset/images',
        'improved_yolo_dataset/images/train',
        'improved_yolo_dataset/images/val',
        'improved_yolo_dataset/images/test',
        'improved_yolo_dataset/labels',
        'improved_yolo_dataset/labels/train',
        'improved_yolo_dataset/labels/val',
        'improved_yolo_dataset/labels/test'
    ]
    
    for dir_path in yolo_dirs:
        Path(os.path.join(base_path, dir_path)).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def split_dataset(file_list: List[str], train_ratio: float = 0.7, val_ratio: float = 0.2, test_ratio: float = 0.1):
    """Split dataset into train/val/test sets"""
    random.shuffle(file_list)
    
    total_files = len(file_list)
    train_end = int(total_files * train_ratio)
    val_end = train_end + int(total_files * val_ratio)
    
    train_files = file_list[:train_end]
    val_files = file_list[train_end:val_end]
    test_files = file_list[val_end:]
    
    return train_files, val_files, test_files

def process_dataset(combined_dir: str, output_dir: str, train_ratio: float = 0.7, val_ratio: float = 0.2, test_ratio: float = 0.1):
    """Main function to process the dataset with improvements"""
    
    # Create YOLO structure
    create_yolo_structure(output_dir)
    
    # Initialize detector
    detector = ImprovedUIElementDetector()
    
    # Get all JSON files
    json_files = [f for f in os.listdir(combined_dir) if f.endswith('.json')]
    print(f"Found {len(json_files)} JSON files")
    
    # Split dataset
    train_files, val_files, test_files = split_dataset(json_files, train_ratio, val_ratio, test_ratio)
    
    splits = {
        'train': train_files,
        'val': val_files, 
        'test': test_files
    }
    
    # Statistics
    stats = {
        'total_processed': 0,
        'total_elements': 0,
        'class_counts': defaultdict(int),
        'errors': 0,
        'filtered_out': 0
    }
    
    # Process each split
    for split_name, files in splits.items():
        print(f"\nProcessing {split_name} split ({len(files)} files)...")
        
        for json_file in files:
            try:
                # Load JSON data
                json_path = os.path.join(combined_dir, json_file)
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                
                # Get corresponding image file
                image_file = json_file.replace('.json', '.jpg')
                image_path = os.path.join(combined_dir, image_file)
                
                if not os.path.exists(image_path):
                    print(f"Warning: Image {image_file} not found for {json_file}")
                    continue
                
                # Get actual image dimensions
                img_width, img_height = detector.get_image_dimensions(image_path)
                
                # Extract UI elements
                elements = detector.extract_ui_elements(json_data, img_width, img_height)
                
                if not elements:
                    stats['filtered_out'] += 1
                    continue
                
                # Create YOLO annotations
                yolo_lines = detector.create_yolo_annotation(elements, img_width, img_height)
                
                if not yolo_lines:
                    stats['filtered_out'] += 1
                    continue
                
                # Update statistics
                stats['total_processed'] += 1
                stats['total_elements'] += len(yolo_lines)
                
                for line in yolo_lines:
                    class_id = int(line.split()[0])
                    class_name = list(detector.ui_classes.keys())[class_id]
                    stats['class_counts'][class_name] += 1
                
                # Copy image
                dest_image_path = os.path.join(output_dir, 'improved_yolo_dataset', 'images', split_name, image_file)
                shutil.copy2(image_path, dest_image_path)
                
                # Write YOLO annotation
                annotation_file = json_file.replace('.json', '.txt')
                dest_annotation_path = os.path.join(output_dir, 'improved_yolo_dataset', 'labels', split_name, annotation_file)
                
                with open(dest_annotation_path, 'w') as f:
                    f.write('\n'.join(yolo_lines))
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                stats['errors'] += 1
                continue
    
    # Create dataset.yaml file
    create_dataset_yaml(output_dir, detector.ui_classes)
    
    # Print statistics
    print(f"\nDataset processing complete!")
    print(f"Output directory: {os.path.join(output_dir, 'improved_yolo_dataset')}")
    print(f"\nStatistics:")
    print(f"Total images processed: {stats['total_processed']}")
    print(f"Total UI elements detected: {stats['total_elements']}")
    print(f"Average elements per image: {stats['total_elements'] / max(stats['total_processed'], 1):.2f}")
    print(f"Errors: {stats['errors']}")
    print(f"Filtered out (no meaningful elements): {stats['filtered_out']}")
    print(f"\nClass distribution:")
    for class_name, count in sorted(stats['class_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {class_name}: {count}")

def create_dataset_yaml(output_dir: str, ui_classes: Dict[str, int]):
    """Create dataset.yaml file for YOLOv8"""
    yaml_content = f"""# YOLOv8 UI Element Detection Dataset (Improved)
path: {os.path.abspath(os.path.join(output_dir, 'improved_yolo_dataset'))}
train: images/train
val: images/val
test: images/test

# Classes
nc: {len(ui_classes)}
names: {list(ui_classes.keys())}
"""
    
    yaml_path = os.path.join(output_dir, 'improved_yolo_dataset', 'dataset.yaml')
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"Created dataset.yaml: {yaml_path}")

def main():
    parser = argparse.ArgumentParser(description='Improved UI dataset organization for YOLOv8 training')
    parser.add_argument('--input', default='combined', help='Input directory containing images and JSON files')
    parser.add_argument('--output', default='improved_dataset', help='Output directory for improved YOLO dataset')
    parser.add_argument('--train-ratio', type=float, default=0.7, help='Training set ratio')
    parser.add_argument('--val-ratio', type=float, default=0.2, help='Validation set ratio')
    parser.add_argument('--test-ratio', type=float, default=0.1, help='Test set ratio')
    
    args = parser.parse_args()
    
    # Validate ratios
    total_ratio = args.train_ratio + args.val_ratio + args.test_ratio
    if abs(total_ratio - 1.0) > 0.01:
        print("Warning: Ratios don't sum to 1.0, normalizing...")
        args.train_ratio /= total_ratio
        args.val_ratio /= total_ratio
        args.test_ratio /= total_ratio
    
    process_dataset(args.input, args.output, args.train_ratio, args.val_ratio, args.test_ratio)

if __name__ == "__main__":
    main() 