import spacy
from rcqg import WHQuestionGenerator
from test_rcqg import generate_test

nlp = spacy.load('en')
qg = WHQuestionGenerator(nlp)

from IPython import get_ipython

ipython = get_ipython()

ipython.magic("%load_ext autoreload")
ipython.magic("%autoreload 2")


def testmultiple(sentences):
    sentences = sentences.split("\n")
    failedfile = open('failedbrown', 'w')
    for i in sentences:
        i = i.strip()
        print(i)
        print(qg.genqlist(i))
        result = input("Correct? or Not? (y/n)")
        if result == "y":
            generate_test(i)
        else:
            failedfile.write(i)
    return


sl = qg.showlast
dl = qg.displaylast
gl = qg.genqlistlast
