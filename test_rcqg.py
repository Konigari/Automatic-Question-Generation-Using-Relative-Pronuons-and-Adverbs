import spacy
import yaml

import rcqg

nlp = spacy.load('en')
qg = rcqg.WHQuestionGenerator(nlp)


def loadTests():
    try:
        testfile = open('test.txt', 'r')
    except:
        testfile = open('test.txt', 'w')
        testfile.write(yaml.dump([]))
        testfile.close()
        testfile = open('test.txt', 'r')
    return testfile


def generate_test(line):
    tests = yaml.load(loadTests())
    result = next(filter(lambda x: x["Sentence"] == line, tests), False)
    if result:
        result['Questions'] = qg.genqlist(line)
    else:
        temp = {
            'Sentence': line,
            'Questions': qg.genqlist(line)
        }
        tests += [temp]
    testfile = open('test.txt', 'w')
    testfile.write(yaml.dump(tests))

def update_all_tests():
    tests = yaml.load(loadTests())
    for i in tests:
        generate_test(i['Sentence'])

def test_rcqg():
    tests = yaml.load(loadTests())
    for i in tests:
        count = len(i['Questions'])
        counter = 0
        for j in qg.genqlist(i['Sentence']):
            counter += 1
            assert (j in i['Questions']), "Wrong Question" + i['Sentence']
        assert (count == counter), "Wrong number of questions" + str(qg.genqlist(i['Sentence'])) + "From Sentence: " + \
                                   i['Sentence']
