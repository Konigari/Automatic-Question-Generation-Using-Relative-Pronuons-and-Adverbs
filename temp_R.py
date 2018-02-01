import spacy

nlp = spacy.load('en') 
#sentences = list(doc.sents)
doc = nlp(u'The big fat boy ate a sandwich while running behind a bus to help the poor sick kids')
for token in doc:
    print(token.i, token.ent_type_ , token.text, token.dep_, token.head.text, token.head.pos_,
          [child for child in token.children])
    
    

# give_nbor = doc[0].nbor()
# print give_nbor

