export type DiffRow = { kind: "same" | "add" | "del"; text: string };

/** Line-level diff (longest common subsequence). Inputs are small (a submission vs the editor), so O(n*m) is fine. */
export function lineDiff(a: string, b: string): DiffRow[] {
  const x = a.replace(/\r\n/g, "\n").split("\n");
  const y = b.replace(/\r\n/g, "\n").split("\n");
  const n = x.length, m = y.length;
  const lcs: number[][] = Array.from({ length: n + 1 }, () => new Array<number>(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--)
    for (let j = m - 1; j >= 0; j--)
      lcs[i][j] = x[i] === y[j] ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
  const out: DiffRow[] = [];
  let i = 0, j = 0;
  while (i < n && j < m) {
    if (x[i] === y[j]) { out.push({ kind: "same", text: x[i] }); i++; j++; }
    else if (lcs[i + 1][j] >= lcs[i][j + 1]) out.push({ kind: "del", text: x[i++] });
    else out.push({ kind: "add", text: y[j++] });
  }
  while (i < n) out.push({ kind: "del", text: x[i++] });
  while (j < m) out.push({ kind: "add", text: y[j++] });
  return out;
}
