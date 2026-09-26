'use client';

import React from 'react';
import { CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

interface SkillChipProps {
  name: string;
  type: 'matched' | 'weak' | 'missing';
  proficiency?: string | null;
  marketFrequencyPct?: number;
  importance?: string;
  onClick?: () => void;
}

export default function SkillChip({
  name,
  type,
  proficiency,
  marketFrequencyPct,
  importance,
  onClick,
}: SkillChipProps) {
  const isMatched = type === 'matched';
  const isWeak = type === 'weak';
  const isMissing = type === 'missing';

  const styles = isMatched
    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/25 hover:border-emerald-500/40'
    : isWeak
    ? 'bg-amber-500/10 text-amber-300 border-amber-500/25 hover:border-amber-500/40'
    : 'bg-rose-500/10 text-rose-300 border-rose-500/25 hover:border-rose-500/40';

  const Icon = isMatched ? CheckCircle2 : isWeak ? AlertCircle : XCircle;

  return (
    <div
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono transition shadow-sm ${styles} ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <Icon className="w-3.5 h-3.5 flex-shrink-0" />
      <span className="font-semibold text-slate-100">{name}</span>

      {proficiency && (
        <span className="text-[10px] opacity-75 capitalize">
          ({proficiency})
        </span>
      )}

      {marketFrequencyPct !== undefined && marketFrequencyPct > 0 && (
        <span className="text-[10px] opacity-60 bg-slate-900/60 px-1.5 py-0.5 rounded ml-0.5">
          {Math.round(marketFrequencyPct)}%
        </span>
      )}

      {importance === 'required' && (
        <span className="text-[9px] uppercase tracking-wider text-rose-400 font-bold ml-0.5">
          REQ
        </span>
      )}
    </div>
  );
}
