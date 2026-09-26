import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Job Skill Gap & Match Breakdown',
  description: 'Deep-dive into exact employer requirements, candidate skill match scoring, and targeted bridge recommendations.',
};

export default function JobDetailLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
