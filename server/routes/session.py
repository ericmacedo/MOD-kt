from fastapi.responses import StreamingResponse
from routes import LOGGER, fetch_user
from fastapi import APIRouter, Form
from pydantic import BaseModel
from models.user import User
from utils import chunker
from typing import Dict
import json


class SessionBaseForm(BaseModel):
    userId: str

class SessionForm(SessionBaseForm):
    sessionData: Dict

class SessionDeleteForm(SessionBaseForm):
    sessionId: str


router = APIRouter(prefix="/session")


@router.get("")
async def session(userId: str, sessionId: str):
    try:
        user = fetch_user(userId=userId)

        if not sessionId:
            raise Exception("No such session exists")

        user = User(userId=userId)
        session = user.sessionData(id=sessionId)

        response = {"status": "success", "sessionData": session}
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
async def session(form: SessionForm):
    try:
        user = fetch_user(userId=form.userId)

        session = form.sessionData
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

        response = {"status": "success", "sessionData": session}
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


@router.post("")
async def session(form: SessionDeleteForm):
    try:
        user = fetch_user(userId=form.userId)

        user.delete_sessions([form.sessionId])

        response = {"status": "success", "sessionData": None}
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
