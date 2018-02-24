import inspect

import spacy
from spacy import displacy
import ipdb

nlp = spacy.load('en')


def filetotext():
    return open("temp.txt", "r").read()


def show(u_line):
    doc = nlp(u_line)
    print("=========================Sentence -", u_line)
    print("=========================Tokens and POS tags")
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
    print("=========================NER tags")
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
    print("=========================Noun Chunks tags")
    for c in doc.noun_chunks:
        print(c.text)
    print("=========================SENTENCE DONE")


def display(u_line):
    doc = nlp(u_line)
    displacy.serve(doc, style='dep',port = 8080)


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
    return lambda x: set(d2.items()).issubset(set(serialize(x).items()))


def filteratt(att, doc):
    return (list(filter(lambda tup: filt(att)(tup), doc)))


def genq(sentence):
    doc = nlp(sentence)

    relativeclauseswh = filteratt({
        'tag_': 'WP',
    }, doc)

    loc_relative_clause = 0
    for wpword in relativeclauseswh:
        answer = wpword.head.head
        matrix = doc[loc_relative_clause:answer.head.i + 1]
        relclause = doc[wpword.i:]

        if wpword.text.lower() == 'who':
            # print(wpword.text.capitalize() + " " + " ".join([x.text for x in doc[wpword.i + 1:]]) + "?")

            # Find Requirements
            pasttenseverb = filteratt({
                'tag_': 'VBD',
                #'dep_': 'ROOT'
            }, matrix)
            presentcontinuousverb = filteratt({
                'tag_': 'VBG',
                #'dep_': 'ROOT'
            }, matrix)
            pastparticiple = filteratt({
                'tag_': 'VBN',
                #'dep_': 'ROOT'
            }, matrix)
            presentsimple = filteratt({
                'tag_': 'VBP',
                #'dep_': 'ROOT'
            }, matrix)
            presentsimplethird = filteratt({
                'tag_': 'VBZ',
                #'dep_': 'ROOT'
            }, matrix)


            # Rules
            if len(pasttenseverb) > 0:
                pasttenseverb = pasttenseverb[0]
                end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                converted = [x.text for x in doc[loc_relative_clause:pasttenseverb.i]] + [pasttenseverb.lemma_] + [x.text for x in doc[
                                                                                                      pasttenseverb.i + 1:end]]
                print("Whom " + "did " + " ".join(converted) + '?')

            if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0:
                aux = filteratt({
                    'dep_': 'aux'
                }, matrix)[0]
                end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                converted = [aux.text] + [x.text for x in doc[loc_relative_clause:aux.i]] + [x.text for x in doc[aux.i + 1:end]]
                print("Whom %(kwarg)s?" % {'kwarg': " ".join(converted)})
                
            if len(presentsimple) > 0:
                presentsimple = presentsimple[0]
                end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                converted = [x.text for x in doc[loc_relative_clause:presentsimple.i]] + [presentsimple.lemma_] + [x.text for x in doc[
                                                                                                                 presentsimple.i + 1:end]]
                print("Whom " + "do " + " ".join(converted) + '?')
            if len(presentsimplethird) > 0:
                presentsimplethird = presentsimplethird[0]
                end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                converted = [x.text for x in doc[loc_relative_clause:presentsimplethird.i]] + [presentsimplethird.lemma_] + [x.text for x in doc[
                                                                                                                 presentsimplethird.i + 1:end]]
                print("Whom " + "does " + " ".join(converted) + '?')

            # print(wpword.text.capitalize() + " " + " ".join([x.text for x in doc[wpword.i + 1:]]) + "?")
            # print (wpword.text)
            # print("hello")
            #print(relclause)
            # Find Requirements
            pasttenseverb = filteratt({
                'tag_': 'VBD',
                'dep_': 'relcl'
            }, relclause)
            presentcontinuousverb = filteratt({
                'tag_': 'VBG',
                'dep_': 'relcl'
            }, relclause)
            pastparticiple = filteratt({
                'tag_': 'VBN',
                'dep_': 'relcl'
            }, relclause)
            presentsimple = filteratt({
                'tag_': 'VBP',
                'dep_': 'relcl'
            }, relclause)
            presentsimplethird = filteratt({
                'tag_': 'VBZ',
                'dep_': 'relcl'
            }, relclause)

            if wpword.dep_ == "nsubj":
                print(wpword.text.capitalize() + " " + " ".join([x.text for x in doc[wpword.i + 1:]]) + "?")
                loc_relative_clause = wpword.i
            else:
                #   # # Rules
                if len(pasttenseverb) > 0:
                    #print ("here")
                    pasttenseverb = pasttenseverb[0]
                    #print(pasttenseverb)
                    # print ([x.text for x in doc[wpword.i + 1:pasttenseverb.i ]]+ [pasttenseverb.lemma_])
                    converted = [x.text for x in doc[wpword.i + 1:pasttenseverb.i]] + [pasttenseverb.lemma_] + [x.text
                                                                                                                for x in
                                                                                                                doc[
                                                                                                                    pasttenseverb.i+1:]]
                    print("Whom " + "did " + " ".join(converted) + '?')

                if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0:
                    aux = filteratt({
                        'dep_': 'aux',
                    }, relclause)
                    aux += filteratt({
                        'dep_': 'auxpass',
                    }, relclause)
                    aux = aux[0]

                    #end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                    converted = [aux.text] + [x.text for x in doc[wpword.i + 1:aux.i]] + [x.text for x in doc[aux.i + 1:]]
                    print("Whom %(kwarg)s?" % {'kwarg': " ".join(converted)})

                if len(presentsimple) > 0:
                    presentsimple = presentsimple[0]
                    converted = [x.text for x in doc[wpword.i + 1:presentsimple.i]] + [presentsimple.lemma_] + [x.text
                                                                                                                for x in doc[
                                                                                                                     presentsimple.i + 1:]]
                    print("Whom " + "do " + " ".join(converted) + '?')
                if len(presentsimplethird) > 0 :
                    presentsimplethird = presentsimplethird[0]
                    converted = [x.text for x in doc[wpword.i + 1:presentsimplethird.i]] + [
                        presentsimplethird.lemma_] + [x.text for x in doc[
                                                                                                                     presentsimplethird.i+1:]]
                    print("Whom " + "does " + " ".join(converted) + '?')


                # Ram has eaten all the fruits that were left for Sita who is his sister
                    # Who is his sister?
                # Who has eaten?

            loc_relative_clause = wpword.i
