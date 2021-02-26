import os

from flask import (
    Flask, request, 
    redirect, render_template)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from database.db import initialize_db
from database.models import User, EmbDocument

from utils import get_userData

ALLOWED_EXTENSIONS = {"csv", "pdf", "txt"}

app = Flask("Vis-Kt")
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)

# MongoDB setup
app.config['MONGODB_SETTINGS'] = {
    'db': 'idc',
    'host': 'localhost',
    'port': 27017}
initialize_db(app)

@app.route("/auth", methods=["POST"])
# Authetication
#   Returns the userData if success
def auth():
    try:
        if request.method == 'POST':
            userId = request.form["userId"]

            user = User.objects(userId=userId)

            if user:
                return {
                    "status": "Success",
                    "userData": get_userData(userId=userId)
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
        from uuid import uuid4

        from utils import (
            process_text,
            term_frequency)

        userId = request.form["userId"]

        user = User.objects(userId=userId)
        if user:
            user = user.get()
        else:
            raise Exception("No such user exists")
        
        newData = []
        content = []
        processed = []
        file_name = []
        tf = []
        uuid = []
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
                uuid.append(str(uuid4()))

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
                    uuid.append(str(uuid4()))
                    
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
                uuid.append(str(uuid4()))
                
                n_entries += 1

            del f_file, f_format, f_name

            # The following loop saves memory
            for i in range(n_entries):
                doc = dict(
                    id              = uuid.pop(0),
                    file_name       = file_name.pop(0),
                    content         = content.pop(0),
                    term_frequency  = tf.pop(0),
                    # embedding       = embeddings.pop(0),
                    processed       = processed.pop(0))
                
                User.objects(userId=userId).update_one(
                    push__corpus=EmbDocument(
                        id              = doc["id"],
                        file_name       = doc["file_name"],
                        content         = doc["content"],
                        processed       = doc["processed"],
                        # embedding       = doc["embedding"],
                        term_frequency  = doc["term_frequency"]))

                newData.append(doc)
                del doc
            # user.save()

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
                ## ONLY execute if embeddings are calculated in upload time
                # user.graph = cosine_distance_graph(
                #   [ doc["embedding"] for doc in user.corpus]
                # )
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
#       * UMAP
#       * Cosine distance matrix (graph representation)
def process_corpus():
    try:
        from utils import (
            cosine_distance_graph,
            encode_document,
            UMAP, t_SNE,
            Word2Vec)

        if request.method == "GET":
            userId = request.args["userId"]

            user = User.objects(userId=userId)
            if user:
                user = user.get()
            else:
                raise Exception("No such user exists!")

            for doc in user.corpus:
                print(f"Calculating embedding for doc {doc.id}")
                User.objects(
                    userId=userId,
                    corpus__id=doc.id
                ).update(set__corpus__S__embedding=(
                    encode_document(doc.processed)))

            user.update(
                graph       = cosine_distance_graph(user.corpus),
                tsne        = t_SNE(user.corpus),
                umap        = UMAP(user.corpus),
                word2vec    = Word2Vec(user))

            del user

            return {
                "status": "success",
                "userData": user.as_dict()
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

if __name__ == "Vis-Kt":
    app.run(debug=True)
