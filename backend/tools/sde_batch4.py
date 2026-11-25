"""Striver SDE sheet batch 4: the binary-tree, heap, stack, string and greedy problems the app was still missing.

Each expected output comes from a plain reference implementation; the optimal C++ answers are checked against it.
"""
from fractions import Fraction


def make_batch(mk, rng, h):
    TN, tok2tree, tree2tok, rand_tree = h["TN"], h["tok2tree"], h["tree2tok"], h["rand_tree"]
    TREE_IN, TREE_OUT = h["TREE_IN"], h["TREE_OUT"]
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]
    TREE_SIZES = [1, 2, 3, 5, 8, 14, 25, 45, 80]

    # ------------------------------------------------------------ helpers
    def levels(root):
        out, cur = [], [root] if root else []
        while cur:
            out.append(cur)
            cur = [c for n in cur for c in (n.left, n.right) if c]
        return out

    def distinct_tree(m):
        """Random shape, distinct values 1..300, as level-order tokens."""
        toks = rand_tree(m)
        root = tok2tree(toks)
        vals = iter(rng.sample(range(1, 301), m))
        for lvl in levels(root):
            for n in lvl:
                n.val = next(vals)
        return tree2tok(root)

    def inorder_of(n, out):
        if n:
            inorder_of(n.left, out); out.append(n.val); inorder_of(n.right, out)
        return out

    def postorder_of(n, out):
        if n:
            postorder_of(n.left, out); postorder_of(n.right, out); out.append(n.val)
        return out

    def preorder_of(n, out):
        if n:
            out.append(n.val); preorder_of(n.left, out); preorder_of(n.right, out)
        return out

    # ------------------------------------------------------------ references
    def preorder(t): return preorder_of(tok2tree(t), [])
    def postorder(t): return postorder_of(tok2tree(t), [])
    def left_view(t): return [lvl[0].val for lvl in levels(tok2tree(t))]

    def by_distance(t, keep_first):
        root, seen, queue = tok2tree(t), {}, []
        if root:
            queue = [(root, 0)]
        for node, hd in queue:
            if keep_first:
                seen.setdefault(hd, node.val)
            else:
                seen[hd] = node.val
            if node.left: queue.append((node.left, hd - 1))
            if node.right: queue.append((node.right, hd + 1))
        return [seen[k] for k in sorted(seen)]

    def top_view(t): return by_distance(t, True)
    def bottom_view(t): return by_distance(t, False)

    def vertical(t):
        root, items = tok2tree(t), []

        def go(n, col, row):
            if n:
                items.append((col, row, n.val))
                go(n.left, col - 1, row + 1); go(n.right, col + 1, row + 1)
        go(root, 0, 0)
        items.sort()
        out = {}
        for col, _, v in items:
            out.setdefault(col, []).append(v)
        return [out[c] for c in sorted(out)]

    def root_to_node(t, target):
        def go(n, path):
            if not n: return None
            path = path + [n.val]
            if n.val == target: return path
            return go(n.left, path) or go(n.right, path)
        return go(tok2tree(t), []) or []

    def max_width(t):
        best = 0
        stack = [[(tok2tree(t), 0)]] if tok2tree(t) else []
        for lvl in stack:
            best = max(best, lvl[-1][1] - lvl[0][1] + 1)
            nxt = [(c, 2 * i + k) for n, i in lvl for k, c in enumerate((n.left, n.right)) if c]
            if nxt: stack.append(nxt)
        return best

    def boundary(t):
        root = tok2tree(t)
        if not root: return []
        leaf = lambda n: not n.left and not n.right
        out = [] if leaf(root) else [root.val]
        n = root.left
        while n:
            if not leaf(n): out.append(n.val)
            n = n.left or n.right
        def leaves(n):
            if n:
                if leaf(n): out.append(n.val)
                leaves(n.left); leaves(n.right)
        leaves(root)
        right, n = [], root.right
        while n:
            if not leaf(n): right.append(n.val)
            n = n.right or n.left
        return out + right[::-1]

    def build_in_post(inorder, postorder):
        if not postorder: return []
        pos = {v: i for i, v in enumerate(inorder)}
        def go(lo, hi, post):
            if lo > hi or not post: return None
            node = TN(post.pop())
            k = pos[node.val]
            node.right = go(k + 1, hi, post)
            node.left = go(lo, k - 1, post)
            return node
        return tree2tok(go(0, len(inorder) - 1, list(postorder)))

    def flatten(t):
        order = preorder_of(tok2tree(t), [])
        root = cur = None
        for v in order:
            node = TN(v)
            if cur: cur.right = node
            else: root = node
            cur = node
        return tree2tok(root)

    def children_sum(t):
        def ok(n):
            if not n or (not n.left and not n.right): return True
            return n.val == (n.left.val if n.left else 0) + (n.right.val if n.right else 0) and ok(n.left) and ok(n.right)
        return ok(tok2tree(t))

    def fractional_knapsack(values, weights, cap):
        total, left = Fraction(0), cap
        for v, w in sorted(zip(values, weights), key=lambda x: -Fraction(x[0], x[1])):
            take = min(w, left)
            total += Fraction(v * take, w)
            left -= take
        return (total * 100).__floor__()

    def min_coins(amount):
        count = 0
        for c in (1000, 500, 100, 50, 20, 10, 5, 2, 1):
            count, amount = count + amount // c, amount % c
        return count

    def median_text(a, b):
        m = sorted(a + b)
        n = len(m)
        if n % 2: return str(m[n // 2])
        s = m[n // 2 - 1] + m[n // 2]
        return str(s // 2) if s % 2 == 0 else ("-" if s < 0 else "") + f"{abs(s) // 2}.5"

    def merge_k(rows): return sorted(x for r in rows for x in r)
    def k_max_sums(a, b, k): return sorted((x + y for x in a for y in b), reverse=True)[:k]

    def next_greater(nums):
        return [next((y for y in nums[i + 1:] if y > x), -1) for i, x in enumerate(nums)]

    def sort_stack(nums): return sorted(nums)

    def z_function(s):
        n = len(s)
        z = []
        for i in range(n):
            k = 0
            while i + k < n and s[k] == s[i + k]:
                k += 1
            z.append(k)
        return z

    def compare_version(a, b):
        x, y = [int(p) for p in a.split(".")], [int(p) for p in b.split(".")]
        L = max(len(x), len(y))
        x += [0] * (L - len(x)); y += [0] * (L - len(y))
        return (x > y) - (x < y)

    # ------------------------------------------------------------ cases
    def c_trees(lo=-20, hi=50, extra=()):
        return [rand_tree(m, lo, hi) for m in TREE_SIZES] + list(extra)

    def c_root_path():
        out = []
        for m in TREE_SIZES:
            t = distinct_tree(m)
            out.append((t, rng.choice([v for v in t if v is not None])))
        return out

    def c_width():
        out = []
        for m in TREE_SIZES + [150]:
            while True:
                t = rand_tree(m, 1, 99)
                if max_width(t) < 2 ** 31: break
            out.append(t)
        return out + [[1, 3, 2, 5, None, None, 9, 6, None, 7], [1, 3, 2, 5, 3, None, 9]]

    def c_in_post():
        out = []
        for m in [1, 2, 3, 5, 9, 16, 30, 60]:
            root = tok2tree(distinct_tree(m))
            out.append((inorder_of(root, []), postorder_of(root, [])))
        return out

    def valid_sum_tree(m):
        root = tok2tree(rand_tree(m, 0, 0))
        def fill(n):
            if not n.left and not n.right:
                n.val = rng.randint(0, 6)
            else:
                n.val = sum(fill(c) for c in (n.left, n.right) if c)
            return n.val
        fill(root)
        return root

    def c_children_sum():
        out = []
        for m in [1, 2, 3, 4, 6, 9, 12]:
            root = valid_sum_tree(m)
            out.append(tree2tok(root))
            for lvl in levels(root):
                lvl[-1].val += 1
                break
            out.append(tree2tok(root))
        return out + [rand_tree(m, 0, 20) for m in [5, 11]] + [[10, 8, 2, 3, 5, 2], [1]]

    def c_knapsack():
        out = []
        for n in [1, 2, 4, 7, 12, 30]:
            w = arr(n, 1, 50)
            out.append((arr(n, 1, 100), w, rng.randint(1, max(1, sum(w)))))
        return out + [([60, 100, 120], [10, 20, 30], 50), ([500], [30], 10)]

    def c_median():
        out = [(arr(rng.randint(1, n), -100, 100), arr(rng.randint(1, n), -100, 100)) for n in [1, 3, 6, 15, 40, 120, 400]]
        return [(sorted(a), sorted(b)) for a, b in out] + [([1, 3], [2]), ([1, 2], [3, 4]), ([-5], [-4]), ([0, 0], [0, 0])]

    def c_merge_k():
        return [[sorted(arr(rng.randint(1, 8), -50, 90)) for _ in range(k)] for k in [1, 2, 3, 4, 6, 10, 20]]

    def c_kmax():
        out = []
        for n in [1, 2, 4, 8, 20, 60]:
            a, b = arr(n, 0, 100), arr(n, 0, 100)
            out.append((a, b, rng.randint(1, min(n * n, 50))))
        return out + [([1, 4, 2, 3], [2, 5, 1, 6], 4), ([9], [9], 1)]

    def c_versions():
        mk_v = lambda: ".".join(("0" * rng.randint(0, 2)) + str(rng.randint(0, 12)) for _ in range(rng.randint(1, 4)))
        out = [(mk_v(), mk_v()) for _ in range(9)]
        return out + [("1.01", "1.001"), ("1.0", "1.0.0"), ("0.1", "1.1"), ("1.0.1", "1"), ("7.5.2.4", "7.5.3")]

    def c_z():
        out = ["".join(rng.choice("ab") for _ in range(n)) for n in [1, 2, 3, 6, 12, 40, 150, 600]]
        return out + ["aaaaa", "abcabcabc", "abcd", "aabxaabxcaabxaabxay"]

    NODES = "`0 <= n <= 100` nodes"
    ARR = "Line 1: `n`.\nLine 2: `n` space-separated integers."
    return [
        mk("binary-tree-preorder-traversal", "Binary Tree Preorder Traversal", "EASY", ["tree", "dfs", "stack"], [("root", "tree")], "int[]", preorder,
           c_trees(extra=[[]]), "Return the preorder traversal (node, left, right) of the tree. Try an iterative solution.", TREE_IN,
           "The node values in preorder, space separated (a blank line for the empty tree).", [NODES, "`-100 <= val <= 100`"]),
        mk("binary-tree-postorder-traversal", "Binary Tree Postorder Traversal", "EASY", ["tree", "dfs", "stack"], [("root", "tree")], "int[]", postorder,
           c_trees(extra=[[]]), "Return the postorder traversal (left, right, node) of the tree. Try an iterative solution.", TREE_IN,
           "The node values in postorder, space separated (a blank line for the empty tree).", [NODES, "`-100 <= val <= 100`"]),
        mk("left-view-of-binary-tree", "Left View of Binary Tree", "MEDIUM", ["tree", "bfs", "dfs"], [("root", "tree")], "int[]", left_view,
           c_trees(extra=[[]]), "Imagine standing on the left side of the tree. Return the values of the nodes you can see, from top to bottom "
           "(the first node of every level).", TREE_IN, "The visible values, space separated (blank for the empty tree).", [NODES, "`-100 <= val <= 100`"]),
        mk("top-view-of-binary-tree", "Top View of Binary Tree", "MEDIUM", ["tree", "bfs", "hash-table"], [("root", "tree")], "int[]", top_view,
           c_trees(extra=[[]]), "Give the root horizontal distance 0; a left child is one less than its parent and a right child one more. Looking at "
           "the tree from above, each horizontal distance shows its highest node. Return those values from the smallest distance to the largest.",
           TREE_IN, "The top view from left to right, space separated (blank for the empty tree).", [NODES, "`-100 <= val <= 100`"]),
        mk("bottom-view-of-binary-tree", "Bottom View of Binary Tree", "MEDIUM", ["tree", "bfs", "hash-table"], [("root", "tree")], "int[]", bottom_view,
           c_trees(extra=[[]]), "Give the root horizontal distance 0; a left child is one less than its parent and a right child one more. Looking at "
           "the tree from below, each horizontal distance shows its lowest node. If two nodes are equally low at the same distance, the one that comes "
           "later in level order (the right one) is shown. Return the values from the smallest distance to the largest.",
           TREE_IN, "The bottom view from left to right, space separated (blank for the empty tree).", [NODES, "`-100 <= val <= 100`"]),
        mk("vertical-order-traversal-of-a-binary-tree", "Vertical Order Traversal of a Binary Tree", "HARD", ["tree", "dfs", "hash-table", "sorting"],
           [("root", "tree")], "int[][]", vertical, c_trees(extra=[[1, 2, 3, 4, 6, 5, 7], [3, 9, 20, None, None, 15, 7]]),
           "The root is at row 0, column 0; a child sits one row lower, and one column left or right of its parent. Return the nodes grouped by column from "
           "left to right. Inside a column list the nodes from the top row down, and sort nodes in the same row and column by value.", TREE_IN,
           "One line per column, left to right: the values of that column separated by spaces.", ["`1 <= n <= 100` nodes", "`-100 <= val <= 100`"]),
        mk("root-to-node-path-in-a-binary-tree", "Root to Node Path in a Binary Tree", "MEDIUM", ["tree", "dfs", "backtracking"],
           [("root", "tree"), ("target", "int")], "int[]", root_to_node, c_root_path(),
           "All node values are distinct. Return the values on the path from the root to the node whose value is `target`, root first.",
           "Line 1: `n`, the number of tokens.\nLine 2: the tree in level order (`null` for a missing child).\nLine 3: `target`, a value that exists in the tree.",
           "The path values, space separated.", ["`1 <= n <= 100` nodes", "`1 <= val <= 300`, all distinct"]),
        mk("maximum-width-of-binary-tree", "Maximum Width of Binary Tree", "MEDIUM", ["tree", "bfs"], [("root", "tree")], "int", max_width, c_width(),
           "The width of a level is the distance between its leftmost and rightmost existing nodes, counting the missing nodes in between as if the tree were "
           "complete. Return the largest width over all levels. The answer fits in a 32-bit signed integer.", TREE_IN, "The maximum width.",
           ["`1 <= n <= 150` nodes", "`1 <= val <= 99`"]),
        mk("boundary-traversal-of-binary-tree", "Boundary Traversal of Binary Tree", "MEDIUM", ["tree", "dfs"], [("root", "tree")], "int[]", boundary,
           c_trees(extra=[[1], [1, 2], [1, None, 3], [1, 2, 3, 4, 5, 6, 7]]),
           "Walk around the edge of the tree anticlockwise: the root, then the left boundary from top to bottom (leaves excluded), then all the leaves from "
           "left to right, then the right boundary from bottom to top (leaves and the root excluded). Return the values in that order.", TREE_IN,
           "The boundary values, space separated.", ["`1 <= n <= 100` nodes", "`-100 <= val <= 100`"]),
        mk("construct-binary-tree-from-inorder-and-postorder-traversal", "Construct Binary Tree from Inorder and Postorder Traversal", "MEDIUM",
           ["tree", "divide-and-conquer", "hash-table"], [("inorder", "int[]"), ("postorder", "int[]")], "tree", build_in_post, c_in_post(),
           "Given the inorder and postorder traversals of a binary tree with distinct values, rebuild the tree and return its root.",
           "Line 1: `n`.\nLine 2: the inorder values.\nLine 3: `n`.\nLine 4: the postorder values.", TREE_OUT,
           ["`1 <= n <= 60`", "`1 <= val <= 300`, all distinct"]),
        mk("flatten-binary-tree-to-linked-list", "Flatten Binary Tree to Linked List", "MEDIUM", ["tree", "dfs", "linked-list"], [("root", "tree")], "tree", flatten,
           c_trees(extra=[[]]), "Flatten the tree in place into a linked list that uses the right pointers, in the same order as a preorder traversal. "
           "Every left pointer must become `null`. Return the root.", TREE_IN, TREE_OUT, [NODES, "`-100 <= val <= 100`"]),
        mk("children-sum-property", "Check for Children Sum Property", "MEDIUM", ["tree", "dfs"], [("root", "tree")], "bool", children_sum, c_children_sum(),
           "A tree satisfies the children sum property when every node that has at least one child holds a value equal to the sum of its children's values "
           "(a missing child counts as 0). Leaves always satisfy it. Return `true` if the whole tree does.", TREE_IN, "`true` or `false`.",
           ["`1 <= n <= 100` nodes", "`0 <= val <= 100`"]),
        mk("fractional-knapsack", "Fractional Knapsack", "MEDIUM", ["greedy", "sorting"], [("values", "int[]"), ("weights", "int[]"), ("capacity", "int")], "int",
           fractional_knapsack, c_knapsack(),
           "Item `i` has value `values[i]` and weight `weights[i]`, and any fraction of an item may be taken for the same fraction of its value. Find the maximum "
           "total value that fits in a knapsack of the given capacity. To avoid decimals, return **100 times** that value rounded down to an integer.",
           "Line 1: `n`.\nLine 2: the values.\nLine 3: `n`.\nLine 4: the weights.\nLine 5: `capacity`.", "100 times the maximum value, rounded down.",
           ["`1 <= n <= 30`", "`1 <= values[i] <= 100`", "`1 <= weights[i] <= 50`", "`1 <= capacity`"]),
        mk("minimum-number-of-coins", "Minimum Number of Coins", "EASY", ["greedy", "math"], [("amount", "int")], "int", min_coins,
           [1, 2, 3, 7, 9, 18, 49, 93, 100, 121, 999, 1000, 1943, 5000, 98765, 100000],
           "The available denominations are `1, 2, 5, 10, 20, 50, 100, 500, 1000`, with unlimited coins of each. Return the smallest number of coins that add up to "
           "`amount` using a greedy strategy.", "Line 1: `amount`.", "The minimum number of coins.", ["`1 <= amount <= 100000`"]),
        mk("median-of-two-sorted-arrays", "Median of Two Sorted Arrays", "HARD", ["array", "binary-search", "divide-and-conquer"],
           [("nums1", "int[]"), ("nums2", "int[]")], "str", median_text, c_median(),
           "Two sorted arrays are given. Return the median of all their values together. A median is either an integer or ends in `.5`, so return it as text "
           "with no trailing zeros, for example `3` or `2.5` (negative example `-1.5`). Aim for `O(log(min(m, n)))`.",
           "Line 1: `m`.\nLine 2: `nums1`.\nLine 3: `n`.\nLine 4: `nums2`.", "The median as text.",
           ["`1 <= m, n <= 400`", "`-100 <= value <= 100`", "Both arrays are sorted ascending"]),
        mk("merge-k-sorted-arrays", "Merge K Sorted Arrays", "MEDIUM", ["array", "heap"], [("arrays", "int[][]")], "int[]", merge_k, c_merge_k(),
           "`k` arrays are each sorted in ascending order. Merge them into one sorted array, ideally in `O(N log k)` with a min-heap.",
           "Line 1: `k`.\nNext `k` lines: one array each (space separated).", "All values in ascending order.",
           ["`1 <= k <= 20`", "Every array has between 1 and 8 values", "`-50 <= value <= 90`"]),
        mk("k-maximum-sum-combinations", "K Maximum Sum Combinations", "HARD", ["array", "heap", "sorting"], [("a", "int[]"), ("b", "int[]"), ("k", "int")],
           "int[]", k_max_sums, c_kmax(),
           "Two arrays of the same length are given. Form every sum `a[i] + b[j]` and return the `k` largest of them in descending order (equal sums are listed "
           "as often as they occur).", "Line 1: `n`.\nLine 2: `a`.\nLine 3: `n`.\nLine 4: `b`.\nLine 5: `k`.", "The `k` largest sums, descending.",
           ["`1 <= n <= 60`", "`1 <= k <= min(n * n, 50)`", "`0 <= a[i], b[i] <= 100`"]),
        mk("next-greater-element", "Next Greater Element", "MEDIUM", ["array", "stack", "monotonic-stack"], [("nums", "int[]")], "int[]", next_greater,
           [arr(n, -50, 50) for n in [1, 2, 5, 12, 40, 150, 500]] + [[5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [4, 5, 2, 25]],
           "For every element find the first element to its **right** that is strictly greater. Return that value, or `-1` when none exists.", ARR,
           "`n` integers: the next greater value for each position.", ["`1 <= n <= 1000`", "`-10^4 <= nums[i] <= 10^4`"]),
        mk("sort-a-stack", "Sort a Stack", "MEDIUM", ["stack", "recursion", "sorting"], [("stack", "int[]")], "int[]", sort_stack,
           [arr(n, -50, 99) for n in [1, 2, 4, 9, 20, 60, 300]] + [[3, 1, 2], [5, 5, 1]],
           "A stack is given from bottom to top. Sort it so that the **largest** value ends on top, using only stack operations and recursion (no loops over "
           "the data and no extra array). Return the stack from bottom to top.", "Line 1: `n`, the stack size.\nLine 2: the values from bottom to top.",
           "The sorted stack from bottom to top (smallest first).", ["`1 <= n <= 300`", "`-100 <= value <= 100`"]),
        mk("z-function", "Z-Function", "MEDIUM", ["string"], [("s", "str")], "int[]", z_function, c_z(),
           "The Z-array of a string has, at position `i`, the length of the longest common prefix between `s` and the suffix starting at `i`. By definition "
           "`z[0] = n`. Return the Z-array in `O(n)`.", "Line 1: `s`.", "`n` integers: the Z-array.", ["`1 <= s.length <= 1000`", "Lowercase English letters"]),
        mk("compare-version-numbers", "Compare Version Numbers", "MEDIUM", ["string", "two-pointers"], [("version1", "str"), ("version2", "str")], "int", compare_version,
           c_versions(),
           "Versions are numbers joined by dots such as `1.02.3`. Compare them revision by revision as integers (leading zeros do not matter) and treat a missing "
           "revision as `0`. Return `1` if `version1` is newer, `-1` if it is older and `0` if they are equal.", "Line 1: `version1`.\nLine 2: `version2`.",
           "`1`, `-1` or `0`.", ["Digits and dots only", "No two dots next to each other, and neither starts nor ends with a dot", "Each revision fits in a 32-bit integer"]),
    ]
