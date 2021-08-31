import pickle
import numpy as np
from typing import List
from pathlib import Path
from multiprocessing import cpu_count
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from os.path import basename, splitext, isfile, abspath


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

    @classmethod
    def save(cls, path: str, data: np.ndarray):
        with open(path, "wb") as pkl_file:
            pickle.dump(
                obj=data,
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


def train_model(userId: str, corpus: List[str]) -> Bert:
    model = Bert(model_name="allenai-specter")
    model.train(corpus=corpus)
    return model


def get_vectors(userId: str, corpus: List[str]) -> list:
    model = Bert(model_name="allenai-specter")
    model.train(corpus=corpus)

    return model.embeddings
