/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  async rewrites() {
    const backend = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    return [
      { source: '/docs', destination: `${backend}/docs` },
      { source: '/openapi.json', destination: `${backend}/openapi.json` },
      { source: '/health', destination: `${backend}/health` },
      { source: '/auth/:path*', destination: `${backend}/auth/:path*` },
      { source: '/requests/:path*', destination: `${backend}/requests/:path*` },
      { source: '/clusters/api/:path*', destination: `${backend}/clusters/:path*` },
      { source: '/geospatial/:path*', destination: `${backend}/geospatial/:path*` },
      { source: '/simulations/:path*', destination: `${backend}/simulations/:path*` },
      { source: '/priorities/:path*', destination: `${backend}/priorities/:path*` },
      { source: '/stats/:path*', destination: `${backend}/stats/:path*` },
      { source: '/infrastructure/:path*', destination: `${backend}/infrastructure/:path*` },
      { source: '/outcomes/:path*', destination: `${backend}/outcomes/:path*` },
      { source: '/datasets/api/:path*', destination: `${backend}/datasets/:path*` },
      { source: '/audit/:path*', destination: `${backend}/audit/:path*` },
      { source: '/webhooks/:path*', destination: `${backend}/webhooks/:path*` },
    ];
  },
};

module.exports = nextConfig;
