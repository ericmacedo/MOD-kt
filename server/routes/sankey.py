from routes import LOGGER, fetch_user, ErrorResponse
from typing import List, Dict, Any
from utils import sankey_graph
from pydantic import BaseModel
from fastapi import APIRouter

class SankeyResponse(BaseModel):
    sessions: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    index: List[Dict[str, List[str]]]

router = APIRouter(prefix="/sankey")


@router.get("")
def sankey(userId: str):
    try:
        user = fetch_user(userId=userId)

        response = sankey_graph(user=user)
        return SankeyResponse(**response)

    except Exception as e:
        LOGGER.debug(e)
        response = {"message": {"title": str(type(e)), "content": str(e)}}
        return ErrorResponse(**response)
