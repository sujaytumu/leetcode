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
        elif typ == "strs":
            lines.append(str(len(val)))
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
    if ret in ("sets", "rows"):
        # Any order is fine for the solver: the starter code prints the rows sorted, so output order never matters.
        # `sets` also sorts inside each row (combinations), `rows` keeps the order inside a row (permutations).
        rows = sorted(sorted(r) for r in val) if ret == "sets" else sorted(list(r) for r in val)
        return "\n".join(" ".join(map(str, r)) for r in rows) + "\n"
    if ret == "strs":
        return "\n".join(sorted(val)) + "\n"
    if ret == "str":
        return f"{val}\n"
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
        elif t in ("grid", "strs"):
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
        "sets": ["    rows = sorted(sorted(r) for r in result)", "    for row in rows:", '        print(" ".join(map(str, row)))'],
        "rows": ["    rows = sorted(list(r) for r in result)", "    for row in rows:", '        print(" ".join(map(str, row)))'],
        "strs": ["    for s in sorted(result):", "        print(s)"],
        "str": ["    print(result)"],
    }[ret]
    body += ["", "", 'if __name__ == "__main__":', "    main()", ""]
    return "\n".join(body)


JAVA_T = {"int": "int", "str": "String", "int[]": "int[]", "int[][]": "int[][]", "grid": "String[]", "strs": "String[]", "list": "ListNode", "tree": "TreeNode"}
JAVA_RET = {"int": "int", "bool": "boolean", "int[]": "int[]", "int[][]": "int[][]", "list": "ListNode", "tree": "TreeNode",
            "sets": "int[][]", "rows": "int[][]", "strs": "String[]", "str": "String"}
JAVA_DEFAULT = {"int": "0", "bool": "false", "int[]": "new int[0]", "int[][]": "new int[0][]", "list": "null", "tree": "null",
                "sets": "new int[0][]", "rows": "new int[0][]", "strs": "new String[0]", "str": '""'}


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
            # Rows may have any width (pairs, triples, matrix rows): size each row by its tokens.
            out += [f"        int {n}Len = Integer.parseInt(lines.get(pos++).trim());",
                    f"        int[][] {n} = new int[{n}Len][];",
                    f"        for (int i = 0; i < {n}Len; i++) {{",
                    "            StringTokenizer st = new StringTokenizer(lines.get(pos++));",
                    f"            {n}[i] = new int[st.countTokens()];",
                    f"            for (int j = 0; j < {n}[i].length; j++) {n}[i][j] = Integer.parseInt(st.nextToken());", "        }"]
        elif t in ("grid", "strs"):
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
                    '            System.out.println(Arrays.stream(row).mapToObj(String::valueOf).collect(Collectors.joining(" ")));', "        }"],
        "list": ["        System.out.println(listString(result));"],
        "tree": ["        System.out.println(treeString(result));"],
        "sets": ["        int[][] sorted = new int[result.length][];",
                 "        for (int i = 0; i < result.length; i++) {", "            sorted[i] = result[i].clone();",
                 "            Arrays.sort(sorted[i]);", "        }", "        Arrays.sort(sorted, Arrays::compare);",
                 "        for (int[] row : sorted) {",
                 '            System.out.println(Arrays.stream(row).mapToObj(String::valueOf).collect(Collectors.joining(" ")));', "        }"],
        "rows": ["        int[][] sorted = result.clone();", "        Arrays.sort(sorted, Arrays::compare);",
                 "        for (int[] row : sorted) {",
                 '            System.out.println(Arrays.stream(row).mapToObj(String::valueOf).collect(Collectors.joining(" ")));', "        }"],
        "strs": ["        String[] sorted = result.clone();", "        Arrays.sort(sorted);",
                 "        for (String s : sorted) System.out.println(s);"],
        "str": ["        System.out.println(result);"],
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
        elif t in ("grid", "strs"):
            out += [f"const {n}Rows = parseInt(lines[pos++].trim().split(/\\s+/)[0], 10);",
                    f"const {n} = lines.slice(pos, pos + {n}Rows);", f"pos += {n}Rows;"]
        elif t == "list":
            out += [f"const {n}Len = parseInt(lines[pos++], 10);",
                    f"const {n} = buildList({n}Len > 0 ? lines[pos].trim().split(/\\s+/).map(Number) : []);", "pos++;"]
        elif t == "tree":
            out += [f"const {n}Len = parseInt(lines[pos++], 10);",
                    f"const {n} = buildTree({n}Len > 0 ? lines[pos].trim().split(/\\s+/) : []);", "pos++;"]
    if ret in ("sets", "rows"):
        out += ["function compareRows(a, b) {", "  for (let i = 0; i < Math.min(a.length, b.length); i++) {",
                "    if (a[i] !== b[i]) return a[i] - b[i];", "  }", "  return a.length - b.length;", "}", ""]
    out += [f"const result = solve({names});"]
    out += {
        "int": ["console.log(String(result));"],
        "bool": ['console.log(result ? "true" : "false");'],
        "int[]": ['console.log(result.join(" "));'],
        "int[][]": ['console.log(result.map((r) => r.join(" ")).join("\\n"));'],
        "list": ["console.log(listString(result));"],
        "tree": ["console.log(treeString(result));"],
        "sets": ["const rows = result.map((r) => [...r].sort((a, b) => a - b));", "rows.sort(compareRows);",
                 'console.log(rows.map((r) => r.join(" ")).join("\\n"));'],
        "rows": ["const rows = result.map((r) => [...r]);", "rows.sort(compareRows);",
                 'console.log(rows.map((r) => r.join(" ")).join("\\n"));'],
        "strs": ['console.log([...result].sort().join("\\n"));'],
        "str": ["console.log(result);"],
    }[ret]
    out += [""]
    return "\n".join(out)


CPP_T = {"int": "int", "str": "string", "int[]": "vector<int>", "int[][]": "vector<vector<int>>", "grid": "vector<string>", "strs": "vector<string>",
         "list": "ListNode *", "tree": "TreeNode *"}
CPP_RET = {"int": "int", "bool": "bool", "int[]": "vector<int>", "int[][]": "vector<vector<int>>", "list": "ListNode *", "tree": "TreeNode *",
           "sets": "vector<vector<int>>", "rows": "vector<vector<int>>", "strs": "vector<string>", "str": "string"}
CPP_DEFAULT = {"int": "0", "bool": "false", "int[]": "{}", "int[][]": "{}", "list": "nullptr", "tree": "nullptr",
               "sets": "{}", "rows": "{}", "strs": "{}", "str": "{}"}


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
                    f"    vector<vector<int>> {n}({n}Len);",
                    f"    for (int i = 0; i < {n}Len; i++) {{", "        istringstream iss(lines[pos++]);",
                    f"        int v;", f"        while (iss >> v) {n}[i].push_back(v);", "    }"]
        elif t in ("grid", "strs"):
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
        "int[][]": ["    for (auto &row : result) {", "        for (size_t j = 0; j < row.size(); j++) {", '            if (j) cout << " ";',
                    "            cout << row[j];", "        }", '        cout << "\\n";', "    }"],
        "list": ['    cout << listString(result) << "\\n";'],
        "tree": ['    cout << treeString(result) << "\\n";'],
        "sets": ["    for (auto &row : result) sort(row.begin(), row.end());", "    sort(result.begin(), result.end());",
                 "    for (auto &row : result) {", "        for (size_t j = 0; j < row.size(); j++) {", '            if (j) cout << " ";',
                 "            cout << row[j];", "        }", '        cout << "\\n";', "    }"],
        "rows": ["    sort(result.begin(), result.end());",
                 "    for (auto &row : result) {", "        for (size_t j = 0; j < row.size(); j++) {", '            if (j) cout << " ";',
                 "            cout << row[j];", "        }", '        cout << "\\n";', "    }"],
        "strs": ["    sort(result.begin(), result.end());", '    for (auto &s : result) cout << s << "\\n";'],
        "str": ['    cout << result << "\\n";'],
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


def three_sum_all(nums):
    nums, seen = sorted(nums), set()
    for i in range(len(nums) - 2):
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            total = nums[i] + nums[lo] + nums[hi]
            if total == 0:
                seen.add((nums[i], nums[lo], nums[hi]))
                lo += 1
                hi -= 1
            elif total < 0:
                lo += 1
            else:
                hi -= 1
    return [list(t) for t in sorted(seen)]


def four_sum_all(a, target):
    a, seen = sorted(a), set()
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            lo, hi = j + 1, len(a) - 1
            while lo < hi:
                total = a[i] + a[j] + a[lo] + a[hi]
                if total == target:
                    seen.add((a[i], a[j], a[lo], a[hi]))
                    lo += 1
                    hi -= 1
                elif total < target:
                    lo += 1
                else:
                    hi -= 1
    return [list(t) for t in sorted(seen)]


def permutations_unique_all(nums):
    import itertools
    return [list(p) for p in sorted(set(itertools.permutations(nums)))]


def combination_sum_all(candidates, target):
    cands, out = sorted(candidates), []

    def go(start, left, cur):
        if left == 0:
            out.append(list(cur))
            return
        for j in range(start, len(cands)):
            if cands[j] > left:
                break
            cur.append(cands[j])
            go(j, left - cands[j], cur)
            cur.pop()

    go(0, target, [])
    return out


def generate_parentheses_all(n):
    out = []

    def go(cur, opened, closed):
        if len(cur) == 2 * n:
            out.append(cur)
            return
        if opened < n:
            go(cur + "(", opened + 1, closed)
        if closed < opened:
            go(cur + ")", opened, closed + 1)

    go("", 0, 0)
    return out


def min_windows(s, t):
    """Every shortest substring of `s` that contains all characters of `t` (with multiplicity)."""
    length = b6_min_window_len(s, t)
    if length == 0:
        return []
    need = collections.Counter(t)
    return [s[i:i + length] for i in range(len(s) - length + 1)
            if not need - collections.Counter(s[i:i + length])]


def min_window_text(s, t):
    found = min_windows(s, t)
    return found[0] if found else ""


# LeetCode promises a unique answer; keep only test cases that really have one.
min_window_text.accept = lambda s, t: len(min_windows(s, t)) <= 1


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
    mk("3sum-count", "3Sum", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]")], "sets",
       three_sum_all, [[-1, 0, 1, 2, -1, -4], [0, 1, 1], [0, 0, 0], [0, 0, 0, 0], rand_arr(12, -10, 10),
                         rand_arr(60, -30, 30), rand_arr(200, -50, 50), rand_arr(500, -100, 100), rand_arr(3, -5, 5)],
       "Return all the **unique** triplets `[nums[i], nums[j], nums[k]]` such that `i`, `j` and `k` are different indices "
       "and `nums[i] + nums[j] + nums[k] == 0`. The answer must not contain duplicate triplets; you may return the "
       "triplets, and the numbers inside each, in any order.", ARR_IN,
       "One triplet per line, numbers separated by spaces; nothing if there is none. The starter code sorts what you "
       "return before printing, so the order never matters.", ["`3 <= n <= 500`", "`-10^5 <= nums[i] <= 10^5`"]),
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
    mk("distinct-permutations-count", "Permutations II", "MEDIUM", ["backtracking", "math"],
       [("nums", "int[]")], "rows", permutations_unique_all,
       [[1, 1, 2], [1, 2, 3], [1, 1, 1], [1, 2], rand_arr(6, 1, 3), rand_arr(7, 1, 4), rand_arr(8, 1, 3),
        rand_arr(8, 1, 8), [5]],
       "`nums` may contain duplicates. Return all the **unique** permutations, in any order.", ARR_IN,
       "One permutation per line, numbers separated by spaces. The starter code sorts the lines before printing, so "
       "the order never matters.", ["`1 <= n <= 8`", "`1 <= nums[i] <= 10`"]),
    mk("generate-parentheses-count", "Generate Parentheses", "MEDIUM", ["backtracking", "dynamic-programming", "math"],
       [("n", "int")], "strs", generate_parentheses_all, [3, 1, 2, 4, 5, 8, 10, 12, 15],
       "Given `n` pairs of parentheses, return all the combinations of well-formed parentheses, in any order.", N_IN,
       "One string per line. The starter code sorts the lines before printing, so the order never matters.", ["`1 <= n <= 8`"]),
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



# ================================================================ batch 5: more problems (arrays, matrix, stack, search, DP)
MAT_IN = "Line 1: `m`, the number of rows.\nNext `m` lines: the integers of each row, space separated."
MAT_OUT = "The resulting matrix, one row per line, integers space separated."


def b5_plus_one(d):
    return [int(c) for c in str(int("".join(map(str, d))) + 1)]


def b5_sorted_squares(a): return sorted(x * x for x in a)


def b5_disappeared(a):
    s = set(a)
    return [i for i in range(1, len(a) + 1) if i not in s]


def b5_rotate_array(a, k):
    k %= len(a)
    return a[len(a) - k:] + a[:len(a) - k] if k else list(a)


def b5_sort_colors(a): return sorted(a)


def b5_next_perm(a):
    a = list(a)
    i = len(a) - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i >= 0:
        j = len(a) - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
    a[i + 1:] = a[i + 1:][::-1]
    return a


def b5_find_dup(a):
    slow = fast = a[0]
    while True:
        slow, fast = a[slow], a[a[fast]]
        if slow == fast:
            break
    slow = a[0]
    while slow != fast:
        slow, fast = a[slow], a[fast]
    return slow


def b5_spiral(m):
    out, top, bot, left, right = [], 0, len(m) - 1, 0, len(m[0]) - 1
    while top <= bot and left <= right:
        out += m[top][left:right + 1]
        top += 1
        out += [m[i][right] for i in range(top, bot + 1)]
        right -= 1
        if top <= bot:
            out += m[bot][left:right + 1][::-1]
            bot -= 1
        if left <= right:
            out += [m[i][left] for i in range(bot, top - 1, -1)]
            left += 1
    return out


def b5_rotate_image(m): return [list(r) for r in zip(*m[::-1])]


def b5_set_zeroes(m):
    rows = {i for i, r in enumerate(m) for v in r if v == 0}
    cols = {j for r in m for j, v in enumerate(r) if v == 0}
    return [[0 if i in rows or j in cols else v for j, v in enumerate(r)] for i, r in enumerate(m)]


def b5_pascal(n):
    rows = [[1]]
    for _ in range(n - 1):
        p = rows[-1]
        rows.append([1] + [p[i] + p[i + 1] for i in range(len(p) - 1)] + [1])
    return rows


def b5_three_sum_closest(a, target):
    a = sorted(a)
    best = None
    for i in range(len(a) - 2):
        l, r = i + 1, len(a) - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if best is None or abs(s - target) < abs(best - target) or (abs(s - target) == abs(best - target) and s < best):
                best = s
            if s < target:
                l += 1
            elif s > target:
                r -= 1
            else:
                return s
    return best


def b5_first_last(a, target):
    lo = bisect.bisect_left(a, target)
    hi = bisect.bisect_right(a, target)
    return [lo, hi - 1] if lo < hi else [-1, -1]


def b5_rpn(s):
    st = []
    for t in s.split():
        if t in "+-*/" and len(t) == 1:
            b, a = st.pop(), st.pop()
            st.append(a + b if t == "+" else a - b if t == "-" else a * b if t == "*" else int(a / b))
        else:
            st.append(int(t))
    return st[0]


def b5_next_greater_ii(a):
    n, out, st = len(a), [-1] * len(a), []
    for i in range(2 * n):
        while st and a[st[-1]] < a[i % n]:
            out[st.pop()] = a[i % n]
        if i < n:
            st.append(i)
    return out


def b5_car_fleet(target, pos, speed):
    from fractions import Fraction
    fleets, cur = 0, Fraction(0)
    for p, s in sorted(zip(pos, speed), reverse=True):
        t = Fraction(target - p, s)
        if t > cur:
            fleets += 1
            cur = t
    return fleets


def b5_sum_sub_mins(a):
    n, mod = len(a), 10**9 + 7
    left, right, st = [0] * n, [0] * n, []
    for i in range(n):
        while st and a[st[-1]] > a[i]:
            st.pop()
        left[i] = i - (st[-1] if st else -1)
        st.append(i)
    st = []
    for i in range(n - 1, -1, -1):
        while st and a[st[-1]] >= a[i]:
            st.pop()
        right[i] = (st[-1] if st else n) - i
        st.append(i)
    return sum(a[i] * left[i] * right[i] for i in range(n)) % mod


def b5_search_matrix(m, target):
    flat = [v for r in m for v in r]
    i = bisect.bisect_left(flat, target)
    return i < len(flat) and flat[i] == target


def b5_word_break(s, words):
    ws = set(words.split())
    ok = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        ok[i] = any(ok[j] and s[j:i] in ws for j in range(i))
    return ok[len(s)]


def b5_pal_substrings(s):
    cnt = 0
    for c in range(2 * len(s) - 1):
        l, r = c // 2, c // 2 + c % 2
        while l >= 0 and r < len(s) and s[l] == s[r]:
            cnt += 1
            l -= 1
            r += 1
    return cnt


def b5_target_sum(a, target):
    ways = {0: 1}
    for x in a:
        nxt = collections.defaultdict(int)
        for s, c in ways.items():
            nxt[s + x] += c
            nxt[s - x] += c
        ways = nxt
    return ways.get(target, 0)


def b5_delete_earn(a):
    pts = collections.Counter(a)
    take = skip = 0
    prev = None
    for v in sorted(pts):
        if prev is not None and v == prev + 1:
            take, skip = skip + v * pts[v], max(take, skip)
        else:
            take, skip = max(take, skip) + v * pts[v], max(take, skip)
        prev = v
    return max(take, skip)


def b5_cooldown(p):
    hold, sold, rest = -10**9, 0, 0
    for x in p:
        hold, sold, rest = max(hold, rest - x), hold + x, max(rest, sold)
    return max(sold, rest)


def b5_distinct_subseq(s, t):
    dp = [1] + [0] * len(t)
    for c in s:
        for j in range(len(t), 0, -1):
            if t[j - 1] == c:
                dp[j] += dp[j - 1]
    return dp[len(t)]


def b5_regex(s, p):
    memo = {}

    def go(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        if j == len(p):
            res = i == len(s)
        else:
            first = i < len(s) and p[j] in (s[i], ".")
            if j + 1 < len(p) and p[j + 1] == "*":
                res = go(i, j + 2) or (first and go(i + 1, j))
            else:
                res = first and go(i + 1, j + 1)
        memo[(i, j)] = res
        return res
    return go(0, 0)


def b5_burst(a):
    a = [1] + list(a) + [1]
    n = len(a)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for l in range(n - length):
            r = l + length
            dp[l][r] = max(dp[l][k] + dp[k][r] + a[l] * a[k] * a[r] for k in range(l + 1, r))
    return dp[0][n - 1]


def b5_stock3(p):
    b1 = b2 = -10**9
    s1 = s2 = 0
    for x in p:
        b1 = max(b1, -x)
        s1 = max(s1, b1 + x)
        b2 = max(b2, s1 - x)
        s2 = max(s2, b2 + x)
    return s2


def b5_falling_path(m):
    row = list(m[0])
    for r in m[1:]:
        row = [r[j] + min(row[max(0, j - 1):j + 2]) for j in range(len(r))]
    return min(row)


def b5_combo_count(cands, target):
    ways = [1] + [0] * target
    for c in cands:
        for t in range(c, target + 1):
            ways[t] += ways[t - c]
    return ways[target]


def b5_network_delay(times, n, k):
    dist = {i: math.inf for i in range(1, n + 1)}
    dist[k] = 0
    heap = [(0, k)]
    adj = collections.defaultdict(list)
    for u, v, w in times:
        adj[u].append((v, w))
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    m = max(dist.values())
    return -1 if m == math.inf else m


def b5_provinces(g):
    n, seen, cnt = len(g), set(), 0
    for s in range(n):
        if s in seen:
            continue
        cnt += 1
        stack = [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            for v in range(n):
                if g[u][v] and v not in seen:
                    seen.add(v)
                    stack.append(v)
    return cnt


def b5_redundant(edges):
    parent = list(range(len(edges) + 2))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return [u, v]
        parent[ru] = rv


def b5_min_connect(points):
    n = len(points)
    dist = [math.inf] * n
    dist[0] = 0
    used = [False] * n
    total = 0
    for _ in range(n):
        u = min((i for i in range(n) if not used[i]), key=lambda i: dist[i])
        used[u] = True
        total += dist[u]
        for v in range(n):
            if not used[v]:
                dist[v] = min(dist[v], abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1]))
    return total


def b5_arrows(points):
    pts = sorted(points, key=lambda p: p[1])
    arrows, end = 0, -math.inf
    for a, b in pts:
        if a > end:
            arrows += 1
            end = b
    return arrows


def b5_flowers(bed, n):
    bed = [0] + list(bed) + [0]
    for i in range(1, len(bed) - 1):
        if bed[i - 1] == bed[i] == bed[i + 1] == 0:
            bed[i] = 1
            n -= 1
    return n <= 0


def b5_lemonade(bills):
    five = ten = 0
    for b in bills:
        if b == 5:
            five += 1
        elif b == 10:
            if not five:
                return False
            five -= 1
            ten += 1
        else:
            if ten and five:
                ten -= 1
                five -= 1
            elif five >= 3:
                five -= 3
            else:
                return False
    return True


def b5_task_scheduler(tasks, n):
    cnt = collections.Counter(tasks)
    mx = max(cnt.values())
    ties = sum(1 for v in cnt.values() if v == mx)
    return max(len(tasks), (mx - 1) * (n + 1) + ties)


def b5_hamming(x, y): return bin(x ^ y).count("1")


def b5_range_and(l, r):
    shift = 0
    while l != r:
        l >>= 1
        r >>= 1
        shift += 1
    return l << shift


def b5_ugly(n):
    u, i2, i3, i5 = [1], 0, 0, 0
    while len(u) < n:
        nxt = min(u[i2] * 2, u[i3] * 3, u[i5] * 5)
        u.append(nxt)
        if nxt == u[i2] * 2: i2 += 1
        if nxt == u[i3] * 3: i3 += 1
        if nxt == u[i5] * 5: i5 += 1
    return u[-1]


# ---- trees / lists
def b5_subtree(t, s):
    def same(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

    def go(a, b):
        return a is not None and (same(a, b) or go(a.left, b) or go(a.right, b))
    sub = tok2tree(s)
    return go(tok2tree(t), sub) if sub is not None else True


def b5_level_order(t):
    root = tok2tree(t)
    out, level = [], [root] if root else []
    while level:
        out.append([n.val for n in level])
        level = [c for n in level for c in (n.left, n.right) if c]
    return out


def b5_min_depth(t):
    def d(n):
        if n is None:
            return 0
        if n.left is None:
            return 1 + d(n.right)
        if n.right is None:
            return 1 + d(n.left)
        return 1 + min(d(n.left), d(n.right))
    return d(tok2tree(t))


def b5_root_leaf_numbers(t):
    def go(n, cur):
        if n is None:
            return 0
        cur = cur * 10 + n.val
        if n.left is None and n.right is None:
            return cur
        return go(n.left, cur) + go(n.right, cur)
    return go(tok2tree(t), 0)


def b5_rob_tree(t):
    def go(n):
        if n is None:
            return 0, 0
        lt, ls = go(n.left)
        rt, rs = go(n.right)
        take = n.val + ls + rs
        skip = max(lt, ls) + max(rt, rs)
        return take, skip
    return max(go(tok2tree(t)))


def b5_path_sum3(t, target):
    def from_node(n, rem):
        if n is None:
            return 0
        return (n.val == rem) + from_node(n.left, rem - n.val) + from_node(n.right, rem - n.val)

    def go(n):
        return 0 if n is None else from_node(n, target) + go(n.left) + go(n.right)
    return go(tok2tree(t))


def b5_build_tree(pre, ino):
    pos = {v: i for i, v in enumerate(ino)}
    it = iter(pre)

    def build(lo, hi):
        if lo > hi:
            return None
        v = next(it)
        node = TN(v)
        node.left = build(lo, pos[v] - 1)
        node.right = build(pos[v] + 1, hi)
        return node
    return tree2tok(build(0, len(ino) - 1))


def b5_remove_elements(a, v): return [x for x in a if x != v]


def b5_rotate_list(a, k):
    if not a:
        return []
    k %= len(a)
    return a[len(a) - k:] + a[:len(a) - k]


def b5_partition_list(a, x): return [v for v in a if v < x] + [v for v in a if v >= x]


def b5_dedup_all(a):
    c = collections.Counter(a)
    return [v for v in a if c[v] == 1]


def b5_reverse_between(a, l, r): return a[:l - 1] + a[l - 1:r][::-1] + a[r:]


def b5_twin_sum(a): return max(a[i] + a[len(a) - 1 - i] for i in range(len(a) // 2))


# ---- case generators for batch 5
def b5_distinct_tree(m):
    """Random binary tree with m distinct values (level-order tokens)."""
    tok = rand_tree(m)
    root = tok2tree(tok)
    vals = iter(rng.sample(range(-50, 100), m))
    stack = [root] if root else []
    while stack:
        n = stack.pop()
        n.val = next(vals)
        stack += [c for c in (n.left, n.right) if c]
    return tree2tok(root)


def b5_pre_in(tok):
    root = tok2tree(tok)
    pre, ino = [], []

    def go(n):
        if n:
            pre.append(n.val)
            go(n.left)
            ino.append(n.val)
            go(n.right)
    go(root)
    return pre, ino


def b5_matrix(m, n, lo, hi): return [[rng.randint(lo, hi) for _ in range(n)] for _ in range(m)]


def b5_c_plus_one():
    cases = [[1, 2, 3], [4, 3, 2, 1], [9], [9, 9, 9], [0], [1, 9, 9], [8, 9, 9, 9]]
    for n in (5, 20, 60, 100):
        cases.append([rng.randint(1, 9)] + [rng.randint(0, 9) for _ in range(n - 1)])
    return cases + [[9] * 50]


def b5_c_squares():
    return [[-4, -1, 0, 3, 10], [-7, -3, 2, 3, 11], [0], [-5], [-3, -3, 3, 3]] + \
        [sorted(rng.randint(-100, 100) for _ in range(n)) for n in (5, 20, 100, 500, 1000)]


def b5_c_disappeared():
    cases = [[4, 3, 2, 7, 8, 2, 3, 1], [1, 1], [2, 2], [1, 1, 1, 1]]
    for n in (6, 15, 60, 300, 1000):
        a = [rng.randint(1, n) for _ in range(n)]
        a[0] = a[1]
        if len(set(a)) == n:
            a[0] = a[1]
        cases.append(a)
    return cases


def b5_c_rotate_array():
    cases = [([1, 2, 3, 4, 5, 6, 7], 3), ([-1, -100, 3, 99], 2), ([1], 0), ([1, 2], 5), ([1, 2, 3], 3), ([1, 2, 3], 0)]
    for n in (5, 12, 60, 300, 1000):
        cases.append((rand_arr(n, -1000, 1000), rng.randint(0, 100000)))
    return cases


def b5_c_sort_colors():
    return [[2, 0, 2, 1, 1, 0], [2, 0, 1], [0], [1], [2, 2, 2], [1, 0]] + [rand_arr(n, 0, 2) for n in (5, 20, 100, 300)]


def b5_c_next_perm():
    cases = [[1, 2, 3], [3, 2, 1], [1, 1, 5], [1], [1, 3, 2], [2, 3, 1], [1, 5, 1], [5, 4, 7, 5, 3, 2]]
    for n in (4, 8, 20, 100):
        cases.append(rand_arr(n, 0, 20))
    return cases + [sorted(rand_arr(30, 0, 100))]


def b5_dup_case(n, c=1):
    d = rng.randint(1, n)
    others = [v for v in range(1, n + 1) if v != d]
    removed = set(rng.sample(others, min(c - 1, len(others))))
    arr = [v for v in range(1, n + 1) if v not in removed] + [d] * c
    rng.shuffle(arr)
    return arr


def b5_c_find_dup():
    return [[1, 3, 4, 2, 2], [3, 1, 3, 4, 2], [3, 3, 3, 3, 3], [1, 1], [2, 2, 2], [1, 4, 4, 2, 4]] + \
        [b5_dup_case(n, c) for n, c in ((5, 2), (10, 1), (30, 3), (100, 1), (300, 5), (1000, 1))]


def b5_c_spiral():
    return [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], [[7]], [[1, 2, 3]], [[1], [2], [3]],
            [[1, 2], [3, 4]]] + [b5_matrix(m, n, -50, 50) for m, n in ((4, 4), (5, 3), (3, 7), (10, 10), (1, 9), (8, 1))]


def b5_c_rotate_image():
    return [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]], [[1]], [[1, 2], [3, 4]]] + \
        [b5_matrix(n, n, -100, 100) for n in (5, 6, 10, 20)]


def b5_c_set_zeroes():
    cases = [[[1, 1, 1], [1, 0, 1], [1, 1, 1]], [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]], [[1]], [[0]], [[1, 2], [3, 4]]]
    for m, n in ((4, 4), (5, 6), (8, 3), (10, 10)):
        cases.append([[rng.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]) if rng.random() < 0.9 else 0 for _ in range(n)] for _ in range(m)])
    return cases


def b5_c_three_closest():
    cases = [([-1, 2, 1, -4], 1), ([0, 0, 0], 1), ([1, 1, 1, 0], -100), ([1, 2, 5, 10, 11], 12), ([-3, -2, -5, 3, -4], -1)]
    for n in (5, 10, 30, 100, 300):
        cases.append((rand_arr(n, -1000, 1000), rng.randint(-3000, 3000)))
    return cases


def b5_c_first_last():
    cases = [([5, 7, 7, 8, 8, 10], 8), ([5, 7, 7, 8, 8, 10], 6), ([1], 1), ([2, 2], 2), ([1, 2, 3], 4), ([1, 1, 1, 1], 1)]
    for n in (8, 20, 100, 500, 1000):
        a = sorted(rand_arr(n, 0, n // 3 + 2))
        cases.append((a, rng.choice(a)))
        cases.append((a, n))
    return cases


def b5_rand_rpn():
    """Random valid RPN expression whose divisions never divide by zero."""
    def build(depth):
        if depth == 0 or rng.random() < 0.25:
            return str(rng.randint(-20, 20))
        a, b = build(depth - 1), build(depth - 1)
        return f"{a} {b} {rng.choice('+-*/')}"
    while True:
        e = build(rng.randint(1, 4))
        try:
            b5_rpn(e)
            return e
        except ZeroDivisionError:
            continue


def b5_c_rpn():
    return ["2 1 + 3 *", "4 13 5 / +", "10 6 9 3 + -11 * / * 17 + 5 +", "7", "-7 2 /", "7 -2 /", "-3 4 *", "3 -4 +"] + \
        [b5_rand_rpn() for _ in range(5)]


def b5_c_next_greater_ii():
    return [[1, 2, 1], [1, 2, 3, 4, 3], [5], [2, 2, 2], [5, 4, 3, 2, 1]] + [rand_arr(n, -50, 50) for n in (6, 15, 60, 300, 1000)]


def b5_c_car_fleet():
    cases = [(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]), (10, [3], [3]), (100, [0, 2, 4], [4, 2, 1]), (10, [6, 8], [3, 2])]
    for n in (5, 12, 40, 200):
        target = rng.randint(n + 5, 1000)
        pos = rng.sample(range(0, target), n)
        cases.append((target, pos, [rng.randint(1, 20) for _ in range(n)]))
    return cases


def b5_c_sum_sub_mins():
    return [[3, 1, 2, 4], [11, 81, 94, 43, 3], [1], [2, 2, 2], [5, 4, 3, 2, 1]] + \
        [rand_arr(n, 1, 30000) for n in (6, 15, 60, 300, 1000)] + [[30000] * 100]


def b5_c_search_matrix():
    cases = [([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3), ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13), ([[1]], 1), ([[1]], 2),
             ([[1, 3]], 3), ([[1], [3]], 3)]
    for m, n in ((3, 4), (6, 6), (10, 8), (30, 30)):
        vals = sorted(rng.sample(range(-10**4, 10**4), m * n))
        mat = [vals[i * n:(i + 1) * n] for i in range(m)]
        cases.append((mat, rng.choice(vals)))
        cases.append((mat, rng.randint(-10**4, 10**4) | 1))
    return cases


def b5_c_word_break():
    cases = [("leetcode", "leet code"), ("applepenapple", "apple pen"), ("catsandog", "cats dog sand and cat"), ("a", "a"), ("ab", "a"),
             ("aaaaaaa", "aaaa aaa"), ("cars", "car ca rs")]
    for _ in range(4):
        words = sorted({"".join(rng.choices("ab", k=rng.randint(1, 4))) for _ in range(rng.randint(2, 6))})
        s = "".join(rng.choice(words) for _ in range(rng.randint(2, 10)))
        cases.append((s, " ".join(words)))
        t = list(s)
        t[rng.randrange(len(t))] = "c"
        cases.append(("".join(t), " ".join(words)))
    return cases


def b5_c_pal_sub():
    return ["abc", "aaa", "a", "abba", "aaaaa", "abacdfgdcaba"] + ["".join(rng.choices("ab", k=n)) for n in (6, 12, 30, 80)] + \
        ["".join(rng.choices("abcdefghij", k=n)) for n in (50, 200)] + ["a" * 150]


def b5_c_target_sum():
    cases = [([1, 1, 1, 1, 1], 3), ([1], 1), ([1], 2), ([0, 0, 0, 0, 0], 0), ([1, 0], 1)]
    for n in (5, 8, 12, 16, 20):
        a = rand_arr(n, 0, 12)
        cases.append((a, rng.choice([sum(a), sum(a) - 2 * rng.choice(a), 0, rng.randint(-sum(a) - 3, sum(a) + 3)])))
    return cases


def b5_c_delete_earn():
    return [[3, 4, 2], [2, 2, 3, 3, 3, 4], [1], [5, 5, 5], [1, 2, 3, 4, 5, 6]] + \
        [rand_arr(n, 1, k) for n, k in ((6, 5), (15, 10), (60, 30), (300, 100), (1000, 1000), (1000, 20))]


def b5_c_cooldown():
    return [[1, 2, 3, 0, 2], [1], [1, 2], [2, 1], [6, 1, 3, 2, 4, 7], [5, 4, 3, 2, 1]] + [rand_arr(n, 0, 100) for n in (6, 15, 60, 300, 1000)]


def b5_c_distinct_subseq():
    cases = [("rabbbit", "rabbit"), ("babgbag", "bag"), ("a", "a"), ("a", "b"), ("aaa", "aa"), ("abc", "abcd"), ("ddd", "dd")]
    for n, m in ((8, 3), (14, 4), (20, 5), (26, 6), (30, 8)):
        while True:
            s = "".join(rng.choices("abc", k=n))
            t = "".join(rng.choices("abc", k=m))
            if b5_distinct_subseq(s, t) < 2**31:
                cases.append((s, t))
                break
    return cases


def b5_rand_pattern(n):
    out = []
    for _ in range(n):
        c = rng.choice("abc.")
        out.append(c + ("*" if rng.random() < 0.4 else ""))
    return "".join(out)


def b5_c_regex():
    cases = [("aa", "a"), ("aa", "a*"), ("ab", ".*"), ("aab", "c*a*b"), ("mississippi", "mis*is*p*."), ("a", "ab*"), ("ab", ".*c"),
             ("aaa", "a*a"), ("abcd", "d*")]
    for _ in range(9):
        p = b5_rand_pattern(rng.randint(2, 6))
        s = "".join(rng.choices("abc", k=rng.randint(1, 8)))
        cases.append((s, p))
    return cases


def b5_c_burst():
    return [[3, 1, 5, 8], [1, 5], [7], [0, 0], [9, 76, 64, 21], [3, 1, 5, 8, 2, 4]] + [rand_arr(n, 0, 100) for n in (6, 10, 20, 35, 50)]


def b5_c_stock3():
    return [[3, 3, 5, 0, 0, 3, 1, 4], [1, 2, 3, 4, 5], [7, 6, 4, 3, 1], [1], [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]] + \
        [rand_arr(n, 0, 100) for n in (6, 15, 60, 300, 1000)]


def b5_c_falling():
    return [[[2, 1, 3], [6, 5, 4], [7, 8, 9]], [[-19, 57], [-40, -5]], [[5]], [[1, 2], [3, 4]]] + [b5_matrix(n, n, -100, 100) for n in (4, 6, 10, 30, 60)]


def b5_c_combo_count():
    cases = [([2, 3, 6, 7], 7), ([2, 3, 5], 8), ([2], 1), ([1], 2), ([3, 5, 7], 4)]
    for n, t in ((3, 15), (4, 40), (5, 100), (6, 200), (4, 300)):
        cases.append((rng.sample(range(1, 40), n), t))
    return cases


def b5_c_network():
    cases = [([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2), ([[1, 2, 1]], 2, 1), ([[1, 2, 1]], 2, 2), ([[1, 2, 5], [1, 3, 2], [3, 2, 1]], 3, 1)]
    for n, m in ((5, 8), (8, 12), (15, 40), (40, 120), (80, 300)):
        edges = [[rng.randint(1, n), rng.randint(1, n), rng.randint(1, 30)] for _ in range(m)]
        edges = [e for e in edges if e[0] != e[1]] or [[1, 2, 3]]
        cases.append((edges, n, rng.randint(1, n)))
    return cases


def b5_c_provinces():
    def sym(n, p):
        g = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    g[i][j] = g[j][i] = 1
        return g
    return [[[1, 1, 0], [1, 1, 0], [0, 0, 1]], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[1]], [[1, 1], [1, 1]]] + \
        [sym(n, p) for n, p in ((5, 0.2), (8, 0.15), (12, 0.1), (20, 0.08), (40, 0.04))]


def b5_c_redundant():
    cases = [[[1, 2], [1, 3], [2, 3]], [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]], [[1, 2], [1, 2]]]
    for n in (4, 7, 12, 30, 100):
        edges = [[rng.randint(1, i - 1), i] for i in range(2, n + 1)]
        extra = rng.sample(range(1, n + 1), 2)
        edges.append(extra)
        rng.shuffle(edges)
        edges = [rng.sample(e, 2) for e in edges]
        cases.append(edges)
    return cases


def b5_c_min_connect():
    cases = [[[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]], [[3, 12], [-2, 5], [-4, 1]], [[0, 0]], [[0, 0], [1, 1]]]
    for n in (5, 9, 20, 60, 150):
        cases.append(rng.sample([[x, y] for x in range(-30, 30) for y in range(-30, 30)], n))
    return cases


def b5_c_arrows():
    cases = [[[10, 16], [2, 8], [1, 6], [7, 12]], [[1, 2], [3, 4], [5, 6], [7, 8]], [[1, 2], [2, 3], [3, 4], [4, 5]], [[1, 5]],
             [[-2147483648, 2147483647]]]
    for n in (5, 12, 40, 150, 500):
        row = []
        for _ in range(n):
            a = rng.randint(-100, 100)
            row.append([a, a + rng.randint(0, 40)])
        cases.append(row)
    return cases


def b5_c_flowers():
    cases = [([1, 0, 0, 0, 1], 1), ([1, 0, 0, 0, 1], 2), ([0], 1), ([1], 0), ([0, 0, 0, 0, 0], 3), ([0, 0, 0, 0, 0], 4), ([1, 0, 1, 0, 1], 0)]
    for n in (8, 20, 100):
        bed, i = [], 0
        while len(bed) < n:
            bed.append(1 if (not bed or bed[-1] == 0) and rng.random() < 0.35 else 0)
        cases.append((bed, rng.randint(0, n // 3)))
        cases.append((bed, n // 2))
    return cases


def b5_c_lemonade():
    cases = [[5, 5, 5, 10, 20], [5, 5, 10, 10, 20], [5], [10], [5, 10, 5, 20], [5, 5, 5, 5, 20, 20, 5, 5, 20, 5], [20, 5]]
    for n in (6, 15, 60, 300):
        cases.append([rng.choices([5, 10, 20], weights=[6, 2, 2])[0] for _ in range(n)])
        cases.append([5] * (n // 2) + [rng.choice([5, 10, 20]) for _ in range(n // 2)])
    return cases


def b5_c_tasks():
    cases = [([1, 1, 1, 2, 2, 2], 2), ([1, 1, 1, 2, 2, 2], 0), ([1, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 7], 2), ([1], 5), ([1, 2, 3, 4], 3)]
    for n, k, lab in ((8, 2, 3), (20, 3, 4), (60, 5, 6), (200, 10, 10), (300, 50, 26)):
        cases.append(([rng.randint(1, lab) for _ in range(n)], k))
    return cases


def b5_c_hamming():
    return [(1, 4), (3, 1), (0, 0), (0, 2**31 - 1), (2**31 - 1, 2**31 - 1), (93, 73), (10**9, 1)] + \
        [(rng.randint(0, 2**31 - 1), rng.randint(0, 2**31 - 1)) for _ in range(4)]


def b5_c_range_and():
    return [(5, 7), (0, 0), (1, 2147483647), (6, 6), (12, 15), (0, 1), (2147483646, 2147483647)] + \
        [tuple(sorted((rng.randint(0, 10**9), rng.randint(0, 10**9)))) for _ in range(3)] + [(rng.randint(0, 100), rng.randint(100, 200))]


def b5_c_ugly():
    return [10, 1, 2, 11, 15, 50, 100, 500, 1000, 1500, 1690, 7]


def b5_c_subtree():
    cases = [([3, 4, 5, 1, 2], [4, 1, 2]), ([3, 4, 5, 1, 2, None, None, None, None, 0], [4, 1, 2]), ([1], [1]), ([1, 1], [1]), ([1, 2, 3], [2])]
    for m in (6, 12, 30, 80):
        t = rand_tree(m, 0, 6)
        root = tok2tree(t)
        nodes, stack = [], [root]
        while stack:
            n = stack.pop()
            nodes.append(n)
            stack += [c for c in (n.left, n.right) if c]
        cases.append((t, tree2tok(rng.choice(nodes))))
        cases.append((t, rand_tree(rng.randint(1, max(1, m // 3)), 0, 6)))
    return cases


def b5_c_level():
    return [[3, 9, 20, None, None, 15, 7], [1], [], [1, 2, 3, 4, None, None, 5], [1, None, 2, None, 3]] + [rand_tree(m) for m in (6, 14, 30, 70, 100)]


def b5_c_min_depth():
    return [[3, 9, 20, None, None, 15, 7], [2, None, 3, None, 4, None, 5, None, 6], [], [1], [1, 2]] + [rand_tree(m) for m in (6, 14, 30, 70, 100)]


def b5_c_root_leaf():
    cases = [[1, 2, 3], [4, 9, 0, 5, 1], [0], [1, 0], [9, 9, 9]]
    for m in (6, 12, 25, 60, 100):
        while True:
            t = rand_tree(m, 0, 9)
            if b5_root_leaf_numbers(t) < 2**31:
                cases.append(t)
                break
    return cases


def b5_c_rob_tree():
    return [[3, 2, 3, None, 3, None, 1], [3, 4, 5, 1, 3, None, 1], [], [7], [1, 2]] + [rand_tree(m, 0, 100) for m in (6, 14, 30, 70, 100)]


def b5_c_path_sum3():
    cases = [([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1], 8), ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22), ([], 0), ([1], 1),
             ([1, 2], 3), ([1, -1, 1, -1], 0)]
    for m in (6, 14, 30, 70, 100):
        t = rand_tree(m, -4, 8)
        cases.append((t, rng.randint(-4, 14)))
    return cases


def b5_c_build():
    cases = [([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]), ([-1], [-1])]
    for m in (2, 3, 5, 9, 20, 50, 100):
        cases.append(b5_pre_in(b5_distinct_tree(m)))
    return cases


def b5_c_remove_elems():
    cases = [([1, 2, 6, 3, 4, 5, 6], 6), ([], 1), ([7, 7, 7, 7], 7), ([1, 2], 3), ([5], 5)]
    for n in (6, 15, 50, 100):
        cases.append((rand_list(n, 0, 6), rng.randint(0, 6)))
    return cases


def b5_c_rotate_list():
    cases = [([1, 2, 3, 4, 5], 2), ([0, 1, 2], 4), ([], 3), ([1], 99), ([1, 2], 0), ([1, 2, 3], 3)]
    for n in (5, 12, 40, 100):
        cases.append((rand_list(n, -50, 50), rng.randint(0, 10**9)))
    return cases


def b5_c_partition():
    cases = [([1, 4, 3, 2, 5, 2], 3), ([2, 1], 2), ([], 1), ([1], 0), ([5, 4, 3], 6), ([5, 4, 3], 0)]
    for n in (6, 15, 50, 100):
        cases.append((rand_list(n, -20, 20), rng.randint(-20, 20)))
    return cases


def b5_c_dedup_all():
    cases = [[1, 2, 3, 3, 4, 4, 5], [1, 1, 1, 2, 3], [], [1], [1, 1], [1, 2, 3]]
    for n in (6, 15, 50, 100):
        cases.append(rand_sorted_list(n, 0, n // 2 + 1))
    return cases


def b5_c_rev_between():
    cases = [([1, 2, 3, 4, 5], 2, 4), ([5], 1, 1), ([3, 5], 1, 2), ([1, 2, 3], 2, 2), ([1, 2, 3, 4], 1, 4)]
    for n in (6, 12, 40, 100):
        l = rng.randint(1, n)
        cases.append((rand_list(n, -50, 50), l, rng.randint(l, n)))
    return cases


def b5_c_twin():
    return [[5, 4, 2, 1], [4, 2, 2, 3], [1, 100000], [1, 1]] + [rand_list(n, 1, 10**5) for n in (4, 10, 30, 100, 100)]


def _tri(n, lo=1): return list(range(lo, n + lo))


PROBLEMS += [
    mk("plus-one", "Plus One", "EASY", ["array", "math"], [("digits", "int[]")], "int[]", b5_plus_one, b5_c_plus_one(),
       "A large non-negative integer is stored as an array of its decimal digits, most significant digit first. Add one to the number and return the digits of the result.",
       "Line 1: `n`.\nLine 2: the `n` digits, space separated.", "The digits of the incremented number, space separated.",
       ["`1 <= n <= 100`", "`0 <= digits[i] <= 9`", "No leading zeros, except the number 0 itself"]),
    mk("squares-of-a-sorted-array", "Squares of a Sorted Array", "EASY", ["array", "two-pointers", "sorting"], [("nums", "int[]")], "int[]",
       b5_sorted_squares, b5_c_squares(),
       "Given an integer array sorted in non-decreasing order, return an array of the squares of each number, also sorted in non-decreasing order. Try to beat `O(n log n)`.",
       ARR_IN, "The sorted squares, space separated.", ["`1 <= n <= 1000`", "`-100 <= nums[i] <= 100`", "`nums` is sorted in non-decreasing order"]),
    mk("find-all-numbers-disappeared-in-an-array", "Find All Numbers Disappeared in an Array", "EASY", ["array", "hash-table"], [("nums", "int[]")], "int[]",
       b5_disappeared, b5_c_disappeared(),
       "`nums` has `n` integers, each in the range `[1, n]`. Return, in ascending order, every number in `[1, n]` that does not appear in `nums`.",
       ARR_IN, "The missing numbers in ascending order, space separated.", ["`2 <= n <= 1000`", "`1 <= nums[i] <= n`", "At least one number is missing"]),
    mk("pascals-triangle", "Pascal's Triangle", "EASY", ["array", "dynamic-programming"], [("numRows", "int")], "int[][]", b5_pascal,
       [5, 1, 2, 3, 6, 10, 15, 20, 30],
       "Return the first `numRows` rows of Pascal's triangle. Each number is the sum of the two numbers directly above it, and each row starts and ends with `1`.",
       "A single integer `numRows`.", "The rows of the triangle, one row per line.", ["`1 <= numRows <= 30`"]),
    mk("rotate-array", "Rotate Array", "MEDIUM", ["array", "math", "two-pointers"], [("nums", "int[]"), ("k", "int")], "int[]", b5_rotate_array, b5_c_rotate_array(),
       "Rotate the array to the right by `k` steps and return the rotated array. Try to do it in place with `O(1)` extra space.",
       "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The rotated array, space separated.",
       ["`1 <= n <= 1000`", "`-1000 <= nums[i] <= 1000`", "`0 <= k <= 10^5`"]),
    mk("sort-colors", "Sort Colors", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]")], "int[]", b5_sort_colors, b5_c_sort_colors(),
       "The array holds only `0`, `1` and `2` (red, white, blue). Sort it so equal numbers are adjacent in the order `0, 1, 2`, without a library sort. A one-pass solution with constant space exists.",
       ARR_IN, "The sorted array, space separated.", ["`1 <= n <= 300`", "`nums[i]` is `0`, `1` or `2`"]),
    mk("next-permutation", "Next Permutation", "MEDIUM", ["array", "two-pointers"], [("nums", "int[]")], "int[]", b5_next_perm, b5_c_next_perm(),
       "Return the next lexicographically greater permutation of `nums`. If there is none (the array is in descending order), return the lowest possible order (ascending). Use `O(1)` extra space.",
       ARR_IN, "The next permutation, space separated.", ["`1 <= n <= 100`", "`0 <= nums[i] <= 100`"]),
    mk("find-the-duplicate-number", "Find the Duplicate Number", "MEDIUM", ["array", "two-pointers", "binary-search"], [("nums", "int[]")], "int",
       b5_find_dup, b5_c_find_dup(),
       "`nums` holds `n + 1` integers in the range `[1, n]`, and exactly one value is repeated (possibly several times). Return it without modifying the array and using only constant extra space.",
       "Line 1: `n + 1`, the length of the array.\nLine 2: the integers, space separated.", "The repeated number.",
       ["`1 <= n <= 1000`", "`nums.length == n + 1`", "Exactly one value appears more than once"]),
    mk("spiral-matrix", "Spiral Matrix", "MEDIUM", ["matrix", "array"], [("matrix", "int[][]")], "int[]", b5_spiral, b5_c_spiral(),
       "Return all elements of the `m x n` matrix in spiral order, starting at the top-left corner and going clockwise.", MAT_IN,
       "The elements in spiral order, space separated.", ["`1 <= m, n <= 10`", "`-100 <= matrix[i][j] <= 100`"]),
    mk("rotate-image", "Rotate Image", "MEDIUM", ["matrix", "array", "math"], [("matrix", "int[][]")], "int[][]", b5_rotate_image, b5_c_rotate_image(),
       "Rotate the `n x n` matrix by 90 degrees clockwise and return it. Try to do it in place.", MAT_IN, MAT_OUT, ["`1 <= n <= 20`", "`-1000 <= matrix[i][j] <= 1000`"]),
    mk("set-matrix-zeroes", "Set Matrix Zeroes", "MEDIUM", ["matrix", "array", "hash-table"], [("matrix", "int[][]")], "int[][]", b5_set_zeroes, b5_c_set_zeroes(),
       "If an element of the `m x n` matrix is `0`, set its entire row and column to `0`. Return the matrix. An `O(1)` extra space solution exists.", MAT_IN, MAT_OUT,
       ["`1 <= m, n <= 10`", "`-1000 <= matrix[i][j] <= 1000`"]),
    mk("3sum-closest", "3Sum Closest", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]"), ("target", "int")], "int", b5_three_sum_closest, b5_c_three_closest(),
       "Return the sum of three integers in `nums` that is closest to `target`. If two sums are equally close, return the smaller one.",
       "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.", "The closest sum.",
       ["`3 <= n <= 300`", "`-1000 <= nums[i] <= 1000`", "`-10^4 <= target <= 10^4`"]),
    mk("find-first-and-last-position-of-element-in-sorted-array", "Find First and Last Position of Element in Sorted Array", "MEDIUM", ["array", "binary-search"],
       [("nums", "int[]"), ("target", "int")], "int[]", b5_first_last, b5_c_first_last(),
       "Given an array sorted in non-decreasing order, return the first and last index of `target` as `first last`, or `-1 -1` if it is absent. Use `O(log n)` time.",
       "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `target`.", "Two integers, space separated.",
       ["`1 <= n <= 1000`", "`nums` is sorted in non-decreasing order"]),
    mk("search-a-2d-matrix", "Search a 2D Matrix", "MEDIUM", ["matrix", "binary-search"], [("matrix", "int[][]"), ("target", "int")], "bool", b5_search_matrix, b5_c_search_matrix(),
       "Each row of the matrix is sorted ascending and the first number of every row is greater than the last number of the previous row. Return `true` if `target` is in the matrix, in `O(log(m * n))` time.",
       MAT_IN + "\nLast line: `target`.", "`true` or `false`.", ["`1 <= m, n <= 30`", "`-10^4 <= matrix[i][j], target <= 10^4`"]),
    mk("evaluate-reverse-polish-notation", "Evaluate Reverse Polish Notation", "MEDIUM", ["stack", "math"], [("tokens", "str")], "int", b5_rpn, b5_c_rpn(),
       "Evaluate an arithmetic expression written in reverse Polish notation. The operators are `+`, `-`, `*` and `/`, and division truncates toward zero. The expression is always valid and never divides by zero.",
       "A single line: the tokens separated by single spaces.", "The value of the expression.",
       ["`1 <= tokens.length <= 10^4`", "Each token is an operator or an integer in `[-200, 200]`", "The result fits in a 32-bit integer"]),
    mk("next-greater-element-ii", "Next Greater Element II", "MEDIUM", ["array", "stack", "monotonic-stack"], [("nums", "int[]")], "int[]", b5_next_greater_ii, b5_c_next_greater_ii(),
       "The array is circular. For every element, return the first strictly greater number found when scanning forward (wrapping around), or `-1` if there is none.",
       ARR_IN, "One value per element, space separated.", ["`1 <= n <= 1000`", "`-10^9 <= nums[i] <= 10^9`"]),
    mk("car-fleet", "Car Fleet", "MEDIUM", ["array", "stack", "sorting"], [("target", "int"), ("position", "int[]"), ("speed", "int[]")], "int", b5_car_fleet, b5_c_car_fleet(),
       "Cars drive toward a destination `target` miles away on a one-lane road. A car can never pass another; it catches up and then drives at the slower car's speed, forming a fleet. Return the number of fleets that reach the destination.",
       "Line 1: `target`.\nLines 2-3: `n` then the `n` starting positions.\nLines 4-5: `n` then the `n` speeds.", "The number of fleets.",
       ["`1 <= n <= 200`", "`0 <= position[i] < target <= 1000`, all positions distinct", "`1 <= speed[i] <= 20`"]),
    mk("sum-of-subarray-minimums", "Sum of Subarray Minimums", "MEDIUM", ["array", "stack", "monotonic-stack"], [("arr", "int[]")], "int", b5_sum_sub_mins, b5_c_sum_sub_mins(),
       "Return the sum of `min(subarray)` over every contiguous subarray of `arr`, modulo `10^9 + 7`.", ARR_IN, "The sum modulo `10^9 + 7`.",
       ["`1 <= n <= 1000`", "`1 <= arr[i] <= 30000`"]),
    mk("word-break", "Word Break", "MEDIUM", ["string", "dynamic-programming", "hash-table"], [("s", "str"), ("wordDict", "str")], "bool", b5_word_break, b5_c_word_break(),
       "Return `true` if `s` can be split into a sequence of one or more words from the dictionary. A word may be reused any number of times.",
       "Line 1: `s`.\nLine 2: the dictionary words, separated by single spaces.", "`true` or `false`.",
       ["`1 <= s.length <= 300`", "Lowercase English letters", "Dictionary words are non-empty and distinct"]),
    mk("palindromic-substrings", "Palindromic Substrings", "MEDIUM", ["string", "dynamic-programming"], [("s", "str")], "int", b5_pal_substrings, b5_c_pal_sub(),
       "Return how many substrings of `s` are palindromes. Substrings at different positions count separately even if their text is equal.",
       "A single line containing `s`.", "The number of palindromic substrings.", ["`1 <= s.length <= 1000`", "Lowercase English letters"]),
    mk("target-sum", "Target Sum", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]"), ("target", "int")], "int", b5_target_sum, b5_c_target_sum(),
       "Put a `+` or `-` in front of every number and add them up. Return the number of different sign assignments that evaluate to `target`.",
       "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.", "The number of ways.",
       ["`1 <= n <= 20`", "`0 <= nums[i] <= 12`", "The answer fits in a 32-bit integer"]),
    mk("delete-and-earn", "Delete and Earn", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]")], "int", b5_delete_earn, b5_c_delete_earn(),
       "In one move pick any `nums[i]`, earn `nums[i]` points and delete every element equal to `nums[i] - 1` or `nums[i] + 1`. Return the maximum points you can earn.",
       ARR_IN, "The maximum points.", ["`1 <= n <= 1000`", "`1 <= nums[i] <= 1000`"]),
    mk("best-time-to-buy-and-sell-stock-with-cooldown", "Best Time to Buy and Sell Stock with Cooldown", "MEDIUM", ["array", "dynamic-programming"],
       [("prices", "int[]")], "int", b5_cooldown, b5_c_cooldown(),
       "You may trade as often as you like, but after selling you cannot buy on the next day (a one-day cooldown), and you may hold at most one share. Return the maximum profit.",
       ARR_IN, "The maximum profit.", ["`1 <= n <= 1000`", "`0 <= prices[i] <= 1000`"]),
    mk("minimum-falling-path-sum", "Minimum Falling Path Sum", "MEDIUM", ["matrix", "dynamic-programming"], [("matrix", "int[][]")], "int", b5_falling_path, b5_c_falling(),
       "A falling path starts at any cell in the top row and moves down one row at a time to the cell directly below or diagonally left or right. Return the minimum sum over all falling paths of the `n x n` matrix.",
       MAT_IN, "The minimum falling path sum.", ["`1 <= n <= 60`", "`-100 <= matrix[i][j] <= 100`"]),
    mk("combination-sum-count", "Combination Sum", "MEDIUM", ["array", "backtracking", "dynamic-programming"], [("candidates", "int[]"), ("target", "int")], "sets",
       combination_sum_all, b5_c_combo_count(),
       "Given distinct positive integers `candidates` and a `target`, return all the **unique** combinations of candidates that add up to `target`, in any order. A candidate may be chosen any number of times; two combinations are different if the count of at least one chosen number differs.",
       "Line 1: `n`.\nLine 2: `n` distinct integers.\nLine 3: `target`.", "One combination per line, numbers separated by spaces. The starter code sorts the lines before printing, so the order never matters.",
       ["`1 <= n <= 6`", "`1 <= candidates[i] <= 40`", "`1 <= target <= 300`"]),
    mk("distinct-subsequences", "Distinct Subsequences", "HARD", ["string", "dynamic-programming"], [("s", "str"), ("t", "str")], "int", b5_distinct_subseq, b5_c_distinct_subseq(),
       "Return the number of distinct subsequences of `s` that equal `t`.", "Line 1: `s`.\nLine 2: `t`.", "The count.",
       ["`1 <= s.length, t.length <= 30`", "Lowercase English letters", "The answer fits in a 32-bit integer"]),
    mk("regular-expression-matching", "Regular Expression Matching", "HARD", ["string", "dynamic-programming"], [("s", "str"), ("p", "str")], "bool", b5_regex, b5_c_regex(),
       "Implement matching with `.` (any single character) and `*` (zero or more of the preceding element). The match must cover the **entire** string `s`.",
       "Line 1: `s`.\nLine 2: the pattern `p`.", "`true` or `false`.",
       ["`1 <= s.length, p.length <= 20`", "`s` has only lowercase letters; `p` has lowercase letters, `.` and `*`", "Every `*` follows a letter or `.`"]),
    mk("burst-balloons", "Burst Balloons", "HARD", ["array", "dynamic-programming"], [("nums", "int[]")], "int", b5_burst, b5_c_burst(),
       "Bursting balloon `i` earns `nums[i-1] * nums[i] * nums[i+1]` coins, where out-of-range neighbours count as `1`. Burst all balloons in the best order and return the maximum coins.",
       ARR_IN, "The maximum coins.", ["`1 <= n <= 50`", "`0 <= nums[i] <= 100`"]),
    mk("best-time-to-buy-and-sell-stock-iii", "Best Time to Buy and Sell Stock III", "HARD", ["array", "dynamic-programming"], [("prices", "int[]")], "int", b5_stock3, b5_c_stock3(),
       "You may complete at most two transactions, and must sell before buying again. Return the maximum profit.", ARR_IN, "The maximum profit.",
       ["`1 <= n <= 1000`", "`0 <= prices[i] <= 100`"]),
    mk("network-delay-time", "Network Delay Time", "MEDIUM", ["graph", "heap"], [("times", "int[][]"), ("n", "int"), ("k", "int")], "int", b5_network_delay, b5_c_network(),
       "A signal is sent from node `k` of a directed, weighted network with nodes `1..n`. Each row `u v w` of `times` is an edge from `u` to `v` taking `w` time. Return the time for all nodes to receive the signal, or `-1` if some node never does.",
       "Lines 1+: the number of edges, then one `u v w` row per edge.\nNext line: `n`.\nLast line: `k`.", "The minimum time, or `-1`.",
       ["`1 <= n <= 100`", "`1 <= edges <= 6000`", "`1 <= w <= 100`"]),
    mk("number-of-provinces", "Number of Provinces", "MEDIUM", ["graph", "union-find", "dfs"], [("isConnected", "int[][]")], "int", b5_provinces, b5_c_provinces(),
       "`isConnected[i][j] = 1` means cities `i` and `j` are directly connected. A province is a group of cities connected directly or indirectly. Return the number of provinces.",
       MAT_IN, "The number of provinces.", ["`1 <= n <= 200`", "`isConnected[i][i] = 1` and the matrix is symmetric"]),
    mk("redundant-connection", "Redundant Connection", "MEDIUM", ["graph", "union-find"], [("edges", "int[][]")], "int[]", b5_redundant, b5_c_redundant(),
       "A tree with `n` nodes (labelled `1..n`) had one extra edge added, giving `n` edges in total. Return an edge that can be removed so the graph is a tree again. If several qualify, return the one that appears **last** in the input.",
       "Line 1: `n`, the number of edges.\nNext `n` lines: `a b`, one edge per line.", "The edge to remove, as `a b` exactly as it appears in the input.",
       ["`3 <= n <= 100`", "The graph is connected and has exactly one cycle"]),
    mk("min-cost-to-connect-all-points", "Min Cost to Connect All Points", "MEDIUM", ["graph", "union-find", "heap"], [("points", "int[][]")], "int", b5_min_connect, b5_c_min_connect(),
       "Connect all points on a plane using the cheapest set of segments, where a segment between two points costs their Manhattan distance. Return the minimum total cost so that every pair of points is connected by exactly one simple path.",
       "Line 1: `n`.\nNext `n` lines: `x y`.", "The minimum cost.", ["`1 <= n <= 150`", "`-30 <= x, y < 30`", "All points are distinct"]),
    mk("minimum-number-of-arrows-to-burst-balloons", "Minimum Number of Arrows to Burst Balloons", "MEDIUM", ["greedy", "intervals", "sorting"],
       [("points", "int[][]")], "int", b5_arrows, b5_c_arrows(),
       "Balloons are the horizontal intervals `[xstart, xend]`. An arrow shot straight up at `x` bursts every balloon with `xstart <= x <= xend`. Return the fewest arrows that burst all balloons.",
       "Line 1: `n`.\nNext `n` lines: `xstart xend`.", "The minimum number of arrows.",
       ["`1 <= n <= 500`", "`-2^31 <= xstart <= xend <= 2^31 - 1`"]),
    mk("can-place-flowers", "Can Place Flowers", "EASY", ["array", "greedy"], [("flowerbed", "int[]"), ("n", "int")], "bool", b5_flowers, b5_c_flowers(),
       "A flowerbed has plots that are empty (`0`) or planted (`1`), and flowers cannot be planted in adjacent plots. Return `true` if `n` more flowers can be planted without breaking that rule.",
       "Line 1: the length of `flowerbed`.\nLine 2: the plots.\nLine 3: `n`.", "`true` or `false`.",
       ["`1 <= length <= 100`", "No two planted plots are adjacent", "`0 <= n <= length`"]),
    mk("lemonade-change", "Lemonade Change", "EASY", ["array", "greedy"], [("bills", "int[]")], "bool", b5_lemonade, b5_c_lemonade(),
       "Each lemonade costs `$5`. Customers pay with a `$5`, `$10` or `$20` bill, in order, and you start with no change. Return `true` if you can give every customer the correct change.",
       ARR_IN, "`true` or `false`.", ["`1 <= n <= 300`", "`bills[i]` is `5`, `10` or `20`"]),
    mk("task-scheduler", "Task Scheduler", "MEDIUM", ["array", "greedy", "heap"], [("tasks", "int[]"), ("n", "int")], "int", b5_task_scheduler, b5_c_tasks(),
       "Each task (a label) takes one unit of time, and the CPU may idle. Two tasks with the same label must be at least `n` units apart. Return the least number of units needed to finish every task.",
       "Line 1: the number of tasks.\nLine 2: the task labels.\nLine 3: `n`.", "The minimum time.",
       ["`1 <= tasks <= 300`", "`1 <= label <= 26`", "`0 <= n <= 100`"]),
    mk("hamming-distance", "Hamming Distance", "EASY", ["bit-manipulation"], [("x", "int"), ("y", "int")], "int", b5_hamming, b5_c_hamming(),
       "Return the number of bit positions at which the binary representations of `x` and `y` differ.", "Line 1: `x`.\nLine 2: `y`.", "The Hamming distance.",
       ["`0 <= x, y <= 2^31 - 1`"]),
    mk("bitwise-and-of-numbers-range", "Bitwise AND of Numbers Range", "MEDIUM", ["bit-manipulation"], [("left", "int"), ("right", "int")], "int", b5_range_and, b5_c_range_and(),
       "Return the bitwise AND of every integer in the inclusive range `[left, right]`.", "Line 1: `left`.\nLine 2: `right`.", "The AND of the range.",
       ["`0 <= left <= right <= 2^31 - 1`"]),
    mk("ugly-number-ii", "Ugly Number II", "MEDIUM", ["math", "dynamic-programming", "heap"], [("n", "int")], "int", b5_ugly, b5_c_ugly(),
       "An ugly number is a positive integer whose only prime factors are `2`, `3` and `5`. Return the `n`-th ugly number, where `1` is the first.",
       "A single integer `n`.", "The `n`-th ugly number.", ["`1 <= n <= 1690`"]),
    mk("subtree-of-another-tree", "Subtree of Another Tree", "EASY", ["tree", "dfs"], [("root", "tree"), ("subRoot", "tree")], "bool", b5_subtree, b5_c_subtree(),
       "Return `true` if some node of `root` has exactly the same structure and values as the whole tree `subRoot`.",
       "Tree `root` in the format below, then tree `subRoot` in the same format.\n\n" + TREE_IN, "`true` or `false`.", ["`root` has `1 <= n <= 100` nodes", "`subRoot` has `1 <= n <= 100` nodes", VAL]),
    mk("binary-tree-level-order-traversal", "Binary Tree Level Order Traversal", "MEDIUM", ["tree", "bfs"], [("root", "tree")], "int[][]", b5_level_order, b5_c_level(),
       "Return the values of the tree level by level, from left to right.", TREE_IN, "One line per level, values space separated (a blank line for the empty tree).", [LC, "`-20 <= val <= 50`"]),
    mk("minimum-depth-of-binary-tree", "Minimum Depth of Binary Tree", "EASY", ["tree", "dfs", "bfs"], [("root", "tree")], "int", b5_min_depth, b5_c_min_depth(),
       "Return the minimum depth: the number of nodes on the shortest path from the root down to a **leaf** (`0` for the empty tree).", TREE_IN, "The minimum depth.", [LC, VAL]),
    mk("sum-root-to-leaf-numbers", "Sum Root to Leaf Numbers", "MEDIUM", ["tree", "dfs"], [("root", "tree")], "int", b5_root_leaf_numbers, b5_c_root_leaf(),
       "Every node holds a digit `0-9`, so each root-to-leaf path spells a number (for example `1 -> 2 -> 3` is `123`). Return the total of all those numbers.", TREE_IN,
       "The total.", ["`1 <= n <= 100` nodes", "`0 <= val <= 9`", "The answer fits in a 32-bit integer"]),
    mk("house-robber-iii", "House Robber III", "MEDIUM", ["tree", "dfs", "dynamic-programming"], [("root", "tree")], "int", b5_rob_tree, b5_c_rob_tree(),
       "The houses form a binary tree and each node holds the money in that house. Robbing two directly linked houses (parent and child) triggers the alarm. Return the maximum amount you can rob.",
       TREE_IN, "The maximum amount.", [LC, "`0 <= val <= 100`"]),
    mk("path-sum-iii", "Path Sum III", "MEDIUM", ["tree", "dfs"], [("root", "tree"), ("targetSum", "int")], "int", b5_path_sum3, b5_c_path_sum3(),
       "Count the downward paths (from any node to any of its descendants) whose values add up to `targetSum`. A path does not have to start at the root or end at a leaf.",
       TREE_IN + "\nLine 3: `targetSum`.", "The number of paths.", ["`0 <= n <= 100` nodes", "`-100 <= val <= 100`", "`-1000 <= targetSum <= 1000`"]),
    mk("construct-binary-tree-from-preorder-and-inorder-traversal", "Construct Binary Tree from Preorder and Inorder Traversal", "MEDIUM", ["tree", "divide-and-conquer"],
       [("preorder", "int[]"), ("inorder", "int[]")], "tree", b5_build_tree, b5_c_build(),
       "Rebuild the binary tree from its preorder and inorder traversals and return its root.",
       "Lines 1-2: `n` then the preorder values.\nLines 3-4: `n` then the inorder values.", TREE_OUT, ["`1 <= n <= 100`", "All values are unique"]),
    mk("remove-linked-list-elements", "Remove Linked List Elements", "EASY", ["linked-list"], [("head", "list"), ("val", "int")], "list", b5_remove_elements, b5_c_remove_elems(),
       "Remove every node whose value equals `val` and return the new list.", LIST_IN + "\nLine 3: `val`.", LIST_OUT, [LC, "`0 <= val <= 50`"]),
    mk("rotate-list", "Rotate List", "MEDIUM", ["linked-list", "two-pointers"], [("head", "list"), ("k", "int")], "list", b5_rotate_list, b5_c_rotate_list(),
       "Rotate the list to the right by `k` places and return the new list.", LIST_IN + "\nLine 3: `k`.", LIST_OUT, [LC, "`0 <= k <= 10^9`"]),
    mk("partition-list", "Partition List", "MEDIUM", ["linked-list", "two-pointers"], [("head", "list"), ("x", "int")], "list", b5_partition_list, b5_c_partition(),
       "Rearrange the list so every node with a value less than `x` comes before every node with a value greater than or equal to `x`, keeping the original relative order inside each group.",
       LIST_IN + "\nLine 3: `x`.", LIST_OUT, [LC, "`-100 <= val, x <= 100`"]),
    mk("remove-duplicates-from-sorted-list-ii", "Remove Duplicates from Sorted List II", "MEDIUM", ["linked-list", "two-pointers"], [("head", "list")], "list", b5_dedup_all, b5_c_dedup_all(),
       "In a sorted list, delete **every** node whose value appears more than once, so only values that were distinct remain. Return the list.", LIST_IN, LIST_OUT,
       [LC, "The list is sorted in non-decreasing order"]),
    mk("reverse-linked-list-ii", "Reverse Linked List II", "MEDIUM", ["linked-list"], [("head", "list"), ("left", "int"), ("right", "int")], "list", b5_reverse_between, b5_c_rev_between(),
       "Reverse the nodes from position `left` to position `right` (1-indexed) and return the list.", LIST_IN + "\nLine 3: `left`.\nLine 4: `right`.", LIST_OUT,
       ["`1 <= n <= 100`", "`1 <= left <= right <= n`"]),
    mk("maximum-twin-sum-of-a-linked-list", "Maximum Twin Sum of a Linked List", "MEDIUM", ["linked-list", "two-pointers"], [("head", "list")], "int", b5_twin_sum, b5_c_twin(),
       "A list with an even number `n` of nodes has twin pairs: node `i` and node `n - 1 - i`. Return the maximum sum of a twin pair.", LIST_IN, "The maximum twin sum.",
       ["`2 <= n <= 100`, `n` is even", "`1 <= val <= 10^5`"]),
]


# ================================================================ batch 6: more problems (bits, DP, grids, graphs, strings, trees)
def b6_single_number_ii(a):
    ones = twos = 0
    for x in a:
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    return ones if ones < 2**31 else ones - 2**32


def b6_integer_break(n):
    if n <= 3:
        return n - 1
    q, r = divmod(n, 3)
    return 3**q if r == 0 else 3**(q - 1) * 4 if r == 1 else 3**q * 2


def b6_coin_change_ii(amount, coins):
    ways = [1] + [0] * amount
    for c in coins:
        for t in range(c, amount + 1):
            ways[t] += ways[t - c]
    return ways[amount]


def b6_interleave(a, b, c):
    if len(a) + len(b) != len(c):
        return False
    dp = [[False] * (len(b) + 1) for _ in range(len(a) + 1)]
    dp[0][0] = True
    for i in range(len(a) + 1):
        for j in range(len(b) + 1):
            if i and dp[i - 1][j] and a[i - 1] == c[i + j - 1]:
                dp[i][j] = True
            if j and dp[i][j - 1] and b[j - 1] == c[i + j - 1]:
                dp[i][j] = True
    return dp[len(a)][len(b)]


def b6_wildcard(s, p):
    dp = [[False] * (len(p) + 1) for _ in range(len(s) + 1)]
    dp[0][0] = True
    for j in range(1, len(p) + 1):
        dp[0][j] = dp[0][j - 1] and p[j - 1] == "*"
    for i in range(1, len(s) + 1):
        for j in range(1, len(p) + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i][j - 1] or dp[i - 1][j]
            else:
                dp[i][j] = dp[i - 1][j - 1] and p[j - 1] in ("?", s[i - 1])
    return dp[len(s)][len(p)]


def b6_k_distinct(s, k):
    cnt, best, l = collections.Counter(), 0, 0
    for r, ch in enumerate(s):
        cnt[ch] += 1
        while len(cnt) > k:
            cnt[s[l]] -= 1
            if cnt[s[l]] == 0:
                del cnt[s[l]]
            l += 1
        best = max(best, r - l + 1)
    return best


def b6_contiguous(a):
    first, bal, best = {0: -1}, 0, 0
    for i, x in enumerate(a):
        bal += 1 if x else -1
        if bal in first:
            best = max(best, i - first[bal])
        else:
            first[bal] = i
    return best


def b6_valid_sudoku(b):
    seen = set()
    for i in range(9):
        for j in range(9):
            v = b[i][j]
            if v:
                for key in (("r", i, v), ("c", j, v), ("b", i // 3, j // 3, v)):
                    if key in seen:
                        return False
                    seen.add(key)
    return True


def b6_life(b):
    m, n = len(b), len(b[0])
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            c = sum(b[x][y] for x in range(max(0, i - 1), min(m, i + 2)) for y in range(max(0, j - 1), min(n, j + 2))) - b[i][j]
            out[i][j] = 1 if c == 3 or (b[i][j] and c == 2) else 0
    return out


def b6_surrounded(b):
    m, n = len(b), len(b[0])
    keep, stack = set(), [(i, j) for i in range(m) for j in range(n) if (i in (0, m - 1) or j in (0, n - 1)) and b[i][j] == 1]
    while stack:
        i, j = stack.pop()
        if (i, j) in keep:
            continue
        keep.add((i, j))
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < m and 0 <= y < n and b[x][y] == 1 and (x, y) not in keep:
                stack.append((x, y))
    return [[1 if (i, j) in keep else 0 for j in range(n)] for i in range(m)]


def b6_zero_one(g):
    m, n = len(g), len(g[0])
    dist = [[-1] * n for _ in range(m)]
    q = collections.deque()
    for i in range(m):
        for j in range(n):
            if g[i][j] == 0:
                dist[i][j] = 0
                q.append((i, j))
    while q:
        i, j = q.popleft()
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < m and 0 <= y < n and dist[x][y] < 0:
                dist[x][y] = dist[i][j] + 1
                q.append((x, y))
    return dist


def b6_bipartite(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        q = collections.deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True


def b6_cheapest(n, flights, src, dst, k):
    INF = math.inf
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        nxt = dist[:]
        for u, v, w in flights:
            if dist[u] + w < nxt[v]:
                nxt[v] = dist[u] + w
        dist = nxt
    return -1 if dist[dst] == INF else dist[dst]


def b6_min_effort(h):
    m, n = len(h), len(h[0])
    best = [[math.inf] * n for _ in range(m)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        d, i, j = heapq.heappop(heap)
        if (i, j) == (m - 1, n - 1):
            return d
        if d > best[i][j]:
            continue
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < m and 0 <= y < n:
                nd = max(d, abs(h[x][y] - h[i][j]))
                if nd < best[x][y]:
                    best[x][y] = nd
                    heapq.heappush(heap, (nd, x, y))
    return 0


def b6_swim(g):
    n = len(g)
    best = [[math.inf] * n for _ in range(n)]
    best[0][0] = g[0][0]
    heap = [(g[0][0], 0, 0)]
    while heap:
        d, i, j = heapq.heappop(heap)
        if (i, j) == (n - 1, n - 1):
            return d
        if d > best[i][j]:
            continue
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < n and 0 <= y < n:
                nd = max(d, g[x][y])
                if nd < best[x][y]:
                    best[x][y] = nd
                    heapq.heappush(heap, (nd, x, y))
    return 0


def b6_max_rectangle(mat):
    n = len(mat[0])
    heights, best = [0] * n, 0
    for row in mat:
        heights = [h + 1 if v else 0 for h, v in zip(heights, row)]
        st = []
        for i, h in enumerate(heights + [0]):
            start = i
            while st and st[-1][1] >= h:
                idx, hh = st.pop()
                best = max(best, hh * (i - idx))
                start = idx
            st.append((start, h))
    return best


def b6_circular(a):
    total, cur_max, cur_min, best_max, best_min = 0, 0, 0, a[0], a[0]
    for x in a:
        cur_max = max(cur_max + x, x)
        best_max = max(best_max, cur_max)
        cur_min = min(cur_min + x, x)
        best_min = min(best_min, cur_min)
        total += x
    return best_max if best_max < 0 else max(best_max, total - best_min)


def b6_zigzag(t):
    out = b5_level_order(t)
    return [row if i % 2 == 0 else row[::-1] for i, row in enumerate(out)]


def b6_count_nodes(t): return sum(1 for x in t if x is not None)


def b6_min_window_len(s, t):
    need = collections.Counter(t)
    missing, best, l = len(t), math.inf, 0
    for r, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while need[s[l]] < 0:
                need[s[l]] += 1
                l += 1
            best = min(best, r - l + 1)
            need[s[l]] += 1
            missing += 1
            l += 1
    return 0 if best == math.inf else best


def b6_palin2(s):
    def pal(l, r):
        while l < r:
            if s[l] != s[r]:
                return False
            l += 1
            r -= 1
        return True
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]:
            return pal(l + 1, r) or pal(l, r - 1)
        l += 1
        r -= 1
    return True


def b6_isomorphic(s, t):
    a, b = {}, {}
    for x, y in zip(s, t):
        if a.setdefault(x, y) != y or b.setdefault(y, x) != x:
            return False
    return True


def b6_first_unique(s):
    c = collections.Counter(s)
    return next((i for i, ch in enumerate(s) if c[ch] == 1), -1)


def b6_repeated(s): return (s + s)[1:-1].find(s) != -1


def b6_min_add_paren(s):
    open_, add = 0, 0
    for ch in s:
        if ch == "(":
            open_ += 1
        elif open_:
            open_ -= 1
        else:
            add += 1
    return add + open_


def b6_town_judge(n, trust):
    score = [0] * (n + 1)
    for a, b in trust:
        score[a] -= 1
        score[b] += 1
    return next((i for i in range(1, n + 1) if score[i] == n - 1), -1)


def b6_four_sum_count(a, target):
    a, res = sorted(a), set()
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            l, r = j + 1, len(a) - 1
            while l < r:
                s = a[i] + a[j] + a[l] + a[r]
                if s == target:
                    res.add((a[i], a[j], a[l], a[r]))
                    l += 1
                    r -= 1
                elif s < target:
                    l += 1
                else:
                    r -= 1
    return len(res)


def b6_kth_matrix(m, k): return sorted(v for r in m for v in r)[k - 1]


def b6_merge_sorted(a, m, b, n): return sorted(a[:m] + b[:n])


def b6_sum_two(a, b): return a + b


def b6_grid(m, n, p=0.5): return [[1 if rng.random() < p else 0 for _ in range(n)] for _ in range(m)]


def b6_c_single_ii():
    cases = [[2, 2, 3, 2], [0, 1, 0, 1, 0, 1, 99], [-2, -2, 1, -2], [7], [5, 5, 5, 9]]
    for n in (4, 10, 31, 100, 300):
        vals = rng.sample(range(-10**6, 10**6), n // 3 + 1)
        arr = [v for v in vals[1:] for _ in range(3)] + [vals[0]]
        rng.shuffle(arr)
        cases.append(arr)
    return cases


def b6_c_integer_break(): return [2, 10, 3, 4, 5, 6, 7, 8, 9, 11, 25, 40, 58]


def b6_c_coin_ii():
    cases = [(5, [1, 2, 5]), (3, [2]), (10, [10]), (0, [1]), (4, [1, 2, 3])]
    for n, amt in ((3, 50), (4, 120), (5, 300), (6, 500), (4, 1000)):
        cases.append((amt, rng.sample(range(1, 60), n)))
    return cases


def b6_c_interleave():
    cases = [("aabcc", "dbbca", "aadbbcbcac"), ("aabcc", "dbbca", "aadbbbaccc"), ("", "", ""), ("a", "", "a"), ("ab", "cd", "acbd"), ("ab", "cd", "adbc")]
    cases = [c for c in cases if all(c)]  # inputs are single lines, so keep every string non-empty
    for n, m in ((3, 3), (5, 4), (8, 8), (12, 10), (20, 20)):
        a = "".join(rng.choices("ab", k=n))
        b = "".join(rng.choices("ab", k=m))
        merged, i, j = [], 0, 0
        while i < n or j < m:
            if j >= m or (i < n and rng.random() < 0.5):
                merged.append(a[i])
                i += 1
            else:
                merged.append(b[j])
                j += 1
        c = "".join(merged)
        cases.append((a, b, c))
        t = list(c)
        p = rng.randrange(len(t))
        t[p] = "b" if t[p] == "a" else "a"
        cases.append((a, b, "".join(t)))
    return cases


def b6_c_wildcard():
    cases = [("aa", "a"), ("aa", "*"), ("cb", "?a"), ("adceb", "*a*b"), ("acdcb", "a*c?b"), ("a", "?"), ("abc", "a?c"), ("abc", "*")]
    for _ in range(8):
        s = "".join(rng.choices("abc", k=rng.randint(1, 10)))
        p = "".join(rng.choice("abc?*") if rng.random() < 0.8 else rng.choice("?*") for _ in range(rng.randint(1, 7)))
        cases.append((s, p))
        cases.append((s, "".join(c if rng.random() < 0.6 else rng.choice("?*") for c in s)))
    return cases


def b6_c_k_distinct():
    cases = [("eceba", 2), ("aa", 1), ("a", 3), ("abcabc", 2), ("abaccc", 2)]
    for n, k in ((8, 2), (15, 3), (40, 2), (100, 4), (300, 5)):
        cases.append(("".join(rng.choices("abcdefgh", k=n)), k))
    return cases


def b6_c_contiguous():
    return [[0, 1], [0, 1, 0], [0], [1, 1, 1], [0, 0, 1, 0, 0, 0, 1, 1]] + [[rng.randint(0, 1) for _ in range(n)] for n in (6, 15, 60, 300, 1000)]


def b6_valid_board(blank):
    base = [[(3 * (r % 3) + r // 3 + c) % 9 + 1 for c in range(9)] for r in range(9)]
    digits = list(range(1, 10))
    rng.shuffle(digits)
    rows = [r for g in rng.sample(range(3), 3) for r in rng.sample(range(g * 3, g * 3 + 3), 3)]
    cols = [c for g in rng.sample(range(3), 3) for c in rng.sample(range(g * 3, g * 3 + 3), 3)]
    b = [[digits[base[r][c] - 1] for c in cols] for r in rows]
    for _ in range(blank):
        b[rng.randrange(9)][rng.randrange(9)] = 0
    return b


def b6_c_sudoku():
    cases = []
    for blank in (50, 30, 60):
        cases.append(b6_valid_board(blank))
    for blank in (45, 20, 55, 35):
        b = b6_valid_board(blank)
        filled = [(i, j) for i in range(9) for j in range(9) if b[i][j]]
        i, j = rng.choice(filled)
        i2, j2 = rng.choice([(x, y) for x, y in filled if (x, y) != (i, j) and (x == i or y == j or (x // 3, y // 3) == (i // 3, j // 3))] or [(i, j)])
        b[i2][j2] = b[i][j]
        cases.append(b)
        cases.append(b6_valid_board(blank))
    return cases


def b6_c_life():
    return [[[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]], [[1, 1], [1, 0]], [[1]], [[0, 0], [0, 0]]] + [b6_grid(m, n) for m, n in ((4, 4), (5, 6), (8, 8), (10, 6), (12, 12))]


def b6_c_surrounded():
    return [[[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 0, 1], [1, 0, 1, 1]], [[0]], [[1]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]]] + \
        [b6_grid(m, n, 0.6) for m, n in ((4, 4), (5, 7), (8, 8), (10, 10), (12, 6))]


def b6_c_01():
    cases = [[[0, 0, 0], [0, 1, 0], [0, 0, 0]], [[0, 0, 0], [0, 1, 0], [1, 1, 1]], [[0]], [[1, 0]]]
    for m, n in ((4, 4), (5, 7), (8, 8), (10, 10), (12, 6)):
        g = b6_grid(m, n, 0.8)
        g[rng.randrange(m)][rng.randrange(n)] = 0
        cases.append(g)
    return cases


def b6_c_bipartite():
    cases = [(4, [[0, 1], [0, 2], [0, 3], [1, 2], [2, 3]]), (4, [[0, 2], [0, 3], [1, 2], [1, 3]]), (2, [[0, 1]]), (3, [[0, 1], [1, 2], [2, 0]])]
    for n, m in ((6, 6), (8, 7), (12, 10), (20, 22), (40, 45)):
        if rng.random() < 0.5:  # bipartite by construction
            side = [rng.randint(0, 1) for _ in range(n)]
            pairs = [[u, v] for u in range(n) for v in range(u + 1, n) if side[u] != side[v]]
            cases.append((n, rng.sample(pairs, min(len(pairs), m)) or [[0, 1]]))
        else:
            pairs = [[u, v] for u in range(n) for v in range(u + 1, n)]
            cases.append((n, rng.sample(pairs, m)))
    return cases


def b6_c_cheapest():
    cases = [(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1),
             (3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1), (3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0), (2, [[0, 1, 5]], 1, 0, 3)]
    for n, m in ((5, 9), (8, 16), (12, 30), (20, 60), (40, 120)):
        fl = [[rng.randrange(n), rng.randrange(n), rng.randint(1, 100)] for _ in range(m)]
        fl = [f for f in fl if f[0] != f[1]]
        cases.append((n, fl, rng.randrange(n), rng.randrange(n), rng.randint(0, 4)))
    return cases


def b6_c_effort():
    cases = [[[1, 2, 2], [3, 8, 2], [5, 3, 5]], [[1, 2, 3], [3, 8, 4], [5, 3, 5]], [[1]], [[1, 10, 6, 7, 9, 10, 4, 9]]]
    for m, n in ((3, 3), (4, 6), (6, 6), (10, 10), (15, 12)):
        cases.append(b5_matrix(m, n, 1, 100))
    return cases


def b6_c_swim():
    cases = [[[0, 2], [1, 3]], [[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]], [[0]]]
    for n in (3, 4, 6, 8, 12, 20):
        vals = list(range(n * n))
        rng.shuffle(vals)
        cases.append([vals[i * n:(i + 1) * n] for i in range(n)])
    return cases


def b6_c_max_rect():
    return [[[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]], [[0]], [[1]], [[1, 1], [1, 1]]] + \
        [b6_grid(m, n, 0.75) for m, n in ((4, 4), (5, 8), (8, 8), (10, 12), (16, 10))]


def b6_c_circular():
    return [[1, -2, 3, -2], [5, -3, 5], [-3, -2, -3], [7], [-1], [3, -1, 2, -1]] + [rand_arr(n, -30, 30) for n in (6, 15, 60, 300, 1000)]


def b6_c_zigzag():
    return [[3, 9, 20, None, None, 15, 7], [1], [], [1, 2, 3, 4, None, None, 5], [1, 2, 3, 4, 5, 6, 7]] + [rand_tree(m) for m in (6, 14, 30, 70, 100)]


def b6_c_count_nodes():
    return [[1, 2, 3, 4, 5, 6], [], [1], [1, 2], [1, 2, 3]] + [rand_tree(m) for m in (6, 14, 30, 70, 100)]


def b6_c_min_window():
    cases = [("ADOBECODEBANC", "ABC"), ("a", "a"), ("a", "aa"), ("abc", "d"), ("aab", "ab")]
    for n, m in ((10, 3), (20, 4), (60, 5), (150, 6), (300, 8)):
        s = "".join(rng.choices("ABCDEF", k=n))
        t = "".join(rng.sample(s, min(m, n)))
        cases.append((s, t))
    return cases


def b6_c_palin2():
    cases = ["aba", "abca", "abc", "a", "ab", "aa", "deeee", "cupuufxoohdfpgjdmysgvhmvffcnqxjjxqncffvmhvgsymdjgpfdhooxfuupuc"]
    for n in (6, 12, 30, 100):
        half = "".join(rng.choices("abc", k=n // 2))
        s = half + half[::-1]
        t = list(s)
        t[rng.randrange(len(t))] = rng.choice("abc")
        cases.append("".join(t))
        s2 = list(s)
        s2.insert(rng.randrange(len(s2)), rng.choice("abc"))
        cases.append("".join(s2))
    return cases


def b6_c_isomorphic():
    cases = [("egg", "add"), ("foo", "bar"), ("paper", "title"), ("ab", "aa"), ("a", "b"), ("badc", "baba")]
    for n in (6, 12, 30, 100):
        s = "".join(rng.choices("abcdefg", k=n))
        mp = dict(zip("abcdefg", rng.sample("pqrstuv", 7)))
        t = "".join(mp[c] for c in s)
        cases.append((s, t))
        t2 = list(t)
        t2[rng.randrange(n)] = rng.choice("pqrstuv")
        cases.append((s, "".join(t2)))
    return cases


def b6_c_first_unique():
    return ["leetcode", "loveleetcode", "aabb", "z", "abcabc", "aadadaad"] + ["".join(rng.choices("abcdef", k=n)) for n in (8, 20, 60)] + ["".join(rng.choices("abcdefghij", k=300))]


def b6_c_repeated():
    cases = ["abab", "aba", "abcabcabcabc", "a", "aa", "ab", "abaababaab"]
    for n in (2, 3, 5, 12):
        unit = "".join(rng.choices("ab", k=n))
        cases.append(unit * rng.randint(2, 6))
        cases.append("".join(rng.choices("ab", k=n * 3)))
    return cases


def b6_c_min_add():
    return ["())", "(((", "()", ")(", "()))((", "()()"] + ["".join(rng.choices("()", k=n)) for n in (6, 12, 30, 100, 300)]


def b6_c_judge():
    cases = [(2, [[1, 2]]), (3, [[1, 3], [2, 3]]), (3, [[1, 3], [2, 3], [3, 1]]), (4, [[1, 3], [1, 4], [2, 3], [2, 4], [4, 3]])]
    for n in (5, 10, 30, 100):
        j = rng.randint(1, n)
        trust = [[i, j] for i in range(1, n + 1) if i != j]
        extra = [[a, b] for a in range(1, n + 1) for b in range(1, n + 1) if a != b and a != j and b != j and rng.random() < 0.05]
        trust += extra
        if rng.random() < 0.4:
            trust = [t for t in trust if t != trust[0]]
        if not trust:
            trust = [[1, 2]]
        rng.shuffle(trust)
        cases.append((n, trust))
    return cases


def b6_c_four_sum():
    cases = [([1, 0, -1, 0, -2, 2], 0), ([2, 2, 2, 2, 2], 8), ([0, 0, 0, 0], 0), ([1, 2, 3, 4], 100)]
    for n in (6, 10, 20, 40, 80):
        a = rand_arr(n, -10, 10)
        cases.append((a, rng.randint(-10, 10)))
    return cases


def b6_c_kth_matrix():
    cases = [([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8), ([[-5]], 1), ([[1, 2], [1, 3]], 2)]
    for n in (3, 5, 8, 12, 20):
        rows = [sorted(rng.randint(-100, 100) for _ in range(n)) for _ in range(n)]
        cols = [list(c) for c in zip(*rows)]
        cols = [sorted(c) for c in cols]
        mat = [list(r) for r in zip(*cols)]
        mat = [sorted(r) for r in mat]
        # sort rows then columns repeatedly until stable so both rows and columns are non-decreasing
        for _ in range(n):
            mat = [sorted(r) for r in mat]
            mat = [list(r) for r in zip(*[sorted(c) for c in zip(*mat)])]
        cases.append((mat, rng.randint(1, n * n)))
    return cases


def b6_c_merge_sorted():
    cases = [([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3), ([1], 1, [], 0), ([0], 0, [1], 1), ([4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3)]
    for m, n in ((3, 4), (8, 8), (20, 5), (50, 50)):
        a = sorted(rand_arr(m, -100, 100)) + [0] * n
        cases.append((a, m, sorted(rand_arr(n, -100, 100)), n))
    return [c for c in cases if c[3] > 0]


def b6_c_sum_two():
    return [(1, 2), (-2, 3), (0, 0), (-1000, 1000), (1000, 1000), (-1000, -1000), (-5, -7)] + [(rng.randint(-1000, 1000), rng.randint(-1000, 1000)) for _ in range(4)]


PROBLEMS += [
    mk("single-number-ii", "Single Number II", "MEDIUM", ["array", "bit-manipulation"], [("nums", "int[]")], "int", b6_single_number_ii, b6_c_single_ii(),
       "Every element of `nums` appears exactly three times except one, which appears once. Return that single element using linear time and constant extra space.",
       ARR_IN, "The element that appears once.", ["`1 <= n <= 300`", "`-2^31 <= nums[i] <= 2^31 - 1`"]),
    mk("integer-break", "Integer Break", "MEDIUM", ["math", "dynamic-programming"], [("n", "int")], "int", b6_integer_break, b6_c_integer_break(),
       "Break `n` into the sum of at least two positive integers and return the largest product you can get from those integers.", "A single integer `n`.",
       "The maximum product.", ["`2 <= n <= 58`"]),
    mk("coin-change-ii", "Coin Change II", "MEDIUM", ["array", "dynamic-programming"], [("amount", "int"), ("coins", "int[]")], "int", b6_coin_change_ii, b6_c_coin_ii(),
       "Return the number of combinations of the given coins (unlimited supply of each, order does not matter) that make up `amount`.",
       "Line 1: `amount`.\nLine 2: `n`.\nLine 3: the `n` coin values.", "The number of combinations.",
       ["`1 <= n <= 6`", "`1 <= coins[i] <= 60`, all distinct", "`0 <= amount <= 1000`", "The answer fits in a 32-bit integer"]),
    mk("interleaving-string", "Interleaving String", "HARD", ["string", "dynamic-programming"], [("s1", "str"), ("s2", "str"), ("s3", "str")], "bool", b6_interleave, b6_c_interleave(),
       "Return `true` if `s3` is formed by interleaving `s1` and `s2`: both strings are split into pieces, joined alternately, and the relative order of characters within each string is kept.",
       "Line 1: `s1`.\nLine 2: `s2`.\nLine 3: `s3`.", "`true` or `false`.", ["`1 <= s1.length, s2.length <= 20`", "`1 <= s3.length <= 40`", "Lowercase English letters"]),
    mk("wildcard-matching", "Wildcard Matching", "HARD", ["string", "dynamic-programming"], [("s", "str"), ("p", "str")], "bool", b6_wildcard, b6_c_wildcard(),
       "Match the **entire** string `s` against pattern `p`, where `?` matches any single character and `*` matches any sequence of characters (including the empty one).",
       "Line 1: `s`.\nLine 2: `p`.", "`true` or `false`.", ["`1 <= s.length, p.length <= 20`", "`s` has lowercase letters", "`p` has lowercase letters, `?` and `*`"]),
    mk("longest-substring-with-at-most-k-distinct-characters", "Longest Substring with At Most K Distinct Characters", "MEDIUM", ["string", "sliding-window", "hash-table"],
       [("s", "str"), ("k", "int")], "int", b6_k_distinct, b6_c_k_distinct(),
       "Return the length of the longest substring of `s` that contains at most `k` distinct characters.", "Line 1: `s`.\nLine 2: `k`.", "The length.",
       ["`1 <= s.length <= 300`", "`1 <= k <= 20`", "Lowercase English letters"]),
    mk("contiguous-array", "Contiguous Array", "MEDIUM", ["array", "hash-table"], [("nums", "int[]")], "int", b6_contiguous, b6_c_contiguous(),
       "Given a binary array, return the maximum length of a contiguous subarray with an equal number of `0` and `1`.", ARR_IN, "The maximum length (`0` if none).",
       ["`1 <= n <= 1000`", "`nums[i]` is `0` or `1`"]),
    mk("valid-sudoku", "Valid Sudoku", "MEDIUM", ["matrix", "hash-table"], [("board", "int[][]")], "bool", b6_valid_sudoku, b6_c_sudoku(),
       "Determine whether a partially filled `9 x 9` Sudoku board is valid: digits `1-9` must not repeat in any row, column or `3 x 3` box. Empty cells are `0`. The board does not need to be solvable.",
       "Line 1: `9`.\nNext 9 lines: the 9 cells of each row, space separated.", "`true` or `false`.", ["`board.length == 9` and every row has 9 cells", "`0 <= board[i][j] <= 9`"]),
    mk("game-of-life", "Game of Life", "MEDIUM", ["matrix", "array"], [("board", "int[][]")], "int[][]", b6_life, b6_c_life(),
       "Apply one step of Conway's Game of Life to the board (`1` live, `0` dead; neighbours are the 8 surrounding cells, outside the board counts as dead). A live cell survives with 2 or 3 live neighbours, a dead cell with exactly 3 becomes alive, and everything else is dead next step. All cells update at once.",
       MAT_IN, MAT_OUT, ["`1 <= m, n <= 12`", "`board[i][j]` is `0` or `1`"]),
    mk("surrounded-regions", "Surrounded Regions", "MEDIUM", ["matrix", "dfs", "bfs", "graph"], [("board", "int[][]")], "int[][]", b6_surrounded, b6_c_surrounded(),
       "The board holds `1` (O) and `0` (X). Capture every region of `1`s that is fully surrounded by `0`s: flip all its cells to `0`. A region touching the border (directly or through connected `1`s) is never captured. Four-directional connectivity.",
       MAT_IN, MAT_OUT, ["`1 <= m, n <= 12`", "`board[i][j]` is `0` or `1`"]),
    mk("01-matrix", "01 Matrix", "MEDIUM", ["matrix", "bfs", "graph"], [("mat", "int[][]")], "int[][]", b6_zero_one, b6_c_01(),
       "For every cell return the distance to the nearest `0` (distance between adjacent cells is `1`, four directions). The matrix has at least one `0`.",
       MAT_IN, MAT_OUT, ["`1 <= m, n <= 12`", "`mat[i][j]` is `0` or `1`", "At least one `0` exists"]),
    mk("is-graph-bipartite", "Is Graph Bipartite?", "MEDIUM", ["graph", "bfs", "dfs"], [("n", "int"), ("edges", "int[][]")], "bool", b6_bipartite, b6_c_bipartite(),
       "An undirected graph with nodes `0..n-1` is bipartite if its nodes can be split into two sets so that every edge joins nodes from different sets. Return whether it is. The graph may be disconnected.",
       "Line 1: `n`.\nLine 2: `m`, the number of edges.\nNext `m` lines: `u v`.", "`true` or `false`.", ["`2 <= n <= 40`", "`1 <= m <= 100`", "No self-loops or repeated edges"]),
    mk("cheapest-flights-within-k-stops", "Cheapest Flights Within K Stops", "MEDIUM", ["graph", "dynamic-programming", "heap"],
       [("n", "int"), ("flights", "int[][]"), ("src", "int"), ("dst", "int"), ("k", "int")], "int", b6_cheapest, b6_c_cheapest(),
       "There are `n` cities and directed flights `[from, to, price]`. Return the cheapest price from `src` to `dst` using **at most `k` stops** (so at most `k + 1` flights), or `-1` if impossible.",
       "Line 1: `n`.\nLine 2: `m`, the number of flights.\nNext `m` lines: `from to price`.\nThen `src`, `dst` and `k`, one per line.", "The cheapest price, or `-1`.",
       ["`1 <= n <= 40`", "`1 <= price <= 100`", "`0 <= k <= 4`"]),
    mk("path-with-minimum-effort", "Path With Minimum Effort", "MEDIUM", ["matrix", "graph", "heap", "binary-search"], [("heights", "int[][]")], "int", b6_min_effort, b6_c_effort(),
       "Travel from the top-left to the bottom-right cell moving up, down, left or right. The effort of a route is the largest absolute height difference between two consecutive cells on it. Return the minimum effort.",
       MAT_IN, "The minimum effort.", ["`1 <= m, n <= 15`", "`1 <= heights[i][j] <= 100`"]),
    mk("swim-in-rising-water", "Swim in Rising Water", "HARD", ["matrix", "graph", "heap", "binary-search"], [("grid", "int[][]")], "int", b6_swim, b6_c_swim(),
       "In an `n x n` grid of distinct elevations, at time `t` the water covers every cell with elevation at most `t`, and you may swim between adjacent cells that are both covered. Return the earliest time you can reach the bottom-right cell from the top-left.",
       MAT_IN, "The least time.", ["`1 <= n <= 20`", "Values are a permutation of `0..n*n-1`"]),
    mk("maximal-rectangle", "Maximal Rectangle", "HARD", ["matrix", "dynamic-programming", "stack", "monotonic-stack"], [("matrix", "int[][]")], "int", b6_max_rectangle, b6_c_max_rect(),
       "In a binary matrix, find the largest rectangle containing only `1`s and return its area.", MAT_IN, "The area.", ["`1 <= m, n <= 16`", "`matrix[i][j]` is `0` or `1`"]),
    mk("maximum-sum-circular-subarray", "Maximum Sum Circular Subarray", "MEDIUM", ["array", "dynamic-programming"], [("nums", "int[]")], "int", b6_circular, b6_c_circular(),
       "The array is circular (the end connects back to the start). Return the maximum sum of a non-empty subarray, where a subarray may wrap around but uses each element at most once.",
       ARR_IN, "The maximum sum.", ["`1 <= n <= 1000`", "`-30000 <= nums[i] <= 30000`"]),
    mk("binary-tree-zigzag-level-order-traversal", "Binary Tree Zigzag Level Order Traversal", "MEDIUM", ["tree", "bfs"], [("root", "tree")], "int[][]", b6_zigzag, b6_c_zigzag(),
       "Return the level order traversal, but alternate direction: the first level left to right, the next right to left, and so on.", TREE_IN,
       "One line per level (a blank line for the empty tree).", [LC, "`-20 <= val <= 50`"]),
    mk("count-complete-tree-nodes", "Count Complete Tree Nodes", "EASY", ["tree", "binary-search", "dfs"], [("root", "tree")], "int", b6_count_nodes, b6_c_count_nodes(),
       "Return the number of nodes in the tree. (For a complete tree there is an `O(log^2 n)` solution; any tree is accepted here.)", TREE_IN, "The number of nodes.", [LC, VAL]),
    mk("minimum-window-substring-length", "Minimum Window Substring", "HARD", ["string", "sliding-window", "hash-table"], [("s", "str"), ("t", "str")], "str", min_window_text, b6_c_min_window(),
       "Return the minimum window **substring** of `s` such that every character in `t` (including duplicates) is included in the window, or the empty string if there is none. The test data always has a unique answer.", "Line 1: `s`.\nLine 2: `t`.",
       "The window, or an empty line.", ["`1 <= s.length <= 300`", "`1 <= t.length <= 300`", "Uppercase and lowercase English letters"]),
    mk("valid-palindrome-ii", "Valid Palindrome II", "EASY", ["string", "two-pointers"], [("s", "str")], "bool", b6_palin2, b6_c_palin2(),
       "Return `true` if `s` can become a palindrome after deleting **at most one** character.", "A single line containing `s`.", "`true` or `false`.",
       ["`1 <= s.length <= 100000`", "Lowercase English letters"]),
    mk("isomorphic-strings", "Isomorphic Strings", "EASY", ["string", "hash-table"], [("s", "str"), ("t", "str")], "bool", b6_isomorphic, b6_c_isomorphic(),
       "Two strings are isomorphic if the characters of `s` can be replaced to get `t`, with every occurrence replaced consistently and no two different characters mapping to the same one.",
       "Line 1: `s`.\nLine 2: `t`.", "`true` or `false`.", ["`1 <= s.length <= 100`", "`s.length == t.length`"]),
    mk("first-unique-character-in-a-string", "First Unique Character in a String", "EASY", ["string", "hash-table"], [("s", "str")], "int", b6_first_unique, b6_c_first_unique(),
       "Return the index of the first character that does not repeat anywhere in `s`, or `-1` if there is none.", "A single line containing `s`.", "The index, or `-1`.",
       ["`1 <= s.length <= 300`", "Lowercase English letters"]),
    mk("repeated-substring-pattern", "Repeated Substring Pattern", "EASY", ["string"], [("s", "str")], "bool", b6_repeated, b6_c_repeated(),
       "Return `true` if `s` can be built by repeating one of its substrings two or more times.", "A single line containing `s`.", "`true` or `false`.",
       ["`1 <= s.length <= 100`", "Lowercase English letters"]),
    mk("minimum-add-to-make-parentheses-valid", "Minimum Add to Make Parentheses Valid", "MEDIUM", ["string", "stack", "greedy"], [("s", "str")], "int", b6_min_add_paren, b6_c_min_add(),
       "Return the minimum number of parentheses you must insert (anywhere) to make the string of `(` and `)` valid.", "A single line containing `s`.", "The minimum insertions.",
       ["`1 <= s.length <= 300`", "`s` has only `(` and `)`"]),
    mk("find-the-town-judge", "Find the Town Judge", "EASY", ["graph", "array", "hash-table"], [("n", "int"), ("trust", "int[][]")], "int", b6_town_judge, b6_c_judge(),
       "People are labelled `1..n`. The town judge trusts nobody and is trusted by everybody else. Each row `a b` of `trust` means `a` trusts `b`. Return the judge's label, or `-1`.",
       "Line 1: `n`.\nLine 2: `m`, the number of trust pairs.\nNext `m` lines: `a b`.", "The judge's label, or `-1`.", ["`2 <= n <= 100`", "`1 <= m <= 10^4`", "All pairs are distinct"]),
    mk("4sum-count", "4Sum", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]"), ("target", "int")], "sets", four_sum_all, b6_c_four_sum(),
       "Return all the **unique** quadruplets `[nums[a], nums[b], nums[c], nums[d]]` with four different indices whose sum is `target`, in any order. The answer must not contain duplicate quadruplets.",
       "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.", "One quadruplet per line, numbers separated by spaces. The starter code sorts the lines before printing, so the order never matters.", ["`4 <= n <= 80`", "`-10 <= nums[i], target <= 10`"]),
    mk("kth-smallest-element-in-a-sorted-matrix", "Kth Smallest Element in a Sorted Matrix", "MEDIUM", ["matrix", "heap", "binary-search"], [("matrix", "int[][]"), ("k", "int")], "int",
       b6_kth_matrix, b6_c_kth_matrix(),
       "Every row and every column of the `n x n` matrix is sorted in non-decreasing order. Return the `k`-th smallest element (counting duplicates, 1-indexed).",
       MAT_IN + "\nLast line: `k`.", "The `k`-th smallest value.", ["`1 <= n <= 20`", "`1 <= k <= n * n`", "`-100 <= matrix[i][j] <= 100`"]),
    mk("merge-sorted-array", "Merge Sorted Array", "EASY", ["array", "two-pointers", "sorting"], [("nums1", "int[]"), ("m", "int"), ("nums2", "int[]"), ("n", "int")], "int[]",
       b6_merge_sorted, b6_c_merge_sorted(),
       "`nums1` has `m` sorted values followed by `n` placeholder zeros, and `nums2` has `n` sorted values. Merge them into one sorted array of length `m + n` and return it (in place from the back is the classic approach).",
       "Line 1: the length of `nums1` (`m + n`).\nLine 2: `nums1`.\nLine 3: `m`.\nLine 4: the length of `nums2`.\nLine 5: `nums2`.\nLine 6: `n`.",
       "The merged array, space separated.", ["`1 <= n <= 50`", "`0 <= m <= 50`", "`-100 <= values <= 100`"]),
    mk("sum-of-two-integers", "Sum of Two Integers", "EASY", ["bit-manipulation", "math"], [("a", "int"), ("b", "int")], "int", b6_sum_two, b6_c_sum_two(),
       "Return `a + b` **without using the `+` or `-` operators** (use XOR for the sum without carry and AND plus shift for the carry).",
       "Line 1: `a`.\nLine 2: `b`.", "The sum.", ["`-1000 <= a, b <= 1000`"]),
]


# ============================================================== Striver A2Z sheet, batch 1 (arrays)
# New problems use their own seeded generator, so adding them never changes the data of any existing problem.
a2z_rng = random.Random(20261201)


def a2z_arr(n, lo, hi):
    return [a2z_rng.randint(lo, hi) for _ in range(n)]


def largest_element(nums):
    return max(nums)


def second_largest(nums):
    distinct = sorted(set(nums))
    return distinct[-2] if len(distinct) >= 2 else -1


def sorted_and_rotated(nums):
    n = len(nums)
    return sum(1 for i in range(n) if nums[i] > nums[(i + 1) % n]) <= 1


def rotate_left_by_one(nums):
    return nums[1:] + nums[:1]


def linear_search(nums, target):
    return nums.index(target) if target in nums else -1


def union_sorted(a, b):
    return sorted(set(a) | set(b))


def max_consecutive_ones(nums):
    best = run = 0
    for x in nums:
        run = run + 1 if x == 1 else 0
        best = max(best, run)
    return best


def rearrange_by_sign(nums):
    pos = [x for x in nums if x > 0]
    neg = [x for x in nums if x < 0]
    out = []
    for p, q in zip(pos, neg):
        out += [p, q]
    return out


def leaders(nums):
    out, best = [], None
    for x in reversed(nums):
        if best is None or x >= best:
            out.append(x)
            best = x
    return out[::-1]


def longest_sum_k(nums, k):
    first, total, best = {0: -1}, 0, 0
    for i, x in enumerate(nums):
        total += x
        if total - k in first:
            best = max(best, i - first[total - k])
        first.setdefault(total, i)
    return best


def repeating_and_missing(nums):
    n = len(nums)
    seen = set()
    repeating = 0
    for x in nums:
        if x in seen:
            repeating = x
        seen.add(x)
    missing = next(v for v in range(1, n + 1) if v not in seen)
    return [repeating, missing]


def count_xor_k(nums, k):
    seen, xor, total = {0: 1}, 0, 0
    for x in nums:
        xor ^= x
        total += seen.get(xor ^ k, 0)
        seen[xor] = seen.get(xor, 0) + 1
    return total


def count_inversions(nums):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] > nums[j])


def reverse_pairs(nums):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] > 2 * nums[j])


def majority_third(nums):
    c = collections.Counter(nums)
    return sorted(v for v, f in c.items() if f > len(nums) // 3)


def longest_zero_sum(nums):
    return longest_sum_k(nums, 0)


def a2z_cases_rotated():
    out = []
    for n in [1, 2, 3, 5, 8, 20, 60, 200]:
        base = sorted(a2z_arr(n, -50, 50))
        r = a2z_rng.randrange(n)
        out.append(base[r:] + base[:r])
    out += [[3, 4, 5, 1, 2], [2, 1, 3, 4], [1, 1, 1], [6, 10, 6], [1, 2, 3, 4, 5]]
    return out


def a2z_cases_union():
    out = [([1, 2, 3, 4, 5], [1, 2, 3, 6, 7]), ([2, 2, 3, 4, 5], [1, 1, 2, 3, 4]), ([], [5]), ([1], [])]
    for n, m in [(5, 7), (20, 25), (80, 60), (200, 150)]:
        out.append((sorted(a2z_arr(n, -30, 60)), sorted(a2z_arr(m, -30, 60))))
    return out


def a2z_cases_signs():
    out = []
    for h in [1, 2, 3, 5, 10, 40, 150]:
        vals = [a2z_rng.randint(1, 500) for _ in range(h)] + [-a2z_rng.randint(1, 500) for _ in range(h)]
        a2z_rng.shuffle(vals)
        out.append(vals)
    return out


def a2z_cases_repeating():
    out = []
    for n in [2, 3, 5, 8, 20, 100, 500]:
        arr = list(range(1, n + 1))
        a2z_rng.shuffle(arr)
        i, j = a2z_rng.sample(range(n), 2)
        arr[i] = arr[j]
        out.append(arr)
    return out


A2Z_BATCH_1 = [
    mk("largest-element-in-array", "Largest Element in the Array", "EASY", ["array"], [("nums", "int[]")], "int",
       largest_element, [a2z_arr(n, -10000, 10000) for n in [1, 2, 5, 17, 100, 600, 1000]] + [[7], [-3, -3, -9]],
       "Given an array `nums`, return the largest element.", ARR_IN, "The largest element.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("second-largest-element", "Second Largest Element in the Array", "EASY", ["array"], [("nums", "int[]")], "int",
       second_largest, [a2z_arr(n, -50, 50) for n in [2, 3, 6, 25, 150, 800]] + [[4, 4, 4], [9], [1, 2], [5, 5, 3]],
       "Return the second largest **distinct** value of `nums`, or `-1` if there is none (for example when every "
       "element is equal).", ARR_IN, "The second largest distinct element, or `-1`.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("check-if-array-is-sorted-and-rotated", "Check if Array Is Sorted and Rotated", "EASY", ["array"],
       [("nums", "int[]")], "bool", sorted_and_rotated, a2z_cases_rotated() + [a2z_arr(30, -9, 9), a2z_arr(9, 1, 3)],
       "Return `true` if `nums` was originally sorted in non-decreasing order and then rotated some number of "
       "positions (possibly zero). Duplicates are allowed.", ARR_IN, "`true` or `false`.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("left-rotate-array-by-one", "Left Rotate an Array by One Place", "EASY", ["array"], [("nums", "int[]")], "int[]",
       rotate_left_by_one, [a2z_arr(n, -99, 99) for n in [1, 2, 3, 7, 40, 300]],
       "Rotate `nums` one position to the left: the first element moves to the end and every other element shifts "
       "one place towards the front. Return the rotated array.", ARR_IN, "The rotated array.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("linear-search", "Linear Search", "EASY", ["array"], [("nums", "int[]"), ("target", "int")], "int",
       linear_search, [(a2z_arr(n, -20, 20), a2z_rng.randint(-25, 25)) for n in [1, 4, 9, 30, 120, 700]] + [([1, 2, 3], 3), ([5, 5, 5], 5), ([4], 9)],
       "Return the index of the first occurrence of `target` in `nums`, or `-1` if it does not appear.",
       "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.", "The first index, or `-1`.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i], target <= 10^4`"]),
    mk("union-of-two-sorted-arrays", "Union of Two Sorted Arrays", "EASY", ["array", "two-pointers"],
       [("a", "int[]"), ("b", "int[]")], "int[]", union_sorted, a2z_cases_union(),
       "Both arrays are sorted in non-decreasing order. Return their union as a sorted array without duplicates.",
       "Line 1: `n`.\nLine 2: `n` integers (array `a`).\nLine 3: `m`.\nLine 4: `m` integers (array `b`).",
       "The sorted union, each value once.", ["`0 <= n, m <= 1000`", "`-10^4 <= a[i], b[i] <= 10^4`"]),
    mk("max-consecutive-ones", "Max Consecutive Ones", "EASY", ["array"], [("nums", "int[]")], "int",
       max_consecutive_ones, [[a2z_rng.randint(0, 1) for _ in range(n)] for n in [1, 3, 8, 20, 90, 500]] + [[1, 1, 1], [0, 0], [1, 1, 0, 1, 1, 1]],
       "`nums` holds only `0` and `1`. Return the maximum number of consecutive `1`s.", ARR_IN,
       "The longest run of ones.", ["`1 <= n <= 1000`", "`nums[i]` is `0` or `1`"]),
    mk("rearrange-array-elements-by-sign", "Rearrange Array Elements by Sign", "MEDIUM", ["array", "two-pointers"],
       [("nums", "int[]")], "int[]", rearrange_by_sign, a2z_cases_signs(),
       "`nums` has an equal number of positive and negative integers and no zeros. Rearrange it so that the signs "
       "alternate, starting with a positive one, keeping the relative order of the positives and of the negatives.",
       ARR_IN, "The rearranged array.", ["`2 <= n <= 1000`, `n` is even", "`nums[i] != 0`"]),
    mk("leaders-in-an-array", "Leaders in an Array", "MEDIUM", ["array"], [("nums", "int[]")], "int[]",
       leaders, [a2z_arr(n, -20, 60) for n in [1, 3, 6, 15, 90, 500]] + [[16, 17, 4, 3, 5, 2], [10, 22, 12, 3, 0, 6]],
       "An element is a leader if it is greater than or equal to every element to its right (the last element is "
       "always a leader). Return the leaders in the order they appear in `nums`.", ARR_IN, "The leaders, left to right.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("longest-subarray-with-sum-k", "Longest Subarray with Sum K", "MEDIUM", ["array", "hash-table", "prefix-sum"],
       [("nums", "int[]"), ("k", "int")], "int", longest_sum_k,
       [(a2z_arr(n, -9, 9), a2z_rng.randint(-12, 12)) for n in [3, 8, 20, 70, 300, 900]] + [([1, 2, 3, 1, 1, 1, 1, 3, 3], 6), ([2, 3, 5], 5), ([-1, 1, 1], 1)],
       "Return the length of the longest contiguous subarray of `nums` whose sum equals `k`, or `0` if none exists. "
       "Values can be negative.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The length, or `0`.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i], k <= 10^4`"]),
    mk("find-the-repeating-and-missing-number", "Find the Repeating and Missing Number", "MEDIUM", ["array", "math", "hash-table"],
       [("nums", "int[]")], "int[]", repeating_and_missing, a2z_cases_repeating(),
       "`nums` should hold every number from `1` to `n` once, but one number appears twice and another is missing. "
       "Return `[repeating, missing]`.", ARR_IN, "Two integers: the repeating one, then the missing one.",
       ["`2 <= n <= 1000`", "`1 <= nums[i] <= n`"]),
    mk("count-subarrays-with-given-xor", "Count Subarrays with Given XOR", "MEDIUM", ["array", "hash-table", "bit-manipulation"],
       [("nums", "int[]"), ("k", "int")], "int", count_xor_k,
       [(a2z_arr(n, 0, 31), a2z_rng.randint(0, 31)) for n in [2, 6, 15, 60, 250, 900]] + [([4, 2, 2, 6, 4], 6), ([5, 6, 7, 8, 9], 5)],
       "Return the number of contiguous subarrays of `nums` whose bitwise XOR equals `k`.",
       "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The number of subarrays.",
       ["`1 <= n <= 1000`", "`0 <= nums[i], k <= 10^5`"]),
    mk("count-inversions", "Count Inversions", "MEDIUM", ["array", "divide-and-conquer", "sorting"],
       [("nums", "int[]")], "int", count_inversions, [a2z_arr(n, -999, 999) for n in [2, 5, 12, 60, 300, 1000]] + [[5, 3, 2, 4, 1], [1, 2, 3]],
       "An inversion is a pair of indices `i < j` with `nums[i] > nums[j]`. Return the number of inversions in `nums`. "
       "A merge-sort based solution runs in `O(n log n)`.", ARR_IN, "The number of inversions.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("reverse-pairs", "Reverse Pairs", "HARD", ["array", "divide-and-conquer", "sorting"], [("nums", "int[]")], "int",
       reverse_pairs, [a2z_arr(n, -999, 999) for n in [2, 5, 12, 60, 300, 1000]] + [[1, 3, 2, 3, 1], [2, 4, 3, 5, 1]],
       "Return the number of reverse pairs: pairs of indices `i < j` with `nums[i] > 2 * nums[j]`.", ARR_IN,
       "The number of reverse pairs.", ["`1 <= n <= 1000`", "`-10^5 <= nums[i] <= 10^5`"]),
    mk("majority-element-ii", "Majority Element II", "MEDIUM", ["array", "hash-table", "sorting"], [("nums", "int[]")], "int[]",
       majority_third, [[a2z_rng.choice([1, 2, 3, 4]) for _ in range(n)] for n in [3, 8, 20, 60, 300]] + [[3, 2, 3], [1], [1, 2], [2, 2, 9, 3, 9, 3, 9, 3, 9, 3, 9, 3, 9, 9, 9, 2]],
       "Return every element that appears more than `n / 3` times, in ascending order (at most two exist).", ARR_IN,
       "The elements in ascending order (an empty line if there are none).", ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("largest-subarray-with-0-sum", "Largest Subarray with 0 Sum", "MEDIUM", ["array", "hash-table", "prefix-sum"],
       [("nums", "int[]")], "int", longest_zero_sum, [a2z_arr(n, -6, 6) for n in [3, 9, 25, 80, 400, 1000]] + [[15, -2, 2, -8, 1, 7, 10, 23], [1, 2, 3]],
       "Return the length of the longest contiguous subarray of `nums` whose sum is `0`, or `0` if none exists.", ARR_IN,
       "The length, or `0`.", ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
]
PROBLEMS += A2Z_BATCH_1


# ============================================================== Striver A2Z sheet, batch 2 (binary search)
def sorted_arr(n, lo, hi):
    return sorted(a2z_arr(n, lo, hi))


def bs_lower_bound(nums, x):
    return bisect.bisect_left(nums, x)


def bs_upper_bound(nums, x):
    return bisect.bisect_right(nums, x)


def bs_floor_ceil(nums, x):
    below = [v for v in nums if v <= x]
    above = [v for v in nums if v >= x]
    return [max(below) if below else -1, min(above) if above else -1]


def bs_count(nums, x):
    return bisect.bisect_right(nums, x) - bisect.bisect_left(nums, x)


def bs_rotated_contains(nums, x):
    return x in nums


def bs_rotated_min(nums):
    return min(nums)


def bs_rotation_count(nums):
    return nums.index(min(nums))


def bs_single(nums):
    out = 0
    for v in nums:
        out ^= v
    return out


def bs_peak_index(nums):
    return nums.index(max(nums))


def bs_nth_root(n, m):
    x = round(m ** (1.0 / n))
    for c in (x - 1, x, x + 1):
        if c >= 0 and c ** n == m:
            return c
    return -1


def bs_bouquets(bloom, m, k):
    if m * k > len(bloom):
        return -1

    def ok(day):
        made = run = 0
        for b in bloom:
            run = run + 1 if b <= day else 0
            if run == k:
                made += 1
                run = 0
        return made >= m

    lo, hi = min(bloom), max(bloom)
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def bs_smallest_divisor(nums, threshold):
    lo, hi = 1, max(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(-(-x // mid) for x in nums) <= threshold:
            hi = mid
        else:
            lo = mid + 1
    return lo


def bs_aggressive_cows(stalls, cows):
    stalls = sorted(stalls)

    def ok(d):
        placed, last = 1, stalls[0]
        for x in stalls[1:]:
            if x - last >= d:
                placed += 1
                last = x
        return placed >= cows

    lo, hi = 1, stalls[-1] - stalls[0]
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def bs_kth_two(a, b, k):
    return sorted(a + b)[k - 1]


def bs_row_max_ones(mat):
    counts = [sum(r) for r in mat]
    return counts.index(max(counts))


def bs_matrix_contains(mat, target):
    return any(target in row for row in mat)


def bs_kth_missing(arr, k):
    missing, cur = 0, 0
    for v in arr:
        gap = v - cur - 1
        if missing + gap >= k:
            return cur + (k - missing)
        missing += gap
        cur = v
    return cur + (k - missing)


def bs_matrix_median(mat):
    flat = sorted(v for row in mat for v in row)
    return flat[len(flat) // 2]


def a2z_cases_search_x(lo=-40, hi=40):
    out = []
    for n in [1, 2, 5, 12, 40, 150, 600]:
        out.append((sorted_arr(n, lo, hi), a2z_rng.randint(lo - 5, hi + 5)))
    out += [([1, 2, 8, 10, 11, 12, 19], 9), ([3, 3, 3], 3), ([5], 1), ([1, 4, 4, 4, 9], 4)]
    return out


def a2z_rotate(arr):
    r = a2z_rng.randrange(len(arr)) if len(arr) > 1 else 0
    return arr[r:] + arr[:r]


def a2z_cases_rotated_dups():
    out = []
    for n in [1, 3, 6, 15, 50, 200]:
        arr = a2z_rotate(sorted_arr(n, -9, 9))
        out.append((arr, a2z_rng.choice(arr + [100])))
    out += [([2, 5, 6, 0, 0, 1, 2], 0), ([2, 5, 6, 0, 0, 1, 2], 3), ([1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 1, 1, 1, 1], 13)]
    return out


def a2z_cases_rotated_dups_min():
    return [a2z_rotate(sorted_arr(n, -9, 9)) for n in [1, 3, 6, 15, 50, 200]] + [[2, 2, 2, 0, 1], [1, 3, 3], [10, 1, 10, 10, 10]]


def a2z_cases_rotated_distinct():
    out = []
    for n in [1, 2, 5, 11, 40, 200, 700]:
        out.append(a2z_rotate(sorted(a2z_rng.sample(range(-900, 900), n))))
    return out + [[4, 5, 6, 7, 0, 1, 2], [1, 2, 3, 4, 5]]


def a2z_cases_single():
    out = []
    for pairs in [0, 1, 3, 8, 30, 120, 450]:
        vals = sorted(a2z_rng.sample(range(-800, 800), pairs + 1))
        single = vals[a2z_rng.randrange(len(vals))]
        arr = []
        for v in vals:
            arr += [v] if v == single else [v, v]
        out.append(arr)
    return out + [[1, 1, 2, 3, 3, 4, 4, 8, 8], [3, 3, 7, 7, 10, 11, 11]]


def a2z_cases_peak():
    out = []
    for n in [1, 2, 3, 6, 15, 60, 300]:
        vals = sorted(a2z_rng.sample(range(-900, 900), n))
        peak = a2z_rng.randrange(n)
        left = vals[:peak]
        right = vals[peak + 1:]
        arr = left + [vals[peak]] + right[::-1] if False else None
        top = vals[-1]
        rest = vals[:-1]
        cut = a2z_rng.randrange(len(rest) + 1)
        arr = rest[:cut] + [top] + sorted(rest[cut:], reverse=True)
        out.append(arr)
    return out


def a2z_cases_nth_root():
    out = []
    for n, x in [(3, 27), (4, 69), (2, 144), (5, 32), (1, 17), (10, 1024), (3, 1000), (2, 10 ** 9 // 7)]:
        out.append((n, x if n != 4 else 69))
    for n in [2, 3, 4, 5, 6, 7]:
        r = a2z_rng.randint(2, int(1e9 ** (1.0 / n)))
        out.append((n, r ** n))
    return out


def a2z_cases_bouquets():
    out = []
    for n in [3, 7, 15, 40, 150]:
        bloom = a2z_arr(n, 1, 60)
        k = a2z_rng.randint(1, max(1, n // 3))
        out.append((bloom, a2z_rng.randint(1, max(1, n // k)), k))
    return out + [([1, 10, 3, 10, 2], 3, 1), ([1, 10, 3, 10, 2], 3, 2), ([7, 7, 7, 7, 12, 7, 7], 2, 3), ([5], 1, 1), ([2, 3], 5, 1)]


def a2z_cases_divisor():
    out = []
    for n in [2, 5, 12, 40, 200, 600]:
        arr = a2z_arr(n, 1, 500)
        out.append((arr, a2z_rng.randint(n, sum(arr))))
    return out + [([1, 2, 5, 9], 6), ([44, 22, 33, 11, 1], 5), ([19], 5)]


def a2z_cases_cows():
    out = []
    for n in [2, 3, 6, 15, 60, 250]:
        stalls = a2z_rng.sample(range(1, 2000), n)
        out.append((stalls, a2z_rng.randint(2, n)))
    return out + [([0, 3, 4, 7, 10, 9], 4), ([4, 2, 1, 3, 6], 2), ([1, 2], 2)]


def a2z_cases_kth_two():
    out = []
    for n, m in [(1, 1), (3, 4), (6, 2), (20, 30), (100, 80), (300, 250)]:
        a, b = sorted_arr(n, -300, 300), sorted_arr(m, -300, 300)
        out.append((a, b, a2z_rng.randint(1, n + m)))
    return out + [([2, 3, 6, 7, 9], [1, 4, 8, 10], 5), ([100, 112, 256, 349, 770], [72, 86, 113, 119, 265, 445, 892], 7)]


def a2z_cases_row_ones():
    out = []
    for r, c in [(1, 1), (2, 3), (4, 4), (8, 6), (20, 15), (60, 30)]:
        mat = [[0] * (c - k) + [1] * k for k in (a2z_rng.randint(0, c) for _ in range(r))]
        out.append(mat)
    return out + [[[0, 0, 0], [0, 0, 0]], [[0, 1, 1, 1], [0, 0, 1, 1], [1, 1, 1, 1], [0, 0, 0, 0]]]


def a2z_sorted_matrix(r, c):
    m = [[0] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            up = m[i - 1][j] if i else 0
            left = m[i][j - 1] if j else 0
            m[i][j] = max(up, left) + a2z_rng.randint(1, 4)
    return m


def a2z_cases_matrix_ii():
    out = []
    for r, c in [(1, 1), (2, 3), (4, 4), (8, 6), (20, 25), (40, 30)]:
        mat = a2z_sorted_matrix(r, c)
        flat = [v for row in mat for v in row]
        out.append((mat, a2z_rng.choice(flat) if a2z_rng.random() < 0.6 else a2z_rng.randint(0, max(flat) + 3)))
    return out


def a2z_cases_kth_missing():
    out = []
    for n in [1, 3, 7, 20, 100, 400]:
        arr = sorted(a2z_rng.sample(range(1, 3 * n + 8), n))
        out.append((arr, a2z_rng.randint(1, 3 * n)))
    return out + [([2, 3, 4, 7, 11], 5), ([1, 2, 3, 4], 2)]


def a2z_cases_matrix_median():
    out = []
    for r, c in [(1, 1), (3, 3), (3, 5), (5, 5), (7, 9), (15, 21), (25, 25)]:
        out.append([sorted_arr(c, -200, 200) for _ in range(r)])
    return out


A2Z_BATCH_2 = [
    mk("lower-bound", "Lower Bound", "EASY", ["array", "binary-search"], [("nums", "int[]"), ("x", "int")], "int",
       bs_lower_bound, a2z_cases_search_x(),
       "`nums` is sorted in non-decreasing order. Return the index of the first element that is greater than or equal "
       "to `x`, or `n` if there is none.", "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `x`.", "The index.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i], x <= 10^4`"]),
    mk("upper-bound", "Upper Bound", "EASY", ["array", "binary-search"], [("nums", "int[]"), ("x", "int")], "int",
       bs_upper_bound, a2z_cases_search_x(),
       "`nums` is sorted in non-decreasing order. Return the index of the first element that is strictly greater than "
       "`x`, or `n` if there is none.", "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `x`.", "The index.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i], x <= 10^4`"]),
    mk("floor-and-ceil-in-sorted-array", "Floor and Ceil in a Sorted Array", "EASY", ["array", "binary-search"],
       [("nums", "int[]"), ("x", "int")], "int[]", bs_floor_ceil, a2z_cases_search_x(0, 80),
       "`nums` is sorted. The floor of `x` is the largest element `<= x` and the ceil is the smallest element `>= x`. "
       "Return `[floor, ceil]`, using `-1` for a value that does not exist.",
       "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `x`.", "Two integers: the floor, then the ceil.",
       ["`1 <= n <= 1000`", "`0 <= nums[i], x <= 10^4`"]),
    mk("count-occurrences-in-sorted-array", "Count Occurrences in a Sorted Array", "EASY", ["array", "binary-search"],
       [("nums", "int[]"), ("x", "int")], "int", bs_count, a2z_cases_search_x(-8, 8),
       "`nums` is sorted. Return how many times `x` appears, in `O(log n)` time.",
       "Line 1: `n`.\nLine 2: `n` sorted integers.\nLine 3: `x`.", "The count.", ["`1 <= n <= 1000`", "`-10^4 <= nums[i], x <= 10^4`"]),
    mk("search-in-rotated-sorted-array-ii", "Search in Rotated Sorted Array II", "MEDIUM", ["array", "binary-search"],
       [("nums", "int[]"), ("target", "int")], "bool", bs_rotated_contains, a2z_cases_rotated_dups(),
       "`nums` was sorted in non-decreasing order and then rotated at an unknown pivot. It may contain **duplicates**. "
       "Return `true` if `target` is in `nums`.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.", "`true` or `false`.",
       ["`1 <= n <= 1000`", "`-10^4 <= nums[i], target <= 10^4`"]),
    mk("find-minimum-in-rotated-sorted-array-ii", "Find Minimum in Rotated Sorted Array II", "HARD", ["array", "binary-search"],
       [("nums", "int[]")], "int", bs_rotated_min, a2z_cases_rotated_dups_min(),
       "`nums` was sorted in non-decreasing order and then rotated. It may contain **duplicates**. Return its minimum "
       "element.", ARR_IN, "The minimum element.", ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("rotation-count-in-rotated-sorted-array", "How Many Times Is the Array Rotated", "MEDIUM", ["array", "binary-search"],
       [("nums", "int[]")], "int", bs_rotation_count, a2z_cases_rotated_distinct(),
       "`nums` holds distinct values; it was sorted in ascending order and then rotated to the right some number of "
       "times. Return that number of rotations (the index of the smallest element).", ARR_IN, "The rotation count.",
       ["`1 <= n <= 1000`", "All values are distinct"]),
    mk("single-element-in-a-sorted-array", "Single Element in a Sorted Array", "MEDIUM", ["array", "binary-search"],
       [("nums", "int[]")], "int", bs_single, a2z_cases_single(),
       "`nums` is sorted and every element appears exactly twice except one. Return the single element in `O(log n)` "
       "time.", ARR_IN, "The element that appears once.", ["`1 <= n <= 999`, `n` is odd"]),
    mk("find-peak-element", "Find Peak Element", "MEDIUM", ["array", "binary-search"], [("nums", "int[]")], "int",
       bs_peak_index, a2z_cases_peak(),
       "A peak is an element strictly greater than its neighbours (the ends count as having `-infinity` outside). "
       "Return the index of a peak in `O(log n)` time. In the test data the array rises and then falls, so exactly "
       "one peak exists.", ARR_IN, "The index of the peak.", ["`1 <= n <= 1000`", "Adjacent values are different"]),
    mk("nth-root-of-an-integer", "Nth Root of an Integer", "MEDIUM", ["math", "binary-search"],
       [("n", "int"), ("m", "int")], "int", bs_nth_root, a2z_cases_nth_root(),
       "Return the integer `x` with `x^n == m`, or `-1` if `m` is not a perfect `n`-th power.",
       "Line 1: `n`.\nLine 2: `m`.", "The root, or `-1`.", ["`1 <= n <= 30`", "`1 <= m <= 10^9`"]),
    mk("minimum-days-to-make-m-bouquets", "Minimum Number of Days to Make m Bouquets", "MEDIUM", ["array", "binary-search"],
       [("bloomDay", "int[]"), ("m", "int"), ("k", "int")], "int", bs_bouquets, a2z_cases_bouquets(),
       "`bloomDay[i]` is the day the `i`-th flower blooms. A bouquet needs `k` **adjacent** bloomed flowers. Return the "
       "minimum number of days to make `m` bouquets, or `-1` if it is impossible.",
       "Line 1: `n`.\nLine 2: `n` integers (`bloomDay`).\nLine 3: `m`.\nLine 4: `k`.", "The number of days, or `-1`.",
       ["`1 <= n <= 1000`", "`1 <= bloomDay[i] <= 10^9`", "`1 <= m, k`"]),
    mk("smallest-divisor-given-a-threshold", "Find the Smallest Divisor Given a Threshold", "MEDIUM", ["array", "binary-search"],
       [("nums", "int[]"), ("threshold", "int")], "int", bs_smallest_divisor, a2z_cases_divisor(),
       "Choose a positive divisor `d`; the result is the sum of `ceil(nums[i] / d)`. Return the smallest `d` for which "
       "that sum is at most `threshold`.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `threshold`.", "The smallest divisor.",
       ["`1 <= n <= 1000`", "`1 <= nums[i] <= 10^6`", "`n <= threshold <= 10^6`"]),
    mk("aggressive-cows", "Aggressive Cows", "HARD", ["array", "binary-search", "sorting"], [("stalls", "int[]"), ("cows", "int")], "int",
       bs_aggressive_cows, a2z_cases_cows(),
       "Place `cows` cows in the stalls (given by their positions, unsorted) so that the **minimum distance** between any "
       "two cows is as large as possible. Return that largest minimum distance.",
       "Line 1: `n`.\nLine 2: `n` stall positions.\nLine 3: `cows`.", "The largest possible minimum distance.",
       ["`2 <= cows <= n <= 1000`", "`0 <= stalls[i] <= 10^9`, all different"]),
    mk("kth-element-of-two-sorted-arrays", "K-th Element of Two Sorted Arrays", "HARD", ["array", "binary-search"],
       [("a", "int[]"), ("b", "int[]"), ("k", "int")], "int", bs_kth_two, a2z_cases_kth_two(),
       "Both arrays are sorted. Return the `k`-th smallest element (1-indexed) of the merged order, in "
       "`O(log(min(n, m)))` time.", "Line 1: `n`.\nLine 2: `n` integers (`a`).\nLine 3: `m`.\nLine 4: `m` integers (`b`).\nLine 5: `k`.",
       "The k-th element.", ["`1 <= n, m <= 1000`", "`1 <= k <= n + m`"]),
    mk("row-with-maximum-ones", "Row with Maximum Number of 1s", "EASY", ["matrix", "binary-search"],
       [("matrix", "int[][]")], "int", bs_row_max_ones, a2z_cases_row_ones(),
       "Every row of the binary matrix is sorted (zeros first, then ones). Return the index of the row with the most 1s "
       "(the smallest index on ties).", "Line 1: `r`.\nLines 2..: each row, space separated.", "The row index.",
       ["`1 <= r, c <= 100`", "Every row is sorted in non-decreasing order"]),
    mk("search-a-2d-matrix-ii", "Search a 2D Matrix II", "MEDIUM", ["matrix", "binary-search"],
       [("matrix", "int[][]"), ("target", "int")], "bool", bs_matrix_contains, a2z_cases_matrix_ii(),
       "Every row is sorted left to right and every column is sorted top to bottom. Return `true` if `target` is in the "
       "matrix, using the staircase walk in `O(r + c)`.", "Line 1: `r`.\nNext `r` lines: the rows.\nLast line: `target`.",
       "`true` or `false`.", ["`1 <= r, c <= 100`", "Rows and columns are sorted"]),
    mk("kth-missing-positive-number", "Kth Missing Positive Number", "EASY", ["array", "binary-search"],
       [("arr", "int[]"), ("k", "int")], "int", bs_kth_missing, a2z_cases_kth_missing(),
       "`arr` is strictly increasing and holds positive integers. Return the `k`-th positive integer that is missing "
       "from it.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The k-th missing positive integer.",
       ["`1 <= n <= 1000`", "`1 <= arr[i] <= 10^4`", "`1 <= k <= 1000`"]),
    mk("median-in-a-row-wise-sorted-matrix", "Median in a Row-Wise Sorted Matrix", "HARD", ["matrix", "binary-search"],
       [("matrix", "int[][]")], "int", bs_matrix_median, a2z_cases_matrix_median(),
       "Every row is sorted in non-decreasing order and `r * c` is odd. Return the median of all the elements without "
       "flattening and sorting the matrix.", "Line 1: `r`.\nNext `r` lines: the rows.", "The median.",
       ["`1 <= r, c <= 100`, `r * c` is odd", "`-10^4 <= matrix[i][j] <= 10^4`"]),
]
PROBLEMS += A2Z_BATCH_2


# ============================================================== Striver A2Z sheet, batch 3 (recursion and backtracking)
def bt_subsets(nums):
    out = []
    for mask in range(1 << len(nums)):
        out.append([nums[i] for i in range(len(nums)) if mask >> i & 1])
    return out


def bt_subsets_unique(nums):
    return [list(t) for t in sorted({tuple(sorted(sub)) for sub in bt_subsets(nums)})]


def bt_combination_sum_ii(candidates, target):
    found = set()

    def go(i, left, cur):
        if left == 0:
            found.add(tuple(cur))
            return
        if i == len(cands) or left < 0:
            return
        go(i + 1, left - cands[i], cur + [cands[i]])
        go(i + 1, left, cur)

    cands = sorted(candidates)
    go(0, target, [])
    return [list(t) for t in found]


def bt_combination_sum_iii(k, n):
    import itertools
    return [list(c) for c in itertools.combinations(range(1, 10), k) if sum(c) == n]


def bt_permutations(nums):
    import itertools
    return [list(p) for p in itertools.permutations(nums)]


def bt_phone(digits):
    import itertools
    letters = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    return ["".join(p) for p in itertools.product(*(letters[d] for d in digits))]


def bt_subset_sums(nums):
    return sorted(sum(sub) for sub in bt_subsets(nums))


def bt_kth_permutation(n, k):
    import itertools
    return "".join(map(str, list(itertools.permutations(range(1, n + 1)))[k - 1]))


def bt_rat_in_maze(maze):
    n = len(maze)
    out = []
    if maze[0][0] == 0 or maze[n - 1][n - 1] == 0:
        return out
    moves = (("D", 1, 0), ("L", 0, -1), ("R", 0, 1), ("U", -1, 0))

    def go(r, c, path, seen):
        if (r, c) == (n - 1, n - 1):
            out.append(path)
            return
        for name, dr, dc in moves:
            a, b = r + dr, c + dc
            if 0 <= a < n and 0 <= b < n and maze[a][b] == 1 and (a, b) not in seen:
                seen.add((a, b))
                go(a, b, path + name, seen)
                seen.discard((a, b))

    go(0, 0, "", {(0, 0)})
    return out


def bt_m_coloring(graph, m):
    n = len(graph)
    colors = [0] * n

    def go(v):
        if v == n:
            return True
        for c in range(1, m + 1):
            if all(not (graph[v][u] and colors[u] == c) for u in range(v)):
                colors[v] = c
                if go(v + 1):
                    return True
                colors[v] = 0
        return False

    return go(0)


def bt_binary_no_adjacent(n):
    import itertools
    return ["".join(b) for b in itertools.product("01", repeat=n) if "11" not in "".join(b)]


def bt_count_subsequences(nums, k):
    return sum(1 for sub in bt_subsets(nums) if sum(sub) == k)


def bt_subsequences_with_sum(nums, k):
    return [sub for sub in bt_subsets(nums) if sum(sub) == k]


def a2z_cases_small_arrays(sizes, lo, hi, distinct=False):
    out = []
    for n in sizes:
        out.append(a2z_rng.sample(range(lo, hi + 1), n) if distinct else a2z_arr(n, lo, hi))
    return out


def a2z_cases_comb_ii():
    out = []
    for n in [3, 5, 8, 11, 14]:
        cands = a2z_arr(n, 1, 8)
        out.append((cands, a2z_rng.randint(4, 14)))
    return out + [([10, 1, 2, 7, 6, 1, 5], 8), ([2, 5, 2, 1, 2], 5)]


def a2z_cases_phone():
    return ["23", "2", "7", "79", "234", "2379", "9999", "5678"]


def a2z_cases_maze():
    out = [[[1, 0, 0, 0], [1, 1, 0, 1], [1, 1, 0, 0], [0, 1, 1, 1]], [[1, 0], [1, 0]], [[1]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]]]
    for n in [4, 5, 6]:
        maze = [[1 if a2z_rng.random() < 0.72 else 0 for _ in range(n)] for _ in range(n)]
        maze[0][0] = maze[n - 1][n - 1] = 1
        out.append(maze)
    return out


def a2z_cases_coloring():
    out = []
    for n, p, m in [(4, 0.6, 3), (5, 0.7, 3), (6, 0.6, 2), (7, 0.55, 3), (8, 0.5, 3), (6, 0.9, 3), (3, 1.0, 2)]:
        g = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if a2z_rng.random() < p:
                    g[i][j] = g[j][i] = 1
        out.append((g, m))
    return out


A2Z_BATCH_3 = [
    mk("subsets", "Subsets", "MEDIUM", ["array", "backtracking"], [("nums", "int[]")], "sets", bt_subsets,
       a2z_cases_small_arrays([1, 2, 3, 4, 6, 8, 10], -9, 9, True),
       "`nums` holds distinct integers. Return all possible subsets (the power set), including the empty one, in any order.",
       ARR_IN, "One subset per line, numbers separated by spaces (an empty line for the empty subset). The starter code sorts "
       "the lines, so any order is accepted.", ["`1 <= n <= 10`", "All values are distinct"]),
    mk("subsets-ii", "Subsets II", "MEDIUM", ["array", "backtracking"], [("nums", "int[]")], "sets", bt_subsets_unique,
       a2z_cases_small_arrays([1, 2, 4, 6, 8, 10], 1, 4),
       "`nums` may contain duplicates. Return all **unique** subsets, in any order.", ARR_IN,
       "One subset per line (an empty line for the empty subset); order does not matter.", ["`1 <= n <= 10`", "`-10 <= nums[i] <= 10`"]),
    mk("combination-sum-ii", "Combination Sum II", "MEDIUM", ["array", "backtracking"],
       [("candidates", "int[]"), ("target", "int")], "sets", bt_combination_sum_ii, a2z_cases_comb_ii(),
       "Each number in `candidates` may be used **at most once**, and `candidates` may contain duplicates. Return all unique "
       "combinations that sum to `target`, in any order.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.",
       "One combination per line; order does not matter.", ["`1 <= n <= 14`", "`1 <= candidates[i] <= 8`", "`1 <= target <= 14`"]),
    mk("combination-sum-iii", "Combination Sum III", "MEDIUM", ["backtracking"], [("k", "int"), ("n", "int")], "sets",
       bt_combination_sum_iii, [(3, 7), (3, 9), (4, 1), (2, 18), (4, 24), (5, 25), (6, 30), (9, 45), (2, 5)],
       "Find all valid combinations of exactly `k` different numbers from `1` to `9` (each used at most once) that add up "
       "to `n`. Return them in any order.", "Line 1: `k`.\nLine 2: `n`.", "One combination per line; order does not matter.",
       ["`2 <= k <= 9`", "`1 <= n <= 60`"]),
    mk("permutations", "Permutations", "MEDIUM", ["array", "backtracking"], [("nums", "int[]")], "rows", bt_permutations,
       a2z_cases_small_arrays([1, 2, 3, 4, 5, 6, 7], -9, 9, True),
       "`nums` holds distinct integers. Return all permutations, in any order.", ARR_IN,
       "One permutation per line; the starter code sorts the lines.", ["`1 <= n <= 7`", "All values are distinct"]),
    mk("letter-combinations-of-a-phone-number", "Letter Combinations of a Phone Number", "MEDIUM", ["string", "backtracking"],
       [("digits", "str")], "strs", bt_phone, a2z_cases_phone(),
       "Digits `2`-`9` map to letters as on a phone keypad (2 = abc, 3 = def, 4 = ghi, 5 = jkl, 6 = mno, 7 = pqrs, 8 = tuv, "
       "9 = wxyz). Return all letter combinations the digit string could spell, in any order.", "A line with the digit string.",
       "One combination per line; order does not matter.", ["`1 <= digits.length <= 4`", "Each digit is `2`-`9`"]),
    mk("subset-sums", "Subset Sums", "MEDIUM", ["array", "backtracking"], [("nums", "int[]")], "int[]", bt_subset_sums,
       a2z_cases_small_arrays([1, 2, 3, 5, 8, 12, 15], 0, 9),
       "Return the sum of every subset of `nums` (including the empty subset, whose sum is `0`), sorted in ascending order.",
       ARR_IN, "The sums in ascending order, one entry per subset (duplicates are kept).", ["`1 <= n <= 15`", "`0 <= nums[i] <= 100`"]),
    mk("permutation-sequence", "Permutation Sequence", "HARD", ["math", "recursion"], [("n", "int"), ("k", "int")], "str",
       bt_kth_permutation, [(3, 3), (4, 9), (3, 1), (1, 1), (5, 120), (6, 400), (7, 2500), (8, 40320), (9, 123456)],
       "The numbers `1..n` have `n!` permutations. List them in lexicographic order and return the `k`-th one as a string, "
       "without generating all of them.", "Line 1: `n`.\nLine 2: `k`.", "The k-th permutation as a string.",
       ["`1 <= n <= 9`", "`1 <= k <= n!`"]),
    mk("rat-in-a-maze", "Rat in a Maze", "MEDIUM", ["matrix", "backtracking"], [("maze", "int[][]")], "strs", bt_rat_in_maze,
       a2z_cases_maze(),
       "A rat starts at the top-left cell of an `n x n` maze and wants to reach the bottom-right cell. A cell with `1` is open "
       "and `0` is blocked. The rat moves `D`, `L`, `R` or `U` and may not visit a cell twice on one path. Return every path "
       "as a string of moves.", "Line 1: `n`.\nNext `n` lines: the maze rows.",
       "One path per line, nothing if there is no path; the starter code sorts the lines.", ["`1 <= n <= 6`"]),
    mk("m-coloring-problem", "M-Coloring Problem", "HARD", ["graph", "backtracking"], [("graph", "int[][]"), ("m", "int")], "bool",
       bt_m_coloring, a2z_cases_coloring(),
       "Given an undirected graph as an adjacency matrix and `m` colours, return `true` if its vertices can be coloured so that "
       "no two adjacent vertices share a colour.", "Line 1: `n`.\nNext `n` lines: the adjacency matrix rows.\nLast line: `m`.",
       "`true` or `false`.", ["`1 <= n <= 8`", "`1 <= m <= n`"]),
    mk("binary-strings-without-adjacent-ones", "Generate Binary Strings Without Adjacent Ones", "EASY", ["string", "backtracking"],
       [("n", "int")], "strs", bt_binary_no_adjacent, [1, 2, 3, 4, 5, 6, 8, 10],
       "Return all binary strings of length `n` that do not contain two consecutive `1`s, in any order.", N_IN,
       "One string per line; order does not matter.", ["`1 <= n <= 10`"]),
    mk("count-subsequences-with-sum-k", "Count Subsequences with Sum K", "MEDIUM", ["array", "dynamic-programming", "backtracking"],
       [("nums", "int[]"), ("k", "int")], "int", bt_count_subsequences,
       [(a2z_arr(n, 1, 9), a2z_rng.randint(3, 25)) for n in [3, 5, 8, 12, 16, 20]] + [([1, 2, 3], 3), ([2, 2, 2], 4)],
       "Return how many subsequences of `nums` (chosen by index, so equal values at different positions count separately) have "
       "a sum equal to `k`.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "The number of subsequences.",
       ["`1 <= n <= 20`", "`1 <= nums[i] <= 100`", "`1 <= k <= 1000`"]),
    mk("subsequences-with-sum-k", "Print Subsequences with Sum K", "MEDIUM", ["array", "backtracking"],
       [("nums", "int[]"), ("k", "int")], "rows", bt_subsequences_with_sum,
       [(a2z_arr(n, 1, 6), a2z_rng.randint(3, 12)) for n in [3, 5, 7, 9, 11]] + [([1, 2, 3], 3), ([2, 2, 2], 4)],
       "Return every subsequence of `nums` (keeping the original order of its elements, chosen by index) whose sum is `k`, in "
       "any order.", "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `k`.", "One subsequence per line; the starter code sorts the lines.",
       ["`1 <= n <= 11`", "`1 <= nums[i] <= 20`", "`1 <= k <= 100`"]),
]
PROBLEMS += A2Z_BATCH_3


# ============================================================== Striver A2Z sheet, batch 4 (maths basics, sorting, strings)
def m_count_digits(n):
    return len(str(n))


def m_gcd(a, b):
    return math.gcd(a, b)


def m_armstrong(n):
    d = str(n)
    return sum(int(c) ** len(d) for c in d) == n


def m_divisors(n):
    return sorted(d for d in range(1, n + 1) if n % d == 0)


def m_is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def m_sort(nums):
    return sorted(nums)


def st_remove_outer(s):
    out, depth = [], 0
    for ch in s:
        if ch == ")":
            depth -= 1
        if depth > 0:
            out.append(ch)
        if ch == "(":
            depth += 1
    return "".join(out)


def st_reverse_words(s):
    return " ".join(reversed(s.split()))


def st_largest_odd(s):
    for i in range(len(s) - 1, -1, -1):
        if int(s[i]) % 2:
            return s[:i + 1]
    return ""


def st_common_prefix(strs):
    prefix = strs[0]
    for w in strs[1:]:
        while not w.startswith(prefix):
            prefix = prefix[:-1]
    return prefix


def st_rotate(s, goal):
    return len(s) == len(goal) and goal in s + s


def st_max_depth(s):
    best = depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            best = max(best, depth)
        elif ch == ")":
            depth -= 1
    return best


def st_atoi(s):
    i, n = 0, len(s)
    while i < n and s[i] == " ":
        i += 1
    sign = 1
    if i < n and s[i] in "+-":
        sign = -1 if s[i] == "-" else 1
        i += 1
    value = 0
    while i < n and s[i].isdigit():
        value = value * 10 + int(s[i])
        i += 1
    return max(-2 ** 31, min(2 ** 31 - 1, sign * value))


def st_count_and_say(n):
    s = "1"
    for _ in range(n - 1):
        out, i = [], 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            out.append(str(j - i) + s[i])
            i = j
        s = "".join(out)
    return s


def st_strstr(haystack, needle):
    return haystack.find(needle)


def st_beauty(s):
    total = 0
    for i in range(len(s)):
        count = collections.Counter()
        for j in range(i, len(s)):
            count[s[j]] += 1
            total += max(count.values()) - min(count.values())
    return total


def a2z_word(n, alphabet="abcdefghijklmnopqrstuvwxyz"):
    return "".join(a2z_rng.choice(alphabet) for _ in range(n))


def a2z_cases_parens():
    out = ["(()())(())", "(()())(())(()(()))", "()()", "()"]
    for n in [3, 8, 20, 60]:
        s, depth, parts = [], 0, 0
        while parts < n:
            if depth == 0 or (a2z_rng.random() < 0.55 and len(s) < 2 * n):
                s.append("(")
                depth += 1
            else:
                s.append(")")
                depth -= 1
                if depth == 0:
                    parts += 1
        out.append("".join(s))
    return out


def a2z_cases_words():
    out = ["the sky is blue", "hello world", "a good   example", "one", "  spaced   out  words here "]
    for n in [3, 6, 12, 30]:
        out.append(" ".join(a2z_word(a2z_rng.randint(1, 8)) for _ in range(n)))
    return out


def a2z_cases_odd():
    out = ["52", "4206", "35427", "2468", "7", "1000", "3000001"]
    for n in [10, 40, 150]:
        out.append("".join(str(a2z_rng.randint(0, 9)) for _ in range(n)).lstrip("0") or "0")
    return out


def a2z_cases_prefix():
    out = [["flower", "flow", "flight"], ["dog", "racecar", "car"], ["a"], ["abc", "abc"], ["ab", "a"]]
    for n in [3, 6, 15, 40]:
        base = a2z_word(a2z_rng.randint(0, 6), "ab")
        out.append([base + a2z_word(a2z_rng.randint(0, 5), "ab") for _ in range(n)])
    return out


def a2z_cases_rotate():
    out = [("abcde", "cdeab"), ("abcde", "abced"), ("a", "a"), ("ab", "ba"), ("aa", "a")]
    for n in [4, 9, 25, 80]:
        s = a2z_word(n, "ab")
        r = a2z_rng.randrange(n)
        out.append((s, s[r:] + s[:r]))
        out.append((s, a2z_word(n, "ab")))
    return out


def a2z_cases_atoi():
    return ["42", "-42", "4193 with words", "words and 987", "+1", "-91283472332", "91283472332", "0", "00000-42a1234", "2147483647",
            "-2147483648", "3.14159", "+-12", "12345678901234567890"]


def a2z_cases_strstr():
    out = [("sadbutsad", "sad"), ("leetcode", "leeto"), ("a", "a"), ("aaaaa", "bba"), ("mississippi", "issip"), ("abc", "c")]
    for n in [20, 80, 300]:
        h = a2z_word(n, "ab")
        i = a2z_rng.randrange(n - 3)
        out.append((h, h[i:i + a2z_rng.randint(1, 3)] if a2z_rng.random() < 0.7 else a2z_word(4, "ab")))
    return out


A2Z_BATCH_4 = [
    mk("count-digits", "Count Digits", "EASY", ["math"], [("n", "int")], "int", m_count_digits,
       [1, 7, 10, 99, 100, 12345, 999999999, 1000000000, 4800, 20],
       "Return the number of digits of the positive integer `n`.", N_IN, "The number of digits.", ["`1 <= n <= 10^9`"]),
    mk("gcd-of-two-numbers", "GCD of Two Numbers", "EASY", ["math"], [("a", "int"), ("b", "int")], "int", m_gcd,
       [(12, 18), (7, 13), (100, 75), (1, 1), (48, 36), (1000000000, 250000000), (17, 17), (999999937, 2), (54, 24), (270, 192)],
       "Return the greatest common divisor of `a` and `b`.", "Line 1: `a`.\nLine 2: `b`.", "The GCD.", ["`1 <= a, b <= 10^9`"]),
    mk("armstrong-number", "Armstrong Number", "EASY", ["math"], [("n", "int")], "bool", m_armstrong,
       [153, 371, 9474, 123, 1, 10, 9926315, 548834, 1634, 8208, 100, 407],
       "An Armstrong number equals the sum of its digits, each raised to the power of the number of digits (153 = 1³ + 5³ + 3³). "
       "Return `true` if `n` is an Armstrong number.", N_IN, "`true` or `false`.", ["`1 <= n <= 10^9`"]),
    mk("divisors-of-a-number", "Print All Divisors of a Number", "EASY", ["math"], [("n", "int")], "int[]", m_divisors,
       [1, 2, 12, 36, 97, 100, 360, 5040, 99991, 1000000, 735134400 // 1000],
       "Return all positive divisors of `n` in ascending order, checking candidates only up to `sqrt(n)`.", N_IN,
       "The divisors in ascending order.", ["`1 <= n <= 10^6`"]),
    mk("check-prime-number", "Check Prime", "EASY", ["math"], [("n", "int")], "bool", m_is_prime,
       [1, 2, 3, 4, 17, 25, 97, 7919, 1000000007, 999999937, 1000000000, 561],
       "Return `true` if `n` is a prime number, in `O(sqrt(n))` time.", N_IN, "`true` or `false`.", ["`1 <= n <= 10^9`"]),
    mk("sort-an-array", "Sort an Array", "MEDIUM", ["array", "sorting", "divide-and-conquer"], [("nums", "int[]")], "int[]", m_sort,
       [a2z_arr(n, -9999, 9999) for n in [1, 2, 7, 30, 200, 1000, 3000]] + [[5, 2, 3, 1], [5, 1, 1, 2, 0, 0]],
       "Sort `nums` in ascending order in `O(n log n)` time (for example with merge sort), without a built-in sort.", ARR_IN,
       "The sorted array.", ["`1 <= n <= 5000`", "`-10^4 <= nums[i] <= 10^4`"]),
    mk("remove-outermost-parentheses", "Remove Outermost Parentheses", "EASY", ["string", "stack"], [("s", "str")], "str", st_remove_outer,
       a2z_cases_parens(),
       "`s` is a valid parentheses string. Split it into primitive valid parts and remove the outermost pair of each part. "
       "Return the result.", "A line with the string `s`.", "The resulting string (possibly empty).", ["`1 <= s.length <= 100000`", "`s` is a valid parentheses string"]),
    mk("reverse-words-in-a-string", "Reverse Words in a String", "MEDIUM", ["string", "two-pointers"], [("s", "str")], "str", st_reverse_words,
       a2z_cases_words(),
       "Reverse the order of the words in `s`. Words are separated by spaces; the result must have a single space between "
       "words and no leading or trailing spaces.", "A line with the string `s`.", "The words in reverse order.",
       ["`1 <= s.length <= 10000`", "`s` contains at least one word"]),
    mk("largest-odd-number-in-a-string", "Largest Odd Number in String", "EASY", ["string", "math"], [("num", "str")], "str", st_largest_odd,
       a2z_cases_odd(),
       "`num` is a string of digits. Return the largest-valued odd number that is a **substring** of `num`, or an empty string if "
       "there is none.", "A line with the digit string.", "The odd number as a string, or an empty line.", ["`1 <= num.length <= 100000`"]),
    mk("longest-common-prefix", "Longest Common Prefix", "EASY", ["string"], [("strs", "strs")], "str", st_common_prefix, a2z_cases_prefix(),
       "Return the longest common prefix of all the strings, or an empty string if there is none.",
       "Line 1: `n`.\nNext `n` lines: the strings.", "The common prefix (possibly an empty line).",
       ["`1 <= n <= 200`", "`0 <= strs[i].length <= 200`", "Lowercase letters"]),
    mk("rotate-string", "Rotate String", "EASY", ["string"], [("s", "str"), ("goal", "str")], "bool", st_rotate, a2z_cases_rotate(),
       "A shift moves the first character of `s` to the end. Return `true` if `s` can become `goal` after some number of shifts.",
       "Line 1: `s`.\nLine 2: `goal`.", "`true` or `false`.", ["`1 <= s.length, goal.length <= 100`"]),
    mk("maximum-nesting-depth-of-the-parentheses", "Maximum Nesting Depth of the Parentheses", "EASY", ["string", "stack"], [("s", "str")], "int",
       st_max_depth, ["(1+(2*3)+((8)/4))+1", "(1)+((2))+(((3)))", "()(())", "1", "((((()))))", "(a)(b(c)(d(e)))"] + [a2z_cases_parens()[i] for i in (4, 6)],
       "Return the maximum nesting depth of the parentheses in `s`, where the depth of `(1+(2*3))` is 2.", "A line with the string `s`.",
       "The maximum depth.", ["`1 <= s.length <= 100`", "`s` has valid parentheses"]),
    mk("string-to-integer-atoi", "String to Integer (atoi)", "MEDIUM", ["string", "math"], [("s", "str")], "int", st_atoi, a2z_cases_atoi(),
       "Implement `atoi`: skip leading spaces, read an optional `+` or `-`, then read digits until a non-digit. Clamp the result to the "
       "32-bit signed range `[-2^31, 2^31 - 1]`. Return `0` if no digits were read.", "A line with the string `s`.", "The integer.",
       ["`0 <= s.length <= 200`"]),
    mk("count-and-say", "Count and Say", "MEDIUM", ["string"], [("n", "int")], "str", st_count_and_say, [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
       "`countAndSay(1)` is `\"1\"`; each next term describes the previous one by counting runs of equal digits (`\"3322251\"` is read "
       "as two 3s, three 2s, one 5, one 1 and says `\"23321511\"`). Return the `n`-th term.", N_IN, "The `n`-th term.", ["`1 <= n <= 30`"]),
    mk("find-the-index-of-the-first-occurrence-in-a-string", "Find the Index of the First Occurrence in a String", "EASY", ["string", "two-pointers"],
       [("haystack", "str"), ("needle", "str")], "int", st_strstr, a2z_cases_strstr(),
       "Return the index of the first occurrence of `needle` in `haystack`, or `-1` if it is not part of it. A linear-time KMP "
       "solution is the goal.", "Line 1: `haystack`.\nLine 2: `needle`.", "The index or `-1`.", ["`1 <= haystack.length, needle.length <= 1000`"]),
    mk("sum-of-beauty-of-all-substrings", "Sum of Beauty of All Substrings", "MEDIUM", ["string", "hash-table"], [("s", "str")], "int", st_beauty,
       [a2z_word(n, "abcde") for n in [3, 6, 15, 40, 120, 300]] + ["aabcb", "aabcbaa"],
       "The beauty of a string is the difference between the highest and the lowest frequency among the characters that appear in "
       "it. Return the sum of the beauty of all substrings of `s`.", "A line with the string `s`.", "The sum.",
       ["`1 <= s.length <= 500`", "Lowercase letters"]),
]
PROBLEMS += A2Z_BATCH_4

from sde_batch3 import make_batch  # noqa: E402  (greedy, stack, string and recursion problems)
SDE_EXTRA = make_batch(mk, a2z_rng)
PROBLEMS += SDE_EXTRA

from sde_batch4 import make_batch as make_batch_4  # noqa: E402  (real Striver SDE problems the app was still missing)
_have4 = {p["slug"] for p in PROBLEMS}
SDE_BATCH_4 = [p for p in make_batch_4(mk, a2z_rng, dict(TN=TN, tok2tree=tok2tree, tree2tok=tree2tok, rand_tree=rand_tree, TREE_IN=TREE_IN, TREE_OUT=TREE_OUT)) if p["slug"] not in _have4]
PROBLEMS += SDE_BATCH_4

from sde_batch5 import make_batch as make_batch_5  # noqa: E402  (3Sum/4Sum, core graph algorithms and BST problems)
_have5 = {p["slug"] for p in PROBLEMS}
SDE_BATCH_5 = [p for p in make_batch_5(mk, a2z_rng, dict(TN=TN, tok2tree=tok2tree, tree2tok=tree2tok, rand_tree=rand_tree, TREE_IN=TREE_IN, TREE_OUT=TREE_OUT)) if p["slug"] not in _have5]
PROBLEMS += SDE_BATCH_5

from sde_batch6 import make_batch as make_batch_6  # noqa: E402  (classic dynamic-programming problems of the SDE sheet)
_have6 = {p["slug"] for p in PROBLEMS}
SDE_BATCH_6 = [p for p in make_batch_6(mk, a2z_rng) if p["slug"] not in _have6]
PROBLEMS += SDE_BATCH_6

from sde_batch7 import make_batch as make_batch_7  # noqa: E402  (sudoku, combination sum, running median, trie, LRU cache, min stack, more DP)
_have7 = {p["slug"] for p in PROBLEMS}
SDE_BATCH_7 = [p for p in make_batch_7(mk, a2z_rng) if p["slug"] not in _have7]
PROBLEMS += SDE_BATCH_7

from sde_batch8 import make_batch as make_batch_8  # noqa: E402  (LFU, queue/stack/heap designs, trie problems, max XOR, divide integers)
_have8 = {p["slug"] for p in PROBLEMS}
SDE_BATCH_8 = [p for p in make_batch_8(mk, a2z_rng) if p["slug"] not in _have8]
PROBLEMS += SDE_BATCH_8


# Curated sheets: the slugs that belong to each study plan. The tags are added on top of each problem's own tags, so
# regenerating the seed keeps the plans intact (plans.json lists the tag).
STRIVER_SDE = set(['add-two-numbers', 'balanced-binary-tree', 'best-time-to-buy-and-sell-stock', 'binary-tree-inorder-traversal', 'binary-tree-level-order-traversal', 'binary-tree-maximum-path-sum', 'binary-tree-zigzag-level-order-traversal', 'coin-change', 'construct-binary-tree-from-preorder-and-inorder-traversal', 'course-schedule', 'diameter-of-binary-tree', 'edit-distance', 'find-the-duplicate-number', 'is-graph-bipartite', 'kth-largest-element-in-an-array', 'kth-smallest-element-in-a-bst', 'largest-rectangle-in-histogram', 'longest-common-subsequence', 'longest-consecutive-sequence', 'longest-increasing-subsequence', 'longest-substring-without-repeating-characters', 'lowest-common-ancestor-of-a-binary-search-tree', 'lowest-common-ancestor-of-a-binary-tree', 'majority-element', 'maximal-rectangle', 'maximum-depth-of-binary-tree', 'maximum-product-subarray', 'maximum-subarray', 'merge-intervals', 'merge-sorted-array', 'merge-two-sorted-lists', 'middle-of-the-linked-list', 'min-cost-to-connect-all-points', 'network-delay-time', 'next-permutation', 'number-of-islands', 'palindrome-linked-list', 'partition-equal-subset-sum', 'pascals-triangle', 'redundant-connection', 'remove-duplicates-from-sorted-array', 'remove-nth-node-from-end-of-list', 'reverse-linked-list', 'reverse-nodes-in-k-group', 'roman-to-integer', 'rotate-image', 'rotate-list', 'rotting-oranges', 'same-tree', 'search-a-2d-matrix', 'search-in-rotated-sorted-array', 'set-matrix-zeroes', 'sliding-window-maximum', 'sort-colors', 'symmetric-tree', 'top-k-frequent-elements', 'trapping-rain-water', 'two-sum', 'unique-paths', 'valid-parentheses', 'validate-binary-search-tree', 'word-break'])
STRIVER_A2Z = set(['move-zeroes', 'remove-duplicates-from-sorted-array', 'missing-number', 'single-number', 'two-sum', 'sort-colors', 'majority-element', 'maximum-subarray', 'best-time-to-buy-and-sell-stock', 'next-permutation', 'longest-consecutive-sequence', 'set-matrix-zeroes', 'rotate-image', 'spiral-matrix', 'subarray-sum-equals-k', 'pascals-triangle', '3sum-count', '4sum-count', 'merge-intervals', 'merge-sorted-array', 'maximum-product-subarray', 'rotate-array', 'binary-search', 'search-insert-position', 'find-first-and-last-position-of-element-in-sorted-array', 'search-in-rotated-sorted-array', 'find-minimum-in-rotated-sorted-array', 'sqrt-x', 'koko-eating-bananas', 'capacity-to-ship-packages', 'split-array-largest-sum', 'search-a-2d-matrix', 'isomorphic-strings', 'valid-anagram', 'roman-to-integer', 'longest-palindromic-substring-length', 'valid-palindrome', 'palindromic-substrings', 'reverse-linked-list', 'middle-of-the-linked-list', 'merge-two-sorted-lists', 'remove-nth-node-from-end-of-list', 'add-two-numbers', 'odd-even-linked-list', 'palindrome-linked-list', 'sort-list', 'rotate-list', 'reverse-nodes-in-k-group', 'remove-duplicates-from-sorted-list', 'find-the-duplicate-number', 'generate-parentheses-count', 'combination-sum-count', 'n-queens-count', 'word-search', 'palindrome-partitioning-count', 'distinct-permutations-count', 'single-number-ii', 'power-of-two', 'number-of-1-bits', 'count-primes', 'bitwise-and-of-numbers-range', 'valid-parentheses', 'next-greater-element-ii', 'daily-temperatures', 'trapping-rain-water', 'largest-rectangle-in-histogram', 'sum-of-subarray-minimums', 'evaluate-reverse-polish-notation', 'longest-substring-without-repeating-characters', 'longest-repeating-character-replacement', 'minimum-window-substring-length', 'longest-substring-with-at-most-k-distinct-characters', 'sliding-window-maximum', 'kth-largest-element-in-an-array', 'top-k-frequent-elements', 'task-scheduler', 'assign-cookies', 'lemonade-change', 'jump-game', 'jump-game-ii', 'candy', 'non-overlapping-intervals', 'insert-interval', 'meeting-rooms-ii', 'maximum-depth-of-binary-tree', 'balanced-binary-tree', 'diameter-of-binary-tree', 'binary-tree-maximum-path-sum', 'same-tree', 'binary-tree-level-order-traversal', 'binary-tree-zigzag-level-order-traversal', 'symmetric-tree', 'lowest-common-ancestor-of-a-binary-tree', 'binary-tree-inorder-traversal', 'binary-tree-right-side-view', 'construct-binary-tree-from-preorder-and-inorder-traversal', 'count-complete-tree-nodes', 'invert-binary-tree', 'validate-binary-search-tree', 'kth-smallest-element-in-a-bst', 'lowest-common-ancestor-of-a-binary-search-tree', 'number-of-islands', 'rotting-oranges', '01-matrix', 'surrounded-regions', 'number-of-provinces', 'is-graph-bipartite', 'course-schedule', 'network-delay-time', 'cheapest-flights-within-k-stops', 'path-with-minimum-effort', 'redundant-connection', 'min-cost-to-connect-all-points', 'swim-in-rising-water', 'shortest-path-in-binary-matrix', 'number-of-connected-components', 'climbing-stairs', 'house-robber', 'house-robber-ii', 'unique-paths', 'unique-paths-ii', 'minimum-path-sum', 'minimum-falling-path-sum', 'partition-equal-subset-sum', 'coin-change', 'coin-change-ii', 'target-sum', 'longest-increasing-subsequence', 'longest-common-subsequence', 'edit-distance', 'wildcard-matching', 'distinct-subsequences', 'best-time-to-buy-and-sell-stock-ii', 'best-time-to-buy-and-sell-stock-iii', 'best-time-to-buy-and-sell-stock-with-cooldown', 'maximal-rectangle', 'burst-balloons', 'largest-element-in-array', 'second-largest-element', 'check-if-array-is-sorted-and-rotated', 'left-rotate-array-by-one', 'linear-search', 'union-of-two-sorted-arrays', 'max-consecutive-ones', 'rearrange-array-elements-by-sign', 'leaders-in-an-array', 'longest-subarray-with-sum-k', 'find-the-repeating-and-missing-number', 'count-subarrays-with-given-xor', 'count-inversions', 'reverse-pairs', 'majority-element-ii', 'largest-subarray-with-0-sum', 'lower-bound', 'upper-bound', 'floor-and-ceil-in-sorted-array', 'count-occurrences-in-sorted-array', 'search-in-rotated-sorted-array-ii', 'find-minimum-in-rotated-sorted-array-ii', 'rotation-count-in-rotated-sorted-array', 'single-element-in-a-sorted-array', 'find-peak-element', 'nth-root-of-an-integer', 'minimum-days-to-make-m-bouquets', 'smallest-divisor-given-a-threshold', 'aggressive-cows', 'kth-element-of-two-sorted-arrays', 'row-with-maximum-ones', 'search-a-2d-matrix-ii', 'kth-missing-positive-number', 'median-in-a-row-wise-sorted-matrix', 'subsets', 'subsets-ii', 'combination-sum-ii', 'combination-sum-iii', 'permutations', 'letter-combinations-of-a-phone-number', 'subset-sums', 'permutation-sequence', 'rat-in-a-maze', 'm-coloring-problem', 'binary-strings-without-adjacent-ones', 'count-subsequences-with-sum-k', 'subsequences-with-sum-k', 'count-digits', 'gcd-of-two-numbers', 'armstrong-number', 'divisors-of-a-number', 'check-prime-number', 'sort-an-array', 'remove-outermost-parentheses', 'reverse-words-in-a-string', 'largest-odd-number-in-a-string', 'longest-common-prefix', 'rotate-string', 'maximum-nesting-depth-of-the-parentheses', 'string-to-integer-atoi', 'count-and-say', 'find-the-index-of-the-first-occurrence-in-a-string', 'sum-of-beauty-of-all-substrings'])
SHEET_TAGS = (("striver-sde", STRIVER_SDE), ("striver-a2z", STRIVER_A2Z))
STRIVER_SDE |= {p["slug"] for p in SDE_EXTRA}
STRIVER_A2Z |= {p["slug"] for p in SDE_EXTRA}
STRIVER_SDE |= {p["slug"] for p in SDE_BATCH_4}
STRIVER_A2Z |= {p["slug"] for p in SDE_BATCH_4 if p["slug"] not in ("z-function", "compare-version-numbers")}
STRIVER_SDE |= {p["slug"] for p in SDE_BATCH_5}
STRIVER_A2Z |= {p["slug"] for p in SDE_BATCH_5}
STRIVER_SDE |= {p["slug"] for p in SDE_BATCH_6}
STRIVER_A2Z |= {p["slug"] for p in SDE_BATCH_6}
STRIVER_SDE |= {p["slug"] for p in SDE_BATCH_7}
STRIVER_A2Z |= {p["slug"] for p in SDE_BATCH_7}
STRIVER_SDE |= {p["slug"] for p in SDE_BATCH_8}
STRIVER_A2Z |= {p["slug"] for p in SDE_BATCH_8}
# Already-seeded problems that are also on the real Striver SDE sheet (tag only; their tests and answers exist).
STRIVER_SDE |= set(['count-inversions', 'reverse-pairs', 'majority-element-ii', 'largest-subarray-with-0-sum', 'count-subarrays-with-given-xor', 'find-the-repeating-and-missing-number', 'search-a-2d-matrix-ii', 'nth-root-of-an-integer', 'single-element-in-a-sorted-array', 'kth-element-of-two-sorted-arrays', 'aggressive-cows', 'median-in-a-row-wise-sorted-matrix', 'split-array-largest-sum', 'subset-sums', 'subsets-ii', 'combination-sum-ii', 'combination-sum-count', 'palindrome-partitioning-count', 'permutation-sequence', 'permutations', 'n-queens-count', 'm-coloring-problem', 'next-greater-element-ii', 'reverse-words-in-a-string', 'string-to-integer-atoi', 'longest-common-prefix', 'count-and-say', 'longest-palindromic-substring-length', 'binary-tree-right-side-view', 'count-complete-tree-nodes'])


MAX_CASE_CHARS = 40000  # keep well under the 50,000-character test_cases columns


def to_seed(problem):
    params, ret, ref = problem["params"], problem["ret"], problem["ref"]
    tests = []
    accept = getattr(ref, "accept", None)
    for case in problem["cases"]:
        args = case if isinstance(case, tuple) else (case,)
        if isinstance(case, list) and len(params) == 1:
            args = (case,)
        answer = ref(*args)
        # Answers that list every solution must stay readable, and string answers must be unique.
        if ret in ("sets", "rows", "strs") and len(answer) > 1500:
            continue
        # The database columns hold at most 50,000 characters; one oversized case aborts the whole seed (and the server start).
        if len(fmt_input(params, args)) > MAX_CASE_CHARS or len(fmt_output(ret, answer)) > MAX_CASE_CHARS:
            continue
        if accept is not None and not accept(*args):
            continue
        tests.append({
            "input": fmt_input(params, args),
            "expectedOutput": fmt_output(ret, answer),
            "sample": len(tests) < 2,
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
        "tags": problem["tags"] + [t for t, slugs in SHEET_TAGS if problem["slug"] in slugs and t not in problem["tags"]],
        "description": problem["description"] + "\n" + "\n".join(examples).rstrip() + "\n",
        "starterCode": starters(params, ret),
        "testCases": tests,
    }


# Study-path ordering: topics in the order a learner should meet them, then Easy -> Medium -> Hard inside each topic.
TOPIC_ORDER = ["Arrays & Hashing", "Two Pointers", "Sliding Window", "Stack", "Binary Search", "Linked List", "Trees",
               "Heap", "Backtracking", "Graphs", "Dynamic Programming", "Greedy", "Intervals", "Math & Bits", "Matrix"]
# A problem goes to the first topic here that one of its tags matches (more specific topics come first).
TOPIC_TAGS = [
    ("Linked List", {"linked-list"}), ("Trees", {"tree", "bst"}), ("Graphs", {"graph", "union-find", "topological-sort", "bfs", "dfs"}),
    ("Backtracking", {"backtracking"}), ("Heap", {"heap", "quickselect"}), ("Dynamic Programming", {"dynamic-programming", "dp"}),
    ("Sliding Window", {"sliding-window"}), ("Stack", {"stack", "monotonic-stack"}), ("Binary Search", {"binary-search"}),
    ("Intervals", {"intervals"}), ("Greedy", {"greedy"}), ("Two Pointers", {"two-pointers"}),
    ("Math & Bits", {"math", "bit-manipulation", "sieve"}), ("Matrix", {"matrix"}),
]
DIFF_RANK = {"EASY": 0, "MEDIUM": 1, "HARD": 2}


def topic_of(problem):
    tags = set(problem["tags"])
    return next((name for name, group in TOPIC_TAGS if tags & group), "Arrays & Hashing")


def study_order(problems):
    """Returns the problems sorted into study-path order (the position in this list is the problem's number)."""
    indexed = list(enumerate(problems))
    indexed.sort(key=lambda ip: (TOPIC_ORDER.index(topic_of(ip[1])), DIFF_RANK[ip[1]["difficulty"]], ip[0]))
    return [p for _, p in indexed]


def main():
    seed = [to_seed(p) for p in study_order(PROBLEMS)]
    for number, item in enumerate(seed, 1):
        item["order"] = number
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(len(p["testCases"]) for p in seed)
    print(f"Wrote {len(seed)} problems, {total} test cases -> {OUT}")


if __name__ == "__main__":
    main()
