"use client";
import { Children, isValidElement, ReactNode } from "react";
import Markdown from "react-markdown";

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

/**
 * A problem statement laid out like LeetCode's: section titles are bold "Constraints:" lines, "Example 1:" labels,
 * and each example sits in a box with a left rule and bold Input / Output labels.
 */
export default function ProblemDescription({ markdown }: { markdown: string }) {
  return (
    <div className="md lcdesc">
      <Markdown
        components={{
          h3: ({ children }) => <p className="lchead"><b>{children}:</b></p>,
          strong: ({ children }) => {
            const t = textOf(children);
            return /^Example \d+$/.test(t) ? <b className="lcexample">{children}:</b> : <strong>{children}</strong>;
          },
          pre: ({ children }) => {
            const code = textOf(children).replace(/\n$/, "");
            return <pre className="lcbox">{boldLabels(code)}</pre>;
          },
        }}
      >
        {markdown}
      </Markdown>
    </div>
  );
}
