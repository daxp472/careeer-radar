'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { CandidateSkillInput, RoleItem, SkillItem } from '@/types';
import {
  Radar,
  Plus,
  Trash2,
  Sparkles,
  Search,
  MapPin,
  Briefcase,
  Layers,
  ArrowRight,
  AlertCircle,
  Loader2,
  Check
} from 'lucide-react';

const PROFICIENCY_LEVELS = [
  { key: 'beginner', label: 'Beginner', weight: '25%' },
  { key: 'known', label: 'Known', weight: '50%' },
  { key: 'intermediate', label: 'Intermediate', weight: '70%' },
  { key: 'advanced', label: 'Advanced', weight: '90%' },
  { key: 'expert', label: 'Expert', weight: '100%' },
] as const;

const POPULAR_ROLES = [
  'Full Stack Developer',
  'Frontend Developer',
  'Backend Developer',
  'Software Engineer',
  'Python Developer',
  'React Developer',
  'DevOps Engineer'
];

const SUGGESTED_SKILLS = [
  'React', 'Next.js', 'TypeScript', 'JavaScript', 'Node.js', 'Python',
  'FastAPI', 'PostgreSQL', 'MongoDB', 'Docker', 'AWS', 'Tailwind CSS', 'Git'
];

export default function AnalyzePage() {
  const router = useRouter();

  const [mounted, setMounted] = useState(false);
  const [targetRole, setTargetRole] = useState('Full Stack Developer');
  const [location, setLocation] = useState('Ahmedabad, India');
  const [remotePreference, setRemotePreference] = useState('flexible');
  const [experienceYears, setExperienceYears] = useState(1);

  const [skills, setSkills] = useState<CandidateSkillInput[]>([
    { name: 'React', proficiency: 'advanced', years_experience: 2 },
    { name: 'JavaScript', proficiency: 'intermediate', years_experience: 2 },
    { name: 'Node.js', proficiency: 'known', years_experience: 1 },
    { name: 'MongoDB', proficiency: 'known', years_experience: 1 },
  ]);

  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState<'beginner' | 'known' | 'intermediate' | 'advanced' | 'expert'>('known');

  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const loadingSteps = [
    'Calling SerpApi Google Jobs live search...',
    'Normalizing and deduplicating job requirements...',
    'Extracting canonical skills across job descriptions...',
    'Aggregating market frequency statistics...',
    'Executing deterministic readiness & gap formula...',
    'Formulating evidence-backed AI action plan...'
  ];

  const handleAddSkill = (nameToAdd?: string) => {
    const name = (nameToAdd || newSkillName).trim();
    if (!name) return;

    if (skills.some((s) => s.name.toLowerCase() === name.toLowerCase())) {
      setError(`"${name}" is already in your skills list.`);
      return;
    }

    setSkills([...skills, { name, proficiency: newSkillProficiency, years_experience: 1 }]);
    setNewSkillName('');
    setError(null);
  };

  const handleRemoveSkill = (name: string) => {
    setSkills(skills.filter((s) => s.name !== name));
  };

  const handleProficiencyChange = (name: string, proficiency: CandidateSkillInput['proficiency']) => {
    setSkills(skills.map((s) => (s.name === name ? { ...s, proficiency } : s)));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetRole.trim()) {
      setError('Please enter a target role.');
      return;
    }
    if (skills.length === 0) {
      setError('Please add at least 1 skill to compare against the live market.');
      return;
    }

    setError(null);
    setIsLoading(true);
    setLoadingStep(0);

    // Progress step animation ticker
    const interval = setInterval(() => {
      setLoadingStep((prev) => (prev < loadingSteps.length - 1 ? prev + 1 : prev));
    }, 1800);

    try {
      const response = await api.createAnalysis({
        target_role: targetRole,
        location,
        remote_preference: remotePreference,
        skills,
        experience_years: experienceYears,
      });

      clearInterval(interval);
      router.push(`/analysis/${response.id}`);
    } catch (err: any) {
      clearInterval(interval);
      setIsLoading(false);
      setError(err.message || 'Failed to analyze market. Please verify the backend is active.');
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-3">
          <Radar className="w-3.5 h-3.5" />
          <span>Real-Time Market Check</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Analyze Your Live Market Readiness
        </h1>
        <p className="mt-2 text-sm sm:text-base text-slate-400">
          Enter your target role and current skills to see live employer requirements and identify your top skill gaps.
        </p>
      </div>

      {/* Loading Modal / State */}
      {isLoading ? (
        <div className="p-10 rounded-2xl glass-panel border border-blue-500/30 text-center max-w-xl mx-auto shadow-2xl animate-fade-in">
          <div className="relative w-24 h-24 mx-auto mb-6 flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border-2 border-blue-500/20 animate-ping" />
            <div className="w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/40 flex items-center justify-center">
              <Radar className="w-10 h-10 text-cyan-400 animate-spin" />
            </div>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Analyzing Live Job Market</h3>
          <p className="text-sm font-mono text-cyan-300 min-h-[40px]">
            {loadingSteps[loadingStep]}
          </p>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-6 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-cyan-400 h-full transition-all duration-500"
              style={{ width: `${((loadingStep + 1) / loadingSteps.length) * 100}%` }}
            />
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-8" suppressHydrationWarning>
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-400 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Section 1: Target Position */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800">
            <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
              <Briefcase className="w-4 h-4 text-blue-400" /> Target Role & Location
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Target Role
                </label>
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="e.g. Full Stack Developer, Frontend Developer"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
                  required
                />
                <div className="flex flex-wrap gap-1.5 mt-2.5">
                  {POPULAR_ROLES.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setTargetRole(r)}
                      className={`text-[11px] px-2.5 py-1 rounded-md transition ${
                        targetRole === r
                          ? 'bg-blue-600 text-white font-medium'
                          : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Target Location
                </label>
                <div className="relative">
                  <MapPin className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Ahmedabad, Bengaluru, Remote, India"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3 mt-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                      Remote Preference
                    </label>
                    <select
                      value={remotePreference}
                      onChange={(e) => setRemotePreference(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-white text-xs focus:outline-none focus:border-blue-500"
                    >
                      <option value="flexible">Flexible</option>
                      <option value="remote">Remote Only</option>
                      <option value="hybrid">Hybrid</option>
                      <option value="onsite">On-Site</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                      Years of Experience
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="15"
                      value={experienceYears}
                      onChange={(e) => setExperienceYears(parseInt(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-white text-xs focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Current Skills */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" /> Your Current Skills ({skills.length})
              </h2>
              <span className="text-xs text-slate-400">Select accurate proficiency levels for calibrated signals</span>
            </div>

            {/* Add Skill Input */}
            <div className="flex flex-col sm:flex-row gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800 mb-5">
              <input
                type="text"
                value={newSkillName}
                onChange={(e) => setNewSkillName(e.target.value)}
                placeholder="Type a skill (e.g., TypeScript, Docker, AWS)"
                className="flex-1 px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddSkill();
                  }
                }}
              />
              <div className="flex items-center gap-2">
                <select
                  value={newSkillProficiency}
                  onChange={(e) => setNewSkillProficiency(e.target.value as any)}
                  className="px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  {PROFICIENCY_LEVELS.map((p) => (
                    <option key={p.key} value={p.key}>
                      {p.label} ({p.weight})
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => handleAddSkill()}
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Skill
                </button>
              </div>
            </div>

            {/* Suggested Quick Add Chips */}
            <div className="mb-6">
              <span className="text-[11px] font-mono uppercase text-slate-400 block mb-2">Quick Add Suggestions:</span>
              <div className="flex flex-wrap gap-1.5">
                {SUGGESTED_SKILLS.filter((sk) => !skills.some((s) => s.name.toLowerCase() === sk.toLowerCase())).map((sk) => (
                  <button
                    key={sk}
                    type="button"
                    onClick={() => handleAddSkill(sk)}
                    className="text-xs px-2.5 py-1 rounded-md bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white flex items-center gap-1 transition"
                  >
                    <Plus className="w-3 h-3 text-cyan-400" /> {sk}
                  </button>
                ))}
              </div>
            </div>

            {/* Current Skills List */}
            <div className="space-y-2.5">
              {skills.map((skill) => (
                <div
                  key={skill.name}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-xl bg-slate-900 border border-slate-800/80 hover:border-slate-700 transition"
                >
                  <span className="font-semibold text-sm text-slate-100">{skill.name}</span>

                  <div className="flex items-center gap-2">
                    {/* Proficiency Pill Selector */}
                    <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800">
                      {PROFICIENCY_LEVELS.map((level) => {
                        const isSelected = skill.proficiency === level.key;
                        return (
                          <button
                            key={level.key}
                            type="button"
                            onClick={() => handleProficiencyChange(skill.name, level.key)}
                            className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                              isSelected
                                ? 'bg-blue-600 text-white shadow-sm'
                                : 'text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            {level.label}
                          </button>
                        );
                      })}
                    </div>

                    {/* Delete Button */}
                    <button
                      type="button"
                      onClick={() => handleRemoveSkill(skill.name)}
                      className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-800 transition"
                      title="Remove skill"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-2">
            <button
              type="submit"
              className="w-full py-4 rounded-xl text-base font-bold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 shadow-xl shadow-blue-500/25 flex items-center justify-center gap-2.5 transition"
            >
              <Radar className="w-5 h-5 text-cyan-300 animate-pulse" />
              Analyze Live Job Market & Calculate Readiness
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
