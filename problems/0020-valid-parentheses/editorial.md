## Approach: stack

Push every opening bracket. On a closing bracket, the stack must be non-empty and its top must be the matching opener; pop it. At the end the stack must be empty.

**Complexity:** O(n) time, O(n) space.
