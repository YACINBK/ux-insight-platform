#!/usr/bin/env python3
"""
Dataset Organization Script for YOLOv8 UI Element Detection
Converts Android UI dataset to YOLO format with proper directory structure
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import random
from collections import defaultdict

class UIElementDetector:
    """Class to handle UI element detection and YOLO annotation conversion"""
    
    def __init__(self):
        # Define UI element classes for YOLO training
        self.ui_classes = {
            'button': 0,
            'text': 1, 
            'input': 2,
            'image': 3,
            'container': 4,
            'navigation': 5,
            'icon': 6,
            'checkbox': 7,
            'radio': 8,
            'slider': 9,
            'progress': 10,
            'tab': 11,
            'menu': 12,
            'toolbar': 13,
            'card': 14,
            'list_item': 15
        }
        
        # Mapping from Android classes to our UI classes
        self.class_mapping = {
            # Buttons
            'android.widget.Button': 'button',
            'android.widget.ImageButton': 'button',
            'android.support.v7.widget.AppCompatButton': 'button',
            'android.support.v7.widget.AppCompatImageButton': 'button',
            'android.support.design.widget.FloatingActionButton': 'button',
            'com.google.android.gms.plus.PlusOneButton': 'button',
            'com.kakao.usermgmt.LoginButton': 'button',
            'com.path.base.views.widget.PartlyRoundedButton': 'button',
            
            # Text elements
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
            
            # Images
            'android.widget.ImageView': 'image',
            'android.support.v7.widget.AppCompatImageView': 'image',
            
            # Containers
            'android.widget.FrameLayout': 'container',
            'android.widget.LinearLayout': 'container',
            'android.widget.RelativeLayout': 'container',
            'android.widget.ScrollView': 'container',
            'android.widget.ListView': 'container',
            'android.widget.RecyclerView': 'container',
            'android.support.v7.widget.RecyclerView': 'container',
            
            # Navigation
            'android.widget.TabHost': 'navigation',
            'android.support.design.widget.BottomNavigationView': 'navigation',
            'android.support.v7.widget.Toolbar': 'toolbar',
            'android.widget.ActionMenuView': 'menu',
            
            # Interactive elements
            'android.widget.CheckBox': 'checkbox',
            'android.widget.RadioButton': 'radio',
            'android.widget.SeekBar': 'slider',
            'android.widget.ProgressBar': 'progress',
            
            # Cards and lists
            'android.support.v7.widget.CardView': 'card',
            'android.widget.ListView': 'list_item',
        }
    
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
        
        return x_center_norm, y_center_norm, width_norm, height_norm
    
    def extract_ui_elements(self, json_data: Dict) -> List[Tuple[str, List[int]]]:
        """Extract UI elements and their bounds from JSON data"""
        elements = []
        
        def traverse_node(node):
            if isinstance(node, dict):
                # Check if this is a UI element
                if 'class' in node and 'bounds' in node:
                    android_class = node['class']
                    bounds = node['bounds']
                    
                    # Map to our UI class
                    if android_class in self.class_mapping:
                        ui_class = self.class_mapping[android_class]
                        elements.append((ui_class, bounds))
                
                # Traverse children
                if 'children' in node:
                    for child in node['children']:
                        traverse_node(child)
        
        # Start traversal from root
        if 'activity' in json_data and 'root' in json_data['activity']:
            traverse_node(json_data['activity']['root'])
        
        return elements
    
    def create_yolo_annotation(self, elements: List[Tuple[str, List[int]]], img_width: int, img_height: int) -> List[str]:
        """Create YOLO format annotation lines"""
        yolo_lines = []
        
        for ui_class, bounds in elements:
            if ui_class in self.ui_classes:
                class_id = self.ui_classes[ui_class]
                x_center, y_center, width, height = self.convert_bounds_to_yolo(bounds, img_width, img_height)
                
                # Format: class_id x_center y_center width height
                yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                yolo_lines.append(yolo_line)
        
        return yolo_lines

def create_yolo_structure(base_path: str):
    """Create YOLO directory structure"""
    yolo_dirs = [
        'yolo_dataset',
        'yolo_dataset/images',
        'yolo_dataset/images/train',
        'yolo_dataset/images/val',
        'yolo_dataset/images/test',
        'yolo_dataset/labels',
        'yolo_dataset/labels/train',
        'yolo_dataset/labels/val',
        'yolo_dataset/labels/test'
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
    """Main function to process the dataset"""
    
    # Create YOLO structure
    create_yolo_structure(output_dir)
    
    # Initialize detector
    detector = UIElementDetector()
    
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
                
                # Extract UI elements
                elements = detector.extract_ui_elements(json_data)
                
                if not elements:
                    print(f"Warning: No UI elements found in {json_file}")
                    continue
                
                # Get image dimensions (you might want to use PIL to get actual dimensions)
                # For now, using common Android screen dimensions
                img_width, img_height = 1440, 2560  # Common Android resolution
                
                # Create YOLO annotations
                yolo_lines = detector.create_yolo_annotation(elements, img_width, img_height)
                
                if not yolo_lines:
                    continue
                
                # Copy image
                dest_image_path = os.path.join(output_dir, 'yolo_dataset', 'images', split_name, image_file)
                shutil.copy2(image_path, dest_image_path)
                
                # Write YOLO annotation
                annotation_file = json_file.replace('.json', '.txt')
                dest_annotation_path = os.path.join(output_dir, 'yolo_dataset', 'labels', split_name, annotation_file)
                
                with open(dest_annotation_path, 'w') as f:
                    f.write('\n'.join(yolo_lines))
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                continue
    
    # Create dataset.yaml file
    create_dataset_yaml(output_dir, detector.ui_classes)
    
    print(f"\nDataset processing complete!")
    print(f"Output directory: {os.path.join(output_dir, 'yolo_dataset')}")

def create_dataset_yaml(output_dir: str, ui_classes: Dict[str, int]):
    """Create dataset.yaml file for YOLOv8"""
    yaml_content = f"""# YOLOv8 UI Element Detection Dataset
path: {os.path.abspath(os.path.join(output_dir, 'yolo_dataset'))}
train: images/train
val: images/val
test: images/test

# Classes
nc: {len(ui_classes)}
names: {list(ui_classes.keys())}
"""
    
    yaml_path = os.path.join(output_dir, 'yolo_dataset', 'dataset.yaml')
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"Created dataset.yaml: {yaml_path}")

def main():
    parser = argparse.ArgumentParser(description='Organize UI dataset for YOLOv8 training')
    parser.add_argument('--input', default='combined', help='Input directory containing images and JSON files')
    parser.add_argument('--output', default='organized_dataset', help='Output directory for YOLO dataset')
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