'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { DatabaseJobItem, DatabaseJobSearchResponse } from '@/types';
import {
  Search,
  Filter,
  Briefcase,
  MapPin,
  Building,
  Sparkles,
  Heart,
  ExternalLink,
  ChevronRight,
  Clock,
  RefreshCw,
  SlidersHorizontal,
  Layers,
  ArrowUpDown,
  CheckCircle2,
  AlertCircle,
  Database,
  Radio
} from 'lucide-react';

export default function JobDatabasePage() {
  const { user } = useAuth();

  const [searchRole, setSearchRole] = useState('');
  const [searchLocation, setSearchLocation] = useState('');
  const [remoteType, setRemoteType] = useState('all');
  const [skillFilter, setSkillFilter] = useState('');
  const [minMatch, setMinMatch] = useState<number | undefined>(undefined);
  const [sortBy, setSortBy] = useState('match_score');
  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DatabaseJobSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savedJobIds, setSavedJobIds] = useState<Set<string>>(new Set());
  const [savingJobId, setSavingJobId] = useState<string | null>(null);

  const [refreshingAdmin, setRefreshingAdmin] = useState(false);
  const [refreshMsg, setRefreshMsg] = useState<string | null>(null);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.searchDatabaseJobs({
        role: searchRole || undefined,
        location: searchLocation || undefined,
        remote_type: remoteType !== 'all' ? remoteType : undefined,
        skills: skillFilter || undefined,
        minimum_match: minMatch,
        sort: sortBy,
        page,
        limit: 15,
      });
      setData(res);

      // Track saved status
      const saved = new Set(res.jobs.filter(j => j.is_saved).map(j => j.id));
      setSavedJobIds(saved);
    } catch (err: any) {
      console.error('Failed to load database jobs', err);
      setError(err?.message || 'Failed to load database jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [page, sortBy]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const toggleWatchlist = async (job: DatabaseJobItem) => {
    setSavingJobId(job.id);
    const isCurrentlySaved = savedJobIds.has(job.id);
    try {
      if (isCurrentlySaved) {
        await api.removeFromWatchlist(job.id);
        setSavedJobIds(prev => {
          const next = new Set(prev);
          next.delete(job.id);
          return next;
        });
      } else {
        await api.addToWatchlist(job.id);
        setSavedJobIds(prev => new Set(prev).add(job.id));
      }
    } catch (err) {
      console.error('Failed to toggle watchlist', err);
    } finally {
      setSavingJobId(null);
    }
  };

  const handleAdminRefresh = async () => {
    setRefreshingAdmin(true);
    setRefreshMsg(null);
    try {
      const res = await api.triggerAdminRefresh();
      setRefreshMsg('Database refresh started in background. Results will be updated shortly.');
      setTimeout(() => {
        fetchJobs();
      }, 3000);
    } catch (err) {
      setRefreshMsg('Failed to trigger refresh.');
    } finally {
      setRefreshingAdmin(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Header & Mode Switcher */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5" /> CareerRadar Central Job Database
              </span>
              {data?.database_last_refreshed_at && (
                <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-500" />
                  Refreshed {new Date(data.database_last_refreshed_at).toLocaleString()}
                </span>
              )}
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Market Job Database
            </h1>
            <p className="mt-1 text-slate-400 text-sm max-w-2xl">
              Explore normalized and deduplicated jobs from our weekly market scans. Match scores and skill gaps are dynamically calculated against your candidate profile.
            </p>
          </div>

          {/* Mode Tabs */}
          <div className="flex items-center gap-2 p-1.5 bg-slate-900 border border-slate-800 rounded-xl self-start md:self-auto">
            <Link
              href="/analyze"
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <Radio className="w-3.5 h-3.5 text-rose-400 animate-pulse" /> Live Market Search
            </Link>
            <button
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-blue-600 text-white shadow-md shadow-blue-500/20"
            >
              <Database className="w-3.5 h-3.5" /> CareerRadar Jobs
            </button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-sm shadow-xl space-y-4">
          <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" suppressHydrationWarning>
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Target Role
              </label>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="e.g. Full Stack Developer"
                  value={searchRole}
                  onChange={(e) => setSearchRole(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Location
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="e.g. India, Ahmedabad, Remote"
                  value={searchLocation}
                  onChange={(e) => setSearchLocation(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Remote Type
              </label>
              <select
                value={remoteType}
                onChange={(e) => setRemoteType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Work Types</option>
                <option value="remote">Remote Only</option>
                <option value="hybrid">Hybrid</option>
                <option value="on-site">On-Site</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
                Required Skills
              </label>
              <input
                type="text"
                placeholder="e.g. React, TypeScript, Docker"
                value={skillFilter}
                onChange={(e) => setSkillFilter(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="sm:col-span-2 lg:col-span-4 flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800/60">
              <div className="flex flex-wrap items-center gap-4">
                {/* Min Match Slider */}
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 font-mono">
                    Min Match: <span className="text-blue-400 font-bold">{minMatch ? `${minMatch}%` : 'Any'}</span>
                  </span>
                  <input
                    type="range"
                    min="0"
                    max="90"
                    step="10"
                    value={minMatch || 0}
                    onChange={(e) => setMinMatch(Number(e.target.value) > 0 ? Number(e.target.value) : undefined)}
                    className="w-28 accent-blue-500"
                  />
                </div>

                {/* Sort Order */}
                <div className="flex items-center gap-2">
                  <ArrowUpDown className="w-3.5 h-3.5 text-slate-500" />
                  <span className="text-xs text-slate-400 font-mono">Sort:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    <option value="match_score">Highest Match Score</option>
                    <option value="recent">Most Recent Posted</option>
                    <option value="relevance">Relevance & Skills</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="flex items-center gap-2 px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl shadow-md shadow-blue-500/20 transition"
              >
                <Search className="w-3.5 h-3.5" /> Apply Filters
              </button>
            </div>
          </form>
        </div>

        {/* Admin Refresh Action notice (if applicable) */}
        {refreshMsg && (
          <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs flex items-center justify-between">
            <span>{refreshMsg}</span>
            <button onClick={() => setRefreshMsg(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-semibold">Error:</span>
              <span>{error}</span>
            </div>
            <button
              onClick={() => fetchJobs()}
              className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* Results Info & Count */}
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>
            Found <span className="text-white font-bold">{data?.total || 0}</span> database opportunities
            {data?.applied_filters?.role ? ` for "${data.applied_filters.role}"` : ''}
          </span>
          <button
            onClick={handleAdminRefresh}
            disabled={refreshingAdmin}
            className="flex items-center gap-1.5 text-slate-400 hover:text-blue-400 transition"
            title="Refresh database from market"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshingAdmin ? 'animate-spin text-blue-400' : ''}`} />
            Sync Database
          </button>
        </div>

        {/* Jobs List Grid */}
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-400 text-sm font-mono">Loading market database opportunities...</p>
          </div>
        ) : data?.jobs.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <Layers className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-lg font-bold text-white">No jobs matched your criteria</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              Try adjusting your role keywords, lowering the match threshold, or running an on-demand Live Market Search.
            </p>
            <div className="flex justify-center gap-3 pt-2">
              <button
                onClick={() => {
                  setSearchRole('');
                  setSearchLocation('');
                  setSkillFilter('');
                  setMinMatch(undefined);
                  fetchJobs();
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white rounded-xl transition"
              >
                Reset Filters
              </button>
              <Link
                href="/analyze"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white rounded-xl transition"
              >
                Run Live Search
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {data?.jobs.map((job) => {
              const isSaved = savedJobIds.has(job.id);
              const score = job.match_score ?? 0;
              const isHigh = score >= 80;
              const isMed = score >= 60 && score < 80;

              return (
                <div
                  key={job.id}
                  className="p-5 sm:p-6 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition duration-200 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-lg group"
                >
                  {/* Left Job Info */}
                  <div className="space-y-3 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-[11px] px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        {job.company_name}
                      </span>
                      {job.location && (
                        <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                          <MapPin className="w-3 h-3 text-slate-500" /> {job.location}
                        </span>
                      )}
                      {job.remote_type && job.remote_type !== 'unknown' && (
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          {job.remote_type}
                        </span>
                      )}
                      {job.status === 'stale' && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          Stale
                        </span>
                      )}
                    </div>

                    <h2 className="text-lg sm:text-xl font-bold text-white group-hover:text-blue-400 transition">
                      <Link href={`/jobs/${job.id}`}>
                        {job.title}
                      </Link>
                    </h2>

                    {/* Skill Tags */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      {(job.matched_skills || []).map((s) => (
                        <span
                          key={s}
                          className="px-2.5 py-0.5 rounded-md text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1"
                        >
                          <CheckCircle2 className="w-3 h-3" /> {s}
                        </span>
                      ))}
                      {(job.missing_skills || []).map((s) => (
                        <span
                          key={s}
                          className="px-2.5 py-0.5 rounded-md text-[11px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20"
                        >
                          Missing: {s}
                        </span>
                      ))}
                      {job.skills && job.skills.length > 5 && (
                        <span className="text-[10px] text-slate-500 font-mono self-center">
                          +{job.skills.length - 5} more skills
                        </span>
                      )}
                    </div>

                    {/* Freshness Timestamp */}
                    <div className="flex items-center gap-3 text-[11px] text-slate-500 font-mono pt-1">
                      <span>
                        Posted: {job.posted_at ? new Date(job.posted_at).toLocaleDateString() : 'Recent'}
                      </span>
                      <span>•</span>
                      <span>
                        Discovered: {job.first_seen_at ? new Date(job.first_seen_at).toLocaleDateString() : 'This week'}
                      </span>
                    </div>
                  </div>

                  {/* Right Score & Actions */}
                  <div className="flex items-center md:flex-col justify-between md:justify-center gap-4 pt-4 md:pt-0 border-t md:border-t-0 md:border-l border-slate-800 md:pl-6 min-w-[170px]">
                    {job.match_score !== null && job.match_score !== undefined ? (
                      <div className="text-left md:text-center">
                        <div
                          className={`text-2xl font-black font-mono tracking-tight ${
                            isHigh ? 'text-emerald-400' : isMed ? 'text-blue-400' : 'text-amber-400'
                          }`}
                        >
                          {score.toFixed(1)}%
                        </div>
                        <span className="text-[10px] uppercase font-mono tracking-widest text-slate-400">
                          Match Score
                        </span>
                      </div>
                    ) : (
                      <div className="text-left md:text-center">
                        <span className="text-xs text-slate-500 font-mono">Sign in to match</span>
                      </div>
                    )}

                    <div className="flex items-center gap-2">
                      {/* Save to Watchlist Button */}
                      <button
                        onClick={() => toggleWatchlist(job)}
                        disabled={savingJobId === job.id}
                        className={`p-2 rounded-xl border transition ${
                          isSaved
                            ? 'bg-rose-500/20 border-rose-500 text-rose-400'
                            : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300'
                        }`}
                        title={isSaved ? 'Remove from Watchlist' : 'Save to Watchlist'}
                      >
                        <Heart className={`w-4 h-4 ${isSaved ? 'fill-rose-400' : ''}`} />
                      </button>

                      {/* Detail Gap Analysis Link */}
                      <Link
                        href={`/jobs/${job.id}`}
                        className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition flex items-center gap-1 shadow-md shadow-blue-500/20"
                      >
                        Gap Breakdown <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-center gap-2 pt-6">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-800 transition"
            >
              Previous
            </button>
            <span className="text-xs font-mono text-slate-400 px-3">
              Page {page} of {data.total_pages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
              disabled={page === data.total_pages}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 disabled:opacity-40 hover:bg-slate-800 transition"
            >
              Next
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
