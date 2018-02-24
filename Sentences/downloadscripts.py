import nltk

notbrowntags = ['WDT', 'WP', 'WP$', 'WRB']

tags = ['WPO', 'WPS', 'WQL', 'WRB']

new_tags = ['WDT', 'WP$', 'WPO', 'WPS', 'WQL', 'WRB']


def brown():
    sents = nltk.corpus.brown.tagged_sents()
    print(next(filter(lambda sent: next(filter(lambda x: (x[1] in new_tags), sent), False), sents)))
