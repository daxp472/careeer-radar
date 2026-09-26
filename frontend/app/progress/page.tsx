'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import {
  AnalysisResponse,
  SkillProgressHistoryItem,
  WhatChangedResponse,
  ProfileResponse
} from '@/types';
import ReadinessRing from '@/components/ui/ReadinessRing';
import SkillChip from '@/components/ui/SkillChip';
import EmptyState from '@/components/ui/EmptyState';
import { DashboardSkeleton } from '@/components/ui/Skeleton';
import {
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Calendar,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Clock,
  Briefcase,
  History,
  Activity,
  Award,
  ChevronRight,
  GitCompare,
  Zap
} from 'lucide-react';

export default function ProgressPage() {
  const { user } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [skillProgress, setSkillProgress] = useState<SkillProgressHistoryItem[]>([]);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResponse[]>([]);
  const [whatChanged, setWhatChanged] = useState<WhatChangedResponse | null>(null);

  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null);
  const [selectedBaselineId, setSelectedBaselineId] = useState<string | null>(null);

  const loadData = async () => {
    if (!user) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    try {
      const [profData, progData, histData] = await Promise.all([
        api.getProfile().catch(() => null),
        api.getSkillProgress().catch(() => []),
        api.getUserHistory().catch(() => []),
      ]);

      setProfile(profData);
      setSkillProgress(progData);
      setAnalysisHistory(histData);

      if (histData && histData.length > 0) {
        const latest = histData[0];
        setSelectedAnalysisId(latest.id);
        const baseline = histData.length > 1 ? histData[1].id : undefined;
        setSelectedBaselineId(baseline || null);

        const diffData = await api.getAnalysisDiff(latest.id, baseline).catch(() => null);
        setWhatChanged(diffData);
      }
    } catch (e) {
      console.error('Failed loading progress data', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleCompare = async (analysisId: string, baselineId?: string) => {
    setSelectedAnalysisId(analysisId);
    setSelectedBaselineId(baselineId || null);
    try {
      const diffData = await api.getAnalysisDiff(analysisId, baselineId);
      setWhatChanged(diffData);
    } catch (e) {
      console.error('Diff calculation failed', e);
    }
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <EmptyState
          icon={TrendingUp}
          title="Candidate Progress Intelligence"
          description="Sign in to view your career progression trajectory, verified skill evolutions, and what changed across market scans."
          actionText="Sign In"
          actionHref="/auth/login"
        />
      </div>
    );
  }

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  const latestAnalysis = analysisHistory.length > 0 ? analysisHistory[0] : null;
  const previousAnalysis = analysisHistory.length > 1 ? analysisHistory[1] : null;
  const scoreDelta = latestAnalysis && previousAnalysis
    ? Number((latestAnalysis.readiness_score - previousAnalysis.readiness_score).toFixed(1))
    : null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> Candidate Progress Engine
              </span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Career Trajectory & Growth
            </h1>
            <p className="mt-1 text-slate-400 text-sm">
              Empirical tracking of your market readiness delta, resolved skill gaps, and verified proficiency upgrades over time.
            </p>
          </div>

          <Link
            href="/analyze"
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-blue-500/20 transition self-start md:self-auto"
          >
            <Zap className="w-3.5 h-3.5" /> Check Market Readiness Now
          </Link>
        </div>

        {/* Top Summary Metric Row */}
        {latestAnalysis ? (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {/* Readiness Ring Card */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-center shadow-lg">
              <ReadinessRing
                score={latestAnalysis.readiness_score}
                previousScore={previousAnalysis?.readiness_score}
                size={130}
              />
              <span className="text-xs text-slate-400 mt-2 font-mono">
                {latestAnalysis.target_role} ({latestAnalysis.location || 'Global'})
              </span>
            </div>

            {/* Growth Delta Card */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2 flex flex-col justify-between shadow-lg">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>Readiness Delta</span>
                <Award className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <div className="text-3xl font-black font-mono text-white flex items-center gap-2">
                  {scoreDelta !== null ? (
                    scoreDelta >= 0 ? (
                      <span className="text-emerald-400">+{scoreDelta}%</span>
                    ) : (
                      <span className="text-rose-400">{scoreDelta}%</span>
                    )
                  ) : (
                    <span className="text-blue-400">Baseline</span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  {scoreDelta !== null && scoreDelta >= 0
                    ? 'Growth observed since your previous analysis.'
                    : 'Initial benchmark recorded. Keep upgrading skills to see growth.'}
                </p>
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-[11px] text-slate-500 font-mono">
                {analysisHistory.length} total market scans logged
              </div>
            </div>

            {/* Skill Milestones Card */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2 flex flex-col justify-between shadow-lg">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>Skill Milestones</span>
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <div className="text-3xl font-black font-mono text-indigo-400">
                  {skillProgress.length}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Chronological proficiency level upgrades verified in profile.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-[11px] text-slate-500 font-mono">
                {profile?.skills.length || 0} active candidate skills
              </div>
            </div>

            {/* Gap Reduction Card */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2 flex flex-col justify-between shadow-lg">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>Resolved Gaps</span>
                <CheckCircle2 className="w-4 h-4 text-cyan-400" />
              </div>
              <div>
                <div className="text-3xl font-black font-mono text-cyan-400">
                  {whatChanged?.removed_gaps.length || 0}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Market requirement gaps eliminated compared to baseline.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-[11px] text-slate-500 font-mono">
                {latestAnalysis.missing_skills.length} remaining high-impact gaps
              </div>
            </div>
          </div>
        ) : (
          <EmptyState
            icon={TrendingUp}
            title="No Readiness History Logged"
            description="Run your first live market scan to establish your baseline readiness score and start tracking your growth."
            actionText="Run First Analysis"
            actionHref="/analyze"
          />
        )}

        {/* What Changed Intelligence Section */}
        {whatChanged && (
          <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <GitCompare className="w-4 h-4 text-blue-400" />
                  <h2 className="text-lg font-bold text-white tracking-tight">
                    "What Changed?" Market Delta Intelligence
                  </h2>
                </div>
                <p className="text-xs text-slate-400">
                  Deterministic audit of what shifted between your selected scans.
                </p>
              </div>

              {/* Comparison Selector */}
              {analysisHistory.length > 1 && (
                <div className="flex items-center gap-2 text-xs font-mono">
                  <span className="text-slate-400">Compare with:</span>
                  <select
                    value={selectedBaselineId || ''}
                    onChange={(e) => handleCompare(selectedAnalysisId || analysisHistory[0].id, e.target.value)}
                    className="px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    {analysisHistory
                      .filter((a) => a.id !== selectedAnalysisId)
                      .map((a) => (
                        <option key={a.id} value={a.id}>
                          Scan from {new Date(a.created_at).toLocaleDateString()} ({a.readiness_score}%)
                        </option>
                      ))}
                  </select>
                </div>
              )}
            </div>

            {/* Fact-based summary banner */}
            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-200 text-xs sm:text-sm leading-relaxed">
              <span className="font-bold text-white">Summary: </span>
              {whatChanged.summary}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Eliminated Gaps */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-3">
                <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1.5 uppercase">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Gaps Eliminated ({whatChanged.removed_gaps.length})
                </span>
                {whatChanged.removed_gaps.length === 0 ? (
                  <p className="text-xs text-slate-500">No gap removals in this period.</p>
                ) : (
                  <div className="space-y-1.5">
                    {whatChanged.removed_gaps.map((item) => (
                      <div key={item.skill_name} className="flex items-center justify-between text-xs font-mono p-2 rounded bg-slate-900 border border-slate-800">
                        <span className="text-white font-semibold">{item.skill_name}</span>
                        <span className="text-[10px] text-emerald-400 font-bold">Gap Closed</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Verified Proficiency Upgrades */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-3">
                <span className="text-xs font-mono font-bold text-blue-400 flex items-center gap-1.5 uppercase">
                  <TrendingUp className="w-3.5 h-3.5" /> Skill Upgrades ({whatChanged.improved_proficiencies.length})
                </span>
                {whatChanged.improved_proficiencies.length === 0 ? (
                  <p className="text-xs text-slate-500">No proficiency upgrades in this scan.</p>
                ) : (
                  <div className="space-y-1.5">
                    {whatChanged.improved_proficiencies.map((item) => (
                      <div key={item.skill_name} className="flex items-center justify-between text-xs font-mono p-2 rounded bg-slate-900 border border-slate-800">
                        <span className="text-white font-semibold">{item.skill_name}</span>
                        <span className="text-[10px] text-blue-400 capitalize">
                          {item.from_proficiency} → {item.to_proficiency}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Market Requirement Shifts */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-3">
                <span className="text-xs font-mono font-bold text-indigo-400 flex items-center gap-1.5 uppercase">
                  <Activity className="w-3.5 h-3.5" /> Market Shifts ({whatChanged.market_priority_shifts.length})
                </span>
                {whatChanged.market_priority_shifts.length === 0 ? (
                  <p className="text-xs text-slate-500">Market requirements remained steady.</p>
                ) : (
                  <div className="space-y-1.5">
                    {whatChanged.market_priority_shifts.map((shift) => (
                      <div key={shift.skill_name} className="flex items-center justify-between text-xs font-mono p-2 rounded bg-slate-900 border border-slate-800">
                        <span className="text-white font-semibold">{shift.skill_name}</span>
                        <span className={`text-[10px] font-bold ${shift.delta_pct > 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                          {shift.delta_pct > 0 ? `+${shift.delta_pct}%` : `${shift.delta_pct}%`} demand
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Skill Evolution Timeline Section */}
        <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-cyan-400" />
                <h2 className="text-lg font-bold text-white tracking-tight">
                  Skill Evolution Timeline
                </h2>
              </div>
              <p className="text-xs text-slate-400">
                Verified history of proficiency adjustments made to your developer profile.
              </p>
            </div>
            <Link
              href="/profile"
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              Update Skills <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {skillProgress.length === 0 ? (
            <p className="text-xs text-slate-500 py-6 text-center">
              No skill changes recorded yet. Update your skills in your profile to log milestones.
            </p>
          ) : (
            <div className="relative border-l border-slate-800 ml-4 space-y-5 py-2">
              {skillProgress.map((item, idx) => (
                <div key={item.id || idx} className="relative pl-6 group">
                  {/* Node */}
                  <div className="absolute -left-2 top-1.5 w-4 h-4 rounded-full bg-slate-900 border-2 border-cyan-500 group-hover:border-white transition"></div>
                  
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <span className="font-bold text-sm text-white">{item.skill_name}</span>
                      <span className="text-[11px] text-slate-500 font-mono block sm:inline-block sm:ml-3">
                        {item.category || 'General'}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-xs font-mono">
                      <span className="px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800 capitalize">
                        {item.from_proficiency || 'missing'}
                      </span>
                      <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold capitalize">
                        {item.to_proficiency}
                      </span>
                      <span className="text-[10px] text-slate-500 ml-2">
                        {new Date(item.recorded_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Historical Scans List */}
        <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
          <div className="pb-4 border-b border-slate-800">
            <h2 className="text-lg font-bold text-white tracking-tight">
              Historical Market Analyses ({analysisHistory.length})
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select any past market scan to review full candidate intelligence breakdowns and job matches.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysisHistory.map((scan) => (
              <Link
                key={scan.id}
                href={`/analysis/${scan.id}`}
                className="p-5 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition duration-200 flex flex-col justify-between group shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                      {scan.jobs_analyzed} Live Jobs
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                      {new Date(scan.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition">
                    {scan.target_role}
                  </h3>
                  <span className="text-xs text-slate-400 block mt-0.5">
                    {scan.location || 'India / Remote'}
                  </span>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between mt-4">
                  <div>
                    <span className="text-[10px] uppercase font-mono text-slate-500 block">Readiness</span>
                    <span className="text-xl font-extrabold font-mono text-blue-400">
                      {scan.readiness_score}%
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-cyan-400 flex items-center gap-1">
                    Feedback Report <ChevronRight className="w-3.5 h-3.5" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
