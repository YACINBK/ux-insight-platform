import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Question {
  title: string;
  createdAt?: Date;
  attachments?: string[];
}

export interface DashboardStats {
  totalQuestions: number;
  totalAttachments: number;
  recentQuestions: Question[];
}

@Injectable({
  providedIn: 'root'
})
export class UxTrackingService {
  private apiUrl = (window as any)['API_BASE_URL'] || 'http://localhost:8080/api';

  constructor(private http: HttpClient) {}

  submitQuestion(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/questions`, formData).pipe(
      catchError(this.handleError<any>('submitQuestion'))
    );
  }

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.apiUrl}/questions/dashboard/stats`).pipe(
      catchError(this.handleError<DashboardStats>('getDashboardStats', {
        totalQuestions: 0,
        totalAttachments: 0,
        recentQuestions: []
      }))
    );
  }

  sendToVision(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/questions/vision/analyze`, formData).pipe(
      catchError(this.handleError<any>('sendToVision'))
    );
  }

  premiumAutoAnalysis(url: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/questions/premium-auto/analyze`, { url }).pipe(
      catchError(this.handleError<any>('premiumAutoAnalysis'))
    );
  }

  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed:`, error);
      return of(result as T);
    };
  }
}
