import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/lib/auth-context';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: {
    default: 'CareerRadar — Live Developer Market Readiness & Skill Intelligence',
    template: '%s | CareerRadar',
  },
  description:
    'Continuous market readiness and skill intelligence platform for developers. Analyze live tech job postings, evaluate deterministic skill gaps, and track career progress over time.',
  keywords: [
    'CareerRadar',
    'Developer Job Market',
    'Skill Gap Analysis',
    'Tech Readiness',
    'Software Engineer Jobs',
    'Full Stack Developer',
    'Python Developer',
    'React Developer',
    'Google Jobs',
    'Career Intelligence',
  ],
  authors: [{ name: 'CareerRadar Engineering' }],
  creator: 'CareerRadar',
  publisher: 'CareerRadar',
  metadataBase: new URL('https://careerradar.io'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://careerradar.io',
    siteName: 'CareerRadar',
    title: 'CareerRadar — Live Developer Market Readiness & Skill Intelligence',
    description:
      'Continuous market readiness and skill intelligence platform for developers. Analyze live jobs, calculate deterministic skill gaps, and get AI-guided action plans.',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CareerRadar — Developer Market Readiness Platform',
    description:
      'Turn the live technology job market into actionable skill signals and personalized career intelligence.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-slate-950 text-slate-100 flex flex-col min-h-screen antialiased selection:bg-blue-600 selection:text-white" suppressHydrationWarning>
        <AuthProvider>
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
