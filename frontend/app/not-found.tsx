import Link from "next/link";

export default function NotFound() {
  return (
    <div style={{ textAlign: "center", padding: "56px 0" }}>
      <h2 style={{ fontSize: 40, margin: 0 }}>404</h2>
      <p className="mute">That page does not exist.</p>
      <p><Link href="/">Back to the problem list</Link></p>
    </div>
  );
}
