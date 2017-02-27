import numpy as np
import pandas as pd
import csv
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.feature_extraction.text import CountVectorizer
import os

import warnings
warnings.filterwarnings("ignore")

fposlex = open('resources\PosLex.csv', 'rt', encoding="utf8")
fneglex = open('resources\\NegLex.csv', 'rt', encoding="utf8")


def populate_lex(file):
    lex = []
    reader = csv.reader(file)
    next(reader, None)  # skip first line
    for row in reader:
        if row[2] not in lex:  # using a set would be a solution, but it requires conversion to list
            lex.append(row[2])
    return lex


poslex = populate_lex(fposlex)
neglex = populate_lex(fneglex)
fposlex.close()
fneglex.close()


def classify(tweets, categories):
    tdf = pd.DataFrame(tweets)
    texts = tdf['clean_text']
    cv_pos = CountVectorizer(input='content', vocabulary=poslex, decode_error='ignore', lowercase=False)
    X_pos = cv_pos.fit_transform(texts).toarray()
    cv_neg = CountVectorizer(input='content', vocabulary=neglex, decode_error='ignore', lowercase=False)
    X_neg = cv_neg.fit_transform(texts).toarray()
    sentiment = []
    for irow in range(X_pos.shape[0]):
        prow = X_pos[irow, :]
        nrow = X_neg[irow, :]
        tsentiment = np.sum(prow) - np.sum(nrow)
        if tsentiment > 0:
            sentiment.append("Positive")
        elif tsentiment < 0:
            sentiment.append("Negative")
        else:
            sentiment.append(random.choice(['Positive', 'Negative']))
    tweets['class'] = sentiment
    return tweets


class TermClassifier:

    def __init__(self, X, rank):
        self.cv = CountVectorizer(input='content', decode_error='ignore', lowercase=False, min_df=2)
        self.U_terms = self.get_terms_svd(self.cv.fit_transform(X).toarray().T, rank)

    def normalize_terms(self, U):
        normalized = []
        for row in U:
            norm = np.linalg.norm(row)
            if norm == 0:
                normalized.append([0 for _ in row])
            else:
                normalized.append([cell/norm for cell in row])
        return normalized

    def distance(self, a, b):
        return cosine_similarity(a, b)

    def get_terms_svd(self, X, rank=300):
        U, S, V = np.linalg.svd(np.array(X), full_matrices=False)
        return self.normalize_terms(U[:, :rank])

    def get_closest_neighbors(self, term, index, n_neighbors):
        distances = []
        for i in range(len(self.U_terms)):
            x = self.U_terms[i]
            if index == i:
                distances.append(-99999)
                continue  # it's it self
            distances.append(cosine_similarity(x, term))
        return np.argpartition(distances, -n_neighbors)[-n_neighbors:]

    def classify_terms(self, n_neighbors):
        dir = str(n_neighbors) + '_neighbors\\'
        ext_pos = {}
        ext_neg = {}
        pos_sum = 0
        neg_sum = 0
        new_pos = set()
        new_neg = set()

        terms = self.cv.get_feature_names()
        t = 0
        for u_term in self.U_terms:
            term = terms[t]
            sentiment = 0
            if term in poslex:
                sentiment = 1
            elif term in neglex:
                sentiment = -1
            else:
                t += 1
                continue

            idx = self.get_closest_neighbors(u_term, t, n_neighbors)
            neighs = [terms[i] for i in idx]

            if sentiment == 1:
                ext_pos[term] = neighs
                filename = dir + 'ExtPos(' + term + ').txt'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w", encoding='utf-8') as f:
                    for tn in neighs:
                        f.write(tn+"\n")
            else:
                ext_neg[term] = neighs
                filename = dir + 'ExtNeg(' + term + ').txt'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w", encoding='utf-8') as f:
                    for tn in neighs:
                        f.write(tn+"\n")
            t += 1
        # end for loop
        for term, neighbors in ext_pos.items():
            for n in neighbors:
                if n in poslex:
                    pos_sum += 1
                else:
                    new_pos.add(n)
        for term, neighbors in ext_neg.items():
            for n in neighbors:
                if n in neglex:
                    neg_sum += 1
                else:
                    new_neg.add(n)
        pos_all = len(ext_pos)
        neg_all = len(ext_neg)
        pos_mean = pos_sum / pos_all
        neg_mean = neg_sum / neg_all
        print("\n\n--- Based on nearest %d neighbors classification ---" % n_neighbors)
        print("Mean value of already known positive terms: ", pos_mean)
        print("Mean value of already known negative terms: ", neg_mean)
        print("\n~~~~~Newly found positive terms:")
        for pterm in new_pos:
            print(pterm, end=",  ")
        print("\n\n~~~~~Newly found negative terms:")
        for nterm in new_neg:
            print(nterm, end=",  ")

