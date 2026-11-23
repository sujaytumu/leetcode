const BACKEND = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080").replace(/\/+$/, "");

/**
 * The browser only ever talks to this site's own origin; Vercel forwards /api to the backend. That removes CORS
 * entirely (any Vercel domain or preview URL works, and a waking backend can't be mistaken for a network error)
 * and saves the preflight round trip on every request.
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      { source: "/u/:username", destination: "/:username", permanent: true },
      { source: "/problems", destination: "/problemset", permanent: true },
    ];
  },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${BACKEND}/api/:path*` },
      { source: "/actuator/:path*", destination: `${BACKEND}/actuator/:path*` },
    ];
  },
};
export default nextConfig;
