from fastapi import APIRouter, Form
from routes import LOGGER, fetch_user


router = APIRouter(prefix="/auth")


@router.post("/")
# Authetication
#   Returns the userData if success
def auth(userId: str = Form(...)):
    try:
        user = fetch_user(userId=userId)
        return {
            "status": "Success",
            "userData": user.userData()}
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
