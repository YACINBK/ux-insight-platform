#!/usr/bin/env python3
"""
Dataset Analysis Script for Android UI Dataset
Analyzes the current dataset structure and provides insights before YOLO organization
"""

import os
import json
import argparse
from collections import defaultdict, Counter
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import numpy as np

class DatasetAnalyzer:
    """Analyzes Android UI dataset structure and content"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.stats = {
            'total_files': 0,
            'image_files': 0,
            'json_files': 0,
            'matched_pairs': 0,
            'app_categories': Counter(),
            'ui_classes': Counter(),
            'element_properties': defaultdict(int),
            'screen_resolutions': Counter(),
            'element_depths': [],
            'element_areas': []
        }
    
    def analyze_dataset(self):
        """Main analysis function"""
        print("🔍 Analyzing Android UI Dataset...")
        print("=" * 50)
        
        # Get all files
        all_files = os.listdir(self.dataset_path)
        self.stats['total_files'] = len(all_files)
        
        # Count file types
        image_files = [f for f in all_files if f.endswith('.jpg')]
        json_files = [f for f in all_files if f.endswith('.json')]
        
        self.stats['image_files'] = len(image_files)
        self.stats['json_files'] = len(json_files)
        
        print(f"📊 File Statistics:")
        print(f"   Total files: {self.stats['total_files']}")
        print(f"   Image files: {self.stats['image_files']}")
        print(f"   JSON files: {self.stats['json_files']}")
        
        # Check for matched pairs
        image_bases = {f.replace('.jpg', '') for f in image_files}
        json_bases = {f.replace('.json', '') for f in json_files}
        matched_bases = image_bases.intersection(json_bases)
        self.stats['matched_pairs'] = len(matched_bases)
        
        print(f"   Matched pairs: {self.stats['matched_pairs']}")
        print(f"   Unmatched images: {len(image_bases - json_bases)}")
        print(f"   Unmatched JSONs: {len(json_bases - image_bases)}")
        
        # Analyze JSON files
        print(f"\n📋 Analyzing JSON annotations...")
        self.analyze_json_files(json_files[:1000])  # Sample first 1000 for speed
        
        # Print summary
        self.print_summary()
        
        # Generate visualizations
        self.generate_visualizations()
    
    def analyze_json_files(self, json_files: List[str]):
        """Analyze JSON annotation files"""
        processed = 0
        
        for json_file in json_files:
            try:
                json_path = os.path.join(self.dataset_path, json_file)
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                # Extract app category
                if 'activity_name' in data:
                    app_name = data['activity_name'].split('/')[0]
                    self.stats['app_categories'][app_name] += 1
                
                # Analyze UI elements
                if 'activity' in data and 'root' in data['activity']:
                    self.analyze_ui_elements(data['activity']['root'])
                
                processed += 1
                if processed % 100 == 0:
                    print(f"   Processed {processed} files...")
                    
            except Exception as e:
                print(f"   Error processing {json_file}: {e}")
                continue
    
    def analyze_ui_elements(self, node: Dict, depth: int = 0):
        """Recursively analyze UI elements"""
        if isinstance(node, dict):
            # Track element depth
            self.stats['element_depths'].append(depth)
            
            # Count UI classes
            if 'class' in node:
                android_class = node['class']
                self.stats['ui_classes'][android_class] += 1
            
            # Analyze properties
            for prop in ['clickable', 'focusable', 'enabled', 'visible-to-user']:
                if prop in node:
                    self.stats['element_properties'][f"{prop}:{node[prop]}"] += 1
            
            # Analyze bounds and area
            if 'bounds' in node and len(node['bounds']) == 4:
                bounds = node['bounds']
                area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
                self.stats['element_areas'].append(area)
            
            # Track screen resolution
            if 'bounds' in node and len(node['bounds']) == 4:
                bounds = node['bounds']
                resolution = f"{bounds[2]}x{bounds[3]}"
                self.stats['screen_resolutions'][resolution] += 1
            
            # Recursively analyze children
            if 'children' in node and depth < 10:  # Limit depth to avoid infinite recursion
                for child in node['children']:
                    self.analyze_ui_elements(child, depth + 1)
    
    def print_summary(self):
        """Print analysis summary"""
        print(f"\n📈 Analysis Summary:")
        print("=" * 50)
        
        # Top app categories
        print(f"\n🏆 Top 10 App Categories:")
        for app, count in self.stats['app_categories'].most_common(10):
            print(f"   {app}: {count}")
        
        # Top UI classes
        print(f"\n🎯 Top 15 UI Element Classes:")
        for ui_class, count in self.stats['ui_classes'].most_common(15):
            print(f"   {ui_class}: {count}")
        
        # Element properties
        print(f"\n⚙️  Element Properties:")
        for prop, count in sorted(self.stats['element_properties'].items())[:10]:
            print(f"   {prop}: {count}")
        
        # Screen resolutions
        print(f"\n📱 Screen Resolutions:")
        for res, count in self.stats['screen_resolutions'].most_common(5):
            print(f"   {res}: {count}")
        
        # Element statistics
        if self.stats['element_areas']:
            areas = np.array(self.stats['element_areas'])
            print(f"\n📏 Element Area Statistics:")
            print(f"   Mean area: {np.mean(areas):.0f}")
            print(f"   Median area: {np.median(areas):.0f}")
            print(f"   Min area: {np.min(areas):.0f}")
            print(f"   Max area: {np.max(areas):.0f}")
        
        if self.stats['element_depths']:
            depths = np.array(self.stats['element_depths'])
            print(f"\n🌳 Element Depth Statistics:")
            print(f"   Mean depth: {np.mean(depths):.2f}")
            print(f"   Max depth: {np.max(depths)}")
            print(f"   Depth distribution: {dict(Counter(depths))}")
    
    def generate_visualizations(self):
        """Generate visualization plots"""
        try:
            # Set up the plotting style
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Android UI Dataset Analysis', fontsize=16, fontweight='bold')
            
            # 1. Top app categories
            top_apps = dict(self.stats['app_categories'].most_common(10))
            axes[0, 0].barh(list(top_apps.keys()), list(top_apps.values()))
            axes[0, 0].set_title('Top 10 App Categories')
            axes[0, 0].set_xlabel('Count')
            
            # 2. Top UI classes
            top_classes = dict(self.stats['ui_classes'].most_common(10))
            class_names = [cls.split('.')[-1] for cls in top_classes.keys()]
            axes[0, 1].barh(class_names, list(top_classes.values()))
            axes[0, 1].set_title('Top 10 UI Element Classes')
            axes[0, 1].set_xlabel('Count')
            
            # 3. Element area distribution
            if self.stats['element_areas']:
                areas = np.array(self.stats['element_areas'])
                # Log scale for better visualization
                log_areas = np.log10(areas + 1)
                axes[1, 0].hist(log_areas, bins=50, alpha=0.7, edgecolor='black')
                axes[1, 0].set_title('Element Area Distribution (log scale)')
                axes[1, 0].set_xlabel('Log10(Area + 1)')
                axes[1, 0].set_ylabel('Frequency')
            
            # 4. Element depth distribution
            if self.stats['element_depths']:
                depths = np.array(self.stats['element_depths'])
                depth_counts = Counter(depths)
                axes[1, 1].bar(depth_counts.keys(), depth_counts.values())
                axes[1, 1].set_title('Element Depth Distribution')
                axes[1, 1].set_xlabel('Depth')
                axes[1, 1].set_ylabel('Count')
            
            plt.tight_layout()
            plt.savefig('dataset_analysis.png', dpi=300, bbox_inches='tight')
            print(f"\n📊 Visualization saved as 'dataset_analysis.png'")
            
        except Exception as e:
            print(f"Warning: Could not generate visualizations: {e}")
    
    def suggest_improvements(self):
        """Suggest dataset improvements"""
        print(f"\n💡 Dataset Improvement Suggestions:")
        print("=" * 50)
        
        # Check for class imbalance
        if self.stats['ui_classes']:
            total_elements = sum(self.stats['ui_classes'].values())
            print(f"\n🎯 Class Distribution Analysis:")
            for ui_class, count in self.stats['ui_classes'].most_common(10):
                percentage = (count / total_elements) * 100
                print(f"   {ui_class.split('.')[-1]}: {count} ({percentage:.1f}%)")
        
        # Suggest based on findings
        print(f"\n🔧 Recommendations:")
        print(f"   1. Consider balancing underrepresented UI element classes")
        print(f"   2. Filter out very small elements (likely noise)")
        print(f"   3. Group similar UI classes for better training")
        print(f"   4. Consider app-specific training for better performance")
        print(f"   5. Use data augmentation to increase diversity")

def main():
    parser = argparse.ArgumentParser(description='Analyze Android UI dataset')
    parser.add_argument('--input', default='combined', help='Input directory containing images and JSON files')
    parser.add_argument('--sample-size', type=int, default=1000, help='Number of JSON files to analyze (for speed)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Directory '{args.input}' not found!")
        return
    
    # Initialize analyzer
    analyzer = DatasetAnalyzer(args.input)
    
    # Run analysis
    analyzer.analyze_dataset()
    
    # Suggest improvements
    analyzer.suggest_improvements()

if __name__ == "__main__":
    main() 