/**
 * Public, non-personal API paths that the site can serve from a Vercel-side cache (see app/catalog).
 * Personal data (progress, profile, submissions, bookmarks, run/submit) must never match.
 */
const PUBLIC = [
  /^\/api\/meta(\?|$)/,
  /^\/api\/tags(\?|$)/,
  /^\/api\/plans(\?|$)/,
  /^\/api\/daily(\?|$)/,
  /^\/api\/problems(\?|$)/,
  /^\/api\/problems\/[a-z0-9-]+(\/study)?(\?|$)/,
];

export const isCatalogPath = (apiPath: string): boolean => PUBLIC.some((re) => re.test(apiPath));

/** Same-origin URL of the cached copy of an API path, e.g. /api/meta -> /catalog/meta. */
export const catalogUrl = (apiPath: string): string => `/catalog${apiPath.replace(/^\/api/, "")}`;
