from typing import Optional
from fastapi import APIRouter, Form
from routes import LOGGER, fetch_user
from models.user import User
import json


router = APIRouter(prefix="/session")


@router.get("/")
def projection(userId: str = Form(...),
               sessionId: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        if not sessionId:
            raise Exception("No such session exists")

        user = User(userId=userId)
        session = user.sessionData(id=sessionId)

        return {"status": "success", "sessionData": session}

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
def projection(userId: str = Form(...),
               sessionData: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        session = json.loads(sessionData)
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

        return {"status": "success", "sessionData": session}

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


@router.post("/")
def projection(userId: str = Form(...),
               sessionId: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        user.delete_sessions([sessionId])

        return {"status": "success", "sessionData": None}

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
