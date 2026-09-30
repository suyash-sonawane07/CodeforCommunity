import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000';

export async function POST(request: Request) {
  const body = await request.json();
  
  try {
    const backendRes = await fetch(`${BACKEND_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: body.email, password: body.password }),
    });

    if (!backendRes.ok) {
      const errorBody = await backendRes.json().catch(() => ({}));
      return NextResponse.json(errorBody, { status: backendRes.status });
    }

    const data = await backendRes.json();
    const res = NextResponse.json({ success: true, role: data.role });
    
    res.cookies.set({
      name: 'token',
      value: data.access_token,
      httpOnly: true,
      path: '/',
      sameSite: 'lax',
    });
    
    // We can also store role in an httpOnly cookie for the middleware, 
    // but we decode the JWT in middleware anyway. The prompt says "Middleware: decode the JWT (verify expiry and role)".
    // So we don't strictly need a separate role cookie, but let's keep it for compatibility or just delete it.
    // The prompt says "Token storage: httpOnly cookie ONLY... decode JWT". So we only need 'token'.
    
    return res;
  } catch (error: any) {
    return NextResponse.json({ error: { message: "Internal Server Error" } }, { status: 500 });
  }
}
