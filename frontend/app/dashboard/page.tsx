'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import {
  AnalysisResponse,
  WatchlistItem,
  SkillProgressHistoryItem,
  AlertSettings,
  CandidateScanHistoryItem,
  ProfileResponse
} from '@/types';
import {
  Radar,
  ArrowRight,
  Calendar,
  MapPin,
  Briefcase,
  Layers,
  Sparkles,
  TrendingUp,
  Loader2,
  Plus,
  Heart,
  Clock,
  CheckCircle2,
  AlertCircle,
  Bell,
  Play,
  Settings,
  ExternalLink,
  ChevronRight,
  Zap,
  Trash2
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();

  const [activeTab, setActiveTab] = useState<'watchlist' | 'progress' | 'radar_scans' | 'analyses'>('watchlist');
  const [isLoading, setIsLoading] = useState(true);

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [alertSettings, setAlertSettings] = useState<AlertSettings | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [skillProgress, setSkillProgress] = useState<SkillProgressHistoryItem[]>([]);
  const [scanHistory, setScanHistory] = useState<CandidateScanHistoryItem[]>([]);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResponse[]>([]);

  const [isScanningNow, setIsScanningNow] = useState(false);
  const [scanMessage, setScanMessage] = useState<string | null>(null);

  const loadAllData = async () => {
    if (!user) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    try {
      const [profData, settingsData, watchData, progData, scanData, histData] = await Promise.all([
        api.getProfile().catch(() => null),
        api.getAlertSettings().catch(() => null),
        api.getWatchlist().catch(() => []),
        api.getSkillProgress().catch(() => []),
        api.getScanHistory().catch(() => []),
        api.getUserHistory().catch(() => []),
      ]);

      setProfile(profData);
      setAlertSettings(settingsData);
      setWatchlist(watchData);
      setSkillProgress(progData);
      setScanHistory(scanData);
      setAnalysisHistory(histData);
    } catch (e) {
      console.error('Failed loading dashboard data', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [user]);

  const handleScanNow = async () => {
    setIsScanningNow(true);
    setScanMessage(null);
    try {
      const res = await api.scanNow();
      setScanMessage(`Scan finished! Checked ${res.jobs_checked} database jobs (${res.jobs_above_threshold} matched threshold).`);
      // Reload scans & watchlist
      const [scans, saved] = await Promise.all([api.getScanHistory(), api.getWatchlist()]);
      setScanHistory(scans);
      setWatchlist(saved);
    } catch (e) {
      setScanMessage('Failed to trigger scan.');
    } finally {
      setIsScanningNow(false);
    }
  };

  const handleRemoveFromWatchlist = async (jobId: string) => {
    try {
      await api.removeFromWatchlist(jobId);
      setWatchlist(prev => prev.filter(item => item.job_id !== jobId));
    } catch (e) {
      console.error('Failed to remove from watchlist', e);
    }
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="p-10 rounded-3xl bg-slate-900 border border-slate-800 text-center max-w-xl mx-auto shadow-2xl space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mx-auto">
            <Radar className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Continuous Career Radar</h2>
          <p className="text-sm text-slate-400">
            Sign in to track your skill progression, save dream jobs to your watchlist, and enable weekly automated market radar alerts.
          </p>
          <div className="pt-4 flex items-center justify-center gap-3">
            <Link
              href="/auth/login"
              className="px-5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm font-semibold hover:bg-slate-700 transition"
            >
              Sign In
            </Link>
            <Link
              href="/auth/register"
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-md shadow-blue-500/20 transition"
            >
              Create Free Account
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Top Candidate Hub Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Candidate Monitoring Active
              </span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
              My CareerRadar
            </h1>
            <p className="mt-1 text-slate-400 text-sm">
              {profile?.target_role ? `Targeting ${profile.target_role}` : 'Candidate Profile'}{' '}
              {profile?.target_location ? `in ${profile.target_location}` : ''} • Continuous market watch
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleScanNow}
              disabled={isScanningNow}
              className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-lg shadow-blue-500/20 transition"
            >
              <Play className={`w-3.5 h-3.5 ${isScanningNow ? 'animate-spin' : ''}`} />
              {isScanningNow ? 'Scanning Market...' : 'Run Scan Now'}
            </button>
            <Link
              href="/profile"
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold rounded-xl transition"
            >
              <Settings className="w-3.5 h-3.5 text-slate-400" /> Radar Settings
            </Link>
          </div>
        </div>

        {/* Scan Message banner */}
        {scanMessage && (
          <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs flex items-center justify-between">
            <span>{scanMessage}</span>
            <button onClick={() => setScanMessage(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Summary Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Weekly Radar Status */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Weekly Job Radar</span>
              <Bell className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-xl font-bold text-white flex items-center gap-2">
              {alertSettings?.enabled ? (
                <span className="text-emerald-400">Enabled</span>
              ) : (
                <span className="text-slate-500">Disabled</span>
              )}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              {alertSettings?.enabled
                ? `Every ${alertSettings.day_of_week.toUpperCase()} at ${alertSettings.time_of_day}`
                : 'Turn on in Radar Settings'}
            </p>
          </div>

          {/* Min Match Threshold */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Match Threshold</span>
              <Sparkles className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-xl font-bold text-indigo-400 font-mono">
              {alertSettings?.minimum_match_score || 80}%
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Minimum score for email digest
            </p>
          </div>

          {/* Watchlisted Jobs */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Saved Jobs</span>
              <Heart className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-xl font-bold text-white font-mono">
              {watchlist.length}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Monitored opportunities
            </p>
          </div>

          {/* Tracked Skills */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Candidate Skills</span>
              <TrendingUp className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-xl font-bold text-cyan-400 font-mono">
              {profile?.skills.length || 0}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              {skillProgress.length} recorded evolutions
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-1 overflow-x-auto">
          <button
            onClick={() => setActiveTab('watchlist')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'watchlist'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Heart className="w-4 h-4" /> Watchlist ({watchlist.length})
          </button>
          <button
            onClick={() => setActiveTab('progress')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'progress'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <TrendingUp className="w-4 h-4" /> Skill Evolution ({skillProgress.length})
          </button>
          <button
            onClick={() => setActiveTab('radar_scans')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'radar_scans'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Clock className="w-4 h-4" /> Automated Scans ({scanHistory.length})
          </button>
          <button
            onClick={() => setActiveTab('analyses')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'analyses'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Layers className="w-4 h-4" /> Market Analyses ({analysisHistory.length})
          </button>
        </div>

        {/* Tab 1: Watchlist */}
        {activeTab === 'watchlist' && (
          <div className="space-y-4">
            {isLoading ? (
              <div className="py-16 text-center text-slate-500 text-xs">Loading watchlist...</div>
            ) : watchlist.length === 0 ? (
              <div className="p-12 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-3">
                <Heart className="w-10 h-10 text-slate-600 mx-auto" />
                <h3 className="text-base font-bold text-white">Your Watchlist is empty</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Save jobs from the database or live market search to continuously monitor updates and dynamically track your match score.
                </p>
                <Link
                  href="/jobs"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition mt-2"
                >
                  Explore Database Jobs <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {watchlist.map((item) => (
                  <div
                    key={item.id}
                    className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
                  >
                    <div className="space-y-2 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs text-slate-300 font-semibold">{item.company_name}</span>
                        {item.location && (
                          <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                            <MapPin className="w-3 h-3 text-slate-500" /> {item.location}
                          </span>
                        )}
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {item.status}
                        </span>
                      </div>

                      <h3 className="text-base font-bold text-white hover:text-blue-400 transition">
                        <Link href={`/jobs/${item.job_id}`}>{item.title}</Link>
                      </h3>

                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        {(item.matched_skills || []).map((s) => (
                          <span key={s} className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            ✓ {s}
                          </span>
                        ))}
                        {(item.missing_skills || item.missing_required || []).map((s) => (
                          <span key={s} className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20">
                            Missing: {s}
                          </span>
                        ))}
                      </div>

                      <div className="text-[10px] text-slate-500 font-mono pt-1 flex items-center gap-3">
                        <span>Saved: {new Date(item.saved_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>Last evaluated: {new Date(item.last_checked_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex items-center md:flex-col justify-between md:justify-center gap-4 pt-3 md:pt-0 border-t md:border-t-0 md:border-l border-slate-800 md:pl-6 min-w-[160px]">
                      {item.match_score !== null && item.match_score !== undefined && (
                        <div className="text-left md:text-center">
                          <div className="text-2xl font-black font-mono text-blue-400">
                            {item.match_score.toFixed(1)}%
                          </div>
                          <span className="text-[10px] uppercase font-mono text-slate-400">Dynamic Match</span>
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleRemoveFromWatchlist(item.job_id)}
                          className="p-2 rounded-xl bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-700 transition"
                          title="Remove from Watchlist"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                        <Link
                          href={`/jobs/${item.job_id}`}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition flex items-center gap-1"
                        >
                          Gaps <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Skill Progress Timeline */}
        {activeTab === 'progress' && (
          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs">
              <span className="font-bold">Real Skill Evolution Tracking:</span> As you update your proficiency in your candidate profile, CareerRadar chronologically records each milestone to illustrate your market readiness trajectory.
            </div>

            {skillProgress.length === 0 ? (
              <div className="p-12 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-2">
                <TrendingUp className="w-10 h-10 text-slate-600 mx-auto" />
                <h3 className="text-base font-bold text-white">No Skill Changes Recorded Yet</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Update your candidate skills in your profile to start logging your growth milestones.
                </p>
                <Link
                  href="/profile"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition mt-2"
                >
                  Edit Candidate Skills <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ) : (
              <div className="relative border-l border-slate-800 ml-4 space-y-6 py-2">
                {skillProgress.map((item, idx) => (
                  <div key={item.id || idx} className="relative pl-6 group">
                    {/* Timeline Node */}
                    <div className="absolute -left-2 top-1.5 w-4 h-4 rounded-full bg-slate-900 border-2 border-blue-500 group-hover:border-cyan-400 transition"></div>
                    
                    <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800/80 shadow-md space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-white text-sm">{item.skill_name}</span>
                        <span className="text-slate-500 font-mono text-[11px]">
                          {new Date(item.recorded_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs font-mono pt-1">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 capitalize">
                          {item.from_proficiency || 'missing'}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold capitalize">
                          {item.to_proficiency}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Automated Radar Scans */}
        {activeTab === 'radar_scans' && (
          <div className="space-y-4">
            {scanHistory.length === 0 ? (
              <div className="p-12 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-2">
                <Clock className="w-10 h-10 text-slate-600 mx-auto" />
                <h3 className="text-base font-bold text-white">No Automated Scans Executed Yet</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Click "Run Scan Now" above or wait for your scheduled weekly radar execution.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {scanHistory.map((scan) => (
                  <div
                    key={scan.id}
                    className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white">
                          Scan {new Date(scan.started_at).toLocaleString()}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
                          scan.status === 'completed'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-rose-500/10 text-rose-400'
                        }`}>
                          {scan.status}
                        </span>
                      </div>
                      <div className="text-slate-400 font-mono text-[11px] flex items-center gap-3">
                        <span>Checked {scan.jobs_checked} database jobs</span>
                        <span>•</span>
                        <span className="text-blue-400">{scan.jobs_above_threshold} above threshold</span>
                      </div>
                    </div>

                    <div className="text-right font-mono text-[11px]">
                      {scan.email_sent ? (
                        <span className="text-emerald-400">📧 Digest Sent</span>
                      ) : (
                        <span className="text-slate-500">In-App Signal Only</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 4: Market Analyses (Phase 1 & 2 History) */}
        {activeTab === 'analyses' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysisHistory.length === 0 ? (
              <div className="col-span-full p-12 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-2">
                <Layers className="w-10 h-10 text-slate-600 mx-auto" />
                <h3 className="text-base font-bold text-white">No Market Analysis Runs Yet</h3>
                <Link
                  href="/analyze"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition mt-2"
                >
                  Run Market Analysis <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ) : (
              analysisHistory.map((scan) => (
                <Link
                  key={scan.id}
                  href={`/analysis/${scan.id}`}
                  className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                        {scan.jobs_analyzed} Live Jobs
                      </span>
                      <span className="text-xs text-slate-500">
                        {new Date(scan.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-white mb-1">{scan.target_role}</h3>
                    <p className="text-xs text-slate-400 flex items-center gap-1 mb-4">
                      <MapPin className="w-3 h-3 text-slate-500" /> {scan.location || 'Global'}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] uppercase font-mono text-slate-400 block">Readiness</span>
                      <span className="text-xl font-extrabold font-mono text-blue-400">{scan.readiness_score}%</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs font-semibold text-cyan-400">
                      View Report <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>
        )}

      </div>
    </div>
  );
}
