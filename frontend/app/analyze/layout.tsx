import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Live Market Readiness Analyzer',
  description: 'Analyze real-time employer demand, compare your candidate skills against live job listings, and discover high-priority skill gaps.',
};

export default function AnalyzeLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
