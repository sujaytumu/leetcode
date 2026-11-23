"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clock, endSession, useMock } from "@/lib/mock";

/** Sticky strip under the navbar while a mock interview is running. */
export default function MockBar() {
  const { session, running, remaining } = useMock();
  const path = usePathname();
  if (!session || !running) return null;
  const low = remaining < 300;
  return (
    <div className="mockbar" role="status">
      <b>Mock interview</b>
      <span className={`mockclock${low ? " low" : ""}`} aria-label="Time left">{clock(remaining)}</span>
      <span className="mockprobs">
        {session.slugs.map((s, i) => (
          <Link key={s} href={`/problems/${s}`} className={path === `/problems/${s}` ? "on" : ""}>Problem {i + 1}</Link>
        ))}
      </span>
      <span className="grow" />
      <Link href="/mock">Details</Link>
      <button onClick={() => { if (confirm("End the mock interview now?")) endSession(); }}>End</button>
    </div>
  );
}
