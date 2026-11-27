"""Striver SDE sheet batch 7: Sudoku and Combination Sum (recursion), more DP, running median (heap), a trie, and the two
classic design problems (LRU Cache, Min Stack) expressed as a stream of commands, because every problem reads stdin and prints stdout.

Each expected output comes from a plain reference implementation; the optimal C++ answers are checked against it.
"""
import heapq
from collections import OrderedDict


def make_batch(mk, rng):
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]
    word = lambda n, alpha: "".join(rng.choice(alpha) for _ in range(n))
    INT_MAX = 2**31 - 1

    # ------------------------------------------------------------------ references
    def combination_sum(candidates, target):
        cs, out = sorted(candidates), []

        def go(i, left, cur):
            if left == 0:
                out.append(list(cur))
                return
            for j in range(i, len(cs)):
                if cs[j] > left:
                    break
                cur.append(cs[j])
                go(j, left - cs[j], cur)
                cur.pop()
        go(0, target, [])
        return out

    # ---- sudoku
    def sudoku_solutions(board, limit):
        """Counts solutions (up to `limit`) and returns (count, first solution)."""
        g = [row[:] for row in board]
        rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
        for r in range(9):
            for c in range(9):
                if g[r][c]:
                    b = 1 << g[r][c]
                    rows[r] |= b; cols[c] |= b; boxes[r // 3 * 3 + c // 3] |= b
        found, first = [0], [None]

        def go():
            best, cells = None, 10
            for r in range(9):
                for c in range(9):
                    if g[r][c] == 0:
                        used = rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]
                        free = [d for d in range(1, 10) if not used >> d & 1]
                        if len(free) < cells:
                            best, cells = (r, c, free), len(free)
                            if cells == 0:
                                return
            if best is None:
                found[0] += 1
                if first[0] is None:
                    first[0] = [row[:] for row in g]
                return
            r, c, free = best
            for d in free:
                b = 1 << d
                g[r][c] = d; rows[r] |= b; cols[c] |= b; boxes[r // 3 * 3 + c // 3] |= b
                go()
                g[r][c] = 0; rows[r] ^= b; cols[c] ^= b; boxes[r // 3 * 3 + c // 3] ^= b
                if found[0] >= limit:
                    return
        go()
        return found[0], first[0]

    def sudoku_solve(board):
        count, sol = sudoku_solutions(board, 2)
        assert count == 1, "sudoku case must have exactly one solution"
        return sol

    def make_sudoku(clues):
        empty = [[0] * 9 for _ in range(9)]
        # random full grid: fill with a shuffled-digit solver
        full = [row[:] for row in empty]
        digits = list(range(1, 10))

        def fill(pos):
            if pos == 81:
                return True
            r, c = divmod(pos, 9)
            rng.shuffle(digits)
            for d in list(digits):
                if all(full[r][k] != d for k in range(9)) and all(full[k][c] != d for k in range(9)) and \
                   all(full[r // 3 * 3 + i][c // 3 * 3 + j] != d for i in range(3) for j in range(3)):
                    full[r][c] = d
                    if fill(pos + 1):
                        return True
                    full[r][c] = 0
            return False
        fill(0)
        puzzle, cells = [row[:] for row in full], [(r, c) for r in range(9) for c in range(9)]
        rng.shuffle(cells)
        left = 81
        for r, c in cells:
            if left <= clues:
                break
            keep = puzzle[r][c]
            puzzle[r][c] = 0
            if sudoku_solutions(puzzle, 2)[0] != 1:
                puzzle[r][c] = keep
            else:
                left -= 1
        return puzzle

    # ---- dp
    def bitonic(nums):
        n = len(nums)
        inc, dec = [1] * n, [1] * n
        for i in range(n):
            for j in range(i):
                if nums[j] < nums[i]:
                    inc[i] = max(inc[i], inc[j] + 1)
        for i in range(n - 1, -1, -1):
            for j in range(n - 1, i, -1):
                if nums[j] < nums[i]:
                    dec[i] = max(dec[i], dec[j] + 1)
        return max(inc[i] + dec[i] - 1 for i in range(n))

    def count_lis(nums):
        n = len(nums)
        length, ways = [1] * n, [1] * n
        for i in range(n):
            for j in range(i):
                if nums[j] < nums[i]:
                    if length[j] + 1 > length[i]:
                        length[i], ways[i] = length[j] + 1, ways[j]
                    elif length[j] + 1 == length[i]:
                        ways[i] += ways[j]
        top = max(length)
        return sum(w for l, w in zip(length, ways) if l == top)

    def min_insertions(s):
        n = len(s)
        dp = [[0] * n for _ in range(n)]       # dp[i][j] = insertions to make s[i..j] a palindrome
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                dp[i][j] = dp[i + 1][j - 1] if s[i] == s[j] else 1 + min(dp[i + 1][j], dp[i][j - 1])
        return dp[0][n - 1]

    # ---- heap / trie / design
    def running_median(nums):
        low, high, out = [], [], []          # low = max-heap (negated), high = min-heap
        for x in nums:
            heapq.heappush(low, -x)
            heapq.heappush(high, -heapq.heappop(low))
            if len(high) > len(low):
                heapq.heappush(low, -heapq.heappop(high))
            out.append(-low[0] if len(low) > len(high) else (-low[0] + high[0]) // 2)
        return out

    def trie_counts(words, queries):
        root = {}
        for w in words:
            node = root
            for ch in w:
                node = node.setdefault(ch, {"#": 0})
                node["#"] += 1
        out = []
        for q in queries:
            node = root
            for ch in q:
                node = node.get(ch)
                if node is None:
                    break
            out.append(0 if node is None else node["#"])
        return out

    def lru(capacity, ops):
        cache, out = OrderedDict(), []
        for line in ops:
            parts = line.split()
            if parts[0] == "put":
                k, v = int(parts[1]), int(parts[2])
                if k in cache:
                    cache.move_to_end(k)
                cache[k] = v
                if len(cache) > capacity:
                    cache.popitem(last=False)
            else:
                k = int(parts[1])
                if k in cache:
                    cache.move_to_end(k)
                    out.append(cache[k])
                else:
                    out.append(-1)
        return out

    def min_stack(ops):
        stack, out = [], []
        for line in ops:
            parts = line.split()
            if parts[0] == "push":
                stack.append(int(parts[1]))
            elif parts[0] == "pop":
                stack.pop()
            elif parts[0] == "top":
                out.append(stack[-1])
            else:
                out.append(min(stack))
        return out

    # ------------------------------------------------------------------ cases
    def c_combination():
        cases = [([2, 3, 6, 7], 7), ([2, 3, 5], 8), ([2], 1), ([1], 3), ([7, 3, 2], 18), ([4, 2, 8], 8), ([3, 5, 7], 15)]
        for n, hi, target in ((3, 9, 20), (4, 12, 24), (5, 15, 30), (4, 8, 30), (6, 20, 40), (5, 10, 38)):
            while True:
                cs = rng.sample(range(2, hi + 1), n)
                if len(combination_sum(cs, target)) <= 150:
                    break
            cases.append((cs, target))
        return cases

    def c_sudoku():
        # the well-known LeetCode example first (digits, 0 = empty)
        rows = ["530070000", "600195000", "098000060", "800060003", "400803001", "700020006", "060000280", "000419005", "000080079"]
        cases = [[[int(ch) for ch in r] for r in rows]]
        for clues in (45, 40, 36, 32, 30, 28, 26, 24, 23):
            cases.append(make_sudoku(clues))
        return cases

    def c_bitonic():
        cases = [[1, 11, 2, 10, 4, 5, 2, 1], [12, 11, 40, 5, 3, 1], [80, 60, 30, 40, 20, 10], [1], [5, 5, 5], [1, 2, 3, 4], [4, 3, 2, 1], [1, 3, 2]]
        for n, hi in ((10, 20), (25, 50), (60, 100), (150, 300), (300, 1000), (500, 1000)):
            cases.append(arr(n, 1, hi))
        return cases

    def c_count_lis():
        cases = [[1, 3, 5, 4, 7], [2, 2, 2, 2, 2], [1], [1, 2, 4, 3, 5, 4, 7, 2], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [3, 1, 2]]
        for n, hi in ((10, 5), (20, 10), (40, 15), (80, 30), (150, 60), (300, 200)):
            while True:
                a = arr(n, 1, hi)
                if count_lis(a) <= INT_MAX:
                    break
            cases.append(a)
        return cases

    def c_insertions():
        cases = ["zzazz", "mbadm", "leetcode", "a", "ab", "abcd", "aaaa", "abcba"]
        for n, alpha in ((12, "ab"), (30, "abc"), (80, "abcd"), (150, "ab"), (300, "abcde"), (500, "abc")):
            cases.append(word(n, alpha))
        return cases

    def c_median():
        cases = [[2, 3, 4], [1, 2], [5], [5, 15, 1, 3], [7, 7, 7, 7], [1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1], [10, 0, 10, 0]]
        for n, hi in ((10, 20), (25, 100), (60, 1000), (150, 10000), (400, 100000), (1000, 100000)):
            cases.append(arr(n, 0, hi))
        return cases

    def c_trie():
        cases = [(["apple", "app", "apt", "bat"], ["app", "ap", "b", "c", "apple", "applee"]),
                 (["a"], ["a", "b", "aa"]), (["cat", "cat", "car"], ["ca", "cat", "car", "c"]), (["abc", "abd", "ab"], ["ab", "abc", "abd", "a", "abe"])]
        for n, m, wl, alpha in ((10, 8, 5, "ab"), (30, 15, 6, "abc"), (80, 30, 8, "abcd"), (150, 60, 10, "ab"), (200, 100, 10, "abc")):
            words = [word(rng.randint(1, wl), alpha) for _ in range(n)]
            queries = [word(rng.randint(1, wl), alpha) for _ in range(m // 2)] + [w[:rng.randint(1, len(w))] for w in rng.sample(words, m - m // 2)]
            rng.shuffle(queries)
            cases.append((words, queries))
        return cases

    def c_lru():
        cases = [(2, ["put 1 1", "put 2 2", "get 1", "put 3 3", "get 2", "put 4 4", "get 1", "get 3", "get 4"]),
                 (1, ["put 2 1", "get 2", "put 3 2", "get 2", "get 3"]),
                 (2, ["put 2 1", "put 2 2", "get 2", "put 1 1", "put 4 1", "get 2"]),
                 (3, ["put 1 10", "put 2 20", "put 3 30", "get 1", "put 4 40", "get 2", "get 3", "get 4", "get 1"])]
        for cap, n, keys in ((2, 20, 4), (3, 40, 6), (5, 80, 10), (10, 150, 25), (20, 250, 40), (50, 300, 120)):
            ops = [f"put {rng.randint(1, keys)} {rng.randint(0, 1000)}" if rng.random() < 0.45 else f"get {rng.randint(1, keys)}" for _ in range(n)]
            ops[-1] = f"get {rng.randint(1, keys)}"
            cases.append((cap, ops))
        return cases

    def c_min_stack():
        cases = [(["push -2", "push 0", "push -3", "getMin", "pop", "top", "getMin"],), (["push 5", "top", "getMin"],),
                 (["push 2", "push 2", "push 1", "getMin", "pop", "getMin", "pop", "getMin"],)]
        cases = [c[0] for c in cases]
        for n in (12, 30, 60, 120, 200, 300):
            ops, size = [], 0
            for _ in range(n):
                roll = rng.random()
                if size == 0 or roll < 0.4:
                    ops.append(f"push {rng.randint(-1000, 1000)}"); size += 1
                elif roll < 0.6:
                    ops.append("pop"); size -= 1
                elif roll < 0.8:
                    ops.append("top")
                else:
                    ops.append("getMin")
            if size == 0:
                ops.append("push 0")
            if not any(o in ("top", "getMin") for o in ops):
                ops.append("getMin")
            cases.append(ops)
        return cases

    return [
        mk("combination-sum", "Combination Sum", "MEDIUM", ["array", "backtracking"], [("candidates", "int[]"), ("target", "int")], "sets", combination_sum, c_combination(),
           "Given distinct positive integers `candidates` and a `target`, return every unique combination of candidates that adds up to `target`. "
           "The same number may be used any number of times; two combinations are different if the count of some number differs.",
           "Line 1: `n`.\nLine 2: the `n` candidates.\nLine 3: `target`.",
           "One combination per line, numbers ascending, lines sorted. The starter code prints the rows for you; an empty output means there is none.",
           ["`1 <= n <= 6`", "`2 <= candidates[i] <= 20`, all distinct", "`1 <= target <= 40`", "At most 150 combinations"]),
        mk("sudoku-solver", "Sudoku Solver", "HARD", ["matrix", "backtracking"], [("board", "int[][]")], "int[][]", sudoku_solve, c_sudoku(),
           "Fill the empty cells (`0`) of a 9 x 9 Sudoku so that every row, every column and every 3 x 3 box contains the digits 1 to 9 exactly once. "
           "Return the solved board.",
           "Line 1: `9`.\nLines 2 to 10: each row as 9 space-separated digits, `0` for an empty cell.",
           "The solved board: 9 lines of 9 space-separated digits.", ["The board is a valid Sudoku", "There is exactly one solution"]),
        mk("longest-bitonic-subsequence", "Longest Bitonic Subsequence", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]")], "int", bitonic, c_bitonic(),
           "A subsequence is **bitonic** if it first strictly increases and then strictly decreases (either part may be a single element, so a purely "
           "increasing or purely decreasing subsequence also counts). Return the length of the longest bitonic subsequence of `nums`.",
           "Line 1: `n`.\nLine 2: `n` space-separated integers.", "The length of the longest bitonic subsequence.", ["`1 <= n <= 500`", "`1 <= nums[i] <= 1000`"]),
        mk("number-of-longest-increasing-subsequences", "Number of Longest Increasing Subsequences", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]")], "int", count_lis, c_count_lis(),
           "Return how many strictly increasing subsequences of `nums` have the maximum possible length. Subsequences are counted by the positions they use.",
           "Line 1: `n`.\nLine 2: `n` space-separated integers.", "The number of longest increasing subsequences.",
           ["`1 <= n <= 300`", "`1 <= nums[i] <= 200`", "The answer fits in a 32-bit integer"]),
        mk("minimum-insertion-steps-to-make-a-string-palindrome", "Minimum Insertion Steps to Make a String Palindrome", "HARD", ["string", "dynamic-programming"], [("s", "str")], "int", min_insertions, c_insertions(),
           "In one step you may insert any character at any position of `s`. Return the minimum number of insertions that make `s` a palindrome.",
           "A line with the string `s`.", "The minimum number of insertions.", ["`1 <= s.length <= 500`", "Lowercase English letters"]),
        mk("find-median-from-data-stream", "Find Median from Data Stream", "HARD", ["heap", "design"], [("nums", "int[]")], "int[]", running_median, c_median(),
           "Numbers arrive one at a time. After each arrival, report the median of all numbers seen so far. When the count is even, the median is the "
           "average of the two middle values **rounded down**.",
           "Line 1: `n`.\nLine 2: the `n` numbers in arrival order.", "`n` space-separated medians, one per arrival.",
           ["`1 <= n <= 1000`", "`0 <= nums[i] <= 100000`"]),
        mk("implement-trie-prefix-count", "Implement Trie (Prefix Count)", "MEDIUM", ["string", "trie"], [("words", "strs"), ("queries", "strs")], "int[]", trie_counts, c_trie(),
           "Insert all `words` into a trie (a word may appear several times and counts every time). For each query, return how many inserted words start "
           "with that query as a prefix (a word is a prefix of itself).",
           "Line 1: `n`, then `n` lines, one word each.\nThen `m`, then `m` lines, one query each.", "`m` space-separated counts, one per query.",
           ["`1 <= n <= 200`, `1 <= m <= 100`", "`1 <= length <= 10`", "Lowercase English letters"]),
        mk("lru-cache", "LRU Cache", "MEDIUM", ["stack", "design", "hash-table"], [("capacity", "int"), ("ops", "strs")], "int[]", lru, c_lru(),
           "Simulate a Least Recently Used cache with the given `capacity` by running the commands in order. `put k v` stores or updates a key (and makes "
           "it the most recently used); if the cache then holds more than `capacity` keys, the least recently used key is removed. `get k` returns its value "
           "(or `-1` if absent) and makes it the most recently used. Return the result of every `get`, in order.",
           "Line 1: `capacity`.\nLine 2: `m`, the number of commands.\nThen `m` lines, each `put k v` or `get k`.",
           "The results of the `get` commands as space-separated integers.",
           ["`1 <= capacity <= 50`", "`1 <= m <= 300`", "`1 <= k <= 120`, `0 <= v <= 1000`", "At least one `get`"]),
        mk("min-stack", "Min Stack", "MEDIUM", ["stack", "design"], [("ops", "strs")], "int[]", min_stack, c_min_stack(),
           "Run a stack with these commands: `push x`, `pop`, `top` (report the top element) and `getMin` (report the smallest element in the stack). "
           "Every command must take constant time. Return the results of all `top` and `getMin` commands, in order.",
           "Line 1: `m`, the number of commands.\nThen `m` lines, each one command.", "The results as space-separated integers.",
           ["`1 <= m <= 300`", "`-1000 <= x <= 1000`", "`pop`, `top` and `getMin` are only called on a non-empty stack", "At least one `top` or `getMin`"]),
    ]
