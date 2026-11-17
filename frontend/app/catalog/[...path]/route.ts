import { NextRequest, NextResponse } from "next/server";
import { isCatalogPath } from "@/lib/catalog";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export const maxDuration = 15;

/**
 * Cached read-through proxy for public catalogue data. Vercel keeps the backend's answer for 5 minutes and, once it
 * is older, serves the stale copy instantly while refreshing in the background. That keeps first paint fast even
 * when the free-tier backend is asleep, and the background refresh also wakes it. Gives up after 8s so the browser
 * can fall back to the backend directly.
 */
export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const target = `/api/${path.join("/")}${req.nextUrl.search}`;
  if (!isCatalogPath(target)) return NextResponse.json({ error: "Not cacheable" }, { status: 404 });
  try {
    const res = await fetch(`${API}${target}`, {
      next: { revalidate: 300 },
      signal: AbortSignal.timeout(8000),
      headers: { Accept: "application/json" },
    });
    if (res.status === 204) return new NextResponse(null, { status: 204 });
    if (!res.ok) return new NextResponse(null, { status: res.status === 404 ? 404 : 502 });
    return new NextResponse(await res.text(), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, s-maxage=300, stale-while-revalidate=86400",
      },
    });
  } catch {
    return new NextResponse(null, { status: 504 });
  }
}
