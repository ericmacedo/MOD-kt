from models import User, Document
from sklearn.cluster import KMeans
import seaborn as sns
import os, pickle
import numpy as np

class Clusterer:
    clusterer_path = "./users/{}/doc_clusterer.bin"
    def __init__(self,
                user:User,
                k:int,
                seed:dict=None):
        
        self.userId = user.userId
        self.doc_model = user.doc_model
        self.word2vec = user.word2vec
        self.doc2vec = user.doc2vec
        self.index = user.index
        corpus = user.corpus
        self.embeddings = [doc.embedding for doc in corpus]
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
                for term in self.word2vec.wv.similar_by_vector(centroid, topn=50)])

        self.doc_labels = None
        doc_clusterer = self.cluster_documents()

        self.cluster_names = []
        self.colors = []
        if self.seed:
            for index in range(self.k):
                self.cluster_names.append(seed["cluster_names"][index])
                self.colors.append(seed["colors"][index])
        else:
            palette = sns.color_palette("tab20").as_hex()
            for i in range(self.k):
                self.cluster_names.append(f"cluster_{i}")
                self.colors.append(palette[i])

        self.doc_clusters = dict()
        for cluster_name in self.cluster_names:
            self.doc_clusters[f"{cluster_name}"] = list()

        for index, label in enumerate(self.doc_labels):
            self.doc_clusters[f"{self.cluster_names[label]}"].append(
                corpus[index].id)

        pickle.dump(doc_clusterer, open(self.__path, "wb"))


    def cluster_words(self) -> KMeans:
        self.word2vec.wv.init_sims()

        if self.seed: # UPDATE CLUSTERS GIVEN USER SEEDS
            init_mode = np.zeros((int(self.k), self.word2vec.vector_size))
            for i in range(self.k):
                positive = []
                negative = []
                for word in self.seed["cluster_words"]:
                    if word["weight"] > 0:
                        positive.append(word["word"])
                    else:
                        negative.append(word["word"])

                seed_terms = positive + [
                    term[0]
                    for term in self.word2vec.wv.most_similar(
                        positive=(positive if positive else None),
                        negative=(negative if negative else None),
                        topn=(50 - len(positive)))
                ]

                init_mode[i] = np.mean([
                    self.word2vec.wv.word_vec(term)
                    for term in seed_terms
                ], axis=0)

        else: # NEW RANDOM CLUSTERS
            init_mode = "k-means++"

        # Clustering word vectors
        k_means = KMeans(
            n_clusters=self.k,
            init=init_mode,
            n_init=1,
            tol=1e-5
        ).fit(self.word2vec.wv.vectors_norm)
        self.word_clusters = k_means.labels_

        return k_means

    def cluster_documents(self) -> KMeans:
        from utils import l2_norm, encode_document

        if self.doc_model == "Doc2Vec":
            doc_seeds = np.array([
                self.doc2vec.infer_vector(paragraph)
                for paragraph in self.seed_paragraphs
            ])
            doc_seeds = l2_norm(doc_seeds)
        else:
            doc_seeds = [
                encode_document(paragraph)
                for paragraph in self.seed_paragraphs]

        k_means = KMeans(
            n_clusters=self.k,
            init=doc_seeds,
            n_init=1,
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