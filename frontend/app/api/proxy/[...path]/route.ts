import { NextResponse, NextRequest } from 'next/server';

function getBackendUrl(): string {
  const url = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`;
  }
  return url;
}

const BACKEND_URL = getBackendUrl();

async function handle(req: NextRequest, { params }: { params: { path: string[] } }) {
  const token = req.cookies.get('token')?.value;
  const path = params.path.join('/');
  const targetUrl = new URL(`/${path}`, BACKEND_URL);
  targetUrl.search = req.nextUrl.search;

  const headers = new Headers();
  req.headers.forEach((value, key) => {
    if (key.toLowerCase() !== 'host' && key.toLowerCase() !== 'connection') {
      headers.set(key, value);
    }
  });

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let body: any = undefined;
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    try {
      body = await req.text(); // fetch text or buffer
    } catch (e) {}
  }

  const response = await fetch(targetUrl.toString(), {
    method: req.method,
    headers,
    body,
  });

  const resHeaders = new Headers(response.headers);
  resHeaders.delete('content-encoding');

  return new NextResponse(response.body, {
    status: response.status,
    headers: resHeaders,
  });
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
