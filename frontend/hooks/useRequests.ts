import { useState, useEffect } from 'react';
import { fetchApi } from '../lib/api';

export function useMyRequests() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchApi<any>('/requests?mine=true')
      .then(res => setData(res.items || []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

export function useCreateRequest() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = async (payload: any) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchApi<any>('/requests', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      return res;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  const uploadAudio = async (id: string, base64: string) => {
      // Actually backend expects audio_base64 in the main request or separate POST /requests/{id}/audio?
      // Based on PRD / schema: POST /requests/{id}/audio
      return fetchApi<any>(`/requests/${id}/audio`, {
          method: 'POST',
          body: JSON.stringify({ audio_base64: base64 })
      });
  }

  return { create, uploadAudio, loading, error };
}

export function useRequestStatus(id: string) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    const fetchStatus = async () => {
      try {
        const res = await fetchApi<any>(`/requests/${id}`);
        setData(res);
        if (res.status === 'resolved' || res.status === 'completed' || res.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        clearInterval(interval);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStatus();
    interval = setInterval(fetchStatus, 3000);
    
    return () => clearInterval(interval);
  }, [id]);

  return { data, loading };
}
