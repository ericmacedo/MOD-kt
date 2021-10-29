from fastapi.responses import StreamingResponse
from utils import sankey_graph, chunker
from routes import LOGGER, fetch_user
from fastapi import APIRouter, Request


router = APIRouter(prefix="/sankey")


@router.get("")
async def sankey(userId: str, request: Request):
    try:
        user = fetch_user(userId=userId)

        response = sankey_graph(user=user)
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
