from sklearn.feature_extraction.text import TfidfVectorizer
from collections import OrderedDict
from typing import List, Iterable
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pickle


class ModelType(Enum):
    DOCUMENT = "document"
    WORD = "word"


@dataclass
class BagOfWords:
    n: int
    m: int

    index: List[str]
    matrix: Iterable[List]
    vocabulary: OrderedDict

    def train(self, corpus: List[str], index: List[str] = None) -> np.array:
        allWords = dict()
        vectorizer = TfidfVectorizer(min_df=2)

        tfidf_matrix = vectorizer.fit_transform(corpus)
        tfidf_feature_names = vectorizer.get_feature_names()
        tfidf_feature_names_hashmap = {}

        self.n, self.m = tfidf_matrix.shape  # (N documents, M features)
        self.index = index if index else [f"doc_{i}" for i in range(self.n)]

        # tfidf feature names hashmap
        for j in range(0, self.m):
            tfidf_feature_names_hashmap[tfidf_feature_names[j]] = j

        # filter based on the mean tf/idf
        tfidf_mean = tfidf_matrix.mean(0).mean()
        words_tfidf = tfidf_matrix.mean(0)
        for index, item in enumerate(np.nditer(words_tfidf)):
            if item > tfidf_mean:
                allWords[tfidf_feature_names[index]] = 0

        self.vocabulary = OrderedDict(sorted(allWords.items()))

        # create document term matrix (out)
        self.matrix = list()
        for j in range(self.n):
            self.matrix.append(list())
            tfidf_hashmap = {}
            for col in tfidf_matrix.getrow(j).nonzero()[1]:
                if tfidf_feature_names[col] in self.vocabulary:
                    tfidf_hashmap[col] = tfidf_matrix[j, col]

            for word, score in self.vocabulary.items():
                word_index = tfidf_feature_names_hashmap.get(word)
                if tfidf_feature_names_hashmap.get(word) in tfidf_hashmap:
                    self.matrix[j].append(
                        tfidf_hashmap.get(word_index))
                else:
                    self.matrix[j].append(0.0)

        self.matrix = np.array(self.matrix, dtype=np.float32)
        return self.matrix

    @classmethod
    def load(cls, path: str):
        return pickle.load(open(path, "rb"))

    def save(self, path: str):
        with open(path, "wb") as pkl_file:
            pickle.dump(
                obj=self,
                file=pkl_file,
                protocol=pickle.DEFAULT_PROTOCOL,
                fix_imports=True)
