#!/usr/bin/env python3
"""
Complete Workflow Script for UI Element Detection
Orchestrates the entire process from dataset analysis to YOLOv8 training
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import time

def run_command(command: str, description: str) -> bool:
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"   Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'ultralytics',
        'PIL',
        'numpy',
        'matplotlib',
        'seaborn',
        'PyYAML'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'PyYAML':
                import yaml
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def analyze_dataset(input_dir: str):
    """Run dataset analysis"""
    command = f"python dataset_analyzer.py --input {input_dir}"
    return run_command(command, "Dataset Analysis")

def organize_dataset(input_dir: str, output_dir: str, train_ratio: float, val_ratio: float, test_ratio: float):
    """Organize dataset for YOLO training"""
    command = f"python enhanced_organizer.py --input {input_dir} --output {output_dir} --train-ratio {train_ratio} --val-ratio {val_ratio} --test-ratio {test_ratio}"
    return run_command(command, "Dataset Organization")

def train_model(dataset_yaml: str, model_size: str, epochs: int, batch_size: int, device: str):
    """Train YOLOv8 model"""
    command = f"python train_yolo.py --dataset {dataset_yaml} --model-size {model_size} --epochs {epochs} --batch-size {batch_size} --device {device} --validate --export"
    return run_command(command, "YOLOv8 Training")

def main():
    parser = argparse.ArgumentParser(description='Complete workflow for UI element detection')
    parser.add_argument('--input', default='combined', help='Input directory containing images and JSON files')
    parser.add_argument('--output', default='organized_dataset', help='Output directory for organized dataset')
    parser.add_argument('--train-ratio', type=float, default=0.7, help='Training set ratio')
    parser.add_argument('--val-ratio', type=float, default=0.2, help='Validation set ratio')
    parser.add_argument('--test-ratio', type=float, default=0.1, help='Test set ratio')
    parser.add_argument('--model-size', default='n', choices=['n', 's', 'm', 'l', 'x'], 
                       help='YOLOv8 model size')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--device', default='0', help='Device to use (0, 1, cpu)')
    parser.add_argument('--skip-analysis', action='store_true', help='Skip dataset analysis')
    parser.add_argument('--skip-organization', action='store_true', help='Skip dataset organization')
    parser.add_argument('--skip-training', action='store_true', help='Skip model training')
    
    args = parser.parse_args()
    
    print("🚀 UI Element Detection - Complete Workflow")
    print("=" * 60)
    print(f"📁 Input directory: {args.input}")
    print(f"📁 Output directory: {args.output}")
    print(f"🤖 Model size: YOLOv8{args.model_size}")
    print(f"📊 Train/Val/Test split: {args.train_ratio}/{args.val_ratio}/{args.test_ratio}")
    print(f"🎯 Training epochs: {args.epochs}")
    print(f"⚙️  Batch size: {args.batch_size}")
    print(f"💻 Device: {args.device}")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        sys.exit(1)
    
    # Check input directory
    if not os.path.exists(args.input):
        print(f"\n❌ Input directory '{args.input}' not found!")
        sys.exit(1)
    
    start_time = time.time()
    
    # Step 1: Dataset Analysis
    if not args.skip_analysis:
        if not analyze_dataset(args.input):
            print("\n❌ Dataset analysis failed. Stopping workflow.")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping dataset analysis")
    
    # Step 2: Dataset Organization
    if not args.skip_organization:
        if not organize_dataset(args.input, args.output, args.train_ratio, args.val_ratio, args.test_ratio):
            print("\n❌ Dataset organization failed. Stopping workflow.")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping dataset organization")
    
    # Step 3: Model Training
    if not args.skip_training:
        dataset_yaml = os.path.join(args.output, 'yolo_dataset', 'dataset.yaml')
        if not os.path.exists(dataset_yaml):
            print(f"\n❌ Dataset YAML file not found: {dataset_yaml}")
            print("   Make sure to run dataset organization first")
            sys.exit(1)
        
        if not train_model(dataset_yaml, args.model_size, args.epochs, args.batch_size, args.device):
            print("\n❌ Model training failed.")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping model training")
    
    # Calculate total time
    total_time = time.time() - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    
    print("\n" + "=" * 60)
    print("🎉 Workflow completed successfully!")
    print(f"⏱️  Total time: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    # Print next steps
    print("\n📋 Next Steps:")
    print("   1. Check training results in 'runs/ui_detection/train/'")
    print("   2. Evaluate model performance on test set")
    print("   3. Fine-tune hyperparameters if needed")
    print("   4. Export model for deployment")
    print("   5. Integrate model into your application")
    
    # Print useful commands
    print("\n🔧 Useful Commands:")
    print(f"   # Validate model: yolo val model=runs/ui_detection/train/weights/best.pt data={dataset_yaml}")
    print(f"   # Predict on images: yolo predict model=runs/ui_detection/train/weights/best.pt source=test_images/")
    print(f"   # Export model: yolo export model=runs/ui_detection/train/weights/best.pt format=onnx")

if __name__ == "__main__":
    main() 