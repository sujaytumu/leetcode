class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        lo, best = prices[0], 0
        for p in prices[1:]:
            best = max(best, p - lo)
            lo = min(lo, p)
        return best
