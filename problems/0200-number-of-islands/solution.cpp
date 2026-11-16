class Solution {
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
