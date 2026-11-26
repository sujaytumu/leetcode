"""Striver sheet batch 5: 3Sum/4Sum, the core graph algorithms and the BST problems the app was still missing.

Every expected output comes from a deliberately different (usually brute-force) reference, so the optimal C++ answers in
answers/a2z-06-graphs-bst.txt are checked against an independent method.
"""
import heapq
from collections import deque
from itertools import combinations

INF = 100000000  # "unreachable" in Bellman-Ford


def make_batch(mk, rng, h):
    TN, tok2tree, tree2tok, rand_tree = h["TN"], h["tok2tree"], h["tree2tok"], h["rand_tree"]
    TREE_IN = h["TREE_IN"]
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]
    N_SMALL = [1, 2, 3, 4, 6, 9, 14, 22, 35]
    TREE_SIZES = [1, 2, 3, 5, 8, 14, 25, 45, 80]

    # ------------------------------------------------------------------ graph helpers
    def tree_edges(n):
        order = list(range(n))
        rng.shuffle(order)
        return [[order[i], order[rng.randrange(i)]] for i in range(1, n)]

    def distinct_pairs(n, m, directed):
        pool = [(i, j) for i in range(n) for j in range(n) if i != j and (directed or i < j)]
        picked = rng.sample(pool, min(m, len(pool)))
        out = []
        for u, v in picked:
            if not directed and rng.random() < 0.5:
                u, v = v, u
            out.append([u, v])
        return out

    def dag_edges(n, m):
        perm = list(range(n))
        rng.shuffle(perm)
        pool = [(i, j) for i in range(n) for j in range(i + 1, n)]
        return [[perm[i], perm[j]] for i, j in rng.sample(pool, min(m, len(pool)))]

    def adj_of(n, edges, directed):
        adj = [[] for _ in range(n)]
        for e in edges:
            adj[e[0]].append(e[1])
            if not directed:
                adj[e[1]].append(e[0])
        return adj

    def components(n, edges, skip_edge=None, skip_node=None):
        adj = [[] for _ in range(n)]
        for i, e in enumerate(edges):
            if i == skip_edge or e[0] == skip_node or e[1] == skip_node:
                continue
            adj[e[0]].append(e[1])
            adj[e[1]].append(e[0])
        seen, count = set(), 0
        for s in range(n):
            if s == skip_node or s in seen:
                continue
            count += 1
            seen.add(s)
            queue = [s]
            for u in queue:
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        queue.append(v)
        return count

    def closure(n, edges):
        reach = [[False] * n for _ in range(n)]
        for u, v in edges:
            reach[u][v] = True
        for k in range(n):
            for i in range(n):
                if reach[i][k]:
                    for j in range(n):
                        if reach[k][j]:
                            reach[i][j] = True
        return reach

    # ------------------------------------------------------------------ tree helpers
    def levels(root):
        out, cur = [], [root] if root else []
        while cur:
            out.append(cur)
            cur = [c for n in cur for c in (n.left, n.right) if c]
        return out

    def bst_insert(root, v):
        if not root:
            return TN(v)
        node = root
        while True:
            side = "left" if v < node.val else "right"
            nxt = getattr(node, side)
            if nxt is None:
                setattr(node, side, TN(v))
                return root
            node = nxt

    def random_bst(m, lo=1, hi=200):
        values = rng.sample(range(lo, hi + 1), m)
        root = None
        for v in values:
            root = bst_insert(root, v)
        return root

    def inorder_of(n, out):
        if n:
            inorder_of(n.left, out); out.append(n.val); inorder_of(n.right, out)
        return out

    def preorder_of(n, out):
        if n:
            out.append(n.val); preorder_of(n.left, out); preorder_of(n.right, out)
        return out

    def distinct_tree(m):
        toks = rand_tree(m)
        root = tok2tree(toks)
        vals = iter(rng.sample(range(1, 301), m))
        for lvl in levels(root):
            for n in lvl:
                n.val = next(vals)
        return tree2tok(root)

    # ------------------------------------------------------------------ references: arrays
    def three_sum(nums):
        a, found = sorted(nums), set()
        for i, j, k in combinations(range(len(a)), 3):
            if a[i] + a[j] + a[k] == 0:
                found.add((a[i], a[j], a[k]))
        return [list(t) for t in sorted(found)]

    def four_sum(nums, target):
        a, found = sorted(nums), set()
        for i, j, k, l in combinations(range(len(a)), 4):
            if a[i] + a[j] + a[k] + a[l] == target:
                found.add((a[i], a[j], a[k], a[l]))
        return [list(t) for t in sorted(found)]

    # ------------------------------------------------------------------ references: graphs
    def cycle_undirected(n, edges):
        return len(edges) > n - components(n, edges)

    def cycle_directed(n, edges):
        indeg, adj = [0] * n, adj_of(n, edges, True)
        for _, v in edges:
            indeg[v] += 1
        queue, done = [u for u in range(n) if indeg[u] == 0], 0
        for u in queue:
            done += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)
        return done < n

    def topo_smallest(n, edges):
        indeg, adj = [0] * n, adj_of(n, edges, True)
        for _, v in edges:
            indeg[v] += 1
        heap = [u for u in range(n) if indeg[u] == 0]
        heapq.heapify(heap)
        order = []
        while heap:
            u = heapq.heappop(heap)
            order.append(u)
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    heapq.heappush(heap, v)
        return order

    def bfs_order(n, edges):
        adj = [sorted(a) for a in adj_of(n, edges, False)]
        seen, order, queue = {0}, [], deque([0])
        while queue:
            u = queue.popleft()
            order.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        return order

    def dfs_order(n, edges):
        adj = [sorted(a) for a in adj_of(n, edges, False)]
        seen, order = set(), []

        def go(u):
            seen.add(u)
            order.append(u)
            for v in adj[u]:
                if v not in seen:
                    go(v)
        go(0)
        return order

    def unit_distances(n, edges, src):
        adj = adj_of(n, edges, False)
        dist = [-1] * n
        dist[src] = 0
        queue = deque([src])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        return dist

    def dijkstra_ref(n, edges, src):  # relaxes everything until nothing changes (no heap, unlike the answer)
        dist = [None] * n
        dist[src] = 0
        changed = True
        while changed:
            changed = False
            for u, v, w in edges:
                for a, b in ((u, v), (v, u)):
                    if dist[a] is not None and (dist[b] is None or dist[a] + w < dist[b]):
                        dist[b] = dist[a] + w
                        changed = True
        return [-1 if d is None else d for d in dist]

    def bellman_ford(n, edges, src):
        dist = [INF] * n
        dist[src] = 0
        for _ in range(n - 1):
            for u, v, w in edges:
                if dist[u] != INF and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                return [-1]
        return dist

    def floyd(matrix):
        n = len(matrix)
        out = []
        for s in range(n):  # one Dijkstra per source (the answer uses Floyd-Warshall)
            dist = {s: 0}
            heap = [(0, s)]
            while heap:
                d, u = heapq.heappop(heap)
                if d > dist[u]:
                    continue
                for v in range(n):
                    if matrix[u][v] > 0 and (v not in dist or d + matrix[u][v] < dist[v]):
                        dist[v] = d + matrix[u][v]
                        heapq.heappush(heap, (dist[v], v))
            out.append([dist.get(v, -1) for v in range(n)])
        return out

    def mst_weight(n, edges):  # Prim; the answer uses Kruskal
        adj = [[] for _ in range(n)]
        for u, v, w in edges:
            adj[u].append((w, v))
            adj[v].append((w, u))
        seen, total, heap = set(), 0, [(0, 0)]
        while heap:
            w, u = heapq.heappop(heap)
            if u in seen:
                continue
            seen.add(u)
            total += w
            for item in adj[u]:
                heapq.heappush(heap, item)
        return total

    def safe_nodes(n, edges):
        reach = closure(n, edges)
        on_cycle = [u for u in range(n) if reach[u][u]]
        return [u for u in range(n) if not any(u == c or reach[u][c] for c in on_cycle)]

    def network_ops(n, edges):
        if len(edges) < n - 1:
            return -1
        return components(n, edges) - 1

    def scc_count(n, edges):
        reach = closure(n, edges)
        reps = set()
        for u in range(n):
            reps.add(min(v for v in range(n) if v == u or (reach[u][v] and reach[v][u])))
        return len(reps)

    def bridges(n, edges):
        base = components(n, edges)
        out = [sorted(e) for i, e in enumerate(edges) if components(n, edges, skip_edge=i) > base]
        return sorted(out)

    def articulation(n, edges):
        base = components(n, edges)
        out = [v for v in range(n) if components(n, edges, skip_node=v) > base]
        return out or [-1]

    # ------------------------------------------------------------------ references: trees
    def ceil_bst(t, key):
        return min([v for v in inorder_of(tok2tree(t), []) if v >= key], default=-1)

    def floor_bst(t, key):
        return max([v for v in inorder_of(tok2tree(t), []) if v <= key], default=-1)

    def successor(t, key):
        return min([v for v in inorder_of(tok2tree(t), []) if v > key], default=-1)

    def bst_from_preorder(nums):
        root = None
        for v in nums:
            root = bst_insert(root, v)
        return tree2tok(root)

    def two_sum_bst(t, k):
        vals = inorder_of(tok2tree(t), [])
        return any(k - v in vals for v in vals if k - v != v)

    def recover(t):
        root = tok2tree(t)
        fixed = iter(sorted(inorder_of(root, [])))

        def go(n):
            if n:
                go(n.left); n.val = next(fixed); go(n.right)
        go(root)
        return tree2tok(root)

    def largest_bst(t):
        root, best = tok2tree(t), 0

        def count(n):
            return 0 if not n else 1 + count(n.left) + count(n.right)

        def walk(n):
            nonlocal best
            if not n:
                return
            vals = inorder_of(n, [])
            if all(a < b for a, b in zip(vals, vals[1:])):
                best = max(best, len(vals))
            walk(n.left); walk(n.right)
        walk(root)
        return best

    def parents_of(t):
        root, parent, nodes = tok2tree(t), {}, {}
        stack = [root]
        while stack:
            n = stack.pop()
            nodes[n.val] = n
            for c in (n.left, n.right):
                if c:
                    parent[c.val] = n.val
                    stack.append(c)
        return nodes, parent

    def distances_from(t, start):
        nodes, parent = parents_of(t)
        dist, queue = {start: 0}, deque([start])
        while queue:
            u = queue.popleft()
            nbrs = [c.val for c in (nodes[u].left, nodes[u].right) if c] + ([parent[u]] if u in parent else [])
            for v in nbrs:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        return dist

    def burn_time(t, start):
        return max(distances_from(t, start).values())

    def at_distance(t, target, k):
        return sorted(v for v, d in distances_from(t, target).items() if d == k)

    # ------------------------------------------------------------------ cases
    def c_three_sum():
        out = [[-1, 0, 1, 2, -1, -4], [0, 0, 0], [0, 1, 1], [0, 0, 0, 0], [-2, 0, 1, 1, 2]]
        out += [arr(n, -8, 8) for n in [3, 4, 6, 9, 14, 25, 50, 100]]
        out += [arr(n, -300, 300) for n in [10, 40, 100]]
        return out

    def c_four_sum():
        out = [([1, 0, -1, 0, -2, 2], 0), ([2, 2, 2, 2, 2], 8), ([1, 2, 3, 4], 100)]
        for n in [4, 5, 7, 10, 16, 24, 40]:
            out.append((arr(n, -6, 6), rng.randint(-8, 8)))
        out += [(arr(n, -60, 60), rng.randint(-100, 100)) for n in [12, 30]]
        return out

    def c_undirected():
        out = [(3, [[0, 1], [1, 2]]), (3, [[0, 1], [1, 2], [2, 0]]), (1, []), (4, [[0, 1], [2, 3]])]
        for n in N_SMALL[2:]:
            t = tree_edges(n)
            out.append((n, t))
            keep = [e for e in t if rng.random() < 0.75]
            out.append((n, keep))
            if n >= 3:
                extra = [e for e in distinct_pairs(n, 3, False) if sorted(e) not in [sorted(x) for x in t]][:1]
                out.append((n, t + extra))
            out.append((n, distinct_pairs(n, rng.randint(0, 2 * n), False)))
        return out

    def c_directed():
        out = [(3, [[0, 1], [1, 2]]), (3, [[0, 1], [1, 2], [2, 0]]), (2, [[0, 1], [1, 0]]), (1, [])]
        for n in N_SMALL[2:]:
            dag = dag_edges(n, rng.randint(0, 2 * n))
            out.append((n, dag))
            out.append((n, dag + [list(reversed(rng.choice(dag)))] if dag else dag))
            out.append((n, distinct_pairs(n, rng.randint(0, 2 * n), True)))
        return out

    def c_dag():
        out = [(4, [[3, 0], [1, 0], [2, 0]]), (5, [[4, 0], [4, 1], [3, 1], [3, 2]]), (1, []), (3, [])]
        for n in N_SMALL[2:]:
            out.append((n, dag_edges(n, rng.randint(0, 2 * n))))
            out.append((n, dag_edges(n, n // 2)))
        return out

    def c_traversal():
        out = [(5, [[0, 1], [0, 2], [0, 3], [2, 4]]), (1, []), (4, [[1, 2], [2, 3]])]
        for n in N_SMALL[2:]:
            out.append((n, tree_edges(n)))
            out.append((n, distinct_pairs(n, rng.randint(0, 2 * n), False)))
        return out

    def c_unit_paths():
        out = [(6, [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4]], 0), (3, [[0, 1]], 2)]
        for n in N_SMALL[2:]:
            edges = distinct_pairs(n, rng.randint(n // 2, 2 * n), False)
            out.append((n, edges, rng.randrange(n)))
        return out

    def weighted(n, m, lo=1, hi=30, directed=False):
        return [e + [rng.randint(lo, hi)] for e in distinct_pairs(n, m, directed)]

    def c_dijkstra():
        out = [(5, [[0, 1, 2], [0, 2, 4], [1, 2, 1], [1, 3, 7], [2, 4, 3]], 0), (3, [[0, 1, 5]], 2)]
        for n in N_SMALL[2:]:
            out.append((n, weighted(n, rng.randint(n // 2, 3 * n)), rng.randrange(n)))
        return out

    def no_neg_cycle_edges(n, m):
        pot = [rng.randint(0, 12) for _ in range(n)]
        out = []
        for u, v in [tuple(e) for e in distinct_pairs(n, m, True)]:
            out.append([u, v, rng.randint(0, 9) + pot[u] - pot[v]])  # reweighting keeps every cycle non-negative
        return out

    def c_bellman():
        out = [(3, [[0, 1, 5], [1, 2, -3]], 0), (3, [[0, 1, 1], [1, 2, -3], [2, 0, 1]], 0), (3, [[1, 2, -4], [2, 1, 1]], 0)]
        for n in N_SMALL[2:]:
            out.append((n, no_neg_cycle_edges(n, rng.randint(n // 2, 3 * n)), rng.randrange(n)))
            out.append((n, weighted(n, rng.randint(n // 2, 3 * n), -4, 12, True), rng.randrange(n)))
        return out

    def c_floyd():
        out = [[[0, 4, -1], [-1, 0, 2], [3, -1, 0]], [[0]], [[0, -1], [-1, 0]]]
        for n in N_SMALL[2:]:
            m = [[0 if i == j else -1 for j in range(n)] for i in range(n)]
            for u, v in distinct_pairs(n, rng.randint(n, 3 * n), True):
                m[u][v] = rng.randint(1, 40)
            out.append(m)
        return out

    def c_mst():
        out = [(3, [[0, 1, 5], [1, 2, 3], [0, 2, 1]]), (2, [[0, 1, 9]])]
        for n in N_SMALL[2:]:
            if n < 2:
                continue
            edges = [e + [rng.randint(1, 60)] for e in tree_edges(n)]
            have = {tuple(sorted(e[:2])) for e in edges}
            for e in distinct_pairs(n, rng.randint(0, 2 * n), False):
                if tuple(sorted(e)) not in have:
                    edges.append(e + [rng.randint(1, 60)])
                    have.add(tuple(sorted(e)))
            rng.shuffle(edges)
            out.append((n, edges))
        return out

    def c_safe():
        out = [(7, [[1, 2], [2, 3], [5], [0], [5], [], []][0:0] or [[0, 1], [0, 2], [1, 2], [1, 3], [3, 4]]), (2, [[0, 1], [1, 0]]), (3, [])]
        for n in N_SMALL[2:]:
            out.append((n, distinct_pairs(n, rng.randint(n // 2, int(1.6 * n)), True)))
            out.append((n, dag_edges(n, rng.randint(1, n))))
        return out

    def c_network():
        out = [(4, [[0, 1], [0, 2], [1, 2]]), (6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]]), (6, [[0, 1], [0, 2], [0, 3], [1, 2]]), (1, [])]
        for n in N_SMALL[2:]:
            out.append((n, distinct_pairs(n, rng.randint(max(0, n - 3), n + 2), False)))
            out.append((n, distinct_pairs(n, n // 2, False)))
        return out

    def c_scc():
        out = [(5, [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4]]), (3, [[0, 1], [1, 2]]), (1, [])]
        for n in N_SMALL[2:]:
            out.append((n, distinct_pairs(n, rng.randint(n // 2, 2 * n), True)))
            out.append((n, distinct_pairs(n, n, True)))
        return out

    def c_bridges():
        out = [(4, [[0, 1], [1, 2], [2, 0], [1, 3]]), (2, [[0, 1]]), (3, [[0, 1], [1, 2], [2, 0]])]
        for n in [4, 6, 9, 14, 22]:
            t = tree_edges(n)
            out.append((n, t))
            out.append((n, t + [e for e in distinct_pairs(n, 3, False) if sorted(e) not in [sorted(x) for x in t]][:2]))
            out.append((n, distinct_pairs(n, rng.randint(n // 2, n + n // 2), False)))
        return out

    def c_articulation():
        out = [(5, [[0, 1], [1, 4], [2, 4], [2, 3], [3, 4]]), (2, [[0, 1]]), (4, [[0, 1], [1, 2], [2, 3], [3, 0]])]
        for n in [4, 6, 9, 14, 22]:
            t = tree_edges(n)
            out.append((n, t))
            out.append((n, t + [e for e in distinct_pairs(n, 4, False) if sorted(e) not in [sorted(x) for x in t]][:3]))
            out.append((n, distinct_pairs(n, rng.randint(n // 2, n + n // 2), False)))
        return out

    def bst_tokens(m):
        return tree2tok(random_bst(m))

    def c_bst_key():
        out = []
        for m in TREE_SIZES:
            t = bst_tokens(m)
            vals = inorder_of(tok2tree(t), [])
            out.append((t, rng.choice(vals)))
            out.append((t, rng.randint(0, 205)))
        out += [([8, 3, 10, 1, 6, None, 14], 5), ([8, 3, 10, 1, 6, None, 14], 14), ([8, 3, 10, 1, 6, None, 14], 0)]
        return out

    def c_successor():
        out = []
        for m in TREE_SIZES:
            t = bst_tokens(m)
            out.append((t, rng.choice(inorder_of(tok2tree(t), []))))
        out += [([5, 3, 6, 2, 4, None, None, 1], 6), ([5, 3, 6, 2, 4, None, None, 1], 4), ([2, 1, 3], 1)]
        return out

    def c_preorder_bst():
        out = [[8, 5, 1, 7, 10, 12], [3], [1, 2, 3, 4], [4, 3, 2, 1]]
        for m in TREE_SIZES[1:]:
            out.append(preorder_of(random_bst(m), []))
        return out

    def c_two_sum_bst():
        out = []
        for m in TREE_SIZES:
            t = bst_tokens(m)
            vals = inorder_of(tok2tree(t), [])
            if m > 1:
                out.append((t, rng.choice(vals) + rng.choice([v for v in vals])))
            out.append((t, rng.randint(2, 380)))
        out += [([5, 3, 6, 2, 4, None, 7], 9), ([5, 3, 6, 2, 4, None, 7], 28), ([2, 1, 3], 4), ([1], 2)]
        return out

    def c_recover():
        out = [[1, 3, None, None, 2], [3, 1, 4, None, None, 2]]
        for m in TREE_SIZES[1:]:
            root = random_bst(m)
            nodes = [n for lvl in levels(root) for n in lvl]
            a, b = rng.sample(nodes, 2)
            a.val, b.val = b.val, a.val
            out.append(tree2tok(root))
        return out

    def c_largest_bst():
        out = [[10, 5, 15, 1, 8, None, 7], [5, 4, 6, None, 3, 7, 8], [1], [2, 1, 3]]
        for m in TREE_SIZES[1:]:
            out.append(rand_tree(m, 0, 25))
            root = random_bst(m, 1, 120)
            nodes = [n for lvl in levels(root) for n in lvl]
            rng.choice(nodes).val = rng.randint(1, 120)
            out.append(tree2tok(root))
        return out

    def c_burn():
        out = [([1, 5, 3, None, 4, 10, 6, 9, 2], 3), ([1], 1)]
        for m in TREE_SIZES[1:]:
            t = distinct_tree(m)
            out.append((t, rng.choice([v for v in t if v is not None])))
        return out

    def c_dist_k():
        out = [([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 2), ([1], 1, 3)]
        for m in TREE_SIZES[1:]:
            t = distinct_tree(m)
            out.append((t, rng.choice([v for v in t if v is not None]), rng.randint(0, 5)))
        return out

    # ------------------------------------------------------------------ statements
    GRAPH_IN = "Line 1: `n`, the number of nodes (labelled `0` to `n - 1`).\nLine 2: `m`, the number of edges.\nNext `m` lines: `u v`."
    GRAPH_IN = "Line 1: `n`, the number of nodes (labelled `0` to `n - 1`).\nLine 2: `m`, the number of edges.\nNext `m` lines: two integers `u v`."
    WGRAPH_IN = "Line 1: `n`, the number of nodes (labelled `0` to `n - 1`).\nLine 2: `m`, the number of edges.\nNext `m` lines: three integers `u v w`."
    SRC = "\nLast line: `src`, the start node."
    NODES = "`0 <= n <= 100` nodes"
    ARR = "Line 1: `n`.\nLine 2: `n` space-separated integers."
    SIMPLE = "No self-loops and no repeated edges"
    VAL = "`-100 <= val <= 100`"
    BST_NOTE = "all values are distinct"

    return [
        mk("three-sum", "3Sum", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]")], "int[][]", three_sum, c_three_sum(),
           "Return every unique triplet `[a, b, c]` of values from `nums` (taken from three different positions) with `a + b + c = 0`. Write each triplet "
           "in ascending order and list the triplets in ascending order too (compared value by value). The answer must not contain duplicate triplets.",
           ARR, "One triplet per line, as three space-separated integers (a blank line when there is none).",
           ["`3 <= n <= 100`", "`-300 <= nums[i] <= 300`"]),
        mk("four-sum", "4Sum", "MEDIUM", ["array", "two-pointers", "sorting"], [("nums", "int[]"), ("target", "int")], "int[][]", four_sum, c_four_sum(),
           "Return every unique quadruplet `[a, b, c, d]` of values from `nums` (taken from four different positions) with `a + b + c + d = target`. Write each "
           "quadruplet in ascending order and list the quadruplets in ascending order too (compared value by value). The answer must not contain duplicates.",
           "Line 1: `n`.\nLine 2: `n` integers.\nLine 3: `target`.", "One quadruplet per line (a blank line when there is none).",
           ["`4 <= n <= 40`", "`-60 <= nums[i] <= 60`", "`-100 <= target <= 100`"]),
        mk("detect-cycle-in-an-undirected-graph", "Detect Cycle in an Undirected Graph", "MEDIUM", ["graph", "dfs", "union-find"],
           [("n", "int"), ("edges", "int[][]")], "bool", cycle_undirected, c_undirected(),
           "An undirected graph has `n` nodes and the given edges. The graph may be disconnected. Return `true` if it contains a cycle.",
           GRAPH_IN, "`true` or `false`.", ["`1 <= n <= 35`", SIMPLE]),
        mk("detect-cycle-in-a-directed-graph", "Detect Cycle in a Directed Graph", "MEDIUM", ["graph", "dfs", "topological-sort"],
           [("n", "int"), ("edges", "int[][]")], "bool", cycle_directed, c_directed(),
           "A directed graph has `n` nodes and edges `u -> v`. Return `true` if it contains a directed cycle.",
           GRAPH_IN, "`true` or `false`.", ["`1 <= n <= 35`", "No self-loops and no repeated edges (`u -> v` and `v -> u` may both appear)"]),
        mk("topological-sort", "Topological Sort", "MEDIUM", ["graph", "topological-sort", "bfs", "heap"], [("n", "int"), ("edges", "int[][]")], "int[]", topo_smallest,
           c_dag(),
           "A directed acyclic graph has `n` nodes and edges `u -> v`, meaning `u` must come before `v`. Many orders can be valid, so return the "
           "**lexicographically smallest** topological order (when several nodes are available, always take the smallest label).",
           GRAPH_IN, "The `n` nodes in that order, space separated.", ["`1 <= n <= 35`", "The graph is acyclic", SIMPLE]),
        mk("bfs-of-graph", "BFS of Graph", "EASY", ["graph", "bfs"], [("n", "int"), ("edges", "int[][]")], "int[]", bfs_order, c_traversal(),
           "An undirected graph is given. Run a breadth-first search from node `0`, always visiting the neighbours of a node in ascending label order. "
           "Return the nodes in the order they are visited (only the nodes reachable from `0`).",
           GRAPH_IN, "The visited nodes, space separated.", ["`1 <= n <= 35`", SIMPLE]),
        mk("dfs-of-graph", "DFS of Graph", "EASY", ["graph", "dfs"], [("n", "int"), ("edges", "int[][]")], "int[]", dfs_order, c_traversal(),
           "An undirected graph is given. Run a depth-first search from node `0`, always trying the neighbours of a node in ascending label order. "
           "Return the nodes in the order they are first visited (only the nodes reachable from `0`).",
           GRAPH_IN, "The visited nodes, space separated.", ["`1 <= n <= 35`", SIMPLE]),
        mk("shortest-path-in-undirected-graph", "Shortest Path in Undirected Graph (Unit Weights)", "MEDIUM", ["graph", "bfs"],
           [("n", "int"), ("edges", "int[][]"), ("src", "int")], "int[]", unit_distances, c_unit_paths(),
           "Every edge of an undirected graph has length 1. Return, for every node, the length of the shortest path from `src`, or `-1` when the node cannot be reached.",
           GRAPH_IN + SRC, "`n` integers: the distance to nodes `0 .. n - 1`.", ["`1 <= n <= 35`", SIMPLE]),
        mk("dijkstra-algorithm", "Dijkstra's Algorithm", "MEDIUM", ["graph", "heap", "shortest-path"], [("n", "int"), ("edges", "int[][]"), ("src", "int")], "int[]",
           dijkstra_ref, c_dijkstra(),
           "An undirected graph has positive edge weights. Return, for every node, the length of the shortest path from `src`, or `-1` when it cannot be reached.",
           WGRAPH_IN + SRC, "`n` integers: the shortest distance to nodes `0 .. n - 1`.", ["`1 <= n <= 35`", "`1 <= w <= 30`", SIMPLE]),
        mk("bellman-ford-algorithm", "Bellman-Ford Algorithm", "MEDIUM", ["graph", "dynamic-programming", "shortest-path"],
           [("n", "int"), ("edges", "int[][]"), ("src", "int")], "int[]", bellman_ford, c_bellman(),
           "A directed graph may have negative edge weights. If a negative cycle can be reached from `src`, return the single value `-1`. Otherwise return "
           "the shortest distance from `src` to every node, using `100000000` for nodes that cannot be reached.",
           "Line 1: `n`.\nLine 2: `m`.\nNext `m` lines: `u v w` for a directed edge `u -> v` of weight `w`.\nLast line: `src`.",
           "Either the single value `-1`, or `n` distances separated by spaces.", ["`1 <= n <= 35`", "`-4 <= w <= 30`"]),
        mk("floyd-warshall", "Floyd Warshall", "MEDIUM", ["graph", "dynamic-programming", "shortest-path"], [("matrix", "int[][]")], "int[][]", floyd, c_floyd(),
           "A directed graph is given as an `n x n` matrix where `matrix[i][j]` is the weight of the edge `i -> j`, or `-1` when there is no such edge "
           "(`matrix[i][i] = 0`). Return the matrix of shortest distances between every pair of nodes, using `-1` where no path exists.",
           "Line 1: `n`.\nNext `n` lines: the rows of the matrix.", "`n` lines: the shortest-distance matrix.", ["`1 <= n <= 35`", "`1 <= weight <= 40` for real edges"]),
        mk("minimum-spanning-tree", "Minimum Spanning Tree", "MEDIUM", ["graph", "union-find", "greedy", "heap"], [("n", "int"), ("edges", "int[][]")], "int", mst_weight,
           c_mst(),
           "A connected, undirected, weighted graph is given. Return the total weight of its minimum spanning tree (Kruskal's or Prim's algorithm).",
           WGRAPH_IN, "The total weight of the MST.", ["`2 <= n <= 35`", "`1 <= w <= 60`", "The graph is connected", SIMPLE]),
        mk("eventual-safe-states", "Find Eventual Safe States", "MEDIUM", ["graph", "dfs", "topological-sort"], [("n", "int"), ("edges", "int[][]")], "int[]", safe_nodes,
           c_safe(),
           "In a directed graph a node is **terminal** when it has no outgoing edge and **safe** when every path starting from it ends in a terminal node. "
           "Return all safe nodes in ascending order.", GRAPH_IN, "The safe nodes in ascending order, space separated (a blank line when there are none).",
           ["`1 <= n <= 35`", "No self-loops and no repeated edges"]),
        mk("number-of-operations-to-make-network-connected", "Number of Operations to Make Network Connected", "MEDIUM", ["graph", "union-find", "dfs"],
           [("n", "int"), ("connections", "int[][]")], "int", network_ops, c_network(),
           "`n` computers are joined by the given cables. In one operation you can unplug a cable and plug it between any two computers. Return the minimum "
           "number of operations that makes every computer connected, or `-1` when it is impossible.",
           "Line 1: `n`.\nLine 2: `m`, the number of cables.\nNext `m` lines: `u v`.", "The minimum number of operations, or `-1`.", ["`1 <= n <= 35`", SIMPLE]),
        mk("strongly-connected-components-kosaraju", "Strongly Connected Components (Kosaraju's Algorithm)", "HARD", ["graph", "dfs"],
           [("n", "int"), ("edges", "int[][]")], "int", scc_count, c_scc(),
           "In a directed graph, two nodes are in the same strongly connected component when each can reach the other. Return the number of strongly connected components.",
           GRAPH_IN, "The number of strongly connected components.", ["`1 <= n <= 35`", "No self-loops and no repeated edges"]),
        mk("critical-connections-in-a-network", "Bridges in a Graph (Critical Connections)", "HARD", ["graph", "dfs"], [("n", "int"), ("edges", "int[][]")], "int[][]", bridges,
           c_bridges(),
           "A bridge is an edge whose removal increases the number of connected components. Return every bridge of the undirected graph as `u v` with `u < v`, "
           "sorted in ascending order.", GRAPH_IN, "One bridge per line (a blank line when there is none).", ["`2 <= n <= 25`", SIMPLE]),
        mk("articulation-point-in-graph", "Articulation Point in a Graph", "HARD", ["graph", "dfs"], [("n", "int"), ("edges", "int[][]")], "int[]", articulation,
           c_articulation(),
           "An articulation point is a node whose removal (together with its edges) increases the number of connected components. Return all articulation "
           "points of the undirected graph in ascending order, or the single value `-1` when there are none.",
           GRAPH_IN, "The articulation points in ascending order, space separated, or `-1`.", ["`2 <= n <= 25`", SIMPLE]),
        mk("ceil-in-a-bst", "Ceil in a BST", "MEDIUM", ["tree", "bst"], [("root", "tree"), ("key", "int")], "int", ceil_bst, c_bst_key(),
           "Given a binary search tree and a `key`, return the smallest value in the tree that is greater than or equal to `key`, or `-1` if there is none.",
           "Line 1: `n`, the number of tokens.\nLine 2: the BST in level order (`null` for a missing child).\nLine 3: `key`.", "The ceil, or `-1`.",
           ["`1 <= n <= 100` nodes", "`1 <= val <= 200`, " + BST_NOTE, "`0 <= key <= 205`"]),
        mk("floor-in-a-bst", "Floor in a BST", "MEDIUM", ["tree", "bst"], [("root", "tree"), ("key", "int")], "int", floor_bst, c_bst_key(),
           "Given a binary search tree and a `key`, return the largest value in the tree that is less than or equal to `key`, or `-1` if there is none.",
           "Line 1: `n`, the number of tokens.\nLine 2: the BST in level order (`null` for a missing child).\nLine 3: `key`.", "The floor, or `-1`.",
           ["`1 <= n <= 100` nodes", "`1 <= val <= 200`, " + BST_NOTE, "`0 <= key <= 205`"]),
        mk("inorder-successor-in-bst", "Inorder Successor in BST", "MEDIUM", ["tree", "bst"], [("root", "tree"), ("key", "int")], "int", successor, c_successor(),
           "Given a binary search tree and the value `key` of one of its nodes, return the value of that node's inorder successor (the next larger value in the "
           "tree), or `-1` if the node holds the largest value. Aim for `O(h)`.",
           "Line 1: `n`, the number of tokens.\nLine 2: the BST in level order (`null` for a missing child).\nLine 3: `key`, a value that exists in the tree.",
           "The successor's value, or `-1`.", ["`1 <= n <= 100` nodes", "`1 <= val <= 200`, " + BST_NOTE]),
        mk("construct-binary-search-tree-from-preorder-traversal", "Construct Binary Search Tree from Preorder Traversal", "MEDIUM", ["tree", "bst", "stack"],
           [("preorder", "int[]")], "tree", bst_from_preorder, c_preorder_bst(),
           "Given the preorder traversal of a binary search tree with distinct values, rebuild the tree and return its root. Aim for `O(n)`.",
           ARR, "The tree in level order (`null` for a missing child, trailing `null`s omitted).", ["`1 <= n <= 80`", "`1 <= val <= 200`, " + BST_NOTE]),
        mk("two-sum-iv-input-is-a-bst", "Two Sum IV - Input is a BST", "EASY", ["tree", "bst", "two-pointers"], [("root", "tree"), ("k", "int")], "bool", two_sum_bst,
           c_two_sum_bst(),
           "Given a binary search tree and an integer `k`, return `true` if two **different** nodes hold values that add up to `k`.",
           "Line 1: `n`, the number of tokens.\nLine 2: the BST in level order (`null` for a missing child).\nLine 3: `k`.", "`true` or `false`.",
           ["`1 <= n <= 100` nodes", "`1 <= val <= 200`, " + BST_NOTE, "`2 <= k <= 380`"]),
        mk("recover-binary-search-tree", "Recover Binary Search Tree", "MEDIUM", ["tree", "bst", "dfs"], [("root", "tree")], "tree", recover, c_recover(),
           "The values of exactly two nodes of a binary search tree were swapped by mistake. Recover the tree without changing its structure and return the root. "
           "(`O(1)` extra space is possible with a Morris traversal.)",
           TREE_IN, "The repaired tree in level order.", ["`2 <= n <= 80` nodes", "`1 <= val <= 200`, " + BST_NOTE]),
        mk("largest-bst-subtree", "Largest BST Subtree", "HARD", ["tree", "bst", "dfs"], [("root", "tree")], "int", largest_bst, c_largest_bst(),
           "Return the number of nodes of the largest subtree of the given binary tree that is itself a valid binary search tree (every left value strictly smaller "
           "and every right value strictly larger than the node, all the way down). Duplicate values may appear in the tree.",
           TREE_IN, "The size of the largest BST subtree.", ["`1 <= n <= 100` nodes", "`0 <= val <= 120`"]),
        mk("amount-of-time-for-binary-tree-to-be-infected", "Minimum Time to Burn a Binary Tree", "MEDIUM", ["tree", "bfs", "hash-table"],
           [("root", "tree"), ("start", "int")], "int", burn_time, c_burn(),
           "At minute 0 the node with value `start` catches fire. Every minute the fire spreads from a burning node to its parent and to its children. "
           "Return how many minutes it takes for the whole tree to burn.",
           "Line 1: `n`, the number of tokens.\nLine 2: the tree in level order (`null` for a missing child).\nLine 3: `start`, a value that exists in the tree.",
           "The number of minutes.", ["`1 <= n <= 100` nodes", "`1 <= val <= 300`, all distinct"]),
        mk("all-nodes-distance-k-in-binary-tree", "All Nodes Distance K in Binary Tree", "MEDIUM", ["tree", "bfs", "hash-table"],
           [("root", "tree"), ("target", "int"), ("k", "int")], "int[]", at_distance, c_dist_k(),
           "Return the values of all nodes that are exactly `k` edges away from the node whose value is `target` (moving to a parent or to a child counts as one edge). "
           "List the values in ascending order.",
           "Line 1: `n`, the number of tokens.\nLine 2: the tree in level order (`null` for a missing child).\nLine 3: `target`, a value that exists in the tree.\nLine 4: `k`.",
           "The values, ascending and space separated (a blank line when there are none).", ["`1 <= n <= 100` nodes", "`0 <= val <= 300`, all distinct", "`0 <= k <= 5`"]),
    ]
