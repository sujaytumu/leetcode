class Solution:
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
