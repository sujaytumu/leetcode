"use client";
import { Children, isValidElement, ReactNode, useState } from "react";
import Markdown, { type Components } from "react-markdown";
import { formatInput, formatOutput } from "@/lib/example";

const textOf = (n: ReactNode): string =>
  Children.toArray(n).map((c) => (typeof c === "string" ? c : isValidElement(c) ? textOf((c.props as { children?: ReactNode }).children) : "")).join("");

/** Bold the "Input:" / "Output:" / "Explanation:" labels inside an example box, as LeetCode does. */
function boldLabels(code: string): ReactNode {
  return code.split("\n").map((line, i, lines) => {
    const m = /^(Input|Output|Explanation):(.*)$/.exec(line);
    return (
      <span key={i}>
        {m ? <><b>{m[1]}:</b>{m[2]}</> : line}
        {i < lines.length - 1 ? "\n" : ""}
      </span>
    );
  });
}

/** Examples as LeetCode's current page shows them: bold label, value in an inline code chip, one line each. */
function exampleLines(code: string, cpp: boolean): ReactNode {
  const conv = (v: string) => (cpp ? v.replace(/\[/g, "{").replace(/\]/g, "}") : v);
  return code.split("\n").map((line, i) => {
    const m = /^(Input|Output|Explanation):\s*(.*)$/.exec(line);
    if (!m) return line.trim() ? <div key={i} className="exline">{line}</div> : null;
    return m[1] === "Explanation"
      ? <div key={i} className="exline"><b>Explanation:</b> {m[2]}</div>
      : <div key={i} className="exline"><b>{m[1]}:</b> <code>{conv(m[2])}</code></div>;
  });
}

/**
 * A problem statement laid out like LeetCode's: section titles are bold "Constraints:" lines, "Example 1:" labels,
 * and each example sits in a box with a left rule and bold Input / Output labels.
 */
/** Split "intro ### A ... ### B ..." into the intro and its titled sections. */
export function splitSections(md: string): { intro: string; sections: { title: string; body: string }[] } {
  const parts = md.split(/^### +/m);
  const sections = parts.slice(1).map((p) => {
    const nl = p.indexOf("\n");
    return nl < 0 ? { title: p.trim(), body: "" } : { title: p.slice(0, nl).trim(), body: p.slice(nl + 1) };
  });
  return { intro: parts[0], sections };
}

const IO_TITLES = new Set(["input", "output"]);

/**
 * LeetCode's order is statement, Examples, Constraints, then anything else (follow-ups). Ours also carries "Input"
 * and "Output" sections that describe the stdin layout; those go in a collapsed block at the end.
 */
export function reorderForLeetCode(md: string): { main: string; ioFormat: string } {
  const { intro, sections } = splitSections(md);
  if (sections.length === 0) return { main: md, ioFormat: "" };
  const lower = (t: string) => t.trim().toLowerCase();
  const take = (name: string) => sections.filter((s) => lower(s.title) === name);
  const examples = take("examples"), constraints = take("constraints");
  const io = sections.filter((s) => IO_TITLES.has(lower(s.title)));
  const rest = sections.filter((s) => !["examples", "constraints"].includes(lower(s.title)) && !IO_TITLES.has(lower(s.title)));
  const render = (list: { title: string; body: string }[]) => list.map((x) => `### ${x.title}\n${x.body}`).join("\n");
  return {
    main: [intro.trimEnd(), examples.map((x) => x.body.trim()).join("\n\n"), render(constraints), render(rest)].filter(Boolean).join("\n\n"),
    ioFormat: render(io),
  };
}

export default function ProblemDescription({ markdown, python }: { markdown: string; python?: string }) {
  const { main, ioFormat } = reorderForLeetCode(markdown);
  const [cpp, setCpp] = useState(false);
  let firstExample = true;
  const components: Components = {
          h3: ({ children }) => <p className="lchead"><b>{children}:</b></p>,
          strong: ({ children }) => {
            const t = textOf(children);
            if (!/^Example \d+$/.test(t)) return <strong>{children}</strong>;
            const head = (
              <span className="lcexhead">
                <b className="lcexample">{children}:</b>
                {firstExample && (
                  <span className="lcseg" role="group" aria-label="Example notation">
                    <button type="button" className={cpp ? "" : "on"} onClick={() => setCpp(false)}>Original</button>
                    <button type="button" className={cpp ? "on" : ""} onClick={() => setCpp(true)}>C++</button>
                  </span>
                )}
              </span>
            );
            firstExample = false;
            return head;
          },
          pre: ({ children }) => {
            const code = textOf(children).replace(/\n$/, "");
            // Show examples the way LeetCode does (named arguments on one line) when the layout is recognised.
            const m = python ? /^Input:\n([\s\S]*?)\n\nOutput:\n([\s\S]*)$/.exec(code) : null;
            const input = m && python ? formatInput(python, m[1] + "\n") : null;
            const output = m && python ? formatOutput(python, m[2] + "\n") : null;
            if (input !== null && output !== null) {
              return <div className="lcbox2">{exampleLines(`Input: ${input}\nOutput: ${output}`, cpp)}</div>;
            }
            return <pre className="lcbox">{boldLabels(code)}</pre>;
          },
  };
  return (
    <div className="md lcdesc">
      <Markdown components={components}>{main}</Markdown>
      {ioFormat && (
        <details className="iofmt">
          <summary>Input / Output format</summary>
          <Markdown components={components}>{ioFormat}</Markdown>
        </details>
      )}
    </div>
  );
}
