import os

from flask import (
    Flask, request, 
    redirect, render_template)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from models import Corpus

ALLOWED_EXTENSIONS = {"csv", "pdf", "txt"}
USERS_FOLDER = "./users"

app = Flask("Vis-Kt")
app.config['UPLOAD_FOLDER'] = USERS_FOLDER
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/auth", methods=["POST"])
def auth():
    if request.method == 'POST':
        userId = request.form["userId"]

        if os.path.isdir(f"{USERS_FOLDER}/{userId}"):
            from models import Corpus

            return {
                "status": "Success",
                "userData": {
                    "userId": userId,
                    "corpus": Corpus.get_items(userId=userId)
                }
            }, 200
        else:
            return {
                "status": "Fail"
            }, 500

@app.route("/corpus", methods=["POST"])
def corpus():
    from utils import get_userData

    # USER SETTINGS
    userId = request.form["userId"]
    
    if request.method == 'POST':
        from utils import process_text

        f_file = request.files.getlist("file")[0]
        f_format = request.form["format"]
        f_name = secure_filename(request.form["fileName"])
        
        if f_format == "file-pdf":
            from utils import pdf_to_string
            
            pdf_content = pdf_to_string(f_file)

            pdf_processed = process_text(pdf_content)

            Corpus.add(
                userId=userId,
                file_name=f_name,
                content=pdf_content,
                processed=pdf_processed)

            del pdf_content, pdf_processed

        elif f_format == "file-csv":
            import pandas as pd

            csv_fields = request.form["fields"]

            pd_csv = pd.read_csv(f_file, encoding="utf-8")

            for index, row in pd_csv.iterrows():
                csv_content = ""
                for field in csv_fields:
                    csv_content += f"{row[field]} "
                
                csv_processed = process_text(csv_content)

                Corpus.add(
                    userId=userId,
                    file_name=f"{f_name}_{index}",
                    content=csv_content,
                    processed=csv_processed)
            
            del pd_csv, csv_fields, csv_content, csv_processed

        elif f_format == "file-alt":
            txt_content = f_file.stream.read().decode("utf-8")
            txt_processed = process_text(txt_content)

            Corpus.add(
                userId=userId,
                file_name=f_name,
                content=txt_content,
                processed=txt_processed)

            del txt_content, txt_processed

        del f_file, f_format, f_name
    
    return {
        "status": "Success",
        "userData": {
            "userId": userId,
            "corpus": Corpus.get_items(userId=userId)
        }
    }, 200

@app.route("/delete", methods=["POST"])
def delete():
    if request.method == 'POST':
        from models import Corpus

        ids = request.form["ids"].split(",")
        userId = request.form["userId"]
        RESET_FLAG = True if request.form["RESET_FLAG"] == "true" else False


        Corpus.delete(
            userId=userId,
            ids=(None if RESET_FLAG else ids))

        del ids
        return {
            "status": "Success",
            "userData": {
                "userId": userId,
                "corpus": Corpus.get_items(userId=userId)
            }
        }, 200


if __name__ == "Vis-Kt":
    app.run(debug=True)