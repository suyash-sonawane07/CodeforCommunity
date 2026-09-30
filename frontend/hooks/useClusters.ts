import { useState, useEffect } from 'react';
import { fetchApi } from '../lib/api';

export function useClusters(filters = '') {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchClusters = () => {
    fetchApi<any>(`/clusters${filters}`)
      .then(res => setData(res.items || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchClusters();
    const interval = setInterval(fetchClusters, 15000);
    return () => clearInterval(interval);
  }, [filters]);

  return { data, loading, refetch: fetchClusters };
}

export function useClusterDetail(id: string) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if(!id) return;
    fetchApi<any>(`/clusters/${id}`)
      .then(res => setData(res))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  return { data, loading };
}

export function usePriorities() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi<any>('/priorities')
      .then(res => setData(res))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return { data, loading };
}

export function useReview() {
  const [loading, setLoading] = useState(false);
  const review = async (id: string, action: string, note: string) => {
    setLoading(true);
    try {
      await fetchApi(`/clusters/${id}/review`, {
        method: 'POST',
        body: JSON.stringify({ action, note })
      });
    } finally {
      setLoading(false);
    }
  };
  return { review, loading };
}
