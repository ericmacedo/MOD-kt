import numpy as np
from pathlib import Path
from typing import Iterable
from nltk.stem import wordnet
from sklearn.utils import shuffle
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from multiprocessing import cpu_count
from os.path import basename, splitext, isfile
from utils import process_text, calculateSample

name = splitext(basename(__file__))[0]


def model_path(userId: str) -> str:
    return str(Path(
        f"./users/{userId}/{name}.bin"
    ).resolve())


def load_model(userId: str) -> Word2Vec:
    path = model_path(userId)
    if isfile(path):
        model = Word2Vec.load(path)
        return model
    return None


def save_model(userId: str, model: Word2Vec):
    model.save(model_path(userId))


def train_model(userId: str, corpus: Iterable[str]) -> Word2Vec:
    sentences = [doc.split(" ") for doc in corpus]

    corpus_size = len(corpus)

    model = Word2Vec(
        window=8,
        min_count=5,
        size=100,
        alpha=0.025,
        min_alpha=0.0007,
        sample=calculateSample(corpus_size),
        hs=1,
        sg=1,
        negative=15,
        ns_exponent=0.75,
        workers=cpu_count(),
        iter=40)

    model.build_vocab(sentences=sentences)

    model.train(
        shuffle(sentences),
        total_examples=corpus_size,
        epochs=40)

    model.wv.init_sims(replace=True)
    save_model(userId=userId, model=model)
    return model


def get_vectors(userId: str,
                data: Iterable[str] = None) -> Iterable[Iterable[float]]:
    model = load_model(userId=userId)
    return model.wv.vectors.tolist()


def cluster(userId: str,
            k: int,
            seed: dict = None) -> Iterable[Iterable[float]]:
    def handle_unseen_words(words: list) -> list:
        words_filtered = [
            *filter(lambda word: word in model.wv, words)]
        if len(words) != 0 and len(words_filtered) == 0:
            synonyms = []
            for word in words:
                synonyms += [process_text(syn) for syn in synonyms(word)]
            synonyms = [
                *filter(lambda word: word in model.wv, synonyms)]
            if len(synonyms) == 0:
                raise Exception(
                    "Neither the words nor its synonyms in the vocabulary")
            else:
                words_filtered = [*synonyms]

        return words_filtered

    def synonyms(word: str) -> list:
        word = word.replace("-", "_")
        synonyms = []
        for syn in wordnet.synsets(word):
            for lm in syn.lemmas():
                synonyms.append(lm.name())
        return [*set(synonyms)]

    model = load_model(userId=userId)

    if seed:  # UPDATE CLUSTERS GIVEN USER SEEDS
        init_mode = np.zeros((k, model.vector_size))
        for i in range(k):
            positive = []
            negative = []
            for word in seed["cluster_words"][i]:
                if word["weight"] > 0:
                    positive.append(word["word"])
                else:
                    negative.append(word["word"])

            # Handling unseen words for Word2Vec
            # FastText can handle unseen words
            positive = handle_unseen_words(positive)
            negative = handle_unseen_words(negative)

            seed_terms = positive + [
                term[0]
                for term in model.wv.most_similar(
                    positive=(positive if positive else None),
                    negative=(negative if negative else None),
                    topn=(50 - len(positive)))
            ]

            init_mode[i] = np.mean([
                model.wv.word_vec(term)
                for term in seed_terms
            ], axis=0)
    else:  # NEW RANDOM CLUSTERS
        init_mode = "k-means++"

    # Clustering word vectors
    k_means = KMeans(
        n_clusters=k,
        init=init_mode,
        n_init=10,
        tol=1e-5
    ).fit(model.wv.vectors)

    return k_means.cluster_centers_


def seed_paragraph(userId: str, centroid: Iterable, topn: int = 50) -> dict:
    model = load_model(userId=userId)

    return dict(
        paragraph=[
            term[0]
            for term in model.wv.similar_by_vector(centroid, topn=topn)]
    )


def most_similar(userId: str, positive: list, topn: int = 10) -> list:
    pass
