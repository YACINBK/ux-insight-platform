import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FileUploadComponent } from '../file-upload/file-upload.component';
import { UxTrackingService } from '../../services/ux-tracking-service';

@Component({
  selector: 'app-question-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatSnackBarModule,
    FileUploadComponent
  ],
  templateUrl: './question-form.component.html',
  styleUrls: ['./question-form.component.scss']
})
export class QuestionFormComponent {
  @Output() questionSubmitted = new EventEmitter<void>();
  @Output() analysisStarted = new EventEmitter<void>();
  @Output() llmResponse = new EventEmitter<any>();

  questionForm: FormGroup;
  attachments: File[] = [];
  selectedImages: File[] = [];
  isSubmitting = false;

  constructor(
    private fb: FormBuilder,
    private uxTrackingService: UxTrackingService,
    private snackBar: MatSnackBar
  ) {
    this.questionForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(5)]]
    });
  }

  onFilesSelected(files: File[]): void {
    // Separate JSON files and images
    const jsonFiles = files.filter(file => file.type === 'application/json');
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    // Add JSON files to attachments
    this.attachments = [...this.attachments, ...jsonFiles];
    
    // Add image files to selectedImages array
    if (imageFiles.length > 0) {
      this.selectedImages = [...this.selectedImages, ...imageFiles];
      
      this.snackBar.open(`${imageFiles.length} image(s) added for analysis.`, 'Close', {
        duration: 3000,
        panelClass: ['info-snackbar']
      });
    }
    
    // Show warning for unsupported files
    const unsupportedFiles = files.filter(file => 
      file.type !== 'application/json' && !file.type.startsWith('image/')
    );
    if (unsupportedFiles.length > 0) {
      this.snackBar.open('Some files were ignored. Only JSON and image files are supported.', 'Close', {
        duration: 3000,
        panelClass: ['warning-snackbar']
      });
    }
  }

  removeAttachment(index: number): void {
    this.attachments.splice(index, 1);
  }

  removeImage(index: number): void {
    this.selectedImages.splice(index, 1);
  }

  async onSubmit(): Promise<void> {
    if (this.questionForm.valid) {
      this.isSubmitting = true;
      this.analysisStarted.emit(); // Notify dashboard that analysis started
      
      try {
        // Step 1: Process all images through Vision API
        let allVisionResults = [];
        if (this.selectedImages.length > 0) {
          this.snackBar.open(`Processing ${this.selectedImages.length} image(s)...`, 'Close', {
            duration: 2000,
            panelClass: ['info-snackbar']
          });
          
          for (let i = 0; i < this.selectedImages.length; i++) {
            const image = this.selectedImages[i];
            try {
              const visionResult = await this.analyzeImage(image);
              if (visionResult && !visionResult.error) {
                allVisionResults.push({
                  imageName: image.name,
                  imageIndex: i,
                  ...visionResult
                });
              }
            } catch (error) {
              console.error(`Error processing image ${image.name}:`, error);
              this.snackBar.open(`Error processing image ${image.name}`, 'Close', {
                duration: 3000,
                panelClass: ['error-snackbar']
              });
            }
          }
        }

        // Step 2: Submit everything to the main endpoint
        const formData = new FormData();
        formData.append('title', this.questionForm.get('title')?.value);
        
        // Add JSON attachments
        this.attachments.forEach((file) => {
          formData.append('attachments', file);
        });

        // Add all vision analysis results
        if (allVisionResults.length > 0) {
          formData.append('visionAnalysis', JSON.stringify(allVisionResults));
        }

        // Submit to Spring Boot
        this.uxTrackingService.submitQuestion(formData).subscribe({
          next: (response) => {
            this.snackBar.open('Analysis submitted successfully!', 'Close', {
              duration: 3000,
              panelClass: ['success-snackbar']
            });
            
            // Emit the LLM response to be displayed in chat
            this.llmResponse.emit(response);
            
            this.resetForm();
            this.questionSubmitted.emit();
            this.isSubmitting = false;
          },
          error: (error) => {
            this.snackBar.open('Error submitting analysis. Please try again.', 'Close', {
              duration: 3000,
              panelClass: ['error-snackbar']
            });
            this.isSubmitting = false;
          }
        });

      } catch (error) {
        this.snackBar.open('Error processing analysis. Please try again.', 'Close', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        this.isSubmitting = false;
      }
    }
  }

  private analyzeImage(imageFile: File): Promise<any> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('attachments', imageFile);
      
      this.uxTrackingService.sendToVision(formData).subscribe({
        next: (result) => resolve(result),
        error: (error) => reject(error)
      });
    });
  }

  resetForm(): void {
    this.questionForm.reset();
    this.attachments = [];
    this.selectedImages = [];
  }

  getErrorMessage(fieldName: string): string {
    const field = this.questionForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
    }
    if (field?.hasError('minlength')) {
      const requiredLength = field.errors?.['minlength']?.requiredLength;
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be at least ${requiredLength} characters`;
    }
    return '';
  }
}
