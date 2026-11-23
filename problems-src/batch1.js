// Batch 1: original statements, tests, editorials and solutions (Python / C++ / Java).
// Materialize with: node scripts/materialize.js problems-src/batch1.js
const P = (n, params, returns, extra = {}) => ({ name: n, params, returns, ...extra });
const nums = (name = "nums") => ({ name, type: "int[]" });

module.exports = [
  {
    id: 2, slug: "add-two-numbers", title: "Add Two Numbers", difficulty: "Medium", tags: ["Linked List", "Math"],
    statement: "Two non-empty linked lists hold non-negative integers, one digit per node, with the **least significant digit first**. Add the two numbers and return the sum as a linked list in the same format.\n\nNeither number has leading zeros, except the number 0 itself.",
    constraints: ["Each list has between `1` and `100` nodes.", "`0 <= Node.val <= 9`"],
    signature: P("addTwoNumbers", [{ name: "l1", type: "ListNode" }, { name: "l2", type: "ListNode" }], "ListNode"),
    examples: [{ input: { l1: [2, 4, 3], l2: [5, 6, 4] }, output: [7, 0, 8], explanation: "342 + 465 = 807." }, { input: { l1: [9, 9, 9, 9], l2: [1] }, output: [0, 0, 0, 0, 1] }],
    hints: ["Simulate schoolbook addition and carry a digit forward.", "A dummy head node removes special cases for the first node."],
    tests: [{ l1: [2, 4, 3], l2: [5, 6, 4] }, { l1: [0], l2: [0] }, { l1: [9, 9, 9, 9, 9, 9, 9], l2: [9, 9, 9, 9] }, { l1: [1], l2: [9, 9] }, { l1: [5], l2: [5] }, { l1: [1, 8], l2: [0] }],
    editorial: "## Approach: digit-by-digit simulation\n\nWalk both lists together, summing the two digits plus the carry. Append `sum % 10` to the result and carry `sum / 10`. Continue while either list or the carry is non-zero.\n\nA dummy head avoids special-casing the first node.\n\n**Complexity:** O(max(m, n)) time, O(1) extra space beyond the output.",
    py: `class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)
        cur, carry = dummy, 0
        while l1 or l2 or carry:
            s = carry
            if l1:
                s += l1.val
                l1 = l1.next
            if l2:
                s += l2.val
                l2 = l2.next
            carry, d = divmod(s, 10)
            cur.next = ListNode(d)
            cur = cur.next
        return dummy.next
`,
    cpp: `class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        ListNode dummy(0);
        ListNode* cur = &dummy;
        int carry = 0;
        while (l1 || l2 || carry) {
            int s = carry;
            if (l1) { s += l1->val; l1 = l1->next; }
            if (l2) { s += l2->val; l2 = l2->next; }
            carry = s / 10;
            cur->next = new ListNode(s % 10);
            cur = cur->next;
        }
        return dummy.next;
    }
};
`,
    java: `class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0), cur = dummy;
        int carry = 0;
        while (l1 != null || l2 != null || carry != 0) {
            int s = carry;
            if (l1 != null) { s += l1.val; l1 = l1.next; }
            if (l2 != null) { s += l2.val; l2 = l2.next; }
            carry = s / 10;
            cur.next = new ListNode(s % 10);
            cur = cur.next;
        }
        return dummy.next;
    }
}
`,
  },
  {
    id: 9, slug: "palindrome-number", title: "Palindrome Number", difficulty: "Easy", tags: ["Math"],
    statement: "Return `true` if the integer `x` reads the same forwards and backwards, otherwise `false`.\n\nNegative numbers are never palindromes. Try to solve it without converting the integer to a string.",
    constraints: ["`-2^31 <= x <= 2^31 - 1`"],
    signature: P("isPalindrome", [{ name: "x", type: "int" }], "bool"),
    examples: [{ input: { x: 121 }, output: true }, { input: { x: -121 }, output: false, explanation: "Reads 121- from right to left." }, { input: { x: 10 }, output: false }],
    hints: ["Reverse only half of the number and compare with the other half."],
    tests: [{ x: 121 }, { x: -121 }, { x: 10 }, { x: 0 }, { x: 7 }, { x: 1221 }, { x: 12321 }, { x: 1000021 }, { x: 2147447412 }, { x: 2147483647 }],
    editorial: "## Approach: reverse half the digits\n\nNegative numbers and numbers ending in 0 (other than 0) cannot be palindromes. Otherwise peel digits off the end into `rev` until `rev >= x`; now `rev` holds the reversed second half. The number is a palindrome if `x == rev` (even length) or `x == rev / 10` (odd length).\n\nHalf-reversing also sidesteps integer overflow.\n\n**Complexity:** O(log₁₀ n) time, O(1) space.",
    py: `class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0 or (x % 10 == 0 and x != 0):
            return False
        rev = 0
        while x > rev:
            rev = rev * 10 + x % 10
            x //= 10
        return x == rev or x == rev // 10
`,
    cpp: `class Solution {
public:
    bool isPalindrome(int x) {
        if (x < 0 || (x % 10 == 0 && x != 0)) return false;
        int rev = 0;
        while (x > rev) {
            rev = rev * 10 + x % 10;
            x /= 10;
        }
        return x == rev || x == rev / 10;
    }
};
`,
    java: `class Solution {
    public boolean isPalindrome(int x) {
        if (x < 0 || (x % 10 == 0 && x != 0)) return false;
        int rev = 0;
        while (x > rev) {
            rev = rev * 10 + x % 10;
            x /= 10;
        }
        return x == rev || x == rev / 10;
    }
}
`,
  },
  {
    id: 20, slug: "valid-parentheses", title: "Valid Parentheses", difficulty: "Easy", tags: ["String", "Stack"],
    statement: "A string `s` contains only the characters `(`, `)`, `{`, `}`, `[` and `]`. Decide whether it is valid.\n\nA string is valid when every opening bracket is closed by the same type of bracket, and brackets close in the correct order.",
    constraints: ["`1 <= s.length <= 10^4`", "`s` consists only of the six bracket characters."],
    signature: P("isValid", [{ name: "s", type: "string" }], "bool"),
    examples: [{ input: { s: "()[]{}" }, output: true }, { input: { s: "(]" }, output: false }, { input: { s: "([{}])" }, output: true }],
    hints: ["The most recently opened bracket must be the first one closed."],
    tests: [{ s: "()" }, { s: "()[]{}" }, { s: "(]" }, { s: "([)]" }, { s: "{[]}" }, { s: "(" }, { s: ")" }, { s: "((((((((((" }, { s: "([{}])" }, { s: "(" .repeat(5000) + ")".repeat(5000) }],
    editorial: "## Approach: stack\n\nPush every opening bracket. On a closing bracket, the stack must be non-empty and its top must be the matching opener; pop it. At the end the stack must be empty.\n\n**Complexity:** O(n) time, O(n) space.",
    py: `class Solution:
    def isValid(self, s: str) -> bool:
        pair = {')': '(', ']': '[', '}': '{'}
        st = []
        for c in s:
            if c in pair:
                if not st or st.pop() != pair[c]:
                    return False
            else:
                st.append(c)
        return not st
`,
    cpp: `class Solution {
public:
    bool isValid(string s) {
        string st;
        for (char c : s) {
            if (c == '(' || c == '[' || c == '{') st.push_back(c);
            else {
                if (st.empty()) return false;
                char o = st.back();
                st.pop_back();
                if ((c == ')' && o != '(') || (c == ']' && o != '[') || (c == '}' && o != '{')) return false;
            }
        }
        return st.empty();
    }
};
`,
    java: `class Solution {
    public boolean isValid(String s) {
        Deque<Character> st = new ArrayDeque<>();
        for (char c : s.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') st.push(c);
            else {
                if (st.isEmpty()) return false;
                char o = st.pop();
                if ((c == ')' && o != '(') || (c == ']' && o != '[') || (c == '}' && o != '{')) return false;
            }
        }
        return st.isEmpty();
    }
}
`,
  },
  {
    id: 53, slug: "maximum-subarray", title: "Maximum Subarray", difficulty: "Medium", tags: ["Array", "Dynamic Programming", "Divide and Conquer"],
    statement: "Given an integer array `nums`, find the contiguous non-empty subarray with the largest sum and return that sum.",
    constraints: ["`1 <= nums.length <= 10^5`", "`-10^4 <= nums[i] <= 10^4`"],
    signature: P("maxSubArray", [nums()], "int"),
    examples: [{ input: { nums: [-2, 1, -3, 4, -1, 2, 1, -5, 4] }, output: 6, explanation: "The subarray [4, -1, 2, 1] has sum 6." }, { input: { nums: [5, 4, -1, 7, 8] }, output: 23 }],
    hints: ["Let best[i] be the best sum of a subarray ending at i. How does it relate to best[i-1]?"],
    tests: [{ nums: [-2, 1, -3, 4, -1, 2, 1, -5, 4] }, { nums: [1] }, { nums: [5, 4, -1, 7, 8] }, { nums: [-1] }, { nums: [-3, -2, -5] }, { nums: [0, 0, 0] }, { nums: Array.from({ length: 100000 }, (_, i) => (i % 7) - 3) }],
    editorial: "## Approach: Kadane's algorithm\n\nKeep `cur`, the best sum of a subarray ending at the current element: `cur = max(x, cur + x)`. Track the maximum `cur` seen.\n\nIf the running sum becomes worse than starting fresh at `x`, restarting is always better.\n\n**Complexity:** O(n) time, O(1) space.",
    py: `class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        cur = best = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best
`,
    cpp: `class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        int cur = nums[0], best = nums[0];
        for (size_t i = 1; i < nums.size(); i++) {
            cur = max(nums[i], cur + nums[i]);
            best = max(best, cur);
        }
        return best;
    }
};
`,
    java: `class Solution {
    public int maxSubArray(int[] nums) {
        int cur = nums[0], best = nums[0];
        for (int i = 1; i < nums.length; i++) {
            cur = Math.max(nums[i], cur + nums[i]);
            best = Math.max(best, cur);
        }
        return best;
    }
}
`,
  },
  {
    id: 70, slug: "climbing-stairs", title: "Climbing Stairs", difficulty: "Easy", tags: ["Math", "Dynamic Programming"],
    statement: "You are climbing a staircase with `n` steps. Each move climbs either `1` or `2` steps. Return the number of distinct ways to reach the top.",
    constraints: ["`1 <= n <= 45`"],
    signature: P("climbStairs", [{ name: "n", type: "int" }], "int"),
    examples: [{ input: { n: 2 }, output: 2, explanation: "1+1 or 2." }, { input: { n: 3 }, output: 3, explanation: "1+1+1, 1+2, 2+1." }],
    hints: ["To stand on step n you came from n-1 or n-2."],
    tests: [{ n: 1 }, { n: 2 }, { n: 3 }, { n: 4 }, { n: 10 }, { n: 30 }, { n: 44 }, { n: 45 }],
    editorial: "## Approach: Fibonacci recurrence\n\n`ways(n) = ways(n-1) + ways(n-2)` with `ways(1) = 1`, `ways(2) = 2`. Only the previous two values are needed, so keep two variables.\n\n**Complexity:** O(n) time, O(1) space.",
    py: `class Solution:
    def climbStairs(self, n: int) -> int:
        a, b = 1, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b
`,
    cpp: `class Solution {
public:
    int climbStairs(int n) {
        int a = 1, b = 1;
        for (int i = 1; i < n; i++) {
            int c = a + b;
            a = b;
            b = c;
        }
        return b;
    }
};
`,
    java: `class Solution {
    public int climbStairs(int n) {
        int a = 1, b = 1;
        for (int i = 1; i < n; i++) {
            int c = a + b;
            a = b;
            b = c;
        }
        return b;
    }
}
`,
  },
  {
    id: 104, slug: "maximum-depth-of-binary-tree", title: "Maximum Depth of Binary Tree", difficulty: "Easy", tags: ["Tree", "Depth-First Search", "Breadth-First Search"],
    statement: "Return the maximum depth of a binary tree: the number of nodes on the longest path from the root down to a leaf. An empty tree has depth `0`.\n\nTrees are given in level order with `null` for missing children.",
    constraints: ["The tree has between `0` and `10^4` nodes.", "`-100 <= Node.val <= 100`"],
    signature: P("maxDepth", [{ name: "root", type: "TreeNode" }], "int"),
    examples: [{ input: { root: [3, 9, 20, null, null, 15, 7] }, output: 3 }, { input: { root: [1, null, 2] }, output: 2 }],
    hints: ["The depth of a tree is 1 plus the larger depth of its two subtrees."],
    tests: [{ root: [3, 9, 20, null, null, 15, 7] }, { root: [1, null, 2] }, { root: [] }, { root: [0] }, { root: [1, 2, 3, 4, null, null, 5, 6] }, { root: [1, 2, null, 3, null, 4, null, 5] }],
    editorial: "## Approach: recursion (or BFS)\n\n`depth(node) = 0` for null, otherwise `1 + max(depth(left), depth(right))`.\n\nFor very deep, skewed trees an iterative level-order traversal avoids recursion limits.\n\n**Complexity:** O(n) time, O(h) space for the recursion stack.",
    py: `class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        depth = 0
        level = [root]
        while level:
            depth += 1
            nxt = []
            for n in level:
                if n.left: nxt.append(n.left)
                if n.right: nxt.append(n.right)
            level = nxt
        return depth
`,
    cpp: `class Solution {
public:
    int maxDepth(TreeNode* root) {
        if (!root) return 0;
        int depth = 0;
        queue<TreeNode*> q;
        q.push(root);
        while (!q.empty()) {
            depth++;
            for (size_t i = q.size(); i > 0; i--) {
                TreeNode* n = q.front();
                q.pop();
                if (n->left) q.push(n->left);
                if (n->right) q.push(n->right);
            }
        }
        return depth;
    }
};
`,
    java: `class Solution {
    public int maxDepth(TreeNode root) {
        if (root == null) return 0;
        int depth = 0;
        Queue<TreeNode> q = new ArrayDeque<>();
        q.add(root);
        while (!q.isEmpty()) {
            depth++;
            for (int i = q.size(); i > 0; i--) {
                TreeNode n = q.poll();
                if (n.left != null) q.add(n.left);
                if (n.right != null) q.add(n.right);
            }
        }
        return depth;
    }
}
`,
  },
  {
    id: 121, slug: "best-time-to-buy-and-sell-stock", title: "Best Time to Buy and Sell Stock", difficulty: "Easy", tags: ["Array", "Dynamic Programming"],
    statement: "`prices[i]` is a stock price on day `i`. Choose one day to buy and a **later** day to sell. Return the maximum profit, or `0` if no profitable trade exists.",
    constraints: ["`1 <= prices.length <= 10^5`", "`0 <= prices[i] <= 10^4`"],
    signature: P("maxProfit", [nums("prices")], "int"),
    examples: [{ input: { prices: [7, 1, 5, 3, 6, 4] }, output: 5, explanation: "Buy at 1, sell at 6." }, { input: { prices: [7, 6, 4, 3, 1] }, output: 0 }],
    hints: ["For each day, the best buy is the cheapest price seen before it."],
    tests: [{ prices: [7, 1, 5, 3, 6, 4] }, { prices: [7, 6, 4, 3, 1] }, { prices: [1] }, { prices: [2, 4, 1] }, { prices: [3, 3, 3] }, { prices: [1, 10000] }, { prices: Array.from({ length: 100000 }, (_, i) => (i * 7919) % 10001) }],
    editorial: "## Approach: single pass\n\nTrack the minimum price so far. The best profit selling today is `price - minSoFar`; keep the maximum of those.\n\n**Complexity:** O(n) time, O(1) space.",
    py: `class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        lo, best = prices[0], 0
        for p in prices[1:]:
            best = max(best, p - lo)
            lo = min(lo, p)
        return best
`,
    cpp: `class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int lo = prices[0], best = 0;
        for (size_t i = 1; i < prices.size(); i++) {
            best = max(best, prices[i] - lo);
            lo = min(lo, prices[i]);
        }
        return best;
    }
};
`,
    java: `class Solution {
    public int maxProfit(int[] prices) {
        int lo = prices[0], best = 0;
        for (int i = 1; i < prices.length; i++) {
            best = Math.max(best, prices[i] - lo);
            lo = Math.min(lo, prices[i]);
        }
        return best;
    }
}
`,
  },
  {
    id: 200, slug: "number-of-islands", title: "Number of Islands", difficulty: "Medium", tags: ["Array", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"],
    statement: "A grid of characters `'1'` (land) and `'0'` (water) is given. An island is a maximal group of land cells connected horizontally or vertically. Return the number of islands.\n\nEverything outside the grid is water.",
    constraints: ["`1 <= m, n <= 300`", "`grid[i][j]` is `'0'` or `'1'`."],
    signature: P("numIslands", [{ name: "grid", type: "char[][]" }], "int"),
    examples: [{ input: { grid: [["1", "1", "0"], ["1", "0", "0"], ["0", "0", "1"]] }, output: 2 }],
    hints: ["Each time you find unvisited land, flood-fill the whole island and count once."],
    tests: [{ grid: [["1", "1", "0"], ["1", "0", "0"], ["0", "0", "1"]] }, { grid: [["1"]] }, { grid: [["0"]] }, { grid: [["1", "0", "1"], ["0", "1", "0"], ["1", "0", "1"]] }, { grid: [["1", "1", "1", "1"], ["1", "0", "0", "1"], ["1", "1", "1", "1"]] }, { grid: Array.from({ length: 300 }, () => Array(300).fill("1")) }, { grid: Array.from({ length: 300 }, (_, i) => Array.from({ length: 300 }, (_, j) => ((i + j) % 2 === 0 ? "1" : "0"))) }],
    editorial: "## Approach: flood fill\n\nScan every cell. On unvisited land, increment the answer and sink the whole island (mark visited) with an explicit stack, which avoids recursion-depth problems on a 300×300 all-land grid.\n\n**Complexity:** O(m·n) time, O(m·n) space worst case.",
    py: `class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        m, n = len(grid), len(grid[0])
        seen = [[False] * n for _ in range(m)]
        count = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == '1' and not seen[i][j]:
                    count += 1
                    seen[i][j] = True
                    st = [(i, j)]
                    while st:
                        x, y = st.pop()
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            a, b = x + dx, y + dy
                            if 0 <= a < m and 0 <= b < n and grid[a][b] == '1' and not seen[a][b]:
                                seen[a][b] = True
                                st.append((a, b))
        return count
`,
    cpp: `class Solution {
public:
    int numIslands(vector<vector<char>>& grid) {
        int m = grid.size(), n = grid[0].size(), count = 0;
        vector<vector<char>> seen(m, vector<char>(n, 0));
        int dx[4] = {1, -1, 0, 0}, dy[4] = {0, 0, 1, -1};
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++) {
                if (grid[i][j] != '1' || seen[i][j]) continue;
                count++;
                seen[i][j] = 1;
                vector<pair<int, int>> st{{i, j}};
                while (!st.empty()) {
                    auto [x, y] = st.back();
                    st.pop_back();
                    for (int d = 0; d < 4; d++) {
                        int a = x + dx[d], b = y + dy[d];
                        if (a >= 0 && a < m && b >= 0 && b < n && grid[a][b] == '1' && !seen[a][b]) {
                            seen[a][b] = 1;
                            st.push_back({a, b});
                        }
                    }
                }
            }
        return count;
    }
};
`,
    java: `class Solution {
    public int numIslands(char[][] grid) {
        int m = grid.length, n = grid[0].length, count = 0;
        boolean[][] seen = new boolean[m][n];
        int[] dx = {1, -1, 0, 0}, dy = {0, 0, 1, -1};
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++) {
                if (grid[i][j] != '1' || seen[i][j]) continue;
                count++;
                seen[i][j] = true;
                Deque<int[]> st = new ArrayDeque<>();
                st.push(new int[]{i, j});
                while (!st.isEmpty()) {
                    int[] c = st.pop();
                    for (int d = 0; d < 4; d++) {
                        int a = c[0] + dx[d], b = c[1] + dy[d];
                        if (a >= 0 && a < m && b >= 0 && b < n && grid[a][b] == '1' && !seen[a][b]) {
                            seen[a][b] = true;
                            st.push(new int[]{a, b});
                        }
                    }
                }
            }
        return count;
    }
}
`,
  },
  {
    id: 206, slug: "reverse-linked-list", title: "Reverse Linked List", difficulty: "Easy", tags: ["Linked List", "Recursion"],
    statement: "Reverse a singly linked list and return the new head.",
    constraints: ["The list has between `0` and `5000` nodes.", "`-5000 <= Node.val <= 5000`"],
    signature: P("reverseList", [{ name: "head", type: "ListNode" }], "ListNode"),
    examples: [{ input: { head: [1, 2, 3, 4, 5] }, output: [5, 4, 3, 2, 1] }, { input: { head: [] }, output: [] }],
    hints: ["Keep track of the previous node while walking the list and flip each `next` pointer."],
    tests: [{ head: [1, 2, 3, 4, 5] }, { head: [1, 2] }, { head: [] }, { head: [7] }, { head: Array.from({ length: 5000 }, (_, i) => i - 2500) }],
    editorial: "## Approach: iterative pointer reversal\n\nWalk the list with `prev` (initially null) and `cur`. For each node save `next`, point `cur.next` at `prev`, then advance both.\n\n**Complexity:** O(n) time, O(1) space.",
    py: `class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev = None
        while head:
            head.next, prev, head = prev, head, head.next
        return prev
`,
    cpp: `class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        ListNode* prev = nullptr;
        while (head) {
            ListNode* nxt = head->next;
            head->next = prev;
            prev = head;
            head = nxt;
        }
        return prev;
    }
};
`,
    java: `class Solution {
    public ListNode reverseList(ListNode head) {
        ListNode prev = null;
        while (head != null) {
            ListNode nxt = head.next;
            head.next = prev;
            prev = head;
            head = nxt;
        }
        return prev;
    }
}
`,
  },
  {
    id: 283, slug: "move-zeroes", title: "Move Zeroes", difficulty: "Easy", tags: ["Array", "Two Pointers"],
    statement: "Move all `0`s in `nums` to the end **in place**, keeping the relative order of the non-zero elements. Do not return anything; modify `nums` directly.",
    constraints: ["`1 <= nums.length <= 10^4`", "`-2^31 <= nums[i] <= 2^31 - 1`"],
    signature: P("moveZeroes", [nums()], "void", { mutates: "nums" }),
    examples: [{ input: { nums: [0, 1, 0, 3, 12] }, output: [1, 3, 12, 0, 0] }, { input: { nums: [0] }, output: [0] }],
    hints: ["Write non-zero elements forward with one pointer, then fill the tail with zeros."],
    tests: [{ nums: [0, 1, 0, 3, 12] }, { nums: [0] }, { nums: [1, 2, 3] }, { nums: [0, 0, 0, 1] }, { nums: [4, 0, 5, 0, 0, 6, 0] }, { nums: Array.from({ length: 10000 }, (_, i) => (i % 3 === 0 ? 0 : i)) }],
    editorial: "## Approach: two pointers\n\nKeep `w`, the next write position. For every non-zero element, copy it to `nums[w++]`. After the scan, set the remaining positions to zero. This performs the fewest writes while preserving order.\n\n**Complexity:** O(n) time, O(1) space.",
    py: `class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        w = 0
        for x in nums:
            if x != 0:
                nums[w] = x
                w += 1
        for i in range(w, len(nums)):
            nums[i] = 0
`,
    cpp: `class Solution {
public:
    void moveZeroes(vector<int>& nums) {
        size_t w = 0;
        for (int x : nums)
            if (x != 0) nums[w++] = x;
        while (w < nums.size()) nums[w++] = 0;
    }
};
`,
    java: `class Solution {
    public void moveZeroes(int[] nums) {
        int w = 0;
        for (int x : nums)
            if (x != 0) nums[w++] = x;
        while (w < nums.length) nums[w++] = 0;
    }
}
`,
  },
];
