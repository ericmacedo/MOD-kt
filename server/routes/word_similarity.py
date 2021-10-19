from fastapi import APIRouter, Form
from routes import LOGGER, fetch_user


router = APIRouter(prefix="/word_similarity")


@router.post("/")
def projection(userId: str = Form(...),
               query: str = Form(...)):

    try:
        user = fetch_user(userId=userId)

        query = query.split(",")

        word_sim = user.word_vectors.most_similar(user.userId, query)

        return {
            "status": "success",
            "query": query,
            "most_similar": word_sim}

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
