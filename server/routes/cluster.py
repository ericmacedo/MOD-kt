from fastapi.responses import StreamingResponse
from routes import LOGGER, fetch_user
from fastapi import APIRouter, Request
from clusterer import Clusterer
from pydantic import BaseModel
from typing import List, Dict
from utils import chunker


class ClusterForm(BaseModel):
    userId: str
    recluster: bool
    seed: Dict
    cluster_k: int
    index: List[str]


router = APIRouter(prefix="/cluster")


@router.post("")
async def cluster(form: ClusterForm, request: Request):
    try:
        user = fetch_user(userId=form.userId)

        if form.recluster:
            seed = form.seed
            k = form.cluster_k
            index = form.index
            session = {}
        else:
            session = user.sessionData(id=None)
            seed = None
            k = int(form.cluster_k)
            index = user.index

        clusterer = Clusterer(
            user=user,
            index=index,
            k=k,
            seed=seed)

        session["clusters"] = {
            "cluster_k":        clusterer.k,
            "labels":           clusterer.doc_labels.tolist(),
            "colors":           clusterer.colors,
            "cluster_names":    clusterer.cluster_names,
            "cluster_docs":     clusterer.doc_clusters,
            "cluster_words":    [[
                {"word": word, "weight": 1}
                for word in paragraph["paragraph"][:5]
            ] for paragraph in clusterer.seed_paragraphs
            ]
        }

        response = {"status": "success", "sessionData": session}
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
