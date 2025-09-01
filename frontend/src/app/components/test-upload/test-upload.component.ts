import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-test-upload',
  template: `
    <form (submit)="onSubmit($event)">
      <input type="file" (change)="onFileChange($event)" multiple>
      <button type="submit">Upload</button>
    </form>
  `
})
export class TestUploadComponent {
  files: File[] = [];

  constructor(private http: HttpClient) {}

  onFileChange(event: any) {
    this.files = Array.from(event.target.files);
  }

  onSubmit(event: Event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append('title', 'Test upload');
    this.files.forEach(file => formData.append('attachments', file));
    this.http.post('http://localhost:8080/api/questions/test-upload', formData)
      .subscribe(res => console.log('Upload response:', res));
  }
} 