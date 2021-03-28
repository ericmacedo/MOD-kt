from flask import (
    Flask, request, Response,
    redirect, render_template)
from flask_cors import CORS
from werkzeug.utils import secure_filename

import logging

from models import User, Document

from clusterer import Clusterer

from utils import (
    process_text, term_frequency,
    t_SNE, displaCy_NER, most_similar,
    similarity_graph, l2_norm,
    encode_document, Doc_2_Vec,
    Fast_Text, Word_2_Vec, sankey_graph)

import json

import faulthandler
faulthandler.enable()

from nltk import download as NLTK_Downloader
NLTK_Downloader("stopwords", quiet=True)

logging.basicConfig(filename="./log/flask.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

app = Flask(__name__, static_url_path="")
CORS(app)

@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")

@app.route("/auth", methods=["POST"])
# Authetication
#   Returns the userData if success
def auth():
    try:
        if request.method == 'POST':
            userId = request.form["userId"]

            user = User(userId=userId)
            if user:
                return Response(json.dumps({
                    "status": "Success",
                    "userData": user.userData()
                }), content_type='application/json')  
            else:
                raise Exception("No such user exists!")
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/corpus", methods=["POST", "PUT"])
# CRUD operations on the corpus
#   POST:   Delete operation
#   PUT:    Upload operation
def corpus():
    try:
        userId = request.form["userId"]

        user = User(userId=userId)
        if not user:
            raise Exception("No such user exists")
        
        newData = []
        content = []
        processed = []
        file_name = []
        tf = []
        n_entries = 0
        
        if request.method == 'PUT':
            f_file = request.files.getlist("file")[0]
            f_format = request.form["format"]
            f_name = secure_filename(request.form["fileName"])
            
            if f_format == "file-pdf":
                from utils import pdf_to_string

                file_name.append(f_name)
                content.append(process_text(
                    pdf_to_string(f_file)))
                processed.append(
                    process_text(content[0], deep=True))
                tf.append(
                    term_frequency(processed[0]))

                n_entries += 1
            elif f_format == "file-csv":
                import pandas as pd

                csv_fields = request.form["fields"].split(",")

                pd_csv = pd.read_csv(f_file, encoding="utf-8")

                for index, row in pd_csv.iterrows():
                    csv_content = ""
                    for field in csv_fields:
                        csv_content += f"{row[field]} "
                    
                    file_name.append(f"{f_name}_{index}")
                    content.append(process_text(csv_content))
                    processed.append(process_text(csv_content, deep=True))
                    tf.append(
                        term_frequency(processed[index]))
                    
                    n_entries += 1
                del pd_csv, csv_fields, csv_content

            elif f_format == "file-alt":
                file_name.append(f_name)
                content.append(process_text(
                    f_file.stream.read().decode("utf-8", errors="ignore")))
                processed.append(
                    process_text(content[0], deep=True))
                tf.append(
                    term_frequency(processed[0]))
                
                n_entries += 1

            del f_file, f_format, f_name

            # The following loop saves memory
            for i in range(n_entries):
                doc = dict(
                    file_name       = file_name.pop(0),
                    content         = content.pop(0),
                    term_frequency  = tf.pop(0),
                    processed       = processed.pop(0))
                
                doc = user.append_document(
                    file_name       = doc["file_name"],
                    content         = doc["content"],
                    processed       = doc["processed"],
                    term_frequency  = doc["term_frequency"])

                newData.append(doc)
                del doc

            del file_name, content, processed, tf, n_entries

        elif request.method == "POST":
            RESET_FLAG = True if request.form["RESET_FLAG"] == "true" else False

            if RESET_FLAG: # RESET WORKSPACE
                user.clear_workspace()
            else:
                ids = request.form["ids"].split(",")
                user.delete_documents(ids)

        del user
        
        return Response(json.dumps({
            "status": "Success",
            "newData": newData
        }), content_type='application/json')
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/process_corpus", methods=["GET", "POST"])
# Operation to process the corpus
#   It computes:
#       * FastText vectors
#       * t-SNE
#       * Distance matrix (graph representation)
def process_corpus():
    try:
        if request.method == "GET": # ground up processing
            userId = request.args["userId"]
            performance = request.args["performance"].upper()

            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            user.generate_index()
            corpus = user.corpus

            if performance == "HIGH":
                # SETTINGS
                user.doc_model = "S-BERT"
                user.word_model = "FastText"
                
                user.fast_text = Fast_Text(user)
                embeddings = encode_documents([
                    doc.content for doc in corpus])
                for doc in corpus:
                    doc.embedding = embeddings.pop(0)
            else:
                # SETTINGS
                user.doc_model = "Doc2Vec"
                user.word_model = "Word2Vec"

                user.word2vec = Word_2_Vec(user)

                model = Doc_2_Vec(user)
                user.doc2vec = model

                for index, doc in enumerate(corpus):
                    doc.embedding = l2_norm(
                        model.infer_vector(doc.processed.split(" "), steps=5)
                    ).tolist()

                del model
            
            graph  = similarity_graph(corpus)
            user.graph = graph
            user.tsne   = t_SNE(corpus)

            user.isProcessed = True
            
            return Response(json.dumps({
                "status": "success",
                "userData": user.userData()
            }), content_type='application/json')

        elif request.method == "POST": # Increment processing
            userId = request.form["userId"]

            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            new_docs = request.form["new_docs"].split(",")
            
            docs = [
                Document(userId=userId, id=id)
                for id in new_docs]

            user.generate_index()
            corpus = user.corpus

            if user.word_model == "FastText":
                user.fast_text = Fast_Text(user=user)
            else:
                user.word2vec = Word_2_Vec(user=user)

            if user.doc_model == "S-BERT":
                embeddings = encode_documents([
                    doc.content for doc in corpus])
                for doc in corpus:
                    doc.embedding = embeddings.pop(0)
            else:
                doc2vec = user.doc2vec

                for doc in docs:
                    doc.embedding = l2_norm(
                        doc2vec.infer_vector(doc.processed.split(" "), steps=5)
                    ).tolist()

            corpus = user.corpus # refresh corpus reference
            
            graph  = similarity_graph(corpus)
            user.graph = graph
            
            tsne  = t_SNE(corpus)
            user.tsne = tsne

            seed = json.loads(request.form["clusters"])
            k = seed["cluster_k"]

            clusterer = Clusterer(
                user=user,
                index=user.index,
                k=k,
                seed=seed)

            return Response(json.dumps({
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
                            { "word": word, "weight": 1 }
                            for word in paragraph[:5]
                            ] for paragraph in clusterer.seed_paragraphs
                        ]
                    }
                }
            }), content_type='application/json')
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/projection", methods=["POST"])
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

            if projection ==  "t-SNE":
                perplexity = int(request.form["perplexity"])
                projection = t_SNE(corpus, perplexity=perplexity)

            return Response(json.dumps({
                "status": "success",
                "projection": projection
            }), content_type='application/json')

    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/session", methods=["GET", "PUT", "POST"])
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
                name            = session["name"],
                notes           = session["notes"],
                index           = session["index"],
                clusters        = session["clusters"],
                graph           = session["graph"],
                tsne            = session["tsne"],
                controls        = session["controls"],
                selected        = session["selected"],
                focused         = session["focused"],
                highlight       = session["highlight"],
                word_similarity = session["word_similarity"])

        elif request.method == "POST":
            userId = request.form["userId"]
            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            sessionId = request.form["sessionId"]

            user.delete_sessions([sessionId])

        return Response(json.dumps({
            "status": "success",
            "sessionData": session
        }), content_type='application/json')

    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/cluster", methods=["POST"])
def cluster():
    try:
        if request.method == "POST":
            userId = request.form["userId"]

            user = User(userId=userId)
            
            if "session" in request.form:
                session = json.loads(request.form["session"])
                seed = session["clusters"]
                k = seed["cluster_k"]
            else:
                session = user.sessionData(id=None)
                seed = None
                k = int(request.form["cluster_k"])

            clusterer = Clusterer(
                user=user,
                index=session["index"],
                k=k,
                seed=seed)

            session["clusters"] = {
                "cluster_k":        clusterer.k,
                "labels":           clusterer.doc_labels.tolist(),
                "colors":           clusterer.colors,
                "cluster_names":    clusterer.cluster_names,
                "cluster_docs":     clusterer.doc_clusters,
                "cluster_words":    [[
                    { "word": word, "weight": 1 }
                    for word in paragraph[:5]
                    ] for paragraph in clusterer.seed_paragraphs
                ]
            }
                    
            return Response(json.dumps({
                "status": "success",
                "sessionData": session
            }), content_type='application/json')

    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/word_similarity", methods=["POST"])
def word_similarity():
    try:
        if request.method == "POST":
            userId = request.form["userId"]

            query = request.form["query"].split(",")

            user = User(userId=userId)
            word_sim = most_similar(user, query)

            return Response(json.dumps({
                "status": "success",
                "query": query,
                "most_similar": word_sim
            }), content_type='application/json')
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/sankey", methods=["GET"])
def sankey():
    try:
        if request.method == "GET":
            userId = request.args["userId"]
            
            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            return Response(json.dumps(
                sankey_graph(user=user)
            ), content_type='application/json')
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500