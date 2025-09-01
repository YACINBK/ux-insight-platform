#!/usr/bin/env python3
"""
Detailed Class Analysis for UI Element Dataset
Analyzes class distribution, annotation quality, and provides insights for balancing
"""

import os
import json
import argparse
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

class DetailedClassAnalyzer:
    """Analyzes class distribution and annotation quality in detail"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.stats = {
            'class_counts': Counter(),
            'class_areas': defaultdict(list),
            'class_depths': defaultdict(list),
            'annotation_quality': defaultdict(list),
            'empty_annotations': 0,
            'total_files': 0,
            'files_with_elements': 0
        }
    
    def analyze_annotations(self):
        """Analyze all annotation files in detail"""
        print("🔍 Analyzing annotation files...")
        
        # Analyze train, val, test splits
        splits = ['train', 'val', 'test']
        
        for split in splits:
            labels_dir = os.path.join(self.dataset_path, 'labels', split)
            if not os.path.exists(labels_dir):
                continue
                
            print(f"\n📊 Analyzing {split} split...")
            annotation_files = [f for f in os.listdir(labels_dir) if f.endswith('.txt')]
            
            for ann_file in annotation_files:
                self.stats['total_files'] += 1
                ann_path = os.path.join(labels_dir, ann_file)
                
                try:
                    with open(ann_path, 'r') as f:
                        lines = f.readlines()
                    
                    if not lines or all(line.strip() == '' for line in lines):
                        self.stats['empty_annotations'] += 1
                        continue
                    
                    self.stats['files_with_elements'] += 1
                    
                    for line in lines:
                        line = line.strip()
                        if line:
                            parts = line.split()
                            if len(parts) == 5:
                                class_id = int(parts[0])
                                x_center, y_center, width, height = map(float, parts[1:5])
                                
                                # Get class name
                                class_name = self.get_class_name(class_id)
                                self.stats['class_counts'][class_name] += 1
                                
                                # Calculate area
                                area = width * height
                                self.stats['class_areas'][class_name].append(area)
                                
                                # Quality metrics
                                quality_score = self.calculate_quality_score(width, height, x_center, y_center)
                                self.stats['annotation_quality'][class_name].append(quality_score)
                
                except Exception as e:
                    print(f"Error processing {ann_file}: {e}")
                    continue
    
    def get_class_name(self, class_id: int) -> str:
        """Get class name from class ID"""
        class_names = [
            'button', 'text', 'input', 'image', 'container', 'navigation', 'icon', 
            'checkbox', 'radio', 'slider', 'progress', 'tab', 'menu', 'toolbar', 
            'card', 'list_item', 'webview', 'map', 'video', 'ad'
        ]
        return class_names[class_id] if class_id < len(class_names) else f'unknown_{class_id}'
    
    def calculate_quality_score(self, width: float, height: float, x_center: float, y_center: float) -> float:
        """Calculate annotation quality score"""
        # Check if coordinates are within bounds
        if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 < width <= 1 and 0 < height <= 1):
            return 0.0
        
        # Check if element is too small (likely noise)
        if width < 0.01 or height < 0.01:
            return 0.1
        
        # Check if element is too large (likely background)
        if width > 0.9 or height > 0.9:
            return 0.3
        
        # Normal size elements get higher scores
        if 0.01 <= width <= 0.3 and 0.01 <= height <= 0.3:
            return 1.0
        
        return 0.7
    
    def print_detailed_stats(self):
        """Print comprehensive statistics"""
        print("\n" + "="*80)
        print("📈 DETAILED CLASS ANALYSIS")
        print("="*80)
        
        # Overall statistics
        print(f"\n📊 Overall Statistics:")
        print(f"   Total annotation files: {self.stats['total_files']}")
        print(f"   Files with elements: {self.stats['files_with_elements']}")
        print(f"   Empty annotation files: {self.stats['empty_annotations']}")
        print(f"   Empty file percentage: {(self.stats['empty_annotations']/self.stats['total_files']*100):.2f}%")
        
        # Class distribution
        total_elements = sum(self.stats['class_counts'].values())
        print(f"\n🎯 Class Distribution (Total: {total_elements} elements):")
        print("-" * 60)
        
        for class_name, count in self.stats['class_counts'].most_common():
            percentage = (count / total_elements) * 100
            avg_area = np.mean(self.stats['class_areas'][class_name]) if self.stats['class_areas'][class_name] else 0
            avg_quality = np.mean(self.stats['annotation_quality'][class_name]) if self.stats['annotation_quality'][class_name] else 0
            
            print(f"   {class_name:12} | {count:6} ({percentage:5.1f}%) | Avg Area: {avg_area:.4f} | Quality: {avg_quality:.2f}")
        
        # Identify imbalanced classes
        print(f"\n⚠️  Class Balance Analysis:")
        print("-" * 60)
        
        if total_elements > 0:
            expected_percentage = 100 / len(self.stats['class_counts'])
            print(f"   Expected percentage per class: {expected_percentage:.1f}%")
            
            underrepresented = []
            overrepresented = []
            
            for class_name, count in self.stats['class_counts'].items():
                percentage = (count / total_elements) * 100
                if percentage < expected_percentage * 0.1:  # Less than 10% of expected
                    underrepresented.append((class_name, count, percentage))
                elif percentage > expected_percentage * 10:  # More than 10x expected
                    overrepresented.append((class_name, count, percentage))
            
            if underrepresented:
                print(f"\n   🔴 Underrepresented classes (< {expected_percentage*0.1:.1f}%):")
                for class_name, count, percentage in underrepresented:
                    print(f"      {class_name}: {count} ({percentage:.1f}%)")
            
            if overrepresented:
                print(f"\n   🟡 Overrepresented classes (> {expected_percentage*10:.1f}%):")
                for class_name, count, percentage in overrepresented:
                    print(f"      {class_name}: {count} ({percentage:.1f}%)")
        
        # Quality analysis
        print(f"\n🔍 Annotation Quality Analysis:")
        print("-" * 60)
        
        for class_name in self.stats['class_counts'].keys():
            if self.stats['annotation_quality'][class_name]:
                quality_scores = self.stats['annotation_quality'][class_name]
                avg_quality = np.mean(quality_scores)
                low_quality = sum(1 for q in quality_scores if q < 0.5)
                total = len(quality_scores)
                
                print(f"   {class_name:12} | Avg Quality: {avg_quality:.2f} | Low Quality: {low_quality}/{total} ({low_quality/total*100:.1f}%)")
    
    def generate_visualizations(self):
        """Generate detailed visualizations"""
        try:
            # Set up the plotting style
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Detailed UI Element Class Analysis', fontsize=16, fontweight='bold')
            
            # 1. Class distribution pie chart
            if self.stats['class_counts']:
                class_names = list(self.stats['class_counts'].keys())
                counts = list(self.stats['class_counts'].values())
                
                # Only show top 10 classes for readability
                if len(class_names) > 10:
                    sorted_data = sorted(zip(class_names, counts), key=lambda x: x[1], reverse=True)
                    class_names = [x[0] for x in sorted_data[:10]]
                    counts = [x[1] for x in sorted_data[:10]]
                
                axes[0, 0].pie(counts, labels=class_names, autopct='%1.1f%%', startangle=90)
                axes[0, 0].set_title('Class Distribution (Top 10)')
            
            # 2. Class counts bar chart
            if self.stats['class_counts']:
                class_names = list(self.stats['class_counts'].keys())
                counts = list(self.stats['class_counts'].values())
                
                # Sort by count
                sorted_data = sorted(zip(class_names, counts), key=lambda x: x[1], reverse=True)
                class_names = [x[0] for x in sorted_data]
                counts = [x[1] for x in sorted_data]
                
                axes[0, 1].barh(range(len(class_names)), counts)
                axes[0, 1].set_yticks(range(len(class_names)))
                axes[0, 1].set_yticklabels(class_names)
                axes[0, 1].set_title('Class Counts')
                axes[0, 1].set_xlabel('Count')
            
            # 3. Area distribution by class
            if self.stats['class_areas']:
                # Get top 5 classes by count
                top_classes = [name for name, _ in self.stats['class_counts'].most_common(5)]
                
                for i, class_name in enumerate(top_classes):
                    if self.stats['class_areas'][class_name]:
                        areas = np.array(self.stats['class_areas'][class_name])
                        # Log scale for better visualization
                        log_areas = np.log10(areas + 1e-6)
                        axes[1, 0].hist(log_areas, alpha=0.7, label=class_name, bins=20)
                
                axes[1, 0].set_title('Area Distribution (Top 5 Classes)')
                axes[1, 0].set_xlabel('Log10(Area)')
                axes[1, 0].set_ylabel('Frequency')
                axes[1, 0].legend()
            
            # 4. Quality distribution
            if self.stats['annotation_quality']:
                # Get top 5 classes by count
                top_classes = [name for name, _ in self.stats['class_counts'].most_common(5)]
                
                quality_data = []
                quality_labels = []
                
                for class_name in top_classes:
                    if self.stats['annotation_quality'][class_name]:
                        quality_data.extend(self.stats['annotation_quality'][class_name])
                        quality_labels.extend([class_name] * len(self.stats['annotation_quality'][class_name]))
                
                if quality_data:
                    axes[1, 1].hist(quality_data, bins=20, alpha=0.7, edgecolor='black')
                    axes[1, 1].set_title('Annotation Quality Distribution')
                    axes[1, 1].set_xlabel('Quality Score')
                    axes[1, 1].set_ylabel('Frequency')
            
            plt.tight_layout()
            plt.savefig('detailed_class_analysis.png', dpi=300, bbox_inches='tight')
            print(f"\n📊 Detailed visualization saved as 'detailed_class_analysis.png'")
            
        except Exception as e:
            print(f"Warning: Could not generate visualizations: {e}")
    
    def suggest_improvements(self):
        """Suggest improvements for class balancing"""
        print(f"\n💡 IMPROVEMENT SUGGESTIONS")
        print("="*80)
        
        total_elements = sum(self.stats['class_counts'].values())
        if total_elements == 0:
            return
        
        expected_percentage = 100 / len(self.stats['class_counts'])
        
        print(f"\n🎯 Class Balancing Strategies:")
        print(f"   1. **Data Augmentation**: Use YOLOv8's built-in augmentation for underrepresented classes")
        print(f"   2. **Class Weights**: Apply higher weights to underrepresented classes during training")
        print(f"   3. **Filtering**: Remove very small or low-quality annotations")
        print(f"   4. **Reclassification**: Group similar classes together")
        print(f"   5. **Oversampling**: Duplicate samples from underrepresented classes")
        
        print(f"\n🔧 Specific Recommendations:")
        
        # Check for empty classes
        empty_classes = []
        for class_name in ['button', 'text', 'input', 'image', 'checkbox', 'radio', 'slider', 'progress']:
            if self.stats['class_counts'][class_name] == 0:
                empty_classes.append(class_name)
        
        if empty_classes:
            print(f"   ⚠️  Empty classes detected: {', '.join(empty_classes)}")
            print(f"      → Consider removing these classes or improving class mapping")
        
        # Check for dominant classes
        dominant_threshold = expected_percentage * 5  # 5x expected
        dominant_classes = []
        for class_name, count in self.stats['class_counts'].items():
            percentage = (count / total_elements) * 100
            if percentage > dominant_threshold:
                dominant_classes.append((class_name, percentage))
        
        if dominant_classes:
            print(f"   ⚠️  Dominant classes detected:")
            for class_name, percentage in dominant_classes:
                print(f"      → {class_name}: {percentage:.1f}% (expected: {expected_percentage:.1f}%)")
            print(f"      → Consider splitting dominant classes into subclasses")
        
        print(f"\n📋 Recommended Actions:")
        print(f"   1. Review class mapping in enhanced_organizer.py")
        print(f"   2. Adjust overlap filtering threshold")
        print(f"   3. Implement class weights in training")
        print(f"   4. Use data augmentation for underrepresented classes")

def main():
    parser = argparse.ArgumentParser(description='Detailed class analysis for UI element dataset')
    parser.add_argument('--dataset', required=True, help='Path to organized dataset directory')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset):
        print(f"Error: Dataset directory '{args.dataset}' not found!")
        return
    
    # Initialize analyzer
    analyzer = DetailedClassAnalyzer(args.dataset)
    
    # Run analysis
    analyzer.analyze_annotations()
    analyzer.print_detailed_stats()
    analyzer.generate_visualizations()
    analyzer.suggest_improvements()

if __name__ == "__main__":
    main() 