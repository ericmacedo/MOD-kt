from fastapi.responses import StreamingResponse
from routes import LOGGER, fetch_user
from fastapi import APIRouter, Form
from pydantic import BaseModel
from typing import List
from utils import chunker

class WordSimilarityForm(BaseModel):
    userId: str
    query: List[str]

router = APIRouter(prefix="/word_similarity")


@router.post("")
async def word_similarity(form: WordSimilarityForm):

    try:
        user = fetch_user(userId=form.userId)

        word_sim = user.word_vectors.most_similar(user.userId, form.query)

        response = {
            "status": "success",
            "query": form.query,
            "most_similar": word_sim}
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
