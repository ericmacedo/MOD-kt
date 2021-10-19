from fastapi import APIRouter, Form
from routes import LOGGER, fetch_user
from clusterer import Clusterer
import json


router = APIRouter(prefix="/cluster")


@router.post("/")
def projection(userId: str = Form(...),
               recluster: str = Form(...),
               seed: str = Form(...),
               cluster_k: str = Form(...),
               index: str = Form(...)):
    try:
        user = fetch_user(userId=userId)

        recluster = True if recluster == "true" else False

        if recluster:
            seed = json.loads(seed)
            k = seed["cluster_k"]
            index = index.split(",")
            session = {}
        else:
            session = user.sessionData(id=None)
            seed = None
            k = int(cluster_k)
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

        return {"status": "success", "sessionData": session}

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
