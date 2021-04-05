#TAG-CLASS
class Solution:
    def __init__(self):
        #TAG-INIT
        pass
    def run(self ,var0,x):
        localVar0=self.removeList(var0,x)
        return self.printlist(var0)
        #TAG-RUN
        pass
    def removeList(self, arr, x):
        return arr.remove(x)
    def printlist(self,the_list):
        for eachitem in the_list:
            print(eachitem)
    #TAG-METHOD

if __name__ == '__main__':
    s = Solution()
    #TAG-SCRIPT

