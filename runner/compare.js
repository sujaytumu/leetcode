// Answer comparison. Modes:
//   exact             deep equality (numbers compared with a small tolerance when non-integer)
//   unordered         top-level array compared as a multiset
//   unordered_nested  inner arrays and the outer array compared as multisets
function cmp(a, b) {
  if (typeof a === "number" && typeof b === "number") return a - b;
  const x = JSON.stringify(a);
  const y = JSON.stringify(b);
  return x < y ? -1 : x > y ? 1 : 0;
}

function canon(v, mode) {
  if (!Array.isArray(v)) return v;
  if (mode === "unordered") return [...v].sort(cmp);
  if (mode === "unordered_nested") return v.map((x) => (Array.isArray(x) ? [...x].sort(cmp) : x)).sort(cmp);
  return v;
}

function eq(a, b) {
  if (typeof a === "number" && typeof b === "number") {
    if (Number.isInteger(a) && Number.isInteger(b)) return a === b;
    return Math.abs(a - b) <= 1e-5 * Math.max(1, Math.abs(a), Math.abs(b));
  }
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((x, i) => eq(x, b[i]));
  return a === b;
}

function compare(expected, actual, mode = "exact") {
  return eq(canon(expected, mode), canon(actual, mode));
}

module.exports = { compare };
