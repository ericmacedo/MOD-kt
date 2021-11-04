from fastapi.responses import ORJSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from typing import Optional

from routes import (
    auth, cluster, corpus,
    process_corpus, projection,
    sankey, session, word_similarity)

from tqdm import tqdm
from functools import partialmethod

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)


FRONTEND_ROUTES = ["", "corpus", "dashboard", "sessions"]

app = FastAPI(title="i2DC", default_response_class=ORJSONResponse)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(GZipMiddleware, minimum_size=200)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

for route in [auth, cluster, corpus,
              process_corpus, projection,
              sankey, session, word_similarity]:
    app.include_router(route.router, prefix="/api")


@app.get("/{path}", response_class=FileResponse)
@app.get("/", response_class=FileResponse)
def index(path: Optional[str] = None):
    path = path if path else ""
    if path in FRONTEND_ROUTES:
        return "static/index.html"
