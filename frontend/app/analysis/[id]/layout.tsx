import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Market Readiness & Action Plan Report',
  description: 'Review your personalized market readiness score, top skill gaps, and AI-guided career action plan.',
};

export default function AnalysisDetailLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
