## Approach: one pass with a hash map

Brute force tries all pairs: O(n²) time. We can do better by remembering what we have already seen.

While scanning, for each `x = nums[i]` the partner we need is `target - x`. If that value is already in the map, we are done. Otherwise store `x -> i` and move on.

Storing *after* the lookup guarantees we never pair an element with itself.

**Complexity:** O(n) time, O(n) space.

**Pitfall:** `target - x` can overflow a 32-bit int in C++/Java when values reach ±10⁹, so the solutions widen to 64-bit first.
