import spacy
nlp = spacy.load('en')

def filetotext():
	return open("temp.txt","r").read()

def show(u_line):
	doc = nlp(u_line)	
	print("Sentence -" ,u_line) 
	print("Tokens and POS tags")
	for token in doc:
	    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,token.shape_, token.is_alpha, token.is_stop)					
	print("NER tags")
	doc = nlp(u_line)	
	for ent in doc.ents:
		print(ent.text, ent.start_char, ent.end_char, ent.label_) 
	print("SENTENCE DONE")