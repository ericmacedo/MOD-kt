import os

from flask import (
    Flask, request, 
    redirect, render_template)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from database.db import initialize_db
from database.models import User, EmbDocument

from uuid import uuid4

from utils import (
    get_userData,
    process_text,
    term_frequency)

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
    if request.method == 'POST':
        userId = request.form["userId"]

        user = User.objects(userId=userId)

        if user:
            return {
                "status": "Success",
                "userData": get_userData(userId=userId)
            }, 200
        else:
            return {
                "status": "Fail"
            }, 500

@app.route("/corpus", methods=["POST", "PUT"])
# CRUD operations on the corpus
#   POST:   Delete operation
#   PUT:    Upload operation
def corpus():
    # TODO migrate to MongoDB
    userId = request.form["userId"]

    user = User.objects(userId=userId)
    if user:
        user = user.get()
    else:
        return {
            "status": "Fail"
        }, 500
    
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
                processed       = processed.pop(0))

            user.corpus.append(EmbDocument(
                id              = doc["id"],
                file_name       = doc["file_name"],
                content         = doc["content"],
                processed       = doc["processed"],
                term_frequency  = doc["term_frequency"]))

            newData.append(doc)
            del doc
        user.save()

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
        "userData": get_userData(userId=userId, newData=newData)
    }, 200

@app.route("/process_corpus", methods=["POST"])
# Operation to process the corpus
#   It computes:
#       * Word2Vec vectors
#       * t-SNE
#       * UMAP
#       * Cosine distance matrix (graph representation)
def process_corpus():
    from utils import (
        cosine_distance_graph,
        UMAP, t_SNE,
        Word2Vec)
    from models import Corpus

    if request.method == "POST":
        userId = request.form["userId"]
        corpus = Corpus.get_items(userId=userId)

        graph = cosine_distance_graph(userId=userId)


        
        tsne = t_SNE(userId=userId)
        print("t-SNE calculated")
        
        umap = UMAP(userId=userId)
        print("UMAP calculated")
        
        w2v = Word2Vec(userId=userId)
        print("Word2Vec calculated")


if __name__ == "Vis-Kt":
    app.run(debug=True)