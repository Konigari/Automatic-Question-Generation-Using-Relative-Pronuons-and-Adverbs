import copy
import inspect

from spacy import displacy


def filetotext():
    return open("temp.txt", "r").read()


class WHQuestionGenerator():
    last = False

    def __init__(self, nlp):
        self.nlp = nlp

    def lastdec(fun):
        def newfun(self, x):
            self.last = x
            return fun(self, x)

        return newfun

    @lastdec
    def show(self, u_line):
        doc = self.nlp(u_line)
        print("=========================Sentence -", u_line)
        print("=========================Text Lemma POS Tag Dep Shape Is_Alpha Is_Stop")
        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha,
                  token.is_stop)
        print("=========================NER  tags")
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
        print("=========================Noun Chunks tags")
        for c in doc.noun_chunks:
            print(c.text)
        print("=========================SENTENCE DONE")

    @lastdec
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

    def _filteratt(self, att, doc):
        att = self.expand(att)
        if len(att) == 1:
            att = att[0]
        if type(att) == list:
            return sum([self._filteratt(i, doc) for i in att], [])
        return list(filter(lambda tup: self.filt(att)(tup), doc))

    def filteratt(self, att, doc):
        return sorted(self._filteratt(att, doc), key=lambda x: x.i)

    def conjHandling(self, doc):
        if type(doc) == str:
            doc = self.nlp(doc)
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
            if len(noun_chunks) > 0:
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
            startind = start
            endind = end
            for ind, val in enumerate(doc):
                if val.i == start:
                    startind = ind
                if val.i == end:
                    endind = ind

            return [x.text for x in doc[:startind]] + [x.text for x in doc[endind + 1:]]

        def VerbChunk(root):
            aux_verb = self.filteratt({
                'dep_': ['aux', 'auxpass']
            }, list(root.children))
            if len(aux_verb) > 0:
                return aux_verb[0].i
            else:
                return root.i
                # if root.head == aux or root.head == auxpass :

                #   return root.head.i

        def NounCousin(root):
            Head_Noun_Chunk = root
            Root_children = self.filteratt({
                'pos_': ['NOUN', 'PROPN', 'PRON']
            }, list(root.children))
            for child in Root_children:
                if child.dep_ != 'nsubj':
                    Head_Noun_Chunk = child
            return Head_Noun_Chunk

        def NounParent(index):
            original = index
            Head_Noun_Chunk = index.head
            while (Head_Noun_Chunk.pos_ not in ['NOUN', 'PROPN']):

                if Head_Noun_Chunk.dep_ == "ROOT":
                    return NounCousin(Head_Noun_Chunk)
                elif Head_Noun_Chunk == Head_Noun_Chunk.head:
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
                return doc[noun.i:noun.i + 1]

        def PPChunker(doc, Head_Noun_Chunk):
            end = Head_Noun_Chunk
            while True:
                if Head_Noun_Chunk.dep_ == "ROOT":
                    break
                elif Head_Noun_Chunk.head.text == "of" and Head_Noun_Chunk.head.head.pos_ in ["NOUN"]:
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
        adjusted_answer = False

        for wpindex, wpword in enumerate(relativeclauseswh):
            adjusted_answer = False

            '''
            Rule 1: Using the matrix clause
            Rule 2: Using the embedded clause
            Rule 3: Relative clause modifying the NP Constituent
            '''

            def subs_answer():
                index = wpword.i
                while (doc[index - 1].pos_ not in ["NOUN", "DET", "PROPN", "PRP"]):
                    index = index - 1
                    if index <= 0:
                        return False
                # flag set if ccomp or advcl occurs
                answer = getNounChunk(doc[index - 1])
                return answer

            if wpword.head.dep_ in ['ccomp', 'advcl']:
                adjusted_answer = True
                answer = subs_answer()
            else:
                answer = PPChunker(doc, NounParent(wpword))

            matrix = doc[loc_relative_clause:wpword.i]
            relclause = doc[wpword.i:]

            hasanswer = {
                'who': True,
                'whom': True,
                'whose': True,
                'which': True,
                'that': True,
                'when': False,
                'how': False,
                'why': False,
                'whatsoever': False,
                'whomsoever': False
            }

            conversions = {
                'who': ['Who', 'Who', 'Who'],
                'whom': ['Whom', 'Whom', 'Who'],
                'whose': ['Who', 'Whose', 'Who'],
                'which': [False, 'What', 'What'],
                'what': ['What', 'What', False],

                'that': ['What', 'What', 'What'],
                'where': ['Where', 'Where', 'Where'],
                'when': [False, 'When', False],
                'how': ['What', 'How', False, ],
                'why': ['What', 'Why', False, ],
                'whatsoever': ['What', 'What', False],
                'whomsoever': ['Who', 'Who', False]
            }
            if wpword.text.lower() in conversions.keys():
                if answer:
                    end = answer.start
                else:
                    end = wpword.i

                questionwords = conversions[wpword.text.lower()]
                # Find Requirements - Special case where root comes after relative clause
                root = self.filteratt({
                    'dep_': ['ROOT'],
                }, doc[wpword.i:])

                # Rules
                # Rule 0
                if len(root) > 0:
                    if self.filteratt({'dep_': ['nsubj', 'nsubjpass']}, list(root[0].children))[0].text in answer.text:
                        yield (1, questionwords[0] + " " + doc[VerbChunk(root[0]):].text + "?")

                # Rule 1
                if questionwords[0]:

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
                    # print(matrix,"hie")

                    if len(pasttenseverb) > 0:

                        if (pasttenseverb[0].lemma_ == "be"):
                            noun = self.filteratt({
                                'dep_': 'nsubj'
                            }, pasttenseverb[0].children)[0]
                            yield (2, "%s %s %s?" % (questionwords[0], pasttenseverb[0].text, " ".join(
                                without(pasttenseverb[0].i, pasttenseverb[0].i, doc[loc_relative_clause:end]))))

                        else:
                            pasttenseverb = pasttenseverb[0]

                            converted = [x.text for x in doc[loc_relative_clause:pasttenseverb.i]] + [
                                pasttenseverb.lemma_] + [
                                            x.text for x in doc[
                                                            pasttenseverb.i + 1:end]]
                            yield (3, "%s did %s?" % (questionwords[0], " ".join(converted)))

                    if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0 or len(bareverb) > 0:
                        aux = self.filteratt({
                            'dep_': ['aux', 'auxpass']
                        }, matrix)[0]

                        converted = [aux.text] + without(aux.i, aux.i, doc[loc_relative_clause: end])
                        yield (4, "%s %s?" % (questionwords[0], " ".join(converted)))

                    if len(presentsimple) > 0:

                        if (presentsimple[0].lemma_ == "be"):
                            noun = self.filteratt({
                                'dep_': 'nsubj'
                            }, presentsimple[0].children)[0]
                            yield (5, "%s %s %s %s?" % (
                                questionwords[0], presentsimple[0].text, getNounChunk(noun).text,
                                doc[presentsimple[0].i + 1:end]))
                        else:
                            presentsimple = presentsimple[0]

                            converted = [x.text for x in doc[loc_relative_clause:presentsimple.i]] + [
                                presentsimple.lemma_] + [
                                            x.text for x in doc[
                                                            presentsimple.i + 1:end]]
                            yield (6, "%s do %s?" % (questionwords[0], " ".join(converted)))

                    if len(presentsimplethird) > 0:
                        if (presentsimplethird[0].lemma_ == "be"):
                            noun = self.filteratt({
                                'dep_': 'nsubj'
                            }, presentsimplethird[0].children)[0]
                            yield (
                                7,
                                "%s %s %s?" % (questionwords[0], presentsimplethird[0].text, getNounChunk(noun).text))
                        else:
                            presentsimplethird = presentsimplethird[0]

                            converted = [x.text for x in doc[loc_relative_clause:presentsimplethird.i]] + [
                                presentsimplethird.lemma_] + [x.text for x in doc[
                                                                              presentsimplethird.i + 1:end]]
                            yield (8, "%s does %s?" % (questionwords[0], " ".join(converted)))

                if questionwords[1]:
                    # Rule 2
                    # Find Requirements
                    pasttenseverb = self.filteratt({
                        'tag_': 'VBD',
                        'dep_': ['relcl', 'ccomp', 'advcl']
                    }, relclause)
                    presentcontinuousverb = self.filteratt({
                        'tag_': 'VBG',
                        'dep_': ['relcl', 'ccomp', 'advcl']
                    }, relclause)
                    pastparticiple = self.filteratt({
                        'tag_': 'VBN',
                        'dep_': ['relcl', 'ccomp', 'advcl']
                    }, relclause)
                    presentsimple = self.filteratt({
                        'tag_': 'VBP',
                        'dep_': ['relcl', 'ccomp', 'advcl']
                    }, relclause)
                    presentsimplethird = self.filteratt({
                        'tag_': 'VBZ',
                        'dep_': ['relcl', 'ccomp', 'advcl']
                    }, relclause)
                    ending = doc[wpword.i:]
                    punctCheck = self.filteratt({
                        'pos_': ['PUNCT']
                    }, ending)
                    if (len(punctCheck) > 0):
                        end = punctCheck[0].i
                    else:
                        if wpindex + 1 < len(relativeclauseswh):
                            end = relativeclauseswh[wpindex + 1].i
                        else:
                            end = None

                    if wpword.dep_ == "nsubj" or wpword.dep_ == "nsubjpass":
                        # TODO - Mukul says its Hack , Co-authors disagree , Module overlap
                        if len(root) > 0:
                            yield (9, "%s %s?" % (
                                questionwords[1], " ".join([x.text for x in doc[wpword.i + 1:VerbChunk(root[0])]])))
                        else:
                            yield (10, "%s %s?" % (questionwords[1], " ".join([x.text for x in doc[wpword.i + 1:end]])))

                    else:
                        #   # # Rules

                        if len(pasttenseverb) > 0:
                            pasttenseverb = pasttenseverb[0]
                            converted = [x.text for x in doc[wpword.i + 1:pasttenseverb.i]] + [pasttenseverb.lemma_] + [
                                x.text
                                for x in
                                doc[
                                pasttenseverb.i + 1:end]]
                            yield (11, "%s did %s?" % (questionwords[1], " ".join(converted)))

                        if len(presentcontinuousverb) > 0 or len(pastparticiple) > 0:
                            aux = self.filteratt({
                                'dep_': ['aux', 'auxpass']
                            }, relclause)[0]
                            converted = [aux.text] + without(aux.i, aux.i, doc[wpword.i + 1:end])
                            yield (12, "%s %s?" % (questionwords[1], " ".join(converted)))

                        if len(presentsimple) > 0:
                            presentsimple = presentsimple[0]
                            converted = [x.text for x in doc[wpword.i + 1:presentsimple.i]] + [presentsimple.lemma_] + [
                                x.text
                                for x in doc[
                                         presentsimple.i + 1:end]]
                            yield (13, "%s do %s?" % (questionwords[1], " ".join(converted)))
                        if len(presentsimplethird) > 0:
                            presentsimplethird = presentsimplethird[0]
                            converted = [x.text for x in doc[wpword.i + 1:presentsimplethird.i]] + [
                                presentsimplethird.lemma_] + [x.text for x in doc[
                                                                              presentsimplethird.i + 1:end]]
                            yield (14, "%s does %s?" % (questionwords[1], " ".join(converted)))

                if questionwords[2]:
                    # Rule 3

                    temp_head = answer
                    checker = self.filteratt({
                        'dep_': ['nsubj', 'relcl']
                    }, sum([list(x.children) for x in answer], []))

                    if (len(checker) == 0 or adjusted_answer):
                        head = doc[answer.end - 1]
                    elif (len(checker[0].head)):
                        head = checker[0].head

                    if not head:
                        print("Subject modified by relative clause not found.")
                    elif (head.pos_ == "PROPN"):
                        # stop rule 3 questions at the noun_chunk only
                        if (head.tag_ == "NNS"):
                            if len(pasttenseverb) > 0:
                                yield (15, "%s were %s?" % (questionwords[2], answer))
                            else:
                                yield (16, "%s are %s?" % (questionwords[2], answer))
                        elif (not head.tag_ == "NNS"):
                            if len(pasttenseverb) > 0:
                                yield (17, "%s was %s?" % (questionwords[2], answer))
                            else:
                                yield (18, "%s is %s?" % (questionwords[2], answer))
                    else:
                        ending = doc[wpword.i:]
                        punctCheck = self.filteratt({
                            'pos_': ['PUNCT']
                        }, ending)

                        if (len(punctCheck) > 0):
                            end = punctCheck[0].i
                        else:
                            if wpindex + 1 < len(relativeclauseswh):
                                end = relativeclauseswh[wpindex + 1].i
                            elif wpindex + 1 == len(relativeclauseswh):
                                end = wpword.i
                            else:
                                end = None

                        if (head.tag_ == "NNS"):
                            if len(pasttenseverb) > 0:
                                yield (19, "%s were %s %s?" % (questionwords[2], answer, doc[head.i + 1:end]))
                            else:
                                yield (20, "%s are %s %s?" % (questionwords[2], answer, doc[head.i + 1:end]))
                        else:
                            if len(pasttenseverb) > 0:
                                yield (21, "%s was %s %s?" % (questionwords[2], answer, doc[head.i + 1:end]))
                            else:
                                yield (22, "%s is %s %s?" % (questionwords[2], answer, doc[head.i + 1:end]))

            # When matrix sentence is immediately complete, waiting for a verb , it's called appositoin- in this case,

            loc_relative_clause = wpword.i

    def preprocessing(self, sentence):
        sentence = sentence.strip('.')
        return sentence

    @lastdec
    def genqlistdev(self, sentence):
        sentence = self.preprocessing(sentence)
        doc = self.nlp(sentence)
        sentences = self.conjHandling(doc)
        return sum([list(self.genq(x.text)) for x in sentences], [])

    @lastdec
    def genqlist(self, sentence):
        sentence = self.preprocessing(sentence)
        doc = self.nlp(sentence)
        sentences = self.conjHandling(doc)
        return sum([[x[1] for x in self.genq(x.text)] for x in sentences], [])

    def genqlistlast(self):
        if self.last:
            return self.genqlist(self.last)

    def showlast(self):
        if self.last:
            return self.show(self.last)

    def displaylast(self):
        if self.last:
            return self.display(self.last)
