import spacy

from rcqg import WHQuestionGenerator

print("Loading Model...")
nlp = spacy.load('en')
qg = WHQuestionGenerator(nlp)

while True:
    sentence = input("Enter a sentence with atleast one relative clause: ")
    print("============ Generated Questions: ============")
    questions = qg.genqlist(sentence)
    for i in questions:
        print(i)
    print("============ Done ============")
