import numpy as np
#TAG-IMPORT
#TAG-CLASS
class Solution:
    def __init__(self):
        #TAG-INIT
        pass
    def run(self ,nums):
        return self.running_sum_of_array(nums)
        #TAG-RUN
        pass
    def running_sum_of_array(self,x):
        return np.cumsum(x)
    #TAG-METHOD

if __name__ == '__main__':
    s = Solution()
    #TAG-SCRIPT

