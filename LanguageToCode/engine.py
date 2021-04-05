__authors__ = "Dr. Malik Mohammad Zubair and Joshua Gisi "
__copyright__ = ""
__credits__ = ["Malik Mohammad Zubair", "Joshua Gisi"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Joshua Gisi"
__email__ = "Joshua.Gisi22@gmail.com"
__status__ = "Development"

import sqlite3
import os
import subprocess
from collections import defaultdict

from Parseing_Data_Actions import parser
from Parseing_Data_Actions import dataType
from collections import OrderedDict
from StackOverflowFetch import fromTheOverflow

class codeObj:
    def __init__(self, data, indents):
        self.data = data
        self.indents = indents

    def __str__(self):
        return f"w {self.indents} : {self.data}"

class engine:
    def __init__(self):
        self.tag_library = {}
        self.database_filepath = "N:\\_Programming\\nltc\\data\\algorithms.db"
        self.db_key = {'PID':0, 'name':1, 'payload':2, 'call':3, 'parameters':4, 'return':5}
        self.shortenedWords = defaultdict(str,{'int':'integer', 'str':'string', 'bool':'boolean'})
        self.interchangeableWords = defaultdict(str, {'int': 'integer', 'str': 'string', 'bool': 'boolean', 'integer': 'int', 'string': 'str', 'boolean': 'bool'})


    def load_empty_template_as_list(self):
        template = open('N:\\_Programming\\nltc\\data\\EmptyTemplate.tmplt','r')
        templateList = []
        self.tag_library.clear()
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



    def update_tag_indexes(self, baseCode):
        for i, line in enumerate(baseCode):
            if line.data[0:4] == "#TAG":
                self.tag_library[line.data] = i



    def set_inputs(self, baseCode, inputs):
        runIndx = None
        var_iterator = 0
        for i, line in enumerate(baseCode): # fine the end code args code
            if line.data == 'def run(self #TAG-ARGS):':
                runIndx = i
        # format inputs
        str_ins = ""

        for input in inputs:
            # print(input.name)
            if input.name is None or input.name == "":
                name = "var" + str(var_iterator)
                input.name = name
                var_iterator += 1
            else:
                name = input.name
            str_ins += f",{name}"
        baseCode[runIndx].data = baseCode[runIndx].data.replace('#TAG-ARGS', str_ins)
        return baseCode



    def set_output(self, baseCode, outputs):
        runIdnx = self.tag_library['#TAG-RUN']
        if baseCode[runIdnx-1].data[:3] == 'def':
            return baseCode
        else:
            baseCode[runIdnx-1].data = 'return ' + baseCode[runIdnx-1].data
        return baseCode



    def evolve_vars(self, combinedCode, inputs):

        def find_predictions(param, input_pool, shortenedWords):
            ans = []
            param_type = param.split('-')[-1]
            param_type = param_type.strip()
            if param_type == 'VAR':
                return input_pool
            else:
                for input in input_pool:
                    if input.isList and param_type.lower() == 'list':
                        ans.append(input)
                    elif str(input.type).lower() == param_type.lower() or shortenedWords[str(input.type).lower()] == param_type.lower():
                        ans.append(input)
                if len(ans) == 0:
                    return input_pool
            return ans

        # 1. Extract the run method
        runIndx = None
        for i, line in enumerate(combinedCode): # fine the end code args code
            if line.data[:8] == 'def run(':
                runIndx = i
        run_script = combinedCode[runIndx:self.tag_library['#TAG-RUN']]
        input_pool = inputs
        to_try = OrderedDict()
        to_try_ticker = []
        newVarCntr = 0
        for i, run_line in enumerate(run_script): # INPUTS MUST ALREADY BE IN PLACE!
            # 2. Find holes
            if '#TAG-VAR' in run_line.data:
                # print(run_line.data)
                call, extracted = run_line.data.split('(')
                extracted = extracted.split(')')[0]
                params = extracted.split(',')
                if run_line.data[:6] != 'return':
                    newvar = 'localVar' + str(newVarCntr)
                    run_line.data = newvar + '=' + run_line.data
                    newVarCntr += 1
                for j, param in enumerate(params):
                    # print(j, param)
                    to_try[f'{runIndx+i}_{j}'] = find_predictions(param, input_pool, self.interchangeableWords)

                    to_try_ticker.append(len(to_try[f'{runIndx+i}_{j}']))

                if run_line.data[:6] != 'return':
                    input_pool.append(dataType(name=newvar))

        # print(to_try)
        # print(to_try_ticker)
        to_try_tracker = [0] * len(to_try_ticker)
        while to_try_ticker[0] > to_try_tracker[0]:
            i = len(to_try_tracker) - 1

            while to_try_tracker[i] >= to_try_ticker[i]:
                to_try_tracker[i] = 0
                i -= 1
                to_try_tracker[i] += 1
                if i == 0: break

            if to_try_tracker[0] >= to_try_ticker[0]: break

            s = []
            j = 0
            last = '-1'
            for key, item in to_try.items():
                if key[0] == last or last == '-1':
                    s.append(item[to_try_tracker[j]])
                else:
                    # flush s
                    insert = ','.join([d.name for d in s])
                    insert = f'({insert})'
                    combinedCode[int(last.split('_')[0])].data = combinedCode[int(last.split('_')[0])].data.split('(')[0] + insert
                    s.clear()
                    s.append(item[to_try_tracker[j]])
                last = key[0]
                j += 1

            # print(to_try_tracker)
            to_try_tracker[-1] += 1
            insert = ','.join([d.name for d in s])
            insert = f'({insert})'
            combinedCode[int(last.split('_')[0])].data = combinedCode[int(last.split('_')[0])].data.split('(')[0] + insert

            #################### Run and Get Results #####################
            print()
            print("5: Compile Check  =========================")
            self.write_code_from_list('out.py', combinedCode)

            if self.compile_new_code('out.py') == "":
                print("Compile Successful")
                print()
                print("6: Run Test Cases  ========================")
                result = self.run_test_cases('out.py', [([1, 2, 3, 4], 3), ([151, 1531, 1763, 41632], 151), ([2], 2), ([-1, 2, 45, 3], 3)])
                if result == "next method": break
                elif result == "passed cases": return "successful", combinedCode
            print("Compile Failed")
            ##############################################################

        return "failed", combinedCode



    def evolve(self, pools, test_cases):
        methods_in_solution = len(pools)
        token_methods = []
        token_calls = []
        combinedCode = None
        # print("number of method in solution", methods_in_solution)
        ######### Load Template as Token and Predicted Code ##########
        print()
        print("4: Code from Docs Selected  ===============")
        for data in pools:
            temp_method = []
            temp_call = []
            for row in data:
                temp_method.append(self.load_code_as_list(row[2]))
                temp_call.append(self.load_code_as_list(row[3]))
            token_methods.append(temp_method)
            token_calls.append(temp_call)
        ##############################################################

        ################## Combining Code loop #######################
        combo_counter = [len(row) for row in token_calls]
        combo_tracker = [0] * len(combo_counter)
        while combo_counter[0] > combo_tracker[0]:
            #################### Handle Input Args #######################
            baseCode = self.load_empty_template_as_list()
            combinedCode = self.set_inputs(baseCode, inputs)
            ##############################################################
            print(combo_tracker)
            i = len(combo_tracker)-1

            while combo_tracker[i] >= combo_counter[i]:
                combo_tracker[i] = 0
                i-=1
                combo_tracker[i] += 1
                if i == 0: break

            if combo_tracker[0] >= combo_counter[0]: break

            for method_index in range(methods_in_solution):
                combinedCode = self.combine(combinedCode, token_methods[method_index][combo_tracker[method_index]], 'METHOD')
                combinedCode = self.combine(combinedCode, token_calls[method_index][combo_tracker[method_index]], 'RUN')

            ###################### Handle Output #########################
            combinedCode = self.set_output(combinedCode, outputs)
            ##############################################################

            ####################### evolve Vars ##########################
            message, combinedCode = driver.evolve_vars(combinedCode, inputs)
            if message == 'successful': break
            ##############################################################

            combo_tracker[i] += 1

        ##############################################################
        return combinedCode



    def write_code_from_list(self, filename, code):
        outFile = open(filename, 'r+')
        outFile.truncate(0)
        for line in code:
            outFile.write(' '*line.indents+line.data+'\n')
        outFile.close()



    def compile_new_code(self, filename):
        cmd = 'python ' + filename
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout.decode('utf-8'))
        if stderr:
            print(stderr.decode('utf-8'))
        return stderr.decode('utf-8')



    def nlp_user_query(self, query):
        parseEngine = parser()
        return parseEngine.parse(query)



    def query_database(self, prompt):
        database = sqlite3.connect(self.database_filepath)
        cursor = database.cursor()
        cursor.execute("SELECT * FROM 'algorithms'")
        payload = cursor.fetchall()
        return payload[0]



    def collect_pool(self, actions, live=True, num=1):
        # Returns a 2d array where the fist dimension is the actions and the second is the order
        pool = []
        ftf = fromTheOverflow()
        for action in actions:
            temp = []
            docs_return = driver.predict_from_docs(action, 'algorithms')
            if len(docs_return) == 0:
                temp = ftf.run(''.join(action), live=live, num=num)
            else:
                temp = docs_return
            pool.append(temp)
        return pool



    def predict_from_docs(self, action, table_name):
        database = sqlite3.connect(self.database_filepath)
        cursor = database.cursor()
        predictions = []
        top = action[0]
        query = f"SELECT * FROM '{table_name}' WHERE name LIKE '{top}' "
        bottoms = action[1:]
        for bottom in bottoms:
            query += f"OR name LIKE '{top} {bottom}'"
        # print(query)
        cursor.execute(query)
        payloads = cursor.fetchall()
        if payloads:
            for payload in payloads:
                predictions.append(payload)
        cursor.close()
        return predictions



    def combine(self, baseCode, predictSolution, tag):
        indexOfTag = self.tag_library['#TAG-'+tag]
        parentIndent = baseCode[indexOfTag].indents
        for line in predictSolution[::-1]:
            line.indents += parentIndent
            baseCode.insert(indexOfTag, line)
        self.update_tag_indexes(baseCode)
        return baseCode



    def run_test_cases(self, filename, cases):
        name = filename.split('.')[0]
        out = getattr(__import__(name), 'Solution')
        ref = out()
        for case in cases:
            try:
                print(ref.run(case[0],case[1]))
                return "passed cases"
            except Exception as e:
                print(e)
                return "next method"


    def print_specialdata(self, data, label=""):
        print(f"num {label}: {len(data)}")
        for d in data:
            print(d)
        # print(' ================ ')



if __name__ == '__main__':
    # top_50_Leet = open('N:\\_Programming\\openai\\data\\LeetCode_Easy_dataset.txt')
    # p1 = top_50_Leet.readline()
    # p2 = top_50_Leet.readline()
    # p3 = top_50_Leet.readline()
    # p4 = top_50_Leet.readline()
    # p5 = top_50_Leet.readline()

    driver = engine()

    # inputs, outputs, actions = driver.nlp_user_query("Given a list and an integer x. Remove every x from the list") # "Given a list and an integer x. Return True if x is in the list"
    inputs, outputs, actions = driver.nlp_user_query("Given a list and an integer x. Remove every x from the list. Then print the list")
    print("1: Predicted Inputs and Outputs ===========")
    driver.print_specialdata(inputs, 'inputs')
    driver.print_specialdata(outputs, 'outputs')
    print()
    print("2: Predicted Actions ======================")
    print(actions)

    ######################## Create pools ########################
    print()
    print("3: Suggested Code =========================")
    pools = driver.collect_pool(actions, live=False, num=4)
    print(pools)
    # ############################################################

    ##################### Begin the Evolution ####################
    driver.evolve(pools, [([1, 2, 3, 4], 3), ([151, 1531, 1763, 41632], 151), ([2], 2), ([-1, 2, 45, 3], 3)])
    ##############################################################
