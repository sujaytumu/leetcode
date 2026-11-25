"""Striver sheet batch 3: greedy, stack, string and recursion problems.

Every expected output comes from a deliberately simple reference (brute force where possible), so the optimal C++
answers in answers/a2z-03-greedy-stacks-strings.txt are checked against an independent method.
"""
import itertools


def make_batch(mk, rng):
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]
    SIZES = [1, 2, 5, 12, 40, 150, 500]

    # ---------------------------------------------------------------- references
    def meetings(start, end):
        count, last = 0, -1
        for s, e in sorted(zip(start, end), key=lambda m: (m[1], m[0])):
            if s > last:
                count, last = count + 1, e
        return count

    def platforms(arr_, dep):
        best = 0
        for i in range(len(arr_)):  # busiest moment is always some arrival
            best = max(best, sum(1 for j in range(len(arr_)) if arr_[j] <= arr_[i] <= dep[j]))
        return best

    def job_sequencing(deadline, profit):
        slot = [None] * (max(deadline) + 1)
        for p, d in sorted(zip(profit, deadline), key=lambda j: -j[0]):
            for t in range(d, 0, -1):
                if slot[t] is None:
                    slot[t] = p
                    break
        done = [p for p in slot[1:] if p is not None]
        return [len(done), sum(done)]

    def next_smaller(nums):
        out = []
        for i, x in enumerate(nums):
            out.append(next((y for y in nums[i + 1:] if y < x), -1))
        return out

    def stock_span(prices):
        out = []
        for i, p in enumerate(prices):
            k = 1
            while i - k >= 0 and prices[i - k] <= p:
                k += 1
            out.append(k)
        return out

    def window_maxima_of_minima(nums):
        n = len(nums)
        return [max(min(nums[i:i + k]) for i in range(n - k + 1)) for k in range(1, n + 1)]

    def celebrity(m):
        n = len(m)
        for i in range(n):
            if all(m[j][i] == 1 and m[i][j] == 0 for j in range(n) if j != i):
                return i
        return -1

    def to_roman(num):
        out = ""
        for v, s in [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                     (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
            while num >= v:
                out, num = out + s, num - v
        return out

    def kmp_search(text, pat):
        hits = [i for i in range(len(text) - len(pat) + 1) if text[i:i + len(pat)] == pat]
        return hits or [-1]

    def min_chars_palindrome(s):
        for p in range(len(s), 0, -1):
            if s[:p] == s[:p][::-1]:
                return len(s) - p
        return len(s) - 1

    def count_and_say(n):
        s = "1"
        for _ in range(n - 1):
            out, i = "", 0
            while i < len(s):
                j = i
                while j < len(s) and s[j] == s[i]:
                    j += 1
                out += str(j - i) + s[i]
                i = j
            s = out
        return s

    def permutation_sequence(n, k):
        return "".join(next(itertools.islice(itertools.permutations("123456789"[:n]), k - 1, None)))

    def subset_sums(nums):
        n = len(nums)
        return sorted(sum(nums[i] for i in range(n) if mask >> i & 1) for mask in range(1 << n))

    def m_coloring(n, edges, m):
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        color = [-1] * n

        def go(v):
            if v == n:
                return True
            for c in range(m):
                if all(color[u] != c for u in adj[v]):
                    color[v] = c
                    if go(v + 1):
                        return True
                    color[v] = -1
            return False
        return go(0)

    def maze_paths(grid):
        n = len(grid)
        if grid[0][0] == 0 or grid[n - 1][n - 1] == 0:
            return 0
        seen = [[False] * n for _ in range(n)]

        def go(r, c):
            if r == n - 1 and c == n - 1:
                return 1
            seen[r][c] = True
            total = 0
            for dr, dc in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 1 and not seen[nr][nc]:
                    total += go(nr, nc)
            seen[r][c] = False
            return total
        return go(0, 0)

    # ---------------------------------------------------------------- cases
    def c_meetings():
        out = []
        for n in SIZES:
            s = arr(n, 0, 120)
            out.append((s, [x + rng.randint(0, 12) for x in s]))
        return out + [([1, 3, 0, 5, 8, 5], [2, 4, 6, 7, 9, 9]), ([10, 12, 20], [20, 25, 30]), ([5], [5])]

    def c_platforms():
        out = []
        for n in SIZES:
            a = arr(n, 0, 2359)
            out.append((a, [x + rng.randint(0, 300) for x in a]))
        return out + [([900, 940, 950, 1100, 1500, 1800], [910, 1200, 1120, 1130, 1900, 2000]), ([100, 200], [100, 300]), ([5], [5])]

    def c_jobs():
        out = []
        for n in SIZES:
            out.append((arr(n, 1, max(2, n // 2 + 1)), arr(n, 1, 500)))
        return out + [([4, 1, 1, 1], [20, 10, 40, 30]), ([2, 1, 2, 1, 1], [100, 19, 27, 25, 15]), ([1], [7])]

    def c_arrays(lo, hi, extra=()):
        return [arr(n, lo, hi) for n in SIZES] + list(extra)

    def c_celebrity():
        out = []
        for n in [2, 3, 5, 8, 20, 60]:
            m = [[rng.randint(0, 1) for _ in range(n)] for _ in range(n)]
            for i in range(n):
                m[i][i] = 0
            if len(out) % 2 == 0:
                c = rng.randrange(n)
                for j in range(n):
                    m[c][j] = 0
                    if j != c:
                        m[j][c] = 1
            out.append(m)
        out.append([[0, 1, 0], [0, 0, 0], [0, 1, 0]])
        return out

    def c_roman():
        return [3, 4, 9, 14, 40, 58, 90, 400, 1994, 2024, 3999, 1, 3888, rng.randint(1, 3999), rng.randint(1, 3999)]

    def c_kmp():
        out = []
        for n, m in [(10, 2), (30, 3), (80, 2), (200, 4), (600, 3), (900, 5)]:
            text = "".join(rng.choice("ab") for _ in range(n))
            out.append((text, "".join(rng.choice("ab") for _ in range(m))))
        return out + [("aaaaa", "aa"), ("abcabcabc", "abc"), ("hello", "xyz"), ("a", "a"), ("abab", "ababab")]

    def c_palindrome():
        out = ["".join(rng.choice("abc") for _ in range(n)) for n in [1, 2, 3, 6, 15, 60, 300, 900]]
        return out + ["abcd", "aacecaaa", "aba", "aaaa", "abbacd"]

    def c_perm():
        out = []
        for n in range(1, 9):
            import math
            out.append((n, rng.randint(1, math.factorial(n))))
        return out + [(3, 1), (3, 6), (4, 9), (8, 40320), (8, 1)]

    def c_subsets():
        return [arr(n, -9, 20) for n in [1, 2, 3, 5, 7, 9, 10]] + [[1, 1, 1], [0, 0], [3, 34, 4, 12, 5, 2]]

    def c_color():
        out = []
        for n, e, m in [(4, 5, 3), (4, 5, 2), (5, 7, 3), (6, 10, 3), (7, 12, 3), (8, 16, 4), (9, 20, 3), (10, 25, 4), (6, 8, 2)]:
            edges = set()
            while len(edges) < min(e, n * (n - 1) // 2):
                u, v = sorted(rng.sample(range(n), 2))
                edges.add((u, v))
            out.append((n, [list(x) for x in sorted(edges)], m))
        return out + [(2, [[0, 1]], 1), (3, [[0, 1], [1, 2], [0, 2]], 3), (3, [[0, 1], [1, 2], [0, 2]], 2)]

    def c_maze():
        out = []
        for n in [2, 3, 4, 5, 5, 6, 6, 6]:
            g = [[1 if rng.random() < 0.8 else 0 for _ in range(n)] for _ in range(n)]
            g[0][0] = g[n - 1][n - 1] = 1
            out.append(g)
        return out + [[[1, 1], [1, 1]], [[1, 0], [0, 1]], [[1]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]]]

    ARR = "Line 1: `n`.\nLine 2: `n` space-separated integers."
    ONE = lambda v: [f"`1 <= n <= 1000`", v]
    batch = [
        mk("n-meetings-in-one-room", "N Meetings in One Room", "MEDIUM", ["array", "greedy", "sorting"],
           [("start", "int[]"), ("end", "int[]")], "int", meetings, c_meetings(),
           "Meeting `i` runs from `start[i]` to `end[i]` (both inclusive) and one room is available. A meeting can only "
           "begin after the previous one has ended, so it must start strictly later than the previous end. Return the "
           "maximum number of meetings that can be held.",
           "Line 1: `n`.\nLine 2: `n` start times.\nLine 3: `n`.\nLine 4: `n` end times.", "The maximum number of meetings.",
           ["`1 <= n <= 1000`", "`0 <= start[i] <= end[i] <= 10^4`"]),
        mk("minimum-platforms", "Minimum Platforms", "MEDIUM", ["array", "greedy", "sorting"],
           [("arr", "int[]"), ("dep", "int[]")], "int", platforms, c_platforms(),
           "Train `i` arrives at `arr[i]` and leaves at `dep[i]`. A train still occupies its platform at its departure "
           "time, so a train arriving at that same moment needs another platform. Return the minimum number of platforms "
           "needed so that no train waits.",
           "Line 1: `n`.\nLine 2: `n` arrival times.\nLine 3: `n`.\nLine 4: `n` departure times.", "The minimum number of platforms.",
           ["`1 <= n <= 1000`", "`0 <= arr[i] <= dep[i] <= 10^4`"]),
        mk("job-sequencing-problem", "Job Sequencing Problem", "MEDIUM", ["array", "greedy", "sorting"],
           [("deadline", "int[]"), ("profit", "int[]")], "int[]", job_sequencing, c_jobs(),
           "Every job takes one unit of time and earns `profit[i]` only if it is finished by `deadline[i]` (time slots "
           "are numbered from 1). Only one job runs at a time. Return `[jobs done, total profit]` for the best schedule.",
           "Line 1: `n`.\nLine 2: `n` deadlines.\nLine 3: `n`.\nLine 4: `n` profits.", "Two integers: the number of jobs, then the total profit.",
           ["`1 <= n <= 1000`", "`1 <= deadline[i] <= n`", "`1 <= profit[i] <= 500`"]),
        mk("next-smaller-element", "Next Smaller Element", "MEDIUM", ["array", "stack", "monotonic-stack"],
           [("nums", "int[]")], "int[]", next_smaller, c_arrays(-50, 50, [[1], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [4, 8, 5, 2, 25]]),
           "For every element, find the first element to its **right** that is strictly smaller. Return an array holding "
           "that value, or `-1` where none exists.", ARR, "`n` integers: the next smaller value for each position.",
           ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
        mk("stock-span-problem", "Stock Span Problem", "MEDIUM", ["array", "stack", "monotonic-stack"],
           [("prices", "int[]")], "int[]", stock_span, c_arrays(1, 60, [[100, 80, 60, 70, 60, 75, 85], [10, 20, 30], [30, 20, 10]]),
           "The span of a day is the number of consecutive days ending on it (including itself) whose price is less than or "
           "equal to that day's price. Return the span for every day.", "Line 1: `n`.\nLine 2: `n` daily prices.",
           "`n` integers: the span of each day.", ["`1 <= n <= 1000`", "`1 <= prices[i] <= 10^4`"]),
        mk("maximum-of-minimums-for-every-window-size", "Maximum of Minimums for Every Window Size", "HARD", ["array", "stack", "monotonic-stack"],
           [("nums", "int[]")], "int[]", window_maxima_of_minima, c_arrays(1, 90, [[10, 20, 30, 50, 10, 70, 30], [1], [3, 3, 3]]),
           "For every window size `k` from 1 to `n`, take the minimum of each window of that size and keep the largest of "
           "those minimums. Return the `n` answers for `k = 1, 2, ..., n`.", ARR, "`n` integers: the answer for each window size.",
           ["`1 <= n <= 1000`", "`1 <= nums[i] <= 10^4`"]),
        mk("celebrity-problem", "The Celebrity Problem", "MEDIUM", ["matrix", "stack", "two-pointers"],
           [("M", "int[][]")], "int", celebrity, c_celebrity(),
           "In a party of `n` people, `M[i][j] = 1` means person `i` knows person `j`. A celebrity is known by everybody "
           "else and knows nobody. Return the celebrity's index, or `-1` if there is none. Try to use `O(n)` calls to the "
           "matrix instead of checking every pair.", "Line 1: `n`.\nNext `n` lines: the rows of `M`.", "The index of the celebrity, or `-1`.",
           ["`2 <= n <= 100`", "`M[i][i] = 0`"]),
        mk("integer-to-roman", "Integer to Roman", "MEDIUM", ["math", "string"], [("num", "int")], "str", to_roman, c_roman(),
           "Convert an integer to a Roman numeral using the usual subtractive forms (`IV`, `IX`, `XL`, `XC`, `CD`, `CM`).",
           "Line 1: `num`.", "The Roman numeral.", ["`1 <= num <= 3999`"]),
        mk("kmp-pattern-search", "Find All Occurrences of a Pattern", "MEDIUM", ["string"], [("text", "str"), ("pattern", "str")],
           "int[]", kmp_search, c_kmp(),
           "Return the starting index of every occurrence of `pattern` in `text`, overlapping occurrences included, in "
           "increasing order. If there is none return `[-1]`. Aim for `O(n + m)` with the KMP prefix function.",
           "Line 1: `text`.\nLine 2: `pattern`.", "The indices separated by spaces, or `-1`.",
           ["`1 <= text.length <= 1000`", "`1 <= pattern.length <= 1000`", "Lowercase English letters"]),
        mk("minimum-characters-to-make-palindrome", "Shortest Palindrome Length", "HARD", ["string"], [("s", "str")], "int", min_chars_palindrome,
           c_palindrome(),
           "You may add characters only at the **front** of `s`. Return the minimum number of characters to add so that "
           "the whole string becomes a palindrome.", "Line 1: `s`.", "The minimum number of characters.",
           ["`1 <= s.length <= 1000`", "Lowercase English letters"]),
        mk("count-and-say", "Count and Say", "MEDIUM", ["string"], [("n", "int")], "str", count_and_say,
           [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30],
           "`countAndSay(1) = \"1\"`, and `countAndSay(n)` describes `countAndSay(n - 1)` by reading its runs of equal "
           "digits aloud: each run becomes its length followed by the digit. For example `3322251` becomes `23321511`. "
           "Return `countAndSay(n)`.", "Line 1: `n`.", "The `n`-th term.", ["`1 <= n <= 30`"]),
        mk("permutation-sequence", "Permutation Sequence", "HARD", ["math", "recursion"], [("n", "int"), ("k", "int")], "str",
           permutation_sequence, c_perm(),
           "List all permutations of the digits `1..n` in increasing order. Return the `k`-th one (1-indexed) as a string, "
           "without generating all of them.", "Line 1: `n`.\nLine 2: `k`.", "The `k`-th permutation.",
           ["`1 <= n <= 8`", "`1 <= k <= n!`"]),
        mk("subset-sums", "Subset Sums", "MEDIUM", ["array", "backtracking", "bit-manipulation"], [("nums", "int[]")], "int[]",
           subset_sums, c_subsets(),
           "Return the sum of every subset of `nums` (the empty subset gives `0`), sorted in increasing order. Equal sums "
           "from different subsets are all listed.", ARR, "`2^n` integers in increasing order.",
           ["`1 <= n <= 10`", "`-10^4 <= nums[i] <= 10^4`"]),
        mk("m-coloring-problem", "M-Coloring Problem", "HARD", ["graph", "backtracking"],
           [("n", "int"), ("edges", "int[][]"), ("m", "int")], "bool", m_coloring, c_color(),
           "An undirected graph has `n` vertices (numbered from 0). Return `true` if its vertices can be coloured with at "
           "most `m` colours so that no two adjacent vertices share a colour.",
           "Line 1: `n`.\nLine 2: `e`, the number of edges.\nNext `e` lines: `u v`.\nLast line: `m`.", "`true` or `false`.",
           ["`2 <= n <= 10`", "`1 <= e <= 30`", "`1 <= m <= n`"]),
        mk("rat-in-a-maze-count", "Rat in a Maze (Count Paths)", "MEDIUM", ["matrix", "backtracking"], [("grid", "int[][]")], "int",
           maze_paths, c_maze(),
           "A rat starts at the top-left cell of an `n x n` grid and wants to reach the bottom-right cell. A `1` cell is "
           "open and a `0` cell is blocked. It moves up, down, left or right and may not visit a cell twice in one path. "
           "Return the number of different paths.", "Line 1: `n`.\nNext `n` lines: the rows, `n` integers each.", "The number of paths.",
           ["`1 <= n <= 6`"]),
    ]
    return [p for p in batch if p["slug"] not in {"count-and-say", "permutation-sequence", "subset-sums", "m-coloring-problem"}]
