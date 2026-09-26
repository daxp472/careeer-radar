'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { ProfileResponse, CandidateSkillInput, AlertSettings } from '@/types';
import {
  User,
  Briefcase,
  MapPin,
  Layers,
  Plus,
  Trash2,
  Save,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Bell,
  Sparkles,
  Clock,
  Mail,
  Sliders,
  Globe
} from 'lucide-react';

const PROFICIENCY_LEVELS = [
  { key: 'beginner', label: 'Beginner' },
  { key: 'known', label: 'Known' },
  { key: 'intermediate', label: 'Intermediate' },
  { key: 'advanced', label: 'Advanced' },
  { key: 'expert', label: 'Expert' },
] as const;

const DAYS_OF_WEEK = [
  { key: 'monday', label: 'Monday' },
  { key: 'tuesday', label: 'Tuesday' },
  { key: 'wednesday', label: 'Wednesday' },
  { key: 'thursday', label: 'Thursday' },
  { key: 'friday', label: 'Friday' },
  { key: 'saturday', label: 'Saturday' },
  { key: 'sunday', label: 'Sunday' },
];

const TIMEZONES = [
  { key: 'Asia/Kolkata', label: 'India Standard Time (Asia/Kolkata)' },
  { key: 'UTC', label: 'Coordinated Universal Time (UTC)' },
  { key: 'America/New_York', label: 'US Eastern Time (America/New_York)' },
  { key: 'America/Los_Angeles', label: 'US Pacific Time (America/Los_Angeles)' },
  { key: 'Europe/London', label: 'London GMT/BST (Europe/London)' },
  { key: 'Asia/Dubai', label: 'Gulf Standard Time (Asia/Dubai)' },
  { key: 'Asia/Singapore', label: 'Singapore Time (Asia/Singapore)' },
];

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [targetRole, setTargetRole] = useState('');
  const [targetLocation, setTargetLocation] = useState('');
  const [remotePreference, setRemotePreference] = useState('flexible');
  const [experienceYears, setExperienceYears] = useState(0);
  const [skills, setSkills] = useState<CandidateSkillInput[]>([]);

  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState<'beginner' | 'known' | 'intermediate' | 'advanced' | 'expert'>('known');

  // Automation Settings
  const [alertSettings, setAlertSettings] = useState<AlertSettings | null>(null);
  const [radarEnabled, setRadarEnabled] = useState(true);
  const [radarDay, setRadarDay] = useState('monday');
  const [radarTime, setRadarTime] = useState('10:00');
  const [radarTimezone, setRadarTimezone] = useState('Asia/Kolkata');
  const [radarMinMatch, setRadarMinMatch] = useState(80);
  const [radarEmailEnabled, setRadarEmailEnabled] = useState(true);
  const [radarInAppEnabled, setRadarInAppEnabled] = useState(true);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setIsLoading(false);
      return;
    }
    Promise.all([
      api.getProfile(),
      api.getAlertSettings().catch(() => null),
    ])
      .then(([prof, settings]) => {
        setProfile(prof);
        setTargetRole(prof.target_role || '');
        setTargetLocation(prof.target_location || '');
        setRemotePreference(prof.remote_preference || 'flexible');
        setExperienceYears(prof.experience_years || 0);
        setSkills(prof.skills.map((s) => ({ name: s.name, proficiency: s.proficiency as any, years_experience: s.years_experience })));

        if (settings) {
          setAlertSettings(settings);
          setRadarEnabled(settings.enabled);
          setRadarDay(settings.day_of_week.toLowerCase());
          setRadarTime(settings.time_of_day);
          setRadarTimezone(settings.timezone);
          setRadarMinMatch(settings.minimum_match_score);
          setRadarEmailEnabled(settings.email_enabled);
          setRadarInAppEnabled(settings.in_app_enabled);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [user]);

  const handleAddSkill = () => {
    const name = newSkillName.trim();
    if (!name) return;
    if (skills.some((s) => s.name.toLowerCase() === name.toLowerCase())) {
      setError(`Skill "${name}" is already in your profile.`);
      return;
    }
    setSkills([...skills, { name, proficiency: newSkillProficiency, years_experience: 1 }]);
    setNewSkillName('');
    setError(null);
  };

  const handleRemoveSkill = (name: string) => {
    setSkills(skills.filter((s) => s.name !== name));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setIsSaving(true);

    try {
      const [updatedProfile, updatedSettings] = await Promise.all([
        api.updateProfile({
          target_role_name: targetRole,
          target_location: targetLocation,
          remote_preference: remotePreference,
          experience_years: experienceYears,
          skills,
        }),
        api.updateAlertSettings({
          enabled: radarEnabled,
          day_of_week: radarDay,
          time_of_day: radarTime,
          timezone: radarTimezone,
          minimum_match_score: radarMinMatch,
          email_enabled: radarEmailEnabled,
          in_app_enabled: radarInAppEnabled,
        })
      ]);

      setProfile(updatedProfile);
      setAlertSettings(updatedSettings);
      setMessage('Candidate profile & Weekly Job Radar settings saved successfully.');
    } catch (err: any) {
      setError(err.message || 'Failed to save settings.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-xl mx-auto my-16 p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center">
        <User className="w-10 h-10 text-blue-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-white">Developer Profile & Settings</h2>
        <p className="text-xs text-slate-400 mt-1">Please sign in to manage your default career profile, verified skills, and automated scan schedules.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="py-20 text-center">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-2" />
        <p className="text-xs text-slate-400">Loading candidate profile & radar settings...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Candidate Profile & Automation</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Configure your career preferences, evolve your skills over time, and customize your Weekly Job Radar schedule.
        </p>
      </div>

      {message && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2 mb-6">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2 mb-6">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6" suppressHydrationWarning>
        {/* Career Preferences */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-blue-400" /> Career Preferences
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Target Role
              </label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Full Stack Developer"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Target Location
              </label>
              <input
                type="text"
                value={targetLocation}
                onChange={(e) => setTargetLocation(e.target.value)}
                placeholder="e.g. India, Ahmedabad, Remote"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>
        </div>

        {/* Skills Evolution & Management */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" /> Candidate Skills ({skills.length})
            </h2>
            <span className="text-[11px] text-slate-400 font-mono">
              Changes are logged in Skill Progress History
            </span>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 p-3 rounded-xl bg-slate-950 border border-slate-800">
            <input
              type="text"
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              placeholder="Add skill (e.g. TypeScript, AWS, Docker)"
              className="flex-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
            <div className="flex items-center gap-2">
              <select
                value={newSkillProficiency}
                onChange={(e) => setNewSkillProficiency(e.target.value as any)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none"
              >
                {PROFICIENCY_LEVELS.map((p) => (
                  <option key={p.key} value={p.key}>{p.label}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={handleAddSkill}
                className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1 transition"
              >
                <Plus className="w-3.5 h-3.5" /> Add
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto pr-1 custom-scrollbar">
            {skills.map((s) => (
              <div
                key={s.name}
                className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800/80"
              >
                <span className="text-xs font-semibold text-white">{s.name}</span>
                <div className="flex items-center gap-2">
                  <select
                    value={s.proficiency}
                    onChange={(e) => {
                      const updated = skills.map(item =>
                        item.name === s.name ? { ...item, proficiency: e.target.value as any } : item
                      );
                      setSkills(updated);
                    }}
                    className="px-2 py-1 rounded bg-slate-900 border border-slate-800 text-[11px] text-cyan-400 capitalize focus:outline-none"
                  >
                    {PROFICIENCY_LEVELS.map((p) => (
                      <option key={p.key} value={p.key}>{p.label}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(s.name)}
                    className="text-slate-500 hover:text-red-400 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Phase 3: Candidate Weekly Job Radar Settings */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Bell className="w-4 h-4 text-indigo-400" /> Weekly Job Radar Automation
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                CareerRadar automatically scans new opportunities in the central database on your personalized schedule.
              </p>
            </div>
            {/* Enable/Disable Toggle */}
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={radarEnabled}
                onChange={(e) => setRadarEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 ${radarEnabled ? '' : 'opacity-40 pointer-events-none'}`}>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" /> Preferred Scan Day
              </label>
              <select
                value={radarDay}
                onChange={(e) => setRadarDay(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {DAYS_OF_WEEK.map((d) => (
                  <option key={d.key} value={d.key}>{d.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" /> Preferred Scan Time
              </label>
              <input
                type="time"
                value={radarTime}
                onChange={(e) => setRadarTime(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-slate-500" /> Timezone
              </label>
              <select
                value={radarTimezone}
                onChange={(e) => setRadarTimezone(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz.key} value={tz.key}>{tz.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
                <span className="flex items-center gap-1.5"><Sliders className="w-3.5 h-3.5 text-slate-500" /> Minimum Match Threshold</span>
                <span className="text-blue-400 font-bold font-mono">{radarMinMatch}%</span>
              </label>
              <input
                type="range"
                min="50"
                max="95"
                step="5"
                value={radarMinMatch}
                onChange={(e) => setRadarMinMatch(Number(e.target.value))}
                className="w-full accent-blue-500 mt-2"
              />
            </div>

            <div className="md:col-span-2 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                  <input
                    type="checkbox"
                    checked={radarEmailEnabled}
                    onChange={(e) => setRadarEmailEnabled(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-800 text-blue-600 focus:ring-0"
                  />
                  <Mail className="w-3.5 h-3.5 text-slate-400" /> Send Weekly Email Digest
                </label>
                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                  <input
                    type="checkbox"
                    checked={radarInAppEnabled}
                    onChange={(e) => setRadarInAppEnabled(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-800 text-blue-600 focus:ring-0"
                  />
                  <Bell className="w-3.5 h-3.5 text-slate-400" /> In-App Notification Alerts
                </label>
              </div>

              {alertSettings?.next_scan_at && (
                <span className="text-[11px] text-slate-400 font-mono">
                  Next execution: <span className="text-white">{new Date(alertSettings.next_scan_at).toLocaleString()}</span>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Save Button */}
        <button
          type="submit"
          disabled={isSaving}
          className="w-full py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2 transition disabled:opacity-50"
        >
          {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Save Profile & Automation Settings
        </button>
      </form>
    </div>
  );
}
