class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        w = 0
        for x in nums:
            if x != 0:
                nums[w] = x
                w += 1
        for i in range(w, len(nums)):
            nums[i] = 0
