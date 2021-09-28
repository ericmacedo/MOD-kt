import pickle
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from typing import List, Iterable, Dict
from dataclasses import dataclass, field
from os.path import basename, splitext, isfile
from sentence_transformers import SentenceTransformer


@dataclass
class Bert:
    model_name: str
    embeddings: list = field(default_factory=list)

    def __init__(self, model_name: str = "allenai-specter"):
        self.model_name = model_name

    def train(self, corpus: List[str]) -> list:
        transformer = SentenceTransformer(self.model_name)
        self.embeddings = transformer.encode(corpus).tolist()

        del transformer
        return self.embeddings

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


def train_model(userId: str, corpus: Iterable[str]) -> Bert:
    model = Bert(model_name="allenai-specter")
    model.train(corpus=corpus)
    return model


def get_vectors(userId: str, data: Iterable[str]) -> Iterable[Iterable[float]]:
    model = Bert(model_name="allenai-specter")
    return model.train(corpus=data)


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
