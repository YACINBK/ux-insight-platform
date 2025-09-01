import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    <div class="file-upload-container">
      <div class="upload-buttons">
        <button type="button" mat-raised-button color="accent" (click)="selectImages()" class="upload-btn">
          <mat-icon>image</mat-icon>
          Add Images
        </button>

        <button type="button" mat-raised-button color="accent" (click)="selectJsonFiles()" class="upload-btn">
          <mat-icon>code</mat-icon>
          Add JSON Data
        </button>
      </div>

      <div class="drop-zone"
           [class.drag-over]="isDragOver"
           (dragover)="onDragOver($event)"
           (dragleave)="onDragLeave($event)"
           (drop)="onDrop($event)">

        <div class="drop-content">
          <mat-icon class="drop-icon">cloud_upload</mat-icon>
          <h3>Drag & Drop Files Here</h3>
          <p>Or use the buttons above to select files</p>
          <div class="supported-formats">
            <span class="format-chip">Images: JPG, PNG, GIF, WebP</span>
            <span class="format-chip">Data: JSON</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent {
  @Output() filesSelected = new EventEmitter<File[]>();

  isDragOver = false;
  acceptedTypes = {
    images: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
    json: ['application/json', 'text/json']
  };

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;

    const files = Array.from(event.dataTransfer?.files || []);
    this.handleFiles(files);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    this.handleFiles(files);
    input.value = '';
  }

  private handleFiles(files: File[]): void {
    const validFiles = files.filter(file => this.isValidFile(file));
    if (validFiles.length > 0) {
      this.filesSelected.emit(validFiles);
    }
  }

  private isValidFile(file: File): boolean {
    const allAcceptedTypes = [...this.acceptedTypes.images, ...this.acceptedTypes.json];
    return allAcceptedTypes.includes(file.type);
  }

  selectImages(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = this.acceptedTypes.images.join(',');
    input.onchange = (event) => this.onFileSelected(event);
    input.click();
  }

  selectJsonFiles(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = this.acceptedTypes.json.join(',');
    input.onchange = (event) => this.onFileSelected(event);
    input.click();
  }
}

@Component({
  selector: 'app-image-upload',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="image-upload-container">
      <button type="button" (click)="selectImage()">Select Image</button>
      <input type="file" accept="image/*" style="display:none" #imageInput (change)="onImageSelected($event)">
      <div *ngIf="selectedImage">
        <span>{{ selectedImage.name }}</span>
        <button type="button" (click)="removeImage()">Remove</button>
      </div>
    </div>
  `,
  styles: [`.image-upload-container { margin-bottom: 1em; }`]
})
export class ImageUploadComponent {
  @Output() imageSelected = new EventEmitter<File | null>();
  selectedImage: File | null = null;

  selectImage(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (event: any) => this.onImageSelected(event);
    input.click();
  }

  onImageSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files && input.files.length > 0 ? input.files[0] : null;
    this.selectedImage = file;
    this.imageSelected.emit(this.selectedImage);
  }

  removeImage(): void {
    this.selectedImage = null;
    this.imageSelected.emit(null);
  }
}
