__authors__ = "Dr. Malik Mohammad Zubair and Joshua Gisi "
__copyright__ = ""
__credits__ = ["Malik Mohammad Zubair", "Joshua Gisi"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Joshua Gisi"
__email__ = "Joshua.Gisi22@gmail.com"
__status__ = "Development"

from stackapi import StackAPI
import re
import sqlite3
import subprocess

class codeObj:
    def __init__(self, data, indents):
        self.data = data
        self.indents = indents

    def __str__(self):
        return f"w {self.indents} : {self.data}"


class fromTheOverflow:

    def __init__(self):
        self.__DataBaseFilePath__ = "N:\\_Programming\\nltc\\data\\algorithms.db"
        self.template_path = 'N:\\_Programming\\nltc\\data\\CompileTemplate.tmplt'
        self.tag_library = {}

    def exeSqlInsert(self, command):
        connection = sqlite3.connect(self.__DataBaseFilePath__)
        # Get a cursor to execute sql statements
        cursor = connection.cursor()
        cursor.execute(command)
        connection.commit()
        connection.close()



    def exeSqlSelect(self, command):
        # Create a database if not exists and get a connection to it
        connection = sqlite3.connect(self.__DataBaseFilePath__)
        # Get a cursor to execute sql statements
        cursor = connection.cursor()
        cursor.execute(command)
        rows = cursor.fetchall()
        connection.close()
        return rows



    def compile_new_code(self, filename, debug=True):
        cmd = 'python ' + filename
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout != "" and debug:
            print(stdout.decode('utf-8'))
        if stderr != "" and debug:
            print(stderr.decode('utf-8'))
        return stderr.decode('utf-8')



    def combine(self, baseCode, predictSolution, tag):
        indexOfTag = self.tag_library['#TAG-' + tag]
        parentIndent = baseCode[indexOfTag].indents
        for line in predictSolution[::-1]:
            line.indents += parentIndent
            baseCode.insert(indexOfTag, line)
        self.update_tag_indexes(baseCode)
        return baseCode



    def update_tag_indexes(self, baseCode):
        for i, line in enumerate(baseCode):
            if line.data[0:4] == "#TAG":
                self.tag_library[line.data] = i



    def load_empty_template_as_list(self):
        template = open(self.template_path, 'r')
        templateList = []
        for i, line in enumerate(template):
            whiteSpace = next((i for i, c in enumerate(line) if c != ' '), len(line))
            noSpaces = line.strip()
            templateList.append(codeObj(noSpaces, whiteSpace))
            if noSpaces[0:4] == '#TAG':
                self.tag_library[noSpaces] = i
        return templateList



    def load_code_as_list(self, s):
        templateList = []
        for i, line in enumerate(s.split('\n')):
            whiteSpace = next((i for i, c in enumerate(line) if c != ' '), len(line))
            noSpaces = line.strip()
            templateList.append(codeObj(noSpaces, whiteSpace))
            if noSpaces[0:4] == '#TAG':
                self.tag_library[noSpaces] = i
        return templateList



    def write_code_from_list(self, filename, code):
        outFile = open(filename, 'r+')
        outFile.truncate(0)
        for line in code:
            outFile.write(' '*line.indents+line.data+'\n')
        outFile.close()



    def get_recent(self, num, table):
        return self.exeSqlSelect(f"SELECT * FROM {table} ORDER BY PID desc limit {num}")


    def load_into_db(self, code, desc):
        payload = code[4]
        payload = payload.replace("'","''")
        payload = payload.split('\n')
        payload = "'||char(10)||'".join(payload)
        payload = payload.replace("''||", "")
        payload = payload.strip()
        defName = code[0]
        call = code[1]
        str_params = ','.join(code[2])
        q_id = code[3]
        returndata = "NONE" # maybe run some test cases to find out what it returns???
        insert_line = "NONE"
        sql_cmd = f"INSERT INTO algorithms_temp (name, payload, call, parameters, return, line, Desc, QID) VALUES (" \
                  f"'{defName}','{payload}','{call}','{str_params}','{returndata}','{insert_line}','{desc}', '{q_id}')"
        print(sql_cmd)
        self.exeSqlInsert(sql_cmd)



    def filter(self, ready_code, code_qid, desc):
        # print(ready_code)
        # print(code_qid)
        passed_filter = []
        for q_index, code in enumerate(ready_code):
            defName = "NONE"
            params = "NONE"
            call = "NONE"
            payload = "NONE"
            baseCode = self.load_empty_template_as_list()
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if len(lines) == 1:
                    return_statement = "NONE"
                    defName = '_'.join(desc.split(" "))
                    split_line = line.split('=')
                    if len(split_line) == 1:
                        return_statement = split_line[0].strip()
                        if return_statement[:5] != "print":
                            return_statement = 'return ' + return_statement
                        else: break
                    elif len(split_line) == 2:
                        var = split_line[0].strip()
                        return_statement = split_line[1].strip()
                        if return_statement[:5] != "print":
                            return_statement = 'return ' + return_statement
                        else: break
                    else: break

                    if return_statement != "NONE": # Find parameters
                        signature_split = return_statement.split('(')
                        if len(signature_split) != 2: continue  # TODO: Handle parentheses in signature
                        signature_split_1 = signature_split[0]
                        params = signature_split[1]
                        # Find params
                        params = params.replace(')', '')
                        params = params.split(',')
                        params = [p.strip() for p in params]
                        str_params = ','.join(params)

                        # Find call
                        call = 'self.' + defName + '(' + '#TAG-VAR,' * len(params)
                        call = call[:-1] + ')'

                        # insert the new function header
                        lines = [f"def {defName}({str_params}):", f'    {return_statement}']
                        defLine = 0

                elif line[:3] == 'def':
                    """
                    Handle straight methods in the code
                    """
                    defLine = i
                    # Find def name
                    defName = line.split(' ', 1)[1]
                    signature_split = defName.split('(')
                    if len(signature_split) != 2: continue  # TODO: Handle parentheses in signature
                    defName = signature_split[0]
                    params = signature_split[1]
                    # Find params
                    params = params.replace('):', '')
                    params = params.split(',')
                    params = [p.strip() for p in params]
                    str_params = ','.join(params)

                    # Find call
                    call = 'self.' + defName + '(' + '#TAG-VAR,' * len(params)
                    call = call[:-1] + ')'
                    # print(defName, params, call)

            if defName != "NONE" and params != "NONE" and call != "NONE":
                # print(lines)
                if 'self' in params[0] or params[0] == '':
                    if len(params) == 0:
                        payload = 'def '+defName+'('+','.join(params) + '):\n'
                    else:
                        payload = 'def ' + defName + '(self):\n'
                else:
                    if len(params) == 0:
                        payload = 'def '+defName+'(self):\n'
                    else:
                        payload = 'def ' + defName + '(self,' + ','.join(params) + '):\n'
                payload += "\n".join(lines[defLine+1:])

            combinedCode = self.combine(baseCode, self.load_code_as_list(payload), 'METHOD')
            # combinedCode = self.combine(combinedCode, self.load_code_as_list(call), 'RUN')

            self.write_code_from_list('compile.py', combinedCode)

            c = self.compile_new_code('compile.py', debug=False)
            if c == "":
                passed_filter.append([defName, call, params, code_qid[q_index], payload])

        return passed_filter



    def run(self, desc, live=True, num=5):
        if not live:
            return self.get_recent(num, 'algorithms_temp')
        SITE = StackAPI('stackoverflow')
        SITE.max_pages = 16
        SITE.page_size = 1
        questions = SITE.fetch('search/advanced', sort='relevance', tagged='python', q=desc)
        items = questions['items'] # [0]['question_id'])
        q_ids = []

        for item in items:
            q_ids.append(item['question_id'])

        # print("q_ids:", q_ids)
        raw_code = []
        code_qid = []
        answers = SITE.fetch('questions/{ids}/answers', ids=q_ids, sort='votes', filter='withbody')

        for answer in answers['items']:
            raw_code.append(answer['body'])
            code_qid.append(answer['question_id'])

        # raw_code = ['<pre><code>def altElement(a):\n    return a[::2]\n</code></pre>\n', '<p>Slice notation <code>a[start_index:end_index:step]</code></p>\n\n<pre><code>return a[::2]\n</code></pre>\n\n<p>where <code>start_index</code> defaults to <code>0</code> and <code>end_index</code> defaults to the <code>len(a)</code>.</p>\n', '<p>Alternatively, you could do:</p>\n\n<pre><code>for i in range(0, len(a), 2):\n    #do something\n</code></pre>\n\n<p>The extended slice notation <em>is</em> much more concise, though.</p>\n']
        ready_code = []
        for code in raw_code:
            # regex to extract required strings
            res = re.findall(r"<pre><code>(.*?)</code></pre>", code, re.DOTALL)
            if not res:
                continue
            res = res[0]
            res = re.sub(r'(?m)^ *#.*\n?','',res)
            res = res.rstrip("\n")
            ready_code.append(res)

        # code_qid = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        # ready_code = ['y = np.cumsum(x)', 'y = np.add.accumulate(x)', "import multiprocessing\nimport numpy as np\nimport thread\n\nclass Sum: #again, this class is from ParallelPython's example code (I modified for an array and added comments)\n    def __init__(self):\n        self.value = np.zeros((1,512*512)) #this is the initialization of the sum\n        self.lock = thread.allocate_lock()\n        self.count = 0\n\n    def add(self,value):\n        self.count += 1\n        self.lock.acquire() #lock so sum is correct if two processes return at same time\n        self.value += value #the actual summation\n        self.lock.release()\n\ndef computation(index):\n    array1 = np.ones((1,512*512))*index #this is where the array-returning computation goes\n    return array1\n\ndef summers(num_iters):\n    pool = multiprocessing.Pool(processes=8)\n\n    sumArr = Sum() #create an instance of callback class and zero the sum\n    for index in range(num_iters):\n        singlepoolresult = pool.apply_async(computation,(index,),callback=sumArr.add)\n\n    pool.close()\n    pool.join() #waits for all the processes to finish\n\n    return sumArr.value", 'is_sum = lambda seq, x: any(x == y + z for yi, y in enumerate(seq) for zi, z in enumerate(seq) if zi != yi)', 'sorty = []\ni = 0\nfor n in range(len(nums)):\n            print(n)\n            if sum(sorty) &lt;= sum(nums):\n                sorty.append(nums[-1])\n                nums.pop()\n            else: \n                break\n\nreturn sorty', 'arr = np.array([0.1, 1, 1.2, 0.5, -0.3, -0.2, 0.1, 0.5, 1])\nw = 3  #rolling window\n\narr[arr&lt;0]=0\n\nshape = arr.shape[0]-w+1, w  #Expected shape of view (7,3)\nstrides = arr.strides[0], arr.strides[0] #Strides (8,8) bytes\nrolling = np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)\n\nrolling_sum = np.sum(rolling, axis=1)\nrolling_sum', "import sys\nimport random\nimport time\nimport multiprocessing\nimport numpy as np\n\nnumpows = 5\nnumitems = 25\nnprocs = 4\n\ndef expensiveComputation( i ):\n  time.sleep( random.random() * 10 )\n  return np.array([i**j for j in range(numpows)])\n\ndef listsum( l ):\n  sum = np.zeros_like(l[0])\n  for item in l:\n    sum = sum + item\n  return sum\n\ndef partition(lst, n):\n  division = len(lst) / float(n)\n  return [ lst[int(round(division * i)): int(round(division * (i + 1)))] for i in xrange(n) ]\n\ndef myRunningSum( l ):\n  sum = np.zeros(numpows)\n  for item in l:\n     sum = sum + expensiveComputation(item)\n  return sum\n\nif __name__ == '__main__':\n\n  random.seed(1)\n  data = range(numitems)\n\n  pool = multiprocessing.Pool(processes=4,)\n  calculations = pool.map(myRunningSum, partition(data,nprocs))\n\n  print 'Answer is:', listsum(calculations)\n  print 'Expected answer: ', np.array([25.,300.,4900.,90000.,1763020.])", 'st_age = [0]*3 \nfor g in range(3):\n    st_age[g] = int(input("Enter student age "))\n\ng = sum = 0 \nwhile g &lt; len(st_age): #am I using this correctly? \n    sum = sum + st_age[g]\n    g += 1\n\nprint sum', 'out = ((Orginal - Mutated)**2).sum()', 'print(x[0:np.flatnonzero(x.cumsum()&gt;userNum)[0]+1])', "def testFunction(array):\n    s = 0\n    for i in array:\n        s += i    \n    mx = s\n    print('The sum of {} is: {}'.format(array, s))\n    k = 1\n    for i in array[:-1]: \n        s -= i \n        print('The sum of {} is: {}'.format(array[k:], s))\n        mx = mx if s &lt; mx else s \n        k += 1\n    return mx\n\nprint(testFunction([1, 2, -3, 4, 5]))", 'difference = np.abs(y_test_predicted - y_test_unscaled)\nerror = difference / y_test_predicted\nav_error = np.mean(error)', 'import numpy as np\n\n\ndef rolling_window(a, window):\n    &quot;&quot;&quot;Recipe from https://stackoverflow.com/q/6811183/4001592&quot;&quot;&quot;\n    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)\n    strides = a.strides + (a.strides[-1],)\n    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)\n\n\na = np.array([0.1, 1, 1.2, 0.5, -0.3, -0.2, 0.1, 0.5, 1])\n\nres = rolling_window(np.clip(a, 0, a.max()), 3).sum(axis=1)\nprint(res)', "In [20]: np.correlate(arr.clip(0), np.ones(3), mode='valid')\nOut[20]: array([2.3, 2.7, 1.7, 0.5, 0.1, 0.6, 1.6])", "\nlist_1 = []\nlist_2 = [0]\nlist_3 = [0, 0]\nlist_4 = [0, 0, 0]\nlist_5 = [-2, 4, -2, 4]\nlist_6 = [2, -4, 2, -4]\n\nt_list = [ 2, 6\n          , -3\n          , 7\n          , -2, -5\n          , 10, 13, 13, 13, 13, 12, 12, 12, 12, 12, 8, 8, 8, 8, 8, 8\n          , -9\n          , 8\n          , -9, -9, -9, -9, -9, -9, -9, -9\n          , 12, 12, 12, 12, 12\n           ]  # expected result: [6, -3, 7, -5, 13, -9, 8]\n\nall_lists = [list_1, list_2, list_3, list_4, list_5, list_6, t_list]\n\ndef sign_differs(n1, n2):\n    '''return True if n1 and n2 have different signs.'''\n    return n1 &lt; 0 and n2 &gt;= 0 or n1 &gt;= 0 and n2 &lt; 0\n\nfor a_list in all_lists:\n    print(f'a_list: {a_list}')\n\n    sum_list = []\n    prev_idx = 0\n    for idx in range(1, len(a_list)):\n        n1, n2 = a_list[idx-1], a_list[idx]\n        if n1 in sum_list:\n            continue\n        if sign_differs(n1, n2):  # +/- or -/+ detected\n            if a_list[prev_idx] &gt;= 0:\n                max_abs = max(a_list[prev_idx:idx])  # largest positive\n            else:\n                max_abs = min(a_list[prev_idx:idx])  # smallest negative\n\n            if not max_abs in sum_list:\n                sum_list.append(max_abs)\n            prev_idx = idx\n\n    print(f'sum_list: {sum_list}\\n')"]
        # print(ready_code)

        filtered_code = self.filter(ready_code, code_qid, desc)

        # Read code and load into data base
        for i, snippet in enumerate(filtered_code):
            self.load_into_db(snippet, desc)

        print(f"{len(ready_code)} new methods loaded")
        return self.get_recent(len(ready_code), 'algorithms_temp')

if __name__ == '__main__':
    print(fromTheOverflow().run("running sum of array"))
