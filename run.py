import spacy
from rcqg import WHQuestionGenerator
from test_rcqg import generate_test

nlp = spacy.load('en')
qg = WHQuestionGenerator(nlp)

from IPython import get_ipython

ipython = get_ipython()

ipython.magic("%load_ext autoreload")
ipython.magic("%autoreload 2")
