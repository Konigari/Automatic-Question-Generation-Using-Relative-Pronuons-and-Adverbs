import nltk

import language_check

tool = language_check.LanguageTool('en-US')

from IPython import get_ipython

ipython = get_ipython()

ipython.magic("%load_ext autoreload")
ipython.magic("%autoreload 2")

notbrowntags = ['WDT', 'WP', 'WP$', 'WRB']

tags = ['WPO', 'WPS', 'WQL', 'WRB']

brown_tags = ['WDT', 'WP$', 'WPO', 'WPS', 'WQL', 'WRB']



def brown(new_tags):
    sents = nltk.corpus.brown.tagged_sents()
    filteredsents = (filter(lambda sent: next(filter(lambda x: (x[1] in new_tags), sent), False), sents))
    filename = "brown_filtered.txt"
    print(len(list(filteredsents)))
    with open(filename, 'w') as file:
        for i in filteredsents:
            file.write(" ".join(nltk.untag(i)) + "\n")
    file.close()


def genbrownquestions():
    import rcqg
    import spacy
    nlp = spacy.load('en')
    filename = "brown_filtered.txt"
    qg = rcqg.WHQuestionGenerator(nlp)
    failedfile = open('failedbrown', 'w')
    writefile = open('brownquestions', 'w')
    with open(filename, 'r') as file:
        print("started")
        count = 0
        for filteredsent in file:
            count += 1
            print("Current count: ", count)
            try:
                for question in qg.genqlist(filteredsent):
                    writefile.write(question + '\n')
            except:
                failedfile.write(filteredsent)
        writefile.close()
        failedfile.close()
        file.close()


def grammarcheck():
    successfile = open('successgrammarbrown', 'w')
    failedfile = open('failedgrammarbrown', 'w')
    questionfile = open('brownquestions', 'r')
    print("started")
    count = 0
    for filteredsent in questionfile:
        count += 1
        print("Current count: ", count)
        if len(tool.check(filteredsent)) > 0:
            failedfile.write(filteredsent)
        else:
            successfile.write(filteredsent)
    successfile.close()
    questionfile.close()
    failedfile.close()
