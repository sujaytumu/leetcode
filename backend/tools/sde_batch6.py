"""Striver SDE sheet batch 6: the classic dynamic-programming problems the sheet still lacked.

Each expected output comes from a plain reference implementation; the optimal C++ answers are checked against it.
"""
from bisect import bisect_right


def make_batch(mk, rng):
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]
    word = lambda n, alpha: "".join(rng.choice(alpha) for _ in range(n))

    # ------------------------------------------------------------------ references
    def knapsack(weights, values, cap):
        best = [0] * (cap + 1)
        for w, v in zip(weights, values):
            for c in range(cap, w - 1, -1):
                best[c] = max(best[c], best[c - w] + v)
        return best[cap]

    def rod_cutting(prices):
        n = len(prices)
        best = [0] * (n + 1)
        for j in range(1, n + 1):
            best[j] = max(prices[i - 1] + best[j - i] for i in range(1, j + 1))
        return best[n]

    def chain(dims):
        m = len(dims) - 1
        cost = [[0] * m for _ in range(m)]
        for length in range(2, m + 1):
            for i in range(m - length + 1):
                j = i + length - 1
                cost[i][j] = min(cost[i][k] + cost[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1] for k in range(i, j))
        return cost[0][m - 1]

    def min_cuts(s):
        n = len(s)
        pal = [[False] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])
        cuts = [0] * n
        for j in range(n):
            cuts[j] = 0 if pal[0][j] else min(cuts[i - 1] + 1 for i in range(1, j + 1) if pal[i][j])
        return cuts[n - 1]

    def lps(s):
        n = len(s)
        dp = [[0] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            dp[i][i] = 1
            for j in range(i + 1, n):
                dp[i][j] = dp[i + 1][j - 1] + 2 if s[i] == s[j] else max(dp[i + 1][j], dp[i][j - 1])
        return dp[0][n - 1]

    def eggs_classic(eggs, floors):
        """Textbook O(eggs * floors^2) table, used for small inputs and as the reference."""
        dp = [[0] * (floors + 1) for _ in range(eggs + 1)]
        for f in range(1, floors + 1):
            dp[1][f] = f
        for e in range(2, eggs + 1):
            for f in range(1, floors + 1):
                dp[e][f] = 1 + min(max(dp[e - 1][x - 1], dp[e][f - x]) for x in range(1, f + 1))
        return dp[eggs][floors]

    def egg_drop(eggs, floors):
        """Fewest moves m such that `eggs` eggs can distinguish `floors` floors."""
        reach, moves = [0] * (eggs + 1), 0
        while reach[eggs] < floors:
            moves += 1
            for e in range(eggs, 0, -1):
                reach[e] = reach[e] + reach[e - 1] + 1
        return moves

    def job_scheduling(start, end, profit):
        jobs = sorted(zip(end, start, profit))
        ends = [j[0] for j in jobs]
        best = [0] * (len(jobs) + 1)
        for i, (e, s, p) in enumerate(jobs):
            k = bisect_right(ends, s, 0, i)  # jobs that finish at or before this one starts
            best[i + 1] = max(best[i], best[k] + p)
        return best[-1]

    def subset_sum(nums, target):
        reach = 1
        for x in nums:
            reach |= reach << x
        return bool((reach >> target) & 1)

    def common_substring(a, b):
        best, prev = 0, [0] * (len(b) + 1)
        for i in range(1, len(a) + 1):
            cur = [0] * (len(b) + 1)
            for j in range(1, len(b) + 1):
                if a[i - 1] == b[j - 1]:
                    cur[j] = prev[j - 1] + 1
                    best = max(best, cur[j])
            prev = cur
        return best

    def max_sum_increasing(nums):
        best = list(nums)
        for i in range(len(nums)):
            for j in range(i):
                if nums[j] < nums[i]:
                    best[i] = max(best[i], best[j] + nums[i])
        return max(best)

    # ------------------------------------------------------------------ cases
    def c_knapsack():
        cases = [([1, 3, 4, 5], [1, 4, 5, 7], 7), ([10], [60], 5), ([5], [10], 5), ([1, 2, 3], [6, 10, 12], 5),
                 ([4, 5, 1], [1, 2, 3], 4), ([2, 3, 4, 5], [3, 4, 5, 6], 5), ([3, 4, 5], [30, 50, 60], 8)]
        for n, cap, wmax in ((8, 20, 10), (15, 60, 25), (30, 150, 40), (60, 400, 60), (100, 1000, 100), (100, 700, 90), (80, 900, 100)):
            cases.append((arr(n, 1, wmax), arr(n, 1, 1000), cap))
        return cases

    def c_rod():
        cases = [[1], [2, 5, 7, 8, 10], [3, 5, 8, 9, 10, 17, 17, 20], [1, 5, 8, 9, 10, 17, 17, 20], [10, 1, 1, 1], [1, 1, 1, 1, 1]]
        for n in (6, 12, 25, 50, 80, 100):
            cases.append(arr(n, 1, 1000))
        return cases

    def c_chain():
        cases = [[10, 20], [10, 20, 30], [10, 20, 30, 40, 30], [40, 20, 30, 10, 30], [1, 2, 3, 4, 3], [5, 4, 6, 2, 7]]
        for n in (6, 9, 14, 25, 50, 80, 101):
            cases.append(arr(n, 1, 50))
        return cases

    def c_cuts():
        cases = ["aab", "a", "ab", "aaaa", "abcba", "abcd", "noonabbad", "ababbbabbababa", "cdd", "aabaa"]
        for n, alpha in ((12, "ab"), (30, "abc"), (60, "ab"), (120, "abcd"), (200, "ab"), (300, "abc")):
            cases.append(word(n, alpha))
        cases.append("a" * 250)
        cases.append("abcdefghij" * 20)
        return cases

    def c_lps():
        cases = ["bbbab", "cbbd", "a", "ab", "aaaa", "agbdba", "abcde", "character", "racecar"]
        for n, alpha in ((15, "ab"), (40, "abc"), (90, "abcd"), (200, "abc"), (400, "ab"), (700, "abcde"), (1000, "ab")):
            cases.append(word(n, alpha))
        return cases

    def c_eggs():
        cases = [(1, 2), (2, 6), (2, 10), (3, 14), (1, 1), (1, 100), (2, 36), (2, 100), (3, 25), (4, 100), (10, 1), (5, 5)]
        cases += [(2, 1000), (3, 1000), (7, 500), (4, 5000), (100, 10000), (50, 9999), (2, 10000), (6, 8192)]
        return cases

    def c_jobs():
        cases = [([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]), ([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60]),
                 ([1, 1, 1], [2, 3, 4], [5, 6, 4]), ([1], [2], [7]), ([1, 2], [2, 3], [5, 5]), ([1, 3], [4, 6], [8, 9])]
        for n, span in ((8, 20), (15, 40), (30, 100), (60, 300), (120, 600), (200, 1000)):
            start = arr(n, 1, span - 1)
            end = [min(span, s + rng.randint(1, max(2, span // 5))) for s in start]
            cases.append((start, end, arr(n, 1, 1000)))
        return cases

    def c_subset():
        cases = [([3, 34, 4, 12, 5, 2], 9), ([3, 34, 4, 12, 5, 2], 30), ([1], 1), ([1], 2), ([2, 4, 6], 5), ([5, 5, 5], 10), ([7, 3, 2, 5, 8], 14)]
        for n, hi, target in ((10, 20, 55), (20, 40, 300), (40, 60, 777), (60, 80, 1500), (100, 100, 4000), (100, 90, 5000), (50, 100, 2)):
            cases.append((arr(n, 1, hi), target))
        return cases

    def c_substr():
        cases = [("abcdxyz", "xyzabcd"), ("zxabcdezy", "yzabcdezx"), ("a", "b"), ("abc", "abc"), ("abcdef", "xabcy"), ("aaaa", "aa")]
        for n, m, alpha in ((12, 10, "ab"), (30, 25, "abc"), (80, 60, "abcd"), (200, 180, "ab"), (350, 300, "abc"), (500, 500, "ab")):
            a, b = word(n, alpha), word(m, alpha)
            # plant a shared block so the answer is not always tiny
            block = word(max(3, min(n, m) // 4), alpha)
            i, j = rng.randint(0, n - len(block)), rng.randint(0, m - len(block))
            cases.append((a[:i] + block + a[i + len(block):], b[:j] + block + b[j + len(block):]))
        return cases

    def c_msis():
        cases = [[1, 101, 2, 3, 100, 4, 5], [3, 4, 5, 10], [10, 5, 4, 3], [1], [5, 5, 5], [4, 6, 1, 3, 8, 4, 6], [1, 2, 3, 4, 5]]
        for n, hi in ((10, 20), (25, 100), (60, 300), (150, 500), (400, 1000), (800, 1000), (1000, 1000)):
            cases.append(arr(n, 1, hi))
        return cases

    N_LINE = "Line 1: `n`.\nLine 2: `n` space-separated integers."
    return [
        mk("zero-one-knapsack", "0/1 Knapsack", "MEDIUM", ["array", "dynamic-programming"],
           [("weights", "int[]"), ("values", "int[]"), ("capacity", "int")], "int", knapsack, c_knapsack(),
           "There are `n` items; item `i` weighs `weights[i]` and is worth `values[i]`. Each item can be taken at most once. "
           "Return the largest total value that fits in a knapsack with the given `capacity`.",
           "Line 1: `n`.\nLine 2: the `n` weights.\nLine 3: `n` again.\nLine 4: the `n` values.\nLine 5: `capacity`.",
           "The maximum total value.", ["`1 <= n <= 100`", "`1 <= weights[i] <= 100`, `1 <= values[i] <= 1000`", "`1 <= capacity <= 1000`"]),
        mk("rod-cutting", "Rod Cutting", "MEDIUM", ["array", "dynamic-programming"], [("prices", "int[]")], "int", rod_cutting, c_rod(),
           "A rod has length `n` (the length of `prices`). `prices[i]` is the price of a piece of length `i + 1`. "
           "Cut the rod into pieces of whole lengths (or do not cut at all) and return the largest total price you can get.",
           N_LINE, "The maximum total price.", ["`1 <= n <= 100`", "`1 <= prices[i] <= 1000`"]),
        mk("matrix-chain-multiplication", "Matrix Chain Multiplication", "HARD", ["array", "dynamic-programming"], [("dims", "int[]")], "int", chain, c_chain(),
           "Matrix `i` has `dims[i]` rows and `dims[i + 1]` columns, so `dims` describes a chain of `n - 1` matrices. Multiplying a `p x q` matrix by a "
           "`q x r` matrix costs `p * q * r` scalar multiplications. Return the minimum total cost of multiplying the whole chain, choosing the best "
           "way to place the brackets.", N_LINE, "The minimum number of scalar multiplications.",
           ["`2 <= n <= 101`", "`1 <= dims[i] <= 50`", "With `n = 2` there is a single matrix and the cost is `0`"]),
        mk("palindrome-partitioning-ii", "Palindrome Partitioning II", "HARD", ["string", "dynamic-programming"], [("s", "str")], "int", min_cuts, c_cuts(),
           "Cut the string `s` into pieces so that every piece is a palindrome. Return the minimum number of cuts needed.",
           "A line with the string `s`.", "The minimum number of cuts.", ["`1 <= s.length <= 300`", "Lowercase English letters"]),
        mk("longest-palindromic-subsequence", "Longest Palindromic Subsequence", "MEDIUM", ["string", "dynamic-programming"], [("s", "str")], "int", lps, c_lps(),
           "Return the length of the longest palindromic **subsequence** of `s` (characters keep their order but need not be next to each other).",
           "A line with the string `s`.", "The length of the longest palindromic subsequence.", ["`1 <= s.length <= 1000`", "Lowercase English letters"]),
        mk("egg-dropping-puzzle", "Egg Dropping Puzzle", "HARD", ["math", "binary-search", "dynamic-programming"], [("eggs", "int"), ("floors", "int")], "int", egg_drop, c_eggs(),
           "You have `eggs` identical eggs and a building with `floors` floors. There is a critical floor `f` (`0 <= f <= floors`): an egg dropped from a floor "
           "higher than `f` breaks, otherwise it survives and can be reused. Return the minimum number of drops that is **guaranteed** to find `f`, whatever it is.",
           "Line 1: `eggs`.\nLine 2: `floors`.", "The minimum number of drops in the worst case.", ["`1 <= eggs <= 100`", "`1 <= floors <= 10000`"]),
        mk("maximum-profit-in-job-scheduling", "Maximum Profit in Job Scheduling", "HARD", ["array", "binary-search", "dynamic-programming"],
           [("startTime", "int[]"), ("endTime", "int[]"), ("profit", "int[]")], "int", job_scheduling, c_jobs(),
           "Job `i` runs from `startTime[i]` to `endTime[i]` and pays `profit[i]`. You can do jobs one after another, but two jobs may not overlap; a job may start "
           "at the exact moment another one ends. Return the maximum total profit.",
           "Line 1: `n`.\nLine 2: the `n` start times.\nLine 3: `n` again.\nLine 4: the `n` end times.\nLine 5: `n` again.\nLine 6: the `n` profits.",
           "The maximum profit.", ["`1 <= n <= 200`", "`1 <= startTime[i] < endTime[i] <= 1000`", "`1 <= profit[i] <= 1000`"]),
        mk("subset-sum-equal-to-target", "Subset Sum Equal to Target", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]"), ("target", "int")], "bool", subset_sum, c_subset(),
           "Return `true` if some subset of `nums` adds up to exactly `target`.",
           "Line 1: `n`.\nLine 2: `n` space-separated integers.\nLine 3: `target`.", "`true` or `false`.",
           ["`1 <= n <= 100`", "`1 <= nums[i] <= 100`", "`1 <= target <= 5000`"]),
        mk("longest-common-substring", "Longest Common Substring", "MEDIUM", ["string", "dynamic-programming"], [("s1", "str"), ("s2", "str")], "int", common_substring, c_substr(),
           "Return the length of the longest **substring** (consecutive characters) that appears in both `s1` and `s2`. Return `0` if they share none.",
           "Line 1: `s1`.\nLine 2: `s2`.", "The length of the longest common substring.", ["`1 <= s1.length, s2.length <= 500`", "Lowercase English letters"]),
        mk("maximum-sum-increasing-subsequence", "Maximum Sum Increasing Subsequence", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]")], "int", max_sum_increasing, c_msis(),
           "Among all strictly increasing subsequences of `nums`, return the largest possible sum of its elements.",
           N_LINE, "The maximum sum.", ["`1 <= n <= 1000`", "`1 <= nums[i] <= 1000`"]),
    ]
