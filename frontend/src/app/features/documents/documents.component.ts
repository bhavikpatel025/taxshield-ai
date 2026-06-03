import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';

import { AuditResult, DocumentRecord, DocumentUploadResponse } from '../../core/models/api.models';
import { PlatformApiService } from '../../core/services/platform-api.service';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTableModule
  ],
  template: `
    <section class="page-header">
      <div>
        <h1>Documents</h1>
        <p>Upload text-based tax notes for audit flag detection.</p>
      </div>
      <label class="file-button">
        <input type="file" accept=".txt,.csv,.json,text/plain,text/csv,application/json" (change)="selectFile($event)">
        <mat-icon>attach_file</mat-icon>
        {{ selectedFile()?.name ?? 'Select file' }}
      </label>
      <button mat-flat-button color="primary" type="button" [disabled]="!selectedFile() || loading()" (click)="upload()">
        @if (loading()) {
          <mat-spinner diameter="18"></mat-spinner>
        } @else {
          <mat-icon>upload</mat-icon>
        }
        Upload
      </button>
    </section>

    @if (error()) {
      <p class="error">{{ error() }}</p>
    }

    @if (latestAudit(); as audit) {
      <section class="result-band">
        <div>
          <span class="eyebrow">Risk level</span>
          <h2>{{ audit.risk_level | uppercase }}</h2>
        </div>
        <div class="flag-list">
          @for (flag of audit.flags; track flag.code) {
            <mat-chip>
              {{ flag.code }} · {{ flag.severity }}
            </mat-chip>
          }
        </div>
      </section>
      <section class="findings">
        @for (flag of audit.flags; track flag.code) {
          <mat-card>
            <mat-card-header>
              <mat-card-title>{{ flag.code }}</mat-card-title>
              <mat-card-subtitle>{{ flag.supporting_tax_authority }}</mat-card-subtitle>
            </mat-card-header>
            <mat-card-content>{{ flag.description }}</mat-card-content>
          </mat-card>
        }
      </section>
    }

    <mat-card>
      <mat-card-header>
        <mat-card-title>Document History</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <table mat-table [dataSource]="documents()" class="data-table">
          <ng-container matColumnDef="filename">
            <th mat-header-cell *matHeaderCellDef>File</th>
            <td mat-cell *matCellDef="let row">{{ row.filename }}</td>
          </ng-container>
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef>Status</th>
            <td mat-cell *matCellDef="let row">{{ row.status }}</td>
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
export class DocumentsComponent implements OnInit {
  readonly selectedFile = signal<File | null>(null);
  readonly loading = signal(false);
  readonly error = signal('');
  readonly documents = signal<DocumentRecord[]>([]);
  readonly latestAudit = signal<AuditResult | null>(null);
  readonly columns = ['filename', 'status', 'created_at'];

  constructor(private readonly api: PlatformApiService) {}

  ngOnInit(): void {
    this.refresh();
  }

  selectFile(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.item(0) ?? null);
  }

  upload(): void {
    const file = this.selectedFile();
    if (!file) {
      return;
    }
    this.loading.set(true);
    this.error.set('');
    this.api.uploadDocument(file).subscribe({
      next: (response: DocumentUploadResponse) => {
        this.latestAudit.set(response.audit);
        this.loading.set(false);
        this.selectedFile.set(null);
        this.refresh();
      },
      error: (error) => {
        this.loading.set(false);
        this.error.set(error.error?.detail ?? 'Upload failed');
      }
    });
  }

  private refresh(): void {
    this.api.listDocuments().subscribe((documents) => this.documents.set(documents));
  }
}
