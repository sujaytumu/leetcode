"""Striver SDE sheet batch 8: LFU Cache and the queue / stack / heap implementations (as streams of commands, since every problem
reads stdin and prints stdout), the remaining trie problems, Maximum XOR, and Divide Two Integers.

Each expected output comes from a plain reference implementation; the optimal C++ answers are checked against it.
"""
from collections import deque
import heapq

INT_MIN, INT_MAX = -(2**31), 2**31 - 1


def make_batch(mk, rng):
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]
    word = lambda n, alpha: "".join(rng.choice(alpha) for _ in range(n))

    # ------------------------------------------------------------------ references
    def lfu(capacity, ops):
        """Evict the least frequently used key; on a tie the least recently used one. Plain scan, easy to trust."""
        store, out, clock = {}, [], 0          # key -> [value, frequency, last-used time]
        for line in ops:
            clock += 1
            parts = line.split()
            k = int(parts[1])
            if parts[0] == "get":
                if k in store:
                    store[k][1] += 1
                    store[k][2] = clock
                    out.append(store[k][0])
                else:
                    out.append(-1)
            else:
                v = int(parts[2])
                if k in store:
                    store[k] = [v, store[k][1] + 1, clock]
                else:
                    if len(store) == capacity:
                        victim = min(store, key=lambda key: (store[key][1], store[key][2]))
                        del store[victim]
                    store[k] = [v, 1, clock]
        return out

    def queue_with_stacks(ops):
        q, out = deque(), []
        for line in ops:
            parts = line.split()
            if parts[0] == "push":
                q.append(int(parts[1]))
            elif parts[0] == "pop":
                out.append(q.popleft())
            elif parts[0] == "peek":
                out.append(q[0])
            else:
                out.append(0 if q else 1)
        return out

    def stack_with_queues(ops):
        st, out = [], []
        for line in ops:
            parts = line.split()
            if parts[0] == "push":
                st.append(int(parts[1]))
            elif parts[0] == "pop":
                out.append(st.pop())
            elif parts[0] == "top":
                out.append(st[-1])
            else:
                out.append(0 if st else 1)
        return out

    def min_heap(ops):
        h, out = [], []
        for line in ops:
            parts = line.split()
            if parts[0] == "push":
                heapq.heappush(h, int(parts[1]))
            elif parts[0] == "pop":
                out.append(heapq.heappop(h))
            elif parts[0] == "peek":
                out.append(h[0])
            else:
                out.append(len(h))
        return out

    def longest_word(words):
        have = set(words)
        good = [w for w in have if all(w[:i] in have for i in range(1, len(w)))]
        if not good:
            return "None"
        return min(good, key=lambda w: (-len(w), w))

    def max_xor(nums):
        best = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                best = max(best, nums[i] ^ nums[j])
        return best

    def distinct_substrings(s):
        return len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})

    def divide(a, b):
        q = abs(a) // abs(b)
        if (a < 0) != (b < 0):
            q = -q
        return max(INT_MIN, min(INT_MAX, q))

    # ------------------------------------------------------------------ cases
    def op_stream(n, kinds, valid, value=lambda: rng.randint(-1000, 1000)):
        """Random valid command stream; `valid(kind, size)` says whether a command may run now. Size is tracked by the caller via kinds."""
        ops, size = [], 0
        for _ in range(n):
            while True:
                kind = rng.choice(kinds)
                if valid(kind, size):
                    break
            if kind == "push":
                ops.append(f"push {value()}"); size += 1
            else:
                ops.append(kind)
                if kind == "pop":
                    size -= 1
        return ops

    def finish(ops, size_after, observers):
        """Make sure at least one command produces output."""
        if not any(o.split()[0] in observers for o in ops):
            ops.append(observers[-1])
        return ops

    def stream_cases(kinds, observers, examples):
        cases = list(examples)
        for n in (8, 20, 40, 80, 150, 250):
            ops = op_stream(n, kinds, lambda k, size: size > 0 or k in ("push", "empty", "size"))
            cases.append(finish(ops, 0, observers))
        return cases

    def c_lfu():
        cases = [(2, ["put 1 1", "put 2 2", "get 1", "put 3 3", "get 2", "get 3", "put 4 4", "get 1", "get 3", "get 4"]),
                 (1, ["put 1 1", "get 1", "put 2 2", "get 1", "get 2"]),
                 (2, ["put 1 1", "put 2 2", "put 1 10", "put 3 3", "get 1", "get 2", "get 3"]),
                 (3, ["put 1 1", "put 2 2", "put 3 3", "get 1", "get 1", "get 2", "put 4 4", "get 3", "get 4", "get 2", "get 1"])]
        for cap, n, keys in ((2, 20, 4), (3, 40, 6), (5, 80, 10), (10, 150, 25), (20, 250, 40), (50, 300, 120)):
            ops = [f"put {rng.randint(1, keys)} {rng.randint(0, 1000)}" if rng.random() < 0.45 else f"get {rng.randint(1, keys)}" for _ in range(n)]
            ops[-1] = f"get {rng.randint(1, keys)}"
            cases.append((cap, ops))
        return cases

    def c_queue():
        return stream_cases(["push", "push", "pop", "peek", "empty"], ("pop", "peek", "empty"),
                            [["push 1", "push 2", "peek", "pop", "empty"], ["empty"], ["push 7", "pop", "empty"], ["push 3", "push 4", "pop", "push 5", "pop", "pop", "empty"]])

    def c_stack():
        return stream_cases(["push", "push", "pop", "top", "empty"], ("pop", "top", "empty"),
                            [["push 1", "push 2", "top", "pop", "empty"], ["empty"], ["push 7", "pop", "empty"], ["push 3", "push 4", "pop", "push 5", "pop", "pop", "empty"]])

    def c_heap():
        return stream_cases(["push", "push", "push", "pop", "peek", "size"], ("pop", "peek", "size"),
                            [["push 5", "push 2", "push 8", "peek", "pop", "pop", "size"], ["size"], ["push 1", "push 1", "pop", "pop", "size"], ["push -3", "push 0", "peek", "push -9", "pop", "peek"]])

    def c_longest_word():
        cases = [["k", "ki", "kir", "kira", "kiran"], ["a", "banana", "app", "appl", "ap", "apply", "apple"], ["abc", "bc", "ab", "bd"], ["x"], ["ab", "abc"],
                 ["w", "wo", "wor", "worl", "world", "wa", "wal", "walk"], ["b", "ba", "bat", "c", "ca", "cat"]]
        for n, wl, alpha in ((10, 4, "ab"), (30, 5, "abc"), (80, 6, "ab"), (150, 8, "abc"), (200, 10, "ab")):
            words = {word(rng.randint(1, wl), alpha) for _ in range(n)}
            # grow a chain of prefixes so a non-trivial answer exists
            seed = word(wl, alpha)
            words |= {seed[:i] for i in range(1, wl + 1)}
            words = list(words)
            rng.shuffle(words)
            cases.append(words[:200])
        return cases

    def c_max_xor():
        cases = [[3, 10, 5, 25, 2, 8], [14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70], [0, 0], [1, 2], [8, 8, 8], [5, 25], [2, 4, 8, 16, 32]]
        for n, hi in ((10, 20), (30, 1000), (100, 100000), (300, 10**6), (800, 2**30 - 1), (1500, 2**30 - 1)):
            cases.append(arr(n, 0, hi))
        return cases

    def c_distinct():
        cases = ["abc", "aaa", "abab", "a", "ab", "abcabc", "banana", "mississippi"]
        for n, alpha in ((10, "ab"), (30, "abc"), (60, "abcd"), (120, "ab"), (200, "abc"), (300, "abcde")):
            cases.append(word(n, alpha))
        return cases

    def c_divide():
        cases = [(10, 3), (7, -3), (-7, 3), (-7, -3), (0, 5), (1, 1), (1, -1), (5, 7), (-5, 7), (INT_MIN, -1), (INT_MIN, 1), (INT_MAX, 1), (INT_MAX, 2),
                 (INT_MIN, 2), (INT_MIN, -2), (INT_MAX, -1), (INT_MIN, INT_MAX), (2**30, 3), (-2**30, 7), (100, 100), (99, 100)]
        for _ in range(10):
            cases.append((rng.randint(INT_MIN, INT_MAX), rng.choice([-1, 1]) * rng.randint(1, 10**rng.randint(1, 9))))
        return cases

    CMD = "Line 1: `m`, the number of commands.\nThen `m` lines, each one command."
    return [
        mk("lfu-cache", "LFU Cache", "HARD", ["stack", "design", "hash-table"], [("capacity", "int"), ("ops", "strs")], "int[]", lfu, c_lfu(),
           "Simulate a Least Frequently Used cache with the given `capacity`. `put k v` stores or updates a key, `get k` returns its value or `-1`. "
           "Every `put` and every successful `get` of a key raises that key's use count by one (a new key starts at 1). When a new key arrives and the "
           "cache is full, first remove the key with the **smallest use count**; if several tie, remove the **least recently used** among them. "
           "Return the result of every `get`, in order.",
           "Line 1: `capacity`.\nLine 2: `m`, the number of commands.\nThen `m` lines, each `put k v` or `get k`.",
           "The results of the `get` commands as space-separated integers.",
           ["`1 <= capacity <= 50`", "`1 <= m <= 300`", "`1 <= k <= 120`, `0 <= v <= 1000`", "At least one `get`"]),
        mk("implement-queue-using-stacks", "Implement Queue using Stacks", "EASY", ["stack", "design"], [("ops", "strs")], "int[]", queue_with_stacks, c_queue(),
           "Build a first-in-first-out queue using only stacks. Run the commands `push x`, `pop` (remove and report the front), `peek` (report the front) "
           "and `empty` (report `1` if the queue is empty, else `0`). Return the results of all `pop`, `peek` and `empty` commands, in order.",
           CMD, "The results as space-separated integers.", ["`1 <= m <= 250`", "`-1000 <= x <= 1000`", "`pop` and `peek` only run on a non-empty queue", "At least one `pop`, `peek` or `empty`"]),
        mk("implement-stack-using-queues", "Implement Stack using Queues", "EASY", ["stack", "design"], [("ops", "strs")], "int[]", stack_with_queues, c_stack(),
           "Build a last-in-first-out stack using only queues. Run the commands `push x`, `pop` (remove and report the top), `top` (report the top) "
           "and `empty` (report `1` if the stack is empty, else `0`). Return the results of all `pop`, `top` and `empty` commands, in order.",
           CMD, "The results as space-separated integers.", ["`1 <= m <= 250`", "`-1000 <= x <= 1000`", "`pop` and `top` only run on a non-empty stack", "At least one `pop`, `top` or `empty`"]),
        mk("implement-min-heap", "Implement Min Heap", "MEDIUM", ["heap", "design"], [("ops", "strs")], "int[]", min_heap, c_heap(),
           "Build a min-heap (priority queue) and run the commands `push x`, `pop` (remove and report the smallest), `peek` (report the smallest) and "
           "`size` (report how many values are stored). Return the results of all `pop`, `peek` and `size` commands, in order.",
           CMD, "The results as space-separated integers.", ["`1 <= m <= 250`", "`-1000 <= x <= 1000`", "`pop` and `peek` only run on a non-empty heap", "At least one `pop`, `peek` or `size`"]),
        mk("longest-word-with-all-prefixes", "Longest Word With All Prefixes", "MEDIUM", ["string", "trie"], [("words", "strs")], "str", longest_word, c_longest_word(),
           "Find the longest word in `words` such that **every prefix** of it (of length 1 up to its length) is also in `words`. If several words have "
           "that length, return the lexicographically smallest. If no word qualifies, return `None`.",
           "Line 1: `n`, then `n` lines, one word each.", "The word, or `None`.", ["`1 <= n <= 200`", "`1 <= length <= 10`", "Lowercase English letters"]),
        mk("maximum-xor-of-two-numbers-in-an-array", "Maximum XOR of Two Numbers in an Array", "MEDIUM", ["array", "trie", "bit-manipulation"], [("nums", "int[]")], "int", max_xor, c_max_xor(),
           "Return the largest value of `nums[i] XOR nums[j]` over all pairs with `i != j`.",
           "Line 1: `n`.\nLine 2: `n` space-separated integers.", "The maximum XOR.", ["`2 <= n <= 1500`", "`0 <= nums[i] < 2^30`"]),
        mk("count-distinct-substrings", "Count Distinct Substrings", "MEDIUM", ["string", "trie"], [("s", "str")], "int", distinct_substrings, c_distinct(),
           "Return the number of different non-empty substrings of `s` (equal substrings at different positions count once).",
           "A line with the string `s`.", "The number of distinct substrings.", ["`1 <= s.length <= 300`", "Lowercase English letters"]),
        mk("divide-two-integers", "Divide Two Integers", "MEDIUM", ["math", "bit-manipulation"], [("dividend", "int"), ("divisor", "int")], "int", divide, c_divide(),
           "Divide `dividend` by `divisor` without using multiplication, division or the modulo operator. The result is truncated toward zero. "
           "If it falls outside the 32-bit signed range, return the nearest bound: `2147483647` or `-2147483648`.",
           "Line 1: `dividend`.\nLine 2: `divisor`.", "The truncated quotient, clamped to 32 bits.", ["`-2^31 <= dividend, divisor <= 2^31 - 1`", "`divisor != 0`"]),
    ]
