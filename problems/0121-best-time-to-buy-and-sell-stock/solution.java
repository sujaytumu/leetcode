class Solution {
    public int maxProfit(int[] prices) {
        int lo = prices[0], best = 0;
        for (int i = 1; i < prices.length; i++) {
            best = Math.max(best, prices[i] - lo);
            lo = Math.min(lo, prices[i]);
        }
        return best;
    }
}
