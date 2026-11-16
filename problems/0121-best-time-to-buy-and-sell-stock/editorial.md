## Approach: single pass

Track the minimum price so far. The best profit selling today is `price - minSoFar`; keep the maximum of those.

**Complexity:** O(n) time, O(1) space.
