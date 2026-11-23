import Link from "next/link";
import { tagLabel, type ProblemSummary } from "@/lib/api";

const cap = (d: string) => d[0] + d.slice(1).toLowerCase();

/** Problems that share the most topics with this one, closest in study-path order first (LeetCode's "Similar Questions"). */
export function similarTo(current: ProblemSummary, all: ProblemSummary[], limit = 6): ProblemSummary[] {
  const mine = new Set(current.tags);
  const pos = current.number ?? current.id;
  return all
    .filter((p) => p.slug !== current.slug)
    .map((p) => ({ p, shared: p.tags.filter((t) => mine.has(t)).length }))
    .filter((x) => x.shared > 0)
    .sort((a, b) => b.shared - a.shared || Math.abs((a.p.number ?? a.p.id) - pos) - Math.abs((b.p.number ?? b.p.id) - pos))
    .slice(0, limit)
    .map((x) => x.p);
}

/** Collapsible sections under a problem statement, as on LeetCode. */
export default function SimilarProblems({ current, all }: { current: ProblemSummary; all: ProblemSummary[] }) {
  const similar = similarTo(current, all);
  return (
    <div className="related">
      <details>
        <summary>Related Topics</summary>
        <div className="relbody">{current.tags.map((t) => <span className="tag" key={t}>{tagLabel(t)}</span>)}</div>
      </details>
      {similar.length > 0 && (
        <details>
          <summary>Similar Questions</summary>
          <ul className="relbody simlist">
            {similar.map((p) => (
              <li key={p.slug}>
                <Link href={`/problems/${p.slug}`}>{p.number ?? p.id}. {p.title}</Link>
                <span className={p.difficulty}>{cap(p.difficulty)}</span>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
