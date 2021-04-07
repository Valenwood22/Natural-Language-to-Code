__authors__ = "Dr. Malik Mohammad Zubair and Joshua Gisi "
__copyright__ = ""
__credits__ = ["Malik Mohammad Zubair", "Joshua Gisi"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Joshua Gisi"
__email__ = "Joshua.Gisi22@gmail.com"
__status__ = "Development"

import os
from pathlib import Path

import spacy
from spacy import displacy
from nltk.stem import LancasterStemmer


class dataType:
    def __init__(self, name=None, type=None, subType=None, isList=False ):
        if name is not None:
            self.name = ''.join(e for e in name if e.isalnum())
        else:
            self.name = name
        self.type = type
        self.subType = subType
        self.isList = isList

    def __str__(self):
        if self.name is None or self.name == "":
            n = "'unknown'"
        else:
            n = self.name
        if self.type is None:
            t = "'unknown'"
        else:
            t = self.type
        if self.isList:
            return f'name: {n} type: list of {t}'
        if self.type == "No Output":
            return "No Output"
        return f'name: {n} type: {t}'


# noinspection PyUnresolvedReferences
class parser:
    def __init__(self):
        self.dataTypes = {"string", "strings", "integer", "integers", "float", "floats", "list", "array", "dictionary", "boolean", "booleans", "set", "tuple", "tuples"}
        self.inputs = {'given', 'find'}
        self.outputs = {'return'}
        self.actions = {'add', 'reverse', 'convert', 'is'}
        self.actions_interpreter = {'remov':'remove', 'revers':'reverse', 'giv':'given'}
        self.stopwords = {'signed'}
        self.nlp = spacy.load('en_core_web_sm')



    def parse(self, prompt):
        doc = self.nlp(prompt)
        parts = self.splitByVerbs(doc)
        return self.predictLabel(parts)

        # input_data = self.findInputData(doc)
        # output_data = self.findOutputData(doc, input_data)
        #
        # for t in input_data:
        #     print(t)
        # print('===')
        # print(output_data)
        # self.display(doc)

    def splitByVerbs(self, doc):
        ans = []
        cur = []
        for t in doc:
            if t.text in self.stopwords:
                continue
            if t.pos == spacy.symbols.VERB or t.pos == spacy.symbols.PROPN:
                ans.append(cur)
                cur = []
                cur.append(t)
            elif t.pos == spacy.symbols.NOUN or t.pos == spacy.symbols.CCONJ or t.pos == spacy.symbols.SYM or\
                    t.pos == spacy.symbols.X or t.pos == spacy.symbols.ADJ or t.pos == spacy.symbols.ADP:
                cur.append(t)
        ans.append(cur)
        return ans[1:]

    def extractDatatypes(self, s):
        split = []
        temp = []
        for t in s:
            if t.text == 'and':
                split.append(temp)
                temp = []
            else:
                temp.append(t)
        split.append(temp)

        dataTypes = []
        for dt in split:
            isList = False
            name = ""
            type = None
            for word in dt:
                if word.text.lower() in ['list', 'array']:
                    isList = True
                elif word.text.lower() in self.dataTypes:
                    type = word.text
                elif word.pos == spacy.symbols.NOUN and word.dep_ != 'compound':
                    name = word.text
                elif word.pos == spacy.symbols.SYM or word.pos == spacy.symbols.X:
                    name = word.text
                elif t.pos == spacy.symbols.ADJ:
                    name += word.text + " "
            dataTypes.append(dataType(name=name,type=type,isList=isList))
        return dataTypes




    def predictLabel(self, sentences):
        # def convert_str(arr):
        #     print(arr)
        #     for i in range(1,len(arr)):
        #         arr[i] = arr[i].text
        #     return arr

        inputs = []
        outputs = []
        actions = []
        wordnet_lemmatizer = LancasterStemmer()
        for s in sentences:
            format_s = wordnet_lemmatizer.stem(s[0].text.lower())
            # print(s)
            if format_s in self.actions_interpreter:
                format_s = self.actions_interpreter[format_s]
            # print(format_s)
            if format_s in self.inputs:
                # print('Inputs:', self.printS(s))
                # print(self.printDt(self.extractDatatypes(s[1:])))
                inputs.extend(self.extractDatatypes(s[1:]))
            elif format_s in self.outputs:
                # print('Outputs:', self.printS(s))
                # print(self.printDt(self.extractDatatypes(s[1:])))
                outputs.extend(self.extractDatatypes(s[1:]))
            else:
                # if format_s in self.actions:
                s[0] = format_s
                actions.append(s)

        # convert spacy token to strings
        for action in actions:
            for i in range(1,len(action)):
                action[i] = action[i].text

        return inputs, outputs, actions



    def printS(self, tl):
        s = ""
        for word in tl:
            s += word.text + " "
        return s



    def printDt(self, dtObj):
        s = ""
        for obj in dtObj:
            s += str(obj) + "    "
        return s



    def display(self, prompt):
        doc = self.nlp(prompt)
        svg = displacy.render(doc, style='dep')
        output_path = Path(os.path.join("./", "SentenceDecompositions/custom1.svg"))
        output_path.open('w', encoding="utf-8").write(svg)




    def cleaning(self, doc):
        return



    def print_specialdata(self, data, label=""):
        print(f"num {label}: {len(data)}")
        for d in data:
            print(d)

if __name__ == '__main__':
    engine = parser()
    # engine.display('Given a list and an integer x. Remove x from the list')
    # top_50_Leet = open('N:\\_Programming\\nltc\\data\\LeetCode_Easy_dataset.txt')
    # p1 = top_50_Leet.readline()
    p1 = 'Given an array nums. Return the running sum of nums.'
    # p2 = top_50_Leet.readline()
    # p3 = top_50_Leet.readline()
    # p4 = top_50_Leet.readline()
    # p5 = top_50_Leet.readline()
    print(p1)
    inputs, outputs, actions = engine.parse(p1)
    engine.print_specialdata(inputs, "Inputs")
    print("===================================")
    engine.print_specialdata(outputs, "Outputs")

    print("===================================")
    # actions = [["two", "numbers", "add", "up", "to", "target"]]
    print(actions)

