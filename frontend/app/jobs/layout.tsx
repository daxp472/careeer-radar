import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Live Tech Jobs & Match Explorer',
  description: 'Search centralized live developer jobs filtered by recency, inspect match scores, and discover required vs preferred skill requirements.',
};

export default function JobsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
