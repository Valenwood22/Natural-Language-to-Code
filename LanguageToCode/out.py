#TAG-CLASS
class Solution:
    def __init__(self):
        #TAG-INIT
        pass
    def run(self ,romannumeral):
        return self.palindrome(romannumeral)
        #TAG-RUN
        pass
    def palindrome(self,num):
        return str(num) == str(num)[::-1]
    #TAG-METHOD

if __name__ == '__main__':
    s = Solution()
    #TAG-SCRIPT

