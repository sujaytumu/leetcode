class Solution {
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
