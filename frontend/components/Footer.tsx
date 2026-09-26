import React from 'react';
import Link from 'next/link';
import { Radar, ShieldCheck, Database, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/60 mt-auto py-12 text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="md:col-span-2 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center">
              <Radar className="w-4 h-4 text-blue-400" />
            </div>
            <span className="font-bold text-white tracking-wide">CAREERRADAR</span>
          </div>
          <p className="text-sm text-slate-400 max-w-sm">
            Live developer market-readiness intelligence. Turning raw hiring demand into transparent, actionable skill signals.
          </p>
          <div className="flex items-center gap-4 text-xs font-mono text-slate-400 pt-2">
            <span className="flex items-center gap-1"><Database className="w-3 h-3 text-cyan-400" /> Google Jobs Live API</span>
            <span className="flex items-center gap-1"><Cpu className="w-3 h-3 text-emerald-400" /> Deterministic Engine</span>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">Product</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/analyze" className="hover:text-white transition">Market Readiness Check</Link></li>
            <li><Link href="/dashboard" className="hover:text-white transition">Analysis History</Link></li>
            <li><Link href="/profile" className="hover:text-white transition">Developer Profile</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">Integrations</h4>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-blue-400" /> SerpApi Google Jobs</li>
            <li className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-indigo-400" /> Gemini Explanations</li>
            <li className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> PostgreSQL Source of Truth</li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 pt-6 border-t border-slate-900 text-xs text-center text-slate-400">
        &copy; {new Date().getFullYear()} CareerRadar. Live Market Intelligence Platform.
      </div>
    </footer>
  );
}
