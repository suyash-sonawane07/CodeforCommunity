'use client';
import { useState } from 'react';
import { useAuth } from '@/hooks';
import Link from 'next/link';

export default function SignupPage() {
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState('citizen@municipal.org');
  const [password, setPassword] = useState('password');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(email, password);
  };
  
  return (
    <div className="min-h-screen bg-surface-container flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-surface rounded-2xl shadow-lg border border-outline-variant p-6">
        <h1 className="text-2xl font-bold mb-4">CivicPulse Signup</h1>
        
        {error && (
          <div className="bg-error-container text-on-error-container p-3 rounded-lg mb-4">
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
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        
        <div className="mt-4 text-center text-sm">
          <Link href="/login" className="text-primary hover:underline">Already have an account? Sign in</Link>
        </div>
      </div>
    </div>
  );
}
