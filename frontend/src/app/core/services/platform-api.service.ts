import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  AskQuestionResponse,
  DocumentRecord,
  DocumentUploadResponse,
  QuestionHistory,
  UsageSummary
} from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class PlatformApiService {
  constructor(private readonly http: HttpClient) {}

  getUsage(): Observable<UsageSummary> {
    return this.http.get<UsageSummary>(`${environment.apiBaseUrl}/subscriptions/usage`);
  }

  uploadDocument(file: File): Observable<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<DocumentUploadResponse>(`${environment.apiBaseUrl}/documents/upload`, formData);
  }

  listDocuments(): Observable<DocumentRecord[]> {
    return this.http.get<DocumentRecord[]>(`${environment.apiBaseUrl}/documents`);
  }

  askQuestion(question: string): Observable<AskQuestionResponse> {
    return this.http.post<AskQuestionResponse>(`${environment.apiBaseUrl}/qa/ask`, { question });
  }

  listQuestionHistory(): Observable<QuestionHistory[]> {
    return this.http.get<QuestionHistory[]>(`${environment.apiBaseUrl}/qa/history`);
  }
}
