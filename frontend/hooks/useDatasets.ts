import { useState, useEffect } from 'react';
import { fetchApi } from '../lib/api';

export function useDatasets() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi<any>('/datasets')
      .then(res => setData(res.items || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return { data, loading };
}
