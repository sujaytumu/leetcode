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
