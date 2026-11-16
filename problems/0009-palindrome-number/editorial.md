## Approach: reverse half the digits

Negative numbers and numbers ending in 0 (other than 0) cannot be palindromes. Otherwise peel digits off the end into `rev` until `rev >= x`; now `rev` holds the reversed second half. The number is a palindrome if `x == rev` (even length) or `x == rev / 10` (odd length).

Half-reversing also sidesteps integer overflow.

**Complexity:** O(log₁₀ n) time, O(1) space.
