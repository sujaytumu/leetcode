class Solution {
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
