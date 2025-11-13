import type { Metadata } from 'next'
import AppShell from '@/components/AppShell';
import './globals.css'

export const metadata: Metadata = {
  title: 'Algo-Viz - Master Engineering Through Visual Animations',
  description: 'Learn engineering subjects with animated step-by-step solutions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AppShell>
          {children}
        </AppShell>
      </body>
    </html>
  )
}

// =========================================
// IMPORTANT: This is the ONLY code that should be in app/layout.tsx
// The sidebar and header should be in a separate component!
// =========================================