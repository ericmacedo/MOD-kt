import os

from flask import (
    Flask, request, 
    redirect, render_template)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from models import User

from utils import (
    process_text, term_frequency)

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
                content.append(pdf_to_string(f_file))
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
                    content.append(csv_content)
                    processed.append(process_text(csv_content))
                    tf.append(
                        term_frequency(processed[index]))
                    
                    n_entries += 1
                del pd_csv, csv_fields, csv_content

            elif f_format == "file-alt":
                file_name.append(f_name)
                content.append(
                    f_file.stream.read().decode("utf-8", errors="ignore"))
                processed.append(
                    process_text(content[0]))
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
                    # embedding       = embeddings.pop(0),
                    processed       = processed.pop(0))
                
                doc = user.append_document(
                    file_name       = doc["file_name"],
                    content         = doc["content"],
                    processed       = doc["processed"],
                    # embedding       = doc["embedding"],
                    term_frequency  = doc["term_frequency"])

                newData.append(doc)
                del doc

            # TODO UPDATE WORD2VEC MODEL
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
#       * Word2Vec vectors
#       * t-SNE
#       * Distance matrix (graph representation)
def process_corpus():
    try:
        from utils import (
            distance_graph, t_SNE,
            encode_document,
            Word2Vec, Doc2Vec)

        if request.method == "GET":
            userId = request.args["userId"]
            model = request.args["model"]

            user = User(userId=userId)
            if not user:
                raise Exception("No such user exists!")

            user.generate_index()
            corpus = user.corpus

            # # TRAIN WORD VECTORS
            user.word2vec = Word2Vec(user)

            if model == "S-BERT":
                embeddings = [
                    encode_document(doc.processed)
                    for doc in corpus]
            else:
                # TRAIN PARAGRAPH VECTORS
                model = Doc2Vec(user)
                user.doc2vec = model
                embeddings = [
                    vec.tolist()
                    for vec in model.docvecs.vectors_docs_norm]
                del model
            
            for doc in corpus:
                doc.embedding = embeddings.pop(0)

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

@app.route("/projection", methods=["GET"])
def projection():
    pass

@app.route("/session", methods=["GET", "PUT"])
def session():
    try:
        if request.method == "GET":
            userId = request.args["userId"]
            sessionId = request.args["sessionId"] if (
                "sessionId" in request.args) else None

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
    pass

if __name__ == "Vis-Kt":
    app.run(debug=True)
