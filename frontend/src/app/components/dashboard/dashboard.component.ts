import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { FormsModule } from '@angular/forms';
import { ChatConversationComponent } from '../chat-conversation/chat-conversation.component';
import { QuestionFormComponent } from '../question-form/question-form.component';
import { UxTrackingService, Question } from '../../services/ux-tracking-service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatCardModule,
    MatIconModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatTabsModule,
    FormsModule,
    ChatConversationComponent,
    QuestionFormComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  recentQuestions: Question[] = [];
  totalQuestions = 0;
  totalAttachments = 0;
  chatHistory: Array<any> = [];
  isLoading = false;
  showRecentPanel = false;
  
  // Toggle mode functionality
  currentMode: 'manual' | 'premium' = 'manual';
  isAutoModeLoading = false;
  autoModeError = '';
  urlInput = '';

  constructor(private uxTrackingService: UxTrackingService) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.uxTrackingService.getDashboardStats().subscribe(data => {
      this.totalQuestions = data.totalQuestions || 0;
      this.totalAttachments = data.totalAttachments || 0;
      this.recentQuestions = data.recentQuestions || [];
    });
  }

  // Toggle mode methods
  switchToManualMode(): void {
    this.currentMode = 'manual';
    this.autoModeError = '';
    this.urlInput = '';
  }

  switchToPremiumMode(): void {
    this.currentMode = 'premium';
    this.autoModeError = '';
  }

  startAutoAnalysis(): void {
    if (!this.urlInput.trim()) {
      this.autoModeError = 'Please enter a valid URL';
      return;
    }

    this.isAutoModeLoading = true;
    this.autoModeError = '';

    // Call the backend premium auto analysis service
    this.uxTrackingService.premiumAutoAnalysis(this.urlInput.trim()).subscribe({
      next: (response) => {
        this.isAutoModeLoading = false;
        
        if (response.error) {
          this.autoModeError = response.error;
          return;
        }

        // Format the response for chat display
        let message = `🎯 **Premium Auto Analysis Complete**\n\n`;
        message += `**Website:** ${response.url}\n`;
        message += `**Analysis Type:** ${response.analysis_type}\n\n`;
        
        if (response.results) {
          message += `**UX Metrics:**\n`;
          message += `• User Engagement Score: ${response.results.user_engagement_score}/100\n`;
          message += `• Navigation Efficiency: ${response.results.navigation_efficiency}/100\n`;
          message += `• Conversion Optimization: ${response.results.conversion_optimization}/100\n`;
          message += `• Mobile Responsiveness: ${response.results.mobile_responsiveness}/100\n`;
          message += `• Load Time Optimization: ${response.results.load_time_optimization}/100\n\n`;
          
          if (response.results.recommendations) {
            message += `**Recommendations:**\n`;
            response.results.recommendations.forEach((rec: string, index: number) => {
              message += `${index + 1}. ${rec}\n`;
            });
          }
        }
        
        message += `\n**Note:** This is currently in demo mode. Real implementation requires adding our tracking script to your website and collecting user data over time.`;

        this.chatHistory.push({
          isUser: false,
          message: message,
          timestamp: new Date()
        });

        // Reload dashboard stats
        this.loadDashboardData();
      },
      error: (error) => {
        this.isAutoModeLoading = false;
        this.autoModeError = 'Sorry for the inconvenience. This error is out of handling and will be resolved shortly.';
        console.error('Premium auto analysis error:', error);
      }
    });
  }

  onQuestionSubmitted(): void {
    // Reload dashboard data when a new question is submitted
    this.loadDashboardData();
  }

  onLLMResponse(response: any): void {
    console.log('LLM Response received:', response);
    
    let message = '';
    
    // Handle different response formats
    if (typeof response === 'string') {
      try {
        // Try to parse as JSON
        const parsedResponse = JSON.parse(response);
        message = parsedResponse.answer || parsedResponse.message || response;
      } catch (e) {
        // If not JSON, use as plain text
        message = response;
      }
    } else if (response && typeof response === 'object') {
      // Handle object response
      message = response.answer || response.message || JSON.stringify(response);
    } else {
      // Fallback
      message = String(response);
    }
    
    // Add the LLM response to chat history
    this.chatHistory.push({
      isUser: false,
      message: message,
      timestamp: new Date()
    });
    
    // Ensure loading state is reset
    this.isLoading = false;
  }

  onAnalysisStarted(): void {
    this.isLoading = true;
  }
}
