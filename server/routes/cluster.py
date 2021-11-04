from routes import (
    LOGGER, fetch_user, SessionData,
    ClusterData, ErrorResponse)
from clusterer import Clusterer
from pydantic import BaseModel
from typing import List, Dict
from fastapi import APIRouter


class ClusterForm(BaseModel):
    userId: str
    recluster: bool
    seed: Dict
    cluster_k: int
    index: List[str]


class ClusterResponse(BaseModel):
    status: str = "Success"
    sessionData: SessionData


router = APIRouter(prefix="/cluster")


@router.post("")
def cluster(form: ClusterForm):
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

        clusters = {
            "cluster_k":        clusterer.k,
            "labels":           clusterer.doc_labels.tolist(),
            "colors":           clusterer.colors,
            "cluster_names":    clusterer.cluster_names,
            "cluster_docs":     clusterer.doc_clusters,
            "cluster_words":    [[
                {"word": word, "weight": 1}
                for word in paragraph["paragraph"][:5]
            ] for paragraph in clusterer.seed_paragraphs]
        }
        session["clusters"] = ClusterData(**clusters)

        response = {"sessionData": SessionData(**session)}
        return ClusterResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)
