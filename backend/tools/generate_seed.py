#!/usr/bin/env python3
"""Generates backend/src/main/resources/seed/problems.json.

Expected outputs come from the reference solutions below, so test data is correct by construction.
Run from anywhere:  python3 backend/tools/generate_seed.py
"""
import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src/main/resources/seed/problems.json"
rng = random.Random(20261115)

# ---------------------------------------------------------------- I/O helpers
# Param types: int, str, int[], int[][], grid (list of strings).
# Return types: int, bool, int[], int[][].


def fmt_input(params, args):
    lines = []
    for (_, typ), val in zip(params, args):
        if typ == "int":
            lines.append(str(val))
        elif typ == "str":
            lines.append(val)
        elif typ == "int[]":
            lines.append(str(len(val)))
            lines.append(" ".join(map(str, val)))
        elif typ == "int[][]":
            lines.append(str(len(val)))
            lines.extend(" ".join(map(str, row)) for row in val)
        elif typ == "grid":
            lines.append(f"{len(val)} {len(val[0])}")
            lines.extend(val)
        else:
            raise ValueError(typ)
    return "\n".join(lines) + "\n"


def fmt_output(ret, val):
    if ret == "int":
        return f"{val}\n"
    if ret == "bool":
        return ("true" if val else "false") + "\n"
    if ret == "int[]":
        return " ".join(map(str, val)) + "\n"
    if ret == "int[][]":
        return "\n".join(" ".join(map(str, r)) for r in val) + "\n"
    raise ValueError(ret)


# ------------------------------------------------------------ starter code
def cap(name):
    return name[0].upper() + name[1:]


def starter_python(params, ret):
    names = ", ".join(n for n, _ in params)
    body = ["import sys", "", "", f"def solve({names}):", "    # Write your solution here", "    pass", "", "", "def main():",
            "    lines = sys.stdin.read().splitlines()", "    pos = 0"]
    for n, t in params:
        if t == "int":
            body += [f"    {n} = int(lines[pos]); pos += 1"]
        elif t == "str":
            body += [f"    {n} = lines[pos]; pos += 1"]
        elif t == "int[]":
            body += [f"    {n}_len = int(lines[pos]); pos += 1",
                     f"    {n} = list(map(int, lines[pos].split())) if {n}_len > 0 else []; pos += 1"]
        elif t == "int[][]":
            body += [f"    {n}_len = int(lines[pos]); pos += 1",
                     f"    {n} = [list(map(int, lines[pos + i].split())) for i in range({n}_len)]; pos += {n}_len"]
        elif t == "grid":
            body += [f"    {n}_rows = int(lines[pos].split()[0]); pos += 1",
                     f"    {n} = lines[pos:pos + {n}_rows]; pos += {n}_rows"]
    body += [f"    result = solve({names})"]
    body += {
        "int": ["    print(result)"],
        "bool": ['    print("true" if result else "false")'],
        "int[]": ['    print(" ".join(map(str, result)))'],
        "int[][]": ["    for row in result:", '        print(" ".join(map(str, row)))'],
    }[ret]
    body += ["", "", 'if __name__ == "__main__":', "    main()", ""]
    return "\n".join(body)


JAVA_T = {"int": "int", "str": "String", "int[]": "int[]", "int[][]": "int[][]", "grid": "String[]"}
JAVA_RET = {"int": "int", "bool": "boolean", "int[]": "int[]", "int[][]": "int[][]"}
JAVA_DEFAULT = {"int": "0", "bool": "false", "int[]": "new int[0]", "int[][]": "new int[0][]"}


def starter_java(params, ret):
    sig = ", ".join(f"{JAVA_T[t]} {n}" for n, t in params)
    names = ", ".join(n for n, _ in params)
    out = ["import java.io.*;", "import java.util.*;", "import java.util.stream.*;", "", "public class Main {",
           f"    static {JAVA_RET[ret]} solve({sig}) {{", "        // Write your solution here",
           f"        return {JAVA_DEFAULT[ret]};", "    }", "",
           "    public static void main(String[] args) throws IOException {",
           "        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));",
           "        List<String> lines = new ArrayList<>();", "        String line;",
           "        while ((line = br.readLine()) != null) lines.add(line);", "        int pos = 0;"]
    for n, t in params:
        if t == "int":
            out += [f"        int {n} = Integer.parseInt(lines.get(pos++).trim());"]
        elif t == "str":
            out += [f"        String {n} = lines.get(pos++);"]
        elif t == "int[]":
            out += [f"        int {n}Len = Integer.parseInt(lines.get(pos++).trim());",
                    f"        int[] {n} = new int[{n}Len];",
                    f"        if ({n}Len > 0) {{",
                    f"            StringTokenizer st = new StringTokenizer(lines.get(pos));",
                    f"            for (int i = 0; i < {n}Len; i++) {n}[i] = Integer.parseInt(st.nextToken());",
                    "        }", "        pos++;"]
        elif t == "int[][]":
            out += [f"        int {n}Len = Integer.parseInt(lines.get(pos++).trim());",
                    f"        int[][] {n} = new int[{n}Len][2];",
                    f"        for (int i = 0; i < {n}Len; i++) {{",
                    "            StringTokenizer st = new StringTokenizer(lines.get(pos++));",
                    f"            {n}[i][0] = Integer.parseInt(st.nextToken());",
                    f"            {n}[i][1] = Integer.parseInt(st.nextToken());", "        }"]
        elif t == "grid":
            out += [f"        int {n}Rows = Integer.parseInt(new StringTokenizer(lines.get(pos++)).nextToken());",
                    f"        String[] {n} = new String[{n}Rows];",
                    f"        for (int i = 0; i < {n}Rows; i++) {n}[i] = lines.get(pos++);"]
    out += [f"        {JAVA_RET[ret]} result = solve({names});"]
    out += {
        "int": ["        System.out.println(result);"],
        "bool": ["        System.out.println(result);"],
        "int[]": ['        System.out.println(Arrays.stream(result).mapToObj(String::valueOf).collect(Collectors.joining(" ")));'],
        "int[][]": ["        for (int[] row : result) {",
                    '            System.out.println(row[0] + " " + row[1]);', "        }"],
    }[ret]
    out += ["    }", "}", ""]
    return "\n".join(out)


def starter_js(params, ret):
    names = ", ".join(n for n, _ in params)
    out = ['const lines = require("fs").readFileSync(0, "utf8").split("\\n").map((l) => l.replace(/\\r$/, ""));',
           "let pos = 0;", "", f"function solve({names}) {{", "  // Write your solution here", "}", ""]
    for n, t in params:
        if t == "int":
            out += [f"const {n} = parseInt(lines[pos++], 10);"]
        elif t == "str":
            out += [f"const {n} = lines[pos++];"]
        elif t == "int[]":
            out += [f"const {n}Len = parseInt(lines[pos++], 10);",
                    f"const {n} = {n}Len > 0 ? lines[pos].trim().split(/\\s+/).map(Number) : [];", "pos++;"]
        elif t == "int[][]":
            out += [f"const {n}Len = parseInt(lines[pos++], 10);", f"const {n} = [];",
                    f"for (let i = 0; i < {n}Len; i++) {n}.push(lines[pos++].trim().split(/\\s+/).map(Number));"]
        elif t == "grid":
            out += [f"const {n}Rows = parseInt(lines[pos++].trim().split(/\\s+/)[0], 10);",
                    f"const {n} = lines.slice(pos, pos + {n}Rows);", f"pos += {n}Rows;"]
    out += [f"const result = solve({names});"]
    out += {
        "int": ["console.log(String(result));"],
        "bool": ['console.log(result ? "true" : "false");'],
        "int[]": ['console.log(result.join(" "));'],
        "int[][]": ['console.log(result.map((r) => r.join(" ")).join("\\n"));'],
    }[ret]
    out += [""]
    return "\n".join(out)


CPP_T = {"int": "int", "str": "string", "int[]": "vector<int>", "int[][]": "vector<vector<int>>", "grid": "vector<string>"}
CPP_RET = {"int": "int", "bool": "bool", "int[]": "vector<int>", "int[][]": "vector<vector<int>>"}
CPP_DEFAULT = {"int": "0", "bool": "false", "int[]": "{}", "int[][]": "{}"}


def starter_cpp(params, ret):
    sig = ", ".join(f"{CPP_T[t]} {n}" for n, t in params)
    names = ", ".join(n for n, _ in params)
    out = ["#include <bits/stdc++.h>", "using namespace std;", "",
           f"{CPP_RET[ret]} solve({sig}) {{", "    // Write your solution here", f"    return {CPP_DEFAULT[ret]};", "}", "",
           "int main() {", "    ios::sync_with_stdio(false);", "    cin.tie(nullptr);",
           "    vector<string> lines;", "    string line;",
           "    while (getline(cin, line)) {",
           "        if (!line.empty() && line.back() == '\\r') line.pop_back();",
           "        lines.push_back(line);", "    }", "    size_t pos = 0;"]
    for n, t in params:
        if t == "int":
            out += [f"    int {n} = stoi(lines[pos++]);"]
        elif t == "str":
            out += [f"    string {n} = lines[pos++];"]
        elif t == "int[]":
            out += [f"    int {n}Len = stoi(lines[pos++]);", f"    vector<int> {n}({n}Len);",
                    f"    if ({n}Len > 0) {{", "        istringstream iss(lines[pos]);",
                    f"        for (auto &v : {n}) iss >> v;", "    }", "    pos++;"]
        elif t == "int[][]":
            out += [f"    int {n}Len = stoi(lines[pos++]);",
                    f"    vector<vector<int>> {n}({n}Len, vector<int>(2));",
                    f"    for (int i = 0; i < {n}Len; i++) {{", "        istringstream iss(lines[pos++]);",
                    f"        iss >> {n}[i][0] >> {n}[i][1];", "    }"]
        elif t == "grid":
            out += [f"    int {n}Rows = stoi(lines[pos++]);",
                    f"    vector<string> {n}(lines.begin() + pos, lines.begin() + pos + {n}Rows);",
                    f"    pos += {n}Rows;"]
    out += [f"    {CPP_RET[ret]} result = solve({names});"]
    out += {
        "int": ['    cout << result << "\\n";'],
        "bool": ['    cout << (result ? "true" : "false") << "\\n";'],
        "int[]": ["    for (size_t i = 0; i < result.size(); i++) {",
                  '        if (i) cout << " ";', "        cout << result[i];", "    }", '    cout << "\\n";'],
        "int[][]": ["    for (auto &row : result) {", '        cout << row[0] << " " << row[1] << "\\n";', "    }"],
    }[ret]
    out += ["    return 0;", "}", ""]
    return "\n".join(out)


def starters(params, ret):
    return {
        "java": starter_java(params, ret),
        "python": starter_python(params, ret),
        "javascript": starter_js(params, ret),
        "cpp": starter_cpp(params, ret),
    }


# --------------------------------------------------------- reference solutions
def two_sum(nums, target):
    hits = [(i, j) for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] + nums[j] == target]
    assert len(hits) == 1, "two-sum cases must have exactly one answer"
    return list(hits[0])


def valid_parentheses(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack


def palindrome_number(x):
    return x >= 0 and str(x) == str(x)[::-1]


def max_subarray(nums):
    best = cur = nums[0]
    for v in nums[1:]:
        cur = max(v, cur + v)
        best = max(best, cur)
    return best


def best_time(prices):
    lo, best = prices[0], 0
    for p in prices[1:]:
        best = max(best, p - lo)
        lo = min(lo, p)
    return best


def climb(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def contains_duplicate(nums):
    return len(set(nums)) != len(nums)


def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def longest_substring(s):
    seen, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1
        seen[ch] = right
        best = max(best, right - left + 1)
    return best


def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    pre = 1
    for i in range(n):
        out[i] = pre
        pre *= nums[i]
    suf = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suf
        suf *= nums[i]
    return out


def coin_change(coins, amount):
    inf = amount + 1
    dp = [0] + [inf] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != inf else -1


def trap(height):
    lo, hi = 0, len(height) - 1
    lmax = rmax = water = 0
    while lo < hi:
        if height[lo] < height[hi]:
            lmax = max(lmax, height[lo])
            water += lmax - height[lo]
            lo += 1
        else:
            rmax = max(rmax, height[hi])
            water += rmax - height[hi]
            hi -= 1
    return water


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return prev[len(b)]


def merge_intervals(intervals):
    merged = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged


def num_islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count += 1
                stack = [(r, c)]
                seen.add((r, c))
                while stack:
                    y, x = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == "1" and (ny, nx) not in seen:
                            seen.add((ny, nx))
                            stack.append((ny, nx))
    return count


# ------------------------------------------------------------ case generators
def rand_arr(n, lo, hi):
    return [rng.randint(lo, hi) for _ in range(n)]


def two_sum_cases():
    cases = [([2, 7, 11, 15], 9), ([3, 2, 4], 6), ([3, 3], 6), ([-1, -2, -3, -4, -5], -8), ([0, 4, 3, 0], 0)]
    while len(cases) < 9:
        n = rng.choice([10, 50, 200])
        nums = rng.sample(range(-5000, 5000), n)
        i, j = sorted(rng.sample(range(n), 2))
        target = nums[i] + nums[j]
        try:
            two_sum(nums, target)
        except AssertionError:
            continue
        cases.append((nums, target))
    return cases


def paren_cases():
    cases = ["()", "()[]{}", "(]", "([)]", "{[]}", "(", "]", "((((((((((()))))))))))"]
    for _ in range(4):
        n = rng.choice([20, 100, 500])
        cases.append("".join(rng.choice("()[]{}") for _ in range(n)))
    # balanced long case
    stack, out = [], []
    pairs = {"(": ")", "[": "]", "{": "}"}
    for _ in range(300):
        if stack and rng.random() < 0.5:
            out.append(pairs[stack.pop()])
        else:
            o = rng.choice("([{")
            stack.append(o)
            out.append(o)
    while stack:
        out.append(pairs[stack.pop()])
    cases.append("".join(out))
    return cases


def sorted_unique(n, lo, hi):
    return sorted(rng.sample(range(lo, hi), n))


def bs_cases():
    cases = [([-1, 0, 3, 5, 9, 12], 9), ([-1, 0, 3, 5, 9, 12], 2), ([5], 5), ([5], -5), ([1, 3], 3)]
    for _ in range(5):
        arr = sorted_unique(rng.choice([50, 500, 1000]), -10**5, 10**5)
        cases.append((arr, rng.choice(arr)))
    cases.append((sorted_unique(500, -10**5, 10**5), 10**5 + 7))
    return cases


def lss_cases():
    cases = ["abcabcbb", "bbbbb", "pwwkew", "a", "au", "dvdf", "abba", "tmmzuxt"]
    for _ in range(4):
        cases.append("".join(rng.choice("abcdefgh ") for _ in range(rng.choice([30, 300, 1000]))))
    return cases


def coin_cases():
    cases = [([1, 2, 5], 11), ([2], 3), ([1], 0), ([186, 419, 83, 408], 6249), ([2, 5, 10, 1], 27)]
    for _ in range(4):
        coins = rng.sample(range(1, 60), rng.randint(1, 6))
        cases.append((coins, rng.randint(0, 2000)))
    return cases


def edit_cases():
    cases = [("horse", "ros"), ("intention", "execution"), ("a", "b"), ("abc", "abc"), ("kitten", "sitting")]
    for _ in range(4):
        a = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 120)))
        b = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 120)))
        cases.append((a, b))
    return cases


def interval_cases():
    cases = [[[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 4], [4, 5]], [[1, 4], [0, 4]], [[5, 6]], [[1, 10], [2, 3], [4, 5]]]
    for _ in range(4):
        n = rng.choice([10, 60, 200])
        arr = []
        for _ in range(n):
            s = rng.randint(0, 1000)
            arr.append([s, s + rng.randint(0, 25)])
        cases.append(arr)
    return cases


def grid_cases():
    cases = [
        ["11110", "11010", "11000", "00000"],
        ["11000", "11000", "00100", "00011"],
        ["1"],
        ["0"],
        ["101", "010", "101"],
    ]
    for _ in range(4):
        r, c = rng.choice([(10, 10), (30, 25), (50, 50)])
        cases.append(["".join("1" if rng.random() < 0.45 else "0" for _ in range(c)) for _ in range(r)])
    return cases


# ------------------------------------------------------------------ problems
def desc(summary, input_fmt, output_fmt, constraints, notes=""):
    parts = [summary.strip(), "", "### Input", input_fmt.strip(), "", "### Output", output_fmt.strip(), "",
             "### Constraints"]
    parts += [f"- {c}" for c in constraints]
    if notes:
        parts += ["", "### Notes", notes.strip()]
    return "\n".join(parts)


PROBLEMS = [
    dict(slug="two-sum", title="Two Sum", difficulty="EASY", tags=["array", "hash-table"],
         params=[("nums", "int[]"), ("target", "int")], ret="int[]", ref=two_sum, cases=two_sum_cases(),
         description=desc(
             "Given an array of integers `nums` and an integer `target`, find the two numbers that add up to `target`. "
             "Each input has **exactly one** solution and you may not use the same element twice.",
             "Line 1: `n`, the length of `nums`.\nLine 2: `n` space-separated integers.\nLine 3: `target`.",
             "The two indices, smaller first, separated by a space.",
             ["`2 <= n <= 200`", "`-10^4 <= nums[i], target <= 10^4`", "Exactly one valid pair exists"])),
    dict(slug="valid-parentheses", title="Valid Parentheses", difficulty="EASY", tags=["string", "stack"],
         params=[("s", "str")], ret="bool", ref=valid_parentheses, cases=paren_cases(),
         description=desc(
             "Given a string `s` containing only `()[]{}`, determine whether it is valid. Brackets must close in the "
             "correct order and every close bracket needs a matching open bracket of the same type.",
             "A single line containing the string `s`.", "`true` if `s` is valid, otherwise `false`.",
             ["`1 <= s.length <= 1000`", "`s` consists only of `()[]{}`"])),
    dict(slug="palindrome-number", title="Palindrome Number", difficulty="EASY", tags=["math"],
         params=[("x", "int")], ret="bool", ref=palindrome_number,
         cases=[121, -121, 10, 0, 7, 1221, 12321, 123456789, 1000000001, -1, 2147447412, 100],
         description=desc(
             "Given an integer `x`, return whether it reads the same backward as forward. Negative numbers are never "
             "palindromes.",
             "A single integer `x`.", "`true` or `false`.", ["`-2^31 <= x <= 2^31 - 1`"])),
    dict(slug="maximum-subarray", title="Maximum Subarray", difficulty="MEDIUM", tags=["array", "dynamic-programming"],
         params=[("nums", "int[]")], ret="int", ref=max_subarray,
         cases=[[-2, 1, -3, 4, -1, 2, 1, -5, 4], [1], [5, 4, -1, 7, 8], [-3, -2, -1], [0, 0, 0],
                rand_arr(20, -50, 50), rand_arr(500, -100, 100), rand_arr(1000, -1000, 1000), [-1, 2], [2, -1, 2]],
         description=desc(
             "Find the contiguous, non-empty subarray with the largest sum and return that sum.",
             "Line 1: `n`.\nLine 2: `n` space-separated integers.", "The maximum subarray sum.",
             ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"])),
    dict(slug="best-time-to-buy-and-sell-stock", title="Best Time to Buy and Sell Stock", difficulty="EASY",
         tags=["array", "dynamic-programming"], params=[("prices", "int[]")], ret="int", ref=best_time,
         cases=[[7, 1, 5, 3, 6, 4], [7, 6, 4, 3, 1], [1], [2, 4, 1], [3, 2, 6, 5, 0, 3],
                rand_arr(100, 0, 1000), rand_arr(1000, 0, 10000), sorted(rand_arr(50, 0, 500)),
                sorted(rand_arr(50, 0, 500), reverse=True)],
         description=desc(
             "`prices[i]` is the price of a stock on day `i`. Buy on one day and sell on a later day to maximise profit. "
             "Return the maximum profit, or `0` if no profit is possible.",
             "Line 1: `n`.\nLine 2: `n` space-separated prices.", "The maximum profit.",
             ["`1 <= n <= 1000`", "`0 <= prices[i] <= 10^4`"])),
    dict(slug="climbing-stairs", title="Climbing Stairs", difficulty="EASY", tags=["math", "dynamic-programming"],
         params=[("n", "int")], ret="int", ref=climb, cases=[2, 3, 1, 4, 5, 10, 20, 30, 44, 45],
         description=desc(
             "You are climbing a staircase with `n` steps. Each move climbs 1 or 2 steps. "
             "How many distinct ways can you reach the top?",
             "A single integer `n`.", "The number of distinct ways.", ["`1 <= n <= 45`"])),
    dict(slug="contains-duplicate", title="Contains Duplicate", difficulty="EASY", tags=["array", "hash-table"],
         params=[("nums", "int[]")], ret="bool", ref=contains_duplicate,
         cases=[[1, 2, 3, 1], [1, 2, 3, 4], [1, 1, 1, 3, 3, 4, 3, 2, 4, 2], [7], [0, 0],
                rng.sample(range(-10**5, 10**5), 500), rand_arr(500, -10**5, 10**5), [-1, -1]],
         description=desc(
             "Return `true` if any value appears at least twice in the array, otherwise `false`.",
             "Line 1: `n`.\nLine 2: `n` space-separated integers.", "`true` or `false`.",
             ["`1 <= n <= 1000`", "`-10^9 <= nums[i] <= 10^9`"])),
    dict(slug="binary-search", title="Binary Search", difficulty="EASY", tags=["array", "binary-search"],
         params=[("nums", "int[]"), ("target", "int")], ret="int", ref=binary_search, cases=bs_cases(),
         description=desc(
             "Given a sorted array of distinct integers and a `target`, return the index of `target` or `-1` if it is "
             "not present. Your algorithm should run in `O(log n)`.",
             "Line 1: `n`.\nLine 2: `n` ascending space-separated integers.\nLine 3: `target`.",
             "The index of `target`, or `-1`.", ["`1 <= n <= 1000`", "All values are distinct and sorted ascending"])),
    dict(slug="longest-substring-without-repeating-characters", title="Longest Substring Without Repeating Characters",
         difficulty="MEDIUM", tags=["string", "sliding-window", "hash-table"], params=[("s", "str")], ret="int",
         ref=longest_substring, cases=lss_cases(),
         description=desc(
             "Return the length of the longest substring of `s` that contains no repeated characters.",
             "A single line containing `s` (it may contain spaces).", "The length of the longest such substring.",
             ["`1 <= s.length <= 1000`", "`s` contains letters and spaces"])),
    dict(slug="product-of-array-except-self", title="Product of Array Except Self", difficulty="MEDIUM",
         tags=["array", "prefix-sum"], params=[("nums", "int[]")], ret="int[]", ref=product_except_self,
         cases=[[1, 2, 3, 4], [-1, 1, 0, -3, 3], [2, 3], [0, 0], [5, 0, 2], rand_arr(8, -5, 5), rand_arr(10, -3, 3),
                [1] * 20, rand_arr(9, 1, 9)],
         description=desc(
             "Return an array `answer` where `answer[i]` is the product of every element of `nums` except `nums[i]`. "
             "Do it without using division, in `O(n)` time. The product always fits in a 32-bit signed integer.",
             "Line 1: `n`.\nLine 2: `n` space-separated integers.", "`n` space-separated integers.",
             ["`2 <= n <= 20`", "`-30 <= nums[i] <= 30`", "Every prefix/suffix product fits in a 32-bit integer"])),
    dict(slug="coin-change", title="Coin Change", difficulty="MEDIUM", tags=["dynamic-programming"],
         params=[("coins", "int[]"), ("amount", "int")], ret="int", ref=coin_change, cases=coin_cases(),
         description=desc(
             "Given coin denominations and a target `amount`, return the fewest coins needed to make that amount, or "
             "`-1` if it is impossible. You have an unlimited supply of each coin.",
             "Line 1: number of coin types.\nLine 2: the coin values.\nLine 3: `amount`.",
             "The minimum number of coins, or `-1`.",
             ["`1 <= coins.length <= 12`", "`1 <= coins[i] <= 10^4`", "`0 <= amount <= 10^4`"])),
    dict(slug="merge-intervals", title="Merge Intervals", difficulty="MEDIUM", tags=["array", "sorting"],
         params=[("intervals", "int[][]")], ret="int[][]", ref=merge_intervals, cases=interval_cases(),
         description=desc(
             "Merge all overlapping intervals (touching intervals such as `[1,4]` and `[4,5]` overlap) and return the "
             "non-overlapping intervals that cover the input, sorted by start.",
             "Line 1: `n`, the number of intervals.\nNext `n` lines: `start end`.",
             "The merged intervals, one `start end` pair per line, sorted by start.",
             ["`1 <= n <= 200`", "`0 <= start <= end <= 10^4`"])),
    dict(slug="number-of-islands", title="Number of Islands", difficulty="MEDIUM", tags=["matrix", "graph"],
         params=[("grid", "grid")], ret="int", ref=num_islands, cases=grid_cases(),
         description=desc(
             "Given a grid of `1` (land) and `0` (water), count the islands. An island is a group of land cells "
             "connected horizontally or vertically.",
             "Line 1: `rows cols`.\nNext `rows` lines: a string of `cols` characters, each `0` or `1`.",
             "The number of islands.", ["`1 <= rows, cols <= 50`"])),
    dict(slug="trapping-rain-water", title="Trapping Rain Water", difficulty="HARD",
         tags=["array", "two-pointers", "stack"], params=[("height", "int[]")], ret="int", ref=trap,
         cases=[[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], [4, 2, 0, 3, 2, 5], [1], [3, 3, 3], [5, 4, 3, 2, 1],
                rand_arr(30, 0, 20), rand_arr(500, 0, 300), rand_arr(1000, 0, 10000), [2, 0, 2]],
         description=desc(
             "Given `n` non-negative integers representing an elevation map where each bar has width 1, compute how "
             "much water it can trap after raining.",
             "Line 1: `n`.\nLine 2: `n` space-separated heights.", "The total units of trapped water.",
             ["`1 <= n <= 1000`", "`0 <= height[i] <= 10^4`"])),
    dict(slug="edit-distance", title="Edit Distance", difficulty="HARD", tags=["string", "dynamic-programming"],
         params=[("word1", "str"), ("word2", "str")], ret="int", ref=edit_distance, cases=edit_cases(),
         description=desc(
             "Return the minimum number of operations to convert `word1` into `word2`. Allowed operations are insert a "
             "character, delete a character, or replace a character.",
             "Line 1: `word1`.\nLine 2: `word2`.", "The minimum number of operations.",
             ["`1 <= word1.length, word2.length <= 120`", "Lowercase English letters"])),
]


def to_seed(problem):
    params, ret, ref = problem["params"], problem["ret"], problem["ref"]
    tests = []
    for i, case in enumerate(problem["cases"]):
        args = case if isinstance(case, tuple) else (case,)
        if isinstance(case, list) and len(params) == 1:
            args = (case,)
        tests.append({
            "input": fmt_input(params, args),
            "expectedOutput": fmt_output(ret, ref(*args)),
            "sample": i < 2,
        })
    samples = [t for t in tests if t["sample"]]
    examples = ["", "### Examples"]
    for n, t in enumerate(samples, 1):
        examples += [f"**Example {n}**", "```text", "Input:", t["input"].rstrip("\n"), "", "Output:",
                     t["expectedOutput"].rstrip("\n"), "```", ""]
    return {
        "slug": problem["slug"],
        "title": problem["title"],
        "difficulty": problem["difficulty"],
        "tags": problem["tags"],
        "description": problem["description"] + "\n" + "\n".join(examples).rstrip() + "\n",
        "starterCode": starters(params, ret),
        "testCases": tests,
    }


def main():
    seed = [to_seed(p) for p in PROBLEMS]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(len(p["testCases"]) for p in seed)
    print(f"Wrote {len(seed)} problems, {total} test cases -> {OUT}")


if __name__ == "__main__":
    main()
