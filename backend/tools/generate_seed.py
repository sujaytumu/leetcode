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


# ------------------------------------------------------------ batch 2 problems
# Appended after the original 15 so their random test data is unchanged.
import bisect
import heapq
import math


def single_number(nums):
    r = 0
    for x in nums:
        r ^= x
    return r


def majority_element(nums):
    cand, cnt = None, 0
    for x in nums:
        if cnt == 0:
            cand = x
        cnt += 1 if x == cand else -1
    return cand


def missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)


def valid_anagram(a, b):
    return sorted(a) == sorted(b)


def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def find_min_rotated(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


def container(height):
    l, r, best = 0, len(height) - 1, 0
    while l < r:
        best = max(best, min(height[l], height[r]) * (r - l))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best


def house_robber(nums):
    a = b = 0
    for x in nums:
        a, b = b, max(b, a + x)
    return b


def lis(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def jump_game(nums):
    far = 0
    for i, x in enumerate(nums):
        if i > far:
            return False
        far = max(far, i + x)
    return True


def unique_paths(m, n):
    return math.comb(m + n - 2, m - 1)


def daily_temperatures(t):
    res = [0] * len(t)
    st = []
    for i, x in enumerate(t):
        while st and t[st[-1]] < x:
            j = st.pop()
            res[j] = i - j
        st.append(i)
    return res


def subarray_sum_k(nums, k):
    seen = {0: 1}
    s = cnt = 0
    for x in nums:
        s += x
        cnt += seen.get(s - k, 0)
        seen[s] = seen.get(s, 0) + 1
    return cnt


def kth_largest(nums, k):
    return heapq.nlargest(k, nums)[-1]


def max_product(nums):
    best = hi = lo = nums[0]
    for x in nums[1:]:
        cands = (x, hi * x, lo * x)
        hi, lo = max(cands), min(cands)
        best = max(best, hi)
    return best


def longest_pal_len(s):
    best = 0
    for c in range(len(s)):
        for l, r in ((c, c), (c, c + 1)):
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            best = max(best, r - l - 1)
    return best


def min_cost_stairs(cost):
    a = b = 0
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b


def count_primes(n):
    if n < 3:
        return 0
    sieve = bytearray([1]) * n
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return sum(sieve)


def isqrt_floor(x):
    return math.isqrt(x)


def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            dp[i][j] = dp[i + 1][j + 1] + 1 if a[i] == b[j] else max(dp[i + 1][j], dp[i][j + 1])
    return dp[0][0]


def partition_equal(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    reach = 1
    for x in nums:
        reach |= reach << x
    return bool((reach >> target) & 1)


def search_insert(nums, target):
    return bisect.bisect_left(nums, target)


def first_missing_positive(nums):
    s = set(nums)
    i = 1
    while i in s:
        i += 1
    return i


def largest_rect(h):
    st, best = [], 0
    for i, x in enumerate(h + [0]):
        start = i
        while st and st[-1][1] >= x:
            idx, hh = st.pop()
            best = max(best, hh * (i - idx))
            start = idx
        st.append((start, x))
    return best


def rotate_sorted(arr, k):
    k %= len(arr)
    return arr[k:] + arr[:k]


def single_cases():
    cases = [[2, 2, 1], [4, 1, 2, 1, 2], [1], [-1, -1, -2], [0, 7, 7]]
    for n in (5, 50, 300, 999):
        vals = rng.sample(range(-10**4, 10**4), n // 2 + 1)
        arr = [v for v in vals[1:] for _ in (0, 1)] + [vals[0]]
        rng.shuffle(arr)
        cases.append(arr)
    return cases


def majority_cases():
    cases = [[3, 2, 3], [2, 2, 1, 1, 1, 2, 2], [5], [1, 1], [7, 7, 7, 1, 2]]
    for n in (11, 101, 501, 999):
        m = rng.randint(-100, 100)
        arr = [m] * (n // 2 + 1) + [rng.randint(-100, 100) for _ in range(n - n // 2 - 1)]
        rng.shuffle(arr)
        cases.append(arr)
    return cases


def missing_cases():
    cases = [[3, 0, 1], [0, 1], [9, 6, 4, 2, 3, 5, 7, 0, 1], [0], [1]]
    for n in (10, 100, 500, 1000):
        arr = list(range(n + 1))
        arr.pop(rng.randrange(len(arr)))
        rng.shuffle(arr)
        cases.append(arr)
    return cases


def anagram_cases():
    cases = [("anagram", "nagaram"), ("rat", "car"), ("a", "a"), ("ab", "a"), ("listen", "silent")]
    for n in (10, 100, 800):
        a = [rng.choice("abcdefghij") for _ in range(n)]
        b = a[:]
        rng.shuffle(b)
        cases.append(("".join(a), "".join(b)))
        c = b[:]
        c[0] = "z" if c[0] != "z" else "y"
        cases.append(("".join(a), "".join(c)))
    return cases


def rotated_array(n, lo=-10**4, hi=10**4):
    arr = sorted(rng.sample(range(lo, hi), n))
    return rotate_sorted(arr, rng.randrange(n))


def search_rot_cases():
    cases = [([4, 5, 6, 7, 0, 1, 2], 0), ([4, 5, 6, 7, 0, 1, 2], 3), ([1], 0), ([1], 1), ([3, 1], 1)]
    for n in (10, 100, 1000):
        arr = rotated_array(n)
        cases.append((arr, rng.choice(arr)))
        cases.append((arr, 10**4 + 5))
    return cases


def min_rot_cases():
    cases = [[3, 4, 5, 1, 2], [4, 5, 6, 7, 0, 1, 2], [11, 13, 15, 17], [2, 1], [5]]
    for n in (10, 100, 1000):
        cases.append(rotated_array(n))
    return cases


def temp_cases():
    cases = [[73, 74, 75, 71, 69, 72, 76, 73], [30, 40, 50, 60], [30, 60, 90], [50], [90, 80, 70]]
    for n in (20, 200, 1000):
        cases.append(rand_arr(n, 30, 100))
    return cases


def subsum_cases():
    cases = [([1, 1, 1], 2), ([1, 2, 3], 3), ([1], 0), ([0, 0, 0], 0), ([-1, -1, 1], 0)]
    for n in (20, 200, 1000):
        arr = rand_arr(n, -10, 10)
        cases.append((arr, rng.randint(-20, 20)))
    return cases


def kth_cases():
    cases = [([3, 2, 1, 5, 6, 4], 2), ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), ([1], 1), ([2, 1], 2), ([5, 5, 5], 3)]
    for n in (20, 200, 1000):
        arr = rand_arr(n, -10**4, 10**4)
        cases.append((arr, rng.randint(1, n)))
    return cases


def maxprod_cases():
    cases = [[2, 3, -2, 4], [-2, 0, -1], [-2], [0, 2], [-2, 3, -4], [2, -5, -2, -4, 3]]
    for n in (8, 15, 20):
        while True:
            arr = rand_arr(n, -2, 3)
            if max(abs(max_product(arr)), 0) < 2**31:
                cases.append(arr)
                break
    return cases


def pal_cases():
    cases = ["babad", "cbbd", "a", "ac", "racecar", "abacdfgdcaba"]
    for n in (30, 200, 600):
        cases.append("".join(rng.choice("ab") for _ in range(n)))
    return cases


def cost_cases():
    cases = [[10, 15, 20], [1, 100, 1, 1, 1, 100, 1, 1, 100, 1], [0, 0], [5, 5], [1, 2, 3]]
    for n in (10, 100, 1000):
        cases.append(rand_arr(n, 0, 999))
    return cases


def lcs_cases():
    cases = [("abcde", "ace"), ("abc", "abc"), ("abc", "def"), ("a", "a"), ("bl", "yby")]
    for n, m in ((20, 25), (100, 80), (300, 300)):
        cases.append(("".join(rng.choice("abcd") for _ in range(n)), "".join(rng.choice("abcd") for _ in range(m))))
    return cases


def partition_cases():
    cases = [[1, 5, 11, 5], [1, 2, 3, 5], [1, 1], [2], [3, 3, 3, 4, 5]]
    for n in (10, 40, 100):
        cases.append(rand_arr(n, 1, 100))
    cases.append([rng.randint(1, 50) * 2 for _ in range(60)])
    return cases


def insert_cases():
    cases = [([1, 3, 5, 6], 5), ([1, 3, 5, 6], 2), ([1, 3, 5, 6], 7), ([1, 3, 5, 6], 0), ([1], 1)]
    for n in (10, 200, 1000):
        arr = sorted_unique(n, -10**4, 10**4)
        cases.append((arr, rng.randint(-10**4 - 5, 10**4 + 5)))
    return cases


def firstmiss_cases():
    cases = [[1, 2, 0], [3, 4, -1, 1], [7, 8, 9, 11, 12], [1], [2], [1, 2, 3, 4, 5]]
    for n in (20, 200, 1000):
        arr = list(range(1, n + 1))
        arr.pop(rng.randrange(n))
        arr += rand_arr(10, -50, 0)
        rng.shuffle(arr)
        cases.append(arr)
    return cases


def rect_cases():
    cases = [[2, 1, 5, 6, 2, 3], [2, 4], [1], [6, 5, 4, 3], [0, 0, 0], [2, 1, 2]]
    for n in (20, 200, 1000):
        cases.append(rand_arr(n, 0, 10000))
    return cases


def mk(slug, title, difficulty, tags, params, ret, ref, cases, summary, inp, outp, cons):
    return dict(slug=slug, title=title, difficulty=difficulty, tags=tags, params=params, ret=ret, ref=ref, cases=cases,
                description=desc(summary, inp, outp, cons))


ARR_IN = "Line 1: `n`.\nLine 2: `n` space-separated integers."

PROBLEMS += [
    mk("single-number", "Single Number", "EASY", ["array", "bit-manipulation"], [("nums", "int[]")], "int",
       single_number, single_cases(),
       "Every element appears exactly twice except one, which appears once. Return that single element. Aim for "
       "linear time and constant extra space.", ARR_IN, "The element that appears once.",
       ["`1 <= n <= 999`, `n` is odd", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("majority-element", "Majority Element", "EASY", ["array", "hash-table", "sorting"], [("nums", "int[]")], "int",
       majority_element, majority_cases(),
       "Return the element that appears more than `n / 2` times. It is guaranteed to exist.", ARR_IN,
       "The majority element.", ["`1 <= n <= 999`", "A majority element always exists"]),
    mk("missing-number", "Missing Number", "EASY", ["array", "math", "bit-manipulation"], [("nums", "int[]")], "int",
       missing_number, missing_cases(),
       "`nums` holds `n` distinct numbers from the range `[0, n]`. Return the one number in that range that is "
       "missing.", ARR_IN, "The missing number.", ["`1 <= n <= 1000`", "All values are distinct"]),
    mk("valid-anagram", "Valid Anagram", "EASY", ["string", "hash-table", "sorting"],
       [("s", "str"), ("t", "str")], "bool", valid_anagram, anagram_cases(),
       "Return `true` if `t` is an anagram of `s`, meaning it uses exactly the same letters with the same counts.",
       "Line 1: `s`.\nLine 2: `t`.", "`true` or `false`.",
       ["`1 <= s.length, t.length <= 1000`", "Lowercase English letters"]),
    mk("search-insert-position", "Search Insert Position", "EASY", ["array", "binary-search"],
       [("nums", "int[]"), ("target", "int")], "int", search_insert, insert_cases(),
       "Given a sorted array of distinct integers and a `target`, return the index of the target if present, "
       "otherwise the index where it would be inserted to keep the array sorted. Use `O(log n)` time.",
       "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `target`.", "The index.",
       ["`1 <= n <= 1000`", "`nums` is sorted ascending with distinct values"]),
    mk("sqrt-x", "Sqrt(x)", "EASY", ["math", "binary-search"], [("x", "int")], "int", isqrt_floor,
       [4, 8, 0, 1, 2, 15, 16, 99, 2147395599, 2147483647, 1000000, 46340 * 46340],
       "Return the square root of `x` rounded down to the nearest integer, without using a built-in power or root "
       "function.", "A single integer `x`.", "`floor(sqrt(x))`.", ["`0 <= x <= 2^31 - 1`"]),
    mk("count-primes", "Count Primes", "MEDIUM", ["math", "sieve"], [("n", "int")], "int", count_primes,
       [10, 0, 1, 2, 3, 20, 100, 1000, 4999, 5000, 97, 98],
       "Return the number of prime numbers that are strictly less than `n`.", "A single integer `n`.",
       "The count of primes below `n`.", ["`0 <= n <= 5000`"]),
    mk("find-minimum-in-rotated-sorted-array", "Find Minimum in Rotated Sorted Array", "MEDIUM",
       ["array", "binary-search"], [("nums", "int[]")], "int", find_min_rotated, min_rot_cases(),
       "A sorted array of distinct integers was rotated at an unknown pivot. Return its minimum element in "
       "`O(log n)` time.", ARR_IN, "The minimum element.", ["`1 <= n <= 1000`", "All values are distinct"]),
    mk("search-in-rotated-sorted-array", "Search in Rotated Sorted Array", "MEDIUM", ["array", "binary-search"],
       [("nums", "int[]"), ("target", "int")], "int", search_rotated, search_rot_cases(),
       "A sorted array of distinct integers was rotated at an unknown pivot. Return the index of `target`, or `-1` "
       "if it is absent. Use `O(log n)` time.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.",
       "The index of `target`, or `-1`.", ["`1 <= n <= 1000`", "All values are distinct"]),
    mk("container-with-most-water", "Container With Most Water", "MEDIUM", ["array", "two-pointers", "greedy"],
       [("height", "int[]")], "int", container,
       [[1, 8, 6, 2, 5, 4, 8, 3, 7], [1, 1], [4, 3, 2, 1, 4], [1, 2, 1], rand_arr(30, 0, 100), rand_arr(500, 0, 5000),
        rand_arr(1000, 0, 10000), [0, 0, 5, 0]],
       "Vertical lines stand at positions `0..n-1` with the given heights. Pick two lines that, together with the "
       "x-axis, hold the most water, and return that amount.", ARR_IN, "The maximum area.",
       ["`2 <= n <= 1000`", "`0 <= height[i] <= 10^4`"]),
    mk("house-robber", "House Robber", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]")], "int",
       house_robber,
       [[1, 2, 3, 1], [2, 7, 9, 3, 1], [5], [2, 1], [0, 0, 0], rand_arr(20, 0, 400), rand_arr(200, 0, 400),
        rand_arr(1000, 0, 400)],
       "Houses are in a row and each holds some money. Robbing two adjacent houses triggers an alarm. Return the "
       "maximum you can rob in one night.", ARR_IN, "The maximum amount.",
       ["`1 <= n <= 1000`", "`0 <= nums[i] <= 400`"]),
    mk("longest-increasing-subsequence", "Longest Increasing Subsequence", "MEDIUM",
       ["array", "binary-search", "dynamic-programming"], [("nums", "int[]")], "int", lis,
       [[10, 9, 2, 5, 3, 7, 101, 18], [0, 1, 0, 3, 2, 3], [7, 7, 7, 7], [1], sorted(rand_arr(30, -100, 100)),
        rand_arr(50, -100, 100), rand_arr(500, -10**4, 10**4), rand_arr(1000, -10**4, 10**4)],
       "Return the length of the longest strictly increasing subsequence of `nums`.", ARR_IN, "The length.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("jump-game", "Jump Game", "MEDIUM", ["array", "greedy", "dynamic-programming"], [("nums", "int[]")], "bool",
       jump_game,
       [[2, 3, 1, 1, 4], [3, 2, 1, 0, 4], [0], [1, 0], [2, 0, 0], rand_arr(30, 0, 3), rand_arr(500, 0, 2),
        rand_arr(1000, 0, 5), [0, 1]],
       "You start at index `0`; `nums[i]` is the maximum jump length from index `i`. Return whether you can reach "
       "the last index.", ARR_IN, "`true` or `false`.", ["`1 <= n <= 1000`", "`0 <= nums[i] <= 1000`"]),
    mk("unique-paths", "Unique Paths", "MEDIUM", ["math", "dynamic-programming"], [("m", "int"), ("n", "int")], "int",
       unique_paths, [(3, 7), (3, 2), (1, 1), (1, 10), (10, 1), (7, 3), (10, 10), (15, 15), (16, 16), (2, 2)],
       "A robot starts at the top-left of an `m x n` grid and can only move right or down. Return the number of "
       "distinct paths to the bottom-right corner.", "Line 1: `m`.\nLine 2: `n`.", "The number of paths.",
       ["`1 <= m, n <= 16`"]),
    mk("daily-temperatures", "Daily Temperatures", "MEDIUM", ["array", "stack", "monotonic-stack"],
       [("temperatures", "int[]")], "int[]", daily_temperatures, temp_cases(),
       "For each day, return how many days you must wait for a warmer temperature, or `0` if none is coming.",
       ARR_IN, "`n` space-separated integers, one per day.", ["`1 <= n <= 1000`", "`30 <= temperatures[i] <= 100`"]),
    mk("subarray-sum-equals-k", "Subarray Sum Equals K", "MEDIUM", ["array", "hash-table", "prefix-sum"],
       [("nums", "int[]"), ("k", "int")], "int", subarray_sum_k, subsum_cases(),
       "Return the number of contiguous, non-empty subarrays whose sum equals `k`.",
       "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The number of subarrays.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`", "`-10^7 <= k <= 10^7`"]),
    mk("kth-largest-element-in-an-array", "Kth Largest Element in an Array", "MEDIUM",
       ["array", "heap", "sorting", "quickselect"], [("nums", "int[]"), ("k", "int")], "int", kth_largest, kth_cases(),
       "Return the `k`-th largest element in sorted order (duplicates count separately), not the `k`-th distinct "
       "element.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The `k`-th largest element.",
       ["`1 <= k <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("maximum-product-subarray", "Maximum Product Subarray", "MEDIUM", ["array", "dynamic-programming"],
       [("nums", "int[]")], "int", max_product, maxprod_cases(),
       "Return the largest product of any contiguous, non-empty subarray. The answer fits in a 32-bit signed "
       "integer.", ARR_IN, "The maximum product.", ["`1 <= n <= 20`", "`-2 <= nums[i] <= 3`"]),
    mk("longest-palindromic-substring-length", "Longest Palindromic Substring (Length)", "MEDIUM",
       ["string", "dynamic-programming"], [("s", "str")], "int", longest_pal_len, pal_cases(),
       "Return the length of the longest palindromic substring of `s`.", "A single line containing `s`.",
       "The length.", ["`1 <= s.length <= 1000`", "Lowercase English letters"]),
    mk("min-cost-climbing-stairs", "Min Cost Climbing Stairs", "EASY", ["array", "dynamic-programming"],
       [("cost", "int[]")], "int", min_cost_stairs, cost_cases(),
       "`cost[i]` is the price of stepping on stair `i`, after which you may climb one or two stairs. You may start "
       "at stair `0` or `1`. Return the minimum cost to reach the top, one step beyond the last stair.", ARR_IN,
       "The minimum cost.", ["`2 <= n <= 1000`", "`0 <= cost[i] <= 999`"]),
    mk("longest-common-subsequence", "Longest Common Subsequence", "MEDIUM", ["string", "dynamic-programming"],
       [("text1", "str"), ("text2", "str")], "int", lcs, lcs_cases(),
       "Return the length of the longest common subsequence of two strings. A subsequence keeps relative order but "
       "may skip characters.", "Line 1: `text1`.\nLine 2: `text2`.", "The length.",
       ["`1 <= length <= 300`", "Lowercase English letters"]),
    mk("partition-equal-subset-sum", "Partition Equal Subset Sum", "MEDIUM", ["array", "dynamic-programming"],
       [("nums", "int[]")], "bool", partition_equal, partition_cases(),
       "Return whether `nums` can be split into two subsets with equal sums.", ARR_IN, "`true` or `false`.",
       ["`1 <= n <= 100`", "`1 <= nums[i] <= 100`"]),
    mk("first-missing-positive", "First Missing Positive", "HARD", ["array", "hash-table"], [("nums", "int[]")],
       "int", first_missing_positive, firstmiss_cases(),
       "Return the smallest positive integer that does not appear in `nums`. Try to do it in `O(n)` time with "
       "`O(1)` extra space.", ARR_IN, "The smallest missing positive integer.",
       ["`1 <= n <= 1100`", "`-2^31 <= nums[i] <= 2^31 - 1`"]),
    mk("largest-rectangle-in-histogram", "Largest Rectangle in Histogram", "HARD", ["array", "stack", "monotonic-stack"],
       [("heights", "int[]")], "int", largest_rect, rect_cases(),
       "Bars of width 1 and the given heights form a histogram. Return the area of the largest rectangle that fits "
       "inside it.", ARR_IN, "The largest area.", ["`1 <= n <= 1000`", "`0 <= heights[i] <= 10^4`"]),
]


# ------------------------------------------------------------ batch 3 problems
# Appended after batch 2 so the random data of every earlier problem is unchanged.
from collections import Counter, deque


def rand_str(n, alphabet):
    return "".join(rng.choice(alphabet) for _ in range(n))


# ---- two pointers -----------------------------------------------------------
def valid_palindrome(s):
    t = [c.lower() for c in s if c.isalnum()]
    return t == t[::-1]


def valid_palindrome_cases():
    cases = ["A man, a plan, a canal: Panama", "race a car", ".,", "0P", "ab_a", "No lemon, no melon",
             "Was it a car or a cat I saw?", "abc"]
    for _ in range(3):
        cases.append(rand_str(rng.randint(5, 60), "abcXYZ019 ,.!"))
    for _ in range(2):
        base = rand_str(rng.randint(3, 30), "abcdeABCDE0123")
        mid = rng.choice(["", "x", " "])
        cases.append((base + mid + base[::-1]).replace("a", "A, ", 1))
    return cases


def two_sum_ii(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return [lo + 1, hi + 1]
        if s < target:
            lo += 1
        else:
            hi -= 1
    raise AssertionError("no pair")


def pair_count(nums, target):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] + nums[j] == target)


def two_sum_ii_cases():
    cases = [([2, 7, 11, 15], 9), ([2, 3, 4], 6), ([-1, 0], -1)]
    while len(cases) < 9:
        n = rng.choice([10, 50, 300])
        nums = sorted(rng.sample(range(-1000, 1000), n))
        i, j = sorted(rng.sample(range(n), 2))
        if pair_count(nums, nums[i] + nums[j]) == 1:
            cases.append((nums, nums[i] + nums[j]))
    return cases


def three_sum_count(nums):
    nums = sorted(nums)
    seen = set()
    for i in range(len(nums) - 2):
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s == 0:
                seen.add((nums[i], nums[lo], nums[hi]))
                lo += 1
                hi -= 1
            elif s < 0:
                lo += 1
            else:
                hi -= 1
    return len(seen)


def remove_duplicates(nums):
    return list(dict.fromkeys(nums))


def move_zeroes(nums):
    nz = [x for x in nums if x != 0]
    return nz + [0] * (len(nums) - len(nz))


# ---- sliding window ---------------------------------------------------------
def min_size_subarray(target, nums):
    best, left, total = 0, 0, 0
    for right, v in enumerate(nums):
        total += v
        while total >= target:
            span = right - left + 1
            best = span if best == 0 else min(best, span)
            total -= nums[left]
            left += 1
    return best


def longest_repeating(s, k):
    counts, left, best, top = Counter(), 0, 0, 0
    for right, ch in enumerate(s):
        counts[ch] += 1
        top = max(top, counts[ch])
        while right - left + 1 - top > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def sliding_window_max(nums, k):
    dq, out = deque(), []
    for i, v in enumerate(nums):
        while dq and nums[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


def permutation_in_string(s1, s2):
    n = len(s1)
    need = Counter(s1)
    for i in range(len(s2) - n + 1):
        if Counter(s2[i:i + n]) == need:
            return True
    return False


# ---- bit manipulation -------------------------------------------------------
def number_of_1_bits(n):
    return bin(n).count("1")


def counting_bits(n):
    return [bin(i).count("1") for i in range(n + 1)]


def power_of_two(n):
    return n > 0 and n & (n - 1) == 0


# ---- backtracking -----------------------------------------------------------
def n_queens(n):
    cols, d1, d2 = set(), set(), set()

    def go(r):
        if r == n:
            return 1
        total = 0
        for c in range(n):
            if c in cols or r - c in d1 or r + c in d2:
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c)
            total += go(r + 1)
            cols.remove(c); d1.remove(r - c); d2.remove(r + c)
        return total

    return go(0)


def word_search(grid, word):
    rows, cols = len(grid), len(grid[0])
    seen = set()

    def dfs(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or (r, c) in seen or grid[r][c] != word[i]:
            return False
        seen.add((r, c))
        ok = any(dfs(r + dr, c + dc, i + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        seen.remove((r, c))
        return ok

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))


def word_search_cases():
    base = ["ABCE", "SFCS", "ADEE"]
    cases = [(base, "ABCCED"), (base, "SEE"), (base, "ABCB")]
    for _ in range(5):
        r, c = rng.choice([(3, 4), (4, 4), (5, 5), (6, 6)])
        grid = ["".join(rng.choice("ABC") for _ in range(c)) for _ in range(r)]
        if rng.random() < 0.6:
            y, x = rng.randrange(r), rng.randrange(c)
            path, used = [grid[y][x]], {(y, x)}
            for _ in range(rng.randint(3, 8)):
                options = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
                           if 0 <= y + dy < r and 0 <= x + dx < c and (y + dy, x + dx) not in used]
                if not options:
                    break
                y, x = rng.choice(options)
                used.add((y, x))
                path.append(grid[y][x])
            cases.append((grid, "".join(path)))
        else:
            cases.append((grid, rand_str(rng.randint(5, 9), "ABCD")))
    return cases


def count_subsets(nums, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for v in nums:
        for s in range(target, v - 1, -1):
            dp[s] += dp[s - v]
    return dp[target]


def distinct_perms_count(nums):
    total = math.factorial(len(nums))
    for c in Counter(nums).values():
        total //= math.factorial(c)
    return total


def catalan(n):
    return math.comb(2 * n, n) // (n + 1)


def palindrome_partitions(s):
    n = len(s)
    ways = [1] + [0] * n
    for i in range(1, n + 1):
        for j in range(i):
            piece = s[j:i]
            if piece == piece[::-1]:
                ways[i] += ways[j]
    return ways[n]


# ---- graphs -----------------------------------------------------------------
def course_schedule(n, prereqs):
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for a, b in prereqs:
        adj[b].append(a)
        indeg[a] += 1
    queue = deque(i for i in range(n) if indeg[i] == 0)
    done = 0
    while queue:
        u = queue.popleft()
        done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return done == n


def course_cases():
    cases = [(2, [[1, 0]]), (2, [[1, 0], [0, 1]])]
    for n in (5, 20, 60, 100, 100, 150):
        order = list(range(n))
        rng.shuffle(order)
        pos = {v: i for i, v in enumerate(order)}
        edges = set()
        for _ in range(rng.randint(n, 2 * n)):
            a, b = rng.sample(range(n), 2)
            if pos[a] < pos[b]:
                a, b = b, a
            edges.add((a, b))  # a comes after b: always acyclic
        edges = [list(e) for e in sorted(edges)]
        if len(cases) % 2 == 1:
            a, b = edges[rng.randrange(len(edges))]
            edges.append([b, a])  # closes a cycle
        cases.append((n, edges))
    return cases


def connected_components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = n
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            comps -= 1
    return comps


def random_edges(n, m):
    return [rng.sample(range(n), 2) for _ in range(m)]


def components_cases():
    cases = [(5, [[0, 1], [1, 2], [3, 4]]), (5, [[0, 1], [1, 2], [2, 3], [3, 4]])]
    for n, m in ((10, 4), (30, 20), (100, 60), (200, 150), (200, 90), (50, 10), (1000, 800)):
        cases.append((n, random_edges(n, m)))
    return cases


def valid_path(n, edges, source, destination):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen, queue = {source}, deque([source])
    while queue:
        u = queue.popleft()
        if u == destination:
            return True
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return False


def valid_path_cases():
    cases = [(3, [[0, 1], [1, 2], [2, 0]], 0, 2), (6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5)]
    for n, m in ((10, 8), (30, 25), (100, 80), (100, 150), (200, 160), (60, 30)):
        s, d = rng.sample(range(n), 2)
        cases.append((n, random_edges(n, m), s, d))
    return cases


def rotting_oranges(grid):
    rows, cols = len(grid), len(grid[0])
    cells = [list(r) for r in grid]
    queue = deque((r, c) for r in range(rows) for c in range(cols) if cells[r][c] == "2")
    fresh = sum(row.count("1") for row in cells)
    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                y, x = r + dr, c + dc
                if 0 <= y < rows and 0 <= x < cols and cells[y][x] == "1":
                    cells[y][x] = "2"
                    fresh -= 1
                    queue.append((y, x))
        minutes += 1
    return minutes if fresh == 0 else -1


def rand_grid(rows, cols, weights):
    chars, probs = zip(*weights)
    return ["".join(rng.choices(chars, probs, k=cols)) for _ in range(rows)]


def rotting_cases():
    cases = [["211", "110", "011"], ["211", "011", "101"], ["02"], ["0"], ["1"]]
    for r, c in ((5, 5), (8, 8), (12, 10), (20, 20)):
        cases.append(rand_grid(r, c, (("0", 0.2), ("1", 0.7), ("2", 0.1))))
    return cases


def shortest_path_binary(grid):
    n = len(grid)
    if grid[0][0] == "1" or grid[n - 1][n - 1] == "1":
        return -1
    queue, seen = deque([(0, 0, 1)]), {(0, 0)}
    while queue:
        r, c, d = queue.popleft()
        if (r, c) == (n - 1, n - 1):
            return d
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                y, x = r + dr, c + dc
                if 0 <= y < n and 0 <= x < n and grid[y][x] == "0" and (y, x) not in seen:
                    seen.add((y, x))
                    queue.append((y, x, d + 1))
    return -1


def shortest_cases():
    cases = [["01", "10"], ["000", "110", "110"]]
    for n, p in ((5, 0.3), (8, 0.25), (12, 0.35), (20, 0.3), (30, 0.3), (30, 0.45), (3, 0.5)):
        g = [list(r) for r in rand_grid(n, n, (("0", 1 - p), ("1", p)))]
        g[0][0] = g[n - 1][n - 1] = "0" if rng.random() < 0.85 else "1"
        cases.append(["".join(r) for r in g])
    return cases


# ---- greedy -----------------------------------------------------------------
def assign_cookies(g, s):
    g, s = sorted(g), sorted(s)
    i = 0
    for size in s:
        if i < len(g) and g[i] <= size:
            i += 1
    return i


def valid_starts(gas, cost):
    n = len(gas)
    ok = []
    for start in range(n):
        tank = 0
        for k in range(n):
            j = (start + k) % n
            tank += gas[j] - cost[j]
            if tank < 0:
                break
        else:
            ok.append(start)
    return ok


def gas_station(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0
    return start


def gas_cases():
    cases = [([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), ([2, 3, 4], [3, 4, 3])]
    while len(cases) < 9:
        n = rng.choice([5, 20, 100])
        gas = rand_arr(n, 0, 10)
        cost = rand_arr(n, 0, 10)
        starts = valid_starts(gas, cost)
        if len(starts) <= 1:
            assert gas_station(gas, cost) == (starts[0] if starts else -1)
            cases.append((gas, cost))
    return cases


def non_overlapping(intervals):
    intervals = sorted(intervals, key=lambda p: p[1])
    end, removed = -10**9, 0
    for s, e in intervals:
        if s >= end:
            end = e
        else:
            removed += 1
    return removed


def rand_intervals(n, span, width):
    out = []
    for _ in range(n):
        s = rng.randint(0, span)
        out.append([s, s + rng.randint(1, width)])
    return out


# ---- heap / intervals -------------------------------------------------------
def last_stone_weight(stones):
    heap = [-s for s in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = -heapq.heappop(heap), -heapq.heappop(heap)
        if a != b:
            heapq.heappush(heap, -(a - b))
    return -heap[0] if heap else 0


def top_k_frequent(nums, k):
    ranked = sorted(Counter(nums).items(), key=lambda kv: (-kv[1], kv[0]))
    return [v for v, _ in ranked[:k]]


def top_k_cases():
    cases = [([1, 1, 1, 2, 2, 3], 2), ([1], 1)]
    for n, hi in ((10, 4), (30, 8), (100, 15), (300, 40), (500, 100), (200, 5), (50, 50)):
        nums = rand_arr(n, -hi, hi)
        cases.append((nums, rng.randint(1, min(5, len(set(nums))))))
    return cases


def meeting_rooms(intervals):
    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)
    rooms = best = j = 0
    for s in starts:
        while ends[j] <= s:
            j += 1
            rooms -= 1
        rooms += 1
        best = max(best, rooms)
    return best


# ---- grids ------------------------------------------------------------------
def island_perimeter(grid):
    rows, cols = len(grid), len(grid[0])
    total = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                total += 4
                if r > 0 and grid[r - 1][c] == "1":
                    total -= 2
                if c > 0 and grid[r][c - 1] == "1":
                    total -= 2
    return total


def maximal_square(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * (cols + 1) for _ in range(rows + 1)]
    best = 0
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            if grid[r - 1][c - 1] == "1":
                dp[r][c] = 1 + min(dp[r - 1][c], dp[r][c - 1], dp[r - 1][c - 1])
                best = max(best, dp[r][c])
    return best * best


def binary_grid_cases(first):
    cases = list(first)
    for r, c, p in ((4, 4, 0.5), (6, 8, 0.6), (10, 10, 0.7), (15, 12, 0.8), (20, 20, 0.85), (30, 30, 0.9)):
        cases.append(rand_grid(r, c, (("1", p), ("0", 1 - p))))
    return cases


# ---- math -------------------------------------------------------------------
def happy_number(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1


def fast_power_mod(base, exp, mod):
    return pow(base, exp, mod)


ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
         (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def to_roman(n):
    out = []
    for value, sym in ROMAN:
        while n >= value:
            out.append(sym)
            n -= value
    return "".join(out)


def roman_to_integer(s):
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        if i + 1 < len(s) and vals[ch] < vals[s[i + 1]]:
            total -= vals[ch]
        else:
            total += vals[ch]
    return total


def perfect_squares(n):
    dp = [0] + [n] * n
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j * j] + 1)
            j += 1
    return dp[n]


def excel_column(s):
    total = 0
    for ch in s:
        total = total * 26 + ord(ch) - 64
    return total


def to_excel(n):
    out = []
    while n:
        n, r = divmod(n - 1, 26)
        out.append(chr(65 + r))
    return "".join(reversed(out))


# ---- dynamic programming ----------------------------------------------------
def decode_ways(s):
    prev2, prev1 = 1, 1 if s[0] != "0" else 0
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += prev1
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1


def unique_paths_obstacles(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                continue
            if r == 0 and c == 0:
                dp[r][c] = 1
            else:
                dp[r][c] = (dp[r - 1][c] if r else 0) + (dp[r][c - 1] if c else 0)
    return dp[rows - 1][cols - 1]


def is_subsequence(s, t):
    it = iter(t)
    return all(ch in it for ch in s)


def house_robber_ii(nums):
    def line(a):
        prev = cur = 0
        for v in a:
            prev, cur = cur, max(cur, prev + v)
        return cur

    return nums[0] if len(nums) == 1 else max(line(nums[1:]), line(nums[:-1]))


# ------------------------------------------------------------------ catalogue
N_IN = "A single integer `n`."
STR_IN = "A single line containing the string `s`."
INTERVALS_IN = "Line 1: `n`, the number of intervals.\nNext `n` lines: `start end`."
GRID_IN = "Line 1: `rows cols`.\nNext `rows` lines: a string of `cols` characters."
EDGES_IN = ("Line 1: `n`.\nLine 2: `m`, the number of edges.\nNext `m` lines: two integers `a b` describing one edge")

PROBLEMS += [
    # --- two pointers
    mk("valid-palindrome", "Valid Palindrome", "EASY", ["string", "two-pointers"], [("s", "str")], "bool",
       valid_palindrome, valid_palindrome_cases(),
       "After lowercasing and removing every character that is not a letter or digit, does the string read the same "
       "forwards and backwards?", STR_IN, "`true` or `false`.",
       ["`1 <= s.length <= 200`", "`s` contains printable ASCII characters"]),
    mk("two-sum-ii-input-array-is-sorted", "Two Sum II - Sorted Input", "MEDIUM", ["array", "two-pointers", "binary-search"],
       [("numbers", "int[]"), ("target", "int")], "int[]", two_sum_ii, two_sum_ii_cases(),
       "`numbers` is sorted in non-decreasing order. Find the one pair that sums to `target` and return their "
       "**1-based** indices, smaller first. Use only constant extra space.",
       "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `target`.", "The two 1-based indices, separated by a space.",
       ["`2 <= n <= 300`", "`-1000 <= numbers[i] <= 1000`", "Exactly one valid pair exists"]),
    mk("3sum-count", "3Sum (Count Triplets)", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]")], "int",
       three_sum_count, [[-1, 0, 1, 2, -1, -4], [0, 1, 1], [0, 0, 0], [0, 0, 0, 0], rand_arr(12, -10, 10),
                         rand_arr(60, -30, 30), rand_arr(200, -50, 50), rand_arr(500, -100, 100), rand_arr(3, -5, 5)],
       "Count the **distinct** value triplets `[a, b, c]` taken from different indices of `nums` whose sum is `0`. "
       "Two triplets are the same if they hold the same values, regardless of order.", ARR_IN,
       "The number of distinct triplets.", ["`3 <= n <= 500`", "`-10^5 <= nums[i] <= 10^5`"]),
    mk("remove-duplicates-from-sorted-array", "Remove Duplicates from Sorted Array", "EASY", ["array", "two-pointers"],
       [("nums", "int[]")], "int[]", remove_duplicates,
       [[1, 1, 2], [0, 0, 1, 1, 1, 2, 2, 3, 3, 4], [5], [1, 2, 3], sorted(rand_arr(50, 0, 20)),
        sorted(rand_arr(300, -30, 30)), sorted(rand_arr(1000, 0, 100)), [7, 7, 7, 7]],
       "`nums` is sorted. Print the distinct values in their original (sorted) order.", ARR_IN,
       "The distinct values separated by spaces.", ["`1 <= n <= 1000`", "`nums` is sorted in non-decreasing order"]),
    mk("move-zeroes", "Move Zeroes", "EASY", ["array", "two-pointers"], [("nums", "int[]")], "int[]", move_zeroes,
       [[0, 1, 0, 3, 12], [0], [1, 0, 0, 2], rand_arr(20, 0, 3), rand_arr(200, -2, 2), rand_arr(1000, 0, 1), [4, 5, 6],
        [0, 0, 7]],
       "Move every `0` to the end while keeping the relative order of the non-zero elements. Print the resulting "
       "array.", ARR_IN, "The rearranged array separated by spaces.", ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    # --- sliding window
    mk("minimum-size-subarray-sum", "Minimum Size Subarray Sum", "MEDIUM", ["array", "sliding-window", "prefix-sum"],
       [("target", "int"), ("nums", "int[]")], "int", min_size_subarray,
       [(7, [2, 3, 1, 2, 4, 3]), (4, [1, 4, 4]), (11, [1] * 8), (15, [1, 2, 3, 4, 5]), (100, rand_arr(30, 1, 10)),
        (50, rand_arr(200, 1, 20)), (1000, rand_arr(500, 1, 30)), (5, [5]), (3, [1, 1])],
       "Return the length of the shortest contiguous subarray whose sum is at least `target`, or `0` if none exists.",
       "Line 1: `target`.\nLine 2: `n`.\nLine 3: `n` positive integers.", "The minimum length, or `0`.",
       ["`1 <= target <= 10^9`", "`1 <= n <= 1000`", "`1 <= nums[i] <= 10^4`"]),
    mk("longest-repeating-character-replacement", "Longest Repeating Character Replacement", "MEDIUM",
       ["string", "sliding-window", "hash-table"], [("s", "str"), ("k", "int")], "int", longest_repeating,
       [("ABAB", 2), ("AABABBA", 1), ("A", 0), ("ABCDE", 1), (rand_str(40, "AB"), 3), (rand_str(100, "ABC"), 4),
        (rand_str(300, "ABC"), 10), (rand_str(500, "ABCD"), 0), ("AAAA", 2)],
       "You may change at most `k` characters of `s` to any uppercase letter. Return the length of the longest "
       "substring of identical letters you can obtain.", "Line 1: the string `s`.\nLine 2: `k`.", "The maximum length.",
       ["`1 <= s.length <= 500`", "`s` is uppercase English letters", "`0 <= k <= s.length`"]),
    mk("sliding-window-maximum", "Sliding Window Maximum", "HARD", ["array", "sliding-window", "heap", "monotonic-stack"],
       [("nums", "int[]"), ("k", "int")], "int[]", sliding_window_max,
       [([1, 3, -1, -3, 5, 3, 6, 7], 3), ([1], 1), ([9, 11], 2), ([4, 3, 2, 1], 2), (rand_arr(30, -20, 20), 4),
        (rand_arr(200, -1000, 1000), 10), (rand_arr(1000, -10000, 10000), 50), (list(range(100)), 7),
        (list(range(100, 0, -1)), 7)],
       "A window of size `k` slides from the left of `nums` to the right, one position at a time. Print the maximum "
       "of every window.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.",
       "`n - k + 1` window maximums separated by spaces.", ["`1 <= k <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("permutation-in-string", "Permutation in String", "MEDIUM", ["string", "sliding-window", "hash-table"],
       [("s1", "str"), ("s2", "str")], "bool", permutation_in_string,
       [("ab", "eidbaooo"), ("ab", "eidboaoo"), ("a", "a"), ("abc", "ab"), (rand_str(4, "abc"), rand_str(30, "abc")),
        (rand_str(6, "abcd"), rand_str(100, "abcd")), (rand_str(8, "ab"), rand_str(200, "abc")),
        (rand_str(10, "abcde"), rand_str(400, "abcde")), ("adc", "dcda")],
       "Return `true` if some permutation of `s1` appears as a contiguous substring of `s2`.",
       "Line 1: `s1`.\nLine 2: `s2`.", "`true` or `false`.", ["`1 <= s1.length, s2.length <= 400`", "Lowercase letters"]),
    # --- bit manipulation
    mk("number-of-1-bits", "Number of 1 Bits", "EASY", ["bit-manipulation"], [("n", "int")], "int", number_of_1_bits,
       [11, 128, 2147483645, 1, 255, 1023, 2147483647, rng.randint(1, 2**31 - 1), rng.randint(1, 2**31 - 1)],
       "Return the number of `1` bits in the binary representation of the positive integer `n`.", N_IN,
       "The count of set bits.", ["`1 <= n <= 2^31 - 1`"]),
    mk("counting-bits", "Counting Bits", "EASY", ["bit-manipulation", "dynamic-programming"], [("n", "int")], "int[]",
       counting_bits, [2, 5, 1, 10, 16, 33, 100, 500, 1000],
       "For every `i` from `0` to `n` inclusive, count the `1` bits in `i`. Print all `n + 1` counts.", N_IN,
       "`n + 1` integers separated by spaces.", ["`1 <= n <= 1000`"]),
    mk("power-of-two", "Power of Two", "EASY", ["math", "bit-manipulation"], [("n", "int")], "bool", power_of_two,
       [1, 16, 3, 0, -16, 2**30, 2**30 + 1, 218, -2147483648, 1024, 6],
       "Return `true` if `n` is a power of two (`1, 2, 4, 8, ...`).", N_IN, "`true` or `false`.",
       ["`-2^31 <= n <= 2^31 - 1`"]),
    # --- backtracking
    mk("n-queens-count", "N-Queens (Count Solutions)", "HARD", ["backtracking"], [("n", "int")], "int", n_queens,
       [4, 1, 2, 3, 5, 6, 7, 8, 9],
       "Place `n` queens on an `n x n` board so that no two attack each other (same row, column or diagonal). "
       "Return how many distinct placements exist.", N_IN, "The number of solutions.", ["`1 <= n <= 9`"]),
    mk("word-search", "Word Search", "MEDIUM", ["backtracking", "matrix"], [("board", "grid"), ("word", "str")], "bool",
       word_search, word_search_cases(),
       "Return `true` if `word` can be traced through the grid by moving up, down, left or right between adjacent "
       "cells without using any cell twice.", GRID_IN + "\nLast line: the `word`.", "`true` or `false`.",
       ["`1 <= rows, cols <= 6`", "`1 <= word.length <= 9`", "Uppercase letters"]),
    mk("count-subsets-with-sum", "Count Subsets With Target Sum", "MEDIUM", ["backtracking", "dynamic-programming"],
       [("nums", "int[]"), ("target", "int")], "int", count_subsets,
       [([1, 1, 1, 1, 1], 3), ([2, 3, 5, 6, 8, 10], 10), ([1, 2, 3], 7), (rand_arr(10, 1, 9), 15),
        (rand_arr(15, 1, 20), 40), (rand_arr(20, 1, 30), 100), (rand_arr(20, 1, 10), 60), ([5], 5), ([4, 4], 4)],
       "Count the subsets (chosen by index, so equal values count separately) of `nums` whose elements add up to "
       "exactly `target`.", "Line 1: `n`.\nLine 2: `n` positive integers.\nLine 3: `target`.",
       "The number of subsets.", ["`1 <= n <= 20`", "`1 <= nums[i] <= 50`", "`1 <= target <= 500`"]),
    mk("distinct-permutations-count", "Distinct Permutations Count", "MEDIUM", ["backtracking", "math"],
       [("nums", "int[]")], "int", distinct_perms_count,
       [[1, 1, 2], [1, 2, 3], [1, 1, 1], [1, 2], rand_arr(6, 1, 3), rand_arr(7, 1, 4), rand_arr(8, 1, 3),
        rand_arr(8, 1, 8), [5]],
       "`nums` may contain duplicates. Return how many different arrangements (as value sequences) it has.", ARR_IN,
       "The number of distinct permutations.", ["`1 <= n <= 8`", "`1 <= nums[i] <= 10`"]),
    mk("generate-parentheses-count", "Generate Parentheses (Count)", "MEDIUM", ["backtracking", "dynamic-programming", "math"],
       [("n", "int")], "int", catalan, [3, 1, 2, 4, 5, 8, 10, 12, 15],
       "Return how many well-formed strings of `n` pairs of parentheses exist.", N_IN, "The count.", ["`1 <= n <= 15`"]),
    mk("palindrome-partitioning-count", "Palindrome Partitioning (Count)", "MEDIUM",
       ["backtracking", "dynamic-programming", "string"], [("s", "str")], "int", palindrome_partitions,
       ["aab", "a", "aaa", "abc", "abba", rand_str(10, "ab"), rand_str(14, "ab"), "a" * 16, rand_str(16, "abc")],
       "Count the ways to cut `s` into pieces so that every piece is a palindrome.", STR_IN, "The number of ways.",
       ["`1 <= s.length <= 16`", "Lowercase letters"]),
    # --- graphs
    mk("course-schedule", "Course Schedule", "MEDIUM", ["graph", "topological-sort", "bfs"],
       [("numCourses", "int"), ("prerequisites", "int[][]")], "bool", course_schedule, course_cases(),
       "There are `numCourses` courses labelled `0..numCourses-1`. Each pair `[a, b]` means you must take course `b` "
       "before `a`. Return whether all courses can be finished.",
       "Line 1: `numCourses`.\nLine 2: `m`, the number of prerequisites.\nNext `m` lines: `a b`.", "`true` or `false`.",
       ["`1 <= numCourses <= 150`", "`1 <= m <= 400`"]),
    mk("number-of-connected-components", "Number of Connected Components", "MEDIUM", ["graph", "union-find", "dfs"],
       [("n", "int"), ("edges", "int[][]")], "int", connected_components, components_cases(),
       "An undirected graph has `n` nodes labelled `0..n-1`. Return the number of connected components.", EDGES_IN + ".",
       "The number of components.", ["`1 <= n <= 1000`", "`1 <= m <= 1000`"]),
    mk("find-if-path-exists-in-graph", "Find if Path Exists in Graph", "EASY", ["graph", "bfs", "union-find"],
       [("n", "int"), ("edges", "int[][]"), ("source", "int"), ("destination", "int")], "bool", valid_path,
       valid_path_cases(),
       "Return whether a path exists between `source` and `destination` in an undirected graph.",
       EDGES_IN + ".\nThen `source` on its own line, then `destination` on its own line.", "`true` or `false`.",
       ["`2 <= n <= 200`", "`1 <= m <= 300`"]),
    mk("rotting-oranges", "Rotting Oranges", "MEDIUM", ["graph", "bfs", "matrix"], [("grid", "grid")], "int",
       rotting_oranges, rotting_cases(),
       "Each cell is `0` (empty), `1` (fresh orange) or `2` (rotten orange). Every minute, fresh oranges next to a "
       "rotten one (up, down, left, right) rot. Return the minutes until none are fresh, or `-1` if that is impossible.",
       GRID_IN, "The minutes, or `-1`.", ["`1 <= rows, cols <= 20`"]),
    mk("shortest-path-in-binary-matrix", "Shortest Path in Binary Matrix", "MEDIUM", ["graph", "bfs", "matrix"],
       [("grid", "grid")], "int", shortest_path_binary, shortest_cases(),
       "In an `n x n` grid of `0` (open) and `1` (blocked), find the shortest path from the top-left to the bottom-right "
       "moving in any of the 8 directions through open cells. Return the number of cells on that path, or `-1`.",
       GRID_IN + "\n(The grid is square.)", "The path length, or `-1`.", ["`1 <= n <= 30`"]),
    # --- greedy
    mk("assign-cookies", "Assign Cookies", "EASY", ["greedy", "sorting", "two-pointers"],
       [("g", "int[]"), ("s", "int[]")], "int", assign_cookies,
       [([1, 2, 3], [1, 1]), ([1, 2], [1, 2, 3]), ([10, 9, 8], [1, 2]), (rand_arr(10, 1, 10), rand_arr(8, 1, 10)),
        (rand_arr(100, 1, 50), rand_arr(100, 1, 50)), (rand_arr(300, 1, 100), rand_arr(200, 1, 100)), ([5], [5]),
        ([1, 1, 1], [9]), (rand_arr(500, 1, 1000), rand_arr(500, 1, 1000))],
       "Child `i` is content with a cookie of size at least `g[i]`. Each cookie `s[j]` can go to one child. Return the "
       "maximum number of content children.",
       "Line 1: `n`.\nLine 2: the greed factors `g`.\nLine 3: `m`.\nLine 4: the cookie sizes `s`.",
       "The maximum number of content children.", ["`1 <= n, m <= 500`", "`1 <= g[i], s[j] <= 1000`"]),
    mk("gas-station", "Gas Station", "MEDIUM", ["greedy", "array"], [("gas", "int[]"), ("cost", "int[]")], "int",
       gas_station, gas_cases(),
       "Stations are arranged in a circle. `gas[i]` is the fuel you gain at station `i` and `cost[i]` the fuel to drive "
       "to the next one. Starting with an empty tank, return the index of the station from which you can complete the "
       "circuit, or `-1`. The answer is unique when it exists.",
       "Line 1: `n`.\nLine 2: `gas`.\nLine 3: `n`.\nLine 4: `cost`.", "The starting index, or `-1`.",
       ["`1 <= n <= 100`", "`0 <= gas[i], cost[i] <= 10`"]),
    mk("non-overlapping-intervals", "Non-overlapping Intervals", "MEDIUM", ["greedy", "intervals", "sorting"],
       [("intervals", "int[][]")], "int", non_overlapping,
       [[[1, 2], [2, 3], [3, 4], [1, 3]], [[1, 2], [1, 2], [1, 2]], [[1, 2], [2, 3]], rand_intervals(10, 20, 6),
        rand_intervals(50, 100, 15), rand_intervals(200, 300, 30), rand_intervals(300, 100, 40), [[0, 5]],
        rand_intervals(100, 50, 10)],
       "Return the minimum number of intervals to remove so the rest do not overlap. Intervals that only touch at an "
       "endpoint (such as `[1,2]` and `[2,3]`) do not overlap.", INTERVALS_IN, "The minimum removals.",
       ["`1 <= n <= 300`", "`0 <= start < end <= 10^4`"]),
    # --- heap
    mk("last-stone-weight", "Last Stone Weight", "EASY", ["heap", "array"], [("stones", "int[]")], "int",
       last_stone_weight,
       [[2, 7, 4, 1, 8, 1], [1], [3, 3], rand_arr(10, 1, 20), rand_arr(30, 1, 100), rand_arr(100, 1, 1000),
        rand_arr(5, 1, 5), [9, 3, 2, 10], rand_arr(60, 1, 50)],
       "Repeatedly smash the two heaviest stones. If they are equal both vanish; otherwise the heavier one keeps the "
       "difference. Return the weight of the last remaining stone, or `0`.", "Line 1: `n`.\nLine 2: the stone weights.",
       "The final weight.", ["`1 <= n <= 100`", "`1 <= stones[i] <= 1000`"]),
    mk("top-k-frequent-elements", "Top K Frequent Elements", "MEDIUM", ["heap", "hash-table", "sorting"],
       [("nums", "int[]"), ("k", "int")], "int[]", top_k_frequent, top_k_cases(),
       "Return the `k` most frequent values. Order them by frequency (highest first); break ties by the smaller value "
       "first.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "`k` integers separated by spaces.",
       ["`1 <= n <= 500`", "`1 <= k <=` the number of distinct values"]),
    mk("meeting-rooms-ii", "Meeting Rooms II", "MEDIUM", ["heap", "intervals", "sorting"], [("intervals", "int[][]")],
       "int", meeting_rooms,
       [[[0, 30], [5, 10], [15, 20]], [[7, 10], [2, 4]], [[1, 5], [5, 9]], rand_intervals(10, 30, 10),
        rand_intervals(50, 100, 30), rand_intervals(200, 300, 60), rand_intervals(300, 80, 50), [[1, 2]],
        rand_intervals(100, 40, 20)],
       "Each interval is a meeting `[start, end)`. Return the minimum number of rooms needed. A meeting that starts "
       "exactly when another ends can reuse its room.", INTERVALS_IN, "The minimum number of rooms.",
       ["`1 <= n <= 300`", "`0 <= start < end <= 10^4`"]),
    # --- grids
    mk("island-perimeter", "Island Perimeter", "EASY", ["matrix", "array"], [("grid", "grid")], "int",
       island_perimeter, binary_grid_cases([["0100", "1110", "0100", "1100"], ["1"], ["10", "01"]]),
       "Cells are `1` (land) or `0` (water). Return the total length of the edges between land cells and water or the "
       "grid boundary.", GRID_IN, "The perimeter.", ["`1 <= rows, cols <= 30`"]),
    mk("maximal-square", "Maximal Square", "MEDIUM", ["matrix", "dynamic-programming"], [("matrix", "grid")], "int",
       maximal_square, binary_grid_cases([["10100", "10111", "11111", "10010"], ["01", "10"], ["0"]]),
       "Find the largest square made only of `1`s and return its **area**.", GRID_IN, "The area.",
       ["`1 <= rows, cols <= 30`"]),
    # --- math
    mk("happy-number", "Happy Number", "EASY", ["math", "hash-table"], [("n", "int")], "bool", happy_number,
       [19, 2, 1, 7, 4, 100, 116, 2147483647, rng.randint(1, 10**9), 1111111],
       "Repeatedly replace `n` with the sum of the squares of its digits. `n` is happy if this reaches `1`, and unhappy "
       "if it loops forever.", N_IN, "`true` or `false`.", ["`1 <= n <= 2^31 - 1`"]),
    mk("fast-power-mod", "Fast Modular Exponentiation", "MEDIUM", ["math", "divide-and-conquer"],
       [("base", "int"), ("exp", "int"), ("mod", "int")], "int", fast_power_mod,
       [(2, 10, 1000), (3, 200, 13), (0, 0, 7), (5, 3, 1), (2, 1000000000, 1000000007),
        (123456789, 987654321, 999999937), (10, 0, 5), (999999999, 999999999, 1000000000), (7, 1, 2)],
       "Compute `base^exp mod mod`. `exp` can be as large as `10^9`, so use fast exponentiation and take care that "
       "intermediate products can overflow 32 bits. `0^0` is `1`.", "Three lines: `base`, `exp`, `mod`.",
       "The result.", ["`0 <= base, exp <= 10^9`", "`1 <= mod <= 10^9`"]),
    mk("roman-to-integer", "Roman to Integer", "EASY", ["math", "string"], [("s", "str")], "int", roman_to_integer,
       [to_roman(n) for n in (3, 58, 1994, 4, 9, 3999, 1, 444, 2024, rng.randint(1, 3999), rng.randint(1, 3999))],
       "Convert a valid Roman numeral to an integer. Subtractive forms such as `IV` and `CM` apply.", STR_IN,
       "The integer value.", ["`1 <= value <= 3999`"]),
    mk("perfect-squares", "Perfect Squares", "MEDIUM", ["math", "dynamic-programming", "bfs"], [("n", "int")], "int",
       perfect_squares, [12, 13, 1, 2, 7, 43, 100, 6175, 9999, 10000],
       "Return the least number of perfect squares (`1, 4, 9, 16, ...`) that sum to `n`.", N_IN,
       "The minimum count.", ["`1 <= n <= 10^4`"]),
    mk("excel-sheet-column-number", "Excel Sheet Column Number", "EASY", ["math", "string"], [("columnTitle", "str")],
       "int", excel_column,
       ["A", "AB", "ZY", "Z", "AA", "FXSHRXW", "XFD", to_excel(rng.randint(1, 10**6)), to_excel(rng.randint(10**6, 2 * 10**9))],
       "Return the column number for an Excel column title (`A -> 1`, `Z -> 26`, `AA -> 27`, ...).",
       "A single line containing the column title.", "The column number.",
       ["`1 <= title.length <= 7`", "Uppercase letters, value fits in 32 bits"]),
    # --- dynamic programming
    mk("decode-ways", "Decode Ways", "MEDIUM", ["dynamic-programming", "string"], [("s", "str")], "int", decode_ways,
       ["12", "226", "06", "0", "10", "27", "11106", rand_str(20, "12"), rand_str(30, "0123456789").lstrip("0") or "1",
        "1" * 35],
       "Letters map to numbers (`A -> 1`, ..., `Z -> 26`). Return how many ways a digit string can be decoded back into "
       "letters. Leading zeros make a piece invalid.", STR_IN, "The number of decodings.",
       ["`1 <= s.length <= 35`", "Digits only"]),
    mk("unique-paths-ii", "Unique Paths II", "MEDIUM", ["dynamic-programming", "matrix"], [("grid", "grid")], "int",
       unique_paths_obstacles,
       [["000", "010", "000"], ["01", "00"], ["1"]]
       + [rand_grid(r, c, (("0", 0.85), ("1", 0.15))) for r, c in ((5, 5), (8, 6), (10, 10), (12, 12), (15, 15), (9, 14))],
       "A robot moves only right or down from the top-left to the bottom-right of a grid. Cells marked `1` are "
       "obstacles. Return the number of distinct paths.", GRID_IN, "The number of paths.",
       ["`1 <= rows, cols <= 15`", "The answer fits in 32 bits"]),
    mk("is-subsequence", "Is Subsequence", "EASY", ["string", "two-pointers", "dynamic-programming"],
       [("s", "str"), ("t", "str")], "bool", is_subsequence,
       [("abc", "ahbgdc"), ("axc", "ahbgdc"), ("a", "a"), ("b", "abc"), (rand_str(5, "abc"), rand_str(40, "abc")),
        (rand_str(8, "abcd"), rand_str(100, "abcd")), (rand_str(20, "ab"), rand_str(300, "ab")),
        (rand_str(3, "xyz"), rand_str(50, "abc")), ("abc", "cba")],
       "Return `true` if `s` can be obtained from `t` by deleting some characters without reordering the rest.",
       "Line 1: `s`.\nLine 2: `t`.", "`true` or `false`.", ["`1 <= s.length <= 100`", "`1 <= t.length <= 300`"]),
    mk("house-robber-ii", "House Robber II", "MEDIUM", ["dynamic-programming", "array"], [("nums", "int[]")], "int",
       house_robber_ii,
       [[2, 3, 2], [1, 2, 3, 1], [1, 2, 3], [5], [1, 2], rand_arr(10, 0, 50), rand_arr(50, 0, 100),
        rand_arr(200, 0, 400), rand_arr(500, 0, 1000)],
       "Houses are arranged in a circle, so the first and last are neighbours. You cannot rob two adjacent houses. "
       "Return the maximum amount you can rob.", ARR_IN, "The maximum amount.",
       ["`1 <= n <= 500`", "`0 <= nums[i] <= 1000`"]),
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
