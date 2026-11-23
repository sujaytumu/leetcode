## Approach: flood fill

Scan every cell. On unvisited land, increment the answer and sink the whole island (mark visited) with an explicit stack, which avoids recursion-depth problems on a 300×300 all-land grid.

**Complexity:** O(m·n) time, O(m·n) space worst case.
