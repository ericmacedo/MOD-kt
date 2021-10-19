from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from werkzeug.utils import secure_filename
from routes import LOGGER, fetch_user
from typing import List, Optional
from pydantic import BaseModel
from utils import process_text
from utils import chunker
from io import BytesIO


router = APIRouter(prefix="/corpus")

class CorpusForm(BaseModel):
    userId: str
    RESET_FLAG: bool
    ids: List[str] = []


@router.post("")
async def corpus(form: CorpusForm):
    try:
        user = fetch_user(userId=form.userId)

        if form.RESET_FLAG:  # RESET WORKSPACE
            user.clear_workspace()
        else:
            user.delete_documents(form.ids)

        response = {"status": "Success", "newData": []}
        return StreamingResponse(chunker(response))

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


@router.put("")
async def corpus(userId: str = Form(...),
                 file: UploadFile = File(...),
                 fileName: str = Form(...),
                 format: str = Form(...),
                 fields: Optional[List[str]] = Form(...)):
    try:
        user = fetch_user(userId=userId)

        newData, content, file_name, n_entries = [], [], [], 0

        f_file = BytesIO(file.file.read())
        f_format = format
        f_name = secure_filename(fileName)

        if f_format == "file-pdf":
            from utils import pdf_to_string

            file_name.append(f_name)
            content.append(pdf_to_string(f_file))

            n_entries += 1
        elif f_format == "file-csv":
            import pandas as pd

            pd_csv = pd.read_csv(f_file, encoding="utf-8")

            for index, row in pd_csv.iterrows():
                csv_content = ""
                for field in fields:
                    csv_content += f"{row[field]} "

                file_name.append(f"{f_name}_{index}")
                content.append(csv_content)

                n_entries += 1

            
            del pd_csv, csv_content

        elif f_format == "file-alt":
            file_name.append(f_name)
            content.append(f_file.read().decode(
                encoding="utf-8", errors="ignore"))

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

        response = {"status": "Success", "newData": newData}
        return StreamingResponse(chunker(response))

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
