from os.path import basename, splitext, isfile
from typing import List, Iterable, Dict
from sklearn.cluster import KMeans
from models.document import Bert
from pathlib import Path
import numpy as np


name = splitext(basename(__file__))[0]


def model_path(userId: str) -> str:
    return str(Path(
        f"./users/{userId}/{name}.bin"
    ).resolve())


def load_model(userId: str) -> Bert:
    path = model_path(userId)
    if isfile(path):
        return Bert.load(path)
    return None


def save_model(userId: str, model: Bert):
    model.save(model_path(userId))


def train_model(userId: str, corpus: Iterable[str]) -> Iterable:
    model = Bert(model_name="allenai-specter")

    embeddings = model.train(corpus=corpus)
    save_model(userId=userId, model=model)

    del model
    Bert.clear_memory()
    return embeddings


def get_vectors(userId: str, data: Iterable[str]) -> Iterable[Iterable[float]]:
    model = load_model(userId=userId)

    if not model:
        model = Bert(model_name="allenai-specter")

    embeddings = model.train(corpus=data)

    del model
    Bert.clear_memory()
    return embeddings


def cluster(userId: str,
            seed_paragraphs: Iterable[Dict[str, Iterable]],
            k: int,
            embeddings: List) -> Iterable[int]:
    doc_seeds = get_vectors(
        userId=userId,
        data=[" ".join(p["paragraph"]) for p in seed_paragraphs])

    return KMeans(
        n_clusters=k,
        init=np.array(doc_seeds, dtype=np.float32),
        n_init=10,
        tol=1e-5
    ).fit_predict(embeddings)
