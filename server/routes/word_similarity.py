from routes import LOGGER, fetch_user, ErrorResponse
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter


class WordSimilarityForm(BaseModel):
    userId: str
    query: List[str]


class WordSimilarityResponse(BaseModel):
    status: str = "Success"
    query: List[str]
    most_similar: List[Dict[str, Any]]


router = APIRouter(prefix="/word_similarity")


@router.post("")
def word_similarity(form: WordSimilarityForm):

    try:
        user = fetch_user(userId=form.userId)

        word_sim = user.word_vectors.most_similar(user.userId, form.query)

        response = {"query": form.query, "most_similar": word_sim}

        return WordSimilarityResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)
