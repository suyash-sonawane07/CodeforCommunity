const NEXT_PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/proxy';

export class ApiError extends Error {
  code?: string;
  details?: any;
  constructor(message: string, code?: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }
}

let isRedirecting = false;

export async function fetchApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${NEXT_PUBLIC_API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && path !== '/auth/login') {
    if (typeof window !== 'undefined' && !isRedirecting) {
      isRedirecting = true;
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.replace('/login?expired=1');
    }
    return new Promise(() => {}); // never resolve while redirecting
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(errorBody.error?.message || response.statusText || 'API Error', errorBody.error?.code);
  }

  return response.json();
}
