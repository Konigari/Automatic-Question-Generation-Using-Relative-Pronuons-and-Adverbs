import spacy
from rcqg import WHQuestionGenerator

nlp = spacy.load('en')
qg = WHQuestionGenerator(nlp)
