from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from routes import (
    auth, cluster, corpus,
    process_corpus, projection,
    sankey, session, word_similarity)


app = FastAPI(default_response_class=ORJSONResponse)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(GZipMiddleware, minimum_size=1000)
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
