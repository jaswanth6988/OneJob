import { APIResponse, ErrorResponse, TokenResponse, UserProfile, Resume, ResumeListItem } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

class ApiClient {
  private refreshing: Promise<boolean> | null = null;
  private async renewSession(): Promise<boolean> {
    if (this.refreshing) return this.refreshing;
    this.refreshing = (async () => {
      const token = localStorage.getItem('refresh_token');
      if (!token) return false;
      try {
        const response = await fetch(`${BASE_URL}/auth/refresh`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh_token:token})});
        if (!response.ok) return false;
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return true;
      } catch { return false; }
    })();
    try { return await this.refreshing; } finally { this.refreshing = null; }
  }

  private getHeaders() {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}, retried = false): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const headers = this.getHeaders();
    
    // Allow overriding headers, e.g. for multipart/form-data
    const finalHeaders = options.headers ? { ...headers, ...options.headers } : headers;
    
    // Remove Content-Type if it's FormData, let browser set it with boundary
    if (options.body instanceof FormData && finalHeaders && 'Content-Type' in finalHeaders) {
      delete (finalHeaders as any)['Content-Type'];
    }

    const response = await fetch(url, { ...options, headers: finalHeaders });
    
    if (response.status === 401 && !retried && typeof window !== 'undefined' && await this.renewSession()) {
      return this.request<T>(endpoint, options, true);
    }
    if (!response.ok) {
      const error: ErrorResponse = await response.json().catch(() => ({ error: 'An error occurred' }));
      if (response.status === 401 && typeof window !== 'undefined') { localStorage.removeItem('token'); window.dispatchEvent(new Event('auth-expired')); }
      const detail = error.detail;
      throw new Error(typeof detail === 'string' ? detail : error.error || `Request failed (${response.status}). Please try again.`);
    }
    
    return response.status === 204 ? undefined as T : response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data instanceof FormData ? data : JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  auth = {
    register: (data: any) => this.post<APIResponse<TokenResponse>>('/auth/register', data),
    login: (data: any) => this.post<APIResponse<TokenResponse>>('/auth/login', data),
    refresh: () => this.renewSession(),
    getMe: () => this.get<APIResponse<UserProfile>>('/auth/me'),
  };

  profile = {
    getProfile: () => this.get<APIResponse<UserProfile>>('/profile'),
    updateProfile: (data: Partial<UserProfile>) => this.put<APIResponse<UserProfile>>('/profile', data),
  };

  resumes = {
    uploadResume: (file: File, title: string, versionName: string, roleLabel: string = 'General') => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('version_name', versionName);
      formData.append('role_label', roleLabel);
      return this.post<APIResponse<Resume>>('/resumes/upload', formData);
    },
    getResumes: () => this.get<APIResponse<ResumeListItem[]>>('/resumes'),
    getResume: (id: string) => this.get<APIResponse<Resume>>(`/resumes/${id}`),
    updateResume: (id: string, data: Partial<Resume>) => this.put<APIResponse<Resume>>(`/resumes/${id}`, data),
    deleteResume: (id: string) => this.delete<APIResponse<void>>(`/resumes/${id}`),
  };

    applications = {
    list: (status?: string) => this.get<any>(`/applications${status ? `?status=${status}` : ''}`),
    start: (jobId: string, mode: 'DRY_RUN' | 'LIVE' = 'DRY_RUN', resumeId?: string) => this.post<any>(`/applications/start/${jobId}`, { mode, resume_id: resumeId }),
    getDetails: (appId: string) => this.get<any>(`/applications/${appId}`),
  };

  tailor = {
    analyze: (jobId: string, resumeId?: string) =>
      this.post<any>(`/tailor/${jobId}${resumeId ? `?resume_id=${resumeId}` : ''}`, {}),
  };

  interview = {
    generateQuestions: (jobId: string, resumeId?: string) =>
      this.post<any>(`/interview/questions/${jobId}${resumeId ? `?resume_id=${resumeId}` : ''}`, {}),
    evaluateAnswer: (jobId: string, question: string, answer: string, resumeId?: string) =>
      this.post<any>('/interview/evaluate', { job_id: jobId, question, answer, resume_id: resumeId }),
  };

  chat = {
    send: (message: string, history: { role: string; content: string }[] = []) =>
      this.post<any>('/chat', { message, history }),
  };
}

export const api = new ApiClient();
