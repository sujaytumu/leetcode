## Approach: Fibonacci recurrence

`ways(n) = ways(n-1) + ways(n-2)` with `ways(1) = 1`, `ways(2) = 2`. Only the previous two values are needed, so keep two variables.

**Complexity:** O(n) time, O(1) space.
