import spacy
import inspect
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

def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr

def genq(sentence):
	def getAtt(obj):
		return {
			'tag_': obj.tag_,
			'dep_': obj.dep_
		}

	def filt(d2):
		return lambda x:set(getAtt(x).items()).issubset(set(d2.items()))

	doc = nlp(sentence)
	att = {
		'tag_' : 'WP',
		'dep_' : 'nsubj'
	}
	words = (list(filter(lambda tup: filt(att)(tup[1]), enumerate(doc))))
	word = words[0]
	index = word[0]
	print(word[1].text + " " + " ".join(sentence.split(" ")[index+1:])+"?")

	## who did they give the chocolate to