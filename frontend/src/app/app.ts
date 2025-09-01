import { Component } from '@angular/core';
import { DashboardComponent } from './components/dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DashboardComponent],
  template: `
    <div class="app-container">
      <app-dashboard></app-dashboard>
    </div>
  `,
  styles: [`
    .app-container {
      min-height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
  `]
})
export class AppComponent {
  title = 'ux-tracking-dashboard';
}

