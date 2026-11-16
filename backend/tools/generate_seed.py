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
# Param types: int, str, int[], int[][], grid (list of strings), list (singly linked list), tree (binary tree).
# Return types: int, bool, int[], int[][], list, tree.
# Wire format: `list` is `n` then `n` ints; `tree` is `n` then `n` level-order tokens where `null` is a missing child.
# In the reference solutions a list is a Python list of ints and a tree is a level-order Python list with None gaps.


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
        elif typ == "list":
            lines.append(str(len(val)))
            lines.append(" ".join(map(str, val)))
        elif typ == "tree":
            lines.append(str(len(val)))
            lines.append(" ".join("null" if v is None else str(v) for v in val))
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
    if ret == "list":
        return " ".join(map(str, val)) + "\n"
    if ret == "tree":
        toks = list(val)
        while toks and toks[-1] is None:
            toks.pop()
        return " ".join("null" if v is None else str(v) for v in toks) + "\n"
    raise ValueError(ret)


# ------------------------------------------------------------ starter code
def uses(params, ret, kind):
    return ret == kind or any(t == kind for _, t in params)


PY_LIST = ["class ListNode:", "    def __init__(self, val=0, next=None):", "        self.val = val", "        self.next = next", "",
           "", "def build_list(vals):", "    head = None", "    for v in reversed(vals):", "        head = ListNode(v, head)",
           "    return head", "", "", "def list_values(node):", "    out = []", "    while node:", "        out.append(node.val)",
           "        node = node.next", "    return out", "", ""]
PY_TREE = ["from collections import deque", "", "", "class TreeNode:", "    def __init__(self, val=0, left=None, right=None):",
           "        self.val = val", "        self.left = left", "        self.right = right", "", "",
           "def build_tree(tokens):", '    if not tokens or tokens[0] == "null":', "        return None",
           "    root = TreeNode(int(tokens[0]))", "    queue = deque([root])", "    i = 1",
           "    while queue and i < len(tokens):", "        node = queue.popleft()",
           '        if i < len(tokens) and tokens[i] != "null":', "            node.left = TreeNode(int(tokens[i]))",
           "            queue.append(node.left)", "        i += 1",
           '        if i < len(tokens) and tokens[i] != "null":', "            node.right = TreeNode(int(tokens[i]))",
           "            queue.append(node.right)", "        i += 1", "    return root", "", "",
           "def tree_tokens(root):", "    out = []", "    queue = deque([root])", "    while queue:",
           "        node = queue.popleft()", "        if node is None:", '            out.append("null")', "        else:",
           "            out.append(str(node.val))", "            queue.append(node.left)", "            queue.append(node.right)",
           '    while out and out[-1] == "null":', "        out.pop()", "    return out", "", ""]

JAVA_LIST = ["    static class ListNode {", "        int val;", "        ListNode next;", "        ListNode(int val) { this.val = val; }",
             "    }", "",
             "    static ListNode buildList(int[] vals) {", "        ListNode dummy = new ListNode(0), tail = dummy;",
             "        for (int v : vals) { tail.next = new ListNode(v); tail = tail.next; }", "        return dummy.next;", "    }", "",
             "    static String listString(ListNode node) {", "        StringBuilder sb = new StringBuilder();",
             "        for (; node != null; node = node.next) { if (sb.length() > 0) sb.append(' '); sb.append(node.val); }",
             "        return sb.toString();", "    }", ""]
JAVA_TREE = ["    static class TreeNode {", "        int val;", "        TreeNode left, right;", "        TreeNode(int val) { this.val = val; }",
             "    }", "",
             "    static TreeNode buildTree(String[] t) {", '        if (t.length == 0 || t[0].equals("null")) return null;',
             "        TreeNode root = new TreeNode(Integer.parseInt(t[0]));", "        Deque<TreeNode> queue = new ArrayDeque<>();",
             "        queue.add(root);", "        int i = 1;", "        while (!queue.isEmpty() && i < t.length) {",
             "            TreeNode node = queue.poll();", '            if (i < t.length && !t[i].equals("null")) {',
             "                node.left = new TreeNode(Integer.parseInt(t[i]));", "                queue.add(node.left);", "            }",
             "            i++;", '            if (i < t.length && !t[i].equals("null")) {',
             "                node.right = new TreeNode(Integer.parseInt(t[i]));", "                queue.add(node.right);", "            }",
             "            i++;", "        }", "        return root;", "    }", "",
             "    static String treeString(TreeNode root) {", "        List<String> out = new ArrayList<>();",
             "        Deque<TreeNode> queue = new LinkedList<>(); // allows null entries", "        queue.add(root);", "        while (!queue.isEmpty()) {",
             "            TreeNode node = queue.poll();", '            if (node == null) { out.add("null"); continue; }',
             "            out.add(String.valueOf(node.val));", "            queue.add(node.left);", "            queue.add(node.right);",
             "        }", '        while (!out.isEmpty() && out.get(out.size() - 1).equals("null")) out.remove(out.size() - 1);',
             '        return String.join(" ", out);', "    }", ""]

JS_LIST = ["class ListNode {", "  constructor(val = 0, next = null) {", "    this.val = val;", "    this.next = next;", "  }", "}", "",
           "function buildList(vals) {", "  let head = null;",
           "  for (let i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head);", "  return head;", "}", "",
           "function listString(node) {", "  const out = [];", "  for (; node; node = node.next) out.push(node.val);",
           '  return out.join(" ");', "}", ""]
JS_TREE = ["class TreeNode {", "  constructor(val = 0, left = null, right = null) {", "    this.val = val;", "    this.left = left;",
           "    this.right = right;", "  }", "}", "", "function buildTree(t) {",
           '  if (t.length === 0 || t[0] === "null") return null;', "  const root = new TreeNode(Number(t[0]));",
           "  const queue = [root];", "  let head = 0;", "  let i = 1;", "  while (head < queue.length && i < t.length) {",
           "    const node = queue[head++];", '    if (i < t.length && t[i] !== "null") { node.left = new TreeNode(Number(t[i])); queue.push(node.left); }',
           "    i++;", '    if (i < t.length && t[i] !== "null") { node.right = new TreeNode(Number(t[i])); queue.push(node.right); }',
           "    i++;", "  }", "  return root;", "}", "", "function treeString(root) {", "  const out = [];",
           "  const queue = [root];", "  let head = 0;", "  while (head < queue.length) {", "    const node = queue[head++];",
           '    if (!node) { out.push("null"); continue; }', "    out.push(String(node.val));", "    queue.push(node.left, node.right);",
           "  }", '  while (out.length && out[out.length - 1] === "null") out.pop();', '  return out.join(" ");', "}", ""]

CPP_LIST = ["struct ListNode {", "    int val;", "    ListNode *next;", "    ListNode(int v) : val(v), next(nullptr) {}", "};", "",
            "ListNode *buildList(const vector<int> &vals) {", "    ListNode dummy(0);", "    ListNode *tail = &dummy;",
            "    for (int v : vals) { tail->next = new ListNode(v); tail = tail->next; }", "    return dummy.next;", "}", "",
            "string listString(ListNode *node) {", "    string out;", "    for (; node; node = node->next) {",
            '        if (!out.empty()) out += " ";', "        out += to_string(node->val);", "    }", "    return out;", "}", ""]
CPP_TREE = ["struct TreeNode {", "    int val;", "    TreeNode *left, *right;", "    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}",
            "};", "", "TreeNode *buildTree(const vector<string> &t) {", '    if (t.empty() || t[0] == "null") return nullptr;',
            "    TreeNode *root = new TreeNode(stoi(t[0]));", "    queue<TreeNode *> q;", "    q.push(root);", "    size_t i = 1;",
            "    while (!q.empty() && i < t.size()) {", "        TreeNode *node = q.front();", "        q.pop();",
            '        if (i < t.size() && t[i] != "null") { node->left = new TreeNode(stoi(t[i])); q.push(node->left); }',
            "        i++;", '        if (i < t.size() && t[i] != "null") { node->right = new TreeNode(stoi(t[i])); q.push(node->right); }',
            "        i++;", "    }", "    return root;", "}", "", "string treeString(TreeNode *root) {", "    vector<string> out;",
            "    queue<TreeNode *> q;", "    q.push(root);", "    while (!q.empty()) {", "        TreeNode *node = q.front();",
            "        q.pop();", '        if (!node) { out.push_back("null"); continue; }', "        out.push_back(to_string(node->val));",
            "        q.push(node->left);", "        q.push(node->right);", "    }",
            '    while (!out.empty() && out.back() == "null") out.pop_back();', '    string s;', "    for (size_t i = 0; i < out.size(); i++) {",
            '        if (i) s += " ";', "        s += out[i];", "    }", "    return s;", "}", ""]

def cap(name):
    return name[0].upper() + name[1:]


def starter_python(params, ret):
    names = ", ".join(n for n, _ in params)
    prelude = (PY_LIST if uses(params, ret, "list") else []) + (PY_TREE if uses(params, ret, "tree") else [])
    body = ["import sys"] + ([""] if not prelude or prelude[0].startswith("from") else []) + [""]
    body += prelude
    body += [f"def solve({names}):", "    # Write your solution here", "    pass", "", "", "def main():",
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
        elif t == "list":
            body += [f"    {n}_len = int(lines[pos]); pos += 1",
                     f"    {n} = build_list(list(map(int, lines[pos].split())) if {n}_len > 0 else []); pos += 1"]
        elif t == "tree":
            body += [f"    {n}_len = int(lines[pos]); pos += 1",
                     f"    {n} = build_tree(lines[pos].split() if {n}_len > 0 else []); pos += 1"]
    body += [f"    result = solve({names})"]
    body += {
        "int": ["    print(result)"],
        "bool": ['    print("true" if result else "false")'],
        "int[]": ['    print(" ".join(map(str, result)))'],
        "int[][]": ["    for row in result:", '        print(" ".join(map(str, row)))'],
        "list": ['    print(" ".join(map(str, list_values(result))))'],
        "tree": ['    print(" ".join(tree_tokens(result)))'],
    }[ret]
    body += ["", "", 'if __name__ == "__main__":', "    main()", ""]
    return "\n".join(body)


JAVA_T = {"int": "int", "str": "String", "int[]": "int[]", "int[][]": "int[][]", "grid": "String[]", "list": "ListNode", "tree": "TreeNode"}
JAVA_RET = {"int": "int", "bool": "boolean", "int[]": "int[]", "int[][]": "int[][]", "list": "ListNode", "tree": "TreeNode"}
JAVA_DEFAULT = {"int": "0", "bool": "false", "int[]": "new int[0]", "int[][]": "new int[0][]", "list": "null", "tree": "null"}


def starter_java(params, ret):
    sig = ", ".join(f"{JAVA_T[t]} {n}" for n, t in params)
    names = ", ".join(n for n, _ in params)
    prelude = (JAVA_LIST if uses(params, ret, "list") else []) + (JAVA_TREE if uses(params, ret, "tree") else [])
    out = ["import java.io.*;", "import java.util.*;", "import java.util.stream.*;", "", "public class Main {"] + prelude
    out += [f"    static {JAVA_RET[ret]} solve({sig}) {{", "        // Write your solution here",
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
        elif t == "list":
            out += [f"        int {n}Len = Integer.parseInt(lines.get(pos++).trim());",
                    f"        int[] {n}Vals = new int[{n}Len];",
                    f"        if ({n}Len > 0) {{",
                    f"            StringTokenizer st = new StringTokenizer(lines.get(pos));",
                    f"            for (int i = 0; i < {n}Len; i++) {n}Vals[i] = Integer.parseInt(st.nextToken());",
                    "        }", "        pos++;", f"        ListNode {n} = buildList({n}Vals);"]
        elif t == "tree":
            out += [f"        int {n}Len = Integer.parseInt(lines.get(pos++).trim());",
                    f"        String[] {n}Tok = {n}Len > 0 ? lines.get(pos).trim().split(\"\\\\s+\") : new String[0];",
                    "        pos++;", f"        TreeNode {n} = buildTree({n}Tok);"]
    out += [f"        {JAVA_RET[ret]} result = solve({names});"]
    out += {
        "int": ["        System.out.println(result);"],
        "bool": ["        System.out.println(result);"],
        "int[]": ['        System.out.println(Arrays.stream(result).mapToObj(String::valueOf).collect(Collectors.joining(" ")));'],
        "int[][]": ["        for (int[] row : result) {",
                    '            System.out.println(row[0] + " " + row[1]);', "        }"],
        "list": ["        System.out.println(listString(result));"],
        "tree": ["        System.out.println(treeString(result));"],
    }[ret]
    out += ["    }", "}", ""]
    return "\n".join(out)


def starter_js(params, ret):
    names = ", ".join(n for n, _ in params)
    prelude = (JS_LIST if uses(params, ret, "list") else []) + (JS_TREE if uses(params, ret, "tree") else [])
    out = ['const lines = require("fs").readFileSync(0, "utf8").split("\\n").map((l) => l.replace(/\\r$/, ""));',
           "let pos = 0;", ""] + prelude
    out += [f"function solve({names}) {{", "  // Write your solution here", "}", ""]
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
        elif t == "list":
            out += [f"const {n}Len = parseInt(lines[pos++], 10);",
                    f"const {n} = buildList({n}Len > 0 ? lines[pos].trim().split(/\\s+/).map(Number) : []);", "pos++;"]
        elif t == "tree":
            out += [f"const {n}Len = parseInt(lines[pos++], 10);",
                    f"const {n} = buildTree({n}Len > 0 ? lines[pos].trim().split(/\\s+/) : []);", "pos++;"]
    out += [f"const result = solve({names});"]
    out += {
        "int": ["console.log(String(result));"],
        "bool": ['console.log(result ? "true" : "false");'],
        "int[]": ['console.log(result.join(" "));'],
        "int[][]": ['console.log(result.map((r) => r.join(" ")).join("\\n"));'],
        "list": ["console.log(listString(result));"],
        "tree": ["console.log(treeString(result));"],
    }[ret]
    out += [""]
    return "\n".join(out)


CPP_T = {"int": "int", "str": "string", "int[]": "vector<int>", "int[][]": "vector<vector<int>>", "grid": "vector<string>",
         "list": "ListNode *", "tree": "TreeNode *"}
CPP_RET = {"int": "int", "bool": "bool", "int[]": "vector<int>", "int[][]": "vector<vector<int>>", "list": "ListNode *", "tree": "TreeNode *"}
CPP_DEFAULT = {"int": "0", "bool": "false", "int[]": "{}", "int[][]": "{}", "list": "nullptr", "tree": "nullptr"}


def starter_cpp(params, ret):
    sig = ", ".join(f"{CPP_T[t]} {n}" for n, t in params)
    names = ", ".join(n for n, _ in params)
    prelude = (CPP_LIST if uses(params, ret, "list") else []) + (CPP_TREE if uses(params, ret, "tree") else [])
    out = ["#include <bits/stdc++.h>", "using namespace std;", ""] + prelude
    out += [f"{CPP_RET[ret]} solve({sig}) {{", "    // Write your solution here", f"    return {CPP_DEFAULT[ret]};", "}", "",
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
        elif t == "list":
            out += [f"    int {n}Len = stoi(lines[pos++]);", f"    vector<int> {n}Vals({n}Len);",
                    f"    if ({n}Len > 0) {{", "        istringstream iss(lines[pos]);",
                    f"        for (auto &v : {n}Vals) iss >> v;", "    }", "    pos++;",
                    f"    ListNode *{n} = buildList({n}Vals);"]
        elif t == "tree":
            out += [f"    int {n}Len = stoi(lines[pos++]);", f"    vector<string> {n}Tok;",
                    f"    if ({n}Len > 0) {{", "        istringstream iss(lines[pos]);", "        string tok;",
                    f"        while (iss >> tok) {n}Tok.push_back(tok);", "    }", "    pos++;",
                    f"    TreeNode *{n} = buildTree({n}Tok);"]
    out += [f"    {CPP_RET[ret]} result = solve({names});"]
    out += {
        "int": ['    cout << result << "\\n";'],
        "bool": ['    cout << (result ? "true" : "false") << "\\n";'],
        "int[]": ["    for (size_t i = 0; i < result.size(); i++) {",
                  '        if (i) cout << " ";', "        cout << result[i];", "    }", '    cout << "\\n";'],
        "int[][]": ["    for (auto &row : result) {", '        cout << row[0] << " " << row[1] << "\\n";', "    }"],
        "list": ['    cout << listString(result) << "\\n";'],
        "tree": ['    cout << treeString(result) << "\\n";'],
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


# ------------------------------------------------------------ batch 3 problems
# Helpers carry a b3_ prefix so they cannot shadow anything defined earlier; only slugs not already present are kept.
import collections


def b3_to_roman(n):
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = []
    for v, s in vals:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


def b3_roman_to_int(s):
    m = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, c in enumerate(s):
        if i + 1 < len(s) and m[c] < m[s[i + 1]]:
            total -= m[c]
        else:
            total += m[c]
    return total


def b3_last_word(s):
    return len(s.split()[-1])


def b3_happy_number(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1


def b3_power_of_two(n):
    return n > 0 and n & (n - 1) == 0


def b3_counting_bits(n):
    return [bin(i).count("1") for i in range(n + 1)]


def b3_stock_two(prices):
    return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))


def b3_two_sum_sorted(nums, target):
    i, j = 0, len(nums) - 1
    while i < j:
        s = nums[i] + nums[j]
        if s == target:
            return [i + 1, j + 1]
        if s < target:
            i += 1
        else:
            j -= 1
    raise AssertionError("no solution")


def b3_intersect_two(a, b):
    c = collections.Counter(a) & collections.Counter(b)
    return sorted(c.elements())


def b3_reverse_integer(x):
    sign = -1 if x < 0 else 1
    r = sign * int(str(abs(x))[::-1])
    return r if -2**31 <= r <= 2**31 - 1 else 0


def b3_jump_game_two(nums):
    jumps = cur_end = far = 0
    for i in range(len(nums) - 1):
        far = max(far, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = far
    return jumps


def b3_h_index(c):
    c = sorted(c, reverse=True)
    h = 0
    while h < len(c) and c[h] >= h + 1:
        h += 1
    return h


def b3_gas_station(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0
    return start


def b3_candy(r):
    n = len(r)
    c = [1] * n
    for i in range(1, n):
        if r[i] > r[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if r[i] > r[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)


def b3_longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best


def b3_three_sum_count(nums):
    nums = sorted(nums)
    n, cnt = len(nums), 0
    for i in range(n - 2):
        if i and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                cnt += 1
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
    return cnt


def b3_decode_ways(s):
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        if s[i - 1] != "0":
            dp[i] += dp[i - 1]
        if i >= 2 and "10" <= s[i - 2:i] <= "26":
            dp[i] += dp[i - 2]
    return dp[n]


def b3_longest_valid_parens(s):
    st, best = [-1], 0
    for i, c in enumerate(s):
        if c == "(":
            st.append(i)
        else:
            st.pop()
            if not st:
                st.append(i)
            else:
                best = max(best, i - st[-1])
    return best


def b3_min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            v = int(grid[i][j])
            if i == 0 and j == 0:
                dp[i][j] = v
            elif i == 0:
                dp[i][j] = dp[i][j - 1] + v
            elif j == 0:
                dp[i][j] = dp[i - 1][j] + v
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1]) + v
    return dp[-1][-1]


def b3_unique_paths_two(grid):
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    dp[0] = 1
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1":
                dp[j] = 0
            elif j:
                dp[j] += dp[j - 1]
    return dp[-1]


def b3_maximal_square(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if grid[i - 1][j - 1] == "1":
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
                best = max(best, dp[i][j])
    return best * best


def b3_rotting_oranges(grid):
    m, n = len(grid), len(grid[0])
    q = collections.deque()
    fresh = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "2":
                q.append((i, j, 0))
            elif grid[i][j] == "1":
                fresh += 1
    seen = {(i, j) for i, j, _ in q}
    t = 0
    while q:
        i, j, t = q.popleft()
        for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= a < m and 0 <= b < n and grid[a][b] == "1" and (a, b) not in seen:
                seen.add((a, b))
                fresh -= 1
                q.append((a, b, t + 1))
    return t if fresh == 0 else -1


def b3_max_area_island(grid):
    m, n = len(grid), len(grid[0])
    seen = set()
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1" and (i, j) not in seen:
                seen.add((i, j))
                st, area = [(i, j)], 0
                while st:
                    x, y = st.pop()
                    area += 1
                    for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= a < m and 0 <= b < n and grid[a][b] == "1" and (a, b) not in seen:
                            seen.add((a, b))
                            st.append((a, b))
                best = max(best, area)
    return best


def b3_perfect_squares(n):
    dp = [0] + [10**9] * n
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j * j] + 1)
            j += 1
    return dp[n]


def b3_erase_overlap(intervals):
    iv = sorted(intervals, key=lambda x: x[1])
    end, keep = -10**9, 0
    for s, e in iv:
        if s >= end:
            keep += 1
            end = e
    return len(iv) - keep


def b3_meeting_rooms(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()
    cur = best = 0
    for _, d in events:
        cur += d
        best = max(best, cur)
    return best


def b3_insert_interval(intervals, new):
    res, placed = [], False
    s, e = new
    for a, b in intervals:
        if b < s:
            res.append([a, b])
        elif a > e:
            if not placed:
                res.append([s, e])
                placed = True
            res.append([a, b])
        else:
            s, e = min(s, a), max(e, b)
    if not placed:
        res.append([s, e])
    return res


def b3_koko(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(-(-p // mid) for p in piles) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo


def b3_ship_packages(weights, days):
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        d, cur = 1, 0
        for w in weights:
            if cur + w > mid:
                d += 1
                cur = 0
            cur += w
        if d <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo


def b3_split_array(nums, k):
    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        parts, cur = 1, 0
        for x in nums:
            if cur + x > mid:
                parts += 1
                cur = 0
            cur += x
        if parts <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


def b3_partition_labels(s):
    last = {c: i for i, c in enumerate(s)}
    res, start, end = [], 0, 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            res.append(end - start + 1)
            start = i + 1
    return res


def b3_min_size_subarray(target, nums):
    best, left, s = 10**9, 0, 0
    for r, x in enumerate(nums):
        s += x
        while s >= target:
            best = min(best, r - left + 1)
            s -= nums[left]
            left += 1
    return 0 if best == 10**9 else best


def b3_char_replacement(s, k):
    cnt = collections.Counter()
    left = best = maxf = 0
    for r, c in enumerate(s):
        cnt[c] += 1
        maxf = max(maxf, cnt[c])
        while r - left + 1 - maxf > k:
            cnt[s[left]] -= 1
            left += 1
        best = max(best, r - left + 1)
    return best


def b3_perm_in_string(s1, s2):
    if len(s1) > len(s2):
        return False
    need = collections.Counter(s1)
    win = collections.Counter(s2[:len(s1)])
    if win == need:
        return True
    for i in range(len(s1), len(s2)):
        win[s2[i]] += 1
        out = s2[i - len(s1)]
        win[out] -= 1
        if win[out] == 0:
            del win[out]
        if win == need:
            return True
    return False


def b3_sliding_max(nums, k):
    dq, out = collections.deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


# ---- case generators
def b3_rgrid(m, n, chars, weights=None):
    return ["".join(rng.choices(chars, weights=weights, k=n)) for _ in range(m)]


def b3_roman_cases():
    cases = ["III", "LVIII", "MCMXCIV", "IV", "IX", "I", "MMMCMXCIX", "XL", "CD", "CM"]
    for _ in range(3):
        cases.append(b3_to_roman(rng.randint(1, 3999)))
    return cases


def b3_last_word_cases():
    cases = ["Hello World", "fly me   to   the moon", "a", "luffy is still joyboy", "word  word"]
    for n in (5, 30, 100):
        words = ["".join(rng.choice("abcdefgh") for _ in range(rng.randint(1, 8))) for _ in range(n // 5 + 1)]
        cases.append(" ".join(words))
    return cases


def b3_sorted_pair_cases():
    cases = [([2, 7, 11, 15], 9), ([2, 3, 4], 6), ([-1, 0], -1), ([1, 2, 3, 4, 4, 9, 56, 90], 8)]
    for n in (10, 100, 1000):
        arr = sorted(rng.sample(range(-10**4, 10**4), n))
        i, j = sorted(rng.sample(range(n), 2))
        cases.append((arr, arr[i] + arr[j]))
    return cases


def b3_intersect_cases():
    cases = [([1, 2, 2, 1], [2, 2]), ([4, 9, 5], [9, 4, 9, 8, 4]), ([1], [1]), ([3, 1, 2], [1, 3])]
    for n, m in ((20, 30), (200, 150), (1000, 800)):
        a, b = rand_arr(n, 0, 30), rand_arr(m, 0, 30)
        cases.append((a, b))
    return cases


def b3_reverse_int_cases():
    return [123, -123, 120, 0, 1534236469, -2147483648, 2147483647, 1463847412, -1563847412, 7, -10, 1000000003]


def b3_jump2_cases():
    cases = [[2, 3, 1, 1, 4], [2, 3, 0, 1, 4], [1], [1, 1, 1, 1], [5, 1, 1, 1, 1, 1]]
    for n in (20, 200, 1000):
        arr = [rng.randint(1, 5) for _ in range(n - 1)] + [0]
        cases.append(arr)
    return cases


def b3_hindex_cases():
    cases = [[3, 0, 6, 1, 5], [1, 3, 1], [0], [100], [0, 0, 0], [5, 5, 5, 5, 5]]
    for n in (20, 200, 1000):
        cases.append(rand_arr(n, 0, 600))
    return cases


def b3_gas_cases():
    cases = [([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), ([2, 3, 4], [3, 4, 3]), ([5], [4]), ([3, 1, 1], [1, 2, 2])]
    for n in (10, 100, 1000):
        while True:
            gas, cost = rand_arr(n, 0, 20), rand_arr(n, 0, 20)
            if rng.random() < 0.7:
                cost = [min(c, g + rng.randint(0, 3)) for c, g in zip(cost, gas)]
            if sum(gas) >= sum(cost) or rng.random() < 0.3:
                cases.append((gas, cost))
                break
    return cases


def b3_candy_cases():
    cases = [[1, 0, 2], [1, 2, 2], [1], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [1, 3, 2, 2, 1], [2, 2, 2]]
    for n in (20, 200, 1000):
        cases.append(rand_arr(n, 0, 50))
    return cases


def b3_consec_cases():
    cases = [[100, 4, 200, 1, 3, 2], [0, 3, 7, 2, 5, 8, 4, 6, 0, 1], [1], [1, 2, 0, 1], [9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]]
    for n in (20, 200, 1000):
        cases.append(rand_arr(n, -300, 300))
    return cases


def b3_three_sum_cases():
    cases = [[-1, 0, 1, 2, -1, -4], [0, 1, 1], [0, 0, 0], [0, 0, 0, 0], [-2, 0, 1, 1, 2], [1, 2, 3]]
    for n in (20, 100, 500):
        cases.append(rand_arr(n, -60, 60))
    return cases


def b3_decode_cases():
    cases = ["12", "226", "06", "0", "10", "27", "11106", "1", "2101", "100"]
    for n in (10, 40, 100):
        cases.append("".join(rng.choice("0123456789" if rng.random() < .3 else "12126") for _ in range(n)))
    return cases


def b3_vparen_cases():
    cases = ["(()", ")()())", "", "()", "()(())", ")(", "(((", "()()", "(()()(()"]
    cases = [c for c in cases if c]
    for n in (20, 200, 1000):
        cases.append("".join(rng.choice("()") for _ in range(n)))
    return cases


def b3_mps_cases():
    return [b3_rgrid(3, 3, "0123456789"), ["1"], ["12", "51"], ["13", "11"], b3_rgrid(1, 7, "0123456789"), b3_rgrid(7, 1, "0123456789"),
            b3_rgrid(10, 10, "0123456789"), b3_rgrid(30, 40, "0123456789"), b3_rgrid(50, 50, "0123456789")]


def b3_up2_cases():
    cases = [["000", "010", "000"], ["00", "10"], ["0"], ["1"], ["01", "00"], ["00", "01"]]
    for m, n in ((5, 5), (8, 12), (12, 12)):
        cases.append(b3_rgrid(m, n, "01", [9, 1]))
    return cases


def b3_square_cases():
    cases = [["10100", "10111", "11111", "10010"], ["01", "10"], ["0"], ["1"], ["11", "11"]]
    for m, n in ((6, 6), (15, 20), (50, 50)):
        cases.append(b3_rgrid(m, n, "01", [1, 3]))
    return cases


def b3_rot_cases():
    cases = [["211", "110", "011"], ["211", "011", "101"], ["02"], ["0"], ["1"], ["2"], ["1112"]]
    for m, n in ((5, 5), (10, 12), (30, 30)):
        cases.append(b3_rgrid(m, n, "012", [2, 6, 1]))
    return cases


def b3_island_cases():
    cases = [["11000", "11000", "00100", "00011"], ["0"], ["1"], ["101", "010", "101"], ["111", "111"]]
    for m, n in ((6, 6), (20, 20), (50, 50)):
        cases.append(b3_rgrid(m, n, "01", [1, 1]))
    return cases


def b3_interval_pairs(n, hi=100, minlen=1, maxlen=20):
    out = []
    for _ in range(n):
        s = rng.randint(0, hi)
        out.append([s, s + rng.randint(minlen, maxlen)])
    return out


def b3_nonoverlap_cases():
    cases = [[[1, 2], [2, 3], [3, 4], [1, 3]], [[1, 2], [1, 2], [1, 2]], [[1, 2], [2, 3]], [[0, 5]]]
    for n in (10, 100, 190):
        cases.append(b3_interval_pairs(n, 500, 1, 30))
    return cases


def b3_rooms_cases():
    cases = [[[0, 30], [5, 10], [15, 20]], [[7, 10], [2, 4]], [[0, 5], [5, 10]], [[1, 2]], [[1, 5], [2, 6], [3, 7], [4, 8]]]
    for n in (10, 100, 190):
        cases.append(b3_interval_pairs(n, 500, 1, 60))
    return cases


def b3_insert_cases_iv():
    cases = [([[1, 3], [6, 9]], [2, 5]), ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]), ([[1, 5]], [2, 3]),
             ([[1, 5]], [6, 8]), ([[3, 5]], [0, 1]), ([[1, 5]], [0, 6])]
    for n in (10, 50, 150):
        pts = sorted(rng.sample(range(0, 2000), n * 2))
        iv = [[pts[2 * i], pts[2 * i + 1]] for i in range(n)]
        s = rng.randint(0, 2000)
        cases.append((iv, [s, s + rng.randint(0, 200)]))
    return cases


def b3_koko_cases():
    cases = [([3, 6, 7, 11], 8), ([30, 11, 23, 4, 20], 5), ([30, 11, 23, 4, 20], 6), ([1], 1), ([10], 3)]
    for n in (10, 100, 1000):
        piles = rand_arr(n, 1, 10**4)
        cases.append((piles, rng.randint(n, 3 * n)))
    return cases


def b3_ship_cases():
    cases = [([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5), ([3, 2, 2, 4, 1, 4], 3), ([1, 2, 3, 1, 1], 4), ([5], 1)]
    for n in (10, 100, 1000):
        w = rand_arr(n, 1, 500)
        cases.append((w, rng.randint(1, n)))
    return cases


def b3_split_cases():
    cases = [([7, 2, 5, 10, 8], 2), ([1, 2, 3, 4, 5], 2), ([1, 4, 4], 3), ([10], 1), ([1, 1, 1, 1], 4)]
    for n in (10, 100, 500):
        a = rand_arr(n, 0, 1000)
        cases.append((a, rng.randint(1, min(n, 50))))
    return cases


def b3_plabels_cases():
    cases = ["ababcbacadefegdehijhklij", "eccbbbbdec", "a", "abc", "aaaa", "abab"]
    for n in (30, 200, 500):
        cases.append("".join(rng.choice("abcdefghijklmnop") for _ in range(n)))
    return cases


def b3_minsub_cases():
    cases = [(7, [2, 3, 1, 2, 4, 3]), (4, [1, 4, 4]), (11, [1, 1, 1, 1, 1, 1, 1, 1]), (5, [5]), (3, [1, 1])]
    for n in (10, 100, 1000):
        a = rand_arr(n, 1, 100)
        cases.append((rng.randint(1, sum(a) + 5), a))
    return cases


def b3_charrep_cases():
    cases = [("ABAB", 2), ("AABABBA", 1), ("A", 0), ("ABC", 0), ("AAAA", 2), ("ABCDE", 4)]
    for n in (30, 300, 1000):
        cases.append(("".join(rng.choice("ABCDE") for _ in range(n)), rng.randint(0, 20)))
    return cases


def b3_perm_str_cases():
    cases = [("ab", "eidbaooo"), ("ab", "eidboaoo"), ("a", "a"), ("abc", "ab"), ("adc", "dcda"), ("hello", "ooolleoooleh")]
    for n, m in ((3, 40), (5, 300), (10, 800)):
        s1 = "".join(rng.choice("abcd") for _ in range(n))
        s2 = "".join(rng.choice("abcd") for _ in range(m))
        if rng.random() < 0.5:
            i = rng.randint(0, m - n)
            p = list(s1)
            rng.shuffle(p)
            s2 = s2[:i] + "".join(p) + s2[i + n:]
        cases.append((s1, s2))
    return cases


def b3_slidemax_cases():
    cases = [([1, 3, -1, -3, 5, 3, 6, 7], 3), ([1], 1), ([9, 11], 2), ([4, 3, 2, 1], 2), ([1, 2, 3, 4], 4)]
    for n in (20, 200, 1000):
        cases.append((rand_arr(n, -10**4, 10**4), rng.randint(1, min(n, 100))))
    return cases


b3_NBITS = [0, 1, 2, 5, 16, 31, 100, 255, 1000, 5000]

_B3_ALL = [
    mk("roman-to-integer", "Roman to Integer", "EASY", ["math", "string"], [("s", "str")], "int", b3_roman_to_int,
       b3_roman_cases(),
       "Convert a Roman numeral to an integer. Symbols are `I=1, V=5, X=10, L=50, C=100, D=500, M=1000`. A smaller "
       "symbol placed before a larger one is subtracted (`IV = 4`, `IX = 9`, `XL = 40`, `XC = 90`, `CD = 400`, "
       "`CM = 900`).", "A single line containing the numeral.", "The integer value.",
       ["The numeral is valid and represents a value from `1` to `3999`"]),
    mk("length-of-last-word", "Length of Last Word", "EASY", ["string"], [("s", "str")], "int", b3_last_word,
       b3_last_word_cases(),
       "A string consists of words separated by one or more spaces. Return the length of the last word.",
       "A single line containing `s` (no leading or trailing spaces).", "The length of the last word.",
       ["`1 <= s.length <= 600`", "Lowercase letters and spaces; at least one word"]),
    mk("happy-number", "Happy Number", "EASY", ["math", "hash-table"], [("n", "int")], "bool", b3_happy_number,
       [19, 2, 1, 7, 4, 100, 116, 999, 1111111, 2147483647, 3, 10],
       "Repeatedly replace `n` with the sum of the squares of its digits. `n` is happy if this process reaches `1`, "
       "and unhappy if it loops forever in a cycle that does not include `1`.", "A single integer `n`.",
       "`true` if `n` is happy, otherwise `false`.", ["`1 <= n <= 2^31 - 1`"]),
    mk("power-of-two", "Power of Two", "EASY", ["math", "bit-manipulation"], [("n", "int")], "bool", b3_power_of_two,
       [1, 16, 3, 0, -16, 2, 1024, 1023, 2147483647, -2147483648, 1073741824, 6],
       "Return `true` if `n` is a power of two (`1, 2, 4, 8, …`).", "A single integer `n`.", "`true` or `false`.",
       ["`-2^31 <= n <= 2^31 - 1`"]),
    mk("counting-bits", "Counting Bits", "EASY", ["dynamic-programming", "bit-manipulation"], [("n", "int")], "int[]",
       b3_counting_bits, b3_NBITS,
       "For every `i` from `0` to `n`, count the number of `1` bits in the binary form of `i`. Return the `n + 1` "
       "counts in order. A linear-time solution exists.", "A single integer `n`.",
       "`n + 1` space-separated integers.", ["`0 <= n <= 5000`"]),
    mk("best-time-to-buy-and-sell-stock-ii", "Best Time to Buy and Sell Stock II", "MEDIUM", ["array", "greedy"],
       [("prices", "int[]")], "int", b3_stock_two,
       [[7, 1, 5, 3, 6, 4], [1, 2, 3, 4, 5], [7, 6, 4, 3, 1], [1], [2, 1, 2, 0, 1], rand_arr(50, 0, 100),
        rand_arr(500, 0, 10000), rand_arr(1000, 0, 10000)],
       "You may buy and sell a stock many times, holding at most one share at any moment (you may sell and buy on "
       "the same day). Return the maximum total profit.", ARR_IN, "The maximum profit.",
       ["`1 <= n <= 1000`", "`0 <= prices[i] <= 10^4`"]),
    mk("two-sum-ii-input-array-is-sorted", "Two Sum II - Input Array Is Sorted", "EASY", ["array", "two-pointers"],
       [("numbers", "int[]"), ("target", "int")], "int[]", b3_two_sum_sorted, b3_sorted_pair_cases(),
       "A **sorted** (non-decreasing) array is given. Find two numbers that add to `target` and return their "
       "**1-based** indices `index1 < index2`. Exactly one solution exists; use only constant extra space.",
       "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `target`.", "`index1 index2`, separated by a space.",
       ["`2 <= n <= 1000`", "A unique valid pair exists"]),
    mk("intersection-of-two-arrays-ii", "Intersection of Two Arrays II", "EASY", ["array", "hash-table", "sorting"],
       [("nums1", "int[]"), ("nums2", "int[]")], "int[]", b3_intersect_two, b3_intersect_cases(),
       "Return the intersection of two arrays, where each value appears as many times as it appears in **both** "
       "arrays. Print the result sorted ascending.",
       "Line 1: length of `nums1`.\nLine 2: `nums1`.\nLine 3: length of `nums2`.\nLine 4: `nums2`.",
       "The intersection, sorted ascending, space-separated.",
       ["`1 <= length <= 1000`", "`0 <= value <= 1000`", "The intersection is never empty"]),
    mk("reverse-integer", "Reverse Integer", "MEDIUM", ["math"], [("x", "int")], "int", b3_reverse_integer,
       b3_reverse_int_cases(),
       "Reverse the decimal digits of a signed 32-bit integer. If the reversed value falls outside "
       "`[-2^31, 2^31 - 1]`, return `0`.", "A single integer `x`.", "The reversed integer, or `0` on overflow.",
       ["`-2^31 <= x <= 2^31 - 1`"]),
    mk("jump-game-ii", "Jump Game II", "MEDIUM", ["array", "greedy", "dynamic-programming"], [("nums", "int[]")],
       "int", b3_jump_game_two, b3_jump2_cases(),
       "You start at index `0`; `nums[i]` is the maximum jump length from `i`. Return the minimum number of jumps to "
       "reach the last index. The last index is always reachable.", ARR_IN, "The minimum number of jumps.",
       ["`1 <= n <= 1000`", "`0 <= nums[i] <= 1000`", "The end is reachable"]),
    mk("h-index", "H-Index", "MEDIUM", ["array", "sorting", "counting-sort"], [("citations", "int[]")], "int", b3_h_index,
       b3_hindex_cases(),
       "`citations[i]` is the number of citations of the `i`-th paper. The h-index is the largest `h` such that the "
       "researcher has at least `h` papers with at least `h` citations each.", ARR_IN, "The h-index.",
       ["`1 <= n <= 1000`", "`0 <= citations[i] <= 1000`"]),
    mk("gas-station", "Gas Station", "MEDIUM", ["array", "greedy"], [("gas", "int[]"), ("cost", "int[]")], "int",
       b3_gas_station, b3_gas_cases(),
       "There are `n` stations on a circular route. Station `i` gives `gas[i]` fuel and the trip to station `i + 1` "
       "costs `cost[i]`. Starting with an empty tank, return the index of the station from which you can complete "
       "one full lap clockwise, or `-1` if impossible. If a solution exists it is unique.",
       "Line 1: `n`.\nLine 2: `gas`.\nLine 3: `n`.\nLine 4: `cost`.", "The starting index, or `-1`.",
       ["`1 <= n <= 1000`", "`0 <= gas[i], cost[i] <= 100`"]),
    mk("candy", "Candy", "HARD", ["array", "greedy"], [("ratings", "int[]")], "int", b3_candy, b3_candy_cases(),
       "Children stand in a line, each with a rating. Give every child at least one candy, and any child with a "
       "higher rating than an adjacent child must receive more candy than that neighbour. Return the minimum total "
       "candy.", "Line 1: `n`.\nLine 2: `n` ratings.", "The minimum number of candies.",
       ["`1 <= n <= 1000`", "`0 <= ratings[i] <= 10^4`"]),
    mk("longest-consecutive-sequence", "Longest Consecutive Sequence", "MEDIUM", ["array", "hash-table", "union-find"],
       [("nums", "int[]")], "int", b3_longest_consecutive, b3_consec_cases(),
       "Return the length of the longest run of consecutive integers (such as `3, 4, 5, 6`) that can be formed from "
       "the values of `nums`, in any order. Aim for `O(n)` time.", ARR_IN, "The length of the longest run.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("three-sum-count", "3Sum (Count)", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]")], "int",
       b3_three_sum_count, b3_three_sum_cases(),
       "Count the **distinct value triplets** `(a, b, c)` taken from different indices such that `a + b + c = 0`. "
       "Two triplets are the same if they contain the same multiset of values.", ARR_IN,
       "The number of distinct triplets.", ["`3 <= n <= 500`", "`-10^5 <= nums[i] <= 10^5`"]),
    mk("decode-ways", "Decode Ways", "MEDIUM", ["string", "dynamic-programming"], [("s", "str")], "int", b3_decode_ways,
       b3_decode_cases(),
       "Letters map to numbers (`A=1, B=2, …, Z=26`). Given a string of digits, return the number of ways to decode "
       "it. A leading `0` cannot be decoded on its own, and `06` is not `6`.", "A single line of digits.",
       "The number of decodings (`0` if none).", ["`1 <= s.length <= 100`", "Digits only", "The answer fits in 32 bits"]),
    mk("longest-valid-parentheses", "Longest Valid Parentheses", "HARD", ["string", "stack", "dynamic-programming"],
       [("s", "str")], "int", b3_longest_valid_parens, b3_vparen_cases(),
       "Given a string of `(` and `)`, return the length of the longest contiguous substring that is a valid, "
       "well-formed set of parentheses.", "A single line `s`.", "The length of the longest valid substring.",
       ["`1 <= s.length <= 1000`"]),
    mk("minimum-path-sum", "Minimum Path Sum", "MEDIUM", ["matrix", "dynamic-programming"], [("grid", "grid")], "int",
       b3_min_path_sum, b3_mps_cases(),
       "A grid of digits gives the cost of each cell. Moving only right or down from the top-left to the "
       "bottom-right cell, return the minimum total cost of a path, including both endpoints.",
       "Line 1: `rows cols`.\nNext `rows` lines: `cols` digits each.", "The minimum path sum.",
       ["`1 <= rows, cols <= 50`", "Each cell is a digit `0`-`9`"]),
    mk("unique-paths-ii", "Unique Paths II", "MEDIUM", ["matrix", "dynamic-programming"], [("grid", "grid")], "int",
       b3_unique_paths_two, b3_up2_cases(),
       "A robot moves only right or down from the top-left to the bottom-right of a grid. Cells marked `1` are "
       "obstacles and cannot be entered. Return the number of distinct paths.",
       "Line 1: `rows cols`.\nNext `rows` lines: `cols` characters, `0` (free) or `1` (obstacle).",
       "The number of paths.", ["`1 <= rows, cols <= 12`", "The answer fits in 32 bits"]),
    mk("maximal-square", "Maximal Square", "MEDIUM", ["matrix", "dynamic-programming"], [("matrix", "grid")], "int",
       b3_maximal_square, b3_square_cases(),
       "In a binary grid, find the largest square made only of `1` cells and return its **area**.",
       "Line 1: `rows cols`.\nNext `rows` lines: `cols` characters, `0` or `1`.", "The area of the largest square.",
       ["`1 <= rows, cols <= 50`"]),
    mk("rotting-oranges", "Rotting Oranges", "MEDIUM", ["matrix", "breadth-first-search"], [("grid", "grid")], "int",
       b3_rotting_oranges, b3_rot_cases(),
       "A grid cell is `0` (empty), `1` (fresh orange) or `2` (rotten orange). Each minute every fresh orange next to "
       "a rotten one (up, down, left, right) becomes rotten. Return the minutes until no fresh orange remains, or "
       "`-1` if some can never rot.", "Line 1: `rows cols`.\nNext `rows` lines: `cols` characters from `0`, `1`, `2`.",
       "The number of minutes, or `-1`.", ["`1 <= rows, cols <= 30`"]),
    mk("max-area-of-island", "Max Area of Island", "MEDIUM", ["matrix", "depth-first-search"], [("grid", "grid")],
       "int", b3_max_area_island, b3_island_cases(),
       "An island is a group of `1` cells connected horizontally or vertically. Return the area (cell count) of the "
       "largest island, or `0` if there is none.",
       "Line 1: `rows cols`.\nNext `rows` lines: `cols` characters, `0` or `1`.", "The largest island area.",
       ["`1 <= rows, cols <= 50`"]),
    mk("perfect-squares", "Perfect Squares", "MEDIUM", ["math", "dynamic-programming"], [("n", "int")], "int",
       b3_perfect_squares, [12, 13, 1, 2, 4, 7, 100, 9999, 10000, 5000, 3, 43],
       "Return the least number of perfect square numbers (`1, 4, 9, 16, …`) that sum to `n`.",
       "A single integer `n`.", "The minimum count.", ["`1 <= n <= 10000`"]),
    mk("non-overlapping-intervals", "Non-overlapping Intervals", "MEDIUM", ["array", "greedy", "sorting"],
       [("intervals", "int[][]")], "int", b3_erase_overlap, b3_nonoverlap_cases(),
       "Return the minimum number of intervals to remove so that the remaining intervals do not overlap. Intervals "
       "that only touch at an endpoint (`[1,2]` and `[2,3]`) do not overlap.",
       "Line 1: `n`.\nNext `n` lines: `start end`.", "The minimum number of removals.",
       ["`1 <= n <= 190`", "`start < end`"]),
    mk("meeting-rooms-ii", "Meeting Rooms II", "MEDIUM", ["array", "heap", "greedy", "sorting"],
       [("intervals", "int[][]")], "int", b3_meeting_rooms, b3_rooms_cases(),
       "Given meeting time intervals `[start, end)`, return the minimum number of rooms needed. A meeting that ends "
       "at time `t` frees its room for one that starts at `t`.", "Line 1: `n`.\nNext `n` lines: `start end`.",
       "The minimum number of rooms.", ["`1 <= n <= 190`", "`start < end`"]),
    mk("insert-interval", "Insert Interval", "MEDIUM", ["array", "intervals"],
       [("intervals", "int[][]"), ("newInterval", "int[]")], "int[][]", b3_insert_interval, b3_insert_cases_iv(),
       "A list of non-overlapping intervals is sorted by start. Insert `newInterval`, merging anything it overlaps "
       "(touching intervals merge too), and return the resulting sorted, non-overlapping list.",
       "Line 1: `n`.\nNext `n` lines: `start end`.\nThen a line containing `2`, then a line `start end` for "
       "`newInterval`.", "The resulting intervals, one `start end` pair per line.",
       ["`1 <= n <= 150`", "Input intervals are sorted and do not overlap"]),
    mk("koko-eating-bananas", "Koko Eating Bananas", "MEDIUM", ["array", "binary-search"],
       [("piles", "int[]"), ("h", "int")], "int", b3_koko, b3_koko_cases(),
       "Koko has banana piles and `h` hours. Each hour she picks one pile and eats up to `k` bananas from it (finishing "
       "early wastes the rest of that hour). Return the smallest integer `k` that lets her finish within `h` hours.",
       "Line 1: `n`.\nLine 2: the piles.\nLine 3: `h`.", "The minimum speed `k`.",
       ["`1 <= n <= 1000`", "`n <= h`", "`1 <= piles[i] <= 10^4`"]),
    mk("capacity-to-ship-packages", "Capacity To Ship Packages Within D Days", "MEDIUM", ["array", "binary-search"],
       [("weights", "int[]"), ("days", "int")], "int", b3_ship_packages, b3_ship_cases(),
       "Packages must be shipped in the given order, loaded onto a ship each day up to its capacity. Return the "
       "least ship capacity that delivers everything within `days` days.",
       "Line 1: `n`.\nLine 2: the weights.\nLine 3: `days`.", "The minimum capacity.",
       ["`1 <= days <= n <= 1000`", "`1 <= weights[i] <= 500`"]),
    mk("split-array-largest-sum", "Split Array Largest Sum", "HARD", ["array", "binary-search", "dynamic-programming"],
       [("nums", "int[]"), ("k", "int")], "int", b3_split_array, b3_split_cases(),
       "Split `nums` into `k` non-empty contiguous subarrays so that the largest subarray sum is as small as "
       "possible, and return that minimised sum.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.",
       "The minimised largest sum.", ["`1 <= k <= n <= 500`", "`0 <= nums[i] <= 1000`"]),
    mk("partition-labels", "Partition Labels", "MEDIUM", ["string", "greedy", "two-pointers"], [("s", "str")],
       "int[]", b3_partition_labels, b3_plabels_cases(),
       "Partition a string into as many parts as possible so that each letter appears in at most one part. Return "
       "the sizes of the parts in order.", "A single line `s`.", "The part sizes, space-separated.",
       ["`1 <= s.length <= 500`", "Lowercase letters"]),
    mk("minimum-size-subarray-sum", "Minimum Size Subarray Sum", "MEDIUM", ["array", "sliding-window", "binary-search"],
       [("target", "int"), ("nums", "int[]")], "int", b3_min_size_subarray, b3_minsub_cases(),
       "Return the minimal length of a contiguous subarray of positive integers whose sum is at least `target`, or "
       "`0` if no subarray qualifies.", "Line 1: `target`.\nLine 2: `n`.\nLine 3: `n` integers.",
       "The minimal length, or `0`.", ["`1 <= n <= 1000`", "`1 <= nums[i] <= 100`"]),
    mk("longest-repeating-character-replacement", "Longest Repeating Character Replacement", "MEDIUM",
       ["string", "sliding-window"], [("s", "str"), ("k", "int")], "int", b3_char_replacement, b3_charrep_cases(),
       "You may change at most `k` characters of `s` to any uppercase letter. Return the length of the longest "
       "substring containing a single repeated letter after those changes.", "Line 1: `s`.\nLine 2: `k`.",
       "The length of the longest such substring.", ["`1 <= s.length <= 1000`", "Uppercase letters", "`0 <= k <= s.length`"]),
    mk("permutation-in-string", "Permutation in String", "MEDIUM", ["string", "sliding-window", "two-pointers"],
       [("s1", "str"), ("s2", "str")], "bool", b3_perm_in_string, b3_perm_str_cases(),
       "Return `true` if some permutation of `s1` appears as a contiguous substring of `s2`.",
       "Line 1: `s1`.\nLine 2: `s2`.", "`true` or `false`.",
       ["`1 <= s1.length, s2.length <= 1000`", "Lowercase letters"]),
    mk("sliding-window-maximum", "Sliding Window Maximum", "HARD", ["array", "sliding-window", "heap", "monotonic-queue"],
       [("nums", "int[]"), ("k", "int")], "int[]", b3_sliding_max, b3_slidemax_cases(),
       "A window of size `k` slides from the left end to the right end of `nums`. Return the maximum of each window "
       "position. Aim for `O(n)` time.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.",
       "`n - k + 1` space-separated maxima.", ["`1 <= k <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
]


_B3_KEEP = ["length-of-last-word", "best-time-to-buy-and-sell-stock-ii", "intersection-of-two-arrays-ii", "reverse-integer", "jump-game-ii", "h-index", "candy", "longest-consecutive-sequence", "longest-valid-parentheses", "minimum-path-sum", "max-area-of-island", "insert-interval", "koko-eating-bananas", "capacity-to-ship-packages", "split-array-largest-sum", "partition-labels"]
PROBLEMS += [p for p in _B3_ALL if p["slug"] in _B3_KEEP]


# ================================================================ batch 4: linked lists and binary trees
# Lists are plain Python lists; trees are level-order token lists with None gaps (see the wire format above).
class TN:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def tok2tree(tokens):
    if not tokens or tokens[0] is None:
        return None
    root = TN(tokens[0])
    queue, i = [root], 1
    qi = 0
    while qi < len(queue) and i < len(tokens):
        node = queue[qi]
        qi += 1
        if i < len(tokens) and tokens[i] is not None:
            node.left = TN(tokens[i])
            queue.append(node.left)
        i += 1
        if i < len(tokens) and tokens[i] is not None:
            node.right = TN(tokens[i])
            queue.append(node.right)
        i += 1
    return root


def tree2tok(root):
    out, queue, qi = [], [root], 0
    while qi < len(queue):
        node = queue[qi]
        qi += 1
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def rand_tree(m, lo=-20, hi=50):
    """Random binary tree with m nodes (random shape), as level-order tokens."""
    if m == 0:
        return []
    root = TN(rng.randint(lo, hi))
    slots = [(root, "left"), (root, "right")]
    for _ in range(m - 1):
        node, side = slots.pop(rng.randrange(len(slots)))
        child = TN(rng.randint(lo, hi))
        setattr(node, side, child)
        slots += [(child, "left"), (child, "right")]
    return tree2tok(root)


def rand_bst(m, lo=1, hi=99):
    """Random BST with m distinct values, as level-order tokens."""
    if m == 0:
        return []
    vals = rng.sample(range(lo, hi + 1), m)
    root = TN(vals[0])
    for v in vals[1:]:
        cur = root
        while True:
            side = "left" if v < cur.val else "right"
            nxt = getattr(cur, side)
            if nxt is None:
                setattr(cur, side, TN(v))
                break
            cur = nxt
    return tree2tok(root)


def rand_sorted_list(n, lo=-30, hi=60):
    return sorted(rng.randint(lo, hi) for _ in range(n))


def rand_list(n, lo=-30, hi=60):
    return [rng.randint(lo, hi) for _ in range(n)]


# ---- list references
def b4_reverse(a): return a[::-1]
def b4_merge(a, b): return sorted(a + b)
def b4_middle(a): return a[len(a) // 2:]
def b4_remove_nth(a, n): return a[:len(a) - n] + a[len(a) - n + 1:]
def b4_palin_list(a): return a == a[::-1]


def b4_dedup_sorted(a):
    out = []
    for v in a:
        if not out or out[-1] != v:
            out.append(v)
    return out


def b4_add_numbers(a, b):
    x = int("".join(map(str, a[::-1])))
    y = int("".join(map(str, b[::-1])))
    return [int(c) for c in str(x + y)[::-1]]


def b4_swap_pairs(a):
    out = list(a)
    for i in range(0, len(out) - 1, 2):
        out[i], out[i + 1] = out[i + 1], out[i]
    return out


def b4_odd_even(a): return a[0::2] + a[1::2]
def b4_sort_list(a): return sorted(a)


def b4_reorder(a):
    out, i, j = [], 0, len(a) - 1
    while i <= j:
        out.append(a[i])
        if i != j:
            out.append(a[j])
        i += 1
        j -= 1
    return out


def b4_reverse_k(a, k):
    out = []
    for i in range(0, len(a), k):
        chunk = a[i:i + k]
        out += chunk[::-1] if len(chunk) == k else chunk
    return out


# ---- tree references
def b4_depth(t):
    def d(n): return 0 if n is None else 1 + max(d(n.left), d(n.right))
    return d(tok2tree(t))


def b4_invert(t):
    def inv(n):
        if n is None:
            return None
        return TN(n.val, inv(n.right), inv(n.left))
    return tree2tok(inv(tok2tree(t)))


def b4_symmetric(t):
    def mirror(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
    root = tok2tree(t)
    return root is None or mirror(root.left, root.right)


def b4_same(p, q):
    def same(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)
    return same(tok2tree(p), tok2tree(q))


def b4_diameter(t):
    best = 0

    def h(n):
        nonlocal best
        if n is None:
            return 0
        l, r = h(n.left), h(n.right)
        best = max(best, l + r)
        return 1 + max(l, r)
    h(tok2tree(t))
    return best


def b4_inorder(t):
    out = []

    def go(n):
        if n:
            go(n.left)
            out.append(n.val)
            go(n.right)
    go(tok2tree(t))
    return out


def b4_right_view(t):
    root = tok2tree(t)
    out, level = [], [root] if root else []
    while level:
        out.append(level[-1].val)
        level = [c for n in level for c in (n.left, n.right) if c]
    return out


def b4_valid_bst(t):
    def ok(n, lo, hi):
        if n is None:
            return True
        return lo < n.val < hi and ok(n.left, lo, n.val) and ok(n.right, n.val, hi)
    return ok(tok2tree(t), float("-inf"), float("inf"))


def b4_path_sum(t, target):
    def go(n, rem):
        if n is None:
            return False
        if n.left is None and n.right is None:
            return n.val == rem
        return go(n.left, rem - n.val) or go(n.right, rem - n.val)
    return go(tok2tree(t), target)


def b4_balanced(t):
    def h(n):
        if n is None:
            return 0
        l, r = h(n.left), h(n.right)
        if l < 0 or r < 0 or abs(l - r) > 1:
            return -1
        return 1 + max(l, r)
    return h(tok2tree(t)) >= 0


def b4_kth_bst(t, k): return b4_inorder(t)[k - 1]


def b4_good_nodes(t):
    def go(n, mx):
        if n is None:
            return 0
        return (1 if n.val >= mx else 0) + go(n.left, max(mx, n.val)) + go(n.right, max(mx, n.val))
    root = tok2tree(t)
    return go(root, root.val) if root else 0


def b4_max_path(t):
    best = float("-inf")

    def h(n):
        nonlocal best
        if n is None:
            return 0
        l, r = max(0, h(n.left)), max(0, h(n.right))
        best = max(best, n.val + l + r)
        return n.val + max(l, r)
    h(tok2tree(t))
    return best


def b4_lca_bst(t, p, q):
    n = tok2tree(t)
    while n:
        if p < n.val and q < n.val:
            n = n.left
        elif p > n.val and q > n.val:
            n = n.right
        else:
            return n.val


def b4_lca(t, p, q):
    def go(n):
        if n is None or n.val in (p, q):
            return n
        l, r = go(n.left), go(n.right)
        return n if l and r else (l or r)
    return go(tok2tree(t)).val


# ---- case generators (the first two are shown as the problem's examples)
def b4_lists(sizes, **kw): return [rand_list(n, **kw) for n in sizes]


def b4_c_reverse(): return [[1, 2, 3, 4, 5], [1, 2], [], [7]] + b4_lists([2, 3, 10, 30, 60, 100])
def b4_c_merge(): return [([1, 2, 4], [1, 3, 4]), ([], [])] + [([], [5]), ([0], [])] + [(rand_sorted_list(rng.randint(0, 40)), rand_sorted_list(rng.randint(0, 40))) for _ in range(6)]
def b4_c_middle(): return [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6], [9]] + b4_lists([2, 3, 10, 11, 50, 99], lo=-50, hi=50)
def b4_c_remove_nth():
    cases = [([1, 2, 3, 4, 5], 2), ([1], 1), ([1, 2], 1), ([1, 2], 2)]
    for n in [3, 10, 30, 60, 100]:
        cases.append((rand_list(n), rng.randint(1, n)))
    return cases
def b4_c_palin_list():
    return [[1, 2, 2, 1], [1, 2], [1], [1, 2, 1], [1, 2, 3, 2, 1], [1, 2, 3, 4], [5, 5, 5, 5], [1, 2, 3, 3, 1]] + [x + x[::-1][len(x) % 2:] for x in (rand_list(20, 0, 9), rand_list(41, 0, 9))] + [rand_list(30, 0, 9)]
def b4_c_dedup(): return [[1, 1, 2], [1, 1, 2, 3, 3], [], [4], [7, 7, 7, 7]] + [rand_sorted_list(n, 0, 15) for n in (5, 20, 60, 100)]
def b4_c_add():
    def digits(n): return [rng.randint(0, 9) for _ in range(n - 1)] + [rng.randint(1, 9)]
    return [([2, 4, 3], [5, 6, 4]), ([0], [0]), ([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]), ([1], [9, 9, 9]), ([5], [5])] + [(digits(rng.randint(1, 30)), digits(rng.randint(1, 30))) for _ in range(5)]
def b4_c_swap(): return [[1, 2, 3, 4], [1], [], [1, 2, 3]] + b4_lists([2, 4, 9, 40, 99])
def b4_c_odd_even(): return [[1, 2, 3, 4, 5], [2, 1, 3, 5, 6, 4, 7], [1], [1, 2]] + b4_lists([3, 8, 15, 50, 100])
def b4_c_sort(): return [[4, 2, 1, 3], [-1, 5, 3, 4, 0], [], [3]] + b4_lists([2, 10, 40, 100, 100], lo=-100, hi=100)
def b4_c_reorder(): return [[1, 2, 3, 4], [1, 2, 3, 4, 5], [1], [1, 2]] + b4_lists([3, 6, 21, 60, 100], lo=1, hi=500)
def b4_c_reverse_k():
    return [([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 3), ([1], 1), ([1, 2, 3, 4], 4), ([1, 2, 3], 5)] + [(rand_list(n), k) for n, k in [(10, 3), (30, 4), (50, 7), (100, 1), (100, 10)]]


def b4_trees(sizes, **kw): return [rand_tree(m, **kw) for m in sizes]


def b4_c_depth(): return [[3, 9, 20, None, None, 15, 7], [1, None, 2], [], [5]] + b4_trees([2, 6, 15, 40, 100])
def b4_c_invert(): return [[4, 2, 7, 1, 3, 6, 9], [2, 1, 3], [], [1]] + b4_trees([4, 9, 20, 60])
def b4_c_symmetric():
    def mirror_tree(m):
        t = tok2tree(rand_tree(m))
        def mir(n): return None if n is None else TN(n.val, mir(n.right), mir(n.left))
        root = TN(t.val, t, mir(t)) if t else None
        return tree2tok(root)
    return [[1, 2, 2, 3, 4, 4, 3], [1, 2, 2, None, 3, None, 3], [1], [], [1, 2, 3], mirror_tree(5), mirror_tree(12)] + b4_trees([7, 20], lo=1, hi=3)
def b4_c_same():
    pairs = [([1, 2, 3], [1, 2, 3]), ([1, 2], [1, None, 2]), ([1, 2, 1], [1, 1, 2]), ([], []), ([], [1])]
    for m in [3, 10, 25]:
        t = rand_tree(m, 1, 4)
        pairs.append((t, list(t)))
        pairs.append((t, rand_tree(m, 1, 4)))
    return pairs
def b4_c_diameter(): return [[1, 2, 3, 4, 5], [1, 2], [1], [1, None, 2, None, 3, None, 4]] + b4_trees([5, 12, 30, 70, 100])
def b4_c_inorder(): return [[1, None, 2, 3], [], [1], [3, 1, 2]] + b4_trees([4, 9, 25, 60])
def b4_c_right_view(): return [[1, 2, 3, None, 5, None, 4], [1, None, 3], [], [1, 2]] + b4_trees([5, 10, 25, 60, 100])
def b4_c_valid_bst():
    def tamper(t):
        t = list(t)
        i = rng.choice([j for j, v in enumerate(t) if v is not None])
        t[i] = rng.randint(1, 99)
        return t
    cases = [[2, 1, 3], [5, 1, 4, None, None, 3, 6], [1, 1], [], [5], [5, 4, 6, None, None, 3, 7], [2, 2, 2]]
    for m in [8, 20, 50]:
        t = rand_bst(m)
        cases += [t, tamper(t)]
    return cases
def b4_c_path_sum():
    cases = [([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22), ([1, 2, 3], 5), ([1, 2], 0), ([], 0), ([1], 1), ([1, 2], 1)]
    for m in [6, 15, 30, 60]:
        t = rand_tree(m, -5, 15)
        root, target = tok2tree(t), 0
        n = root
        while n.left or n.right:
            target += n.val
            n = rng.choice([c for c in (n.left, n.right) if c])
        target += n.val
        cases += [(t, target), (t, target + 1)]
    return cases
def b4_c_balanced(): return [[3, 9, 20, None, None, 15, 7], [1, 2, 2, 3, 3, None, None, 4, 4], [], [1], [1, 2, None, 3]] + b4_trees([6, 14, 30, 60]) + [tree2tok(TN(1, TN(2, TN(3)), TN(4)))]
def b4_c_kth():
    cases = [([3, 1, 4, None, 2], 1), ([5, 3, 6, 2, 4, None, None, 1], 3), ([1], 1)]
    for m, k in [(7, 7), (15, 1), (30, 12), (60, 31), (99, 99)]:
        cases.append((rand_bst(m), k))
    return cases
def b4_c_good(): return [[3, 1, 4, 3, None, 1, 5], [3, 3, None, 4, 2], [1], [], ] + b4_trees([5, 12, 30, 80], lo=-10, hi=10)
def b4_c_maxpath():
    return [[1, 2, 3], [-10, 9, 20, None, None, 15, 7], [-3], [2, -1], [-2, -3]] + b4_trees([6, 15, 40, 90], lo=-30, hi=30)
def b4_c_lca_bst():
    cases = [([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8), ([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4), ([2, 1], 2, 1)]
    for m in [5, 12, 30, 60, 99]:
        t = rand_bst(m)
        vals = [v for v in t if v is not None]
        cases.append((t, *rng.sample(vals, 2)))
    return cases
def b4_c_lca():
    cases = [([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1), ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4), ([1, 2], 1, 2)]
    for m in [5, 12, 30, 60, 99]:
        vals = rng.sample(range(1, 200), m)
        it = iter(vals)
        root = TN(next(it))
        slots = [(root, "left"), (root, "right")]
        for _ in range(m - 1):
            node, side = slots.pop(rng.randrange(len(slots)))
            child = TN(next(it))
            setattr(node, side, child)
            slots += [(child, "left"), (child, "right")]
        cases.append((tree2tok(root), *rng.sample(vals, 2)))
    return cases


LIST_IN = "Line 1: `n`, the number of nodes.\nLine 2: the `n` node values, space separated (blank when `n = 0`)."
TREE_IN = ("Line 1: `n`, the number of tokens.\nLine 2: the tree in level order, space separated. A missing child is written "
           "`null` and trailing `null`s are omitted (blank when `n = 0`, the empty tree).")
LIST_OUT = "The resulting list's values, space separated (a blank line for an empty list)."
TREE_OUT = "The resulting tree in the same level-order format."
LC = "`0 <= n <= 100` nodes"
VAL = "`-100 <= val <= 100`"

PROBLEMS += [
    mk("reverse-linked-list", "Reverse Linked List", "EASY", ["linked-list"], [("head", "list")], "list", b4_reverse,
       b4_c_reverse(), "Given the `head` of a singly linked list, reverse the list and return the new head. Try both an "
       "iterative and a recursive solution.", LIST_IN, LIST_OUT, [LC, VAL]),
    mk("merge-two-sorted-lists", "Merge Two Sorted Lists", "EASY", ["linked-list", "two-pointers"],
       [("list1", "list"), ("list2", "list")], "list", b4_merge, b4_c_merge(),
       "Merge two sorted linked lists into one sorted list by splicing together the nodes of the two lists, and return its head.",
       "The first list in the format below, then the second list in the same format.\n\n" + LIST_IN, LIST_OUT,
       ["Each list has `0 <= n <= 50` nodes", "Both lists are sorted in non-decreasing order"]),
    mk("middle-of-the-linked-list", "Middle of the Linked List", "EASY", ["linked-list", "two-pointers"],
       [("head", "list")], "list", b4_middle, b4_c_middle(),
       "Return the middle node of the list (as the list starting from that node). If there are two middle nodes, return the second one.",
       LIST_IN, "The values from the middle node to the end.", ["`1 <= n <= 100` nodes", VAL]),
    mk("remove-nth-node-from-end-of-list", "Remove Nth Node From End of List", "MEDIUM", ["linked-list", "two-pointers"],
       [("head", "list"), ("n", "int")], "list", b4_remove_nth, b4_c_remove_nth(),
       "Remove the `n`-th node from the end of the list and return its head. Can you do it in one pass?",
       LIST_IN + "\nLine 3: `n`.", LIST_OUT, ["`1 <= size <= 100`", "`1 <= n <= size`"]),
    mk("palindrome-linked-list", "Palindrome Linked List", "EASY", ["linked-list", "two-pointers", "stack"],
       [("head", "list")], "bool", b4_palin_list, b4_c_palin_list(),
       "Return `true` if the values of the list read the same forwards and backwards. Aim for `O(n)` time and `O(1)` extra space.",
       LIST_IN, "`true` or `false`.", ["`1 <= n <= 100` nodes", "`0 <= val <= 9`"]),
    mk("remove-duplicates-from-sorted-list", "Remove Duplicates from Sorted List", "EASY", ["linked-list"],
       [("head", "list")], "list", b4_dedup_sorted, b4_c_dedup(),
       "Given a sorted linked list, delete all duplicates so each value appears only once, and return the list.",
       LIST_IN, LIST_OUT, [LC, "The list is sorted in non-decreasing order"]),
    mk("add-two-numbers", "Add Two Numbers", "MEDIUM", ["linked-list", "math"], [("l1", "list"), ("l2", "list")], "list",
       b4_add_numbers, b4_c_add(),
       "Two non-empty lists represent non-negative integers with the digits stored in **reverse order** (the head is the "
       "ones digit). Add the numbers and return the sum as a list in the same form.",
       "The first list in the format below, then the second list in the same format.\n\n" + LIST_IN, LIST_OUT,
       ["`1 <= n <= 30` nodes per list", "`0 <= digit <= 9`", "No leading zeros except the number 0 itself"]),
    mk("swap-nodes-in-pairs", "Swap Nodes in Pairs", "MEDIUM", ["linked-list"], [("head", "list")], "list", b4_swap_pairs,
       b4_c_swap(), "Swap every two adjacent nodes and return the head. Change the links between nodes; do not just swap the values.",
       LIST_IN, LIST_OUT, [LC, "`0 <= val <= 100`"]),
    mk("odd-even-linked-list", "Odd Even Linked List", "MEDIUM", ["linked-list"], [("head", "list")], "list", b4_odd_even,
       b4_c_odd_even(), "Group all nodes at odd positions first, followed by the nodes at even positions, keeping the "
       "relative order inside each group. Positions start at 1. Use `O(1)` extra space and `O(n)` time.",
       LIST_IN, LIST_OUT, ["`0 <= n <= 100` nodes", VAL]),
    mk("sort-list", "Sort List", "MEDIUM", ["linked-list", "sorting", "divide-and-conquer"], [("head", "list")], "list",
       b4_sort_list, b4_c_sort(), "Sort the linked list in ascending order. For a challenge, do it in `O(n log n)` time and `O(1)` extra space.",
       LIST_IN, LIST_OUT, [LC, VAL]),
    mk("reorder-list", "Reorder List", "MEDIUM", ["linked-list", "two-pointers"], [("head", "list")], "list", b4_reorder,
       b4_c_reorder(), "Reorder `L0 → L1 → … → Ln-1 → Ln` into `L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …` in place, "
       "without changing node values. Return the reordered list.", LIST_IN, LIST_OUT, ["`1 <= n <= 100` nodes", "`1 <= val <= 500`"]),
    mk("reverse-nodes-in-k-group", "Reverse Nodes in k-Group", "HARD", ["linked-list", "recursion"],
       [("head", "list"), ("k", "int")], "list", b4_reverse_k, b4_c_reverse_k(),
       "Reverse the nodes of the list `k` at a time and return the head. If the number of remaining nodes is less than `k`, "
       "leave them as they are. Only the links may change, not the values.", LIST_IN + "\nLine 3: `k`.", LIST_OUT,
       ["`1 <= k <= n <= 100`", VAL]),

    mk("maximum-depth-of-binary-tree", "Maximum Depth of Binary Tree", "EASY", ["tree", "dfs", "bfs"], [("root", "tree")], "int",
       b4_depth, b4_c_depth(), "Return the maximum depth of a binary tree: the number of nodes on the longest path from the root down to a leaf.",
       TREE_IN, "The maximum depth (`0` for the empty tree).", [LC, VAL]),
    mk("invert-binary-tree", "Invert Binary Tree", "EASY", ["tree", "dfs", "bfs"], [("root", "tree")], "tree", b4_invert,
       b4_c_invert(), "Invert the binary tree (swap every node's left and right child) and return its root.", TREE_IN, TREE_OUT, [LC, VAL]),
    mk("symmetric-tree", "Symmetric Tree", "EASY", ["tree", "dfs", "bfs"], [("root", "tree")], "bool", b4_symmetric,
       b4_c_symmetric(), "Return `true` if the tree is a mirror image of itself around its center.", TREE_IN, "`true` or `false`.",
       ["`0 <= n <= 100` nodes", "`-100 <= val <= 100`"]),
    mk("same-tree", "Same Tree", "EASY", ["tree", "dfs"], [("p", "tree"), ("q", "tree")], "bool", b4_same, b4_c_same(),
       "Return `true` if the two binary trees are structurally identical and their nodes hold the same values.",
       "Tree `p` in the format below, then tree `q` in the same format.\n\n" + TREE_IN, "`true` or `false`.", ["Each tree has `0 <= n <= 100` nodes", VAL]),
    mk("diameter-of-binary-tree", "Diameter of Binary Tree", "EASY", ["tree", "dfs"], [("root", "tree")], "int",
       b4_diameter, b4_c_diameter(), "Return the diameter of the tree: the number of **edges** on the longest path between any "
       "two nodes. The path may or may not pass through the root.", TREE_IN, "The diameter.", ["`1 <= n <= 100` nodes", VAL]),
    mk("binary-tree-inorder-traversal", "Binary Tree Inorder Traversal", "EASY", ["tree", "dfs", "stack"], [("root", "tree")],
       "int[]", b4_inorder, b4_c_inorder(), "Return the inorder traversal (left, node, right) of the tree. Try an iterative solution.",
       TREE_IN, "The node values in inorder, space separated (a blank line for the empty tree).", [LC, VAL]),
    mk("binary-tree-right-side-view", "Binary Tree Right Side View", "MEDIUM", ["tree", "bfs", "dfs"], [("root", "tree")],
       "int[]", b4_right_view, b4_c_right_view(), "Imagine standing on the right side of the tree. Return the values of the nodes "
       "you can see, ordered from top to bottom.", TREE_IN, "The visible values, space separated (blank for the empty tree).", [LC, VAL]),
    mk("validate-binary-search-tree", "Validate Binary Search Tree", "MEDIUM", ["tree", "bst", "dfs"], [("root", "tree")], "bool",
       b4_valid_bst, b4_c_valid_bst(), "Return `true` if the tree is a valid binary search tree: for every node, all values in "
       "its left subtree are **strictly less** and all in its right subtree are **strictly greater**.", TREE_IN, "`true` or `false`.",
       ["`0 <= n <= 100` nodes", "`-2^31 <= val <= 2^31 - 1`"]),
    mk("path-sum", "Path Sum", "EASY", ["tree", "dfs"], [("root", "tree"), ("targetSum", "int")], "bool", b4_path_sum,
       b4_c_path_sum(), "Return `true` if the tree has a **root-to-leaf** path whose node values add up to `targetSum`.",
       TREE_IN + "\nLine 3: `targetSum`.", "`true` or `false`.", ["`0 <= n <= 100` nodes", "`-1000 <= val, targetSum <= 1000`"]),
    mk("balanced-binary-tree", "Balanced Binary Tree", "EASY", ["tree", "dfs"], [("root", "tree")], "bool", b4_balanced,
       b4_c_balanced(), "Return `true` if the tree is height-balanced: for every node, the heights of its two subtrees differ by at most one.",
       TREE_IN, "`true` or `false`.", [LC, VAL]),
    mk("kth-smallest-element-in-a-bst", "Kth Smallest Element in a BST", "MEDIUM", ["tree", "bst", "dfs"],
       [("root", "tree"), ("k", "int")], "int", b4_kth_bst, b4_c_kth(), "Given a binary search tree, return the `k`-th smallest value (1-indexed).",
       TREE_IN + "\nLine 3: `k`.", "The `k`-th smallest value.", ["`1 <= k <= n <= 100`", "All values are distinct"]),
    mk("count-good-nodes-in-binary-tree", "Count Good Nodes in Binary Tree", "MEDIUM", ["tree", "dfs"], [("root", "tree")], "int",
       b4_good_nodes, b4_c_good(), "A node `X` is **good** if no node on the path from the root to `X` has a larger value than `X`. "
       "Return the number of good nodes.", TREE_IN, "The number of good nodes.", [LC, "`-10^4 <= val <= 10^4`"]),
    mk("binary-tree-maximum-path-sum", "Binary Tree Maximum Path Sum", "HARD", ["tree", "dfs", "dp"], [("root", "tree")], "int",
       b4_max_path, b4_c_maxpath(), "A path is any sequence of nodes in which consecutive nodes are connected by an edge, visiting "
       "each node at most once; it need not pass through the root. Return the maximum sum of node values over all non-empty paths.",
       TREE_IN, "The maximum path sum.", ["`1 <= n <= 100` nodes", "`-1000 <= val <= 1000`"]),
    mk("lowest-common-ancestor-of-a-binary-search-tree", "Lowest Common Ancestor of a BST", "MEDIUM", ["tree", "bst"],
       [("root", "tree"), ("p", "int"), ("q", "int")], "int", b4_lca_bst, b4_c_lca_bst(),
       "Given a BST and the values of two nodes `p` and `q` that are in it, return the value of their lowest common ancestor "
       "(a node may be its own descendant).", TREE_IN + "\nLine 3: `p`.\nLine 4: `q`.", "The value of the LCA.",
       ["`2 <= n <= 100` nodes", "All values are unique", "`p != q` and both exist in the tree"]),
    mk("lowest-common-ancestor-of-a-binary-tree", "Lowest Common Ancestor of a Binary Tree", "MEDIUM", ["tree", "dfs"],
       [("root", "tree"), ("p", "int"), ("q", "int")], "int", b4_lca, b4_c_lca(),
       "Given a binary tree and the values of two nodes `p` and `q` that are in it, return the value of their lowest common "
       "ancestor (a node may be its own descendant).", TREE_IN + "\nLine 3: `p`.\nLine 4: `q`.", "The value of the LCA.",
       ["`2 <= n <= 100` nodes", "All values are unique", "`p != q` and both exist in the tree"]),
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
