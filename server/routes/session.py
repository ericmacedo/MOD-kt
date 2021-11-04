from routes import LOGGER, fetch_user
from routes import ErrorResponse, SessionData
from pydantic import BaseModel
from fastapi import APIRouter
from models.user import User
from typing import Dict


class SessionBaseForm(BaseModel):
    userId: str


class SessionForm(SessionBaseForm):
    sessionData: Dict


class SessionDeleteForm(SessionBaseForm):
    sessionId: str


class SessionResponse(BaseModel):
    status: str = "Success"
    sessionData: SessionData = None


router = APIRouter(prefix="/session")


@router.get("")
def session(userId: str, sessionId: str):
    try:
        user = fetch_user(userId=userId)

        if not sessionId:
            raise Exception("No such session exists")

        user = User(userId=userId)
        session = user.sessionData(id=sessionId)

        response = {"sessionData": SessionData(**session)}
        return SessionResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)


@router.put("")
def session(form: SessionForm):
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

        response = {"sessionData": SessionData(**session)}
        return SessionResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)


@router.post("")
def session(form: SessionDeleteForm):
    try:
        user = fetch_user(userId=form.userId)
        user.delete_sessions([form.sessionId])
        return SessionResponse()

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)
