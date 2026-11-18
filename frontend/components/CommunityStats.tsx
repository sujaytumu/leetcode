import { CommunityStats as Stats } from "@/lib/api";

/** LeetCode's "Community Stats": discussion posts and the upvotes they earned, each with the last 7 days. */
export default function CommunityStats({ stats }: { stats: Stats }) {
  const rows = [
    { icon: "💬", color: "#10b9a6", label: "Discuss", total: stats.discuss, week: stats.discussLastWeek },
    { icon: "⭐", color: "#ffa116", label: "Reputation", total: stats.reputation, week: stats.reputationLastWeek },
  ];
  return (
    <section className="card commstats">
      <h3 className="sect-h">Community Stats</h3>
      {rows.map((r) => (
        <div key={r.label} className="commrow">
          <span className="commicon" style={{ color: r.color }} aria-hidden="true">{r.icon}</span>
          <div>
            <div><span className="commlabel">{r.label}</span> <b>{r.total}</b></div>
            <div className="mute commweek">Last week <span>{r.week}</span></div>
          </div>
        </div>
      ))}
    </section>
  );
}
