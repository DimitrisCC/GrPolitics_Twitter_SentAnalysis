# coding: utf-8

# # <center> Συστήματα Ανάκτησης Πληροφοριών</center>
# ## <center> Προγραμματιστική Εργασία - Φάση 2</center> 
# ### <center> Δημήτρης Παπαθεοδώρου 3130162 </center> 

# #### Imports

import re
import unicodedata


# #### Stemmer
class GreekAnalyzer:
    one_suff = ('Α', 'Ο', 'Ε', 'Η', 'Ω', 'Υ', 'Ι')
    three_suff = ('ΟΥΣ', 'ΕΙΣ', 'ΕΩΝ', 'ΟΥΝ')
    two_suff = ('ΟΣ', 'ΗΣ', 'ΕΣ', 'ΩΝ', 'ΟΥ', 'ΟΙ', 'ΑΣ', 'ΩΣ', 'ΑΙ', 'ΥΣ', 'ΟΝ', 'ΑΝ', 'ΕΙ')

    class Sentence:
        # This class represents a string which will be cleaned as part of a pre-processing procedure
        def __init__(self, sentence):
            self.sentence = str(sentence).upper()

        def __repr__(self):
            return str(self.sentence)

        # Default argument values are evaluated at function define-time,
        # but self is an argument only available at function call time.
        # Thus arguments in the argument list cannot refer each other.

        def strip_accents(self, sentence=None):
            if sentence is None:
                sentence = self.sentence
            return GreekAnalyzer.Sentence(''.join(c for c in unicodedata.normalize('NFD', sentence)
                                                  if unicodedata.category(c) != 'Mn'))

        def strip_specialcharacters_numbers(self, sentence=None):
            if sentence is None:
                sentence = self.sentence
            return GreekAnalyzer.Sentence(re.sub(r'[^Α-Ωα-ω ]', '', sentence, flags=re.MULTILINE))

        def strip_links(self, sentence=None):
            if sentence is None:
                sentence = self.sentence
            return GreekAnalyzer.Sentence(re.sub(r'^https?:\/\/.*[\r\n]*', '', sentence, flags=re.MULTILINE))

        def strip_tags(self, sentence=None):
            if sentence is None:
                sentence = self.sentence
            return GreekAnalyzer.Sentence(re.sub(r'#\w*|@\w*', '', sentence, flags=re.MULTILINE))

        def stem(self, sentence=None):
            if sentence is None:
                sentence = self.sentence
            stemmed = ""
            for term in sentence.split():
                # Check if term is numeric
                pattern = re.compile("^[+-]?(\\d+(\\.\\d*)?|\\.\\d+)([eE][+-]?\\d+)?$")
                if pattern.match(term):
                    return ''
                # Remove first level suffixes only if the term is 4 letters or more
                if len(term) >= 4:
                    # Remove the 3 letter suffixes
                    if term.endswith(GreekAnalyzer.three_suff):
                        term = term[:-3]
                        # Remove the 2 letter suffixes
                    elif term.endswith(GreekAnalyzer.two_suff):
                        term = term[:-2]
                    # Remove the 1 letter suffixes
                    elif term.endswith(GreekAnalyzer.one_suff):
                        term = term[:-1]
                stemmed += term + ' '
            # return GreekAnalyzer.Sentence(stemmed[:-1])
            return GreekAnalyzer.Sentence(stemmed[:-1])

        def strip_stopwords(self, sentence=None, stop_words=None):
            if sentence is None:
                sentence = self.sentence
            if stop_words is None:
                return GreekAnalyzer.Sentence(sentence)
            for w in stop_words:
                sentence = re.sub(r'\b'+w+r'\b', '', sentence)
            return GreekAnalyzer.Sentence(sentence)

    def __init__(self, sentence):
        if isinstance(sentence, GreekAnalyzer.Sentence):
            self.sentence = sentence
        else:
            self.sentence = GreekAnalyzer.Sentence(sentence)

    def clean(self, sentence=None, stop_words=None):
        if sentence is None:
            sentence = self.sentence
        if isinstance(sentence, GreekAnalyzer.Sentence):
            return str(sentence
                       .strip_accents()
                       .strip_links()
                       .strip_tags()
                       .strip_specialcharacters_numbers()
                       .strip_stopwords(stop_words=stop_words).stem()
                       )
        else:
            return GreekAnalyzer(GreekAnalyzer.Sentence(sentence)).clean(stop_words)


# ### Loading stopwords
fstopwords = open('resources\greekstopwords.txt', 'rt', encoding="utf8")

stopwords = [w.strip() for w in fstopwords.readlines() if w.strip() != '']
del (stopwords[0])  # for some reason it's a garbage word

fstopwords.close()


def clean_tweets(tweets: dict):
    proc = []
    for text in tweets['text']:
        analyzer = GreekAnalyzer(text)
        proc.append(analyzer.clean(stop_words=stopwords))
    tweets['clean_text'] = proc
    return tweets


def format_time(time):
    strtime = str(time)
    digits = len(strtime)
    if digits == 1:
        return "0"+strtime
    else:
        return strtime
