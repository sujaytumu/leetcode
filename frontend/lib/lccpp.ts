/**
 * Problems whose judge input is encoded differently from LeetCode (digits for board cells, labels for characters,
 * values instead of tree nodes, ...). In C++ the editor shows LeetCode's own signature and a hidden forwarding
 * `solve` converts the judge's values to LeetCode's types and back, so the code you write is exactly what you would
 * submit on leetcode.com.
 *
 * `params` and `ret` are what the visible stub shows; `forward(m)` is the body of the hidden `solve`, where `m` is the
 * name of the method you wrote.
 */
export interface CppLc { ret: string; params: string; forward: (m: string) => string }

const SPLIT_WORDS = (from: string, into: string) =>
  `vector<string> ${into}; { istringstream ss(${from}); string w; while (ss >> w) ${into}.push_back(w); }`;

const FIND_NODE = `function<TreeNode*(TreeNode*, int)> find = [&](TreeNode* r, int v) -> TreeNode* { if (!r) return nullptr; if (r->val == v) return r; TreeNode* a = find(r->left, v); return a ? a : find(r->right, v); };`;

export const CPP_LC: Record<string, CppLc> = {
  "evaluate-reverse-polish-notation": {
    ret: "int", params: "vector<string>& tokens",
    forward: (m) => `${SPLIT_WORDS("tokens", "t")} return Solution().${m}(t);`,
  },
  "word-break": {
    ret: "bool", params: "string s, vector<string>& wordDict",
    forward: (m) => `${SPLIT_WORDS("wordDict", "d")} return Solution().${m}(s, d);`,
  },
  "task-scheduler": {
    ret: "int", params: "vector<char>& tasks, int n",
    forward: (m) => `vector<char> t; for (int x : tasks) t.push_back((char)('A' + x % 26)); return Solution().${m}(t, n);`,
  },
  "lowest-common-ancestor-of-a-binary-search-tree": {
    ret: "TreeNode*", params: "TreeNode* root, TreeNode* p, TreeNode* q",
    forward: (m) => `${FIND_NODE} TreeNode* r = Solution().${m}(root, find(root, p), find(root, q)); return r ? r->val : -1;`,
  },
  "lowest-common-ancestor-of-a-binary-tree": {
    ret: "TreeNode*", params: "TreeNode* root, TreeNode* p, TreeNode* q",
    forward: (m) => `${FIND_NODE} TreeNode* r = Solution().${m}(root, find(root, p), find(root, q)); return r ? r->val : -1;`,
  },
  "surrounded-regions": {
    ret: "void", params: "vector<vector<char>>& board",
    forward: (m) => `vector<vector<char>> b(board.size()); for (size_t i = 0; i < board.size(); i++) for (int v : board[i]) b[i].push_back(v ? 'O' : 'X'); Solution().${m}(b); for (size_t i = 0; i < board.size(); i++) for (size_t j = 0; j < board[i].size(); j++) board[i][j] = b[i][j] == 'O' ? 1 : 0; return board;`,
  },
  "valid-sudoku": {
    ret: "bool", params: "vector<vector<char>>& board",
    forward: (m) => `vector<vector<char>> b(board.size()); for (size_t i = 0; i < board.size(); i++) for (int v : board[i]) b[i].push_back(v == 0 ? '.' : (char)('0' + v)); return Solution().${m}(b);`,
  },
  "remove-duplicates-from-sorted-array": {
    ret: "int", params: "vector<int>& nums",
    forward: (m) => `int k = Solution().${m}(nums); nums.resize(k); return nums;`,
  },
  "is-graph-bipartite": {
    ret: "bool", params: "vector<vector<int>>& graph",
    forward: (m) => `vector<vector<int>> g(n); for (auto &e : edges) { g[e[0]].push_back(e[1]); g[e[1]].push_back(e[0]); } return Solution().${m}(g);`,
  },
  "longest-palindromic-substring-length": {
    ret: "string", params: "string s",
    forward: (m) => `string r = Solution().${m}(s); bool pal = true; for (int i = 0, j = (int)r.size() - 1; i < j; i++, j--) if (r[i] != r[j]) pal = false; if (!pal || r.empty() || s.find(r) == string::npos) return -1; return (int)r.size();`,
  },
};
