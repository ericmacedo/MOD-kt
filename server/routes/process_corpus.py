from routes import LOGGER, fetch_user, UserData, ErrorResponse
from typing import List, Dict, Optional
from models.document import Document
from utils import (
    process_text, term_frequency,
    batch_processing, t_SNE,
    similarity_graph)
from clusterer import Clusterer
from pydantic import BaseModel
from fastapi import APIRouter


class ProcessCorpusBaseForm(BaseModel):
    userId: str


class ProcessCorpusForm(ProcessCorpusBaseForm):
    userId: str
    word_model: str
    document_model: str
    stop_words: List[str]


class ProcessCorpusIncrementForm(ProcessCorpusBaseForm):
    new_docs: List[str]
    seed: Dict


class ProcessCorpusResponse(BaseModel):
    status: str = "Success"
    userData: Optional[UserData]
    newData: Optional[Dict]


router = APIRouter(prefix="/process_corpus")


@router.post("")
def process_corpus(form: ProcessCorpusForm):
    try:
        user = fetch_user(userId=form.userId)

        user.stop_words = form.stop_words

        user.generate_index()
        corpus = user.corpus

        processed = batch_processing(
            fn=process_text,
            data=[doc.content for doc in corpus],
            deep=True,
            stop_words=user.stop_words)
        tf = batch_processing(fn=term_frequency, data=processed)

        for doc in corpus:
            doc.term_frequency = tf.pop(0)
            doc.processed = processed.pop(0)

        user.doc_model = form.document_model
        user.word_model = form.word_model

        embeddings = user.train()

        for doc in corpus:
            doc.embedding = embeddings.pop(0)

        graph = similarity_graph(corpus)
        user.graph = graph
        user.tsne = t_SNE(corpus)

        user.isProcessed = True

        response = {"userData": UserData(**user.userData())}
        return ProcessCorpusResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)


@router.put("")
def process_corpus(form: ProcessCorpusIncrementForm):
    try:
        user = fetch_user(userId=form.userId)

        docs = [
            Document(userId=form.userId, id=id)
            for id in form.new_docs]
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

        clusterer = Clusterer(
            user=user,
            index=user.index,
            k=form.seed.cluster_k,
            seed=form.seed)

        response = {
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
        return ProcessCorpusResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)
