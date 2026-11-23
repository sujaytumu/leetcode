class Solution {
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
