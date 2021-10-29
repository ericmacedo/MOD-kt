from fastapi.responses import StreamingResponse
from routes import LOGGER, fetch_user
from fastapi import APIRouter, Request
from pydantic import BaseModel
from utils import chunker


class AuthForm(BaseModel):
    userId: str


router = APIRouter(prefix="/auth")


@router.post("")
# Authetication
#   Returns the userData if success
async def auth(form: AuthForm, request: Request):
    try:
        user = fetch_user(userId=form.userId)
        response = {
            "status": "Success",
            "userData": user.userData()}
        return StreamingResponse(chunker(response, request))
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
