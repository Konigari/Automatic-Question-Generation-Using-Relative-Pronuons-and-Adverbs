import spacy
import inspect
from spacy import displacy
import ipdb
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

def recursePrint(obj):
	l = []
	for i in obj.lefts:
		x = recursePrint(i.children)
		l.append(x)
	l.append(obj.text)
	for i in obj.rights:
		x = recursePrint(i.children)
		l.append(x)
	return l

def serialize(obj):
	return {
		'tag_': obj.tag_,
		'dep_': obj.dep_,
		'pos_': obj.pos_,

	}

def filt(d2):
	return lambda x:set(d2.items()).issubset(set(serialize(x).items()))

def filteratt(att, doc):
	return (list(filter(lambda tup: filt(att)(tup), doc)))


def genq(sentence):

	doc = nlp(sentence)

	relativeclauseswh = filteratt({
		'tag_' : 'WP',
		'dep_' : 'nsubj'
	}, doc)
	rootofrelclause = filteratt({
		'dep_':'relcl'
		}, doc)
	answer = rootofrelclause[0].head

	for relclause in relativeclauseswh:
		if relclause.text.lower()=='who':
			print(relclause.text + " " + " ".join([x.text for x in doc[relclause.i+1:]])+"?")
			beginning = doc[0:answer.head.i]
			#convert verb to lemma
			pasttenseverb = filteratt({
				'tag_':'VBD',
				'dep_':'ROOT'
				}, beginning)

			if len(pasttenseverb)>0:
				pasttenseverb = pasttenseverb[0]
				end = answer.head.i+1 if answer.head.dep_=="prep" else answer.head.i
				converted = [x.text for x in doc[0:pasttenseverb.i]] + [pasttenseverb.lemma_] + [x.text for x in doc[pasttenseverb.i+1:end]]
				print("Who "+"did "+ " ".join(converted) + '?')
						
					
	# relativeclause = 

	## who did they give the chocolate t