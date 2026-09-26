export interface User {
  id: string;
  email: string;
  display_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface CandidateSkillInput {
  name: string;
  proficiency: 'beginner' | 'known' | 'intermediate' | 'advanced' | 'expert';
  years_experience?: number;
}

export interface CandidateSkillResponse {
  id: string;
  skill_id: string;
  name: string;
  category?: string;
  proficiency: string;
  confidence: number;
  years_experience: number;
}

export interface ProfileResponse {
  id: string;
  user_id: string;
  target_role?: string;
  target_location?: string;
  remote_preference: string;
  experience_years: number;
  skills: CandidateSkillResponse[];
}

export interface MarketSkillStatItem {
  skill_id: string;
  name: string;
  category?: string;
  jobs_with_skill: number;
  frequency_pct: number;
  total_mentions: number;
  importance_score: number;
}

export interface ReadinessGapItem {
  skill_id: string;
  name: string;
  category?: string;
  gap_type: 'matched' | 'weak' | 'missing';
  market_frequency_pct: number;
  importance_score: number;
  candidate_proficiency?: string;
  priority_score: number;
  explanation?: string;
}

export interface ActionItemSchema {
  id: string;
  skill_name?: string;
  title: string;
  description: string;
  priority: number;
  estimated_effort_hours: number;
  generated_by: string;
}

export interface MarketRecommendationItem {
  skill_id?: string;
  skill_name: string;
  priority: number;
  why_it_matters: string;
  current_state: string;
  recommended_next_step: string;
  practical_action: string;
  evidence: string;
  market_frequency_pct: number;
  recurring_jobs_count: number;
  total_jobs_analyzed: number;
  generated_by?: string;
}

export interface JobMatchSummary {
  job_id: string;
  title: string;
  company_name: string;
  location?: string;
  apply_url?: string;
  posted_at?: string;

  match_score: number;
  required_match_score: number;
  preferred_match_score: number;

  total_required_skills: number;
  matched_required_skills: number;
  missing_required_skills: number;
  weak_required_skills: number;

  total_preferred_skills: number;
  matched_preferred_skills: number;
  missing_preferred_skills: number;
  weak_preferred_skills: number;

  matched_skills: string[];
  missing_required: string[];
  missing_preferred: string[];
  weak_skills: string[];
}

export interface JobSkillItem {
  skill_id: string;
  name: string;
  category?: string;
  importance: 'required' | 'preferred' | 'mentioned';
  mention_count: number;
  evidence?: string;
}

export interface JobCandidateSkillGapItem {
  id?: string;
  skill_id: string;
  name: string;
  category?: string;
  gap_type: 'matched' | 'weak' | 'missing';
  job_importance: 'required' | 'preferred' | 'mentioned';
  candidate_proficiency?: string;
  priority_score: number;
  evidence: string;
  market_frequency_pct?: number;
}

export interface JobCandidateRecommendationItem {
  id?: string;
  skill_id?: string;
  skill_name?: string;
  priority: number;
  why_it_matters: string;
  current_state: string;
  recommended_next_step: string;
  practical_action: string;
  evidence: string;
  generated_by?: string;
}

export interface JobDetailedAnalysisResponse {
  job_id: string;
  title: string;
  company_name: string;
  location?: string;
  remote_type?: string;
  description?: string;
  apply_url?: string;
  posted_at?: string;

  match_score: number;
  required_match_score: number;
  preferred_match_score: number;

  total_skills_count: number;
  total_required_skills: number;
  matched_required_skills: number;
  missing_required_skills: number;
  weak_required_skills: number;

  total_preferred_skills: number;
  matched_preferred_skills: number;
  missing_preferred_skills: number;
  weak_preferred_skills: number;

  skills: JobSkillItem[];
  gaps: JobCandidateSkillGapItem[];
  matched_skills: JobCandidateSkillGapItem[];
  missing_required_gaps: JobCandidateSkillGapItem[];
  missing_preferred_gaps: JobCandidateSkillGapItem[];
  weak_gaps: JobCandidateSkillGapItem[];

  recommendations: JobCandidateRecommendationItem[];
}

export interface AnalysisResponse {
  id: string;
  status: string;
  target_role: string;
  location?: string;
  jobs_analyzed: number;
  readiness_score: number;
  summary?: string;
  created_at: string;
  market_skills: MarketSkillStatItem[];
  gaps: ReadinessGapItem[];
  matched_skills: ReadinessGapItem[];
  weak_skills: ReadinessGapItem[];
  missing_skills: ReadinessGapItem[];
  action_items: ActionItemSchema[];
  market_recommendations: MarketRecommendationItem[];
  job_matches: JobMatchSummary[];
}

export interface RoleItem {
  id: string;
  name: string;
  normalized_name: string;
}

export interface SkillItem {
  id: string;
  name: string;
  normalized_name: string;
  category?: string;
  aliases: string[];
}

// Phase 3 Types
export interface DatabaseJobItem {
  id: string;
  title: string;
  company_name: string;
  location?: string;
  remote_type?: string;
  description?: string;
  apply_url?: string;
  status: 'active' | 'stale' | 'expired' | 'removed';
  first_seen_at?: string;
  last_seen_at?: string;
  posted_at?: string;
  updated_at?: string;
  skills: JobSkillItem[];
  match_score?: number;
  missing_skills: string[];
  matched_skills: string[];
  is_saved: boolean;
}

export interface DatabaseJobSearchResponse {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  jobs: DatabaseJobItem[];
  applied_filters: Record<string, any>;
  database_last_refreshed_at?: string;
}

export interface WatchlistItem {
  id: string;
  job_id: string;
  title: string;
  company_name: string;
  location?: string;
  remote_type?: string;
  apply_url?: string;
  status: string;
  saved_at: string;
  last_checked_at: string;
  match_score?: number;
  matched_skills: string[];
  missing_skills: string[];
  missing_required?: string[];
}

export interface SkillProgressHistoryItem {
  id: string;
  skill_id: string;
  skill_name: string;
  category?: string;
  from_proficiency: string;
  to_proficiency: string;
  recorded_at: string;
}

export interface AlertSettings {
  id: string;
  user_id: string;
  enabled: boolean;
  frequency: string;
  day_of_week: string;
  time_of_day: string;
  timezone: string;
  minimum_match_score: number;
  email_enabled: boolean;
  in_app_enabled: boolean;
  last_scan_at?: string;
  next_scan_at?: string;
}

export interface CandidateScanHistoryItem {
  id: string;
  started_at: string;
  completed_at?: string;
  jobs_checked: number;
  jobs_matched: number;
  jobs_above_threshold: number;
  email_sent: boolean;
  status: string;
  error_message?: string;
}

export interface NotificationItem {
  id: string;
  type: 'weekly_job_digest' | 'new_job_match' | 'reminder' | 'job_update';
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: NotificationItem[];
  unread_count: number;
}

export interface AdminStatusResponse {
  total_active_jobs: number;
  total_stale_jobs: number;
  total_expired_jobs: number;
  total_jobs: number;
  last_refresh_at?: string;
  recent_reports: Array<Record<string, any>>;
}

// Phase 4 Intelligence Types
export interface SkillChangeItem {
  skill_name: string;
  category?: string;
  from_proficiency?: string;
  to_proficiency: string;
  change_type: 'acquired' | 'improved' | 'weakened' | 'removed_gap' | 'new_gap';
  market_frequency_pct?: number;
}

export interface WhatChangedResponse {
  has_previous_analysis: boolean;
  current_analysis_id: string;
  previous_analysis_id?: string;
  current_created_at: string;
  previous_created_at?: string;
  current_readiness_score: number;
  previous_readiness_score?: number;
  readiness_score_change: number;
  current_jobs_count: number;
  previous_jobs_count?: number;
  newly_acquired_skills: SkillChangeItem[];
  improved_proficiencies: SkillChangeItem[];
  weakened_skills: SkillChangeItem[];
  removed_gaps: SkillChangeItem[];
  new_gaps: SkillChangeItem[];
  jobs_above_threshold_change: number;
  market_priority_shifts: Array<{
    skill_name: string;
    previous_frequency_pct: number;
    current_frequency_pct: number;
    delta_pct: number;
  }>;
  summary: string;
}

export interface CandidateFeedbackSection {
  title: string;
  badge?: string;
  summary: string;
  items: Array<Record<string, any>>;
}

export interface CandidateFeedbackReportResponse {
  analysis_id: string;
  target_role: string;
  location: string;
  readiness_score: number;
  alignment_tier: string;
  analyzed_at: string;
  current_position: CandidateFeedbackSection;
  strongest_areas: CandidateFeedbackSection;
  biggest_gaps: CandidateFeedbackSection;
  what_changed: WhatChangedResponse;
  market_signals: CandidateFeedbackSection;
  personalized_action_plan: MarketRecommendationItem[];
}


