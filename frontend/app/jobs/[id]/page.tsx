'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { JobDetailedAnalysisResponse } from '@/types';
import {
  Radar,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ExternalLink,
  Briefcase,
  MapPin,
  Calendar,
  Sparkles,
  Lightbulb,
  Clock,
  ChevronRight,
  TrendingUp,
  ShieldCheck,
  Layers,
  Loader2,
  Heart
} from 'lucide-react';

export default function JobDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const jobId = params?.id as string;
  const analysisId = searchParams.get('analysis_id') || undefined;

  const [data, setData] = useState<JobDetailedAnalysisResponse | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;
    setIsLoading(true);
    Promise.all([
      api.getJobAnalysis(jobId, analysisId),
      api.getWatchlist().catch(() => []),
    ])
      .then(([jobData, watchData]) => {
        setData(jobData);
        setIsSaved(watchData.some((w) => w.job_id === jobId));
      })
      .catch((err) => setError(err.message || 'Failed to load job analysis.'))
      .finally(() => setIsLoading(false));
  }, [jobId, analysisId]);

  const handleToggleWatchlist = async () => {
    if (!jobId) return;
    setIsSaving(true);
    try {
      if (isSaved) {
        await api.removeFromWatchlist(jobId);
        setIsSaved(false);
      } else {
        await api.addToWatchlist(jobId);
        setIsSaved(true);
      }
    } catch (e) {
      console.error('Failed to toggle watchlist', e);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center p-8 text-center">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin mb-4" />
        <h2 className="text-xl font-bold text-white">Calculating Job-Specific Match...</h2>
        <p className="text-sm text-slate-400 mt-1">Comparing candidate skills against exact job requirements.</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto my-16 p-8 rounded-3xl glass-panel border border-red-500/30 text-center">
        <XCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-white">Job Analysis Error</h2>
        <p className="text-sm text-slate-400 mt-2">{error || 'Could not load job details.'}</p>
        <button
          onClick={() => window.history.back()}
          className="inline-flex items-center gap-2 mt-6 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-sm font-semibold transition"
        >
          <ArrowLeft className="w-4 h-4" /> Go Back
        </button>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
    if (score >= 50) return 'text-blue-400 border-blue-500/40 bg-blue-500/10';
    return 'text-amber-400 border-amber-500/40 bg-amber-500/10';
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Back Link */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => window.history.back()}
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Search Results
        </button>
        {analysisId && (
          <Link
            href={`/analysis/${analysisId}`}
            className="text-xs font-mono text-cyan-400 hover:underline"
          >
            ← Full Market Report
          </Link>
        )}
      </div>

      {/* Header Banner */}
      <div className="p-6 sm:p-8 rounded-3xl glass-panel border border-slate-800 relative overflow-hidden shadow-2xl mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] font-mono uppercase tracking-widest px-2.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Job-Level Match Analysis
              </span>
              {data.remote_type && (
                <span className="text-[10px] font-mono uppercase tracking-widest px-2.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                  {data.remote_type}
                </span>
              )}
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              {data.title}
            </h1>
            <div className="flex flex-wrap items-center gap-4 mt-3 text-xs sm:text-sm text-slate-400">
              <span className="font-semibold text-slate-200">{data.company_name}</span>
              <span>•</span>
              <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-blue-400" /> {data.location || 'India'}</span>
              {data.posted_at && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5 text-slate-500" /> {new Date(data.posted_at).toLocaleDateString()}</span>
                </>
              )}
            </div>
          </div>

          {/* Match Score & Actions */}
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <div className={`p-4 rounded-2xl border flex items-center gap-4 ${getScoreColor(data.match_score)}`}>
              <div className="text-center font-mono">
                <span className="text-3xl sm:text-4xl font-extrabold block leading-none">{data.match_score}%</span>
                <span className="text-[10px] uppercase tracking-wider font-sans opacity-80">Job Match</span>
              </div>
              <div className="text-xs border-l border-white/10 pl-3 space-y-1">
                <div>Required: <strong>{data.required_match_score}%</strong></div>
                <div>Preferred: <strong>{data.preferred_match_score}%</strong></div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleToggleWatchlist}
                disabled={isSaving}
                className={`p-3.5 rounded-xl border flex items-center gap-2 text-xs font-semibold transition ${
                  isSaved
                    ? 'bg-rose-500/20 border-rose-500 text-rose-300'
                    : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-200'
                }`}
                title={isSaved ? 'Saved to Watchlist' : 'Save to Watchlist'}
              >
                <Heart className={`w-4 h-4 ${isSaved ? 'fill-rose-400 text-rose-400' : ''}`} />
                <span>{isSaved ? 'Saved' : 'Save Job'}</span>
              </button>

              {data.apply_url && (
                <a
                  href={data.apply_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-blue-500/25 transition"
                >
                  Apply on Company Site <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">Required Match</span>
          <span className="text-xl font-bold font-mono text-emerald-400">{data.matched_required_skills} / {data.total_required_skills}</span>
          <span className="text-[10px] text-slate-400 block mt-0.5">{data.missing_required_skills} Missing required</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">Preferred Match</span>
          <span className="text-xl font-bold font-mono text-blue-400">{data.matched_preferred_skills} / {data.total_preferred_skills}</span>
          <span className="text-[10px] text-slate-400 block mt-0.5">{data.missing_preferred_skills} Missing preferred</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">Weak Areas</span>
          <span className="text-xl font-bold font-mono text-amber-400">{data.weak_gaps.length} Skills</span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Need depth upgrade</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">Total Verified Skills</span>
          <span className="text-xl font-bold font-mono text-cyan-400">{data.total_skills_count} Skills</span>
          <span className="text-[10px] text-slate-400 block mt-0.5">Extracted from job</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Requirements & Gap Analysis (2 cols) */}
        <div className="lg:col-span-2 space-y-8">
          {/* Section 1: Required vs Preferred Skills Matrix */}
          <div className="p-6 rounded-3xl glass-panel border border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
              <Layers className="w-4 h-4 text-blue-400" /> Job Requirements Breakdown
            </h2>

            <div className="space-y-4">
              {/* Required Skills */}
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-2">
                  Mandatory / Required Skills ({data.total_required_skills})
                </span>
                <div className="flex flex-wrap gap-2">
                  {data.gaps.filter((g) => g.job_importance === 'required').map((g) => (
                    <div
                      key={g.skill_id}
                      className={`px-3 py-1.5 rounded-xl border text-xs font-medium flex items-center gap-1.5 ${
                        g.gap_type === 'matched'
                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                          : g.gap_type === 'weak'
                          ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                          : 'bg-red-500/10 border-red-500/30 text-red-300'
                      }`}
                    >
                      {g.gap_type === 'matched' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                      {g.gap_type === 'weak' && <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
                      {g.gap_type === 'missing' && <XCircle className="w-3.5 h-3.5 text-red-400" />}
                      <span>{g.name}</span>
                      <span className="text-[10px] opacity-70 font-mono">
                        ({g.candidate_proficiency || 'Missing'})
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Preferred Skills */}
              {data.total_preferred_skills > 0 && (
                <div className="pt-3 border-t border-slate-800/80">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-2">
                    Preferred / Nice-to-Have Skills ({data.total_preferred_skills})
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {data.gaps.filter((g) => g.job_importance !== 'required').map((g) => (
                      <div
                        key={g.skill_id}
                        className={`px-3 py-1.5 rounded-xl border text-xs font-medium flex items-center gap-1.5 ${
                          g.gap_type === 'matched'
                            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                            : g.gap_type === 'weak'
                            ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                            : 'bg-slate-900 border-slate-800 text-slate-400'
                        }`}
                      >
                        {g.gap_type === 'matched' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                        {g.gap_type === 'weak' && <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
                        {g.gap_type === 'missing' && <span className="text-slate-500 font-mono">•</span>}
                        <span>{g.name}</span>
                        <span className="text-[10px] opacity-70 font-mono">
                          ({g.candidate_proficiency || 'Missing'})
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Section 2: Detailed Evidence for Gaps */}
          <div className="p-6 rounded-3xl glass-panel border border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
              <ShieldCheck className="w-4 h-4 text-cyan-400" /> Evidence Behind Your Gaps
            </h2>

            <div className="space-y-3">
              {data.gaps.filter((g) => g.gap_type !== 'matched').map((gap) => (
                <div
                  key={gap.skill_id}
                  className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-white">{gap.name}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-mono uppercase font-semibold ${
                          gap.gap_type === 'missing'
                            ? gap.job_importance === 'required' ? 'bg-red-500/20 text-red-400' : 'bg-slate-800 text-slate-400'
                            : 'bg-amber-500/20 text-amber-400'
                        }`}
                      >
                        {gap.job_importance} {gap.gap_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">{gap.evidence}</p>
                  </div>
                  <div className="text-right font-mono text-xs flex-shrink-0">
                    <span className="text-slate-400 block">Gap Priority</span>
                    <span className="text-cyan-400 font-bold">{gap.priority_score}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 3: Job Description Excerpt */}
          {data.description && (
            <div className="p-6 rounded-3xl glass-panel border border-slate-800">
              <h2 className="text-base font-bold text-white mb-3">Job Description</h2>
              <div className="text-xs sm:text-sm text-slate-300 whitespace-pre-line leading-relaxed max-h-60 overflow-y-auto pr-2">
                {data.description}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Personalized Action Suggestions (1 col) */}
        <div className="space-y-6">
          <div className="p-6 rounded-3xl glass-panel border border-amber-500/30 bg-amber-950/5">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-400 mb-2">
              <Lightbulb className="w-4 h-4" /> What To Do Next
            </div>
            <h3 className="text-base font-bold text-white mb-2">Personalized Next Steps</h3>
            <p className="text-xs text-slate-400 mb-5 leading-relaxed">
              Targeted practical projects building upon your existing skillset to qualify for this job.
            </p>

            <div className="space-y-4">
              {data.recommendations.map((rec, idx) => (
                <div key={rec.id || idx} className="p-4 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-300">{rec.skill_name || 'Skill Action'}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      Priority {rec.priority}
                    </span>
                  </div>

                  <p className="text-xs text-slate-200 font-medium leading-relaxed">
                    {rec.recommended_next_step}
                  </p>

                  <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400">
                    <strong className="text-amber-400 block mb-0.5">Practical Project:</strong>
                    {rec.practical_action}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
