/** Grey shimmering placeholder lines shown while content loads. */
export default function Skeleton({ lines = 6 }: { lines?: number }) {
  return (
    <div className="skel-block" aria-hidden="true">
      {Array.from({ length: lines }, (_, i) => <div key={i} className="skel" style={{ width: `${95 - ((i * 17) % 40)}%` }} />)}
    </div>
  );
}
