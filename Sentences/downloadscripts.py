import nltk

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
