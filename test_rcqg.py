import rcqg
import spacy
import yaml

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
    temp = {
        'Sentence': line,
        'Questions': qg.genqlist(line)
    }
    tests += [temp]
    testfile = open('test.txt', 'w')
    testfile.write(yaml.dump(tests))


def test_rcqg():
    tests = yaml.load(loadTests())
    for i in tests:
        count = len(i['Questions'])
        counter = 0
        for j in qg.genq(i['Sentence']):
            counter += 1
            assert (j in i['Questions']), "Wrong Question"
        assert (count == counter), "Wrong number of questions"
