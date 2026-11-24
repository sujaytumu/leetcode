export const dynamic = "force-dynamic";

/** The id of the running deployment; the app compares it with the one it was loaded with to spot new releases. */
export function GET() {
  return Response.json({ id: process.env.NEXT_PUBLIC_BUILD_ID ?? "dev" }, { headers: { "Cache-Control": "no-store" } });
}
