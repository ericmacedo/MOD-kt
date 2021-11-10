from routes import LOGGER, fetch_user, ErrorResponse
from typing import Optional, List
from utils import t_SNE
from pydantic import BaseModel
from fastapi import APIRouter


class ProjectionForm(BaseModel):
    userId: str
    projection: str
    perplexity: Optional[int] = None
    index: List[str]


class ProjectionResponse(BaseModel):
    status: str = "Success"
    projection: List[List[float]]


router = APIRouter(prefix="/projection")


@router.post("")
def projection(form: ProjectionForm):
    try:
        user = fetch_user(userId=form.userId)

        corpus = user.corpus

        corpus = [*filter(lambda doc: doc.id in form.index, corpus)]

        if form.projection == "t-SNE":
            projection = t_SNE(corpus, perplexity=form.perplexity)

        response = {"projection": projection}
        return ProjectionResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)
