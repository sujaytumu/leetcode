## Approach: recursion (or BFS)

`depth(node) = 0` for null, otherwise `1 + max(depth(left), depth(right))`.

For very deep, skewed trees an iterative level-order traversal avoids recursion limits.

**Complexity:** O(n) time, O(h) space for the recursion stack.
