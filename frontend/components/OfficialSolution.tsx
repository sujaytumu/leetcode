"use client";
import Markdown from "react-markdown";
import { useEffect, useState } from "react";
import { Answer, api } from "@/lib/api";

const LABEL: Record<string, string> = { cpp: "C++", java: "Java", python: "Python", javascript: "JavaScript" };
const ORDER = ["cpp", "java", "python", "javascript"];

/**
 * LeetCode pins the official solution at the top of the Solutions tab. This is the same: the repo's verified
 * reference answer for the problem (approach, complexity and code in each language). The code stays folded until
 * you open the card, so it does not spoil the problem just by visiting the tab.
 */
export default function OfficialSolution({ slug }: { slug: string }) {
  const [data, setData] = useState<Answer | null | undefined>(undefined); // undefined = loading, null = none published
  const [open, setOpen] = useState(false);
  const [lang, setLang] = useState("cpp");
  const [approach, setApproach] = useState<"optimal" | "brute">("optimal");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let live = true;
    setData(undefined); setOpen(false); setError("");
    api<Answer | null>(`/api/problems/${slug}/solution`, {}, 30000)
      .then((a) => {
        if (!live) return;
        const keys = a ? ORDER.filter((k) => a.solutions?.[k]) : [];
        setData(a && keys.length ? a : null);
        if (keys.length) setLang(keys[0]);
      })
      .catch((e: Error) => { if (live) { setData(null); setError(e.message); } });
    return () => { live = false; };
  }, [slug]);

  if (data === undefined) return <div className="solrow official skel" style={{ height: 74 }} aria-busy="true" />;
  if (data === null) {
    return (
      <div className="solrow official none">
        <div className="soltitle">Official Solution <span className="pill official-pill">Official</span></div>
        <div className="mute solexcerpt">{error ? `Could not load it (${error}).` : "No reference solution has been published for this problem yet."}</div>
      </div>
    );
  }
  const keys = ORDER.filter((k) => data.solutions[k]);
  const brute = data.bruteForce?.[lang];
  const shown = approach === "brute" && brute ? brute : data.solutions[lang];
  const copy = async () => {
    try { await navigator.clipboard.writeText(shown ?? ""); setCopied(true); setTimeout(() => setCopied(false), 1500); } catch { /* clipboard blocked */ }
  };

  return (
    <div className={`solrow official${open ? " open" : ""}`}>
      <div role="button" tabIndex={0} className="officialhead" aria-expanded={open} onClick={() => setOpen(!open)}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setOpen(!open); } }}>
        <div>
          <div className="soltitle">📌 Official Solution <span className="pill official-pill">Official</span></div>
          <div className="mute solmeta">{keys.map((k) => LABEL[k] ?? k).join(" · ")} · approach, complexity and code</div>
        </div>
        <span className="mute" aria-hidden="true">{open ? "▴" : "▾"}</span>
      </div>
      {open && (
        <div className="officialbody">
          {data.editorial && <div className="md"><Markdown>{data.editorial}</Markdown></div>}
          <div className="casechips" style={{ marginTop: 12 }}>
            {keys.map((k) => <button key={k} className={lang === k ? "on" : ""} onClick={() => setLang(k)}>{LABEL[k] ?? k}</button>)}
            {brute && (
              <>
                <span className="approach-sep" aria-hidden="true" />
                <button className={approach === "brute" ? "on" : ""} onClick={() => setApproach("brute")} title="The simple first idea, slower">Brute force</button>
                <button className={approach !== "brute" ? "on" : ""} onClick={() => setApproach("optimal")} title="The efficient solution">Optimised</button>
              </>
            )}
            <span className="grow" />
            <button onClick={copy}>{copied ? "✔ Copied" : "Copy"}</button>
          </div>
          <pre className="answer-code">{shown}</pre>
          <p className="mute" style={{ fontSize: 12, margin: "6px 0 0" }}>
            Paste it into the editor as it is: the judge supplies the input parsing and printing.
          </p>
        </div>
      )}
    </div>
  );
}
