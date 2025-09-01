#!/usr/bin/env python3
"""
YOLOv8 Training Script for UI Element Detection
Trains a YOLOv8 model on the organized Android UI dataset
"""

import os
import argparse
from pathlib import Path
from ultralytics import YOLO
import yaml

def load_dataset_config(dataset_yaml_path: str) -> dict:
    """Load dataset configuration from YAML file"""
    with open(dataset_yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def train_model(
    dataset_yaml_path: str,
    model_size: str = 'n',
    epochs: int = 100,
    imgsz: int = 640,
    batch_size: int = 16,
    device: str = '0',
    patience: int = 50,
    save_period: int = 10,
    project: str = 'runs/ui_detection',
    name: str = 'train'
):
    """Train YOLOv8 model on UI element detection dataset"""
    
    print("🚀 Starting YOLOv8 Training for UI Element Detection")
    print("=" * 60)
    
    # Load dataset config
    config = load_dataset_config(dataset_yaml_path)
    print(f"📊 Dataset Configuration:")
    print(f"   Path: {config['path']}")
    print(f"   Classes: {config['nc']}")
    print(f"   Class names: {config['names']}")
    
    # Initialize model
    model_name = f"yolov8{model_size}.pt"
    print(f"🤖 Loading model: {model_name}")
    model = YOLO(model_name)
    
    # Training parameters
    train_args = {
        'data': dataset_yaml_path,
        'epochs': epochs,
        'imgsz': imgsz,
        'batch': batch_size,
        'device': device,
        'patience': patience,
        'save_period': save_period,
        'project': project,
        'name': name,
        'verbose': True,
        'save': True,
        'plots': True,
        'conf': 0.25,
        'iou': 0.45,
        'max_det': 300,
        'half': True,  # Use mixed precision
        'amp': True,   # Automatic mixed precision
    }
    
    print(f"⚙️  Training Parameters:")
    for key, value in train_args.items():
        if key != 'data':
            print(f"   {key}: {value}")
    
    # Start training
    print(f"\n🎯 Starting training...")
    results = model.train(**train_args)
    
    print(f"\n✅ Training completed!")
    print(f"📁 Results saved to: {project}/{name}")
    
    return results

def validate_model(
    model_path: str,
    dataset_yaml_path: str,
    conf: float = 0.25,
    iou: float = 0.45
):
    """Validate trained model"""
    print(f"\n🔍 Validating model: {model_path}")
    
    model = YOLO(model_path)
    results = model.val(
        data=dataset_yaml_path,
        conf=conf,
        iou=iou,
        verbose=True
    )
    
    print(f"📊 Validation Results:")
    print(f"   mAP50: {results.box.map50:.4f}")
    print(f"   mAP50-95: {results.box.map:.4f}")
    print(f"   Precision: {results.box.mp:.4f}")
    print(f"   Recall: {results.box.mr:.4f}")
    
    return results

def export_model(model_path: str, format: str = 'onnx'):
    """Export model to different formats"""
    print(f"\n📦 Exporting model to {format.upper()} format...")
    
    model = YOLO(model_path)
    exported_path = model.export(format=format)
    
    print(f"✅ Model exported to: {exported_path}")
    return exported_path

def main():
    parser = argparse.ArgumentParser(description='Train YOLOv8 model for UI element detection')
    parser.add_argument('--dataset', required=True, help='Path to dataset.yaml file')
    parser.add_argument('--model-size', default='n', choices=['n', 's', 'm', 'l', 'x'], 
                       help='YOLOv8 model size (n=nano, s=small, m=medium, l=large, x=xlarge)')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--imgsz', type=int, default=640, help='Input image size')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--device', default='0', help='Device to use (0, 1, cpu)')
    parser.add_argument('--patience', type=int, default=50, help='Early stopping patience')
    parser.add_argument('--save-period', type=int, default=10, help='Save checkpoint every N epochs')
    parser.add_argument('--project', default='runs/ui_detection', help='Project name')
    parser.add_argument('--name', default='train', help='Experiment name')
    parser.add_argument('--validate', action='store_true', help='Validate model after training')
    parser.add_argument('--export', action='store_true', help='Export model after training')
    parser.add_argument('--export-format', default='onnx', choices=['onnx', 'torchscript', 'tflite'], 
                       help='Export format')
    
    args = parser.parse_args()
    
    # Check if dataset file exists
    if not os.path.exists(args.dataset):
        print(f"❌ Error: Dataset file '{args.dataset}' not found!")
        return
    
    # Train model
    results = train_model(
        dataset_yaml_path=args.dataset,
        model_size=args.model_size,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch_size=args.batch_size,
        device=args.device,
        patience=args.patience,
        save_period=args.save_period,
        project=args.project,
        name=args.name
    )
    
    # Get best model path
    best_model_path = os.path.join(args.project, args.name, 'weights', 'best.pt')
    
    if not os.path.exists(best_model_path):
        print(f"❌ Error: Best model not found at {best_model_path}")
        return
    
    # Validate model
    if args.validate:
        validate_model(best_model_path, args.dataset)
    
    # Export model
    if args.export:
        export_model(best_model_path, args.export_format)
    
    print(f"\n🎉 Training pipeline completed!")
    print(f"📁 Best model: {best_model_path}")

if __name__ == "__main__":
    main() 