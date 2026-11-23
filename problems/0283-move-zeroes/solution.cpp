class Solution {
public:
    void moveZeroes(vector<int>& nums) {
        size_t w = 0;
        for (int x : nums)
            if (x != 0) nums[w++] = x;
        while (w < nums.size()) nums[w++] = 0;
    }
};
