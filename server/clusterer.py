from models import User, Document
from utils import (
    synonyms, process_text,
    l2_norm, encode_documents)
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
import os
import numpy as np

# https://medialab.github.io/iwanthue/
# Default pre-set
# 20 colors 
# soft (k-means)
# color blind setting
color_palette = [
    "#885fd8", "#5fb440", "#c657be", "#b6b630", "#5a78d8",
    "#df8e28", "#8974be", "#669c4f", "#d7418f", "#4aaa86",
    "#d54156", "#5a9fd0", "#cd542c", "#b86daf", "#ac9135",
    "#c575a0", "#9c874a", "#b6557a", "#c2744e", "#c3666b"]

class Clusterer:
    clusterer_path = "./users/{}/doc_clusterer.bin"
    def __init__(self,
                user:User,
                index:list,
                k:int,
                seed:dict=None):
        
        self.userId = user.userId

        # SETTINGS
        self.doc_model = user.doc_model
        self.word_model = user.word_model
        
        # EMBEDDINGS
        self.word_vectors = user.fast_text if self.word_model == "FastText" else user.word2vec
        self.doc2vec = user.doc2vec
        
        self.index = index
        corpus = []
        self.embeddings = []
        
        for doc in user.corpus:
            if doc.id in self.index:
                corpus.append(doc)
                self.embeddings.append(doc.embedding)

        self.__path = Clusterer.clusterer_path.format(self.userId)
        
        self.k = k
        
        self.seed = seed
        
        self.seed_paragraphs = []
        self.word_labels = None
        word_clusterer = self.cluster_words()

        # Builds seed paragraphs to cluster documents
        for index, centroid in enumerate(word_clusterer.cluster_centers_):
            self.seed_paragraphs.append([
                term[0]
                for term in self.word_vectors.wv.similar_by_vector(centroid, topn=50)])

        self.doc_labels = None
        doc_clusterer = self.cluster_documents()

        self.cluster_names = []
        self.colors = []
        if self.seed:
            for index in range(self.k):
                self.cluster_names.append(seed["cluster_names"][index])
                self.colors.append(seed["colors"][index])
        else:
            for i in range(self.k):
                self.cluster_names.append(f"cluster_{i}")
                self.colors.append(color_palette[i])

        self.doc_clusters = dict()
        for cluster_name in self.cluster_names:
            self.doc_clusters[f"{cluster_name}"] = list()

        for index, label in enumerate(self.doc_labels):
            self.doc_clusters[f"{self.cluster_names[label]}"].append(
                corpus[index].id)

    def handle_unseen_words(self, words:list) -> list:
        words_filtered = [*filter(lambda word: word in self.word_vectors.wv, words)]
        if len(words) != 0 and len(words_filtered) == 0:
            synonyms = []
            for word in words:
                synonyms += [process_text(syn) for syn in synonyms(word)]
            synonyms = [*filter(lambda word: word in self.word_vectors.wv, synonyms)]
            if len(synonyms) == 0:
                raise Exception("Neither the words nor its synonyms in the vocabulary")
            else:
                words_filtered = [*synonyms]

        return words_filtered

    def cluster_words(self) -> KMeans:
        self.word_vectors.wv.init_sims()

        if self.seed: # UPDATE CLUSTERS GIVEN USER SEEDS
            init_mode = np.zeros((int(self.k), self.word_vectors.vector_size))
            for i in range(self.k):
                positive = []
                negative = []
                for word in self.seed["cluster_words"][i]:
                    if word["weight"] > 0:
                        positive.append(word["word"])
                    else:
                        negative.append(word["word"])
                if self.word_model == "Word2Vec":
                # Handling unseen words for Word2Vec
                # FastText can handle unseen words
                    positive = self.handle_unseen_words(positive)
                    negative = self.handle_unseen_words(negative)

                seed_terms = positive + [
                    term[0]
                    for term in self.word_vectors.wv.most_similar(
                        positive=(positive if positive else None),
                        negative=(negative if negative else None),
                        topn=(50 - len(positive)))
                ]
                
                init_mode[i] = np.mean([
                    self.word_vectors.wv.word_vec(term)
                    for term in seed_terms
                ], axis=0)
        else: # NEW RANDOM CLUSTERS
            init_mode = "k-means++"

        # Clustering word vectors
        k_means = KMeans(
            n_clusters=self.k,
            init=init_mode,
            n_init=10,
            tol=1e-5
        ).fit(self.word_vectors.wv.vectors_norm)
        self.word_clusters = k_means.labels_

        return k_means

    def cluster_documents(self) -> KMeans:
        if self.doc_model == "Doc2Vec":
            doc_seeds = np.array([
                self.doc2vec.infer_vector(shuffle(paragraph), steps=35)
                for paragraph in self.seed_paragraphs
            ], dtype=float)
            doc_seeds = l2_norm(doc_seeds)
        else:
            doc_seeds = np.array(encode_documents([
                " ".join(paragraph)
                for paragraph in self.seed_paragraphs
            ]), dtype=float)

        k_means = KMeans(
            n_clusters=self.k,
            init=doc_seeds,
            n_init=10,
            tol=1e-5
        ).fit(self.embeddings)
        self.doc_labels = k_means.labels_

        return k_means

    @classmethod
    def predict(cls, userId:str, docs:list) -> list:
        model_path = Clusterer.model_path.format(userId)
        
        if os.path.isfile(model_path):
            kmeans = pickle.load(open(model_path, "rb"))
            return kmeans.predict([
                doc.embedding
                for doc in docs
            ])
        return None