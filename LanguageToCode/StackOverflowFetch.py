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

class fromTheOverflow:

    def __init__(self):
        self.__DataBaseFilePath__ = "N:\\_Programming\\nltc\\data\\algorithms.db"

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



    def get_recent(self, num, table):
        return self.exeSqlSelect(f"SELECT * FROM {table} ORDER BY PID desc limit {num}")


    def load_into_db(self, code, desc, q_id):
        defName = "NONE"    #
        payload = "NONE"
        call = "NONE"       #
        params = "NONE"     #
        returndata = "NONE" # maybe run some test cases to find out what it returns???
        insert_line = "NONE"
        lines = code.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line[:3] == 'def':
                defLine = i
                # Find def name
                defName = line.split(' ',1)[1]
                defName, params = defName.split('(')
                # Find params
                params = params.replace('):', '')
                params = params.split(',')
                params = [p.strip() for p in params]
                str_params = ','.join(params)

                # Find call
                call = 'self.' + defName + '(' + '#TAG-VAR,'*len(params)
                call = call[:-1] + ')'

        if defName!="NONE" and params!="NONE" and call!="NONE":
            # insert into database
            if 'self' in params[0] or params[0] == '':
                if len(params) == 0:
                    payload = 'def '+defName+'('+','.join(params) + '):\\n'
                else:
                    payload = 'def ' + defName + '(self):\\n'
            else:
                if len(params) == 0:
                    payload = 'def '+defName+'(self):\\n'
                else:
                    payload = 'def ' + defName + '(self,' + ','.join(params) + '):\\n'
            payload += '\\n'.join(lines[defLine+1:])
            payload = payload.strip()
            payload = payload.replace("'","''")
            sql_cmd = f"INSERT INTO algorithms_temp (name, payload, call, parameters, return, line, Desc, QID) VALUES (" \
                      f"'{defName}','{payload}','{call}','{str_params}','{returndata}','{insert_line}','{desc}', '{q_id}')"
            # print(sql_cmd)
            self.exeSqlInsert(sql_cmd)

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

        # Read code and load into data base
        for i, snippet in enumerate(ready_code):
            self.load_into_db(snippet, desc, code_qid[i])

        print(f"{len(ready_code)} new methods loaded")
        return self.get_recent(len(ready_code), 'algorithms_temp')

if __name__ == '__main__':
    print(fromTheOverflow().run("print list"))
