import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Create Your Free Candidate Account',
  description: 'Join CareerRadar to track tech job market demand, evaluate skill gaps, and receive automated weekly job match alerts.',
};

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
