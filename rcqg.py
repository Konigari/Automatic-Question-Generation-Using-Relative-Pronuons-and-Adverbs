import spacy
import inspect
from spacy import displacy
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

def display(u_line):
	doc = nlp(u_line)	
	displacy.serve(doc, style='dep')

def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr

def genq(sentence):
	def serialize(obj):
		return {
			'tag_': obj.tag_,
			'dep_': obj.dep_,
			'pos_': obj.pos_,

		}

	def filt(d2):
		return lambda x:set(d2.items()).issubset(set(serialize(x).items()))

	def filteratt(att, doc):
		return (list(filter(lambda tup: filt(att)(tup[1]), enumerate(doc))))

	doc = nlp(sentence)

	att = {
		'tag_' : 'WP',
		'dep_' : 'nsubj'
	}
	relativeclauses = filteratt(att, doc)
	for word in relativeclauses:
		index = word[0]
		relclause = word[1]
		print(word[1].text + " " + " ".join(sentence.split(" ")[index+1:])+"?")
		verb_past = filteratt({
			'tag_':'VBD',
			'dep_':'ROOT'
			}, doc)
		for verb in verb_past:
			if relclause.text.lower()=='who':
				print("Who "+"did "+ next(doc.noun_chunks).text + " " + verb[1].lemma_ + " " + "to meet")

	# relativeclause = 

	## who did they give the chocolate t