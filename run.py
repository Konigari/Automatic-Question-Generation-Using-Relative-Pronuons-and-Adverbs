import spacy
from rcqg import WHQuestionGenerator

nlp = spacy.load('en')
qg = WHQuestionGenerator(nlp)

from IPython import get_ipython

ipython = get_ipython()

ipython.magic("%load_ext autoreload")
ipython.magic("%autoreload 2")
