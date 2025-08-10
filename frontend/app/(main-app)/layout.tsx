import NavBar from '@/components/layout/NavBar';
import React from 'react';


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-900">
      <NavBar />
      <main>
        {children}
      </main>
    </div>
  );
}