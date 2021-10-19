from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from routes import (
    auth, cluster, corpus,
    process_corpus, projection,
    sankey, session, word_similarity)

FRONTEND_ROUTES = ["", "corpus", "dashboard", "sessions"]

app = FastAPI(default_response_class=ORJSONResponse)

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

@app.get("/{path}")
@app.get("/")
def index(path: Optional[str] = None):
    path = path if path else ""
    if path in FRONTEND_ROUTES:
        return FileResponse('static/index.html')