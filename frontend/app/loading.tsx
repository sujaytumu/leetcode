/** Shown while a page's code loads, so navigation never flashes blank. */
export default function Loading() {
  return (
    <div className="skel-block" role="status" aria-label="Loading" style={{ maxWidth: 960, margin: "32px auto", padding: "0 16px" }}>
      <div className="skel" style={{ width: "30%", height: 22 }} />
      <div className="skel" style={{ width: "100%" }} />
      <div className="skel" style={{ width: "92%" }} />
      <div className="skel" style={{ width: "96%" }} />
      <div className="skel" style={{ width: "70%" }} />
    </div>
  );
}
