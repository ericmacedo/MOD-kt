import numpy as np
from pathlib import Path
from models import BagOfWords
from sklearn.cluster import KMeans
from typing import Iterable, List, Dict
from scipy.spatial.distance import cosine
from os.path import basename, splitext, isfile

name = splitext(basename(__file__))[0]

# default parameters
confidenceUser = 50
documentPercentileInit = 20.0 * 2 ** (2*(1-confidenceUser/50.0))


def model_path(userId: str) -> str:
    return str(Path(
        f"./users/{userId}/{name}.bin"
    ).resolve())


def load_model(userId: str) -> BagOfWords:
    path = model_path(userId)
    if isfile(path):
        return BagOfWords.load(path)
    return None


def save_model(userId: str, model: BagOfWords):
    model.save(model_path(userId))


def train_model(userId: str, corpus: Iterable[str]) -> Iterable:
    model = BagOfWords()
    model.train(corpus=corpus)
    save_model(userId=userId, model=model)
    return model.matrix.tolist()


def get_vectors(userId: str, data: Iterable[str]) -> Iterable[Iterable[float]]:
    model = load_model(userId=userId)
    if not model:
        model = train_model(
            userId=userId,
            corpus=data)

    return model.matrix.tolist()


def cluster(userId: str,
            seed_paragraphs: Iterable[Dict[str, Iterable]],
            k: int,
            embeddings: List) -> Iterable[int]:
    # iKMeans clustering
    embeddings = np.array(embeddings)
    n, m = embeddings.shape

    seedDocumentsTerms = [i["vector"] for i in seed_paragraphs]

    # select documents related to the selected terms and calculate the centroid of documents
    seedDocumentsTermsCosine = np.zeros((k, n))
    for index, centroid in enumerate(seedDocumentsTerms):
        for document_index in range(0, n):
            seedDocumentsTermsCosine[index, document_index] = cosine(
                centroid, embeddings[document_index, :])

    # upper bound for the number of terms of each cluster
    documentPercentile = documentPercentileInit * n / 100
    seedDocuments = np.zeros((k, m))
    for index, center in enumerate(seedDocumentsTermsCosine):
        average = np.average(center)
        minDistance = center.min()
        counter = 0
        while minDistance < average:
            min_idx = center.argmin()
            seedDocuments[index] += embeddings[min_idx, :]
            counter += 1
            if counter > documentPercentile:
                break
            minDistance = center[min_idx]
            center[min_idx] = 2
        seedDocuments[index] /= counter

    # run kmeans
    return KMeans(
        n_clusters=k,
        init=seedDocuments,
        n_init=1
    ).fit_predict(embeddings)
