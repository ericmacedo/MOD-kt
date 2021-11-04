from routes import LOGGER, fetch_user, UserData
from routes import ErrorResponse
from pydantic import BaseModel
from fastapi import APIRouter


class AuthForm(BaseModel):
    userId: str


class AuthResponse(BaseModel):
    status: str = "Success"
    userData: UserData


router = APIRouter(prefix="/auth")


@router.post("")
# Authetication
#   Returns the userData if success
async def auth(form: AuthForm):
    try:
        user = fetch_user(userId=form.userId)
        response = {"userData": user.userData()}
        return AuthResponse(**response)
    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)
