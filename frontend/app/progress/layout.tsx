import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Candidate Progress & Skill Evolution',
  description: 'Track how your market readiness score and skill proficiencies evolve over time with detailed analysis deltas.',
};

export default function ProgressLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
