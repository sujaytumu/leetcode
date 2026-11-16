class Solution:
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
