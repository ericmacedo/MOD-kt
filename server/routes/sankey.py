from typing import Optional
from fastapi import APIRouter, Form
from routes import LOGGER, fetch_user
from utils import sankey_graph


router = APIRouter(prefix="/projection")


@router.post("/")
def projection(userId: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        return sankey_graph(user=user)

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
