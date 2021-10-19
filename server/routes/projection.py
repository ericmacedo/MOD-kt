from typing import Optional
from fastapi import APIRouter, Form
from routes import LOGGER, fetch_user
from utils import t_SNE


router = APIRouter(prefix="/projection")


@router.post("/")
def projection(userId: str = Form(...),
               projection: str = Form(...),
               perplexity: Optional[str] = Form(...),
               index: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        index = index.split(",")
        corpus = user.corpus

        corpus = [*filter(lambda doc: doc.id in index, corpus)]

        if projection == "t-SNE":
            perplexity = int(perplexity)
            projection = t_SNE(corpus, perplexity=perplexity)

        return {"status": "success", "projection": projection}

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
