import logging
import json
from os import environ
from clusterer import Clusterer
from utils import (
    process_text, term_frequency,
    t_SNE, make_response,
    similarity_graph, sankey_graph,
    batch_processing, l2_norm)
from flask import Blueprint, request
from werkzeug.utils import secure_filename
from models.user import User
from models.document import Document

LOGGER = logging.getLogger(__name__)

api = Blueprint('api', __name__)


@api.route("auth", methods=["POST"])
# Authetication
#   Returns the userData if success
def auth():
    try:
        if request.method == 'POST':
            userId = request.form["userId"]

            user = User(userId=userId)
            if user:
                return make_response({
                    "status": "Success",
                    "userData": user.userData()})
            else:
                raise Exception("No such user exists!")
    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@api.route("corpus", methods=["POST", "PUT"])
# CRUD operations on the corpus
#   POST:   Delete operation
#   PUT:    Upload operation
def corpus():
    try:
        userId = request.form["userId"]

        user = User(userId=userId)
        if not user:
            raise Exception("No such user exists")

        newData, content, file_name, n_entries = [], [], [], 0

        if request.method == 'PUT':
            f_file = request.files.getlist("file")[0]
            f_format = request.form["format"]
            f_name = secure_filename(request.form["fileName"])

            if f_format == "file-pdf":
                from .utils import pdf_to_string

                file_name.append(f_name)
                content.append(pdf_to_string(f_file))

                n_entries += 1
            elif f_format == "file-csv":
                import pandas as pd

                pd_csv = pd.read_csv(f_file, encoding="utf-8")
                csv_fields = request.form["fields"].split(",")

                for index, row in pd_csv.iterrows():
                    csv_content = ""
                    for field in csv_fields:
                        csv_content += f"{row[field]} "

                    file_name.append(f"{f_name}_{index}")
                    content.append(csv_content)

                    n_entries += 1

                del pd_csv, csv_fields, csv_content

            elif f_format == "file-alt":
                file_name.append(f_name)
                content.append(f_file.stream.read().decode(
                    "utf-8", errors="ignore"))

                n_entries += 1

            del f_file, f_format, f_name

            # The following loop saves memory
            for i in range(n_entries):
                doc = dict(
                    file_name=file_name.pop(0),
                    content=process_text(content.pop(0)), deep=False)

                doc = user.append_document(
                    file_name=doc["file_name"],
                    content=doc["content"])

                newData.append(doc)
                del doc

            del file_name, content, n_entries

        elif request.method == "POST":
            RESET_FLAG = True if request.form["RESET_FLAG"] == "true" else False

            if RESET_FLAG:  # RESET WORKSPACE
                user.clear_workspace()
            else:
                ids = request.form["ids"].split(",")
                user.delete_documents(ids)

        del user

        return make_response({
            "status": "Success",
            "newData": newData})
    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@api.route("process_corpus", methods=["PUT", "POST"])
# Operation to process the corpus
#   It computes:
#       * FastText vectors
#       * t-SNE
#       * Distance matrix (graph representation)
def process_corpus():
    try:
        if request.method == "POST":  # ground up processing
            userId = request.form["userId"]
            word_model = request.form["word_model"]
            document_model = request.form["document_model"]

            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            stop_words = request.form["stop_words"].split(",")
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

            return make_response({
                "status": "success",
                "userData": user.userData()})

        elif request.method == "PUT":  # Increment processing
            userId = request.form["userId"]

            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            new_docs = request.form["new_docs"].split(",")

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

            if user.word_model == "FastText":
                user.fast_text = Fast_Text(user=user)
            else:
                user.word2vec = Word_2_Vec(user=user)

            if user.doc_model == "S-BERT":
                embeddings = encode_documents([
                    doc.content for doc in docs])
                for doc in docs:
                    doc.embedding = embeddings.pop(0)
            else:
                doc2vec = user.doc2vec

                for doc in docs:
                    doc.embedding = l2_norm(doc2vec.infer_vector(
                        doc.processed.split(" "), steps=5
                    )).tolist()

            corpus = user.corpus  # refresh corpus reference

            graph = similarity_graph(corpus)
            user.graph = graph

            tsne = t_SNE(corpus)
            user.tsne = tsne

            seed = json.loads(request.form["seed"])
            k = seed["cluster_k"]

            clusterer = Clusterer(
                user=user,
                index=user.index,
                k=k,
                seed=seed)

            # TODO SHORTEN response
            return make_response({
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
            })

    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@api.route("projection", methods=["POST"])
def projection():
    try:
        if request.method == "POST":
            userId = request.form["userId"]

            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            index = request.form["index"].split(",")
            corpus = user.corpus

            corpus = [*filter(lambda doc: doc.id in index, corpus)]

            projection = request.form["projection"]

            if projection == "t-SNE":
                perplexity = int(request.form["perplexity"])
                projection = t_SNE(corpus, perplexity=perplexity)

            return make_response({
                "status": "success",
                "projection": projection})

    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@api.route("session", methods=["GET", "PUT", "POST"])
def session():
    try:
        session = None
        if request.method == "GET":
            userId = request.args["userId"]
            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            sessionId = request.args["sessionId"] if (
                "sessionId" in request.args) else None

            if not sessionId:
                raise Exception("No such session exists")

            user = User(userId=userId)
            session = user.sessionData(id=sessionId)

        elif request.method == "PUT":
            userId = request.form["userId"]
            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            session = json.loads(request.form["sessionData"])
            session = user.append_session(
                name=session["name"],
                notes=session["notes"],
                index=session["index"],
                clusters=session["clusters"],
                graph=session["graph"],
                tsne=session["tsne"],
                controls=session["controls"],
                selected=session["selected"],
                focused=session["focused"],
                highlight=session["highlight"],
                word_similarity=session["word_similarity"])

        elif request.method == "POST":
            userId = request.form["userId"]
            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            sessionId = request.form["sessionId"]

            user.delete_sessions([sessionId])

        return make_response({
            "status": "success",
            "sessionData": session
        })

    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@api.route("cluster", methods=["POST"])
def cluster():
    try:
        if request.method == "POST":
            userId = request.form["userId"]

            user = User(userId=userId)
            recluster = True if request.form["recluster"] == "true" else False

            if recluster:
                seed = json.loads(request.form["seed"])
                k = seed["cluster_k"]
                index = request.form["index"].split(",")
                session = {}
            else:
                session = user.sessionData(id=None)
                seed = None
                k = int(request.form["cluster_k"])
                index = user.index

            clusterer = Clusterer(
                user=user,
                index=index,
                k=k,
                seed=seed)

            session["clusters"] = {
                "cluster_k":        clusterer.k,
                "labels":           clusterer.doc_labels.tolist(),
                "colors":           clusterer.colors,
                "cluster_names":    clusterer.cluster_names,
                "cluster_docs":     clusterer.doc_clusters,
                "cluster_words":    [[
                    {"word": word, "weight": 1}
                    for word in paragraph["paragraph"][:5]
                ] for paragraph in clusterer.seed_paragraphs
                ]
            }

            return make_response({
                "status": "success",
                "sessionData": session})

    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@api.route("word_similarity", methods=["POST"])
def word_similarity():
    try:
        if request.method == "POST":
            userId = request.form["userId"]

            query = request.form["query"].split(",")

            user = User(userId=userId)
            word_sim = user.word_vectors.most_similar(user.userId, query)

            return make_response({
                "status": "success",
                "query": query,
                "most_similar": word_sim})
    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@api.route("sankey", methods=["GET"])
def sankey():
    try:
        if request.method == "GET":
            userId = request.args["userId"]

            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            return make_response(sankey_graph(user=user))
    except Exception as e:
        LOGGER.debug(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500
