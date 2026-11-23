## Approach: Kadane's algorithm

Keep `cur`, the best sum of a subarray ending at the current element: `cur = max(x, cur + x)`. Track the maximum `cur` seen.

If the running sum becomes worse than starting fresh at `x`, restarting is always better.

**Complexity:** O(n) time, O(1) space.
