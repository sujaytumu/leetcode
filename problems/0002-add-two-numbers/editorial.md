## Approach: digit-by-digit simulation

Walk both lists together, summing the two digits plus the carry. Append `sum % 10` to the result and carry `sum / 10`. Continue while either list or the carry is non-zero.

A dummy head avoids special-casing the first node.

**Complexity:** O(max(m, n)) time, O(1) extra space beyond the output.
