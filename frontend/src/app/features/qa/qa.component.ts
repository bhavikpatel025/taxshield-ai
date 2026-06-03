import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';

import { AskQuestionResponse, QuestionHistory } from '../../core/models/api.models';
import { PlatformApiService } from '../../core/services/platform-api.service';

@Component({
  selector: 'app-qa',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatTableModule
  ],
  template: `
    <section class="page-header">
      <div>
        <h1>Tax Q&A</h1>
        <p>Source-backed responses with citation validation.</p>
      </div>
    </section>

    <mat-card>
      <mat-card-content>
        <form class="qa-form" [formGroup]="form" (ngSubmit)="ask()">
          <mat-form-field appearance="outline">
            <mat-label>Tax question</mat-label>
            <textarea matInput rows="4" formControlName="question"></textarea>
          </mat-form-field>
          @if (error()) {
            <p class="error">{{ error() }}</p>
          }
          <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid || loading()">
            @if (loading()) {
              <mat-spinner diameter="18"></mat-spinner>
            } @else {
              <mat-icon>send</mat-icon>
            }
            Submit
          </button>
        </form>
      </mat-card-content>
    </mat-card>

    @if (answer(); as result) {
      <section class="answer-panel">
        <mat-card>
          <mat-card-header>
            <mat-card-title>{{ result.status | uppercase }}</mat-card-title>
            <mat-card-subtitle>Confidence {{ result.confidence | percent:'1.0-0' }}</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <p>{{ result.answer }}</p>
            <div class="citation-list">
              @for (citation of result.citations; track citation.source_id + citation.section) {
                <mat-chip>
                  <mat-icon>verified</mat-icon>
                  {{ citation.source_title }} · {{ citation.section }}
                </mat-chip>
              }
            </div>
          </mat-card-content>
        </mat-card>
      </section>
    }

    <mat-card>
      <mat-card-header>
        <mat-card-title>Q&A History</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <table mat-table [dataSource]="history()" class="data-table">
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef>Status</th>
            <td mat-cell *matCellDef="let row">{{ row.status }}</td>
          </ng-container>
          <ng-container matColumnDef="confidence">
            <th mat-header-cell *matHeaderCellDef>Confidence</th>
            <td mat-cell *matCellDef="let row">{{ row.confidence | percent:'1.0-0' }}</td>
          </ng-container>
          <ng-container matColumnDef="created_at">
            <th mat-header-cell *matHeaderCellDef>Created</th>
            <td mat-cell *matCellDef="let row">{{ row.created_at | date:'short' }}</td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns;"></tr>
        </table>
      </mat-card-content>
    </mat-card>
  `
})
export class QaComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(PlatformApiService);

  readonly loading = signal(false);
  readonly error = signal('');
  readonly answer = signal<AskQuestionResponse | null>(null);
  readonly history = signal<QuestionHistory[]>([]);
  readonly columns = ['status', 'confidence', 'created_at'];
  readonly form = this.fb.nonNullable.group({
    question: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(2000)]]
  });

  ngOnInit(): void {
    this.refreshHistory();
  }

  ask(): void {
    if (this.form.invalid) {
      return;
    }
    this.loading.set(true);
    this.error.set('');
    this.api.askQuestion(this.form.controls.question.value).subscribe({
      next: (response) => {
        this.answer.set(response);
        this.loading.set(false);
        this.refreshHistory();
      },
      error: (error) => {
        this.loading.set(false);
        this.error.set(error.error?.detail ?? 'Question failed');
      }
    });
  }

  private refreshHistory(): void {
    this.api.listQuestionHistory().subscribe((history) => this.history.set(history));
  }
}
