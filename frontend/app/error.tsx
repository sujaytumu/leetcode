"use client";

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div style={{ textAlign: "center", padding: "56px 0" }}>
      <h2 style={{ margin: 0 }}>Something went wrong</h2>
      <p className="mute">{error.message || "An unexpected error occurred."}</p>
      <button className="primary" onClick={reset}>Try again</button>
    </div>
  );
}
