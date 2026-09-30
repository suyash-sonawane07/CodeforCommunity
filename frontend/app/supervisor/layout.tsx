'use client';
import Link from 'next/link';
import { useAuth } from '@/hooks';

export default function SupervisorLayout({ children }: { children: React.ReactNode }) {
  const { logout } = useAuth();
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <header className="bg-white border-b border-slate-200 p-4 flex justify-between items-center shadow-sm">
        <div className="flex gap-6 items-center">
          <h1 className="text-xl font-bold text-blue-700">CivicPulse Supervisor</h1>
          <nav className="flex gap-4">
            <Link href="/supervisor" className="text-slate-600 font-medium hover:text-blue-600 transition">Overview</Link>
            <Link href="/supervisor/map" className="text-slate-600 font-medium hover:text-blue-600 transition">Map</Link>
            <Link href="/supervisor/budget" className="text-slate-600 font-medium hover:text-blue-600 transition">Budget</Link>
            <Link href="/supervisor/data" className="text-slate-600 font-medium hover:text-blue-600 transition">Data</Link>
          </nav>
        </div>
        <button onClick={() => logout()} className="text-red-600 font-medium hover:text-red-800 transition">Logout</button>
      </header>
      <main className="flex-1 p-6">
        {children}
      </main>
    </div>
  );
}
