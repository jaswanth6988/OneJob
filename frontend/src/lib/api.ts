import { APIResponse, ErrorResponse, TokenResponse, UserProfile, Resume, ResumeListItem } from './types';

const BASE_URL = 'http://localhost:8000/api';

class ApiClient {
  private getHeaders() {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const headers = this.getHeaders();
    
    // Allow overriding headers, e.g. for multipart/form-data
    const finalHeaders = options.headers ? { ...headers, ...options.headers } : headers;
    
    // Remove Content-Type if it's FormData, let browser set it with boundary
    if (options.body instanceof FormData && finalHeaders && 'Content-Type' in finalHeaders) {
      delete (finalHeaders as any)['Content-Type'];
    }

    const response = await fetch(url, { ...options, headers: finalHeaders });
    
    if (!response.ok) {
      const error: ErrorResponse = await response.json().catch(() => ({ error: 'An error occurred' }));
      throw new Error(error.error || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
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
    refresh: () => this.post<APIResponse<TokenResponse>>('/auth/refresh', {}),
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
}

export const api = new ApiClient();
