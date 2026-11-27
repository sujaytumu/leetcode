"""Striver A2Z / SDE sheet batch 9: sliding window, stack, sorted-array sums, binary search on the answer and the DP
family (knapsack, rod cutting, matrix chain, palindrome partitioning).

Every expected output comes from a deliberately plain reference (brute force or a differently-shaped recursion), so the
optimal C++ answers in answers/a2z-06-window-stack-dp.txt are checked against an independent method.
"""
import itertools
from functools import lru_cache


def make_batch(mk, rng):
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]
    SIZES = [1, 2, 5, 12, 40, 120, 300]
    ARR = "Line 1: `n`.\nLine 2: `n` space-separated integers."

    # ---------------------------------------------------------------- references
    def k_distinct(nums, k):
        return sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if len(set(nums[i:j + 1])) == k)

    def nice_subarrays(nums, k):
        return sum(1 for i in range(len(nums)) for j in range(i, len(nums))
                   if sum(x % 2 for x in nums[i:j + 1]) == k)

    def fruits(nums):
        return max(j - i + 1 for i in range(len(nums)) for j in range(i, len(nums)) if len(set(nums[i:j + 1])) <= 2)

    def ones_iii(nums, k):
        return max((j - i + 1 for i in range(len(nums)) for j in range(i, len(nums)) if nums[i:j + 1].count(0) <= k), default=0)

    def card_points(points, k):
        n = len(points)
        return max(sum(points[:i]) + sum(points[n - (k - i):]) for i in range(k + 1))

    def three_chars(s):
        return sum(1 for i in range(len(s)) for j in range(i, len(s)) if set(s[i:j + 1]) >= set("abc"))

    def remove_k(num, k):
        digits = list(num)
        for _ in range(k):  # drop the first digit that is bigger than its right neighbour (or the last digit)
            i = 0
            while i + 1 < len(digits) and digits[i] <= digits[i + 1]:
                i += 1
            digits.pop(i)
        return "".join(digits).lstrip("0") or "0"

    def asteroids(nums):
        a = list(nums)
        changed = True
        while changed:
            changed = False
            for i in range(len(a) - 1):
                if a[i] > 0 > a[i + 1]:
                    if a[i] > -a[i + 1]:
                        del a[i + 1]
                    elif a[i] < -a[i + 1]:
                        del a[i]
                    else:
                        del a[i:i + 2]
                    changed = True
                    break
        return a

    def subarray_ranges(nums):
        return sum(max(nums[i:j + 1]) - min(nums[i:j + 1]) for i in range(len(nums)) for j in range(i, len(nums)))

    def three_sum(nums):
        found = {tuple(sorted(c)) for c in itertools.combinations(nums, 3) if sum(c) == 0}
        return [list(t) for t in sorted(found)]

    def four_sum(nums, target):
        found = {tuple(sorted(c)) for c in itertools.combinations(nums, 4) if sum(c) == target}
        return [list(t) for t in sorted(found)]

    def divide(a, b):
        q = abs(a) // abs(b)
        if (a < 0) != (b < 0):
            q = -q
        return max(-2 ** 31, min(2 ** 31 - 1, q))

    def books(pages, m):
        n = len(pages)
        if m > n:
            return -1

        @lru_cache(maxsize=None)
        def best(i, parts):  # smallest possible "largest load" for pages[i:] split into `parts` pieces
            if parts == 1:
                return sum(pages[i:])
            return min(max(sum(pages[i:j]), best(j, parts - 1)) for j in range(i + 1, n - parts + 2))
        return best(0, m)

    def knapsack(w, v, cap):
        @lru_cache(maxsize=None)
        def go(i, room):
            if i == len(w):
                return 0
            skip = go(i + 1, room)
            return max(skip, v[i] + go(i + 1, room - w[i])) if w[i] <= room else skip
        return go(0, cap)

    def unbounded(w, v, cap):
        @lru_cache(maxsize=None)
        def go(room):
            return max([0] + [v[i] + go(room - w[i]) for i in range(len(w)) if w[i] <= room])
        return go(cap)

    def rod(prices):
        @lru_cache(maxsize=None)
        def go(left):
            return max([0] + [prices[c - 1] + go(left - c) for c in range(1, left + 1)])
        return go(len(prices))

    def matrix_chain(dims):
        @lru_cache(maxsize=None)
        def go(i, j):  # matrices i..j, matrix t is dims[t-1] x dims[t]
            if i == j:
                return 0
            return min(go(i, k) + go(k + 1, j) + dims[i - 1] * dims[k] * dims[j] for k in range(i, j))
        return go(1, len(dims) - 1)

    def min_cuts(s):
        n = len(s)
        pal = lambda t: t == t[::-1]

        @lru_cache(maxsize=None)
        def go(i):
            if pal(s[i:]):
                return 0
            return min(1 + go(j + 1) for j in range(i, n - 1) if pal(s[i:j + 1]))
        return go(0)

    def bit_flips(a, b):
        return sum(1 for bit in range(31) if (a >> bit & 1) != (b >> bit & 1))

    # ---------------------------------------------------------------- cases
    def c_k_distinct():
        out = []
        for n in [1, 2, 5, 12, 40, 100, 150]:
            out.append((arr(n, 1, max(2, n // 3)), rng.randint(1, min(3, n))))
        return out + [([1, 2, 1, 2, 3], 2), ([1, 2, 1, 3, 4], 3), ([2, 2, 2], 1), ([1, 2, 3, 4], 4)]

    def c_nice():
        out = []
        for n in [1, 2, 5, 12, 40, 150, 300]:
            out.append((arr(n, 1, 9), rng.randint(1, min(4, n))))
        return out + [([1, 1, 2, 1, 1], 3), ([2, 4, 6], 1), ([2, 2, 2, 1, 2, 2, 1, 2, 2, 2], 2), ([5], 1)]

    def c_fruits():
        out = [arr(n, 0, k) for n, k in [(1, 1), (2, 3), (5, 2), (12, 3), (40, 3), (120, 4), (300, 2), (300, 6)]]
        return out + [[1, 2, 1], [0, 1, 2, 2], [1, 2, 3, 2, 2], [3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4], [7]]

    def c_ones():
        out = []
        for n in [1, 2, 5, 12, 40, 150, 300]:
            out.append(([1 if rng.random() < 0.6 else 0 for _ in range(n)], rng.randint(0, min(4, n))))
        return out + [([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), ([0, 0, 0], 0), ([0, 0, 0], 3), ([1, 1, 1], 0)]

    def c_cards():
        out = []
        for n in [1, 3, 6, 12, 40, 150, 300]:
            out.append((arr(n, 1, 100), rng.randint(1, n)))
        return out + [([1, 2, 3, 4, 5, 6, 1], 3), ([2, 2, 2], 2), ([9, 7, 7, 9, 7, 7, 9], 7), ([1, 1000, 1], 1)]

    def c_three_chars():
        out = ["".join(rng.choice("abc") for _ in range(n)) for n in [3, 4, 8, 15, 40, 120, 300]]
        return out + ["abcabc", "aaacb", "abc", "aaaabbbbcccc", "cbacba"]

    def c_remove_k():
        out = []
        for n in [2, 5, 9, 20, 60, 200]:
            digits = "".join(rng.choice("0123456789") for _ in range(n)).lstrip("0") or "7"
            out.append((digits, rng.randint(0, len(digits))))
        return out + [("1432219", 3), ("10200", 1), ("10", 2), ("9", 1), ("112", 1), ("1234567890", 9), ("100", 1),
                      ("5337", 2), ("1173", 2)]

    def c_asteroids():
        out = []
        for n in [1, 2, 5, 8, 12, 40, 100]:
            while True:
                a = [rng.choice([-1, 1]) * rng.randint(1, 30) for _ in range(n)]
                if asteroids(a):
                    out.append(a)
                    break
        return out + [[5, 10, -5], [10, 2, -5], [-2, -1, 1, 2], [8, -8, 3], [1, -2, -2, -2], [-3, 4, -4, -5]]

    def c_ranges():
        return [arr(n, -20, 60) for n in [1, 2, 5, 12, 40, 120, 300]] + [[1, 2, 3], [4, -2, -3, 4, 1], [5, 5, 5], [7]]

    def c_three_sum():
        out = [arr(n, -12, 12) for n in [3, 5, 8, 12, 25, 50, 90]]
        return out + [[-1, 0, 1, 2, -1, -4], [0, 0, 0, 0], [1, 2, 3], [0, 0, 0], [-2, 0, 1, 1, 2], [-4, -2, -2, -2, 0, 1, 2, 2, 2, 3, 3, 4, 4, 6, 6]]

    def c_four_sum():
        out = []
        for n in [4, 6, 9, 14, 20, 30, 40]:
            out.append((arr(n, -10, 10), rng.randint(-6, 6)))
        return out + [([1, 0, -1, 0, -2, 2], 0), ([2, 2, 2, 2, 2], 8), ([1, 1, 1, 1], 4), ([-3, -1, 0, 2, 4, 5], 2)]

    def c_divide():
        mn, mx = -2 ** 31, 2 ** 31 - 1
        out = [(10, 3), (7, -3), (-7, 3), (-7, -3), (0, 5), (1, 1), (mn, -1), (mn, 1), (mx, 1), (mx, 2), (mn, 2),
               (mn, mn), (mx, mx), (5, 7), (-5, 7), (1, -1)]
        for _ in range(6):
            out.append((rng.randint(mn, mx), rng.choice([-1, 1]) * rng.randint(1, 10 ** rng.randint(1, 9))))
        return out

    def c_books():
        out = []
        for n in [1, 2, 4, 7, 12, 25, 40]:
            pages = arr(n, 1, 90)
            out.append((pages, rng.randint(1, min(n, 6))))
        return out + [([12, 34, 67, 90], 2), ([10, 20, 30, 40], 2), ([5, 5], 3), ([100], 1), ([7, 2, 5, 10, 8], 2)]

    def c_knapsack(unbounded_case):
        out = []
        for n, cap in [(1, 5), (2, 6), (4, 10), (6, 15), (10, 30), (20, 60), (30, 100)]:
            w = arr(n, 1, max(2, cap // 2))
            v = arr(n, 1, 100)
            out.append((w, v, cap))
        extra = [([1, 3, 4, 5], [1, 4, 5, 7], 7), ([2, 3], [10, 20], 1), ([5], [50], 5)]
        if unbounded_case:
            extra += [([2, 4, 6], [5, 11, 13], 16), ([3], [4], 10)]
        return out + extra

    def c_rod():
        return [arr(n, 1, 60) for n in [1, 2, 4, 8, 15, 30, 60]] + [[1, 5, 8, 9, 10, 17, 17, 20], [3, 5, 8, 9, 10, 17, 17, 20], [10], [1, 1, 1]]

    def c_chain():
        out = [arr(n + 1, 2, 40) for n in [1, 2, 3, 4, 6, 9, 14, 22, 30]]
        return out + [[10, 30, 5, 60], [40, 20, 30, 10, 30], [10, 20, 30, 40, 30], [5, 10]]

    def c_cuts():
        out = ["".join(rng.choice("ab") for _ in range(n)) for n in [1, 2, 3, 6, 12, 30, 70, 120]]
        return out + ["aab", "a", "ab", "abcde", "aaaa", "abacdc", "noonabbad", "racecar"]

    def c_bits():
        out = [(10, 7), (3, 4), (0, 0), (1, 2 ** 30), (2 ** 31 - 1, 0), (29, 15), (7, 7), (0, 2 ** 31 - 1)]
        return out + [(rng.randint(0, 2 ** 31 - 1), rng.randint(0, 2 ** 31 - 1)) for _ in range(6)]

    batch = [
        mk("subarrays-with-k-different-integers", "Subarrays with K Different Integers", "HARD",
           ["array", "sliding-window", "hash-table"], [("nums", "int[]"), ("k", "int")], "int", k_distinct, c_k_distinct(),
           "Return the number of contiguous subarrays of `nums` that contain exactly `k` different integers.",
           "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The number of subarrays.",
           ["`1 <= n <= 150`", "`1 <= nums[i] <= n`", "`1 <= k <= n`"]),
        mk("count-number-of-nice-subarrays", "Count Number of Nice Subarrays", "MEDIUM",
           ["array", "sliding-window", "prefix-sum"], [("nums", "int[]"), ("k", "int")], "int", nice_subarrays, c_nice(),
           "A subarray is nice if it contains exactly `k` odd numbers. Return how many nice subarrays `nums` has.",
           "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The number of nice subarrays.",
           ["`1 <= n <= 1000`", "`1 <= nums[i] <= 10^5`", "`1 <= k <= n`"]),
        mk("fruit-into-baskets", "Fruit Into Baskets", "MEDIUM", ["array", "sliding-window", "hash-table"],
           [("fruits", "int[]")], "int", fruits, c_fruits(),
           "`fruits[i]` is the type of fruit on tree `i`. You walk right from any starting tree, picking one fruit from "
           "every tree, and own two baskets that each hold a single fruit type. Stop when a tree has a third type. "
           "Return the maximum number of fruits you can pick.", ARR, "The maximum number of fruits.",
           ["`1 <= n <= 1000`", "`0 <= fruits[i] < n`"]),
        mk("max-consecutive-ones-iii", "Max Consecutive Ones III", "MEDIUM", ["array", "sliding-window"],
           [("nums", "int[]"), ("k", "int")], "int", ones_iii, c_ones(),
           "`nums` holds only `0` and `1`. You may flip at most `k` zeros to ones. Return the length of the longest "
           "run of consecutive ones you can get.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The longest run.",
           ["`1 <= n <= 1000`", "`nums[i]` is `0` or `1`", "`0 <= k <= n`"]),
        mk("maximum-points-you-can-obtain-from-cards", "Maximum Points You Can Obtain from Cards", "MEDIUM",
           ["array", "sliding-window", "prefix-sum"], [("cardPoints", "int[]"), ("k", "int")], "int", card_points, c_cards(),
           "Cards lie in a row with points `cardPoints[i]`. In each of `k` steps you take one card from either the "
           "left end or the right end. Return the maximum total points.",
           "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The maximum score.",
           ["`1 <= n <= 1000`", "`1 <= cardPoints[i] <= 10^4`", "`1 <= k <= n`"]),
        mk("number-of-substrings-containing-all-three-characters", "Number of Substrings Containing All Three Characters", "MEDIUM",
           ["string", "sliding-window"], [("s", "str")], "int", three_chars, c_three_chars(),
           "`s` only has the letters `a`, `b` and `c`. Return the number of substrings that contain at least one of "
           "each of the three letters.", "Line 1: `s`.", "The number of substrings.",
           ["`3 <= s.length <= 1000`", "Only `a`, `b` and `c`"]),
        mk("remove-k-digits", "Remove K Digits", "MEDIUM", ["string", "stack", "greedy", "monotonic-stack"],
           [("num", "str"), ("k", "int")], "str", remove_k, c_remove_k(),
           "Remove exactly `k` digits from the number `num` so that the remaining number is as small as possible. "
           "Return it without leading zeros, or `0` if nothing is left.", "Line 1: `num`.\nLine 2: `k`.",
           "The smallest possible number.", ["`1 <= num.length <= 1000`", "`0 <= k <= num.length`", "`num` has no leading zeros"]),
        mk("asteroid-collision", "Asteroid Collision", "MEDIUM", ["array", "stack"], [("asteroids", "int[]")], "int[]",
           asteroids, c_asteroids(),
           "Each asteroid moves at the same speed: positive values move right, negative values move left, and the "
           "absolute value is its size. When two meet, the smaller one explodes, and both explode if equal. Asteroids "
           "moving the same way never meet. Return what is left after all collisions.", ARR,
           "The surviving asteroids, left to right.", ["`1 <= n <= 1000`", "`1 <= |asteroids[i]| <= 1000`", "At least one asteroid survives"]),
        mk("sum-of-subarray-ranges", "Sum of Subarray Ranges", "MEDIUM", ["array", "stack", "monotonic-stack"],
           [("nums", "int[]")], "int", subarray_ranges, c_ranges(),
           "The range of a subarray is its largest element minus its smallest. Return the sum of the ranges of all "
           "subarrays of `nums`.", ARR, "The sum of all ranges.", ["`1 <= n <= 1000`", "`-100 <= nums[i] <= 100`"]),
        mk("3sum", "3Sum", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]")], "int[][]", three_sum,
           c_three_sum(),
           "Return every unique triplet `[a, b, c]` of `nums` (taken at different positions) with `a + b + c = 0`. Sort "
           "each triplet in increasing order and list the triplets in increasing lexicographic order, with no repeats.",
           ARR, "One triplet per line, numbers separated by spaces. Print nothing if there is none.",
           ["`3 <= n <= 100`", "`-10^4 <= nums[i] <= 10^4`"]),
        mk("4sum", "4Sum", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]"), ("target", "int")], "int[][]",
           four_sum, c_four_sum(),
           "Return every unique quadruplet of `nums` (taken at different positions) that adds up to `target`. Sort each "
           "quadruplet in increasing order and list them in increasing lexicographic order, with no repeats.",
           "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.",
           "One quadruplet per line, numbers separated by spaces. Print nothing if there is none.",
           ["`4 <= n <= 40`", "`-10^4 <= nums[i] <= 10^4`"]),
        mk("divide-two-integers", "Divide Two Integers", "MEDIUM", ["math", "bit-manipulation"],
           [("dividend", "int"), ("divisor", "int")], "int", divide, c_divide(),
           "Divide `dividend` by `divisor` without using multiplication, division or modulo, truncating toward zero. "
           "If the quotient is outside the signed 32-bit range, clamp it to that range.",
           "Line 1: `dividend`.\nLine 2: `divisor`.", "The quotient.",
           ["`-2^31 <= dividend, divisor <= 2^31 - 1`", "`divisor != 0`"]),
        mk("allocate-books", "Allocate Books", "HARD", ["array", "binary-search"], [("pages", "int[]"), ("m", "int")], "int",
           books, c_books(),
           "Book `i` has `pages[i]` pages. Give the books, in order, to `m` students so that each student gets a "
           "contiguous block of at least one book. Minimise the largest number of pages any student reads and return "
           "it, or `-1` if it is impossible.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `m`.",
           "The minimised maximum, or `-1`.", ["`1 <= n <= 1000`", "`1 <= pages[i] <= 10^4`", "`1 <= m <= 1000`"]),
        mk("0-1-knapsack", "0/1 Knapsack", "MEDIUM", ["dynamic-programming"],
           [("weights", "int[]"), ("values", "int[]"), ("capacity", "int")], "int", knapsack, c_knapsack(False),
           "Item `i` weighs `weights[i]` and is worth `values[i]`. Each item can be taken at most once and the total "
           "weight must not exceed `capacity`. Return the maximum total value.",
           "Line 1: `n`.\nLine 2: `n` weights.\nLine 3: `n`.\nLine 4: `n` values.\nLine 5: `capacity`.",
           "The maximum value.", ["`1 <= n <= 100`", "`1 <= weights[i] <= 100`", "`1 <= values[i] <= 1000`", "`1 <= capacity <= 1000`"]),
        mk("unbounded-knapsack", "Unbounded Knapsack", "MEDIUM", ["dynamic-programming"],
           [("weights", "int[]"), ("values", "int[]"), ("capacity", "int")], "int", unbounded, c_knapsack(True),
           "Like the 0/1 knapsack, but every item can be taken any number of times. Return the maximum total value "
           "whose weight does not exceed `capacity`.",
           "Line 1: `n`.\nLine 2: `n` weights.\nLine 3: `n`.\nLine 4: `n` values.\nLine 5: `capacity`.",
           "The maximum value.", ["`1 <= n <= 100`", "`1 <= weights[i] <= 100`", "`1 <= values[i] <= 1000`", "`1 <= capacity <= 1000`"]),
        mk("rod-cutting", "Rod Cutting", "MEDIUM", ["dynamic-programming"], [("price", "int[]")], "int", rod, c_rod(),
           "A rod has length `n`, and a piece of length `i + 1` sells for `price[i]`. Cut the rod into any number of "
           "whole-length pieces and return the maximum total price.", "Line 1: `n`.\nLine 2: `n` prices.",
           "The maximum total price.", ["`1 <= n <= 100`", "`1 <= price[i] <= 1000`"]),
        mk("matrix-chain-multiplication", "Matrix Chain Multiplication", "HARD", ["dynamic-programming"],
           [("dims", "int[]")], "int", matrix_chain, c_chain(),
           "Matrix `i` has `dims[i - 1]` rows and `dims[i]` columns, for `i = 1 .. n - 1`. Multiplying an `a x b` matrix "
           "by a `b x c` matrix costs `a * b * c`. Return the minimum total cost of multiplying the whole chain, "
           "choosing the best order of brackets.", "Line 1: `n`, the length of `dims`.\nLine 2: `n` integers.",
           "The minimum number of scalar multiplications.", ["`2 <= n <= 100`", "`1 <= dims[i] <= 100`"]),
        mk("palindrome-partitioning-ii", "Palindrome Partitioning II", "HARD", ["string", "dynamic-programming"],
           [("s", "str")], "int", min_cuts, c_cuts(),
           "Cut `s` into pieces so that every piece is a palindrome. Return the minimum number of cuts needed.",
           "Line 1: `s`.", "The minimum number of cuts.", ["`1 <= s.length <= 1000`", "Lowercase English letters"]),
        mk("minimum-bit-flips-to-convert-number", "Minimum Bit Flips to Convert Number", "EASY", ["bit-manipulation"],
           [("start", "int"), ("goal", "int")], "int", bit_flips, c_bits(),
           "A bit flip turns one bit of a number from `0` to `1` or from `1` to `0`. Return the minimum number of flips "
           "needed to turn `start` into `goal`.", "Line 1: `start`.\nLine 2: `goal`.", "The number of flips.",
           ["`0 <= start, goal <= 2^31 - 1`"]),
    ]
    return batch
