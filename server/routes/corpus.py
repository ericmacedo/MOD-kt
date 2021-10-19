from werkzeug.utils import secure_filename
from fastapi import APIRouter, Form
from typing import List, Optional
from routes import LOGGER, fetch_user
from utils import process_text


router = APIRouter(prefix="/corpus")


@router.post("/")
def corpus(userId: str = Form(...),
           RESET_FLAG: str = Form(...),
           ids: Optional[str] = Form(...)):

    try:
        user = fetch_user(userId=userId)

        RESET_FLAG = True if RESET_FLAG == "true" else False

        if RESET_FLAG:  # RESET WORKSPACE
            user.clear_workspace()
        else:
            ids = ids.split(",")
            user.delete_documents(ids)

        return {"status": "Success", "newData": []}
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
def corpus(userId: str = Form(...),
           file: List = Form(...),
           format: str = Form(...),
           fileName: str = Form(...),
           fields: Optional[str] = Form(...)):
    try:
        user = fetch_user(userId=userId)

        newData, content, file_name, n_entries = [], [], [], 0

        f_file = file[0]
        f_format = str(format)
        f_name = secure_filename(str(fileName))

        if f_format == "file-pdf":
            from ..utils import pdf_to_string

            file_name.append(f_name)
            content.append(pdf_to_string(f_file))

            n_entries += 1
        elif f_format == "file-csv":
            import pandas as pd

            pd_csv = pd.read_csv(f_file, encoding="utf-8")
            csv_fields = fields.split(",")

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

        del file_name, content, n_entries, user

        return {
            "status": "Success",
            "newData": newData}
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
