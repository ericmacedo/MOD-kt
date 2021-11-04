from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from models.user import User
import logging


class ErrorResponse(BaseModel):
    status: str = "Fail"
    code: int = 500
    message: Dict[str, str]


class ClusterData(BaseModel):
    cluster_k: int
    labels: List[int]
    colors: List[str]
    cluster_names: List[str]
    cluster_docs: Dict[str, List[str]]
    cluster_words: List[List[Dict[str, Any]]]


class SessionData(BaseModel):
    name: Optional[str] = ""
    notes: Optional[str] = ""
    index: Optional[List[str]] = []
    clusters: ClusterData
    graph: Optional[Dict[str, List[Dict[str, Any]]]] = {}
    tsne: Optional[List[List[float]]] = []
    controls: Optional[Dict[str, Any]] = {}
    selected: Optional[List[str]] = []
    focused: Optional[str] = ""
    highlight: Optional[str] = ""
    word_similarity: Optional[Dict[str, List[Any]]] = {}


class UserData(BaseModel):
    userId: str
    corpus: List[Dict]
    sessions: List[Dict]
    isProcessed: bool
    stop_words: List[str]


LOGGER = logging.getLogger(__name__)


def fetch_user(userId: str) -> User:
    user = User(userId=userId)
    if not user:
        raise Exception("No such user exists")
    return user
