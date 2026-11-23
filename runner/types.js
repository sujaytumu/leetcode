// Type model shared by every language generator.
// A type string is a base type followed by any number of "[]" suffixes, e.g. "int[][]".
const BASES = ["int", "long", "double", "bool", "string", "char", "ListNode", "TreeNode"];

function parseType(t) {
  let dims = 0;
  while (t.endsWith("[]")) {
    dims++;
    t = t.slice(0, -2);
  }
  if (!BASES.includes(t)) throw new Error(`Unsupported type: ${t}`);
  return { base: t, dims };
}

function usedBases(sig) {
  const types = sig.params.map((p) => p.type);
  if (sig.returns !== "void") types.push(sig.returns);
  return new Set(types.map((t) => parseType(t).base));
}

// Index of the parameter that holds the answer for in-place problems.
function mutatedParam(sig) {
  if (sig.returns !== "void") return null;
  const p = sig.params.find((x) => x.name === sig.mutates);
  if (!p) throw new Error(`void signature "${sig.name}" needs a valid "mutates" parameter`);
  return p;
}

module.exports = { BASES, parseType, usedBases, mutatedParam };
