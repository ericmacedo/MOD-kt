from fastapi.responses import StreamingResponse
from routes import LOGGER, fetch_user
from fastapi import APIRouter, Request
from typing import Optional, List
from utils import t_SNE, chunker
from pydantic import BaseModel

class ProjectionForm(BaseModel):
    userId: str
    projection: str
    perplexity: Optional[int] = None
    index: List[str]


router = APIRouter(prefix="/projection")


@router.post("")
async def projection(form: ProjectionForm, request: Request):
    try:
        from pdb import set_trace; set_trace() # noqa
        user = fetch_user(userId=form.userId)

        corpus = user.corpus

        corpus = [*filter(lambda doc: doc.id in form.index, corpus)]

        if form.projection == "t-SNE":
            projection = t_SNE(corpus, perplexity=form.perplexity)

        response = {"status": "success", "projection": projection}
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
