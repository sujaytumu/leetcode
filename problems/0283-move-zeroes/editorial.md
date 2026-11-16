## Approach: two pointers

Keep `w`, the next write position. For every non-zero element, copy it to `nums[w++]`. After the scan, set the remaining positions to zero. This performs the fewest writes while preserving order.

**Complexity:** O(n) time, O(1) space.
