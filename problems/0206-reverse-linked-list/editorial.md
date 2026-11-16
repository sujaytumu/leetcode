## Approach: iterative pointer reversal

Walk the list with `prev` (initially null) and `cur`. For each node save `next`, point `cur.next` at `prev`, then advance both.

**Complexity:** O(n) time, O(1) space.
