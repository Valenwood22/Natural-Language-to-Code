#TAG-CLASS
class Solution:
    def __init__(self):
        #TAG-INIT
        pass
    def run(self):
        #TAG-RUN
        pass
    def sign_differs(self,n1,n2):
        '''return True if n1 and n2 have different signs.'''
        return n1 &lt; 0 and n2 &gt;= 0 or n1 &gt;= 0 and n2 &lt; 0
    
    for a_list in all_lists:
        print(f'a_list: {a_list}')
    
        sum_list = []
        prev_idx = 0
        for idx in range(1, len(a_list)):
            n1, n2 = a_list[idx-1], a_list[idx]
            if n1 in sum_list:
                continue
            if sign_differs(n1, n2):  # +/- or -/+ detected
                if a_list[prev_idx] &gt;= 0:
                    max_abs = max(a_list[prev_idx:idx])  # largest positive
                else:
                    max_abs = min(a_list[prev_idx:idx])  # smallest negative
    
                if not max_abs in sum_list:
                    sum_list.append(max_abs)
                prev_idx = idx
    
        print(f'sum_list: {sum_list}\n')
    #TAG-METHOD

if __name__ == '__main__':
    s = Solution()
    #TAG-SCRIPT
    print('successfully compiled')

