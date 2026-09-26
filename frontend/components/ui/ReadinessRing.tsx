'use client';

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface ReadinessRingProps {
  score: number;
  previousScore?: number | null;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
}

export default function ReadinessRing({
  score,
  previousScore,
  size = 140,
  strokeWidth = 10,
  showLabel = true,
}: ReadinessRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.min(100, Math.max(0, score));
  const offset = circumference - (clampedScore / 100) * circumference;

  const isHigh = clampedScore >= 80;
  const isMed = clampedScore >= 60 && clampedScore < 80;

  const strokeColor = isHigh ? '#10b981' : isMed ? '#3b82f6' : '#f59e0b';
  const tier = isHigh ? 'Highly Ready' : isMed ? 'Strong Alignment' : clampedScore >= 40 ? 'Building Foundation' : 'Early Stage';

  const delta = previousScore !== undefined && previousScore !== null ? Number((score - previousScore).toFixed(1)) : null;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="rotate-[-90deg]">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center Metric */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-3xl sm:text-4xl font-black font-mono tracking-tight text-white">
            {clampedScore}%
          </span>
          <span className="text-[10px] uppercase font-mono tracking-widest text-slate-400 -mt-1">
            Readiness
          </span>
        </div>
      </div>

      {showLabel && (
        <div className="mt-3 flex flex-col items-center gap-1">
          <span
            className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold border font-mono"
            style={{
              color: strokeColor,
              backgroundColor: `${strokeColor}15`,
              borderColor: `${strokeColor}30`,
            }}
          >
            {tier}
          </span>

          {delta !== null && (
            <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400 mt-0.5">
              {delta > 0 ? (
                <span className="text-emerald-400 flex items-center gap-0.5 font-bold">
                  <TrendingUp className="w-3 h-3" /> +{delta}%
                </span>
              ) : delta < 0 ? (
                <span className="text-rose-400 flex items-center gap-0.5 font-bold">
                  <TrendingDown className="w-3 h-3" /> {delta}%
                </span>
              ) : (
                <span className="text-slate-400 flex items-center gap-0.5">
                  <Minus className="w-3 h-3" /> Unchanged
                </span>
              )}
              <span>vs previous scan</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
