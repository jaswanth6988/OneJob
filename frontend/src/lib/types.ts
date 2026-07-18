// ── Enums ──

export enum JobStatus {
  NEW = 'NEW',
  MATCHED = 'MATCHED',
  PARTIAL_MATCHED = 'PARTIAL_MATCHED',
  APPLYING = 'APPLYING',
  APPLIED = 'APPLIED',
  MANUAL_REVIEW = 'MANUAL_REVIEW',
  SKIPPED = 'SKIPPED',
  FAILED = 'FAILED',
}

export enum RemoteType {
  REMOTE = 'REMOTE',
  HYBRID = 'HYBRID',
  ONSITE = 'ONSITE',
  UNKNOWN = 'UNKNOWN',
}

export enum ApplicationStatus {
  PENDING = 'PENDING',
  APPLYING = 'APPLYING',
  APPLIED = 'APPLIED',
  MANUAL_REVIEW = 'MANUAL_REVIEW',
  FAILED = 'FAILED',
  SKIPPED = 'SKIPPED',
  RETRYING = 'RETRYING',
}

export enum RoleLabel {
  GENERAL = 'GENERAL',
  DEVELOPER = 'DEVELOPER',
  DATA_AI = 'DATA_AI',
  CLOUD = 'CLOUD',
  SECURITY = 'SECURITY',
  CUSTOM = 'CUSTOM',
}

export enum ManualReviewReason {
  CAPTCHA_DETECTED = 'CAPTCHA_DETECTED',
  IP_BLOCKED = 'IP_BLOCKED',
  LAYOUT_CHANGED = 'LAYOUT_CHANGED',
  FIELD_MISMATCH = 'FIELD_MISMATCH',
  UPLOAD_FAILED = 'UPLOAD_FAILED',
  LOGIN_EXPIRED = 'LOGIN_EXPIRED',
  MFA_REQUIRED = 'MFA_REQUIRED',
  ANSWER_NOT_RECOGNIZED = 'ANSWER_NOT_RECOGNIZED',
  FILE_INVALID = 'FILE_INVALID',
  UNKNOWN_EXCEPTION = 'UNKNOWN_EXCEPTION',
  PAGE_TIMEOUT = 'PAGE_TIMEOUT',
}

export enum Severity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

// ── User ──

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  phone?: string;
  location?: string;
  preferred_roles: string[];
  preferred_locations: string[];
  expected_salary?: string;
  notice_period?: string;
  work_authorization?: string;
  portfolio_links: string[];
  github_link?: string;
  linkedin_link?: string;
  priority_companies: string[];
  priority_roles: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── Resume ──

export interface ExperienceEntry {
  company: string;
  title: string;
  duration: string;
  bullets: string[];
}

export interface EducationEntry {
  school: string;
  degree: string;
  field: string;
  year: string;
}

export interface Resume {
  id: string;
  title: string;
  version_name: string;
  role_label: RoleLabel;
  file_path: string;
  original_filename: string;
  file_type: string;
  parsed_text: string;
  skills: string[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  certifications: string[];
  ats_score: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResumeListItem {
  id: string;
  title: string;
  version_name: string;
  role_label: RoleLabel;
  ats_score: number;
  created_at: string;
}

// ── Job ──

export interface MatchResult {
  matched_skills: string[];
  missing_skills: string[];
  confidence: number;
  reason: string;
  recommended_resume_id?: string;
}

export interface JobPosting {
  id: string;
  source_name: string;
  source_job_id: string;
  title: string;
  company: string;
  location?: string;
  remote_type: RemoteType;
  description: string;
  url: string;
  salary_range?: string;
  apply_url?: string;
  skills_required: string[];
  seniority_level?: string;
  industry?: string;
  score: number;
  status: JobStatus;
  match_result: MatchResult;
  tags: string[];
  is_priority_company: boolean;
  discovered_at: string;
  created_at: string;
  updated_at: string;
}

// ── Application ──

export interface ApplicationAttempt {
  id: string;
  job_id: string;
  resume_id: string;
  user_id: string;
  status: ApplicationStatus;
  failure_reason?: string;
  failure_step?: string;
  retry_count: number;
  max_retries: number;
  screenshot_paths: string[];
  logs_path?: string;
  submitted_payload_summary: Record<string, unknown>;
  applied_at?: string;
  created_at: string;
  updated_at: string;
}

// ── Manual Review ──

export interface ManualReviewItem {
  id: string;
  attempt_id: string;
  job_id: string;
  reason: ManualReviewReason;
  severity: Severity;
  failed_step?: string;
  recommended_action?: string;
  evidence_links: string[];
  ai_summary?: string;
  user_notes?: string;
  is_resolved: boolean;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

// ── API Response Types ──

export interface APIResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ErrorResponse {
  success: false;
  error: string;
  detail?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
