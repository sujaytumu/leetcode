// Per-language starter code and test-driver generation.
//
// Every language exposes:
//   id, label, cm      identifiers (cm = CodeMirror language name)
//   starter(sig)       LeetCode-style starter template for the editor
//   build(sig, code)   { files, compile, run } for the sandbox runner
//
// User code is always placed after exactly one preamble line so that error
// line numbers can be corrected by subtracting LINE_OFFSET.
const fs = require("fs");
const path = require("path");
const { parseType, usedBases, mutatedParam } = require("../types");

const LINE_OFFSET = 1;
const staticFile = (...p) => fs.readFileSync(path.join(process.cwd(), "runner", "lang", ...p), "utf8");

// ---------------------------------------------------------------- Python
const PY_BASE = { int: "int", long: "int", double: "float", bool: "bool", string: "str", char: "str", ListNode: "Optional[ListNode]", TreeNode: "Optional[TreeNode]" };
function pyType(t) {
  const { base, dims } = parseType(t);
  let s = PY_BASE[base];
  for (let i = 0; i < dims; i++) s = `List[${s}]`;
  return s;
}
function pyIn(type, expr) {
  const { base, dims } = parseType(type);
  if (dims === 0 && base === "ListNode") return `list_from(${expr})`;
  if (dims === 0 && base === "TreeNode") return `tree_from(${expr})`;
  return expr;
}
function pyOut(type, expr) {
  const { base, dims } = parseType(type);
  if (dims === 0 && base === "ListNode") return `list_to(${expr})`;
  if (dims === 0 && base === "TreeNode") return `tree_to(${expr})`;
  return expr;
}

const python = {
  id: "python",
  label: "Python3",
  cm: "python",
  ext: "py",
  starter(sig) {
    const used = usedBases(sig);
    let s = "";
    if (used.has("ListNode"))
      s += "# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, val=0, next=None):\n#         self.val = val\n#         self.next = next\n";
    if (used.has("TreeNode"))
      s += "# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n#         self.val = val\n#         self.left = left\n#         self.right = right\n";
    const params = sig.params.map((p) => `${p.name}: ${pyType(p.type)}`).join(", ");
    const ret = sig.returns === "void" ? "None" : pyType(sig.returns);
    s += `class Solution:\n    def ${sig.name}(self, ${params}) -> ${ret}:\n`;
    if (sig.returns === "void") s += `        """\n        Do not return anything, modify ${sig.mutates} in-place instead.\n        """\n`;
    s += "        \n";
    return s;
  },
  build(sig, code) {
    const mut = mutatedParam(sig);
    const decls = sig.params.map((p) => `            ${p.name} = ${pyIn(p.type, `_t["${p.name}"]`)}`).join("\n");
    const args = sig.params.map((p) => p.name).join(", ");
    const call = mut ? `sol.${sig.name}(${args})` : `_r = sol.${sig.name}(${args})`;
    const resExpr = mut ? pyOut(mut.type, mut.name) : pyOut(sig.returns, "_r");
    const main = String.raw`import sys, json, time, threading, traceback
from ds import *
from solution import Solution


def _run():
    tests = json.load(open(sys.argv[1]))
    out = open(sys.argv[2], "w")
    sol = Solution()
    for _t in tests:
        try:
${decls}
            _t0 = time.perf_counter()
            ${call}
            _ms = (time.perf_counter() - _t0) * 1000
            _res = ${resExpr}
            out.write(json.dumps({"ok": True, "out": _res, "ms": _ms}) + "\n")
            out.flush()
        except BaseException:
            out.write(json.dumps({"ok": False, "err": traceback.format_exc()[-2500:]}) + "\n")
            out.flush()
    out.close()


sys.setrecursionlimit(1_000_000)
threading.stack_size(256 * 1024 * 1024)
_th = threading.Thread(target=_run)
_th.start()
_th.join()
sys.stdout.flush()
`;
    const pre =
      "from ds import *; from collections import *; from heapq import *; from bisect import *; from functools import *; import sys, math, heapq, bisect, itertools, functools, collections, string, re\n";
    return {
      files: { "ds.py": staticFile("py", "ds.py"), "solution.py": pre + code, "main.py": main },
      compile: null,
      run: ["python3", "-X", "utf8", "main.py", "tests.json", "results.jsonl"],
      limitVirtualMemory: true,
    };
  },
};

// ------------------------------------------------------------------- C++
const CPP_BASE = { int: "int", long: "long long", double: "double", bool: "bool", string: "string", char: "char", ListNode: "ListNode*", TreeNode: "TreeNode*" };
function cppType(t) {
  const { base, dims } = parseType(t);
  let s = CPP_BASE[base];
  for (let i = 0; i < dims; i++) s = `vector<${s}>`;
  return s;
}

const cpp = {
  id: "cpp",
  label: "C++",
  cm: "cpp",
  ext: "cpp",
  starter(sig) {
    const used = usedBases(sig);
    let s = "";
    if (used.has("ListNode"))
      s += "/**\n * Definition for singly-linked list.\n * struct ListNode {\n *     int val;\n *     ListNode *next;\n *     ListNode() : val(0), next(nullptr) {}\n *     ListNode(int x) : val(x), next(nullptr) {}\n *     ListNode(int x, ListNode *next) : val(x), next(next) {}\n * };\n */\n";
    if (used.has("TreeNode"))
      s += "/**\n * Definition for a binary tree node.\n * struct TreeNode {\n *     int val;\n *     TreeNode *left;\n *     TreeNode *right;\n *     TreeNode() : val(0), left(nullptr), right(nullptr) {}\n *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}\n *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}\n * };\n */\n";
    const params = sig.params.map((p) => `${cppType(p.type)}${parseType(p.type).dims > 0 ? "&" : ""} ${p.name}`).join(", ");
    const ret = sig.returns === "void" ? "void" : cppType(sig.returns);
    s += `class Solution {\npublic:\n    ${ret} ${sig.name}(${params}) {\n        \n    }\n};\n`;
    return s;
  },
  build(sig, code) {
    const mut = mutatedParam(sig);
    const decls = sig.params
      .map((p) => `            ${cppType(p.type)} ${p.name}; __h::cv(__t.get("${p.name}"), ${p.name});`)
      .join("\n");
    const args = sig.params.map((p) => p.name).join(", ");
    const call = mut ? `__sol.${sig.name}(${args})` : `auto __r = __sol.${sig.name}(${args})`;
    const resExpr = mut ? mut.name : "__r";
    const main = String.raw`#include "solution.cpp"

int main(int argc, char **argv) {
    ifstream __in(argv[1]);
    stringstream __ss;
    __ss << __in.rdbuf();
    string __txt = __ss.str();
    __h::Parser __p(__txt);
    __h::J __tests = __p.parse();
    ofstream __out(argv[2]);
    Solution __sol;
    for (size_t __i = 0; __i < __tests.a.size(); __i++) {
        const __h::J &__t = __tests.a[__i];
        try {
${decls}
            auto __t0 = chrono::steady_clock::now();
            ${call};
            double __ms = chrono::duration<double, milli>(chrono::steady_clock::now() - __t0).count();
            string __res = __h::sr(${resExpr});
            __out << "{\"ok\":true,\"out\":" << __res << ",\"ms\":" << __ms << "}" << endl;
        } catch (const exception &__e) {
            __out << "{\"ok\":false,\"err\":" << __h::esc(string("exception: ") + __e.what()) << "}" << endl;
        } catch (...) {
            __out << "{\"ok\":false,\"err\":\"unknown exception\"}" << endl;
        }
    }
    return 0;
}
`;
    return {
      files: { "prelude.h": staticFile("cpp", "prelude.h"), "solution.cpp": '#include "prelude.h"\n' + code, "main.cpp": main },
      compile: ["g++", "-O2", "-std=c++17", "-w", "-o", "main", "main.cpp"],
      run: ["./main", "tests.json", "results.jsonl"],
      limitVirtualMemory: true,
    };
  },
};

// ------------------------------------------------------------------ Java
const JAVA_BASE = { int: "int", long: "long", double: "double", bool: "boolean", string: "String", char: "char", ListNode: "ListNode", TreeNode: "TreeNode" };
function javaType(t) {
  const { base, dims } = parseType(t);
  return JAVA_BASE[base] + "[]".repeat(dims);
}
const JAVA_ARR = { int: "ia", long: "la", double: "da", bool: "ba", string: "sa", char: "ca" };
function javaIn(type, expr) {
  const { base, dims } = parseType(type);
  if (dims === 0) {
    return {
      int: `Json.iv(${expr})`,
      long: `Json.lv(${expr})`,
      double: `Json.dv(${expr})`,
      bool: `(Boolean) ${expr}`,
      string: `(String) ${expr}`,
      char: `Json.cv(${expr})`,
      ListNode: `Json.ln(${expr})`,
      TreeNode: `Json.tn(${expr})`,
    }[base];
  }
  if (dims === 1 && JAVA_ARR[base]) return `Json.${JAVA_ARR[base]}(${expr})`;
  if (dims === 2 && JAVA_ARR[base]) return `Json.${JAVA_ARR[base]}a(${expr})`;
  throw new Error(`Java driver does not support type ${type}`);
}

const java = {
  id: "java",
  label: "Java",
  cm: "java",
  ext: "java",
  starter(sig) {
    const used = usedBases(sig);
    let s = "";
    if (used.has("ListNode"))
      s += "/**\n * Definition for singly-linked list.\n * public class ListNode {\n *     int val;\n *     ListNode next;\n *     ListNode() {}\n *     ListNode(int val) { this.val = val; }\n *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }\n * }\n */\n";
    if (used.has("TreeNode"))
      s += "/**\n * Definition for a binary tree node.\n * public class TreeNode {\n *     int val;\n *     TreeNode left;\n *     TreeNode right;\n *     TreeNode() {}\n *     TreeNode(int val) { this.val = val; }\n *     TreeNode(int val, TreeNode left, TreeNode right) {\n *         this.val = val;\n *         this.left = left;\n *         this.right = right;\n *     }\n * }\n */\n";
    const params = sig.params.map((p) => `${javaType(p.type)} ${p.name}`).join(", ");
    const ret = sig.returns === "void" ? "void" : sig.javaReturn || javaType(sig.returns);
    s += `class Solution {\n    public ${ret} ${sig.name}(${params}) {\n        \n    }\n}\n`;
    return s;
  },
  build(sig, code) {
    const mut = mutatedParam(sig);
    const decls = sig.params
      .map((p) => `                ${javaType(p.type)} ${p.name} = ${javaIn(p.type, `__t.get("${p.name}")`)};`)
      .join("\n");
    const args = sig.params.map((p) => p.name).join(", ");
    const call = mut ? `__sol.${sig.name}(${args}); Object __r = ${mut.name};` : `Object __r = __sol.${sig.name}(${args});`;
    const main = String.raw`import java.util.*;
import java.io.*;
import java.nio.file.*;

public class Main {
    public static void main(String[] args) throws Exception {
        Thread th = new Thread(null, () -> {
            try { run(args); } catch (Exception e) { e.printStackTrace(); }
        }, "runner", 1L << 29);
        th.start();
        th.join();
    }

    @SuppressWarnings("unchecked")
    static void run(String[] args) throws Exception {
        List<Object> tests = (List<Object>) Json.parse(new String(Files.readAllBytes(Paths.get(args[0]))));
        PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(args[1])));
        Solution __sol = new Solution();
        for (Object __o : tests) {
            Map<String, Object> __t = (Map<String, Object>) __o;
            try {
${decls}
                long __t0 = System.nanoTime();
                ${call}
                double __ms = (System.nanoTime() - __t0) / 1e6;
                String __res = Json.ser(__r);
                out.println("{\"ok\":true,\"out\":" + __res + ",\"ms\":" + __ms + "}");
                out.flush();
            } catch (Throwable __e) {
                StringWriter sw = new StringWriter();
                __e.printStackTrace(new PrintWriter(sw));
                String msg = sw.toString();
                if (msg.length() > 2500) msg = msg.substring(0, 2500);
                out.println("{\"ok\":false,\"err\":" + Json.esc(msg) + "}");
                out.flush();
            }
        }
        out.close();
    }
}
`;
    const pre = "import java.util.*; import java.io.*; import java.math.*; import java.util.stream.*;\n";
    return {
      files: {
        "Solution.java": pre + code,
        "Main.java": main,
        "Json.java": staticFile("java", "Json.java"),
        "ListNode.java": staticFile("java", "ListNode.java"),
        "TreeNode.java": staticFile("java", "TreeNode.java"),
      },
      compile: ["javac", "-encoding", "UTF-8", "-Xlint:none", "-nowarn", "-d", "out", "Solution.java", "Main.java", "Json.java", "ListNode.java", "TreeNode.java"],
      run: ["java", "-Xmx512m", "-Xss64m", "-XX:+UseSerialGC", "-cp", "out", "Main", "tests.json", "results.jsonl"],
      limitVirtualMemory: false,
    };
  },
};

const LANGS = { python, cpp, java };

// Remove sandbox paths / JVM noise and shift line numbers back to the user's code.
function cleanErrors(text, dir) {
  if (!text) return "";
  let t = String(text);
  if (dir) t = t.split(dir + "/").join("");
  t = t
    .split("\n")
    .filter((l) => !l.startsWith("Picked up JAVA_TOOL_OPTIONS") && !l.startsWith("Picked up _JAVA_OPTIONS"))
    .join("\n");
  t = t.replace(/(solution\.cpp|Solution\.java):(\d+)/g, (_, f, n) => `${f}:${Math.max(1, Number(n) - LINE_OFFSET)}`);
  t = t.replace(/(Solution\.java:)(\d+)\)/g, (_, f, n) => `${f}${Math.max(1, Number(n) - LINE_OFFSET)})`);
  t = t.replace(/(solution\.py", line )(\d+)/g, (_, f, n) => `${f}${Math.max(1, Number(n) - LINE_OFFSET)}`);
  return t.trim();
}

module.exports = { LANGS, LINE_OFFSET, cleanErrors, cppType, javaType, pyType };
