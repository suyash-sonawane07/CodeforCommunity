import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { jwtVerify } from 'jose';

const JWT_SECRET = process.env.JWT_SECRET || "change-me-dev-only-not-a-secret";
const secretKey = new TextEncoder().encode(JWT_SECRET);

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;

  const res = NextResponse.next();
  res.headers.set('x-debug-token-exists', token ? 'yes' : 'no');
  res.headers.set('x-debug-path', request.nextUrl.pathname);

  if (request.nextUrl.pathname.startsWith('/api/proxy/')) {
    return res;
  }

  const isAuthRoute = request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/signup';
  const isSupervisorRoute = request.nextUrl.pathname.startsWith('/supervisor');
  const isUserRoute = request.nextUrl.pathname.startsWith('/user');

  if (request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (isAuthRoute) {
    if (token) {
      try {
        const { payload } = await jwtVerify(token, secretKey);
        const role = payload.role as string;
        const isSupervisor = role === 'supervisor' || role === 'admin' || role === 'reviewer';
        return NextResponse.redirect(new URL(isSupervisor ? '/supervisor' : '/user', request.url));
      } catch (err) {
        res.cookies.delete('token');
        return res;
      }
    }
    return res;
  }

  if (!token && (isSupervisorRoute || isUserRoute)) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (token) {
    try {
      const { payload } = await jwtVerify(token, secretKey);
      const userRole = payload.role as string;
      res.headers.set('x-debug-role', userRole);

      if (isSupervisorRoute && userRole !== 'supervisor' && userRole !== 'admin' && userRole !== 'reviewer') {
        const redirect = NextResponse.redirect(new URL('/user', request.url));
        redirect.headers.set('x-debug-redirect', 'to-user');
        return redirect;
      }

    } catch (err) {
      const redir = NextResponse.redirect(new URL('/login?expired=1', request.url));
      redir.cookies.delete('token');
      return redir;
    }
  }

  return res;
}

export const config = {
  matcher: ['/user/:path*', '/user', '/supervisor', '/supervisor/:path*', '/login', '/signup', '/'],
};
