import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { RouterLink } from '@angular/router';

import { UsageSummary } from '../../core/models/api.models';
import { PlatformApiService } from '../../core/services/platform-api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule, MatIconModule, MatProgressBarModule],
  template: `
    <section class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p>Subscription usage and V1 workflow status.</p>
      </div>
      <a mat-flat-button color="primary" routerLink="/dashboard/qa">
        <mat-icon>forum</mat-icon>
        Ask question
      </a>
    </section>

    @if (usage(); as data) {
      <section class="metrics-grid">
        <mat-card>
          <mat-card-header>
            <mat-icon mat-card-avatar>workspace_premium</mat-icon>
            <mat-card-title>{{ data.plan | uppercase }}</mat-card-title>
            <mat-card-subtitle>{{ data.status }} plan</mat-card-subtitle>
          </mat-card-header>
        </mat-card>
        <mat-card>
          <mat-card-header>
            <mat-icon mat-card-avatar>help</mat-icon>
            <mat-card-title>{{ data.questions.used }}/{{ data.questions.limit ?? 'Custom' }}</mat-card-title>
            <mat-card-subtitle>Questions today</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <mat-progress-bar mode="determinate" [value]="progress(data.questions.used, data.questions.limit)"></mat-progress-bar>
          </mat-card-content>
        </mat-card>
        <mat-card>
          <mat-card-header>
            <mat-icon mat-card-avatar>upload_file</mat-icon>
            <mat-card-title>{{ data.uploads.used }}/{{ data.uploads.limit ?? 'Custom' }}</mat-card-title>
            <mat-card-subtitle>Uploads today</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <mat-progress-bar mode="determinate" [value]="progress(data.uploads.used, data.uploads.limit)"></mat-progress-bar>
          </mat-card-content>
        </mat-card>
      </section>
    }

    <section class="workflow-grid">
      <a mat-stroked-button routerLink="/dashboard/documents">
        <mat-icon>upload_file</mat-icon>
        Upload document
      </a>
      <a mat-stroked-button routerLink="/dashboard/qa">
        <mat-icon>fact_check</mat-icon>
        Citation Q&A
      </a>
    </section>
  `
})
export class DashboardComponent implements OnInit {
  readonly usage = signal<UsageSummary | null>(null);

  constructor(private readonly api: PlatformApiService) {}

  ngOnInit(): void {
    this.api.getUsage().subscribe((usage) => this.usage.set(usage));
  }

  progress(used: number, limit: number | null): number {
    if (!limit) {
      return 0;
    }
    return Math.min(100, (used / limit) * 100);
  }
}
