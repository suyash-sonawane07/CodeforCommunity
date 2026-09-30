import { useState } from 'react';
import { fetchApi } from '../lib/api';

export function useSimulation() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const simulate = async (allocations: any) => {
    setLoading(true);
    try {
      const res = await fetchApi<any>('/simulations', {
        method: 'POST',
        body: JSON.stringify({ sector_allocations: allocations })
      });
      setResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return { simulate, loading, result };
}
