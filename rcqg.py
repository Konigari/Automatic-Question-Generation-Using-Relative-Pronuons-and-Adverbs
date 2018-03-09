import inspect
import copy
from spacy import displacy


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

    def conjHandling(self, doc):
        sentential_conjunctions = []
        conjunctions = self.filteratt({
            'pos_': ["CCONJ", "PUNCT"],
        }, doc) + self.filteratt({
            'pos_': "ADP",
            'dep_': "mark"
        }, doc)
        sorted_conjunctions = sorted(conjunctions, key=lambda x: x.i)
        end = len(doc)
        for conjunction in reversed(sorted_conjunctions):
            # temp_doc = doc[conjunction.i:]
            noun_chunks = [c for c in doc[conjunction.i:].noun_chunks]
            if noun_chunks[0].root.dep_ == "nsubj":
                sentential_conjunctions.append(conjunction)
            end = conjunction.i
        sentential_conjunctions = reversed(sentential_conjunctions)
        indices = [x.i for x in sentential_conjunctions]

        def splitsentence(sentence):
            start = sentence[0].i
            end = sentence[-1].i
            for i in sentence:
                if i.i in indices:
                    return [doc[start:i.i]] + splitsentence(doc[i.i + 1:end + 1])
            return [sentence]
        return splitsentence(doc)

    def genq(self, sentence):
        def without(start, end, doc):
            return [x.text for x in doc[:start]] + [x.text for x in doc[end + 1:]]

        def VerbChunk(root):
            print(root.text)
            aux_verb = self.filteratt({
                'dep_': ['aux', 'auxpass']
            }, list(root.children))
            print(aux_verb)
            if len(aux_verb) > 0:
                print(aux_verb[0].i)
                return aux_verb[0].i
            else:
                return root.i
            # if root.head == aux or root.head == auxpass :
            # 	return root.head.i

        def NounParent(index):
            original = index
            Head_Noun_Chunk = index.head
            while (Head_Noun_Chunk.pos_ not in ['NOUN']):
                if Head_Noun_Chunk == Head_Noun_Chunk.head:
                    return original
                Head_Noun_Chunk = Head_Noun_Chunk.head
            return Head_Noun_Chunk

        def getNounChunk(noun):
            found = False
            for noun_chunk in doc.noun_chunks:
                if noun_chunk.start <= noun.i and noun_chunk.end >= noun.i:
                    found = True
                    result = noun_chunk
            if found:
                return result
            else:
                return False

        def PPChunker(doc, Head_Noun_Chunk):
            end = Head_Noun_Chunk

            while True:
                if Head_Noun_Chunk.head.text == "of" and Head_Noun_Chunk.head.head.pos_ in ["NOUN"]:
                    Head_Noun_Chunk = Head_Noun_Chunk.head.head
                else:
                    break
            ## TODO - Forward PP chunking( I have met the mother of my son who is)
            return doc[getNounChunk(Head_Noun_Chunk).start:getNounChunk(end).end]

        doc = self.nlp(sentence)

        relativeclauseswh = self.filteratt({
            'tag_': ['WDT', 'WP$', 'WPO', 'WPS', 'WQL', 'WRB', 'WP'],
        }, doc)
        loc_relative_clause = 0

        for wpword in relativeclauseswh:
            '''
            Rule 1: Using the matrix clause
            Rule 2: Using the embedded clause
            Rule 3: Relative clause modifying the NP Constituent
            '''
            answer = PPChunker(doc, NounParent(wpword))
            matrix = doc[loc_relative_clause:answer.start]
            relclause = doc[wpword.i:]
            conversions = {
                'who': ['Who', 'Who', 'Who'],
                'whom': ['Whom', 'Whom', 'Who'],
                'whose': ['Who', 'Whose', 'Who'],
                'which': ['What', 'What', 'What'],
                'that': ['What', 'What', 'What'],
                'when': ['When', 'When', 'When'],
                'how': ['What', 'How', ],
                'why': ['What', 'Why', ],
                'whatsoever': ['What', 'What'],
                'whomsoever': ['Who', 'Who']
            }
            if wpword.text.lower() in conversions.keys():
                questionwords = conversions[wpword.text.lower()]
                # Find Requirements
                root = self.filteratt({
                    'dep_': ['ROOT'],
                }, doc[wpword.i:])

                # Rules
                # Rule 0
                if len(root) > 0:
                    if self.filteratt({'dep_': ['nsubj', 'nsubjpass']}, list(root[0].children))[0].text in answer.text:
                        yield (questionwords[0] + " " + doc[VerbChunk(root[0]):].text + "?")

                # Rule 1
                pasttenseverb = self.filteratt({
                    'tag_': 'VBD',
                    'dep_': 'ROOT'
                }, matrix)
                bareverb = self.filteratt({
                    'tag_': 'VB',
                    'dep_': 'ROOT'
                }, matrix)
                presentcontinuousverb = self.filteratt({
                    'tag_': 'VBG',
                    'dep_': 'ROOT'
                }, matrix)
                pastparticiple = self.filteratt({
                    'tag_': 'VBN',
                    'dep_': 'ROOT'
                }, matrix)
                presentsimple = self.filteratt({
                    'tag_': 'VBP',
                    'dep_': 'ROOT'
                }, matrix)
                presentsimplethird = self.filteratt({
                    'tag_': 'VBZ',
                    'dep_': 'ROOT'
                }, matrix)
                if len(pasttenseverb) > 0:

                    if (pasttenseverb[0].lemma_ == "be"):
                        noun = self.filteratt({
                            'dep_': 'nsubj'
                        }, pasttenseverb[0].children)[0]
                        yield ("%s %s %s?" % (questionwords[0], pasttenseverb[0].text, getNounChunk(noun).text))
                    else:
                        pasttenseverb = pasttenseverb[0]
                        end = (answer.start) if doc[answer.start].pos_ == "ADP" else answer.start
                        converted = [x.text for x in doc[loc_relative_clause:pasttenseverb.i]] + [
                            pasttenseverb.lemma_] + [
                                        x.text for x in doc[
                                                        pasttenseverb.i + 1:end]]
                        yield ("%s did %s?" % (questionwords[0], " ".join(converted)))

                if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0 or len(bareverb) > 0:
                    aux = self.filteratt({
                        'dep_': ['aux', 'auxpass']
                    }, matrix)[0]
                    print("why the fuck you no come here?")
                    end = (answer.start)
                    converted = [aux.text] + without(aux.i, aux.i, doc[loc_relative_clause: end])
                    yield ("%s %s?" % (questionwords[0], " ".join(converted)))

                if len(presentsimple) > 0:
                    presentsimple = presentsimple[0]
                    end = (answer.start) if doc[answer.start].pos_ == "ADP" else answer.start - 1
                    converted = [x.text for x in doc[loc_relative_clause:presentsimple.i]] + [presentsimple.lemma_] + [
                        x.text for x in doc[
                                        presentsimple.i + 1:end]]
                    yield ("%s do %s?" % (questionwords[0], " ".join(converted)))

                if len(presentsimplethird) > 0:
                    if (presentsimplethird[0].lemma_ == "be"):
                        noun = self.filteratt({
                            'dep_': 'nsubj'
                        }, presentsimplethird[0].children)[0]
                        yield ("%s %s %s?" % (questionwords[0], presentsimplethird[0].text, getNounChunk(noun).text))
                    else:
                        presentsimplethird = presentsimplethird[0]
                        end = (answer.start) if doc[answer.start].pos_ == "ADP" else answer.start - 1
                        converted = [x.text for x in doc[loc_relative_clause:presentsimplethird.i]] + [
                            presentsimplethird.lemma_] + [x.text for x in doc[
                                                                          presentsimplethird.i + 1:end]]
                        yield ("%s does %s?" % (questionwords[0], " ".join(converted)))

                # Rule 2
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
                    # TODO - Mukul says its Hack , Co-authors disagree , Module overlap

                    if len(root) > 0:
                        print("fucker")
                        yield (
                        "%s %s?" % (questionwords[1], " ".join([x.text for x in doc[wpword.i + 1:VerbChunk(root[0])]])))
                    else:
                        yield ("%s %s?" % (questionwords[1], " ".join([x.text for x in doc[wpword.i + 1:]])))

                else:
                    #   # # Rules
                    if len(pasttenseverb) > 0:
                        pasttenseverb = pasttenseverb[0]
                        converted = [x.text for x in doc[wpword.i + 1:pasttenseverb.i]] + [pasttenseverb.lemma_] + [
                            x.text
                            for x in
                            doc[
                            pasttenseverb.i + 1:]]
                        yield ("%s did %s?" % (questionwords[1], " ".join(converted)))

                    if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0:
                        aux = self.filteratt({
                            'dep_': ['aux', 'auxpass']
                        }, relclause)[0]
                        converted = [aux.text] + without(aux.i, aux.i, doc[wpword.i:])
                        yield ("%s %s?" % (questionwords[1], " ".join(converted)))

                    if len(presentsimple) > 0:
                        presentsimple = presentsimple[0]
                        converted = [x.text for x in doc[wpword.i + 1:presentsimple.i]] + [presentsimple.lemma_] + [
                            x.text
                            for x in doc[
                                     presentsimple.i + 1:]]
                        yield ("%s do %s?" % (questionwords[1], " ".join(converted)))
                    if len(presentsimplethird) > 0:
                        presentsimplethird = presentsimplethird[0]
                        converted = [x.text for x in doc[wpword.i + 1:presentsimplethird.i]] + [
                            presentsimplethird.lemma_] + [x.text for x in doc[
                                                                          presentsimplethird.i + 1:]]
                        yield ("%s does %s?" % (questionwords[1], " ".join(converted)))

                # Rule 3
                Head_Noun_Chunk = NounParent(wpword)

                noun_chunk = PPChunker(doc, Head_Noun_Chunk).text
                # Requirements
                if not noun_chunk:
                    print("Subject modified by relative clause not found.")
                else:

                    if (Head_Noun_Chunk.tag_ == "NNS"):
                        if len(pasttenseverb) > 0:
                            yield ("%s were %s?" % (questionwords[2], noun_chunk))
                        else:
                            yield ("%s are %s?" % (questionwords[2], noun_chunk))
                    elif(not Head_Noun_Chunk.tag_== "NNS"):
                        if len(pasttenseverb) > 0:
                            yield ("%s was %s?" % (questionwords[2], noun_chunk))
                        else:
                            yield ("%s is %s?" % (questionwords[2], noun_chunk))

                # Rule 4
                if not noun_chunk:
                    print("Subject modified by relative clause not found.")
                else:

                    if (Head_Noun_Chunk.tag_ == "NNS"):
                        if len(pasttenseverb) > 0:
                            yield ("%s were %s %s?" % (questionwords[2], noun_chunk, doc[Head_Noun_Chunk.i + 1:]))
                        else:
                            yield ("%s are %s %s?" % (questionwords[2], noun_chunk, doc[Head_Noun_Chunk.i + 1:]))
                    else:
                        if len(pasttenseverb) > 0:
                            yield ("%s was %s %s?" % (questionwords[2], noun_chunk, doc[Head_Noun_Chunk.i + 1:]))
                        else:
                            yield ("%s is %s %s?" % (questionwords[2], noun_chunk, doc[Head_Noun_Chunk.i + 1:]))
                


            loc_relative_clause = wpword.i

    def genqlist(self, sentence):
        sentence = sentence.strip('. ')
        doc = self.nlp(sentence)
        sentences = self.conjHandling(doc)
        return sum([list(self.genq(x.text)) for x in sentences], [])
