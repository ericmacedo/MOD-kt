import os
import pickle
import numpy as np
from sklearn.utils import shuffle
from sklearn.cluster import KMeans
from models.user import User
from models.document import Document
from utils import l2_norm

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
                 user: User,
                 index: list,
                 k: int,
                 seed: dict = None):

        self.userId = user.userId

        # SETTINGS
        self.doc_model = user.doc_model
        self.word_model = user.word_model

        # EMBEDDINGS
        self.word_vectors = user.word_vectors
        self.doc_vectors = user.doc_vectors

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
        word_clusterer = self.word_vectors.cluster_words(
            userId=user.userId,
            k=self.k,
            seed=self.seed)
        self.word_clusters = word_clusterer.labels_

        # Builds seed paragraphs to cluster documents
        for index, centroid in enumerate(word_clusterer.cluster_centers_):
            self.seed_paragraphs.append(
                self.word_vectors.seed_paragraph(
                    userId=user.userId,
                    vector=centroid))

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

    def cluster_documents(self) -> KMeans:
        doc_seeds = self.doc_vectors.get_vectors(
            userId=self.userId,
            corpus=self.seed_paragraphs)

        k_means = KMeans(
            n_clusters=self.k,
            init=doc_seeds,
            n_init=10,
            tol=1e-5
        ).fit(self.embeddings)
        self.doc_labels = k_means.labels_

        return k_means

    @classmethod
    def predict(cls, userId: str, docs: list) -> list:
        model_path = Clusterer.model_path.format(userId)

        if os.path.isfile(model_path):
            kmeans = pickle.load(open(model_path, "rb"))
            return kmeans.predict([
                doc.embedding
                for doc in docs
            ])
        return None
