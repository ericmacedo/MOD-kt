from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel
from models.user import User
from fastapi import Form
import logging
import inspect


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


def AsForm(cls: Type[BaseModel]):
    new_parameters = []

    for model_field in cls.__fields__.values():
        model_field: ModelField  # type: ignore

        if not model_field.required:
            new_parameters.append(
                inspect.Parameter(
                    model_field.alias,
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=Form(model_field.default),
                    annotation=model_field.outer_type_,
                )
            )
        else:
            new_parameters.append(
                inspect.Parameter(
                    model_field.alias,
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=Form(...),
                    annotation=model_field.outer_type_,
                )
            )

    def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, 'as_form', as_form_func)
    return cls
