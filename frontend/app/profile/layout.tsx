import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Candidate Profile & Skill Inventory',
  description: 'Manage your target role, location, remote preferences, and skill proficiencies to receive tailored market intelligence.',
};

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
