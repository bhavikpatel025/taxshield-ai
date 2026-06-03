export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin' | 'super_admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: User;
}

export interface UsageCounter {
  used: number;
  limit: number | null;
  remaining: number | null;
}

export interface UsageSummary {
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'expired' | 'cancelled';
  usage_date: string;
  questions: UsageCounter;
  uploads: UsageCounter;
}

export interface AuditFlag {
  code: string;
  description: string;
  severity: string;
  supporting_tax_authority: string;
}

export interface AuditResult {
  id: string;
  risk_level: string;
  flags: AuditFlag[];
  created_at: string;
}

export interface DocumentRecord {
  id: string;
  filename: string;
  file_type: string;
  status: string;
  processed_at: string | null;
  created_at: string;
}

export interface DocumentUploadResponse {
  document: DocumentRecord;
  audit: AuditResult;
}

export interface Citation {
  source_id: string;
  source_title: string;
  section: string;
  source_url: string | null;
  validated: boolean;
}

export interface AskQuestionResponse {
  question_id: string;
  status: 'answered' | 'unsupported' | 'failed';
  answer: string;
  confidence: number;
  citations: Citation[];
}

export interface QuestionHistory {
  id: string;
  status: string;
  confidence: number;
  retrieved_chunk_count: number;
  unsupported_reason: string | null;
  created_at: string;
}
