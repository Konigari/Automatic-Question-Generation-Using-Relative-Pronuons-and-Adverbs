import csv

import yaml

f = open('test1.yaml')
w = open('csv.csv', 'w')
obj = yaml.load(f)
cw = csv.writer(w)
cols = ['sentence index', 'question index', 'sentence', 'question', 'relevance', 'syntactic correctness', 'ambiguity',
        'variety']
cw.writerow(cols)
count = 0
for ind, i in enumerate(obj):
    first = True
    for index, question in enumerate(i['questions']):
        if first:
            first = False
            cw.writerow([ind, index, i['sentence'], question])
        else:
            cw.writerow([ind, index, "", question])

w.close()
