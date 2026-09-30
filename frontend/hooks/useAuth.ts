import { useState } from 'react';
import { fetchApi } from '../lib/api';

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error?.message || 'Login failed');
      }
      
      const data = await res.json();
      
      const isSupervisor = data.role === 'supervisor' || data.role === 'reviewer' || data.role === 'analyst' || data.role === 'admin';
      window.location.href = isSupervisor ? '/supervisor' : '/user';
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
  };

  return { login, logout, loading, error };
}
