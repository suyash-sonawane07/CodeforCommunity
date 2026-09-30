'use client';
import { useState, Suspense } from 'react';
import { useAuth } from '@/hooks';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

function LoginForm() {
  const { login, loading, error } = useAuth();
  const searchParams = useSearchParams();
  const expired = searchParams.get('expired');
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(email, password);
  };

  const fillDemoUser = () => {
    setEmail('user@demo.com');
    setPassword('demo123');
  };

  const fillDemoSupervisor = () => {
    setEmail('supervisor@demo.com');
    setPassword('demo123');
  };
  
  return (
    <div className="w-full max-w-md bg-surface rounded-2xl shadow-lg border border-outline-variant p-6">
      <h1 className="text-2xl font-bold mb-4">CivicPulse Login</h1>
      
      {expired && !error && (
        <div className="bg-warning-container text-on-warning-container p-3 rounded-lg mb-4 text-sm">
          Your session has expired. Please log in again.
        </div>
      )}

      {error && (
        <div className="bg-error-container text-on-error-container p-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input 
            type="email" 
            className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required 
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input 
            type="password" 
            className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required 
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-primary-container text-on-primary py-2 rounded-lg font-semibold"
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
      
      <div className="mt-6 flex flex-col gap-2">
        <p className="text-sm text-center text-slate-500">Quick fill demo accounts:</p>
        <div className="flex gap-2 justify-center">
          <button onClick={fillDemoUser} type="button" className="text-xs bg-slate-200 hover:bg-slate-300 py-1 px-3 rounded-full text-slate-800">Demo User</button>
          <button onClick={fillDemoSupervisor} type="button" className="text-xs bg-slate-200 hover:bg-slate-300 py-1 px-3 rounded-full text-slate-800">Demo Supervisor</button>
        </div>
      </div>

      <div className="mt-4 text-center text-sm">
        <Link href="/signup" className="text-primary hover:underline">Need an account? Sign up</Link>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-surface-container flex items-center justify-center p-4">
      <Suspense fallback={<div className="w-full max-w-md bg-surface rounded-2xl shadow-lg border border-outline-variant p-6 text-center">Loading...</div>}>
        <LoginForm />
      </Suspense>
    </div>
  );
}
