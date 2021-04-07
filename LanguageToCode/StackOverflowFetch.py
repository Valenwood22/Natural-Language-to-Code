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



    def filter(self, ready_code, code_qid):
        print(ready_code)
        # print(code_qid)
        defName = "NONE"
        params = "NONE"
        call = "NONE"
        payload = "NONE"
        passed_filter = []
        for q_index, code in enumerate(ready_code):
            baseCode = self.load_empty_template_as_list()
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if line[:3] == 'def':
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

        # print(ready_code)

        filtered_code = self.filter(ready_code, code_qid)
        # print(filtered_code)
        # Read code and load into data base
        for i, snippet in enumerate(filtered_code):
            self.load_into_db(snippet, desc)

        print(f"{len(ready_code)} new methods loaded")
        return self.get_recent(len(ready_code), 'algorithms_temp')

if __name__ == '__main__':
    print(fromTheOverflow().run("print list"))
