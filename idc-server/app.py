import os

from flask import (
    Flask, request, 
    redirect, render_template)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from models import User

from clusterer import Clusterer

from utils import (
    process_text, term_frequency,
    t_SNE, displaCy_NER, most_similar,
    distance_graph,
    encode_document, Doc_2_Vec,
    Fast_Text, Word_2_Vec)

import spacy

import json

from nltk import download as NLTK_Downloader
NLTK_Downloader("stopwords", quiet=True)

ALLOWED_EXTENSIONS = {"csv", "pdf", "txt"}

app = Flask("Vis-Kt")
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)

@app.route("/auth", methods=["POST"])
# Authetication
#   Returns the userData if success
def auth():
    try:
        if request.method == 'POST':
            userId = request.form["userId"]

            user = User(userId=userId)
            if user:
                return {
                    "status": "Success",
                    "userData": user.userData()
                }, 200
            else:
                raise Exception("No such user exists!")
    except Exception as e:
        print(e)
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
                    process_text(content[0]))
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

            # TODO UPDATE FASTTEXT MODEL
            #   Only runs if the corpus is processed

            del file_name, content, processed, tf, n_entries

        elif request.method == "POST":
            ids = request.form["ids"].split(",")

            RESET_FLAG = True if request.form["RESET_FLAG"] == "true" else False

            if RESET_FLAG: # RESET WORKSPACE
                user.clear_workspace()
            else:
                user.delete_documents(ids)

            del ids, RESET_FLAG

        del user
        
        return {
            "status": "Success",
            "newData": newData
        }, 200
    except Exception as e:
        print(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

@app.route("/process_corpus", methods=["GET"])
# Operation to process the corpus
#   It computes:
#       * FastText vectors
#       * t-SNE
#       * Distance matrix (graph representation)
def process_corpus():
    try:
        if request.method == "GET":
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
                
                embeddings = []
                svg = []
                
                user.fast_text = Fast_Text(user)

                nlp = spacy.load("en_core_web_lg")

                for doc in corpus:
                    embeddings.append(
                        encode_document(doc.processed))
                    svg.append(
                        displaCy_NER(nlp(doc.processed)))
            else:
                # SETTINGS
                user.doc_model = "Doc2Vec"
                user.word_model = "Word2Vec"

                user.word2vec = Word_2_Vec(user)

                model = Doc_2_Vec(user)
                user.doc2vec = model
                embeddings = [
                    vec.tolist()
                    for vec in model.docvecs.vectors_docs_norm]

                nlp = spacy.load("en_core_web_sm")
                svg = [
                    displaCy_NER(nlp(
                        process_text(doc.content,deep=False)
                    )) for doc in corpus]

                del model
            del nlp
            
            for doc in corpus:
                doc.embedding = embeddings.pop(0)
                doc.svg = svg.pop(0)

            user.graph  = distance_graph(corpus)
            user.tsne   = t_SNE(corpus)

            return {
                "status": "success",
                "userData": user.userData()
            }, 200

    except Exception as e:
        print(e)
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

            return {
                "status": "success",
                "projection": projection
            }, 200

    except Exception as e:
        print(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500


@app.route("/session", methods=["GET", "PUT"])
def session():
    try:
        if request.method == "GET":
            userId = request.args["userId"]
            sessionId = request.args["sessionId"] if (
                "sessionId" in request.args) else None

            if not sessionId:
                raise Exception("No such sessione exists")

            user = User(userId=userId)
            session = user.sessionData(sessionId=sessionId)
            
            return {
                "status": "success",
                "sessionData": session
            }, 200
        elif request.method == "PUT":
            userId = request.form["userId"]
            session = request.form["sessionData"]

            user = User(userId=userId)
            session = user.append_session(
                name        = session["name"],
                notes       = session["notes"],
                index       = session["index"],
                clusters    = session["clusters"],
                graph       = session["graph"],
                tsne        = session["tsne"],
                controls    = session["controls"])

            return {
                "status": "success",
                "sessionData": session
            }, 200

    except Exception as e:
        print(e)
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
                session = user.sessionData(sessionId=None)
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
                    
            return {
                "status": "success",
                "sessionData": session
            }, 200

    except Exception as e:
        print(e)
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

            return {
                "status": "success",
                "most_similar": word_sim
            }, 200
    except Exception as e:
        print(e)
        return {
            "status": "Fail",
            "message": {
                "title": str(type(e)),
                "content": str(e)
            }
        }, 500

if __name__ == "Vis-Kt":
    app.run(debug=True)
