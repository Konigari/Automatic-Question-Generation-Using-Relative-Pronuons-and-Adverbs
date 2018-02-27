import inspect
import copy
import spacy
from spacy import displacy
import ipdb

def filetotext():
    return open("temp.txt", "r").read()


class WHQuestionGenerator():
    def __init__(self, nlp):
        self.nlp = nlp

    def show(self, u_line):
        doc = self.nlp(u_line)
        print("=========================Sentence -", u_line)
        print("=========================Tokens and POS tags")
        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha,
                  token.is_stop)
        print("=========================NER tags")
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
        print("=========================Noun Chunks tags")
        for c in doc.noun_chunks:
            print(c.text)
        print("=========================SENTENCE DONE")

    def display(self, u_line):
        doc = self.nlp(u_line)
        displacy.serve(doc, style='dep', port=8080)

    def props(self, obj):
        pr = {}
        for name in dir(obj):
            value = getattr(obj, name)
            if not name.startswith('__') and not inspect.ismethod(value):
                pr[name] = value
        return pr

    def serialize(self, obj):
        return {
            'tag_': obj.tag_,
            'dep_': obj.dep_,
            'pos_': obj.pos_,
        }

    def filt(self, d2):
        return lambda x: set(d2.items()).issubset(set(self.serialize(x).items()))

    def expand(self, d, i=0):
        if i >= len(d.keys()):
            return [d]
        ind, val = list(d.items())[i]
        result = []
        if type(val) == list:
            for option in val:
                temp = copy.deepcopy(d)
                temp[ind] = option
                result += self.expand(temp, i + 1)
        else:
            result += self.expand(d, i + 1)
        return result

    def filteratt(self, att, doc):
        att = self.expand(att)
        if len(att) == 1:
            att = att[0]
        if type(att) == list:
            return sum([self.filteratt(i, doc) for i in att], [])
        return list(filter(lambda tup: self.filt(att)(tup), doc))

    def genq(self, sentence):
        doc = self.nlp(sentence)

        relativeclauseswh = self.filteratt({
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
                pasttenseverb = self.filteratt({
                    'tag_': 'VBD',
                    # 'dep_': 'ROOT'
                }, matrix)
                presentcontinuousverb = self.filteratt({
                    'tag_': 'VBG',
                    # 'dep_': 'ROOT'
                }, matrix)
                pastparticiple = self.filteratt({
                    'tag_': 'VBN',
                    # 'dep_': 'ROOT'
                }, matrix)
                presentsimple = self.filteratt({
                    'tag_': 'VBP',
                    # 'dep_': 'ROOT'
                }, matrix)
                presentsimplethird = self.filteratt({
                    'tag_': 'VBZ',
                    # 'dep_': 'ROOT'
                }, matrix)

                # Rules

                if len(pasttenseverb) > 0:
                    pasttenseverb = pasttenseverb[0]
                    end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                    converted = [x.text for x in doc[loc_relative_clause:pasttenseverb.i]] + [pasttenseverb.lemma_] + [
                        x.text for x in doc[
                                        pasttenseverb.i + 1:end]]
                    print("Whom " + "did " + " ".join(converted) + '?')


                if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0:
                    aux = self.filteratt({
                        'dep_': ['aux', 'auxpass']
                    }, matrix)[0]
                    end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                    converted = [aux.text] + [x.text for x in doc[loc_relative_clause:aux.i]] + [x.text for x in
                                                                                                 doc[aux.i + 1:end]]
                    print("Whom %(kwarg)s?" % {'kwarg': " ".join(converted)})


                if len(presentsimple) > 0:
                    presentsimple = presentsimple[0]
                    end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                    converted = [x.text for x in doc[loc_relative_clause:presentsimple.i]] + [presentsimple.lemma_] + [
                        x.text for x in doc[
                                        presentsimple.i + 1:end]]
                    print("Whom " + "do " + " ".join(converted) + '?')

                if len(presentsimplethird) > 0:
                    presentsimplethird = presentsimplethird[0]
                    end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                    converted = [x.text for x in doc[loc_relative_clause:presentsimplethird.i]] + [
                        presentsimplethird.lemma_] + [x.text for x in doc[
                                                                      presentsimplethird.i + 1:end]]
                    print("Whom " + "does " + " ".join(converted) + '?')

                    # Ram has eaten all the fruits that were left for Sita who is his sister
                    # Who is his sister?
                # Who has eaten?
                # print(wpword.text.capitalize() + " " + " ".join([x.text for x in doc[wpword.i + 1:]]) + "?")
                # print (wpword.text)
                # print("hello")
                # print(relclause)
                # Find Requirements
                pasttenseverb = self.filteratt({
                    'tag_': 'VBD',
                    'dep_': 'relcl'
                }, relclause)
                presentcontinuousverb = self.filteratt({
                    'tag_': 'VBG',
                    'dep_': 'relcl'
                }, relclause)
                pastparticiple = self.filteratt({
                    'tag_': 'VBN',
                    'dep_': 'relcl'
                }, relclause)
                presentsimple = self.filteratt({
                    'tag_': 'VBP',
                    'dep_': 'relcl'
                }, relclause)
                presentsimplethird = self.filteratt({
                    'tag_': 'VBZ',
                    'dep_': 'relcl'
                }, relclause)

                if wpword.dep_ == "nsubj" or wpword.dep_ == "nsubjpass":
                    print(wpword.text.capitalize() + " " + " ".join([x.text for x in doc[wpword.i + 1:]]) + "?")
                    loc_relative_clause = wpword.i
                    Head_Noun_Chunk = doc[wpword.i].head.head
                    

                else:
                    Head_Noun_Chunk = doc[wpword.i].head.head.head

                    #   # # Rules
                    if len(pasttenseverb) > 0:
                        # print ("here")
                        pasttenseverb = pasttenseverb[0]
                        # print(pasttenseverb)
                        # print ([x.text for x in doc[wpword.i + 1:pasttenseverb.i ]]+ [pasttenseverb.lemma_])
                        converted = [x.text for x in doc[wpword.i + 1:pasttenseverb.i]] + [pasttenseverb.lemma_] + [
                            x.text
                            for x in
                            doc[
                            pasttenseverb.i + 1:]]
                        print("Whom " + "did " + " ".join(converted) + '?')

                    if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0:
                        aux = self.filteratt({
                            'dep_': 'aux',
                        }, relclause)
                        aux += self.filteratt({
                            'dep_': 'auxpass',
                        }, relclause)
                        aux = aux[0]

                        # end = answer.head.i + 1 if answer.head.pos_ == "ADP" else answer.head.i
                        converted = [aux.text] + [x.text for x in doc[wpword.i + 1:aux.i]] + [x.text for x in
                                                                                              doc[aux.i + 1:]]
                        print("Whom %(kwarg)s?" % {'kwarg': " ".join(converted)})

                    if len(presentsimple) > 0:
                        presentsimple = presentsimple[0]
                        converted = [x.text for x in doc[wpword.i + 1:presentsimple.i]] + [presentsimple.lemma_] + [
                            x.text
                            for x in doc[
                                     presentsimple.i + 1:]]
                        print("Whom " + "do " + " ".join(converted) + '?')
                    if len(presentsimplethird) > 0:
                        presentsimplethird = presentsimplethird[0]
                        converted = [x.text for x in doc[wpword.i + 1:presentsimplethird.i]] + [
                            presentsimplethird.lemma_] + [x.text for x in doc[
                                                                          presentsimplethird.i + 1:]]
                        print("Whom " + "does " + " ".join(converted) + '?')


                Head_Noun_Chunk = doc[wpword.i].head
                while (Head_Noun_Chunk.pos_ not in ['NOUN','PROPN'] and (Head_Noun_Chunk.i != Head_Noun_Chunk.head.i)):
                    Head_Noun_Chunk = Head_Noun_Chunk.head


                print(Head_Noun_Chunk,[i for i in doc.noun_chunks])

                for noun in doc.noun_chunks:
                    if Head_Noun_Chunk.text in noun.text:
                        noun_chunk = noun.text
                # Requirements
                if 'noun_chunk' not in locals():
                    print("Subject modified by relative clause not found.")
                else:
                
                    if (Head_Noun_Chunk.tag_ == "NNS"):
                        if len(pasttenseverb) > 0:
                            print("Who were " + noun_chunk + "?")
                        else:
                            print("Who are " + noun_chunk + "?")
                    else:
                        if len(pasttenseverb) > 0:
                            print("Who was " + noun_chunk + "?")
                        else:
                            print("Who is " + noun_chunk + "?")
                
                loc_relative_clause = wpword.i
