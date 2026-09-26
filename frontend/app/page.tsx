'use client';

import React from 'react';
import Link from 'next/link';
import {
  Radar,
  ArrowRight,
  TrendingUp,
  Cpu,
  ShieldAlert,
  Sparkles,
  Layers,
  CheckCircle2,
  BarChart3,
  Search,
  Code2
} from 'lucide-react';

export default function HomePage() {
  const sampleMarketSkills = [
    { name: 'React', freq: 87, count: '76/87 jobs', cat: 'Frontend', color: 'from-blue-500 to-cyan-400' },
    { name: 'TypeScript', freq: 73, count: '64/87 jobs', cat: 'Language', color: 'from-indigo-500 to-blue-500' },
    { name: 'Node.js', freq: 68, count: '59/87 jobs', cat: 'Backend', color: 'from-emerald-500 to-teal-400' },
    { name: 'AWS', freq: 54, count: '47/87 jobs', cat: 'Cloud', color: 'from-amber-500 to-orange-400' },
    { name: 'Docker', freq: 49, count: '43/87 jobs', cat: 'DevOps', color: 'from-purple-500 to-pink-500' },
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-[400px] h-[400px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Hero Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-medium mb-8 backdrop-blur-md shadow-inner">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Live Market Intelligence — Not Just Another Job Board</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.1]">
          Understand where you stand in today's{' '}
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-300 bg-clip-text text-transparent">
            developer job market
          </span>
          .
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Analyze live job opportunities, discover the skills tech companies repeatedly demand, and compare them against your current skillset with transparent, mathematical readiness signals.
        </p>

        {/* Primary CTAs */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/analyze"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-500 hover:to-indigo-500 shadow-xl shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5 transition duration-200"
          >
            <Radar className="w-5 h-5 animate-pulse text-cyan-300" />
            Check My Market Readiness
            <ArrowRight className="w-4 h-4" />
          </Link>
          <a
            href="#how-it-works"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-4 rounded-xl text-base font-medium text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-800 transition"
          >
            How CareerRadar Works
          </a>
        </div>

        {/* Live Signal Preview Card */}
        <div className="mt-16 max-w-4xl mx-auto p-6 rounded-2xl glass-panel border border-slate-800/80 text-left shadow-2xl relative">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800/60">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                <span className="text-xs font-mono uppercase tracking-wider text-emerald-400">Live Sample Market Scan</span>
              </div>
              <h3 className="text-xl font-bold text-white mt-1">Full Stack Developer — Ahmedabad, India</h3>
            </div>
            <div className="px-4 py-2 rounded-xl bg-slate-900/80 border border-slate-800 text-right">
              <span className="text-xs text-slate-400 block">Sample Analyzed</span>
              <span className="text-base font-mono font-bold text-cyan-400">87 Live Jobs</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-6">
            {/* Market Frequency Bars */}
            <div className="lg:col-span-2 space-y-3.5">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <BarChart3 className="w-4 h-4 text-blue-400" /> Verified Market Skill Frequency
              </span>
              {sampleMarketSkills.map((sk) => (
                <div key={sk.name} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-200">{sk.name}</span>
                    <span className="font-mono text-slate-400">{sk.freq}% <span className="text-slate-500">({sk.count})</span></span>
                  </div>
                  <div className="h-2 w-full bg-slate-800/80 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${sk.color} rounded-full`}
                      style={{ width: `${sk.freq}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Candidate Match Result Card */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800/80 flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Candidate Signal</span>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-4xl font-extrabold text-blue-400 font-mono">72%</span>
                  <span className="text-xs text-emerald-400 font-medium">Ready</span>
                </div>
                <div className="mt-3 space-y-1.5 text-xs text-slate-300">
                  <div className="flex items-center gap-1.5 text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Matched: React, Node.js
                  </div>
                  <div className="flex items-center gap-1.5 text-amber-400">
                    <ShieldAlert className="w-3.5 h-3.5" /> Weak: JavaScript
                  </div>
                  <div className="flex items-center gap-1.5 text-red-400">
                    <ShieldAlert className="w-3.5 h-3.5" /> Missing: TypeScript, AWS, Docker
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 italic">
                "Closing the TypeScript & AWS gap elevates readiness to 94%."
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Flow Section */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-slate-900">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-blue-400 mb-2">Architectural Foundation</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white">How CareerRadar Delivers Ground Truth</h3>
          <p className="mt-3 text-slate-400 text-sm sm:text-base">
            We don't ask an LLM to guess arbitrary numbers. We ingest real employer job listings, calculate transparent frequencies, and produce actionable market evidence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 rounded-2xl glass-panel border border-slate-800/80 glass-panel-hover">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-5">
              <Search className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">1. Live Market Search</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              Dispatches live queries to Google Jobs via SerpApi for your exact target role and location preferences.
            </p>
          </div>

          <div className="p-6 rounded-2xl glass-panel border border-slate-800/80 glass-panel-hover">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-5">
              <Layers className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">2. Deterministic Gap Engine</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              Standardizes skills against canonical dictionaries and computes mathematical coverage: Matched, Weak, and Missing.
            </p>
          </div>

          <div className="p-6 rounded-2xl glass-panel border border-slate-800/80 glass-panel-hover">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-5">
              <Cpu className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">3. Evidence-Backed Action Plan</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              AI translates the verified mathematical evidence into high-impact project roadmaps and learning milestones.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
