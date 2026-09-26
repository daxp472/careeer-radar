'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import {
  AnalysisResponse,
  CandidateFeedbackReportResponse,
  WhatChangedResponse
} from '@/types';
import ReadinessRing from '@/components/ui/ReadinessRing';
import SkillChip from '@/components/ui/SkillChip';
import EmptyState from '@/components/ui/EmptyState';
import { DashboardSkeleton } from '@/components/ui/Skeleton';
import {
  Radar,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  XCircle,
  ExternalLink,
  Briefcase,
  MapPin,
  Calendar,
  Sparkles,
  BarChart2,
  Lightbulb,
  Clock,
  ChevronRight,
  TrendingUp,
  Layers,
  Heart,
  GitCompare,
  Zap,
  Target
} from 'lucide-react';

export default function AnalysisResultPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [feedback, setFeedback] = useState<CandidateFeedbackReportResponse | null>(null);
  const [whatChanged, setWhatChanged] = useState<WhatChangedResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'what_changed' | 'jobs' | 'market' | 'actions'>('overview');

  const [savedJobIds, setSavedJobIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    Promise.all([
      api.getAnalysis(id),
      api.getCandidateFeedback(id).catch(() => null),
      api.getAnalysisDiff(id).catch(() => null),
      api.getWatchlist().catch(() => []),
    ])
      .then(([analysisData, feedbackData, diffData, watchlistData]) => {
        setData(analysisData);
        setFeedback(feedbackData);
        setWhatChanged(diffData);
        setSavedJobIds(new Set(watchlistData.map((w) => w.job_id)));
      })
      .catch((err) => {
        setError(err.message || 'Failed to load analysis results.');
      })
      .finally(() => setIsLoading(false));
  }, [id]);

  const toggleWatchlist = async (jobId: string) => {
    const isSaved = savedJobIds.has(jobId);
    try {
      if (isSaved) {
        await api.removeFromWatchlist(jobId);
        setSavedJobIds((prev) => {
          const next = new Set(prev);
          next.delete(jobId);
          return next;
        });
      } else {
        await api.addToWatchlist(jobId);
        setSavedJobIds((prev) => new Set(prev).add(jobId));
      }
    } catch (e) {
      console.error('Failed to toggle watchlist', e);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <DashboardSkeleton />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto my-16 p-8 rounded-2xl bg-slate-900 border border-red-500/30 text-center space-y-4">
        <XCircle className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-xl font-bold text-white">Analysis Not Found</h2>
        <p className="text-xs text-slate-400">{error || 'Could not locate the requested report.'}</p>
        <Link
          href="/analyze"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition"
        >
          <ArrowLeft className="w-4 h-4" /> Run New Analysis
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Top Breadcrumb & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Command Center
          </Link>
          <div className="flex items-center gap-3">
            <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 font-mono">
              Scan ID: {data.id.slice(0, 8)}
            </span>
            <Link
              href="/analyze"
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition"
            >
              <Zap className="w-3.5 h-3.5" /> New Scan
            </Link>
          </div>
        </div>

        {/* Hero Report Header */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl flex flex-col lg:flex-row lg:items-center justify-between gap-8">
          {/* Left: Role Info & Summary */}
          <div className="space-y-4 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-1.5">
                <Radar className="w-3.5 h-3.5" /> Verified Market Report
              </span>
              <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                {new Date(data.created_at).toLocaleString()}
              </span>
            </div>

            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {data.target_role}
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 flex items-center gap-1.5 mt-1">
                <MapPin className="w-4 h-4 text-slate-500" /> {data.location || 'India / Remote'} • {data.jobs_analyzed} Live Postings Analyzed
              </p>
            </div>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-2xl bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
              {data.summary || feedback?.current_position.summary}
            </p>
          </div>

          {/* Right: Readiness Ring Visualizer */}
          <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-slate-950 border border-slate-800/80 min-w-[200px] shadow-inner">
            <ReadinessRing
              score={data.readiness_score}
              previousScore={whatChanged?.has_previous_analysis ? whatChanged.previous_readiness_score : undefined}
              size={140}
            />
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-1 overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'overview'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Target className="w-4 h-4" /> Overview & Gaps
          </button>
          <button
            onClick={() => setActiveTab('what_changed')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'what_changed'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <GitCompare className="w-4 h-4" /> What Changed?
            {whatChanged && whatChanged.readiness_score_change !== 0 && (
              <span className="ml-1 text-[11px] font-mono font-bold">
                ({whatChanged.readiness_score_change > 0 ? '+' : ''}{whatChanged.readiness_score_change}%)
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('jobs')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'jobs'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Briefcase className="w-4 h-4" /> Matching Jobs ({data.job_matches.length})
          </button>
          <button
            onClick={() => setActiveTab('market')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'market'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <BarChart2 className="w-4 h-4" /> Market Signals ({data.market_skills.length})
          </button>
          <button
            onClick={() => setActiveTab('actions')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition whitespace-nowrap ${
              activeTab === 'actions'
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Lightbulb className="w-4 h-4" /> Action Plan ({data.market_recommendations.length})
          </button>
        </div>

        {/* Tab 1: Overview & Gaps */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Strongest Areas */}
              <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Strongest Market Areas ({data.matched_skills.length})
                  </h3>
                  <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                    Verified
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  You demonstrate verified alignment with these skills repeatedly requested by employers.
                </p>
                <div className="flex flex-wrap gap-2 pt-2">
                  {data.matched_skills.map((g) => (
                    <SkillChip
                      key={g.skill_id}
                      name={g.name}
                      type="matched"
                      proficiency={g.candidate_proficiency}
                      marketFrequencyPct={g.market_frequency_pct}
                    />
                  ))}
                  {data.matched_skills.length === 0 && (
                    <p className="text-xs text-slate-500">No matched skills recorded.</p>
                  )}
                </div>
              </div>

              {/* Top Market Gaps */}
              <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-rose-400" /> High-Impact Gaps ({data.missing_skills.length + data.weak_skills.length})
                  </h3>
                  <span className="text-[11px] font-mono text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded">
                    Priority Focus
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Closing these gaps will yield the highest direct increase in your hiring readiness score.
                </p>
                <div className="flex flex-wrap gap-2 pt-2">
                  {data.missing_skills.map((g) => (
                    <SkillChip
                      key={g.skill_id}
                      name={g.name}
                      type="missing"
                      marketFrequencyPct={g.market_frequency_pct}
                      importance="required"
                    />
                  ))}
                  {data.weak_skills.map((g) => (
                    <SkillChip
                      key={g.skill_id}
                      name={g.name}
                      type="weak"
                      proficiency={g.candidate_proficiency}
                      marketFrequencyPct={g.market_frequency_pct}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Quick Action Plan Preview */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-indigo-400" /> Immediate High-Leverage Actions
                </h3>
                <button
                  onClick={() => setActiveTab('actions')}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-mono"
                >
                  View Full Plan <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.market_recommendations.slice(0, 2).map((rec) => (
                  <div key={rec.skill_name} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-white flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[10px] font-mono font-bold">
                        #{rec.priority}
                      </span>
                      {rec.skill_name}
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {rec.practical_action}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: What Changed */}
        {activeTab === 'what_changed' && (
          <div className="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                  <GitCompare className="w-4 h-4 text-blue-400" /> "What Changed?" Intelligence
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Deterministic delta comparing this scan against your previous baseline.
                </p>
              </div>
              {whatChanged?.has_previous_analysis && (
                <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-300">
                  Delta: <span className={whatChanged.readiness_score_change >= 0 ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                    {whatChanged.readiness_score_change >= 0 ? `+${whatChanged.readiness_score_change}%` : `${whatChanged.readiness_score_change}%`}
                  </span>
                </span>
              )}
            </div>

            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-200 text-xs sm:text-sm leading-relaxed">
              {whatChanged?.summary || 'Baseline analysis recorded. Subsequent scans will show growth deltas.'}
            </div>

            {whatChanged && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-emerald-400 flex items-center gap-1 font-mono">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Gaps Closed ({whatChanged.removed_gaps.length})
                  </span>
                  {whatChanged.removed_gaps.map((g) => (
                    <div key={g.skill_name} className="text-xs text-slate-300 font-mono p-1.5 rounded bg-slate-900">
                      ✓ {g.skill_name}
                    </div>
                  ))}
                  {whatChanged.removed_gaps.length === 0 && <p className="text-xs text-slate-500">None</p>}
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-blue-400 flex items-center gap-1 font-mono">
                    <TrendingUp className="w-3.5 h-3.5" /> Upgrades ({whatChanged.improved_proficiencies.length})
                  </span>
                  {whatChanged.improved_proficiencies.map((g) => (
                    <div key={g.skill_name} className="text-xs text-slate-300 font-mono p-1.5 rounded bg-slate-900">
                      {g.skill_name}: {g.from_proficiency} → {g.to_proficiency}
                    </div>
                  ))}
                  {whatChanged.improved_proficiencies.length === 0 && <p className="text-xs text-slate-500">None</p>}
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-indigo-400 flex items-center gap-1 font-mono">
                    <BarChart2 className="w-3.5 h-3.5" /> Market Shifts ({whatChanged.market_priority_shifts.length})
                  </span>
                  {whatChanged.market_priority_shifts.map((s) => (
                    <div key={s.skill_name} className="text-xs text-slate-300 font-mono p-1.5 rounded bg-slate-900">
                      {s.skill_name}: {s.delta_pct > 0 ? `+${s.delta_pct}%` : `${s.delta_pct}%`} demand
                    </div>
                  ))}
                  {whatChanged.market_priority_shifts.length === 0 && <p className="text-xs text-slate-500">None</p>}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Matching Jobs */}
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-2 text-xs font-mono text-slate-400">
              <span>{data.job_matches.length} Analyzed Job Opportunities</span>
              <span>Sorted by Highest Match Score</span>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {data.job_matches.map((job) => {
                const isSaved = savedJobIds.has(job.job_id);
                const isHigh = job.match_score >= 80;
                const isMed = job.match_score >= 60 && job.match_score < 80;

                return (
                  <div
                    key={job.job_id}
                    className="p-5 sm:p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-md"
                  >
                    <div className="space-y-3 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs text-slate-300 font-semibold">{job.company_name}</span>
                        {job.location && (
                          <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                            <MapPin className="w-3 h-3 text-slate-500" /> {job.location}
                          </span>
                        )}
                      </div>

                      <h3 className="text-lg font-bold text-white hover:text-blue-400 transition">
                        <Link href={`/jobs/${job.job_id}`}>{job.title}</Link>
                      </h3>

                      {/* Required vs Preferred breakdown */}
                      <div className="space-y-2 pt-1">
                        <div className="flex flex-wrap items-center gap-1.5">
                          {job.matched_skills.map((s) => (
                            <span key={s} className="px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              ✓ {s}
                            </span>
                          ))}
                          {job.missing_required.map((s) => (
                            <span key={s} className="px-2 py-0.5 rounded text-[11px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold">
                              Missing Req: {s}
                            </span>
                          ))}
                          {job.missing_preferred.map((s) => (
                            <span key={s} className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                              Missing Pref: {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center md:flex-col justify-between md:justify-center gap-4 pt-3 md:pt-0 border-t md:border-t-0 md:border-l border-slate-800 md:pl-6 min-w-[170px]">
                      <div className="text-left md:text-center">
                        <div className={`text-2xl font-black font-mono ${isHigh ? 'text-emerald-400' : isMed ? 'text-blue-400' : 'text-amber-400'}`}>
                          {job.match_score.toFixed(1)}%
                        </div>
                        <span className="text-[10px] uppercase font-mono text-slate-400">Match Score</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => toggleWatchlist(job.job_id)}
                          className={`p-2 rounded-xl border transition ${
                            isSaved
                              ? 'bg-rose-500/20 border-rose-500 text-rose-400'
                              : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300'
                          }`}
                          title={isSaved ? 'Remove from Watchlist' : 'Save to Watchlist'}
                        >
                          <Heart className={`w-4 h-4 ${isSaved ? 'fill-rose-400' : ''}`} />
                        </button>
                        <Link
                          href={`/jobs/${job.job_id}`}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition flex items-center gap-1"
                        >
                          Gap Breakdown <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 4: Market Signals */}
        {activeTab === 'market' && (
          <div className="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
            <div className="pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-cyan-400" /> Empirical Market Demand Signals
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Exact frequency distribution of technical requirements across all {data.jobs_analyzed} live jobs analyzed in this market scan.
              </p>
            </div>

            <div className="space-y-3">
              {data.market_skills.map((ms) => {
                const isMatched = data.matched_skills.some((m) => m.skill_id === ms.skill_id);
                return (
                  <div key={ms.skill_id} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-sm">{ms.name}</span>
                        <span className="text-slate-500">({ms.category || 'General'})</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${isMatched ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                          {isMatched ? '✓ Verified' : 'Missing Gap'}
                        </span>
                        <span className="font-bold text-white">{ms.frequency_pct}% of jobs</span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${isMatched ? 'bg-emerald-500' : 'bg-rose-500'}`}
                        style={{ width: `${Math.min(100, Math.max(5, ms.frequency_pct))}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 5: Action Plan */}
        {activeTab === 'actions' && (
          <div className="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
            <div className="pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-indigo-400" /> Personalized Skill Bridges & Action Plan
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Targeted recommendations that leverage your existing skills to bridge high-demand market gaps.
              </p>
            </div>

            <div className="space-y-4">
              {data.market_recommendations.map((rec) => (
                <div
                  key={rec.skill_name}
                  className="p-5 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-mono font-bold">
                        #{rec.priority}
                      </span>
                      <h4 className="text-base font-bold text-white">{rec.skill_name}</h4>
                    </div>
                    <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded">
                      Demand: {Math.round(rec.market_frequency_pct)}%
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">
                    <strong className="text-white">Why it matters: </strong>{rec.why_it_matters}
                  </p>

                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-blue-200">
                    <strong className="text-white">Recommended Action: </strong>{rec.practical_action}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
