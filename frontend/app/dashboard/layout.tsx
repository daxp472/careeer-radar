import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Candidate Intelligence Dashboard',
  description: 'View your target market readiness, monitor weekly job radar scans, manage watchlist listings, and track your career growth.',
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
