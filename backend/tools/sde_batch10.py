"""Striver SDE sheet batch 10: Pow(x, n) (decimal output) and the pointer-style linked-list problems.

Linked-list cycles and shared tails cannot be written as plain value lists, so the generator has special parameter kinds:
  cyclelist  - "n / values / pos": a list whose last node links back to node `pos` (-1 = no cycle)
  xlistA/B   - two lists that share their last `k` nodes (the same node objects, not just equal values)
  node       - the returned node is printed as its position (list order; list A's nodes first, then list B's own nodes), -1 for none
"""


def make_batch(mk, rng):
    arr = lambda n, lo, hi: [rng.randint(lo, hi) for _ in range(n)]

    # ------------------------------------------------------------------ references
    def power(x, n):
        return x ** n

    def has_cycle(cl):
        vals, loop = cl
        return bool(vals) and loop >= 0

    def cycle_start(cl):
        vals, loop = cl
        return loop if vals and loop >= 0 else -1

    def cycle_length(cl):
        vals, loop = cl
        return len(vals) - loop if vals and loop >= 0 else 0

    def intersection(a_arg, _b_arg):
        a, b, k = a_arg
        return len(a) - k if k > 0 else -1

    # ------------------------------------------------------------------ cases
    def tie_safe(x, n):
        """Skip results whose 5th decimal sits on a rounding tie: languages round exact ties differently."""
        try:
            r = x ** n
        except (OverflowError, ZeroDivisionError):
            return False
        if abs(r) > 1e6:
            return False
        scaled = abs(r) * 1e5
        return abs((scaled - int(scaled)) - 0.5) > 0.01

    def c_power():
        cases = [(2.0, 10), (2.1, 3), (2.0, -2), (1.0, 2147483647), (-1.0, 2147483647), (-1.0, -2147483648), (0.5, 8), (3.0, 0), (-2.0, 3),
                 (2.0, -2147483648), (0.0, 5), (1.00001, 100000), (0.99999, 100000), (-2.0, 10), (10.0, -3), (1.5, 6), (-0.5, 5), (2.0, 20)]
        cases = [c for c in cases if tie_safe(*c)]
        while len(cases) < 28:
            x, n = round(rng.uniform(-3, 3), 5), rng.randint(-12, 12)
            if x == 0.0 and n < 0:
                continue
            if tie_safe(x, n):
                cases.append((x, n))
        return cases

    def cyc(n, hi, loop):
        return ((arr(n, 0, hi), loop),)

    def c_cycle():
        cases = [(([3, 2, 0, -4], 1),), (([1, 2], 0),), (([1], -1),), (([], -1),), (([1], 0),), (([1, 2, 3, 4, 5], -1),), (([1, 1, 1, 1], 3),)]
        for n, hi in ((6, 9), (15, 50), (40, 100), (100, 100), (500, 1000), (1000, 1000)):
            cases.append(cyc(n, hi, rng.choice([-1, rng.randint(0, n - 1), 0, n - 1])))
        # make sure both answers show up among the larger cases
        cases.append(cyc(300, 5, -1))
        cases.append(cyc(300, 5, 150))
        return cases

    def c_cycle_pos():
        # every case here has a cycle for the "start" and "length" problems except a couple of no-cycle checks
        cases = [(([3, 2, 0, -4], 1),), (([1, 2], 0),), (([1], -1),), (([1], 0),), (([1, 2, 3], 2),), (([5, 5, 5, 5, 5], 2),), (([1, 2, 3, 4, 5], -1),)]
        for n, hi in ((7, 9), (20, 50), (50, 100), (120, 100), (400, 1000), (1000, 1000)):
            cases.append(cyc(n, hi, rng.randint(0, n - 1)))
        cases.append(cyc(500, 3, 0))
        cases.append(cyc(500, 3, 499))
        cases.append(cyc(500, 3, -1))
        return cases

    def shared(a_pre, b_pre, tail):
        return ((a_pre + tail, b_pre + tail, len(tail)), None)

    def c_intersection():
        cases = [shared([4, 1], [5, 6, 1], [8, 4, 5]), shared([1, 9, 1], [3], [2, 4]), (([2, 6, 4], [1, 5], 0), None), (([1], [1], 0), None),
                 shared([], [], [7]), shared([], [1, 2], [3, 4]), shared([1, 2], [], [3]), shared([5, 5], [5], [5, 5, 5]),
                 (([1, 2, 3], [1, 2, 3], 0), None), shared([7], [7], [1, 2, 3, 4, 5, 6])]
        for na, nb, nt in ((5, 7, 4), (20, 15, 10), (50, 80, 30), (150, 100, 120), (300, 300, 1), (400, 10, 500)):
            tail = arr(nt, 0, 9)
            cases.append(shared(arr(na, 0, 9), arr(nb, 0, 9), tail))
        # same values but separate nodes: a value comparison would wrongly report an intersection
        v = arr(30, 0, 3)
        cases.append(((v, v[:], 0), None))
        cases.append(((arr(60, 0, 2), arr(45, 0, 2), 0), None))
        return cases

    CL = "Line 1: `n`, the number of nodes.\nLine 2: the `n` node values.\nLine 3: `pos`, the index of the node that the last node points back to, or `-1` if there is no cycle."
    CYC_CONS = ["`0 <= n <= 1000`", "`-1000 <= value <= 1000`", "`pos` is `-1` or a valid index"]
    return [
        mk("pow-x-n", "Pow(x, n)", "MEDIUM", ["math", "binary-search"], [("x", "double"), ("n", "int")], "double", power, c_power(),
           "Return `x` raised to the power `n`. The result is printed rounded to 5 decimal places, so a small floating point error is fine. "
           "Aim for `O(log n)` multiplications.",
           "Line 1: `x` with 5 decimals.\nLine 2: `n`.", "`x^n` with exactly 5 decimals.",
           ["`-100.0 < x < 100.0`", "`-2^31 <= n <= 2^31 - 1`", "`x` is not `0` when `n` is negative", "The result fits in `[-10^6, 10^6]`"]),
        mk("linked-list-cycle", "Linked List Cycle", "EASY", ["linked-list", "two-pointers"], [("head", "cyclelist")], "bool", has_cycle, c_cycle(),
           "Return `true` if the linked list has a cycle, meaning some node can be reached again by following `next` pointers. "
           "The input gives the node values and `pos`, the index the last node's `next` points to (`-1` means no cycle). Try it in `O(1)` extra space.",
           CL, "`true` or `false`.", CYC_CONS),
        mk("starting-point-of-loop-in-a-linked-list", "Starting Point of Loop in a Linked List", "MEDIUM", ["linked-list", "two-pointers"], [("head", "cyclelist")], "node",
           cycle_start, c_cycle_pos(),
           "Return the node where the cycle begins, or `null` if there is no cycle. The result is printed as the node's **index in the list** "
           "(`0` is the head), or `-1` for `null`. Do not change the list.",
           CL, "The index of the node where the cycle starts, or `-1`.", CYC_CONS),
        mk("length-of-loop-in-a-linked-list", "Length of Loop in a Linked List", "MEDIUM", ["linked-list", "two-pointers"], [("head", "cyclelist")], "int",
           cycle_length, c_cycle_pos(),
           "Return the number of nodes inside the cycle, or `0` if the list has no cycle.", CL, "The number of nodes in the cycle, or `0`.", CYC_CONS),
        mk("intersection-of-two-linked-lists", "Intersection of Two Linked Lists", "EASY", ["linked-list", "two-pointers"],
           [("headA", "xlistA"), ("headB", "xlistB")], "node", intersection, c_intersection(),
           "Two singly linked lists may merge into the same nodes (a shared tail); equal **values** do not mean the same **node**. Return the node where "
           "they first meet, or `null` if they never do. The result is printed as that node's **index in list A** (`0` is its head), or `-1` for `null`. "
           "Do not change the lists. Try `O(n + m)` time and `O(1)` extra space.",
           "Line 1: `n`, the length of list A.\nLine 2: the `n` values of list A.\nLine 3: `m`, the length of list B.\nLine 4: the `m` values of list B.\n"
           "Line 5: `k`, how many nodes at the end of both lists are shared (`0` means the lists never meet).",
           "The index in list A of the first shared node, or `-1`.",
           ["`0 <= n, m <= 1000`", "`0 <= k <= min(n, m)`", "The last `k` values of both lists are the same nodes"]),
    ]
