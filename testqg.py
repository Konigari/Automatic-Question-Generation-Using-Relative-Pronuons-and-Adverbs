import rcqg
import spacy

nlp = spacy.load('en')
qg = rcqg.WHQuestionGenerator(nlp)
x = open('Sentences/sentences.txt')
for line in x:
    print("Sentence: "+ line)
    print("Questions: \n")
    qg.genq(line)
