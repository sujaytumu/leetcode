/**
 * Turns a problem's stdin-style example into LeetCode's named-argument form:
 *   4 / 2 7 11 15 / 9   ->   nums = [2,7,11,15], target = 9
 * The input layout is read from the Python starter's main(), which is generated from a small fixed set of
 * statements, so nothing is guessed. Anything unrecognised returns null and the caller shows the raw text.
 */
type Stmt =
  | { kind: "count" }
  | { kind: "rowcount" }
  | { kind: "ints" | "int" | "dbl" | "str" | "strs" | "matrix" | "tree" | "list"; name: string };

function mainBody(python: string): string[] | null {
  const m = /def main\(\):\n([\s\S]*?)\n\s*\nif __name__/.exec(python);
  return m ? m[1].split("\n").map((l) => l.trim()).filter(Boolean) : null;
}

/** The input statements of main(), in order (count lines included, as they consume a line too). */
export function parseInputSpec(python: string): Stmt[] | null {
  const body = mainBody(python);
  if (!body) return null;
  const out: Stmt[] = [];
  for (const l of body) {
    if (l === "pos = 0" || l.startsWith("lines = ")) continue;
    if (l.startsWith("result = solve(")) break;
    let m: RegExpExecArray | null;
    if ((m = /^(\w+)_len = int\(lines\[pos\]\); pos \+= 1$/.exec(l))) { out.push({ kind: "count" }); continue; }
    if (/^\w+_rows = int\(lines\[pos\]\.split\(\)\[0\]\); pos \+= 1$/.test(l)) { out.push({ kind: "rowcount" }); continue; }
    if ((m = /^(\w+) = list\(map\(int, lines\[pos\]\.split\(\)\)\) if \1_len > 0 else \[\]; pos \+= 1$/.exec(l))) { out.push({ kind: "ints", name: m[1] }); continue; }
    if (/^\w+_loop = int\(lines\[pos\]\); pos \+= 1$/.test(l)) { out.push({ kind: "int", name: "pos" }); continue; }
    if (/^\w+_shared = int\(lines\[pos\]\); pos \+= 1$/.test(l)) { out.push({ kind: "int", name: "shared" }); continue; }
    if ((m = /^(\w+) = int\(lines\[pos\]\); pos \+= 1$/.exec(l))) { out.push({ kind: "int", name: m[1] }); continue; }
    if ((m = /^(\w+) = lines\[pos\]; pos \+= 1$/.exec(l))) { out.push({ kind: "str", name: m[1] }); continue; }
    if ((m = /^(\w+) = lines\[pos:pos \+ \1_rows\]; pos \+= \1_rows$/.exec(l))) { out.push({ kind: "strs", name: m[1] }); continue; }
    if ((m = /^(\w+) = \[list\(map\(int, lines\[pos \+ i\]\.split\(\)\)\) for i in range\(\1_len\)\]; pos \+= \1_len$/.exec(l))) { out.push({ kind: "matrix", name: m[1] }); continue; }
    if ((m = /^(\w+) = build_tree\(lines\[pos\]\.split\(\) if \1_len > 0 else \[\]\); pos \+= 1$/.exec(l))) { out.push({ kind: "tree", name: m[1] }); continue; }
    if ((m = /^(\w+) = build_list\(list\(map\(int, lines\[pos\]\.split\(\)\)\) if \1_len > 0 else \[\]\); pos \+= 1$/.exec(l))) { out.push({ kind: "list", name: m[1] }); continue; }
    // Linked-list kinds: a list given as values plus a loop position, or two lists that share a tail.
    if ((m = /^(\w+)_vals = list\(map\(int, lines\[pos\]\.split\(\)\)\) if \1_len > 0 else \[\]; pos \+= 1$/.exec(l))) { out.push({ kind: "ints", name: m[1] }); continue; }
    if (/^\w+ = (build_cycle_list\(\w+_vals, \w+_loop\)|build_shared\(\w+_vals, \w+_vals, \w+_shared\)|_SECOND\[0\])$/.test(l)) continue; // builds nodes, reads no input
    // A decimal number such as x = 2.00000
    if ((m = /^(\w+) = float\(lines\[pos\]\); pos \+= 1$/.exec(l))) { out.push({ kind: "dbl", name: m[1] }); continue; }
    return null; // a statement this formatter does not know
  }
  return out.length ? out : null;
}

const words = (line: string | undefined) => (line ?? "").trim().split(/\s+/).filter(Boolean);
const arr = (items: string[]) => `[${items.join(",")}]`;
const NUM = /^-?\d+(\.\d+)?$/;
const literal = (t: string) => (NUM.test(t) || t === "null" || t === "true" || t === "false" ? t : JSON.stringify(t));

/** The arguments of an example as name/value pairs, e.g. [{name:"nums", value:"[2,7,11,15]"}, ...]; null if unrecognised. */
export function formatInputParts(python: string, input: string): { name: string; value: string }[] | null {
  const spec = parseInputSpec(python);
  if (!spec) return null;
  const lines = input.replace(/\r/g, "").split("\n");
  let pos = 0;
  let count = 0;
  const parts: { name: string; value: string }[] = [];
  for (const s of spec) {
    if (pos > lines.length) return null;
    if (s.kind === "count" || s.kind === "rowcount") {
      count = parseInt(words(lines[pos])[0] ?? "", 10);
      if (Number.isNaN(count)) return null;
      pos += 1;
      continue;
    }
    switch (s.kind) {
      case "ints": case "list": case "tree":
        parts.push({ name: s.name, value: arr(count > 0 ? words(lines[pos]).map(literal) : []) });
        pos += 1; break;
      case "int": case "dbl":
        if (!NUM.test((lines[pos] ?? "").trim())) return null;
        parts.push({ name: s.name, value: lines[pos].trim() }); pos += 1; break;
      case "str":
        if (lines[pos] === undefined) return null;
        parts.push({ name: s.name, value: JSON.stringify(lines[pos]) }); pos += 1; break;
      case "strs":
        parts.push({ name: s.name, value: arr(lines.slice(pos, pos + count).map((x) => JSON.stringify(x))) });
        pos += count; break;
      case "matrix":
        parts.push({ name: s.name, value: arr(Array.from({ length: count }, (_, i) => arr(words(lines[pos + i])))) });
        pos += count; break;
    }
  }
  return parts.length ? parts : null;
}

/** "nums = [2,7,11,15], target = 9" for the raw stdin text, or null if the layout is not recognised. */
export function formatInput(python: string, input: string): string | null {
  const parts = formatInputParts(python, input);
  return parts ? parts.map((p) => `${p.name} = ${p.value}`).join(", ") : null;
}

/** "[0,1]" / "true" / "[[1,6],[8,10]]" for the raw expected stdout, or null if the output layout is unknown. */
export function formatOutput(python: string, expected: string): string | null {
  const body = mainBody(python);
  if (!body) return null;
  const tail = body.slice(body.findIndex((l) => l.startsWith("result = solve(")) + 1).join("\n");
  const lines = expected.replace(/\r/g, "").split("\n");
  while (lines.length && lines[lines.length - 1].trim() === "") lines.pop();
  if (tail.includes("for row in result:") || tail.includes("for row in rows:")) return arr(lines.map((l) => arr(words(l).map(literal))));
  if (tail.includes("for s in sorted(result):")) return arr(lines.map((l) => JSON.stringify(l)));
  if (/" "\.join\(map\(str, (list_values\(result\)|result)\)\)|tree_tokens\(result\)/.test(tail)) return arr(words(lines.join(" ")).map(literal));
  if (tail.includes('"true" if result else "false"')) return lines.join("").trim();
  if (/^print\((node_index\(result\)|f"\{result:\.5f\}")\)$/.test(tail.trim())) return lines.join("").trim(); // a node's position, or a 5-decimal number
  if (/^print\(result\)$/.test(tail.trim())) {
    const v = lines.join("\n").trim();
    return NUM.test(v) || v === "true" || v === "false" || v === "null" ? v : JSON.stringify(v);
  }
  return null;
}

/** The inverse of formatInputParts: named LeetCode values back to the judge's stdin text; null when a value does not parse. */
export function buildInput(python: string, parts: { name: string; value: string }[]): string | null {
  const spec = parseInputSpec(python);
  if (!spec) return null;
  const byName = new Map(parts.map((p) => [p.name, p.value] as const));
  const parse = (name: string): unknown => {
    const raw = byName.get(name);
    if (raw === undefined) throw new Error("missing");
    return JSON.parse(raw.trim());
  };
  const cell = (v: unknown): string => (v === null ? "null" : String(v));
  try {
    const lines: string[] = [];
    for (let i = 0; i < spec.length; i++) {
      const s = spec[i];
      if (s.kind === "count" || s.kind === "rowcount") {
        const next = spec[i + 1];
        if (!next || !("name" in next)) return null;
        const v = parse(next.name);
        if (!Array.isArray(v)) return null;
        lines.push(String(v.length));
        continue;
      }
      const v = parse(s.name);
      switch (s.kind) {
        case "ints": case "list": case "tree":
          if (!Array.isArray(v)) return null;
          lines.push(v.map(cell).join(" ")); break;
        case "int":
          if (typeof v !== "number") return null;
          lines.push(String(v)); break;
        case "dbl":
          if (typeof v !== "number") return null;
          lines.push(v.toFixed(5)); break;
        case "str":
          if (typeof v !== "string") return null;
          lines.push(v); break;
        case "strs":
          if (!Array.isArray(v)) return null;
          for (const x of v) lines.push(String(x));
          break;
        case "matrix":
          if (!Array.isArray(v)) return null;
          for (const row of v) { if (!Array.isArray(row)) return null; lines.push(row.map(cell).join(" ")); }
          break;
      }
    }
    return lines.join("\n") + "\n";
  } catch {
    return null;
  }
}
