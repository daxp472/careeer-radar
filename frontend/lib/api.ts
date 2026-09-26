import {
  AuthResponse,
  AnalysisResponse,
  ProfileResponse,
  RoleItem,
  SkillItem,
  User,
  CandidateSkillInput,
  JobDetailedAnalysisResponse,
  JobMatchSummary,
  MarketRecommendationItem,
  DatabaseJobSearchResponse,
  WatchlistItem,
  SkillProgressHistoryItem,
  AlertSettings,
  CandidateScanHistoryItem,
  NotificationListResponse,
  AdminStatusResponse,
  WhatChangedResponse,
  CandidateFeedbackReportResponse
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('careerradar_token');
  }

  private getHeaders(customHeaders: HeadersInit = {}): HeadersInit {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return { ...headers, ...customHeaders };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    const headers = this.getHeaders(options.headers || {});

    try {
      const res = await fetch(url, {
        ...options,
        headers,
      });

      if (!res.ok) {
        let errorMessage = `HTTP ${res.status}: ${res.statusText}`;
        try {
          const errorData = await res.json();
          if (errorData?.detail) {
            errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
          }
        } catch {
          // Response body is not JSON
        }
        throw new Error(errorMessage);
      }

      return await res.json();
    } catch (err: any) {
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        throw new Error(`Unable to connect to CareerRadar API server at ${API_BASE_URL}. Please ensure the backend is running.`);
      }
      throw err;
    }
  }

  // Health
  async checkHealth(): Promise<any> {
    return this.request('/health');
  }

  // Auth
  async register(data: { email: string; password: string; display_name: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // Roles & Skills
  async getRoles(): Promise<RoleItem[]> {
    return this.request<RoleItem[]>('/roles');
  }

  async getSkills(category?: string): Promise<SkillItem[]> {
    const endpoint = category ? `/skills?category=${encodeURIComponent(category)}` : '/skills';
    return this.request<SkillItem[]>(endpoint);
  }

  async searchSkills(query: string): Promise<SkillItem[]> {
    return this.request<SkillItem[]>(`/skills/search?q=${encodeURIComponent(query)}`);
  }

  // Profile
  async getProfile(): Promise<ProfileResponse> {
    return this.request<ProfileResponse>('/profile');
  }

  async updateProfile(data: {
    target_role_name?: string;
    target_location?: string;
    remote_preference?: string;
    experience_years?: number;
    skills?: CandidateSkillInput[];
  }): Promise<ProfileResponse> {
    return this.request<ProfileResponse>('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Analyses
  async createAnalysis(payload: {
    target_role: string;
    location?: string;
    remote_preference?: string;
    skills: CandidateSkillInput[];
    experience_years?: number;
  }): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>('/analyses', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getAnalysis(id: string): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>(`/analyses/${id}`);
  }

  async getAnalysisJobs(id: string): Promise<JobMatchSummary[]> {
    return this.request<JobMatchSummary[]>(`/analyses/${id}/jobs`);
  }

  async getAnalysisRecommendations(id: string): Promise<MarketRecommendationItem[]> {
    return this.request<MarketRecommendationItem[]>(`/analyses/${id}/recommendations`);
  }

  async getUserHistory(): Promise<AnalysisResponse[]> {
    return this.request<AnalysisResponse[]>('/analyses/user/history');
  }

  // Phase 4: What Changed & Candidate Intelligence
  async getAnalysisDiff(analysisId: string, baselineId?: string): Promise<WhatChangedResponse> {
    const endpoint = baselineId
      ? `/analyses/${analysisId}/diff?baseline_id=${encodeURIComponent(baselineId)}`
      : `/analyses/${analysisId}/diff`;
    return this.request<WhatChangedResponse>(endpoint);
  }

  async getCandidateFeedback(analysisId: string): Promise<CandidateFeedbackReportResponse> {
    return this.request<CandidateFeedbackReportResponse>(`/analyses/${analysisId}/feedback`);
  }

  // Job-Level Analysis (Phase 2)
  async getJobAnalysis(jobId: string, analysisId?: string): Promise<JobDetailedAnalysisResponse> {
    const endpoint = analysisId
      ? `/jobs/${jobId}/analysis?analysis_id=${encodeURIComponent(analysisId)}`
      : `/jobs/${jobId}/analysis`;
    return this.request<JobDetailedAnalysisResponse>(endpoint);
  }

  async analyzeSpecificJob(jobId: string, skills: CandidateSkillInput[]): Promise<JobDetailedAnalysisResponse> {
    return this.request<JobDetailedAnalysisResponse>(`/jobs/${jobId}/analyze`, {
      method: 'POST',
      body: JSON.stringify(skills),
    });
  }

  // Phase 3: Central Database Job Search
  async searchDatabaseJobs(params: {
    role?: string;
    location?: string;
    remote_type?: string;
    skills?: string;
    status?: string;
    minimum_match?: number;
    sort?: string;
    page?: number;
    limit?: number;
  }): Promise<DatabaseJobSearchResponse> {
    const queryParams = new URLSearchParams();
    if (params.role) queryParams.append('role', params.role);
    if (params.location) queryParams.append('location', params.location);
    if (params.remote_type) queryParams.append('remote_type', params.remote_type);
    if (params.skills) queryParams.append('skills', params.skills);
    if (params.status) queryParams.append('status', params.status);
    if (params.minimum_match !== undefined && params.minimum_match !== null) {
      queryParams.append('minimum_match', params.minimum_match.toString());
    }
    if (params.sort) queryParams.append('sort', params.sort);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());

    return this.request<DatabaseJobSearchResponse>(`/jobs/search?${queryParams.toString()}`);
  }

  // Watchlist
  async getWatchlist(): Promise<WatchlistItem[]> {
    return this.request<WatchlistItem[]>('/watchlist');
  }

  async addToWatchlist(jobId: string): Promise<any> {
    return this.request(`/watchlist/${jobId}`, {
      method: 'POST',
    });
  }

  async removeFromWatchlist(jobId: string): Promise<any> {
    return this.request(`/watchlist/${jobId}`, {
      method: 'DELETE',
    });
  }

  // Skill Progress Timeline
  async getSkillProgress(): Promise<SkillProgressHistoryItem[]> {
    return this.request<SkillProgressHistoryItem[]>('/profile/progress');
  }

  // Automation & Weekly Job Radar
  async getAlertSettings(): Promise<AlertSettings> {
    return this.request<AlertSettings>('/automation/settings');
  }

  async updateAlertSettings(settings: Partial<AlertSettings>): Promise<AlertSettings> {
    return this.request<AlertSettings>('/automation/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  async scanNow(): Promise<any> {
    return this.request('/automation/scan-now', {
      method: 'POST',
    });
  }

  async getScanHistory(): Promise<CandidateScanHistoryItem[]> {
    return this.request<CandidateScanHistoryItem[]>('/automation/scans');
  }

  // In-App Notifications
  async getNotifications(unreadOnly = false): Promise<NotificationListResponse> {
    return this.request<NotificationListResponse>(`/notifications?unread_only=${unreadOnly}`);
  }

  async markNotificationRead(id: string): Promise<any> {
    return this.request(`/notifications/${id}/read`, {
      method: 'PATCH',
    });
  }

  async markAllNotificationsRead(): Promise<any> {
    return this.request('/notifications/read-all', {
      method: 'PATCH',
    });
  }

  // Admin Monitoring
  async getAdminStatus(): Promise<AdminStatusResponse> {
    return this.request<AdminStatusResponse>('/jobs/admin/status');
  }

  async triggerAdminRefresh(): Promise<any> {
    return this.request('/jobs/admin/refresh?run_async=true', {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();
