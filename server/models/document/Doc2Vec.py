import numpy as np
from pathlib import Path
from sklearn.utils import shuffle
from sklearn.cluster import KMeans
from multiprocessing import cpu_count
from typing import List, Iterable, Dict
from models.document import infer_doc2vec
from os.path import basename, splitext, isfile
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from utils import calculateSample, l2_norm, batch_processing


name = splitext(basename(__file__))[0]


def model_path(userId: str) -> str:
    return str(Path(
        f"./users/{userId}/{name}.bin"
    ).resolve())


def load_model(userId: str) -> Doc2Vec:
    path = model_path(userId)
    if isfile(path):
        model = Doc2Vec.load(path)
        model.docvecs.init_sims()
        return model
    return None


def save_model(userId: str, model: Doc2Vec):
    model.save(model_path(userId))


def train_model(userId: str, corpus: Iterable[str]) -> Iterable:
    tagged_data = [
        TaggedDocument(
            doc.split(" "),
            tags=[i]
        ) for i, doc in enumerate(corpus)]

    corpus_size = len(corpus)

    model = Doc2Vec(
        dm=1,
        dm_mean=1,
        dbow_words=1,
        dm_concat=0,
        vector_size=100,
        window=8,
        alpha=0.025,
        min_alpha=0.0007,
        hs=0,
        sample=calculateSample(corpus_size),
        negative=15,
        ns_expoent=0.75,
        min_count=5,
        workers=cpu_count(),
        epochs=40)

    model.build_vocab(documents=tagged_data)

    model.train(
        documents=shuffle(tagged_data),
        total_examples=model.corpus_count,
        epochs=40)

    model.docvecs.init_sims()
    save_model(userId=userId, model=model)
    return get_vectors(userId=userId, data=corpus)


def get_vectors(userId: str, data: Iterable[str]) -> List[List[float]]:
    model = load_model(userId=userId)

    model.docvecs.init_sims()

    return l2_norm(batch_processing(
        fn=infer_doc2vec,
        data=data,
        model=model)
    ).tolist() if data else model.docvecs.vectors_docs_norm.tolist()


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
