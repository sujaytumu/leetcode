import Link from "next/link";
import BackLink from "@/components/BackLink";

export default function NotFound() {
  return (
    <div style={{ textAlign: "center", padding: "56px 0" }}>
      <h2 style={{ fontSize: 40, margin: 0 }}>404</h2>
      <p className="mute">That page does not exist.</p>
      <p className="nf-actions"><BackLink fallback="/problemset">Go back</BackLink><Link href="/problemset" className="btn">Problem list</Link></p>
    </div>
  );
}
