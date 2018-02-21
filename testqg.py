import rcqg
x = open('Sentences/sentences.txt')
for line in x:
    print("Sentence: "+ line)
    print("Questions: \n")
    rcqg.genq(line)