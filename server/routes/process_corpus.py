from fastapi import APIRouter, Form
from routes import LOGGER, fetch_user
from utils import (
    process_text, term_frequency,
    t_SNE, similarity_graph,
    batch_processing)
from clusterer import Clusterer

from models.document import Document
import json


router = APIRouter(prefix="/process_corpus")


@router.post("/")
def process_corpus(userId: str = Form(...),
                   word_model: str = Form(...),
                   document_model: str = Form(...),
                   stop_words: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        stop_words = stop_words.split(",")
        user.stop_words = stop_words

        user.generate_index()
        corpus = user.corpus

        processed = batch_processing(
            fn=process_text,
            data=[doc.content for doc in corpus],
            deep=True,
            stop_words=stop_words)
        tf = batch_processing(fn=term_frequency, data=processed)

        for doc in corpus:
            doc.term_frequency = tf.pop(0)
            doc.processed = processed.pop(0)

        user.doc_model = document_model
        user.word_model = word_model

        embeddings = user.train()

        for doc in corpus:
            doc.embedding = embeddings.pop(0)

        graph = similarity_graph(corpus)
        user.graph = graph
        user.tsne = t_SNE(corpus)

        user.isProcessed = True

        return {"status": "success", "userData": user.userData()}

    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "code": 500,
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }


@router.put("/")
def process_corpus(userId: str = Form(...),
                   new_docs: str = Form(...),
                   seed: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        new_docs = new_docs.split(",")

        docs = [
            Document(userId=userId, id=id)
            for id in new_docs]
        stop_words = user.stop_words

        processed = batch_processing(
            fn=process_text,
            data=[doc.content for doc in docs],
            deep=True,
            stop_words=stop_words)
        tf = batch_processing(fn=term_frequency, data=processed)

        for doc in docs:
            doc.term_frequency = tf.pop(0)
            doc.processed = processed.pop(0)

        user.generate_index()
        corpus = user.corpus

        embeddings = user.train()

        for doc in corpus:
            doc.embedding = embeddings.pop(0)

        corpus = user.corpus  # refresh corpus reference

        graph = similarity_graph(corpus)
        user.graph = graph

        tsne = t_SNE(corpus)
        user.tsne = tsne

        seed = json.loads(seed)
        k = seed["cluster_k"]

        clusterer = Clusterer(
            user=user,
            index=user.index,
            k=k,
            seed=seed)

        return {
            "status": "success",
            "newData": {
                "new_index": [doc.id for doc in docs],
                "index": user.index,
                "corpus": [doc.as_dict() for doc in user.corpus],
                "graph": user.graph,
                "tsne": user.tsne,
                "clusters": {
                    "cluster_k":        clusterer.k,
                    "labels":           clusterer.doc_labels.tolist(),
                    "colors":           clusterer.colors,
                    "cluster_names":    clusterer.cluster_names,
                    "cluster_docs":     clusterer.doc_clusters,
                    "cluster_words":    [[
                        {"word": word, "weight": 1}
                        for word in paragraph[:5]
                    ] for paragraph in clusterer.seed_paragraphs
                    ]
                }
            }
        }

    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "code": 500,
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }
